#!/usr/bin/env python3
"""Regression tests for Worker C remuneration / Fee Guidance residual assurance."""
from __future__ import annotations

import json
import unittest
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REM_ASSURANCE = ROOT / "data/shared/remuneration-notification/service-item-body-assurance.json"
REM_CLASSIFICATION = ROOT / "data/shared/remuneration-notification/residual-classification.json"
FEE_ASSURANCE = ROOT / "data/shared/fee-guidance/item-body-assurance.json"
FEE_CLASSIFICATION = ROOT / "data/shared/fee-guidance/residual-classification.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


class RemunerationFeeResidualAssuranceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rem = load(REM_ASSURANCE)
        cls.rem_class = load(REM_CLASSIFICATION)
        cls.fee = load(FEE_ASSURANCE)
        cls.fee_class = load(FEE_CLASSIFICATION)

    def test_remuneration_classification_is_complete_and_non_promotional(self):
        assurance = {row["service_id"]: row for row in self.rem["services"]}
        classified = {row["service_id"]: row for row in self.rem_class["services"]}
        self.assertEqual(set(assurance), set(classified))
        self.assertEqual(len(classified), 39)
        self.assertEqual(self.rem_class["summary"]["status_promotions"], 0)
        self.assertEqual(
            self.rem_class["summary"]["body_evidence_type_counts"],
            dict(Counter(row["body_evidence_type"] for row in classified.values())),
        )

        for service_id, source in assurance.items():
            row = classified[service_id]
            self.assertEqual(row["item_body_state"], source["projection_state"])
            self.assertFalse(row["currentness_established_by_body_evidence"])

            state = source["projection_state"]
            if state == "PASS":
                self.assertEqual(row["body_evidence_type"], "DIRECT_OFFICIAL_ITEM_BODY_MATCH")
                self.assertEqual(row["service_item_inventory_state"], "COMPLETE")
            elif state == "PARTIAL":
                self.assertEqual(row["body_evidence_type"], "DIRECT_OFFICIAL_SECTION_BODY_FINGERPRINT")
                self.assertEqual(row["service_item_inventory_state"], "INCOMPLETE_CANONICAL_ITEM_BODY")
                self.assertFalse((source.get("invariants") or {}).get("canonical_body_matches_official_body"))
                self.assertFalse((source.get("invariants") or {}).get("all_referenced_nodes_verified"))
            elif state == "NOT_APPLICABLE":
                self.assertEqual(row["body_evidence_type"], "NOT_APPLICABLE")
                self.assertEqual(row["service_item_inventory_state"], "NOT_APPLICABLE")
            else:
                self.assertEqual(row["body_evidence_type"], "BODY_NOT_ESTABLISHED")
                self.assertEqual(row["service_item_inventory_state"], "NOT_ESTABLISHED")

    def test_fee_classification_matches_canonical_assurance(self):
        assurance = {row["service_id"]: row for row in self.fee["service_projections"]}
        classified = {row["service_id"]: row for row in self.fee_class["services"]}
        self.assertEqual(set(assurance), set(classified))
        self.assertEqual(len(classified), 39)
        self.assertEqual(self.fee_class["summary"]["status_promotions"], 0)

        expected_classes = {
            "CURRENT_CONSOLIDATED_BODY",
            "VERSIONED_BODY_AVAILABLE_NOT_CURRENTNESS_PROOF",
            "COMPARISON_BODY_ONLY",
            "LOCATOR_ONLY",
            "BODY_NOT_ESTABLISHED",
            "NOT_APPLICABLE",
        }
        self.assertEqual(
            set(self.fee_class["summary"]["body_evidence_type_counts"]),
            expected_classes,
        )
        self.assertEqual(self.fee_class["summary"]["current_consolidated_body_services"], [])

        for service_id, source in assurance.items():
            row = classified[service_id]
            self.assertEqual(row["body_evidence_type"], source["evidence_class"])
            self.assertEqual(row["item_body_state"], source["service_level_item_body"])
            self.assertEqual(row["scoped_node_count"], source["scoped_node_count"])
            self.assertEqual(row["verified_node_count"], source["verified_node_count"])
            self.assertFalse(row["currentness_established_by_body_evidence"])

            if source["evidence_class"] in {"COMPARISON_BODY_ONLY", "LOCATOR_ONLY", "BODY_NOT_ESTABLISHED"}:
                self.assertNotEqual(source["service_level_item_body"], "PASS")

    def test_amendment_only_evidence_cannot_become_full_item_body_or_currentness(self):
        projections = {row["service_id"]: row for row in self.fee["service_projections"]}
        amendment_records = [
            row
            for row in self.fee["source_level_verifications"]
            if row.get("verification_kind") == "DIRECT_OFFICIAL_R8_AMENDMENT_COMPARISON"
        ]
        self.assertGreaterEqual(len(amendment_records), 1)

        for record in amendment_records:
            self.assertEqual(record["result"], "PASS_BOUNDED_AMENDMENT_RANGE_ONLY")
            self.assertFalse(record["proves_current_integrated_body"])
            self.assertFalse(record["proves_currentness"])
            for item in record["verified_item_ranges"]:
                self.assertFalse(item["scoped_section_fully_verified"])
            for service_id in record["affected_services"]:
                self.assertNotEqual(projections[service_id]["service_level_item_body"], "PASS")

    def test_comparison_only_cannot_establish_currentness(self):
        comparison_services = [
            row for row in self.fee_class["services"]
            if row["body_evidence_type"] == "COMPARISON_BODY_ONLY"
        ]
        self.assertGreater(len(comparison_services), 0)
        self.assertTrue(all(not row["currentness_established_by_body_evidence"] for row in comparison_services))
        self.assertFalse(self.fee["safety"]["currentness_promoted"])

    def test_incomplete_service_item_set_cannot_pass(self):
        dayservice = next(row for row in self.fee["service_projections"] if row["service_id"] == "dayservice")
        self.assertLess(dayservice["verified_node_count"], dayservice["scoped_node_count"])
        self.assertEqual(dayservice["service_level_item_body"], "PARTIAL")
        self.assertFalse(dayservice["projection_to_pass_permitted"])

    def test_not_applicable_services_keep_not_applicable_body_status(self):
        rem_na = {
            row["service_id"] for row in self.rem["services"]
            if row["projection_state"] == "NOT_APPLICABLE"
        }
        fee_na = {
            row["service_id"] for row in self.fee["service_projections"]
            if row["service_level_item_body"] == "NOT_APPLICABLE"
        }
        expected = {"specific-welfare-equipment-sale", "specific-preventive-welfare-equipment-sale"}
        self.assertEqual(rem_na, expected)
        self.assertEqual(fee_na, expected)


if __name__ == "__main__":
    unittest.main()
