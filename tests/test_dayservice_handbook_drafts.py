"""Independent mechanical checks for the *unreviewed* dayservice handbook drafts.

This proves source ID and schema discipline, NOT legal correctness, human review,
currentness or publication approval.
"""
import copy
import hashlib
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DRAFT_PATH = ROOT / "docs/prototypes/data/dayservice-handbook-drafts.v1.json"
HTML_PATH = ROOT / "docs/prototypes/dayservice-handbook.html"
EXPECTED = [
    "applicability", "designation", "staffing", "equipment", "operations",
    "records", "safeguarding", "incident_and_infection", "business_continuity",
    "remuneration", "deductions", "additions", "notifications", "national_qa",
    "sources_and_history",
]
PRIORITY = {
    "staffing", "equipment", "operations", "records",
    "business_continuity", "remuneration", "deductions", "additions",
}
MISSING_SOURCE = {"designation", "notifications", "national_qa", "sources_and_history"}
FORBIDDEN_MARKUP = re.compile(r"<|>|javascript\s*:|data\s*:\s*text/html|onerror\s*=", re.I)
FORBIDDEN_ASSERTIONS = (
    "法的確認済みの手引", "人手レビュー済みの手引",
    "加算の算定を保証", "法的適用を保証", "正式な解釈として確定",
)
EXPECTED_HEAD = "c6e61a44a8287f020d56e1c22d63ad2b74a08b89"
PATHS = {
    "rule": "data/rule-nodes.json",
    "notice": "data/notice-current-skeleton.json",
    "fee": "data/remuneration-current-skeleton.json",
    "sources": "data/sources.json",
}

def fail_if(condition, why):
    if condition:
        raise ValueError(why)

def source_candidates():
    html = HTML_PATH.read_text(encoding="utf-8")
    m = re.search(r"const CANDIDATES=(\[.*?\]);\s*const CANDIDATE_SOURCE_BLOBS=", html, re.S)
    if not m:
        raise ValueError("expected fixed candidate manifest in original HTML")
    candidates = json.loads(m.group(1))
    m2 = re.search(r"const CHAPTERS=(\[.*?\]);\s*const BASE=", html, re.S)
    if not m2:
        raise ValueError("expected fixed chapters in original HTML")
    chapters = json.loads(m2.group(1))
    return candidates, chapters

