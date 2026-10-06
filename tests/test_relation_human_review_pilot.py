from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from build_relation_human_review_pilot import build, render_markdown  # noqa: E402


class RelationHumanReviewPilotTests(unittest.TestCase):
    def test_pilot_is_bounded_review_ready_and_non_promoting(self):
        built = build()
        committed = json.loads(
            (ROOT / "data/relation-human-review-pilot.json").read_text(encoding="utf-8")
        )
        self.assertEqual(built, committed)
        self.assertEqual(built["summary"]["items_total"], 8)
        self.assertEqual(built["summary"]["ready_for_human_review"], 8)
        self.assertEqual(built["summary"]["direct_primary_text_both_sides"], 4)
        self.assertEqual(
            built["summary"]["machine_reconstructed_source_direct_target"], 4
        )
        self.assertEqual(
            built["summary"]["remaining_evidence_pack_items_not_in_pilot"], 50
        )
        self.assertFalse(built["review_contract"]["ai_only_completion_allowed"])
        self.assertTrue(
            built["review_contract"]["fingerprint_mismatch_invalidates_current_decision"]
        )

        for item in built["items"]:
            self.assertEqual(item["review_status"], "READY_FOR_HUMAN_REVIEW")
            self.assertTrue(item["source_url"])
            self.assertTrue(item["source_locator"])
            self.assertTrue(item["target_url"])
            self.assertTrue(item["target_locator"])
            self.assertEqual(
                item["target_pointer_status"], "DIRECT_PRIMARY_TEXT_POINTER"
            )
            self.assertTrue(item["source_excerpt"])
            self.assertTrue(item["target_excerpt"])
            self.assertTrue(item["ai_proposal"])
            self.assertTrue(item["competing_interpretation_or_ambiguity"])
            self.assertTrue(item["currentness_caveat"])
            self.assertEqual(len(item["evidence_fingerprint_sha256"]), 64)
            self.assertEqual(
                item["decision_options"],
                [
                    "CONFIRM_RELATION",
                    "REJECT_RELATION",
                    "NEEDS_MORE_EVIDENCE",
                ],
            )
            self.assertNotEqual(
                item["classification"],
                "SOURCE_LINK_FRESHNESS_OR_DIRECT_EVIDENCE_REQUIRED",
            )

        semantics = [item["asserted_relation_semantics"] for item in built["items"]]
        for previous, current in zip(semantics, semantics[1:]):
            self.assertNotEqual(previous, current)

    def test_generated_markdown_matches_committed_review_sheet(self):
        built = build()
        committed = (
            ROOT / "docs/relation-human-review-pilot.generated.md"
        ).read_text(encoding="utf-8")
        self.assertEqual(render_markdown(built), committed)
        self.assertIn("READY_FOR_HUMAN_REVIEW", committed)
        self.assertIn("HUMAN_REVIEW_COMPLETED", committed)


if __name__ == "__main__":
    unittest.main()
