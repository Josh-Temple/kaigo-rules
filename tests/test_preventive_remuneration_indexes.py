from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATUS = "INDEXED_MHLW_CONSOLIDATED_DISPLAY_NOT_SERVICE_VERIFIED"
SALE_ID = "specific-preventive-welfare-equipment-sale"

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

class PreventiveRemunerationIndexTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = load("data/services/manifest.json")
        cls.targets = [row for row in cls.manifest["services"] if row["service_class"] == "PREVENTIVE_SERVICE" and row["service_id"] != SALE_ID]
        cls.sale = next(row for row in cls.manifest["services"] if row["service_id"] == SALE_ID)
        cls.remuneration_assurance = {
            row["service_id"]: row
            for row in load("data/shared/remuneration-notification/service-item-body-assurance.json")["services"]
        }

    def test_target_set_is_manifest_driven_and_sale_stays_explicit_na(self):
        self.assertEqual(len(self.targets), 9)
        sale_scope = load(f"data/services/{SALE_ID}/remuneration-scope.json")
        self.assertEqual(sale_scope["remuneration_notification"]["state"], "NOT_APPLICABLE")
        self.assertEqual(self.sale["status"], "REGISTERED_NOT_INGESTED")
        self.assertFalse((ROOT / f"data/services/{SALE_ID}/remuneration-index.json").exists())
        sale_config = load(f"data/services/{SALE_ID}.json")
        self.assertIn("NOT_APPLICABLE", sale_config["ingestion_layers"]["remuneration"]["status"])

    def test_each_target_has_bounded_index_and_fail_closed_assurance(self):
        ordinals = []
        for descriptor in self.targets:
            sid = descriptor["service_id"]
            config = load(descriptor["config"])
            scope = load(f"data/services/{sid}/remuneration-scope.json")
            index_path = f"data/services/{sid}/remuneration-index.json"
            index = load(index_path)
            selector = scope["remuneration_notification"]["fee_table_selector"]
            ordinals.append(selector["ordinal"])
            self.assertEqual(descriptor["status"], "PARTIAL_INGESTION", sid)
            self.assertEqual(config["readiness"], "PARTIAL_INGESTION", sid)
            self.assertEqual(config["ingestion_state"], "PARTIAL_INGESTION", sid)
            self.assertEqual(config["ingestion_indexes"]["remuneration"], index_path, sid)
            self.assertEqual(config["ingestion_layers"]["remuneration"]["status"], STATUS, sid)
            self.assertEqual(index["service_scope"]["section_ordinal"], selector["ordinal"])
            self.assertIn(selector["label"], index["service_scope"]["start_marker"])
            self.assertFalse(index["service_scope"]["legal_text_duplicated"])
            self.assertFalse(index["coverage"]["legal_body_copied"])
            self.assertGreater(len(index["top_level_items"]), 0)
            self.assertEqual(index["coverage"]["total_index_entries"], len(index["top_level_items"]) + len(index["child_items"]))
            for item in [*index["top_level_items"], *index["child_items"]]:
                self.assertTrue(item["source_locator"].startswith("別表 指定介護予防サービス介護給付費単位数表"))
            self.assertEqual(scope["remuneration_notification"]["structured_nodes_state"], STATUS)
            self.assertEqual(scope["remuneration_notification"]["structured_index_path"], index_path)
            self.assertEqual(scope["remuneration_notification"]["verification_status"], "NOT_SERVICE_VERIFIED")
            self.assertEqual(scope["remuneration_notification"]["currentness_state"], "NOT_ESTABLISHED_FOR_SERVICE")
            assurance = index["assurance"]
            self.assertEqual(assurance["item_body_verification"], "NOT_ESTABLISHED")
            self.assertEqual(assurance["currentness"], "NOT_ESTABLISHED")
            self.assertEqual(assurance["human_review"], "NOT_REVIEWED")
            self.assertEqual(assurance["publication"], "BLOCKED")
            self.assertEqual(assurance["route_exposure"], "BLOCKED")
            self.assertFalse(assurance["automatic_verification_promotion_allowed"])
            self.assertFalse(config["publication_gate"]["public_routes_enabled"])
            self.assertFalse(config["routing"]["future_service_base_enabled"])
            self.assertNotIn("delegated_remuneration_criteria", config["ingestion_layers"])
            self.assertTrue({"value", "unit", "rate", "body", "full_text"}.isdisjoint(set(walk_keys(index))))
        self.assertEqual(sorted(ordinals), list(range(1, 10)))

    def test_sections_are_contiguous(self):
        rows = []
        for descriptor in self.targets:
            sid = descriptor["service_id"]
            index = load(f"data/services/{sid}/remuneration-index.json")
            rows.append((index["service_scope"]["section_ordinal"], index))
        rows.sort()
        for i, (_, index) in enumerate(rows):
            if i < len(rows) - 1:
                nxt = rows[i + 1][1]["service_scope"]["start_marker"]
                self.assertEqual(index["service_scope"]["end_marker"], nxt)
                self.assertEqual(index["service_scope"]["excluded_next_section"], nxt)
            else:
                self.assertEqual(index["service_scope"]["end_marker"], "END_OF_NOTICE127_FEE_TABLE")
                self.assertIsNone(index["service_scope"]["excluded_next_section"])

    def test_special_relations_remain_separate_and_unverified(self):
        facility = load("data/services/preventive-specific-facility/remuneration-index.json")
        rental = load("data/services/preventive-welfare-equipment-rental/remuneration-index.json")
        self.assertTrue(any(row["relation_type"] == "EXTERNAL_SERVICE_UTILIZATION_REFERENCE" for row in facility["relation_metadata"]))
        self.assertTrue(any(row["relation_type"] == "CALCULATION_REFERENCES_UNIT_PRICE_FAMILY" for row in rental["relation_metadata"]))
        for doc in (facility, rental):
            for row in doc["relation_metadata"]:
                self.assertNotEqual(row["state"], "VERIFIED")

    def test_coverage_projection_counts_ingestion_without_promoting_assurance(self):
        matrix = load("data/database-coverage-matrix.generated.json")
        coverage = matrix["summary"]["source_family_coverage"]["remuneration_notification"]
        self.assertEqual(coverage["ingestion"].get("INGESTED"), 37)
        self.assertEqual(coverage["ingestion"].get("NOT_APPLICABLE"), 2)
        self.assertEqual(coverage["ingestion"].get("NOT_INGESTED", 0), 0)
        by_id = {row["service_id"]: row for row in matrix["services"]}
        for descriptor in self.targets:
            cell = next(x for x in by_id[descriptor["service_id"]]["source_families"] if x["source_family"] == "remuneration_notification")
            self.assertEqual(cell["ingestion"]["state"], "INGESTED")
            self.assertEqual(
                cell["item_body_verification"]["state"],
                self.remuneration_assurance[descriptor["service_id"]]["projection_state"],
            )
            self.assertEqual(cell["currentness"]["state"], "NOT_ESTABLISHED")
            self.assertEqual(cell["human_review"]["state"], "NOT_REVIEWED")
            self.assertEqual(cell["publication"]["state"], "BLOCKED")
            self.assertEqual(cell["route_exposure"]["state"], "BLOCKED")

if __name__ == "__main__":
    unittest.main()
