from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from build_relation_human_review_evidence_pack import build  # noqa: E402


class RelationHumanReviewEvidencePackTests(unittest.TestCase):
    def test_evidence_pack_is_complete_and_non_promoting(self):
        built = build()
        committed = json.loads(
            (ROOT / "data/relation-human-review-evidence-pack.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(built, committed)
        self.assertEqual(built["summary"]["items_total"], 58)
        self.assertEqual(built["summary"]["unresolved_items"], 0)
        self.assertEqual(
            built["summary"]["target_resolution_counts"],
            {
                "CURATED_QA": 1,
                "NOTICE": 7,
                "ORDINANCE_CANONICAL_NODE": 50,
            },
        )
        self.assertFalse(
            built["review_contract"]["semantic_decision_included"]
        )
        self.assertFalse(
            built["review_contract"]["automatic_promotion_allowed"]
        )
        self.assertTrue(
            built["review_contract"]["primary_source_check_still_required"]
        )

        self.assertNotIn(
            "SOURCE_LINK_FRESHNESS_OR_DIRECT_EVIDENCE_REQUIRED",
            {item["classification"] for item in built["items"]},
        )

        for item in built["items"]:
            self.assertIsNone(item["reviewer_decision"])
            self.assertIsNone(item["reviewer_note"])
            self.assertTrue(item["source_evidence"]["excerpt"])
            self.assertTrue(item["target_evidence"]["excerpt"])
            self.assertNotEqual(
                item["source_evidence"]["resolution_kind"], "UNRESOLVED"
            )
            self.assertNotIn(
                item["target_evidence"]["resolution_kind"],
                {"UNRESOLVED", "ORDINANCE_UNRESOLVED"},
            )
            if item["target_evidence"]["resolution_kind"].startswith(
                "ORDINANCE_"
            ):
                self.assertTrue(item["target_evidence"]["canonical_ids"])

    def test_legacy_ordinance_ids_resolve_to_reviewable_nodes(self):
        built = build()
        by_target = {
            item["identity"]["to"]: item["target_evidence"]
            for item in built["items"]
        }
        self.assertEqual(
            by_target["ordinance37.article93.1.1"]["canonical_ids"],
            ["ordinance37.article.93.p.1.i.1"],
        )
        self.assertEqual(
            by_target["ordinance37.article32.1-3"]["canonical_ids"],
            [
                "ordinance37.article.32.p.1",
                "ordinance37.article.32.p.2",
                "ordinance37.article.32.p.3",
            ],
        )
        self.assertEqual(
            by_target["ordinance37.article37-2.3"]["canonical_ids"],
            ["ordinance37.article.37-2.p.1.i.3"],
        )
        self.assertEqual(
            by_target["ordinance37.article95.1-2"]["canonical_ids"],
            [
                "ordinance37.article.95.p.1",
                "ordinance37.article.95.p.2",
            ],
        )
        self.assertEqual(
            by_target["ordinance37.article217.2"]["resolution_kind"],
            "ORDINANCE_CANONICAL_NODE",
        )
        self.assertEqual(
            by_target["ordinance37.article217.2"]["canonical_ids"],
            ["ordinance37.article.217.p.2"],
        )


if __name__ == "__main__":
    unittest.main()
