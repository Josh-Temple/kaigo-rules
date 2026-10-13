"""Candidate pointers only; no certification of legal currentness or human review."""
import copy
import hashlib
import json
import unittest
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
CANDIDATES = ROOT / "docs/prototypes/data/dayservice-handbook-source-candidates.v2.json"
BASE = "c6e61a44a8287f020d56e1c22d63ad2b74a08b89"
SECTIONS = ("designation", "notifications", "national_qa", "sources_and_history")
FILES = {
    "data/sources.json": "0f23469ce8a5e8a4c892d820be9d40565b8712f2",
    "data/care-insurance-act-scope.json": "8af02781b721c811b377ff0525f74ba64646181d",
    "data/qa-items.json": "1b07808d1afe66ed4799fce4053c5cd8412b37a0",
    "data/notice-current-skeleton.json": "77f656242eb2d5c9a5bd1d6e5d0d581813e51630",
}
ALLOWED_HOSTS = {
    "laws.e-gov.go.jp", "www.mhlw.go.jp", "www.kaigokensaku.mhlw.go.jp"
}
NEEDED = {
    "candidate_id", "section_id", "kind", "record_id", "source_id",
    "source_version", "title", "source_locator", "locator_kind", "source_url",
    "repository_path", "repository_blob_sha", "candidate_status",
    "existing_source_status", "existing_record_status", "currentness_limit",
    "applicability_limit", "reason", "notes",
}


def git_blob_sha(raw):
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()


def assert_valid(payload, root=ROOT):
    def require(ok, message):
        if not ok:
            raise ValueError(message)
    require(payload.get("schema_version") == "2.0-draft", "schema")
    require(payload.get("base_pr_head") == BASE, "base head")
    require(payload.get("service_id") == "dayservice", "service")
    require(payload.get("artifact_status") == "CHAPTER_CANDIDATE_ONLY", "promotion")
    require(payload.get("human_review_status") == "HUMAN_REVIEW_NOT_DONE", "review")
    require(payload.get("publication_status") == "PUBLICATION_BLOCKED", "publication")
    require(payload.get("legal_currentness_acceptance") == "NOT_ESTABLISHED", "currentness")
    sources = {}
    for path, expected in FILES.items():
        raw = (root / path).read_bytes()
        require(git_blob_sha(raw) == expected, "upstream blob drift " + path)
        sources[path] = json.loads(raw)
    provenance = payload.get("source_provenance", [])
    require(isinstance(provenance, list) and len(provenance) == len(FILES), "provenance")
    require({(x.get("repository_path"), x.get("repository_blob_sha")) for x in provenance}
            == set(FILES.items()), "provenance identity")
    registry = {x["id"]: x for x in sources["data/sources.json"]}
    qa = {x["id"]: x for x in sources["data/qa-items.json"]}
    notice = {x["id"]: x for x in sources["data/notice-current-skeleton.json"]}
    scope = sources["data/care-insurance-act-scope.json"]
    sections = payload.get("sections")
    require(isinstance(sections, list), "sections")
    require(tuple(x.get("section_id") for x in sections) == SECTIONS, "section identity")
    seen = set()
    for sec in sections:
        require(sec.get("title") and isinstance(sec.get("gaps"), list)
                and len(sec["gaps"]) > 0, "section gaps")
        require(isinstance(sec.get("candidates"), list) and sec["candidates"], "missing section evidence")
        for c in sec["candidates"]:
            require(isinstance(c, dict) and NEEDED <= set(c), "missing candidate fields")
            require(c["section_id"] == sec["section_id"], "chapter mismatch")
            require(c["candidate_id"] not in seen and c["candidate_id"], "duplicate candidate id")
            seen.add(c["candidate_id"])
            for key in ("title", "source_locator", "source_url", "repository_path",
                        "repository_blob_sha", "currentness_limit", "applicability_limit",
                        "reason", "notes"):
                require(isinstance(c[key], str) and c[key].strip(), "empty " + key)
                require("<script" not in c[key].lower() and "</script" not in c[key].lower(),
                        "script payload")
            require(c["repository_path"] in FILES
                    and c["repository_blob_sha"] == FILES[c["repository_path"]], "blob")
            url = urlsplit(c["source_url"])
            require(url.scheme == "https" and url.hostname in ALLOWED_HOSTS
                    and not url.username and not url.password, "unsafe URL")
            src = registry.get(c["source_id"])
            require(src is not None and c["source_url"] == src["url"], "source identity/URL")
            require(c["existing_source_status"] == src.get("status"), "source status")
            require(c["candidate_status"] in ("CANDIDATE", "HISTORICAL"), "candidate status")
            require(c["currentness_limit"].startswith("CURRENTNESS_NOT_ESTABLISHED"),
                    "false currentness")
            require(c["record_id"] is None or isinstance(c["record_id"], str), "record id")
            kind = c["kind"]
            if kind == "source_registry":
                require(c["record_id"] is None and c["repository_path"] == "data/sources.json"
                        and c["source_locator"] == "id=" + src["id"]
                        and c["locator_kind"] == "REPOSITORY_SOURCE_REGISTRY"
                        and c["existing_record_status"] is None, "registry entry")
            elif kind == "law_scope":
                require(c["record_id"] is None and c["source_id"] == "egov-care-insurance-act"
                        and c["repository_path"] == "data/care-insurance-act-scope.json"
                        and c["source_locator"].startswith("focus_paragraphs.")
                        and c["source_locator"].split(".", 1)[1] in scope["focus_paragraphs"]
                        and c["locator_kind"] == "REPOSITORY_SCOPE_ONLY"
                        and c["existing_record_status"] is None, "law scope")
                article = c["source_locator"].split(".", 1)[1]
                name = "第" + article.replace("-2", "条の2") + ("" if "-2" in article else "条")
                require(name in c["title"], "article label")
            elif kind == "qa_item":
                q = qa.get(c["record_id"])
                require(q is not None and c["repository_path"] == "data/qa-items.json"
                        and q["source_id"] == c["source_id"]
                        and "通所介護" in q.get("service", [])
                        and c["source_locator"] == "source_number=" + q["source_number"]
                        + ";issued_at=" + q["issued_at"]
                        and c["source_version"] == q["issued_at"]
                        and c["existing_record_status"] == q["status"]
                        and c["candidate_status"] == "HISTORICAL", "historical QA")
            elif kind == "notice_item":
                n = notice.get(c["record_id"])
                ev = n.get("evidence", []) if n else []
                require(n is not None and c["repository_path"] == "data/notice-current-skeleton.json"
                        and c["existing_record_status"] == n.get("verification_status")
                        and any(e.get("source_id") == c["source_id"]
                        and e.get("locator") == c["source_locator"] for e in ev)
                        and "通所介護" in n.get("service_scope", ""), "notice evidence")
            else:
                raise ValueError("unknown kind " + str(kind))
            if sec["section_id"] == "national_qa":
                require(kind == "qa_item" and c["record_id"] in qa, "no invented QA59")
    require(len(seen) >= 4, "unexpectedly empty")


class CandidateSourceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = json.loads(CANDIDATES.read_text(encoding="utf-8"))

    def broken(self, mutate):
        payload = copy.deepcopy(self.doc)
        mutate(payload)
        with self.assertRaises(ValueError):
            assert_valid(payload)

    def test_genuine_source_and_all_sections(self):
        assert_valid(self.doc)

    def test_negative_duplicate(self):
        self.broken(lambda d: d["sections"][1]["candidates"][0].update(
            candidate_id=d["sections"][0]["candidates"][0]["candidate_id"]))

    def test_negative_nonexistent_source(self):
        self.broken(lambda d: d["sections"][0]["candidates"][0].update(source_id="fictional"))

    def test_negative_forged_url(self):
        self.broken(lambda d: d["sections"][0]["candidates"][0].update(
            source_url="https://www.mhlw.go.jp.evil.example/path"))

    def test_negative_wrong_service(self):
        self.broken(lambda d: d.update(service_id="homevisit"))

    def test_negative_promoted_review(self):
        self.broken(lambda d: d.update(human_review_status="HUMAN_REVIEW_ACCEPTED"))

    def test_negative_promoted_publication(self):
        self.broken(lambda d: d.update(publication_status="PUBLICATION_READY"))

    def test_negative_forged_historical_status(self):
        self.broken(lambda d: d["sections"][2]["candidates"][0].update(
            candidate_status="CANDIDATE"))

    def test_negative_fabricated_qa59(self):
        self.broken(lambda d: d["sections"][2]["candidates"][0].update(
            record_id="qa.dayservice.2026.59"))

    def test_negative_mismatched_locator(self):
        self.broken(lambda d: d["sections"][0]["candidates"][0].update(
            source_locator="focus_paragraphs.999"))

    def test_negative_mismatched_source_blob(self):
        self.broken(lambda d: d["sections"][0]["candidates"][0].update(
            repository_blob_sha="0" * 40))

    def test_negative_missing_required_field(self):
        self.broken(lambda d: d["sections"][3]["candidates"][0].pop("notes"))

    def test_negative_html_script(self):
        self.broken(lambda d: d["sections"][1]["candidates"][0].update(
            notes="<script>alert(1)</script>"))

    def test_negative_source_status_claim(self):
        self.broken(lambda d: d["sections"][3]["candidates"][0].update(
            existing_source_status="verified_source"))

    def test_negative_duplicate_section(self):
        self.broken(lambda d: d["sections"][0].update(section_id="notifications"))

    def test_negative_false_currentness(self):
        self.broken(lambda d: d["sections"][0]["candidates"][0].update(
            currentness_limit="VERIFIED_CURRENT"))


if __name__ == "__main__":
    unittest.main()
