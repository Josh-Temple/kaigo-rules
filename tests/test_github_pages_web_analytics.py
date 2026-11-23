"""Tests for Cloudflare Web Analytics on the generated GitHub Pages site."""
import tempfile
import unittest
from pathlib import Path

from scripts.inject_cloudflare_web_analytics import BEACON_URL, inject, snippet

TOKEN = "b0ce75d6709d4f369cdbcdeb8dbe5d2b"
HTML = (
    '<!doctype html><html lang="ja"><head><title>Page</title>'
    '<meta name="robots" content="noindex,nofollow,noarchive"></head>'
    '<body><main><h1>介護ルール</h1></main></body></html>'
)


class CloudflareWebAnalyticsTests(unittest.TestCase):
    def test_instrument_all_pages_and_verify_without_changing_content(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            nested = root / "handbook" / "homevisit"
            nested.mkdir(parents=True)
            (root / "index.html").write_text(HTML, encoding="utf-8")
            (nested / "staffing.html").write_text(HTML, encoding="utf-8")
            (root / "styles.css").write_text("body{}", encoding="utf-8")
            first = inject(root, TOKEN)
            self.assertEqual(first, {"html_pages": 2, "inserted": 2, "already_instrumented": 0})
            second = inject(root, TOKEN, check_only=True)
            self.assertEqual(second, {"html_pages": 2, "inserted": 0, "already_instrumented": 2})
            third = inject(root, TOKEN)
            self.assertEqual(third["inserted"], 0)
            for page in [root / "index.html", nested / "staffing.html"]:
                content = page.read_text(encoding="utf-8")
                self.assertEqual(content.count(BEACON_URL), 1)
                self.assertIn(snippet(TOKEN), content)
                self.assertIn('content="noindex,nofollow,noarchive"', content)
                self.assertIn("<main><h1>介護ルール</h1></main>", content)
            self.assertEqual((root / "styles.css").read_text(), "body{}")

    def test_reject_malformed_html_and_missing_instrumentation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            page = root / "index.html"
            page.write_text("<html><head></head><body>Oops", encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "closing body"):
                inject(root, TOKEN)
            page.write_text(HTML, encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "tag missing"):
                inject(root, TOKEN, check_only=True)

    def test_reject_wrong_or_duplicate_tag_and_bad_token(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            page = root / "index.html"
            page.write_text(HTML, encoding="utf-8")
            with self.assertRaises(ValueError):
                inject(root, "not-a-token")
            inject(root, TOKEN)
            with self.assertRaisesRegex(RuntimeError, "mismatched"):
                inject(root, "a" * 32, check_only=True)
            page.write_text(page.read_text(encoding="utf-8").replace(
                "</body>", snippet(TOKEN) + "</body>"
            ), encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "duplicate"):
                inject(root, TOKEN, check_only=True)


if __name__ == "__main__":
    unittest.main()
