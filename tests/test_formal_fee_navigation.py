"""Verify published fee navigation without inventing a unit-price table."""
import tempfile
import unittest
from pathlib import Path

from scripts.rewrite_fee_navigation import rewrite

ORIGIN = "https://kaigo-rules.vercel.app"
COMMON = (
    f'<a href="{ORIGIN}/rules?service=dayservice">基準DB</a>'
    f'<a href="{ORIGIN}/notices?service=dayservice">通知DB</a>'
    f'<a href="{ORIGIN}/fees/unit-price">単価・地域区分</a>'
)


class FeeNavigationTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for name in ("fees", "fees/guidance", "legislation", "databases/search"):
            (self.root / name).mkdir(parents=True, exist_ok=True)
        (self.root / "legislation/index.html").write_text("legislation")
        (self.root / "databases/search/index.html").write_text("search")
        self.fees = self.root / "fees/index.html"
        self.guidance = self.root / "fees/guidance/index.html"
        self.fees.write_text(COMMON +
            f'<a href="{ORIGIN}/fees/criteria">告示27号・95号の構造化データを見る →</a>' +
            f'<a href="{ORIGIN}/fees/unit-price">通所介護の一単位単価を見る →</a>' +
            '<p>制度の現行性は原典で確認してください。</p>')
        self.guidance.write_text(COMMON + f'<a href="{ORIGIN}/fees/root">通所介護費</a>')

    def test_known_links_are_local_and_the_search_is_not_labeled_a_price_table(self):
        self.assertEqual(rewrite(self.root), {"pages_changed": 2, "links_changed": 9})
        fees = self.fees.read_text()
        guidance = self.guidance.read_text()
        self.assertNotIn(ORIGIN, fees + guidance)
        self.assertIn('../legislation/index.html?service=dayservice&amp;category=standards', fees)
        self.assertIn('../../legislation/index.html?service=dayservice&amp;category=notices', guidance)
        self.assertIn('../legislation/index.html?category=criteria', fees)
        self.assertIn('href="../index.html">通所介護の報酬一覧', guidance)
        self.assertIn('地域区分の関連資料を検索（一単位単価表ではありません）', fees)
        self.assertIn('制度の現行性は原典で確認してください。', fees)
        self.assertNotIn('通所介護の一単位単価を見る', fees)

    def test_changed_link_fails_before_either_page_is_modified(self):
        self.guidance.write_text(self.guidance.read_text().replace("通所介護費", "別のラベル"))
        original_fees = self.fees.read_text()
        original_guidance = self.guidance.read_text()
        with self.assertRaisesRegex(RuntimeError, "Expected legacy fee link"):
            rewrite(self.root)
        self.assertEqual(self.fees.read_text(), original_fees)
        self.assertEqual(self.guidance.read_text(), original_guidance)

    def test_missing_target_fails_before_modifying_pages(self):
        (self.root / "legislation/index.html").unlink()
        original = self.fees.read_text()
        with self.assertRaisesRegex(RuntimeError, "target missing"):
            rewrite(self.root)
        self.assertEqual(self.fees.read_text(), original)

    def test_unknown_legacy_link_is_not_silently_dropped(self):
        self.guidance.write_text(self.guidance.read_text() + f'<a href="{ORIGIN}/unknown">unknown</a>')
        original = self.fees.read_text()
        with self.assertRaisesRegex(RuntimeError, "unrecognized legacy link"):
            rewrite(self.root)
        self.assertEqual(self.fees.read_text(), original)


if __name__ == "__main__":
    unittest.main()
