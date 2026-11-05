"""Synthetic-only tests of the independent final-byte distribution inventory."""
import copy
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

from scripts import audit_github_pages_reviewed_candidate as auditor

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "reviewed_fixtures", ROOT / "tests/test_github_pages_reviewed_scope.py"
)
fixture_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fixture_module)
SHA = "a" * 40


class FinalByteAuditTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.scope, self.legal, self.qa, self.meta = fixture_module.ReviewedScopeTest().fixture()
        fixture_module.ReviewedScopeTest().generate(
            self.base, (self.scope, self.legal, self.qa, self.meta)
        )
        self.site = self.base / "reviewed-output"

    def check(self, **kwargs):
        return auditor.inspect(self.site, source_sha=SHA, scope=self.scope, **kwargs)[0]

    def assert_hold(self, code, **kwargs):
        result = self.check(**kwargs)
        self.assertEqual(result["status"], "HOLD_NO_DEPLOY", result)
        self.assertIn(code, result["error_codes"], result)

    def test_synthetic_private_scope_all_paths_and_bytes(self):
        result = self.check()
        self.assertEqual(result["status"], "PRIVATE_AUDIT_ONLY", result)
        self.assertFalse(result["deploy_approved"])
        self.assertFalse(result["reviewer_authority_independently_proven"])
        self.assertEqual(result["scoped_id_count"], 2)
        self.assertEqual(result["search_id_count"], 2)
        self.assertEqual(result["html_count"], 4)
        self.assertEqual(result["noindex_html_count"], 4)
        self.assertEqual(result["review_warning_html_count"], 4)

    def test_real_publication_cannot_be_accepted_from_private_generator(self):
        self.assert_hold("PRIVATE_REVIEW_GENERATOR_NOT_PUBLICATION_READY",
                         mode="beta")
        self.assert_hold("INDEPENDENT_RECEIPT_DIGEST_NOT_VERIFIED",
                         mode="public")
        # Even a synthetic "receipt" and a matching digest cannot turn a
        # private review builder into a public release.
        report, hashes = auditor.inspect(self.site, source_sha=SHA, scope=self.scope)
        receipt = {"source_sha": SHA,
                   "distribution_tree_sha256": report["distribution_tree_sha256"],
                   "file_sha256": hashes}
        import hashlib
        raw = json.dumps(receipt).encode()
        self.assert_hold(
            "PRIVATE_REVIEW_GENERATOR_NOT_PUBLICATION_READY",
            mode="beta", receipt=receipt,
            trusted_receipt_sha256=hashlib.sha256(raw).hexdigest(),
            receipt_byte_sha256=hashlib.sha256(raw).hexdigest(),
        )

    def test_extra_html_direct_url_rejected(self):
        extra = self.site / "qa/unreviewed/index.html"
        extra.parent.mkdir(parents=True)
        extra.write_text("<html>UNAPPROVED</html>")
        self.assert_hold("UNAPPROVED_DISTRIBUTION_PATH")

    def test_mutated_search_id_and_search_href_rejected(self):
        path = self.site / "search/rows.json"
        rows = json.loads(path.read_text(encoding="utf-8"))
        rows["rows"][0]["id"] = "unreviewed"
        path.write_text(json.dumps(rows), encoding="utf-8")
        self.assert_hold("SEARCH_APPROVED_ID_MISMATCH")
        self.assert_hold("GZIP_MISMATCH")
        rows["rows"][0]["id"] = self.scope["approvals"][0]["id"]
        rows["rows"][0]["href"] = "../qa/unreviewed/index.html"
        path.write_text(json.dumps(rows), encoding="utf-8")
        self.assert_hold("SEARCH_ROW_OUTSIDE_APPROVED_SCOPE")

    def test_unknown_source_status_and_duplicate_ids_fail(self):
        scope = copy.deepcopy(self.scope)
        scope["approvals"][0]["publish_approved"] = False
        self.assert_hold("UNAPPROVED_SCOPE_ID", scope=scope)
        scope["approvals"][0]["publish_approved"] = True
        scope["approvals"].append(copy.deepcopy(scope["approvals"][0]))
        self.assert_hold("DUPLICATE_SCOPE_ID", scope=scope)

    def test_html_link_escape_and_secret_do_not_enter_output(self):
        file = self.site / "index.html"
        file.write_text(file.read_text(encoding="utf-8") +
                        '<a href="%252e%252e/secret.txt">bad</a>', encoding="utf-8")
        self.assert_hold("UNSAFE_LOCAL_URL")
        file.write_text(file.read_text(encoding="utf-8") +
                        "<script>const x='ghp_" + "A" * 36 + "';</script>", encoding="utf-8")
        result = self.check()
        self.assertIn("POSSIBLE_SECRET", result["error_codes"])
        self.assertNotIn("ghp_", json.dumps(result))

    def test_receipt_cannot_be_reused_after_file_mutation(self):
        result, hashes = auditor.inspect(self.site, source_sha=SHA, scope=self.scope)
        receipt = {"source_sha": SHA,
                   "distribution_tree_sha256": result["distribution_tree_sha256"],
                   "file_sha256": hashes}
        self.assertEqual(self.check(receipt=receipt)["status"], "PRIVATE_AUDIT_ONLY")
        with (self.site / "style.css").open("a", encoding="utf-8") as f:
            f.write("/* byte change */")
        self.assert_hold("DISTRIBUTION_RECEIPT_MISMATCH", receipt=receipt)

    def test_missing_file_and_symlink_fail(self):
        (self.site / "search/app.mjs").unlink()
        self.assert_hold("MISSING_REQUIRED_DISTRIBUTION_PATH")
        (self.site / "link").symlink_to(self.site / "index.html")
        self.assert_hold("SYMLINK_IN_DISTRIBUTION")


if __name__ == "__main__":
    unittest.main()
