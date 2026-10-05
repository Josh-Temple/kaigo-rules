from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from build_relation_human_review_evidence_pack import build as build_evidence  # noqa: E402
from build_relation_human_review_packet import build as build_packet  # noqa: E402
from validate_relation_human_review_hardening import validate  # noqa: E402


class RelationHumanReviewHardeningTests(unittest.TestCase):
    def test_worker_d_snapshot_is_fail_closed(self):
        result = validate()
        self.assertEqual(result["inventory_relations"], 188)
        self.assertEqual(result["independently_covered_relations"], 129)
        self.assertEqual(result["remaining_relations"], 59)
        self.assertEqual(result["worker_d_review_items"], 58)
        self.assertEqual(result["freshness_sensitive_relations"], 1)
        self.assertEqual(result["all_remaining_relations_accounted_for"], 59)
        self.assertEqual(result["freshness_state"], "NOT_ESTABLISHED")
        self.assertEqual(result["human_only_relations"], 41)
        self.assertEqual(result["semantic_text_relations"], 17)
        self.assertEqual(result["machine_safe_closures"], 0)
        self.assertEqual(result["review_state"], "NOT_REVIEWED")
        self.assertEqual(
            result["semantic_text_source_pointer_status_counts"],
            {
                "MACHINE_RECONSTRUCTED_PRIMARY_CANDIDATE": 5,
                "PRIMARY_TEXT_POINTER_INCOMPLETE": 12,
            },
        )

    def test_packet_separates_ai_proposal_from_human_decision(self):
        packet = build_packet()
        self.assertTrue(packet["review_contract"]["ai_proposal_is_not_human_decision"])
        self.assertTrue(
            packet["review_contract"]["reviewer_identity_required_for_decision"]
        )
        self.assertTrue(
            packet["review_contract"]["review_timestamp_required_for_decision"]
        )
        for item in packet["items"]:
            self.assertEqual(item["review_status"], "NOT_REVIEWED")
            self.assertTrue(item["ai_proposal"].startswith("KEEP_OPEN."))
            self.assertTrue(item["human_judgment_question"])
            self.assertTrue(item["competing_interpretation_or_ambiguity"])
            self.assertIsNone(item["reviewer_name"])
            self.assertIsNone(item["reviewer_decision"])
            self.assertIsNone(item["reviewer_note"])
            self.assertIsNone(item["reviewed_at"])

    def test_semantic_text_relations_do_not_close_from_weak_evidence(self):
        evidence = build_evidence()
        semantic = [
            item for item in evidence["items"]
            if item["classification"] == "SEMANTIC_TEXT_CHECK_REQUIRED"
        ]
        self.assertEqual(len(semantic), 17)
        self.assertTrue(all(item["closure_assessment"] == "KEEP_OPEN" for item in semantic))
        self.assertTrue(
            all(
                not item["machine_verifiable_subclaims"]["relation_semantics_verified"]
                for item in semantic
            )
        )


if __name__ == "__main__":
    unittest.main()
