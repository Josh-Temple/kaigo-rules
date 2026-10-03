from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class HomevisitUnitPriceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = json.loads(
            (ROOT / "data/unit-price-homevisit.json").read_text(encoding="utf-8")
        )
        cls.config = json.loads(
            (ROOT / "data/services/homevisit.json").read_text(encoding="utf-8")
        )
        cls.scope = json.loads(
            (ROOT / "data/services/homevisit/unit-price-scope.json").read_text(encoding="utf-8")
        )
        cls.sources = {
            row["id"]: row
            for row in json.loads((ROOT / "data/sources.json").read_text(encoding="utf-8"))
        }

    def test_all_eight_region_rows_are_indexed(self):
        self.assertEqual(len(self.rows), 8)
        self.assertEqual(
            [row["region_class"] for row in self.rows],
            ["一級地", "二級地", "三級地", "四級地", "五級地", "六級地", "七級地", "その他"],
        )
        self.assertTrue(all(row["service"] == "訪問介護" for row in self.rows))

    def test_current_mhlw_ratios_are_preserved(self):
        expected = {
            "一級地": (1140, 11.40),
            "二級地": (1112, 11.12),
            "三級地": (1105, 11.05),
            "四級地": (1084, 10.84),
            "五級地": (1070, 10.70),
            "六級地": (1042, 10.42),
            "七級地": (1021, 10.21),
            "その他": (1000, 10.00),
        }
        actual = {
            row["region_class"]: (row["ratio_per_thousand"], row["unit_price_yen"])
            for row in self.rows
        }
        self.assertEqual(actual, expected)

    def test_rows_use_canonical_unit_price_source(self):
        self.assertTrue(all(row["source_id"] == "mhlw-unit-price-current" for row in self.rows))
        source = self.sources["mhlw-unit-price-current"]
        self.assertEqual(source["url"], self.scope["unit_price_scope"]["official_current_text_url"])
        self.assertEqual(self.scope["repository_service_rows"], "data/unit-price-homevisit.json")

    def test_ingestion_is_explicit_and_assurance_stays_unestablished(self):
        layer = self.config["ingestion_layers"]["unit_price"]
        self.assertEqual(layer["status"], "INDEXED_CURRENT_MHLW_DISPLAY_NOT_SERVICE_VERIFIED")
        self.assertEqual(layer["service_rows"], 8)
        self.assertEqual(layer["currentness"], "NOT_ESTABLISHED")
        self.assertEqual(layer["human_review"], "NOT_REVIEWED")
        self.assertFalse(self.config["publication_gate"]["public_routes_enabled"])
        self.assertFalse(self.config["routing"]["future_service_base_enabled"])


if __name__ == "__main__":
    unittest.main()
