"""Independent static handbook extraction audit. No deployment."""
import importlib.util
import json
import re
import unittest
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / ".github-pages-handbook-pilot"
SRC = ROOT / ".next/server/app/handbook/dayservice"


class VisibleText(HTMLParser):
    def __init__(self, select_article=False):
        super().__init__(convert_charrefs=True)
        self.select_article = select_article
        self.active = not select_article
        self.depth = 0
        self.banned = []
        self.words = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if self.select_article and not self.active and tag == "article" and "handbook-page" in attrs.get("class", "").split():
            self.active = True
            self.depth = 0
        if not self.active:
            return
        if tag == "article":
            self.depth += 1
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
            html = generated.read_text(encoding="utf-8")
            self.assertIn('name="robots" content="noindex', html)
            self.assertNotIn("<script", html)
            self.assertNotIn("__next", html)
            self.assertNotIn("handbook-preview", html)
            self.assertIn("未確認", html)

    def test_navigation_is_stable_and_security_boundaries_hold(self):
        index = (OUT / "index.html").read_text(encoding="utf-8")
        self.assertEqual(index.count('./handbook/dayservice/'), 15)
        self.assertNotIn("<script", index)
        self.assertFalse((OUT / "data").exists())
        self.assertFalse((OUT / "handbook-preview").exists())
        report = json.loads((OUT / "measurement.json").read_text(encoding="utf-8"))
        for row in report["pages"]:
            self.assertLess(row["static_html_bytes"], row["source_html_bytes"])
            self.assertGreater(row["source_links"], 1)


if __name__ == "__main__":
    unittest.main()
