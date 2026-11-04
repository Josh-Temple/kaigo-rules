"""Offline regression tests for independent, fail-closed static distribution audit."""
import gzip
import hashlib
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

MODULE = Path(__file__).resolve().parents[1] / "scripts/audit_github_pages_scope_gate.py"
spec = importlib.util.spec_from_file_location("kaigo_scope_audit", MODULE)
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)
SHA = "a" * 40
HTML = '<html><head><meta name="robots" content="noindex,nofollow"></head><body>Kaigo Rules 試験公開版</body></html>'


class ScopeGateSafetyTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "site"
        self.root.mkdir()
        self.record_id = "r-100"
        self.qa_id = "qa-200"
        self._write("index.html", HTML)
        self._write("legislation/index.html", HTML)
        self._write("legislation/records.json", json.dumps({
            "docs": [{"id": "doc-1", "title": "資料"}],
            "records": [{"id": self.record_id, "document": "doc-1"}],
        }))
        self._write("legislation/record-index.json", json.dumps({
            self.record_id: {"document": "doc-1"}
        }))
        digest = hashlib.sha256(self.record_id.encode()).hexdigest()
        self._write("legislation/record/" + digest + ".html", HTML)
        self._write("databases/search/services.json", "[]")
        self._write("databases/search/global.json", json.dumps({
            "law": [{"id": "law-1", "href": "/law/1"}],
            "qa": [{"id": self.qa_id, "href": "/qa/qa-200"}],
        }))
        original = (self.root / "databases/search/global.json").read_bytes()
        (self.root / "databases/search/global.json.gz").write_bytes(gzip.compress(original))
        for name in ("index.html", "reader.html"):
            self._write("databases/search/qa-details/" + self.qa_id + "/" + name, HTML)
        approved = lambda key: {
            "id": key, "publish_approved": True,
            "state": "APPROVED_FOR_PUBLICATION", "source_url": "https://www.mhlw.go.jp/"
        }
        self.approval = {
            "schema_version": 1, "source_sha": SHA, "decision": "D_ACCEPTED_SCOPED",
            "records": {
                "legal": [approved(self.record_id)],
                "documents": [approved("doc-1")],
                "qa": [approved(self.qa_id)],
                "search": {
                    "global.json:law": [approved("law-1")],
                    "global.json:qa": [approved(self.qa_id)],
                },
            },
        }
        self.refresh_hashes()

    def _write(self, rel, text):
        p = self.root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")

    def refresh_hashes(self):
        self.approval["file_sha256"] = {
            p.relative_to(self.root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in self.root.rglob("*") if p.is_file()
        }

    def run_check(self, approval=None):
        return audit.inspect(self.root, source_sha=SHA,
            approval=self.approval if approval is None else approval)[0]

    def assert_blocked(self, expected):
        report = self.run_check()
        self.assertEqual(report["status"], "HOLD_NO_DEPLOY", report)
        self.assertIn(expected, report["error_codes"])

    def test_matching_scoped_bytes_pass_without_authorizing_release(self):
        result = self.run_check()
        self.assertEqual(result["status"], "PASS_SCOPED_BYTES_ONLY")
        self.assertEqual(result["noindex_html_count"], result["html_count"])
        self.assertEqual(result["beta_banner_html_count"], result["html_count"])
        self.assertEqual(result["approved_scope_counts"]["legal"], 1)
        self.assertNotIn("file_sha256", result)  # no full inventory in public logs

    def test_no_independent_approval_is_hold_even_when_site_looks_safe(self):
        result, _ = audit.inspect(self.root, source_sha=SHA)
        self.assertEqual(result["status"], "HOLD_NO_DEPLOY")
        self.assertIn("NO_INDEPENDENT_APPROVAL", result["error_codes"])

    def test_unapproved_or_unsourced_record_is_rejected(self):
        self.approval["records"]["legal"][0]["publish_approved"] = False
        self.assert_blocked("UNAPPROVED_OR_UNSOURCED_LEGAL")

    def test_unknown_id_cannot_hide_behind_a_recomputed_hash(self):
        data = json.loads((self.root / "databases/search/global.json").read_text())
        data["law"].append({"id": "unknown", "href": "/law/999"})
        self._write("databases/search/global.json", json.dumps(data))
        raw = (self.root / "databases/search/global.json").read_bytes()
        (self.root / "databases/search/global.json.gz").write_bytes(gzip.compress(raw))
        self.refresh_hashes()
        self.assert_blocked("SEARCH_ALLOWLIST_MISMATCH")
        self.assertEqual(self.run_check()["scope_id_difference_counts"]["search_unapproved"], 1)

    def test_duplicate_id_is_rejected_even_with_matching_byte_hashes(self):
        data = json.loads((self.root / "legislation/records.json").read_text())
        data["records"].append(dict(data["records"][0]))
        self._write("legislation/records.json", json.dumps(data))
        self.refresh_hashes()
        self.assert_blocked("DUPLICATE_ID_LEGAL")

    def test_rogue_direct_detail_is_rejected(self):
        self._write("databases/search/qa-details/unapproved/index.html", HTML)
        self.refresh_hashes()
        self.assert_blocked("QA_DIRECT_URL_MISMATCH")

    def test_gzip_must_match_plain_json(self):
        (self.root / "databases/search/global.json.gz").write_bytes(gzip.compress(b'{"law":[]}'))
        self.refresh_hashes()
        self.assert_blocked("GZIP_MISMATCH_OR_OVERSIZE")

    def test_missing_noindex_and_banner_fails(self):
        self._write("index.html", "<html><body>Unlabeled site</body></html>")
        self.refresh_hashes()
        self.assert_blocked("HTML_NOINDEX_MISSING")
        self.assertIn("BETA_BANNER_MISSING", self.run_check()["error_codes"])

    def test_secret_is_detected_without_leaking_value(self):
        self._write("bundle.js", 'const token="ghp_' + "A" * 36 + '";')
        self.refresh_hashes()
        report = self.run_check()
        self.assertIn("POSSIBLE_SECRET", report["error_codes"])
        self.assertNotIn("ghp_", json.dumps(report))

    def test_unapproved_new_file_is_rejected_by_exact_hash_manifest(self):
        self._write("something.js", "const payload='hidden';")
        self.assert_blocked("DISTRIBUTION_BYTES_NOT_APPROVED")

    def test_stale_sha_and_wrong_decision_are_rejected(self):
        self.approval["source_sha"] = "b" * 40
        self.assert_blocked("INVALID_APPROVAL_STATE_OR_SHA")
        self.approval["source_sha"] = SHA
        self.approval["decision"] = "CANDIDATE_SOURCE_MATCH"
        self.assert_blocked("INVALID_APPROVAL_STATE_OR_SHA")

    def test_symlink_is_rejected(self):
        (self.root / "linked").symlink_to(self.root / "index.html")
        self.assert_blocked("SYMLINK_IN_DISTRIBUTION")


if __name__ == "__main__":
    unittest.main()
