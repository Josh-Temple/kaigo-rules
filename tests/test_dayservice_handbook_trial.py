"""Regression checks for the unlinked, unreviewed dayservice handbook trial."""
import json
import re
import unittest
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "docs/prototypes/dayservice-handbook.html"
EXPECTED = [
    "applicability", "designation", "staffing", "equipment", "operations",
    "records", "safeguarding", "incident_and_infection", "business_continuity",
    "remuneration", "deductions", "additions", "notifications", "national_qa",
    "sources_and_history",
]


class Tags(HTMLParser):
    def __init__(self):
        super().__init__()
        self.external_scripts = []
        self.external_frames = []

    def handle_starttag(self, tag, attrs):
        props = dict(attrs)
        if tag == "script" and props.get("src"):
            self.external_scripts.append(props["src"])
        if tag in {"iframe", "object", "embed"}:
            self.external_frames.append(tag)


class DayserviceHandbookTrialTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = HTML.read_text(encoding="utf-8")
        match = re.search(r"const CHAPTERS=(\[.*?\]);\s*const BASE=", cls.html, re.DOTALL)
        if match is None:
            raise AssertionError("chapter data is not found")
        cls.chapters = json.loads(match.group(1))

    def test_exact_15_chapters_no_content_claims(self):
        self.assertEqual([row[0] for row in self.chapters], EXPECTED)
        self.assertEqual(len(set(EXPECTED)), 15)
        for row in self.chapters:
            self.assertEqual(len(row), 4)
            self.assertTrue(row[1].strip())
            self.assertTrue(row[2].strip())
        self.assertIn("確認済み制度解説本文は未掲載", self.html)
        self.assertIn("人手レビュー：未実施", self.html)

    def test_no_untrusted_publication_or_external_code(self):
        self.assertIn('review_completed:false', self.html)
        self.assertIn("default-src 'none'", self.html)
        self.assertIn("connect-src 'none'", self.html)
        self.assertIn('noindex,nofollow,noarchive', self.html)
        self.assertNotIn("innerHTML", self.html)
        self.assertNotIn("fetch(", self.html)
        parsed = Tags()
        parsed.feed(self.html)
        self.assertEqual(parsed.external_scripts, [])
        self.assertEqual(parsed.external_frames, [])

    def test_links_are_fixed_known_existing_navigation(self):
        self.assertIn('const BASE="https://kaigo-rules.vercel.app/"', self.html)
        allowed = {
            "databases/search?service=dayservice", "sources", "qa", "rules",
            "notices", "fees", "fees/criteria", "fees/guidance",
        }
        for row in self.chapters:
            self.assertTrue(row[3])
            self.assertTrue(set(row[3]).issubset(allowed))
            self.assertEqual(len(set(row[3])), len(row[3]))

    def test_notes_never_promote_human_review(self):
        self.assertIn('review_completed:false', self.html)
        self.assertIn('localStorage.setItem(key', self.html)
        self.assertIn('JSON.stringify(data,null,2)', self.html)
        self.assertIn('textContent=', self.html)
        self.assertNotIn('VERIFIED_CURRENT', self.html)
        self.assertNotIn('HUMAN_VERIFIED', self.html)


if __name__ == "__main__":
    unittest.main()
