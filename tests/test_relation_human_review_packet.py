from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from build_relation_human_review_packet import build  # noqa: E402


class RelationHumanReviewPacketTests(unittest.TestCase):
    def test_packet_matches_remaining_relation_queue_without_promotion(self):
        built = build()
        committed = json.loads(
            (ROOT / "data/relation-human-review-packet.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(built, committed)
        self.assertEqual(built["summary"]["items_total"], 57)
        self.assertEqual(built["summary"]["independently_covered_relations"], 130)
        self.assertEqual(built["summary"]["inventory_relations"], 188)
        self.assertEqual(
            built["summary"]["classification_counts"],
            {
                "SEMANTIC_TEXT_CHECK_REQUIRED": 17,
                "CROSS_LAYER_HUMAN_REVIEW_REQUIRED": 4,
                "HUMAN_SEMANTIC_REVIEW_REQUIRED": 36,
            },
        )
        self.assertFalse(built["review_contract"]["automatic_promotion_allowed"])
        self.assertTrue(built["review_contract"]["requires_primary_source_check"])
        self.assertTrue(built["review_contract"]["currentness_is_separate"])

        self.assertNotIn(
            "SOURCE_LINK_FRESHNESS_OR_DIRECT_EVIDENCE_REQUIRED",
            {item["classification"] for item in built["items"]},
        )

        for item in built["items"]:
            self.assertTrue(item["source_file"])
            self.assertIn("source_state", item)
            self.assertIsNone(item["reviewed_by"])
            self.assertIsNone(item["reviewer_rationale"])
            self.assertIsNone(item["reviewer_decision"])
            self.assertIsNone(item["reviewer_note"])
            self.assertIsNone(item["reviewed_at"])
            self.assertIsNotNone(item["source"]["route"])
            self.assertIsNotNone(item["target"]["route"])
            self.assertEqual(
                item["decision_options"],
                [
                    "CONFIRM_RELATION",
                    "REJECT_RELATION",
                    "NEEDS_MORE_EVIDENCE",
                ],
            )


if __name__ == "__main__":
    unittest.main()
