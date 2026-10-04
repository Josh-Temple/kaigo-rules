from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

TARGETS = {
    "homebath": ("2 訪問入浴介護費", "3 訪問看護費", 6, 18, 24),
    "homenursing": ("3 訪問看護費", "4 訪問リハビリテーション費", 10, 36, 46),
    "homerehab": ("4 訪問リハビリテーション費", "5 居宅療養管理指導費", 5, 10, 15),
    "homecaremanagement": ("5 居宅療養管理指導費", "6 通所介護費", 5, 41, 46),
    "shortstay-life": ("8 短期入所生活介護費(1日につき)", "9 短期入所療養介護費", 9, 102, 111),
    "shortstay-medical": ("9 短期入所療養介護費", "10 特定施設入居者生活介護費", 5, 552, 557),
    "specific-facility": ("10 特定施設入居者生活介護費", "11 福祉用具貸与費", 12, 41, 53),
    "welfare-equipment-rental": ("11 福祉用具貸与費(1月につき)", None, 1, 2, 3),
}


class HomeServiceRemunerationExpansionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.matrix = json.loads(
            (ROOT / "data/database-coverage-matrix.generated.json").read_text(encoding="utf-8")
        )

    def test_target_indexes_are_bounded_and_fail_closed(self):
        for service_id, (start, next_section, top_count, child_count, total) in TARGETS.items():
            with self.subTest(service_id=service_id):
                index = json.loads(
                    (ROOT / f"data/services/{service_id}/remuneration-index.json").read_text(encoding="utf-8")
                )
                config = json.loads(
                    (ROOT / f"data/services/{service_id}.json").read_text(encoding="utf-8")
                )
                scope = json.loads(
                    (ROOT / f"data/services/{service_id}/remuneration-scope.json").read_text(encoding="utf-8")
                )
                self.assertEqual(index["layer"], "REMUNERATION_NOTIFICATION")
                self.assertEqual(index["service_scope"]["start_marker"], start)
                self.assertEqual(index["service_scope"]["excluded_next_section"], next_section)
                self.assertFalse(index["service_scope"]["legal_text_duplicated"])
                self.assertEqual(index["official_source"]["source_id"], "mhlw-fee-notice19-base")
                self.assertFalse(index["extraction_policy"]["delegated_remuneration_criteria_included"])
                self.assertEqual(index["coverage"]["top_level_items"], top_count)
                self.assertEqual(index["coverage"]["numeric_child_items"], child_count)
                self.assertEqual(index["coverage"]["total_index_entries"], total)
                self.assertEqual(len(index["top_level_items"]), top_count)
                self.assertEqual(len(index["numeric_child_items"]), child_count)
                self.assertTrue(all(row["numeric_expressions"] for row in index["numeric_child_items"]))
                self.assertTrue(scope["primary_remuneration_notification"]["repository_section_ingested"])
                self.assertEqual(
                    config["ingestion_indexes"]["remuneration"],
                    f"data/services/{service_id}/remuneration-index.json",
                )
                self.assertEqual(
                    config["ingestion_layers"]["remuneration"]["status"],
                    "INDEXED_CURRENT_MHLW_DISPLAY_NOT_SERVICE_VERIFIED",
                )
                assurance = index["assurance"]
                self.assertEqual(assurance["item_body_verification"], "NOT_ESTABLISHED")
                self.assertEqual(assurance["currentness"], "NOT_ESTABLISHED")
                self.assertEqual(assurance["human_review"], "NOT_REVIEWED")
                self.assertEqual(assurance["publication"], "BLOCKED")
                self.assertEqual(assurance["route_exposure"], "BLOCKED")
                self.assertFalse(assurance["automatic_verification_promotion_allowed"])
                self.assertFalse(config["publication_gate"]["public_routes_enabled"])
                self.assertFalse(config["routing"]["future_service_base_enabled"])

    def test_coverage_projection_marks_only_ingestion(self):
        by_id = {row["service_id"]: row for row in self.matrix["services"]}
        for service_id in TARGETS:
            with self.subTest(service_id=service_id):
                cell = next(
                    row for row in by_id[service_id]["source_families"]
                    if row["source_family"] == "remuneration_notification"
                )
                self.assertEqual(cell["ingestion"]["state"], "INGESTED")
                self.assertEqual(cell["item_body_verification"]["state"], "NOT_ESTABLISHED")
                self.assertEqual(cell["currentness"]["state"], "NOT_ESTABLISHED")
                self.assertEqual(cell["human_review"]["state"], "NOT_REVIEWED")
                self.assertEqual(cell["publication"]["state"], "BLOCKED")
                self.assertEqual(cell["route_exposure"]["state"], "BLOCKED")

    def test_specific_welfare_equipment_sale_remains_not_applicable(self):
        scope = json.loads(
            (ROOT / "data/services/specific-welfare-equipment-sale/remuneration-scope.json").read_text(encoding="utf-8")
        )
        config = json.loads(
            (ROOT / "data/services/specific-welfare-equipment-sale.json").read_text(encoding="utf-8")
        )
        self.assertEqual(scope["status"], "SCOPE_DEFINED_NOT_APPLICABLE_TO_NOTICE19")
        self.assertEqual(scope["primary_remuneration_notification"]["scope_relation"], "NOT_APPLICABLE")
        self.assertFalse((ROOT / "data/services/specific-welfare-equipment-sale/remuneration-index.json").exists())
        self.assertNotIn("remuneration", config.get("ingestion_layers", {}))


if __name__ == "__main__":
    unittest.main()
