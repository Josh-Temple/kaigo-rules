import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class QaServiceMappingTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mapping = json.loads((ROOT / "data/qa-service-mapping.json").read_text(encoding="utf-8"))
        cls.meta = json.loads((ROOT / "data/qa-corpus-meta.json").read_text(encoding="utf-8"))
        cls.manifest = json.loads((ROOT / "data/services/manifest.json").read_text(encoding="utf-8"))

    def test_validator_passes(self):
        result = subprocess.run(
            [sys.executable, "scripts/validate_qa_service_mapping.py"],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("Q&A service mapping: OK", result.stdout)

    def test_taxonomy_covers_every_official_workbook_code(self):
        entries = self.mapping["codes"]
        self.assertEqual(
            [entry["service_code"] for entry in entries],
            self.meta["target_service_codes"],
        )
        self.assertEqual(
            self.mapping["summary"]["classification_counts"],
            {
                "SHARED_COMMON_CATEGORY": 6,
                "INDIVIDUAL_SERVICE": 26,
                "HISTORICAL_ABOLISHED_SERVICE": 1,
                "OTHER_SPECIAL": 2,
                "REMUNERATION_ONLY_THEME": 1,
            },
        )

    def test_current_catalog_has_exact_direct_mappings(self):
        current_ids = {service["service_id"] for service in self.manifest["services"]}
        mapped_ids = {
            entry["catalog_mapping"]["service_id"]
            for entry in self.mapping["codes"]
            if entry["catalog_mapping"]["state"] == "MAPPED_CURRENT_CATALOG"
        }
        self.assertTrue(mapped_ids.issubset(current_ids))
        self.assertEqual(len(current_ids), 39)
        self.assertEqual(len(mapped_ids), 26)

    def test_parallel_catalog_services_are_reconciled_to_stable_ids(self):
        by_code = {entry["service_code"]: entry for entry in self.mapping["codes"]}
        expected = {
            "19":"shortstay-medical","20":"specific-facility","21":"welfare-equipment-rental",
            "22":"specific-welfare-equipment-sale","24":"elderly-welfare-facility",
            "25":"elderly-health-facility","42":"dementia-dayservice",
            "43":"small-scale-multifunctional","44":"dementia-group-home",
            "45":"community-specific-facility","46":"community-elderly-facility",
            "47":"nursing-small-scale-multifunctional","49":"care-medical-institution",
        }
        for code, service_id in expected.items():
            self.assertEqual(by_code[code]["catalog_mapping"]["state"], "MAPPED_CURRENT_CATALOG")
            self.assertEqual(by_code[code]["catalog_mapping"]["service_id"], service_id)

    def test_shared_categories_are_relations_not_copies(self):
        shared = [
            entry for entry in self.mapping["codes"]
            if entry["classification"] == "SHARED_COMMON_CATEGORY"
        ]
        self.assertEqual({entry["service_code"] for entry in shared}, {"01", "02", "03", "04", "05", "06"})
        self.assertEqual(len({entry["scope_relation"]["group_id"] for entry in shared}), 6)
        for entry in shared:
            self.assertEqual(entry["scope_relation"]["kind"], "GROUP")
            self.assertEqual(entry["scope_relation"]["membership_state"], "NOT_EXPANDED_IN_QA_MAPPING")
            self.assertIsNone(entry["catalog_mapping"]["service_id"])

    def test_historical_theme_and_special_codes_remain_separate(self):
        by_code = {entry["service_code"]: entry for entry in self.mapping["codes"]}
        self.assertEqual(by_code["26"]["classification"], "HISTORICAL_ABOLISHED_SERVICE")
        self.assertEqual(by_code["50"]["classification"], "REMUNERATION_ONLY_THEME")
        self.assertEqual(by_code["27"]["classification"], "OTHER_SPECIAL")
        self.assertEqual(by_code["51"]["classification"], "OTHER_SPECIAL")
        for code in ("26", "27", "50", "51"):
            self.assertIsNone(by_code[code]["catalog_mapping"]["service_id"])

    def test_raw_scope_variants_fail_closed(self):
        self.assertEqual(
            self.mapping["summary"]["rows_with_qualified_or_variant_raw_service_label"],
            297,
        )
        by_code = {entry["service_code"]: entry for entry in self.mapping["codes"]}
        self.assertGreater(by_code["01"]["row_scope"]["qualified_or_variant_raw_label_rows"], 0)
        self.assertIn(
            "DO_NOT_AUTO_EXPAND",
            by_code["01"]["row_scope"]["policy"],
        )


if __name__ == "__main__":
    unittest.main()
