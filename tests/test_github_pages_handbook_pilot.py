"""Independent static handbook extraction audit. No deployment."""
import importlib.util
import contextlib
import io
import json
import re
import tempfile
import unittest
from unittest.mock import patch
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / ".github-pages-handbook-pilot"
SRC = ROOT / ".next/server/app/handbook/dayservice"

spec = importlib.util.spec_from_file_location(
    "handbook_pilot", ROOT / "scripts/build_github_pages_handbook_pilot.py"
)
pilot = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pilot)


class HandbookSanitizerTest(unittest.TestCase):
    def test_native_checkbox_print_button_and_accessibility_survive(self):
        parser = pilot.ArticleSanitizer()
        parser.feed('<article class="handbook-page"><label><input type="checkbox">'
                    '<span aria-hidden="true"></span>確認</label>'
                    '<button type="button">この章のページを印刷・PDF保存</button>'
                    '<script>alert(1)</script></article>')
        output = "".join(parser.chunks)
        self.assertIn('type="checkbox"', output)
        self.assertNotIn("disabled", output)
        self.assertIn('aria-hidden="true"', output)
        self.assertIn('data-handbook-print="true"', output)
        self.assertNotIn("<script", output)
        self.assertNotIn("alert(1)", output)

    def test_unknown_controls_or_graphics_fail_closed(self):
        for fragment in ('<button>送信</button>', '<input type="text">', '<svg></svg>'):
            parser = pilot.ArticleSanitizer()
            with self.assertRaises(RuntimeError, msg=fragment):
                parser.feed('<article class="handbook-page">' + fragment + '</article>')

    def test_synthetic_fifteen_chapter_build_keeps_controls(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            out = root / "pilot"
            source = root / "rendered"
            source.mkdir()
            (root / "data").mkdir()
            chapters = []
            for number in range(1, 16):
                slug = f"chapter-{number}"
                title = f"検証用の章{number}"
                chapters.append({"section_id": slug, "number": number, "title": title})
                (source / (slug + ".html")).write_text(
                    '<article class="handbook-page"><h1>' + title + '</h1>'
                    '<label><input type="checkbox"><span aria-hidden="true"></span>確認</label>'
                    '<button type="button">この章のページを印刷・PDF保存</button></article>',
                    encoding="utf-8",
                )
            (root / "data/handbook.generated.json").write_text(
                json.dumps({"services": [{"service_id": "dayservice", "chapters": chapters}]}),
                encoding="utf-8",
            )
            with patch.multiple(pilot, ROOT=root, OUT=out, CHAPTERS=out / "handbook/dayservice",
                                SOURCE=source), contextlib.redirect_stdout(io.StringIO()):
                summary = pilot.build()
            self.assertEqual(summary["prerendered_public_chapters"], 15)
            page = (out / "handbook/dayservice/chapter-1.html").read_text(encoding="utf-8")
            self.assertIn('data-handbook-print="true"', page)
            self.assertIn('type="checkbox"', page)
            self.assertNotIn("disabled", page)
            self.assertIn('aria-hidden="true"', page)
            self.assertIn('<script defer src="../../print.js"></script>', page)
            self.assertEqual((out / "print.js").read_text(encoding="utf-8"), pilot.PRINT_JS)


class VisibleText(HTMLParser):
    def __init__(self, select_article=False):
        super().__init__(convert_charrefs=True)
        self.select_article = select_article
        self.active = not select_article
        self.depth = 0
        self.banned = []
        self.words = []
        self.checkbox_count = 0
        self.disabled_checkboxes = 0
        self.button_count = 0
        self.aria_hidden_count = 0

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if self.select_article and not self.active and tag == "article" and "handbook-page" in attrs.get("class", "").split():
            self.active = True
            self.depth = 0
        if not self.active:
            return
        if tag == "article":
            self.depth += 1
        if not self.banned:
            if tag == "input" and attrs.get("type") == "checkbox":
                self.checkbox_count += 1
                self.disabled_checkboxes += int("disabled" in attrs)
            if tag == "button":
                self.button_count += 1
            if attrs.get("aria-hidden") == "true":
                self.aria_hidden_count += 1
        if tag in {"script", "style", "svg", "iframe", "noscript", "template", "canvas", "object"}:
            self.banned.append(tag)

    def handle_endtag(self, tag):
        if not self.active:
            return
        if self.banned and self.banned[-1] == tag:
            self.banned.pop()
        if tag == "article":
            self.depth -= 1
            if self.select_article and self.depth == 0:
                self.active = False

    def handle_data(self, value):
        if self.active and not self.banned:
            self.words.append(value)

    @property
    def normalized(self):
        return re.sub(r"\s+", "", "".join(self.words))


@unittest.skipUnless((OUT / "measurement.json").is_file(),
                     "Pilot output is generated after the normal prebuild checks")
class HandbookStaticPilotTest(unittest.TestCase):
    def test_prerendered_articles_keep_visible_text_and_headings(self):
        report = json.loads((OUT / "measurement.json").read_text(encoding="utf-8"))
        self.assertEqual(report["prerendered_public_chapters"], 15)
        self.assertLess(report["static_output_bytes"], 1_000_000_000)
        self.assertEqual(len(report["pages"]), 15)
        for chapter in report["pages"]:
            slug = chapter["chapter"]
            source = SRC / (slug + ".html")
            generated = OUT / "handbook/dayservice" / (slug + ".html")
            self.assertTrue(source.is_file(), slug)
            self.assertTrue(generated.is_file(), slug)
            original = VisibleText(select_article=True)
            original.feed(source.read_text(encoding="utf-8"))
            output = VisibleText(select_article=True)
            output.feed(generated.read_text(encoding="utf-8"))
            self.assertTrue(original.normalized, slug)
            self.assertEqual(output.normalized, original.normalized, slug)
            self.assertEqual(output.checkbox_count, original.checkbox_count, slug)
            self.assertEqual(output.disabled_checkboxes, original.disabled_checkboxes, slug)
            self.assertEqual(output.button_count, original.button_count, slug)
            self.assertEqual(output.aria_hidden_count, original.aria_hidden_count, slug)
            html = generated.read_text(encoding="utf-8")
            self.assertIn('name="robots" content="noindex', html)
            self.assertEqual(html.count("<script"), 1)
            self.assertIn('<script defer src="../../print.js"></script>', html)
            self.assertNotIn("__next", html)
            self.assertNotIn("handbook-preview", html)
            self.assertIn("未確認", html)

    def test_navigation_is_stable_and_security_boundaries_hold(self):
        index = (OUT / "index.html").read_text(encoding="utf-8")
        self.assertEqual(index.count('./handbook/dayservice/'), 15)
        self.assertEqual(index.count("<script"), 1)
        self.assertIn('<script defer src="./print.js"></script>', index)
        self.assertEqual((OUT / "print.js").read_text(encoding="utf-8"), pilot.PRINT_JS)
        self.assertFalse((OUT / "data").exists())
        self.assertFalse((OUT / "handbook-preview").exists())
        report = json.loads((OUT / "measurement.json").read_text(encoding="utf-8"))
        for row in report["pages"]:
            self.assertLess(row["static_html_bytes"], row["source_html_bytes"])
            self.assertGreater(row["source_links"], 1)


if __name__ == "__main__":
    unittest.main()