def validate(doc, candidate_rows, chapter_rows):
    fail_if(not isinstance(doc, dict), "invalid document")
    fail_if(set(doc) != {
        "schema_version", "base_pr_head", "service_id", "source_snapshot",
        "source_contract", "publication_state", "human_review_state",
        "legal_explanations_accepted", "scope_note", "sections",
    }, "unexpected document keys")
    fail_if(doc["schema_version"] != "1.0.0-draft", "schema version mismatch")
    fail_if(doc["base_pr_head"] != EXPECTED_HEAD, "base PR HEAD drift")
    fail_if(doc["source_snapshot"] != "main@098a349c26f35cd9e9ad8f0b7ff54f2068f6a702", "source snapshot drift")
    fail_if(doc["service_id"] != "dayservice", "cross-service draft")
    fail_if(doc["publication_state"] != "PUBLICATION_BLOCKED", "publication promotion")
    fail_if(doc["human_review_state"] != "HUMAN_REVIEW_NOT_DONE", "human review promotion")
    fail_if(type(doc["legal_explanations_accepted"]) is not int or doc["legal_explanations_accepted"] != 0,
            "accepted legal explanations claimed")
    fail_if(not isinstance(doc["scope_note"], str) or not doc["scope_note"].strip(), "scope note missing")
    fail_if(not isinstance(doc["sections"], list) or len(doc["sections"]) != 15, "invalid section count")
    expected = [row[0] for row in chapter_rows]
    fail_if(expected != EXPECTED, "source chapter schema drift")
    fail_if([s.get("section_id") for s in doc["sections"]] != expected, "missing/reordered sections")
    allow = {(r["chapter_id"], r["record_id"]) for r in candidate_rows}
    names = {row[0]: row[1] for row in chapter_rows}
    all_ids = set()
    for sec in doc["sections"]:
        fail_if(set(sec) != {"section_id","title","intended_user_questions","draft_status","draft_statements","gaps"},
                "section keys mismatch")
        sid = sec["section_id"]
        fail_if(sec["title"] != names[sid], "incorrect section title")
        has_sources = any(k[0] == sid for k in allow)
        expected_state = "DRAFT_UNREVIEWED" if has_sources else "NEEDS_SOURCE"
        fail_if(sec["draft_status"] != expected_state, "draft/source boundary wrong")
        fail_if(not isinstance(sec["intended_user_questions"], list) or len(sec["intended_user_questions"]) < 2,
                "insufficient user questions")
        fail_if(any(not isinstance(q,str) or not q.strip() or FORBIDDEN_MARKUP.search(q)
                    for q in sec["intended_user_questions"]), "invalid user question")
        fail_if(not isinstance(sec["draft_statements"],list) or
                len(sec["draft_statements"]) < (5 if sid in PRIORITY else 3), "empty/insufficient draft")
        fail_if(not isinstance(sec["gaps"],list) or not sec["gaps"], "hidden unresolved gaps")
        for gap in sec["gaps"]:
            fail_if(set(gap) != {"gap_id","issue","next_check","status"} or gap["status"] != "UNRESOLVED",
                    "gap falsely closed")
            fail_if(not gap["issue"].strip() or not gap["next_check"].strip(), "empty gap")
        for st in sec["draft_statements"]:
            fail_if(set(st) != {
                "statement_id","section_id","kind","text","candidate_record_ids",
                "basis_scope","unknowns","review_state",
            }, "statement keys mismatch")
            fail_if(st["section_id"] != sid, "statement cross-chapter")
            fail_if(st["statement_id"] in all_ids, "duplicate statement ID")
            all_ids.add(st["statement_id"])
            fail_if(st["review_state"] != "DRAFT_UNREVIEWED", "review status promoted")
            fail_if(st["kind"] not in ("PROVISIONAL_EXPLANATION","CHECKPOINT"), "unapproved statement kind")
            fail_if(not isinstance(st["text"],str) or not st["text"].strip() or
                    FORBIDDEN_MARKUP.search(st["text"]), "invalid markup in draft")
            fail_if(any(term in st["text"] for term in FORBIDDEN_ASSERTIONS), "unsourced legal certainty")
            refs = st["candidate_record_ids"]
            fail_if(not isinstance(refs,list) or len(refs) != len(set(refs)), "invalid refs")
            fail_if(any((sid, r) not in allow for r in refs), "unknown or other-service/chapter source")
            fail_if(st["kind"] == "PROVISIONAL_EXPLANATION" and not refs, "unanchored provisional explanation")
            fail_if(st["kind"] == "PROVISIONAL_EXPLANATION" and "判断できない" not in st["text"],
                    "provisional explanation lacks qualification")
            expected_basis = "EXISTING_CANDIDATE_POINTER_ONLY" if refs else "UNSOURCED_RESEARCH_PROMPT_ONLY"
            fail_if(st["basis_scope"] != expected_basis, "untrusted basis scope")
            fail_if(not isinstance(st["unknowns"],list) or not st["unknowns"] or
                    any(not isinstance(t,str) or not t.strip() for t in st["unknowns"]), "unknowns hidden")
    fail_if({s["section_id"] for s in doc["sections"] if s["draft_status"] == "NEEDS_SOURCE"} != MISSING_SOURCE,
            "unmapped chapters not visible")
    fail_if(len(all_ids) < 60, "draft does not provide practical checkpoints")
    return True

class DayserviceDraftTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = json.loads(DRAFT_PATH.read_text(encoding="utf-8"))
        cls.candidates, cls.chapters = source_candidates()

    def test_full_draft_contract(self):
        self.assertTrue(validate(self.doc,self.candidates,self.chapters))

    def test_original_candidate_manifest_exactly_27_and_in_11_chapters(self):
        self.assertEqual(len(self.candidates),27)
        self.assertEqual(len({c["chapter_id"] for c in self.candidates}),11)
        self.assertEqual(len({(c["chapter_id"],c["record_id"]) for c in self.candidates}),27)

    def test_referenced_repository_records_and_blob_identity(self):
        by_kind = {}
        source_blobs = {}
        for kind,rel in PATHS.items():
            raw=(ROOT/rel).read_bytes()
            source_blobs[kind]=hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()
            if kind != "sources":
                by_kind[kind] = {row["id"]:row for row in json.loads(raw)}
        for candidate in self.candidates:
            with self.subTest(record=candidate["record_id"]):
                self.assertEqual(candidate["source_blob"],source_blobs[candidate["kind"]])
                original=by_kind[candidate["kind"]][candidate["record_id"]]
                self.assertEqual(candidate["source_status"],original["verification_status"])
                if candidate["kind"] in ("notice","fee"):
                    self.assertIn("通所介護",original["service_scope"])
                else:
                    self.assertIn("通所介護",original["service"])

    def test_no_publication_or_approved_state(self):
        as_text=json.dumps(self.doc,ensure_ascii=False)
        self.assertNotIn('"review_completed": true',as_text)
        self.assertNotIn('"review_state": "HUMAN_REVIEW_ACCEPTED"',as_text)
        self.assertEqual(self.doc["legal_explanations_accepted"],0)
        self.assertEqual(self.doc["publication_state"],"PUBLICATION_BLOCKED")

    def test_negative_mutations_fail_closed(self):
        cases=[]
        def mutation(name,fn):
            d=copy.deepcopy(self.doc)
            fn(d)
            cases.append((name,d))
        mutation("fake_human_review",lambda d:d.update(human_review_state="HUMAN_REVIEW_ACCEPTED"))
        mutation("fake_publication",lambda d:d.update(publication_state="PUBLICATION_READY"))
        mutation("fake_legal_approval",lambda d:d.update(legal_explanations_accepted=True))
        mutation("cross_service",lambda d:d.update(service_id="dayrehab"))
        mutation("source_snapshot_tampering",lambda d:d.update(source_snapshot="main@untrusted"))
        mutation("missing_section",lambda d:d["sections"].pop())
        mutation("duplicate_section",lambda d:d["sections"].__setitem__(1,copy.deepcopy(d["sections"][0])))
        mutation("empty_gap",lambda d:d["sections"][0].update(gaps=[]))
        mutation("promote_statement_review",lambda d:d["sections"][0]["draft_statements"][0].update(review_state="REVIEWED"))
        mutation("unanchored_explanation",lambda d:d["sections"][0]["draft_statements"][0].update(candidate_record_ids=[],basis_scope="UNSOURCED_RESEARCH_PROMPT_ONLY"))
        mutation("unknown_record",lambda d:d["sections"][0]["draft_statements"][0].update(candidate_record_ids=["fake.article999"]))
        mutation("cross_chapter_reference",lambda d:d["sections"][0]["draft_statements"][0].update(candidate_record_ids=["fee.dayservice.note.10"]))
        mutation("xss_script",lambda d:d["sections"][0]["draft_statements"][0].update(text="<script>alert(1)</script>"))
        mutation("xss_js_url",lambda d:d["sections"][0]["draft_statements"][0].update(text="javascript:alert(1)"))
        mutation("unknowns_missing",lambda d:d["sections"][0]["draft_statements"][0].update(unknowns=[]))
        mutation("unsourced_certainty",lambda d:d["sections"][0]["draft_statements"][0].update(text="法的確認済みの手引"))
        mutation("spoof_field",lambda d:d.update(verified=True))
        mutation("wrong_basis_scope",lambda d:d["sections"][0]["draft_statements"][0].update(basis_scope="TRUSTED_CURRENT"))
        mutation("unknown_kind",lambda d:d["sections"][0]["draft_statements"][0].update(kind="OFFICIAL_INTERPRETATION"))
        mutation("duplicate_statement_id",lambda d:d["sections"][0]["draft_statements"][1].update(statement_id=d["sections"][0]["draft_statements"][0]["statement_id"]))
        self.assertGreaterEqual(len(cases),12)
        for name,mutated in cases:
            with self.subTest(negative=name):
                with self.assertRaises((ValueError,KeyError,TypeError)):
                    validate(mutated,self.candidates,self.chapters)

if __name__ == "__main__":
    unittest.main()
