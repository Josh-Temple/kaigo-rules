from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from validate_relation_human_review_decisions import (  # noqa: E402
    ReviewContractError,
    validate_decisions,
)


class RelationHumanReviewDecisionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ledger = json.loads(
            (ROOT / "data/relation-human-review-decisions.json").read_text(
                encoding="utf-8"
            )
        )
        cls.evidence = json.loads(
            (ROOT / "data/relation-human-review-evidence-pack.json").read_text(
                encoding="utf-8"
            )
        )
        cls.pilot = json.loads(
            (ROOT / "data/relation-human-review-pilot.json").read_text(
                encoding="utf-8"
            )
        )

    def valid_decision(self):
        item = self.pilot["items"][0]
        return {
            "review_id": item["review_id"],
            "relation_key": item["relation_key"],
            "reviewer_identity": "human-reviewer-1",
            "reviewer_decision": "NEEDS_MORE_EVIDENCE",
            "reviewer_rationale": "The relation requires additional legal-semantic support.",
            "reviewed_at": "2026-10-06T02:30:00+09:00",
            "evidence_fingerprint_sha256": item["evidence_fingerprint_sha256"],
            "reviewer_attestation": "HUMAN_REVIEW_COMPLETED",
            "decision_state": "CURRENT",
        }

    def with_decision(self, decision):
        ledger = copy.deepcopy(self.ledger)
        ledger["decisions"] = [decision]
        return ledger

    def test_empty_committed_ledger_keeps_all_pilot_items_unreviewed(self):
        result = validate_decisions(self.ledger, self.evidence, self.pilot)
        self.assertEqual(result["decision_records"], 0)
        self.assertEqual(result["current_human_decisions"], 0)
        self.assertEqual(result["stale_evidence_decisions"], 0)
        self.assertEqual(result["unreviewed_pilot_items"], 8)

    def test_valid_current_human_decision_binds_exact_evidence(self):
        result = validate_decisions(
            self.with_decision(self.valid_decision()), self.evidence, self.pilot
        )
        self.assertEqual(result["current_human_decisions"], 1)
        self.assertEqual(result["unreviewed_pilot_items"], 7)

    def test_ai_identity_cannot_satisfy_human_review(self):
        decision = self.valid_decision()
        decision["reviewer_identity"] = "ChatGPT"
        with self.assertRaises(ReviewContractError):
            validate_decisions(
                self.with_decision(decision), self.evidence, self.pilot
            )

    def test_stale_fingerprint_cannot_remain_current(self):
        decision = self.valid_decision()
        decision["evidence_fingerprint_sha256"] = "0" * 64
        with self.assertRaises(ReviewContractError):
            validate_decisions(
                self.with_decision(decision), self.evidence, self.pilot
            )

    def test_stale_decision_can_be_retained_but_not_counted_current(self):
        decision = self.valid_decision()
        decision["evidence_fingerprint_sha256"] = "0" * 64
        decision["decision_state"] = "STALE_EVIDENCE"
        result = validate_decisions(
            self.with_decision(decision), self.evidence, self.pilot
        )
        self.assertEqual(result["current_human_decisions"], 0)
        self.assertEqual(result["stale_evidence_decisions"], 1)
        self.assertEqual(result["unreviewed_pilot_items"], 8)


if __name__ == "__main__":
    unittest.main()
