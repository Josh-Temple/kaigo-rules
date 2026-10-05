from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class RelationReviewPacketHardeningTests(unittest.TestCase):
    def test_validator_passes(self):
        proc = subprocess.run(
            [sys.executable, str(ROOT / "scripts/validate_relation_review_packet_hardening.py")],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertIn("machine_safe_closures=0", proc.stdout)

    def test_human_review_fields_remain_blank_and_explicit(self):
        packet = json.loads(
            (ROOT / "data/relation-human-review-packet.json").read_text(encoding="utf-8")
        )
        evidence = json.loads(
            (ROOT / "data/relation-human-review-evidence-pack.json").read_text(encoding="utf-8")
        )

        freshness = json.loads(
            (ROOT / "data/relation-freshness-direct-evidence-assessment.json").read_text(
                encoding="utf-8"
            )
        )

        self.assertEqual(len(packet["items"]), 58)
        self.assertEqual(len(freshness["items"]), 1)
        self.assertEqual(
            len(packet["items"]) + len(freshness["items"]),
            59,
        )
        self.assertEqual(
            freshness["items"][0]["freshness"]["state"],
            "NOT_ESTABLISHED",
        )
        self.assertEqual(
            freshness["items"][0]["closure_assessment"],
            "KEEP_OPEN",
        )
        self.assertEqual(evidence["summary"]["machine_safe_closures"], 0)
        self.assertEqual(
            evidence["summary"]["semantic_text_source_pointer_status_counts"],
            {
                "MACHINE_RECONSTRUCTED_PRIMARY_CANDIDATE": 5,
                "PRIMARY_TEXT_POINTER_INCOMPLETE": 12,
            },
        )

        for item in packet["items"]:
            self.assertEqual(item["review_status"], "NOT_REVIEWED")
            self.assertIsNone(item["reviewer_name"])
            self.assertIsNone(item["reviewer_decision"])
            self.assertIsNone(item["reviewed_at"])
            self.assertTrue(item["ai_proposal"].startswith("KEEP_OPEN."))
            self.assertTrue(item["competing_interpretation_or_ambiguity"])

        for item in evidence["items"]:
            self.assertEqual(item["closure_assessment"], "KEEP_OPEN")
            self.assertFalse(
                item["machine_verifiable_subclaims"]["relation_semantics_verified"]
            )
            self.assertEqual(item["review_status"], "NOT_REVIEWED")
            self.assertIsNone(item["reviewer_name"])
            self.assertIsNone(item["reviewer_decision"])
            self.assertIsNone(item["reviewed_at"])


if __name__ == "__main__":
    unittest.main()
