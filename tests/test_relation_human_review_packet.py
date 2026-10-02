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
        self.assertEqual(built["summary"]["items_total"], 59)
        self.assertEqual(built["summary"]["independently_covered_relations"], 129)
        self.assertEqual(built["summary"]["inventory_relations"], 188)
        self.assertEqual(
            built["summary"]["classification_counts"],
            {
                "MACHINE_SOURCE_REPARSE_CANDIDATE": 0,
                "SOURCE_LINK_FRESHNESS_OR_DIRECT_EVIDENCE_REQUIRED": 1,
                "SEMANTIC_TEXT_CHECK_REQUIRED": 17,
                "CROSS_LAYER_HUMAN_REVIEW_REQUIRED": 5,
                "HUMAN_SEMANTIC_REVIEW_REQUIRED": 36,
            },
        )
        self.assertFalse(built["review_contract"]["automatic_promotion_allowed"])
        self.assertTrue(built["review_contract"]["requires_primary_source_check"])
        self.assertTrue(built["review_contract"]["currentness_is_separate"])

        for item in built["items"]:
            self.assertIsNone(item["reviewer_decision"])
            self.assertIsNone(item["reviewer_note"])
            self.assertIsNone(item["reviewed_at"])
            self.assertIsNotNone(item["source"]["route"])
            self.assertIsNotNone(item["target"]["route"])
            self.assertIn(
                item["decision_options"],
                [
                    [
                        "CONFIRM_RELATION",
                        "REJECT_RELATION",
                        "NEEDS_MORE_EVIDENCE",
                    ]
                ],
            )


if __name__ == "__main__":
    unittest.main()
