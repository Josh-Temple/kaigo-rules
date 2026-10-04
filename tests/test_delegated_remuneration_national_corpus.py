from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import import_delegated_remuneration_national_corpus as national


class DelegatedRemunerationNationalCorpusTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.corpus = json.loads(
            (ROOT / "data/shared/remuneration-delegated/national-corpus.json").read_text(
                encoding="utf-8"
            )
        )
        cls.identity = json.loads(
            (ROOT / "data/shared/remuneration-delegated/node-identity-map.json").read_text(
                encoding="utf-8"
            )
        )

    def test_committed_corpus_passes_structural_validation(self):
        national.validate_committed(self.corpus)

    def test_registered_canonical_sources_are_fully_paginated(self):
        self.assertEqual(self.corpus["coverage"]["source_documents"], 2)
        self.assertEqual(self.corpus["coverage"]["source_pages"], 7)
        documents = {row["source_id"]: row for row in self.corpus["documents"]}
        self.assertEqual(documents["mhlw-fee-notice27-base"]["observed_pages"], 3)
        self.assertEqual(documents["mhlw-fee-criteria95-current"]["observed_pages"], 4)

    def test_national_corpus_expands_beyond_dayservice_fragment(self):
        self.assertEqual(self.corpus["coverage"]["top_level_nodes"], 338)
        self.assertEqual(
            {row["source_id"]: row["top_level_node_count"] for row in self.corpus["documents"]},
            {
                "mhlw-fee-notice27-base": 24,
                "mhlw-fee-criteria95-current": 314,
            },
        )
        self.assertTrue(
            all(".dayservice." not in row["canonical_node_id"] for row in self.corpus["nodes"])
        )

    def test_legacy_top_level_text_is_referenced_not_duplicated(self):
        national_by_id = {
            row["canonical_node_id"]: row for row in self.corpus["nodes"]
        }
        legacy_top_level_ids = [
            row["canonical_node_id"]
            for row in self.identity["nodes"]
            if row["canonical_node_id"] in national_by_id
        ]
        self.assertEqual(len(legacy_top_level_ids), 15)
        for canonical_id in legacy_top_level_ids:
            row = national_by_id[canonical_id]
            self.assertEqual(row["text_storage"]["kind"], "LEGACY_REFERENCE")
            self.assertNotIn("official_text", row)

    def test_inline_shared_nodes_hold_text_once(self):
        inline = [
            row
            for row in self.corpus["nodes"]
            if row["text_storage"]["kind"] == "INLINE_SHARED_CORPUS"
        ]
        self.assertEqual(len(inline), 323)
        self.assertTrue(all(row.get("official_text") for row in inline))

    def test_assurance_remains_fail_closed(self):
        assurance = self.corpus["assurance"]
        self.assertEqual(assurance["item_body_verification"], "NOT_ESTABLISHED")
        self.assertEqual(assurance["currentness"], "NOT_ESTABLISHED")
        self.assertEqual(
            assurance["service_applicability_verification"],
            "NOT_ESTABLISHED",
        )
        self.assertEqual(
            assurance["service_relation_verification"],
            "NOT_ESTABLISHED",
        )
        self.assertEqual(assurance["human_review"], "NOT_REVIEWED")
        self.assertEqual(assurance["publication"], "BLOCKED")
        self.assertEqual(assurance["route_exposure"], "BLOCKED")
        self.assertFalse(assurance["automatic_promotion_allowed"])


if __name__ == "__main__":
    unittest.main()
