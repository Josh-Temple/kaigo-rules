import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts import prepare_handbook_publication_boundary as boundary


class HandbookPublicationBoundaryTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / 'components').mkdir()
        (self.root / 'data').mkdir()
        self.component = self.root / 'components/service-handbook.tsx'
        self.component.write_text('\n'.join((boundary.OLD_ROLES, boundary.OLD_GUARD,
                                             boundary.HEADING, boundary.HEADING)), encoding='utf-8')
        self.data = self.root / 'data/handbook-content.json'
        payload = {'services': {'example': {'chapters': {'staffing': {'role_sections': [
            {'id': 'role', 'requirements': [
                {'id': 'mesh-held', 'description': '隔離中の文章として、十分に長い文章をここに記載して出力検査で検出できるようにします。'},
                {'id': 'other-held', 'description': 'Research Mesh の隔離候補'},
                {'id': 'kept', 'description': '普通の確認項目'},
            ]}, {'id': 'only-held', 'requirements': [
                {'id': 'mesh-held-2', 'description': 'candidate'},
            ]}]}}}}}
        self.data.write_text(json.dumps(payload, ensure_ascii=False), encoding='utf-8')
        self.hashes = {'COMPONENT_HASH': hashlib.sha256(self.component.read_bytes()).hexdigest(),
                       'DATA_HASH': hashlib.sha256(self.data.read_bytes()).hexdigest(),
                       'EXPECTED_WITHHELD': 3}
        self.patchers = [patch.object(boundary, name, value) for name, value in self.hashes.items()]
        for p in self.patchers:
            p.start()
            self.addCleanup(p.stop)

    def test_patch_filters_held_requirements_and_keeps_original_data(self):
        original_data = self.data.read_bytes()
        self.assertEqual(boundary.apply(self.root), 3)
        component = self.component.read_text(encoding='utf-8')
        self.assertIn('requirement.id.startsWith("mesh-")', component)
        self.assertIn('role.requirements.filter(requirement => !isWithheld(requirement))', component)
        self.assertIn('掲載を控えています', component)
        self.assertEqual(self.data.read_bytes(), original_data)
        with self.assertRaisesRegex(RuntimeError, 'renderer changed'):
            boundary.apply(self.root)

    def test_audit_rejects_withheld_output_and_allows_other_requirements(self):
        site = self.root / 'site'
        page = site / 'handbook/example/staffing.html'
        page.parent.mkdir(parents=True)
        page.write_text('<section id="staffing-role-role-requirement-kept">ok</section>', encoding='utf-8')
        self.assertEqual(boundary.audit(self.root, site),
                         {'quarantined_requirements': 3, 'fully_withheld_roles': 1,
                          'handbook_pages_checked': 1})
        page.write_text('<section id="staffing-role-role-requirement-mesh-held">blocked</section>', encoding='utf-8')
        with self.assertRaisesRegex(RuntimeError, 'Quarantined requirement present'):
            boundary.audit(self.root, site)
        page.write_text('<p>隔離中の文章として、十分に長い文章をここに記載して出力検査で検出できるようにします。</p>', encoding='utf-8')
        with self.assertRaisesRegex(RuntimeError, 'Quarantined text present'):
            boundary.audit(self.root, site)
        page.write_text('<a href="#staffing-role-only-held">held role</a>', encoding='utf-8')
        with self.assertRaisesRegex(RuntimeError, 'Quarantined role or navigation'):
            boundary.audit(self.root, site)

    def test_source_drift_or_missing_page_fails_closed(self):
        self.data.write_text('{}', encoding='utf-8')
        with self.assertRaisesRegex(RuntimeError, 'source data changed'):
            boundary.apply(self.root)
        site = self.root / 'site'
        site.mkdir()
        with self.assertRaisesRegex(RuntimeError, 'source data changed'):
            boundary.audit(self.root, site)

    def test_ordinary_unreviewed_requirement_is_not_automatically_hidden(self):
        self.assertFalse(boundary.quarantined({'id': 'ordinary', 'description': '未確認'}))
        self.assertTrue(boundary.quarantined({'id': 'mesh-held', 'description': '未確認'}))
        self.assertTrue(boundary.quarantined({'id': 'other-held', 'description': 'Research Mesh の隔離候補'}))


if __name__ == '__main__':
    unittest.main()
