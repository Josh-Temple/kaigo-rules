"""Safety/identity regression for unpublished service handbook evidence bridges.

Run:
    python -m unittest discover -s tests -p 'test_handbook_evidence_bridges.py' -v

No legal currentness, policy approval, browser QA, or publication is asserted.
"""
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROTOTYPES = ROOT / "docs" / "prototypes"
BRIDGES = PROTOTYPES / "evidence-bridges"

def embedded(html, identifier):
    match = re.search(
        r'<script\b[^>]*\bid="' + re.escape(identifier)
        + r'"[^>]*>(.*?)</script>', html, re.DOTALL
    )
    if not match:
        raise AssertionError("Missing static evidence script: " + identifier)
    return json.loads(match.group(1))

def statements(doc):
    return [
        (chapter, p)
        for chapter in doc["chapters"]
        for p in chapter["candidate_paragraphs"]
    ]

class EvidenceBridgeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.a = json.loads((BRIDGES / "dayservice.json").read_text(encoding="utf-8"))
        cls.b = json.loads((BRIDGES / "dayrehab.json").read_text(encoding="utf-8"))
        cls.dayservice_html = (PROTOTYPES / "dayservice-handbook.html").read_text(encoding="utf-8")
        cls.dayrehab_html = (PROTOTYPES / "dayrehab-evidence-handbook.html").read_text(encoding="utf-8")

    def test_15_chapters_and_service_isolation(self):
        for service, doc, count in (("dayservice", self.a, 11), ("dayrehab", self.b, 18)):
            with self.subTest(service=service):
                self.assertEqual(doc["service_id"], service)
                self.assertEqual(doc["chapter_count"], 15)
                ids = [x["section_id"] for x in doc["chapters"]]
                self.assertEqual(len(ids), len(set(ids)))
                self.assertEqual(len(statements(doc)), count)
                self.assertEqual(doc["candidate_paragraph_count"], count)
        self.assertEqual(
            [x["section_id"] for x in self.a["chapters"]],
            [x["section_id"] for x in self.b["chapters"]],
        )

    def test_unique_bridge_ids_and_provenance(self):
        all_ids = set()
        for doc, allowed in ((self.a, set(range(1,7))), (self.b, set(range(7,13)))):
            refs = {r["task_id"]: r for r in doc["source_evidence"]}
            self.assertEqual(len(refs), 6)
            for r in refs.values():
                self.assertEqual(r["service_id"], doc["service_id"])
                self.assertTrue(r["library_file_id"].startswith("libfile_"))
                self.assertRegex(r["byte_sha256"], r"^[0-9a-f]{64}$")
                self.assertGreater(r["size_bytes"], 0)
            for chapter, p in statements(doc):
                self.assertNotIn(p["bridge_id"], all_ids)
                all_ids.add(p["bridge_id"])
                self.assertEqual(p["draft_review_state"], "DRAFT_UNREVIEWED")
                self.assertNotEqual(p["text"], "")
                self.assertEqual(p["evidence_library_file_id"], refs[p["evidence_task_id"]]["library_file_id"])
                self.assertIn(chapter["section_id"], {c["section_id"] for c in doc["chapters"]})
                self.assertIsInstance(p["source_identifiers"], list)
                suffix = int(p["evidence_task_id"].rsplit("-", 1)[1])
                self.assertIn(suffix, allowed)
        self.assertEqual(len(all_ids), 29)

    def test_unreviewed_and_no_go(self):
        for doc in (self.a, self.b):
            self.assertEqual(doc["release_gate"], "HOLD_NO_GO")
            self.assertEqual(doc["publication"], "BLOCKED")
            self.assertEqual(doc["currentness"], "NOT_ESTABLISHED")
            self.assertEqual(doc["human_review"], "NOT_REVIEWED")
            self.assertEqual(doc["legal_explanations_accepted"], 0)
            self.assertFalse(doc["real_project_work_enabled"])
        for chapter in self.b["chapters"]:
            self.assertEqual(chapter["mapping_state"], "PROPOSED_LAYOUT_NOT_VERIFIED")

    def test_exact_static_embedded_manifests(self):
        self.assertEqual(self.a, embedded(self.dayservice_html, "handbook-evidence-bridge-json"))
        self.assertEqual(self.b, embedded(self.dayrehab_html, "dayrehab-evidence-json"))

    def test_existing_dayservice_draft_and_legacy_candidates_remain(self):
        prior = embedded(self.dayservice_html, "handbook-drafts-json")
        extra = embedded(self.dayservice_html, "handbook-sources-json")
        draft_count = sum(len(x["draft_statements"]) for x in prior["sections"])
        candidate_count = sum(len(x["candidates"]) for x in extra["sections"])
        self.assertEqual(draft_count, 65)
        self.assertEqual(candidate_count, 11)
        m = re.search(r"const CANDIDATES=(\[.*?\]);\n", self.dayservice_html, re.DOTALL)
        self.assertIsNotNone(m)
        self.assertEqual(len(json.loads(m.group(1))), 27)
        self.assertIn("renderSupplement(id);renderBridge(id);", self.dayservice_html)
        self.assertIn("unparsed_saved_data", self.dayservice_html)
        self.assertIn("review_completed:false", self.dayservice_html)

    def test_local_only_no_network_and_plain_text(self):
        for html in (self.dayservice_html, self.dayrehab_html):
            self.assertIn("connect-src 'none'", html)
            self.assertIn('name="robots" content="noindex,nofollow,noarchive"', html)
            self.assertNotIn("fetch(", html)
            self.assertNotIn("XMLHttpRequest", html)
            self.assertNotIn("innerHTML", html)
        self.assertIn("textContent=item.text", self.dayservice_html)
        self.assertIn("paragraph(item.text)", self.dayrehab_html)
        self.assertNotIn("localStorage", self.dayrehab_html)

if __name__ == "__main__":
    unittest.main()
