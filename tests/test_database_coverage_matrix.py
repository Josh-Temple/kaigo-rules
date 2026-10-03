from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_database_coverage_matrix as coverage


class DatabaseCoverageMatrixTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.matrix = coverage.build()
        cls.by_service = {
            row["service_id"]: row
            for row in cls.matrix["services"]
        }

    def cell(self, service_id: str, family_id: str) -> dict:
        return next(
            cell for cell in self.by_service[service_id]["source_families"]
            if cell["source_family"] == family_id
        )

    def test_manifest_drives_rows(self):
        manifest = coverage.load("data/services/manifest.json")
        self.assertEqual(
            [row["service_id"] for row in self.matrix["services"]],
            [row["service_id"] for row in manifest["services"]],
        )

    def test_shared_corpus_does_not_imply_service_scope(self):
        cell = self.cell("community-dayservice", "care_insurance_act")
        self.assertEqual(cell["corpus_availability"]["state"], "AVAILABLE")
        self.assertEqual(cell["corpus_availability"]["kind"], "SHARED")
        self.assertEqual(cell["service_scope"]["state"], "SCOPE_NOT_DEFINED")

    def test_item_body_pass_does_not_promote_currentness(self):
        cell = self.cell("community-dayservice", "standards_interpretation_notice")
        self.assertEqual(cell["item_body_verification"]["state"], "PASS")
        self.assertEqual(cell["currentness"]["state"], "NOT_ESTABLISHED")

    def test_route_exposure_requires_service_scope(self):
        cell = self.cell("dayrehab", "national_qa")
        self.assertEqual(cell["corpus_availability"]["state"], "AVAILABLE")
        self.assertEqual(cell["service_scope"]["state"], "SCOPE_NOT_DEFINED")
        self.assertEqual(cell["route_exposure"]["state"], "NOT_ESTABLISHED")
        self.assertEqual(cell["publication"]["state"], "NOT_ESTABLISHED")

    def test_projection_is_fail_closed(self):
        policy = self.matrix["policy"]
        self.assertFalse(policy["canonical_status_writeback_allowed"])
        self.assertFalse(policy["verification_auto_promotion_allowed"])
        self.assertFalse(policy["currentness_auto_promotion_allowed"])
        self.assertFalse(policy["human_review_auto_promotion_allowed"])
        self.assertFalse(policy["route_auto_enable_allowed"])
        self.assertFalse(policy["single_completion_percentage_allowed"])

    def test_no_single_completion_percentage(self):
        def keys(value):
            if isinstance(value, dict):
                for key, child in value.items():
                    yield key
                    yield from keys(child)
            elif isinstance(value, list):
                for child in value:
                    yield from keys(child)
        forbidden = {
            "completion_rate",
            "completion_percentage",
            "overall_completion_rate",
            "overall_completion_percentage",
        }
        self.assertTrue(forbidden.isdisjoint(set(keys(self.matrix))))


if __name__ == "__main__":
    unittest.main()
