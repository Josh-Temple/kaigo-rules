import importlib.util
import json
import shutil
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('shared_fee', ROOT / 'scripts/validate_shared_fee_guidance.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class SharedFeeGuidanceTests(unittest.TestCase):
    def test_repository_chain(self):
        self.assertEqual(module.validate(), (66, 6))

    def mutate_and_reject(self, path, mutation):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            shutil.copytree(ROOT / 'data', root / 'data')
            target = root / path
            data = json.loads(target.read_text())
            mutation(data)
            target.write_text(json.dumps(data, ensure_ascii=False))
            with self.assertRaises((AssertionError, KeyError)):
                module.validate(root)

    def test_source_tampering(self):
        self.mutate_and_reject('data/shared/fee-guidance/source-registry.json',
                               lambda d: d['sources'][0].update(snapshot_sha256='0' * 64))

    def test_dangling_relation(self):
        self.mutate_and_reject('data/shared/fee-guidance/service-relations.json',
                               lambda d: d['relations'][0].update(node_id='missing'))

    def test_unsafe_currentness_promotion(self):
        self.mutate_and_reject('data/shared/fee-guidance/national-corpus.json',
                               lambda d: d['nodes'][0]['assurance'].update(currentness='PASS'))

    def test_body_duplication(self):
        self.mutate_and_reject('data/shared/fee-guidance/national-corpus.json',
                               lambda d: d['nodes'][0].update(official_text='duplicated body'))

    def test_coverage_projection_keeps_corpus_scope_and_assurance_separate(self):
        builder_spec = importlib.util.spec_from_file_location(
            'coverage_matrix', ROOT / 'scripts/build_database_coverage_matrix.py')
        builder = importlib.util.module_from_spec(builder_spec)
        builder_spec.loader.exec_module(builder)
        matrix = builder.build()
        rows = {
            row['service_id']: next(
                family for family in row['source_families']
                if family['source_family'] == 'fee_calculation_guidance'
            )
            for row in matrix['services']
        }
        for service_id in ('homevisit', 'homebath', 'homenursing', 'homerehab'):
            row = rows[service_id]
            self.assertEqual(row['corpus_availability']['kind'], 'SHARED')
            self.assertEqual(row['service_scope']['state'], 'SCOPE_DEFINED')
            self.assertEqual(row['ingestion']['state'], 'PARTIAL')
            self.assertEqual(row['item_body_verification']['state'], 'NOT_ESTABLISHED')
            self.assertEqual(row['currentness']['state'], 'NOT_ESTABLISHED')
            self.assertEqual(row['human_review']['state'], 'NOT_REVIEWED')
            self.assertEqual(row['publication']['state'], 'BLOCKED')
            self.assertEqual(row['route_exposure']['state'], 'BLOCKED')
        # Corpus availability is national; service scope remains service-specific.
        other = rows['night-homevisit']
        self.assertEqual(other['corpus_availability']['kind'], 'SHARED')
        self.assertEqual(other['service_scope']['state'], 'SCOPE_NOT_DEFINED')
