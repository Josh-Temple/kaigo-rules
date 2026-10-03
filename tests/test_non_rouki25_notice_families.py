import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

CASES = {
    "community-dayservice": (
        "community_based_services_standards_interpretation",
        21,
        "ITEM_BODY_VERIFIED_CURRENTNESS_PENDING",
        "PASS_CONTENT_EVIDENCE_MATCH_ONLY",
    ),
    "regular-round": (
        "community_based_services_standards_interpretation",
        21,
        "ITEM_BODY_VERIFIED_CURRENTNESS_PENDING",
        "PASS_CONTENT_EVIDENCE_MATCH_ONLY",
    ),
    "night-homevisit": (
        "community_based_services_standards_interpretation",
        25,
        "ITEM_BODY_VERIFIED_CURRENTNESS_PENDING",
        "PASS_CONTENT_EVIDENCE_MATCH_ONLY",
    ),
    "care-management": (
        "care_management_standards_interpretation",
        32,
        "SOURCE_INVENTORY_VERIFIED_ITEM_BODY_GAPS_REMAIN",
        "PARTIAL_WITH_GAPS",
    ),
    "preventive-support": (
        "preventive_support_standards_interpretation",
        34,
        "SOURCE_INVENTORY_VERIFIED_ITEM_BODY_GAPS_REMAIN",
        "PARTIAL_WITH_GAPS",
    ),
}


class NonRouki25NoticeFamilyTest(unittest.TestCase):
    def test_remaining_services_use_correct_notice_layer(self):
        for service_id, (
            source_family,
            expected_items,
            expected_status,
            item_body_status,
        ) in CASES.items():
            with self.subTest(service_id=service_id):
                config = json.loads(
                    (ROOT / f"data/services/{service_id}.json").read_text(
                        encoding="utf-8"
                    )
                )
                self.assertNotIn("rouki25", config["ingestion_layers"])
                layer = config["ingestion_layers"]["standards_interpretation"]
                self.assertEqual(layer["source_family"], source_family)
                self.assertEqual(layer["principal_items"], expected_items)
                self.assertEqual(layer["status"], expected_status)
                self.assertEqual(
                    layer["source_inventory_verification"],
                    "PASS_BOUNDED_SCOPE_ONLY",
                )
                self.assertEqual(layer["item_body_verification"], item_body_status)
                self.assertFalse(config["publication_gate"]["content_ingested"])
                self.assertFalse(config["publication_gate"]["public_routes_enabled"])
                self.assertFalse(
                    config["publication_gate"]["independent_verification_complete"]
                )

    def test_scope_files_preserve_source_specific_gaps(self):
        for service_id, (
            source_family,
            expected_items,
            _expected_status,
            _item_body_status,
        ) in CASES.items():
            with self.subTest(service_id=service_id):
                path = ROOT / f"data/services/{service_id}/standards-interpretation-scope.json"
                scope = json.loads(path.read_text(encoding="utf-8"))
                self.assertEqual(scope["service_id"], service_id)
                self.assertEqual(scope["source_family"], source_family)
                self.assertEqual(
                    scope["work_control"]["expected_principal_items"],
                    expected_items,
                )
                self.assertEqual(scope["currentness_state"], "NOT_ESTABLISHED")
                self.assertEqual(scope["human_review_state"], "NOT_REVIEWED")
                self.assertFalse(scope["publication"]["allowed"])
                self.assertTrue(scope["source_urls"])

    def test_catalog_exposes_correct_notice_layer(self):
        catalog = json.loads(
            (ROOT / "data/services/catalog.generated.json").read_text(
                encoding="utf-8"
            )
        )
        by_id = {row["service_id"]: row for row in catalog["services"]}
        for service_id, (
            source_family,
            expected_items,
            expected_status,
            item_body_status,
        ) in CASES.items():
            with self.subTest(service_id=service_id):
                row = by_id[service_id]
                self.assertNotIn("rouki25", row["ingestion_layers"])
                layer = row["ingestion_layers"]["standards_interpretation"]
                self.assertEqual(layer["source_family"], source_family)
                self.assertEqual(layer["principal_items"], expected_items)
                self.assertEqual(layer["status"], expected_status)
                self.assertEqual(layer["item_body_verification"], item_body_status)


if __name__ == "__main__":
    unittest.main()
