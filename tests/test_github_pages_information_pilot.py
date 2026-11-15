"""Information-page snapshot security and rendered text parity tests."""
import importlib.util
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("info_pages", ROOT / "scripts/build_github_pages_information_pilot.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class InformationPilotTest(unittest.TestCase):
    def test_only_explicit_reader_pages_and_no_preview(self):
        self.assertEqual(set(module.PAGES), {
            "start", "overview", "guide", "sources", "handbook-sources",
            "fees/guidance", "fees",
        })
        self.assertEqual("../" * len(Path("fees/guidance").parts) + "styles.css", "../../styles.css")
        self.assertNotIn("services/source-map", module.PAGES)  # Interactive filtering is not a static snapshot.
        self.assertEqual(module.preserve_original_link("/rules/93?service=dayservice"),
                         "https://kaigo-rules.vercel.app/rules/93?service=dayservice")
        self.assertEqual(module.preserve_original_link("#section"), "#section")
        self.assertEqual(module.preserve_original_link("https://www.mhlw.go.jp/"), "https://www.mhlw.go.jp/")
        with self.assertRaises(RuntimeError):
            module.preserve_original_link("/handbook-preview/private")

    def test_nested_fee_information_routes_share_parent_safely(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "source"
            pages = root / ".next/server/app"
            pages.mkdir(parents=True)
            (root / ".next/BUILD_ID").write_text("validated", encoding="utf-8")
            for route, label in module.PAGES.items():
                source = pages / (route + ".html")
                source.parent.mkdir(parents=True, exist_ok=True)
                source.write_text('<article class="answer-page"><h1>' + label +
                                  '</h1></article>', encoding="utf-8")
            out = Path(tmp) / "unpublished"
            out.mkdir()
            rendered = ("<html><main>確認済みの表示内容</main></html>",
                        SimpleNamespace(done=True, text=["確認済みの表示内容"], links=[]))
            with patch.object(module, "ROOT", root), patch.object(
                module.qa, "render_article", return_value=rendered
            ):
                report = module.add_pages(out)
                self.assertEqual(report["pages"], len(module.PAGES))
                self.assertTrue((out / "fees/index.html").is_file())
                self.assertTrue((out / "fees/guidance/index.html").is_file())
                with self.assertRaisesRegex(RuntimeError, "duplicate"):
                    module.add_pages(out)

    def test_exact_article_text_parity_from_mocked_prerendered_html(self):
        snippet = ('<html><body><article class="answer-page"><h1>制度の全体像</h1>'
                   '<p>原典の確認が必要です。</p><a href="/rules/93">基準</a>'
                   '</article><script>unreviewed hydration payload</script></body></html>')
        rendered, original = module.qa.render_article(
            snippet, "説明", module.preserve_original_link, "../styles.css",
        )
        inspected = module.qa.ArticleSnapshot()
        inspected.feed(rendered)
        self.assertEqual("".join(original.text), "".join(inspected.text))
        self.assertIn('href="https://kaigo-rules.vercel.app/rules/93"', rendered)
        self.assertNotIn("unreviewed hydration payload", rendered)
        self.assertIn('content="noindex', rendered)
