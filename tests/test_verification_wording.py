import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class VerificationWordingTest(unittest.TestCase):
    def test_verified_faq_list_labels_are_scoped_to_evidence_mapping(self):
        home_search = (ROOT / "components/question-search.tsx").read_text(encoding="utf-8")
        cross_search = (ROOT / "app/search/page.tsx").read_text(encoding="utf-8")

        self.assertIn('"根拠対応確認済み"', home_search)
        self.assertIn('"根拠対応確認済み"', cross_search)
        self.assertIn("根拠対応確認済みの実務ページ", cross_search)
        self.assertNotIn('? "確認済み" : "根拠確認中"', home_search)
        self.assertNotIn('? "確認済み" : "根拠確認中"', cross_search)

    def test_verified_faq_state_has_evidence_mapping_metadata(self):
        questions = json.loads((ROOT / "data/questions.json").read_text(encoding="utf-8"))
        verified = [item for item in questions if item.get("status") == "verified"]

        self.assertGreater(len(verified), 0)
        for item in verified:
            with self.subTest(slug=item.get("slug")):
                self.assertTrue(item.get("last_verified"))
                self.assertTrue(item.get("source_refs"))

    def test_faq_detail_keeps_verification_scope_explanation(self):
        detail = (ROOT / "app/questions/[slug]/page.tsx").read_text(encoding="utf-8")

        self.assertIn("FAQ根拠対応を確認済み", detail)
        self.assertIn("FAQの確認状態と、根拠資料全体の確認状態は別です。", detail)
        self.assertIn("各根拠資料の現行性", detail)


if __name__ == "__main__":
    unittest.main()
