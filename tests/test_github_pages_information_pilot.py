"""Information-page snapshot security and rendered text parity tests."""
import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("info_pages", ROOT / "scripts/build_github_pages_information_pilot.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class InformationPilotTest(unittest.TestCase):
    def test_only_explicit_reader_pages_and_no_preview(self):
        self.assertEqual(set(module.PAGES), {
            "start", "overview", "guide", "sources", "handbook-sources",
            "services/source-map", "fees/guidance",
        })
        self.assertEqual("../" * len(Path("fees/guidance").parts) + "styles.css", "../../styles.css")
        self.assertEqual(module.preserve_original_link("/rules/93?service=dayservice"),
                         "https://kaigo-rules.vercel.app/rules/93?service=dayservice")
        self.assertEqual(module.preserve_original_link("#section"), "#section")
        self.assertEqual(module.preserve_original_link("https://www.mhlw.go.jp/"), "https://www.mhlw.go.jp/")
        with self.assertRaises(RuntimeError):
            module.preserve_original_link("/handbook-preview/private")

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
