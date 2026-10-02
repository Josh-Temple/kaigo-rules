import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class GlobalQaCorpusTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.meta = json.loads((ROOT / "data/qa-corpus-meta.json").read_text(encoding="utf-8"))
        cls.corpus = json.loads((ROOT / "data/qa-corpus.json").read_text(encoding="utf-8"))

    def test_global_corpus_matches_generated_metadata(self):
        self.assertEqual(self.meta["scope_mode"], "ALL_CLASSIFIED_ROWS_IN_OFFICIAL_WORKBOOK")
        self.assertEqual(len(self.corpus), 3695)
        self.assertEqual(self.meta["rows_included"], 3695)
        self.assertEqual(
            sorted({row["service_code"] for row in self.corpus}),
            self.meta["target_service_codes"],
        )
        self.assertIn("17", self.meta["target_service_codes"])
        self.assertIn("23", self.meta["target_service_codes"])
        self.assertIn("48", self.meta["target_service_codes"])
        self.assertIn("50", self.meta["target_service_codes"])
        self.assertIn("51", self.meta["target_service_codes"])
        self.assertIn("XX", self.meta["target_service_codes"])

    def test_every_row_preserves_both_classification_contracts(self):
        self.assertEqual(
            self.meta["service_classification"]["current_scope_column"],
            "平成31年3月15日Q&A以降",
        )
        for row in self.corpus:
            self.assertEqual(
                row["scope"],
                self.meta["scope_by_code"][row["service_code"]],
                row["id"],
            )
            self.assertIn("current_service_scope", row, row["id"])

    def test_public_qa_page_is_metadata_driven(self):
        source = (ROOT / "app/qa/page.tsx").read_text(encoding="utf-8")
        self.assertIn("Object.entries(qaMeta.scope_by_code || {})", source)
        self.assertIn("current_service_scope", source)
        self.assertNotIn('["16", "通所介護"]', source)

    def test_database_entry_reflects_global_qa_scope(self):
        source = (ROOT / "app/databases/page.tsx").read_text(encoding="utf-8")
        self.assertIn("全分類で収載", source)
        self.assertIn("全サービス分類", source)
        self.assertNotIn("現在は共通範囲と通所系・通所介護を収載", source)
        self.assertNotIn("対象サービスを順次拡張", source)

    def test_dayservice_search_and_candidate_generation_remain_scoped(self):
        search = (ROOT / "app/search/page.tsx").read_text(encoding="utf-8")
        suggest = (ROOT / "scripts/suggest-qa-links.mjs").read_text(encoding="utf-8")
        self.assertIn('new Set(["01", "02", "06", "16"])', search)
        self.assertIn('["01", "02", "06", "16"].includes(item.service_code)', suggest)

    def test_global_verification_does_not_promote_human_review(self):
        audit = json.loads(
            (ROOT / "data/qa-corpus-independent-audit.json").read_text(encoding="utf-8")
        )
        layers = json.loads(
            (ROOT / "data/services/verification-layers.json").read_text(encoding="utf-8")
        )
        qa_layer = next(item for item in layers["layers"] if item["id"] == "qa-corpus")
        self.assertEqual(qa_layer["scope_kind"], "GLOBAL")
        self.assertEqual(audit["observed"]["rows_included"], 3695)
        self.assertFalse(audit["safety"]["human_verified"])
        self.assertFalse(audit["safety"]["verified_current"])
        self.assertFalse(audit["safety"]["automatic_promotion_allowed"])


if __name__ == "__main__":
    unittest.main()
