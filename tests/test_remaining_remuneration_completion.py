from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_database_coverage_matrix as coverage

APPLICABLE = {
    "care-management": "mhlw-care-management-fee-notice20-current",
    "preventive-support": "mhlw-preventive-support-fee-notice129-current",
    "elderly-welfare-facility": "mhlw-facility-fee-notice21-current",
    "elderly-health-facility": "mhlw-facility-fee-notice21-current",
    "care-medical-institution": "mhlw-facility-fee-notice21-current",
    "preventive-dementia-dayservice": "mhlw-community-preventive-fee-notice128-current",
    "preventive-small-scale-multifunctional": "mhlw-community-preventive-fee-notice128-current",
    "preventive-dementia-group-home": "mhlw-community-preventive-fee-notice128-current",
}
NOT_APPLICABLE = {
    "specific-welfare-equipment-sale",
    "specific-preventive-welfare-equipment-sale",
}
SOURCE_IDS = set(APPLICABLE.values())


def load(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def walk_keys(value):
    if isinstance(value, dict):
        for key, child in value.items():
            yield key
            yield from walk_keys(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk_keys(child)


class RemainingRemunerationCompletionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.matrix = coverage.build()
        cls.by_service = {row["service_id"]: row for row in cls.matrix["services"]}

    def cell(self, service_id: str) -> dict:
        return next(
            cell
            for cell in self.by_service[service_id]["source_families"]
            if cell["source_family"] == "remuneration_notification"
        )

    def test_exact_remaining_ten_are_resolved(self):
        before = {
            "care-management",
            "preventive-support",
            "specific-welfare-equipment-sale",
            "elderly-welfare-facility",
            "elderly-health-facility",
            "care-medical-institution",
            "specific-preventive-welfare-equipment-sale",
            "preventive-dementia-dayservice",
            "preventive-small-scale-multifunctional",
            "preventive-dementia-group-home",
        }
        self.assertEqual(before, set(APPLICABLE) | NOT_APPLICABLE)

        coverage_counts = self.matrix["summary"]["source_family_coverage"]["remuneration_notification"]["ingestion"]
        self.assertEqual(coverage_counts.get("INGESTED"), 37)
        self.assertEqual(coverage_counts.get("NOT_APPLICABLE"), 2)
        self.assertEqual(coverage_counts.get("NOT_INGESTED", 0), 0)

    def test_applicable_services_have_bounded_indexes_and_fail_closed_assurance(self):
        forbidden = {"body", "full_text", "legal_text", "verbatim_text", "value", "unit", "rate"}
        for sid, source_id in APPLICABLE.items():
            with self.subTest(service_id=sid):
                index_path = f"data/services/{sid}/remuneration-index.json"
                index = load(index_path)
                config = load(f"data/services/{sid}.json")

                self.assertEqual(index["official_source"]["source_id"], source_id)
                self.assertFalse(index["service_scope"]["legal_text_duplicated"])
                self.assertFalse(index["coverage"]["legal_body_copied"])
                self.assertFalse(index["coverage"]["item_body_complete"])
                self.assertGreater(index["coverage"]["indexed_top_level_items"], 0)
                self.assertEqual(
                    index["coverage"]["total_index_entries"],
                    len(index["top_level_items"]) + len(index["child_items"]),
                )
                self.assertTrue(forbidden.isdisjoint(set(walk_keys(index))))

                self.assertEqual(config["ingestion_indexes"]["remuneration"], index_path)
                layer = config["ingestion_layers"]["remuneration"]
                self.assertEqual(layer["status"], "INDEXED_CURRENT_MHLW_DISPLAY_NOT_SERVICE_VERIFIED")
                self.assertEqual(layer["item_body_verification"], "NOT_ESTABLISHED")
                self.assertEqual(layer["currentness"], "NOT_ESTABLISHED")
                self.assertEqual(layer["human_review"], "NOT_REVIEWED")

                assurance = index["assurance"]
                self.assertEqual(assurance["item_body_verification"], "NOT_ESTABLISHED")
                self.assertEqual(assurance["currentness"], "NOT_ESTABLISHED")
                self.assertEqual(assurance["relation_verification"], "NOT_ESTABLISHED")
                self.assertEqual(assurance["human_review"], "NOT_REVIEWED")
                self.assertEqual(assurance["publication"], "BLOCKED")
                self.assertEqual(assurance["route_exposure"], "BLOCKED")
                self.assertFalse(assurance["automatic_verification_promotion_allowed"])

                cell = self.cell(sid)
                self.assertEqual(cell["ingestion"]["state"], "INGESTED")
                self.assertEqual(cell["item_body_verification"]["state"], "NOT_ESTABLISHED")
                self.assertEqual(cell["currentness"]["state"], "NOT_ESTABLISHED")
                self.assertEqual(cell["human_review"]["state"], "NOT_REVIEWED")
                self.assertEqual(cell["publication"]["state"], "BLOCKED")
                self.assertEqual(cell["route_exposure"]["state"], "BLOCKED")

    def test_sales_are_explicit_not_applicable_without_fake_index(self):
        for sid in NOT_APPLICABLE:
            with self.subTest(service_id=sid):
                self.assertFalse((ROOT / f"data/services/{sid}/remuneration-index.json").exists())
                config = load(f"data/services/{sid}.json")
                layer = config["ingestion_layers"]["remuneration"]
                self.assertEqual(layer["applicability"], "NOT_APPLICABLE")
                self.assertIn("NOT_APPLICABLE", layer["status"])
                cell = self.cell(sid)
                self.assertEqual(cell["ingestion"]["state"], "NOT_APPLICABLE")
                self.assertEqual(cell["item_body_verification"]["state"], "NOT_ESTABLISHED")
                self.assertEqual(cell["currentness"]["state"], "NOT_ESTABLISHED")
                self.assertEqual(cell["publication"]["state"], "BLOCKED")
                self.assertEqual(cell["route_exposure"]["state"], "BLOCKED")

    def test_primary_sources_are_registered_once(self):
        sources = load("data/sources.json")
        for source_id in SOURCE_IDS:
            rows = [row for row in sources if row["id"] == source_id]
            self.assertEqual(len(rows), 1, source_id)
            self.assertEqual(rows[0]["publisher"], "厚生労働省")
            self.assertTrue(rows[0]["url"].startswith("https://www.mhlw.go.jp/"))


if __name__ == "__main__":
    unittest.main()
