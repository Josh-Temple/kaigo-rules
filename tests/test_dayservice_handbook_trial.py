"""Regression checks for the unlinked, unreviewed dayservice handbook trial."""
import hashlib
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

    @classmethod
    def source_candidates(cls):
        pattern = r"const CANDIDATES=(\[.*?\]);\s*const CANDIDATE_SOURCE_BLOBS="
        match = re.search(pattern, cls.html, re.DOTALL)
        if not match:
            raise AssertionError("candidate source list is missing")
        return json.loads(match.group(1))

    def test_candidates_are_bound_to_real_repository_items(self):
        candidates = self.source_candidates()
        self.assertEqual(len(candidates), 27)
        self.assertEqual(len({row["chapter_id"] for row in candidates}), 11)
        self.assertEqual(len({(r["chapter_id"], r["record_id"]) for r in candidates}), 27)

        paths = {
            "rule": "data/rule-nodes.json",
            "notice": "data/notice-current-skeleton.json",
            "fee": "data/remuneration-current-skeleton.json",
            "sources": "data/sources.json",
        }
        model = {}
        for kind, relative in paths.items():
            path = ROOT / relative
            data = path.read_bytes()
            digest = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
            model[kind] = (json.loads(data), digest)
        snapshot = re.search(
            r"const CANDIDATE_SOURCE_BLOBS=(\{.*?\});\s*const \$=",
            self.html, re.DOTALL,
        )
        self.assertIsNotNone(snapshot)
        recorded = json.loads(snapshot.group(1))
        self.assertEqual(recorded, {k: v[1] for k, v in model.items()})
        official_sources = {r["id"]: r for r in model["sources"][0]}
        indexed = {kind: {r["id"]: r for r in model[kind][0]} for kind in ("rule", "notice", "fee")}

        for row in candidates:
            with self.subTest(row=row["record_id"]):
                self.assertIn(row["chapter_id"], EXPECTED)
                kind = row["kind"]
                self.assertIn(kind, indexed)
                original = indexed[kind][row["record_id"]]
                self.assertEqual(row["source_blob"], model[kind][1])
                self.assertEqual(row["source_status"], original["verification_status"])
                self.assertTrue(row["locator"])
                self.assertIn(row["source_id"], official_sources)
                source = official_sources[row["source_id"]]
                self.assertEqual(row["source_title"], source["title"])
                self.assertEqual(row["official_url"], source["url"])
                self.assertTrue(row["official_url"].startswith("https://www.mhlw.go.jp/"))
                self.assertTrue(row["db_href"].startswith("https://kaigo-rules.vercel.app/"))
                if kind == "rule":
                    self.assertIn("通所介護", original["service"])
                    self.assertEqual(row["source_id"], original["source_id"])
                    self.assertEqual(row["locator"], " / ".join(original["path"]))
                    self.assertEqual(row["excerpt"], original["official_text"])
                    article = re.search(r"article(\d+)", original["id"]).group(1)
                    self.assertEqual(
                        row["db_href"],
                        f"https://kaigo-rules.vercel.app/rules/{article}?service=dayservice",
                    )
                elif kind == "notice":
                    self.assertIn(row["source_id"], [r["source_id"] for r in original["evidence"]])
                    self.assertNotIn("excerpt", row)
                    self.assertEqual(row["db_href"], "https://kaigo-rules.vercel.app/notices")
                else:
                    self.assertEqual(row["source_id"], original["source_id"])
                    self.assertEqual(row["locator"], original["source_locator"])
                    self.assertNotEqual(row["source_status"], "OUT_OF_CORE_SCOPE")
                    self.assertNotIn("excerpt", row)

    def test_unmapped_chapters_and_review_boundary_remain_visible(self):
        candidates = self.source_candidates()
        covered = {r["chapter_id"] for r in candidates}
        self.assertEqual(
            set(EXPECTED) - covered,
            {"designation", "notifications", "national_qa", "sources_and_history"},
        )
        self.assertIn("手引としての確認済み解説：0件", self.html)
        self.assertIn("この手引の人手確認: 未実施", self.html)
        self.assertIn("原典候補", self.html)
        self.assertNotIn("candidate_verified:true", self.html)


if __name__ == "__main__":
    unittest.main()
