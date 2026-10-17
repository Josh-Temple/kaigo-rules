"""Boundary tests for the bounded public official-source navigation pilot.

This suite does not assert legal accuracy, currentness or human acceptance.
Run: python -m unittest discover -s tests -p 'test_handbook_sources_public_pilot.py' -v
"""
import json
import re
import unittest
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "app/handbook-sources/page.tsx"
DAY = ROOT / "app/services/dayservice/page.tsx"
REHAB = ROOT / "app/services/dayrehab/page.tsx"
DATA = ROOT / "docs/prototypes/evidence-bridges"

class BoundedPublicSourcePilot(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = PAGE.read_text(encoding="utf-8")
        cls.day = DAY.read_text(encoding="utf-8")
        cls.rehab = REHAB.read_text(encoding="utf-8")
        cls.a = json.loads((DATA / "dayservice.json").read_text(encoding="utf-8"))
        cls.b = json.loads((DATA / "dayrehab.json").read_text(encoding="utf-8"))

    def test_29_candidates_from_exact_12_evidence_records(self):
        ids = []
        for service, doc, first, count in [
            ("dayservice", self.a, 1, 11),
            ("dayrehab", self.b, 7, 18),
        ]:
            with self.subTest(service=service):
                self.assertEqual(doc["service_id"], service)
                self.assertEqual(doc["chapter_count"], 15)
                self.assertEqual(len(doc["chapters"]), 15)
                self.assertEqual(doc["candidate_paragraph_count"], count)
                self.assertEqual(
                    {x["task_id"] for x in doc["source_evidence"]},
                    {"KR-EVIDENCE-%03d" % i for i in range(first, first + 6)},
                )
                ref = {x["task_id"]: x for x in doc["source_evidence"]}
                for chapter in doc["chapters"]:
                    for item in chapter["candidate_paragraphs"]:
                        ids.append(item["bridge_id"])
                        self.assertEqual(item["draft_review_state"], "DRAFT_UNREVIEWED")
                        evidence = ref[item["evidence_task_id"]]
                        self.assertEqual(item["evidence_library_file_id"], evidence["library_file_id"])
                        self.assertEqual(item["source_url_from_evidence"], evidence["source_url"])
        self.assertEqual(len(ids), 29)
        self.assertEqual(len(set(ids)), 29)

    def test_does_not_render_unreviewed_handbook_text(self):
        self.assertNotIn("item.text", self.source)
        self.assertNotIn("p.text", self.source)
        self.assertNotIn("dangerouslySetInnerHTML", self.source)
        self.assertNotIn("localStorage", self.source)
        self.assertNotIn("fetch(", self.source)
        self.assertNotIn("process.env.VERCEL_ENV", self.source)
        self.assertIn("item.source_identifiers.join", self.source)
        self.assertIn("item.evidence_task_id", self.source)
        self.assertIn("未レビューの手引本文29文は、この公開ページには掲載していません", self.source)

    def test_noindex_and_user_facing_holds(self):
        self.assertIn("robots: { index: false, follow: false, nocache: true }", self.source)
        for marker in [
            'data.release_gate !== "HOLD_NO_GO"',
            'data.publication !== "BLOCKED"',
            'data.currentness !== "NOT_ESTABLISHED"',
            'data.human_review !== "NOT_REVIEWED"',
            'data.real_project_work_enabled !== false',
            'data.legal_explanations_accepted !== 0',
            "if (!validBridge(", "notFound()",
        ]:
            self.assertIn(marker, self.source)
        self.assertNotIn('href="/handbook-preview"', self.source)
        self.assertNotIn("index: true", self.source)

    def test_links_limit_to_exact_first_party_government_origins(self):
        self.assertIn('url.protocol !== "https:"', self.source)
        self.assertIn('["www.mhlw.go.jp", "laws.e-gov.go.jp"].includes(url.hostname)', self.source)
        self.assertIn("url.username || url.password", self.source)
        self.assertIn("url.port", self.source)
        self.assertIn("safeOfficialUrl(", self.source)
        # Data can contain a non-government GitHub PR. This must remain an
        # unlinked metadata record, not be labeled an official government URL.
        urls = [x["source_url"] for d in (self.a, self.b) for x in d["source_evidence"]]
        self.assertTrue(any(urlsplit(u).hostname == "github.com" for u in urls))
        self.assertTrue(all(urlsplit(u).scheme == "https" for u in urls))

    def test_service_entries_are_scoped_to_bounded_trial(self):
        for src, service in [(self.day, "dayservice"), (self.rehab, "dayrehab")]:
            self.assertIn('href="/handbook-sources#%s"' % service, src)
            self.assertIn("未レビュー", src)
            self.assertNotIn('href="/handbook-preview"', src)
        self.assertIn('href={`/databases/search?service=${id}`}', self.source)

    def test_existing_unreviewed_preview_still_production_404(self):
        preview = (ROOT / "app/handbook-preview/page.tsx").read_text(encoding="utf-8")
        self.assertIn('process.env.VERCEL_ENV !== "preview"', preview)
        self.assertIn("notFound()", preview)

if __name__ == "__main__":
    unittest.main()
