from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from build_verification_registry import build  # noqa: E402
from relation_verification_coverage import build_relation_coverage  # noqa: E402


class VerificationRegistryTests(unittest.TestCase):
    def test_relation_coverage_is_identity_derived(self):
        coverage = build_relation_coverage()
        registry = build()
        relation = registry["relation_verification"]
        summary = registry["summary"]

        self.assertEqual(len(coverage["inventory"]), 188)
        self.assertEqual(len(coverage["verified"]), 130)
        self.assertEqual(len(coverage["remaining"]), 58)
        self.assertEqual(coverage["overlap_relations"], 0)
        self.assertEqual(coverage["identity_validation"], "PASS")
        self.assertTrue(coverage["verified"].issubset(coverage["inventory"]))

        self.assertEqual(relation["inventory_relations"], 188)
        self.assertEqual(relation["independently_verified_relations"], 130)
        self.assertEqual(relation["remaining_unverified_relations"], 58)
        self.assertEqual(
            sum(lane["verified_relations"] for lane in relation["lanes"]),
            len(coverage["verified"]),
        )
        article119_lane = next(
            lane for lane in relation["lanes"] if lane["id"] == "dayrehab-article119"
        )
        self.assertEqual(article119_lane["verified_relations"], 25)
        self.assertEqual(article119_lane["status"], "PASS")
        derived_lane = next(
            lane for lane in relation["lanes"]
            if lane["id"] == "remuneration-source-link-derived"
        )
        self.assertEqual(derived_lane["verified_relations"], 3)
        self.assertEqual(derived_lane["status"], "PASS")
        fee_guidance_lane = next(
            lane for lane in relation["lanes"]
            if lane["id"] == "fee-guidance-to-remuneration"
        )
        self.assertEqual(fee_guidance_lane["verified_relations"], 24)
        self.assertEqual(fee_guidance_lane["status"], "PASS")
        notice_explicit_lane = next(
            lane for lane in relation["lanes"]
            if lane["id"] == "notice-ordinance-explicit-reference"
        )
        self.assertEqual(notice_explicit_lane["verified_relations"], 17)
        self.assertEqual(notice_explicit_lane["status"], "PASS")
        source_link_lane = next(
            lane for lane in relation["lanes"]
            if lane["id"] == "remuneration-source-link-independent"
        )
        self.assertEqual(source_link_lane["verified_relations"], 2)
        self.assertEqual(source_link_lane["status"], "PASS")
        service_identity_lane = next(
            lane for lane in relation["lanes"]
            if lane["id"] == "careact-service-identity"
        )
        self.assertEqual(service_identity_lane["verified_relations"], 2)
        self.assertEqual(service_identity_lane["status"], "PASS")
        self.assertEqual(summary["semantic_or_cross_layer_relations_remaining"], 58)
        self.assertEqual(registry["gaps"][0]["remaining"], 58)
        self.assertEqual(
            registry["gaps"][0]["classification_counts"],
            {
                "MACHINE_SOURCE_REPARSE_CANDIDATE": 0,
                "SOURCE_LINK_FRESHNESS_OR_DIRECT_EVIDENCE_REQUIRED": 1,
                "SEMANTIC_TEXT_CHECK_REQUIRED": 17,
                "CROSS_LAYER_HUMAN_REVIEW_REQUIRED": 4,
                "HUMAN_SEMANTIC_REVIEW_REQUIRED": 36,
            },
        )
        self.assertFalse(relation["automatic_promotion_allowed"])


if __name__ == "__main__":
    unittest.main()
