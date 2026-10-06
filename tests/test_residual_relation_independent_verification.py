from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from build_residual_relation_independent_verification import build  # noqa: E402
from relation_verification_coverage import build_relation_coverage  # noqa: E402


class ResidualRelationIndependentVerificationTests(unittest.TestCase):
    def test_new_lane_adds_exactly_one_relation_without_regression(self) -> None:
        coverage = build_relation_coverage()
        lane_counts = {row["id"]: row["verified_relations"] for row in coverage["lanes"]}
        self.assertEqual(lane_counts["residual-service-definition"], 1)
        self.assertEqual(
            sum(value for key, value in lane_counts.items() if key != "residual-service-definition"),
            129,
        )
        self.assertEqual(len(coverage["verified"]), 130)
        self.assertEqual(len(coverage["remaining"]), 58)
        self.assertEqual(coverage["overlap_relations"], 0)

    def test_only_explicit_service_definition_is_newly_verified(self) -> None:
        inventory = build()
        newly = inventory["newly_verified_relations"]
        self.assertEqual(len(newly), 1)
        self.assertEqual(
            newly[0]["identity"],
            {
                "from": "fee.dayservice.root",
                "relation": "defined_service_by",
                "to": "ordinance37.article.92",
            },
        )
        self.assertEqual(newly[0]["evidence_pattern"], "EXPLICIT_LEGAL_CITATION")

    def test_remaining_relations_fail_closed(self) -> None:
        inventory = build()
        self.assertEqual(inventory["summary"]["remaining_unverified"], 58)
        self.assertTrue(
            all(row["disposition"] == "UNVERIFIED" for row in inventory["remaining_relations"])
        )
        self.assertEqual(
            inventory["classification_counts"],
            {
                "MACHINE_SOURCE_REPARSE_CANDIDATE": 0,
                "SOURCE_LINK_FRESHNESS_OR_DIRECT_EVIDENCE_REQUIRED": 1,
                "SEMANTIC_TEXT_CHECK_REQUIRED": 17,
                "CROSS_LAYER_HUMAN_REVIEW_REQUIRED": 4,
                "HUMAN_SEMANTIC_REVIEW_REQUIRED": 36,
            },
        )

    def test_human_semantic_relations_are_not_machine_promoted(self) -> None:
        inventory = build()
        human_rows = [
            row
            for row in inventory["remaining_relations"]
            if row["classification"] == "HUMAN_SEMANTIC_REVIEW_REQUIRED"
        ]
        self.assertEqual(len(human_rows), 36)
        self.assertTrue(all(row["disposition"] == "UNVERIFIED" for row in human_rows))


if __name__ == "__main__":
    unittest.main()
