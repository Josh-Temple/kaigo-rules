import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class PublicUxFeedbackTest(unittest.TestCase):
    def read(self, path: str) -> str:
        return (ROOT / path).read_text(encoding="utf-8")

    def test_homepage_is_database_first(self):
        home = self.read("app/page.tsx")
        self.assertIn('href="/databases/search"', home)
        self.assertIn("サービスを先に決めなくても", home)
        self.assertLess(home.index('href="/databases/search"'), home.index('href="/services"'))
        self.assertNotIn("INITIAL SCOPE", home)
        self.assertNotIn("CURATED PRACTICAL QUESTIONS / DAY SERVICE", home)

    def test_feedback_is_globally_available_and_page_aware(self):
        navigation = self.read("components/service-navigation.tsx")
        feedback_link = self.read("components/site-feedback-link.tsx")
        feedback_page = self.read("app/feedback/page.tsx")

        self.assertIn("SiteFeedbackLink", navigation)
        self.assertIn('label="フィードバック"', navigation)
        self.assertIn("usePathname", feedback_link)
        self.assertIn("window.location.search", feedback_link)
        self.assertIn('target.set("service"', feedback_link)
        self.assertIn('target.set("q"', feedback_link)
        self.assertIn('target.set("db"', feedback_link)
        self.assertIn('target.set("source_family"', feedback_link)
        for category in ("誤り", "古い", "見つからない", "分かりにくい"):
            self.assertIn('"' + category + '"', feedback_page)
        self.assertIn("内容をコピー", feedback_page)
        self.assertIn("画面の文脈", feedback_page)
        self.assertIn("検索語", feedback_page)
        self.assertIn("個人情報や非公開情報が含まれる場合は削除してください", feedback_page)
        self.assertIn("氏名、利用者情報、事業所の非公開情報", feedback_page)

    def test_public_verification_ui_does_not_fall_back_to_raw_codes(self):
        labels = self.read("lib/public-verification.ts")
        summary = self.read("components/verification-summary.tsx")
        search = self.read("app/databases/search/page.tsx")
        notices = self.read("app/notices/page.tsx")
        guidance = self.read("app/fees/guidance/page.tsx")

        self.assertIn('return labels[value] || "確認情報あり"', labels)
        self.assertIn("<summary>出典・確認情報</summary>", summary)
        self.assertNotIn("content_verification?.evidence", summary)
        self.assertNotIn("本文照合：{notice.content_verification}", search)
        self.assertNotIn("<strong>PASS</strong>", notices)
        self.assertNotIn("現行性HOLD", notices)
        self.assertNotIn("現行性GAP", notices)
        self.assertNotIn("<code>MACHINE_RECONSTRUCTED_NEEDS_HUMAN_CHECK</code>", guidance)
        self.assertNotIn("<code>VERIFIED_CURRENT</code>", guidance)
        self.assertNotIn("本文SHA-256", guidance)


if __name__ == "__main__":
    unittest.main()
