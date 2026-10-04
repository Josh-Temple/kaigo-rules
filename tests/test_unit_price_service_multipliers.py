import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class UnitPriceServiceMultiplierTest(unittest.TestCase):
    def setUp(self):
        self.data = json.loads((ROOT / "data/unit-price-service-multipliers.json").read_text(encoding="utf-8"))
        self.manifest = json.loads((ROOT / "data/services/manifest.json").read_text(encoding="utf-8"))

    def test_service_universe_is_explicit(self):
        self.assertEqual(
            [row["service_id"] for row in self.manifest["services"]],
            [row["service_id"] for row in self.data["service_mappings"]],
        )

    def test_region_assignments_are_shared_not_duplicated_per_service(self):
        self.assertEqual("data/unit-price-region-assignments.json", self.data["shared_region_assignments"])
        for row in self.data["service_mappings"]:
            self.assertNotIn("region_assignments", row)
            self.assertNotIn("municipality_assignments", row)

    def test_non_applicable_purchase_benefits_are_not_forced_into_eight_regions(self):
        rows = {row["service_id"]: row for row in self.data["service_mappings"]}
        for service_id in (
            "specific-welfare-equipment-sale",
            "specific-preventive-welfare-equipment-sale",
        ):
            self.assertEqual("NOT_APPLICABLE", rows[service_id]["applicability"])
            self.assertNotIn("multiplier_profile_id", rows[service_id])

    def test_ingestion_does_not_claim_verification(self):
        for row in self.data["service_mappings"]:
            if row["applicability"] == "APPLIES":
                self.assertEqual(
                    "INDEXED_CURRENT_MHLW_DISPLAY_NOT_SERVICE_VERIFIED",
                    row["ingestion_status"],
                )
        self.assertFalse(self.data["assurance"]["automatic_promotion_allowed"])

if __name__ == "__main__":
    unittest.main()
