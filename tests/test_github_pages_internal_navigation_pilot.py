"""Exact static navigation: only generated pages may replace production links."""
import importlib.util
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "private_navigation", ROOT / "scripts/localize_github_pages_links_pilot.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class PrivateNavigationTest(unittest.TestCase):
    def test_known_routes_only_and_exact_anchors(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            files = {
                "index.html": '<html><body id="home"></body></html>',
                "services/dayservice/index.html": '<html><body><h1 id="national_qa">手引</h1></body></html>',
                "guide/index.html": '<html><body><h1 id="guide">ガイド</h1></body></html>',
                "handbook/dayservice/staffing.html": '<html><body><h1 id="staff">人員</h1></body></html>',
                "databases/search/index.html": '<html><body><h1 id="search">検索</h1></body></html>',
                "databases/search/qa.html": '<html><body><h1>国Q&A</h1></body></html>',
                "databases/search/qa-details/qa.example/reader.html": '<html><body>読者向け</body></html>',
                "databases/search/legal/rules/dayservice/93.html": '<html><body><h1 id="rule">第93条</h1></body></html>',
            }
            for name, content in files.items():
                p = out / name
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text(content, encoding="utf-8")
            source = out / "handbook/dayservice/staffing.html"
            before = source.read_text(encoding="utf-8") + "".join(
                '<a href="' + target + '">リンク</a>' for target in [
                    "https://kaigo-rules.vercel.app/services/dayservice#national_qa",
                    "https://kaigo-rules.vercel.app/rules/93?service=dayservice#rule",
                    "https://kaigo-rules.vercel.app/qa/qa.example?reader=1",
                    "https://kaigo-rules.vercel.app/databases/search?q=%E7%9C%8B%E8%AD%B7",
                    "https://kaigo-rules.vercel.app/guide#guide",
                    "https://kaigo-rules.vercel.app/services/dayservice#missing",
                    "https://kaigo-rules.vercel.app/notices",
                    "https://www.mhlw.go.jp/official",
                    "https://kaigo-rules.vercel.app/qa/qa.example?preview=1",
                    "https://kaigo-rules.vercel.app/handbook/dayservice/missing",
                ])
            source.write_text(before, encoding="utf-8")
            report = module.localize(out)
            self.assertEqual(report["links_localized"], 5)
            updated = source.read_text(encoding="utf-8")
            self.assertIn('../../services/dayservice/index.html#national_qa', updated)
            self.assertIn('../../databases/search/legal/rules/dayservice/93.html#rule', updated)
            self.assertIn('../../databases/search/qa-details/qa.example/reader.html', updated)
            self.assertIn('../../databases/search/index.html?q=%E7%9C%8B%E8%AD%B7', updated)
            self.assertIn('../../guide/index.html#guide', updated)
            for unchanged in ("#missing", "https://www.mhlw.go.jp/official",
                              "/notices", "?preview=1", "/staffing/missing"):
                self.assertIn(unchanged if unchanged != "/staffing/missing" else "handbook/dayservice/missing", updated)
            self.assertEqual(module.localize(out)["links_localized"], 0)

    def test_refuses_unsafe_unpublished_or_missing_targets(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for link in ("https://kaigo-rules.vercel.app/handbook-preview/x",
                         "https://kaigo-rules.vercel.app/rules/93?service=unknown",
                         "https://kaigo-rules.vercel.app/qa/../../etc/passwd",
                         "https://kaigo-rules.vercel.app@evil.example/qa",
                         "http://kaigo-rules.vercel.app/qa"):
                self.assertIsNone(module.destination(root, link))
