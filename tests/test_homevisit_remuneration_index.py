from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class HomevisitRemunerationIndexTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index = json.loads(
            (ROOT / "data/services/homevisit/remuneration-index.json").read_text(encoding="utf-8")
        )
        cls.config = json.loads(
            (ROOT / "data/services/homevisit.json").read_text(encoding="utf-8")
        )
        cls.scope = json.loads(
            (ROOT / "data/services/homevisit/remuneration-scope.json").read_text(encoding="utf-8")
        )

    def test_section_is_bounded_to_homevisit(self):
        scope = self.index["service_scope"]
        self.assertEqual(scope["start_marker"], "1 訪問介護費")
        self.assertEqual(scope["excluded_next_section"], "2 訪問入浴介護費")
        self.assertFalse(scope["legal_text_duplicated"])

    def test_structural_inventory_counts_and_markers(self):
        coverage = self.index["coverage"]
        self.assertEqual(coverage["top_level_items"], 25)
        self.assertEqual(coverage["numeric_child_items"], 21)
        self.assertEqual(coverage["total_index_entries"], 46)

        top_markers = {row["marker"] for row in self.index["top_level_items"]}
        self.assertEqual(
            top_markers,
            {"イ", "ロ", "ハ", *{f"注{i}" for i in range(1, 18)}, "ニ", "ホ", "ヘ", "ト", "チ"},
        )

    def test_key_numeric_rows_are_preserved_as_index_data(self):
        rows = {row["marker"]: row for row in self.index["child_items"]}
        self.assertEqual(rows["イ(1)"]["value"], {"value": 163, "unit": "単位/回"})
        self.assertEqual(rows["ロ(2)"]["value"], {"value": 220, "unit": "単位/回"})
        self.assertEqual(rows["注10(1)"]["value"]["rate"], "+20/100")
        self.assertEqual(rows["チ(6)"]["value"]["rate"], "+170/1000")

    def test_scope_source_and_ingestion_index_are_bound(self):
        source = self.index["canonical_sources"][0]
        self.assertEqual(
            source["url"],
            self.scope["primary_fee_schedule"]["official_current_text_url"],
        )
        self.assertEqual(
            self.config["ingestion_indexes"]["remuneration"],
            "data/services/homevisit/remuneration-index.json",
        )
        self.assertEqual(
            self.config["ingestion_layers"]["remuneration"]["status"],
            "INDEXED_CURRENT_MHLW_DISPLAY_NOT_SERVICE_VERIFIED",
        )

    def test_ingestion_does_not_promote_assurance_layers(self):
        assurance = self.index["assurance"]
        self.assertEqual(assurance["item_body_verification"], "NOT_ESTABLISHED")
        self.assertEqual(assurance["currentness"], "NOT_ESTABLISHED")
        self.assertEqual(assurance["human_review"], "NOT_REVIEWED")
        self.assertEqual(assurance["publication"], "BLOCKED")
        self.assertEqual(assurance["route_exposure"], "BLOCKED")
        self.assertFalse(assurance["automatic_verification_promotion_allowed"])
        self.assertFalse(self.config["publication_gate"]["public_routes_enabled"])
        self.assertFalse(self.config["routing"]["future_service_base_enabled"])


if __name__ == "__main__":
    unittest.main()
