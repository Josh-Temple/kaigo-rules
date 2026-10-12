"""Offline tests for integrity-only source transport receipt validation."""

from __future__ import annotations

import hashlib
import importlib.util
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "check_source_transport_receipt.py"
spec = importlib.util.spec_from_file_location("check_source_transport_receipt", SCRIPT)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(module)


class ReceiptIntegrityTests(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        self.raw = Path(self.folder.name) / "original.bin"
        self.bytes = b"PK\x03\x04" + b"fixture bytes only"
        self.raw.write_bytes(self.bytes)
        self.receipt = {
            "schema_version": 1,
            "observed_at_utc": "2026-10-12T12:01:00Z",
            "request_url": "https://www.mhlw.go.jp/content/example.xlsx",
            "final_url": "https://www.mhlw.go.jp/content/example.xlsx",
            "http_status": 200,
            "redirects": [],
            "response_headers": {"Content-Type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"},
            "byte_count": len(self.bytes),
            "sha256": hashlib.sha256(self.bytes).hexdigest(),
        }

    def reject(self, change):
        receipt = deepcopy(self.receipt)
        change(receipt)
        with self.assertRaises(module.ReceiptError):
            module.check_receipt(receipt, self.raw)

    def test_integrity_only_never_authenticates_original_source(self):
        result = module.check_receipt(self.receipt, self.raw)
        self.assertEqual(result["raw_receipt_integrity"], "CONSISTENT")
        self.assertEqual(result["origin_authenticity"], "NOT_VERIFIED_BY_OFFLINE_CHECK")
        self.assertEqual(result["publication_decision"], "NOT_AUTHORIZED")

    def test_reject_hash_spoof(self):
        self.reject(lambda x: x.update(sha256="0" * 64))

    def test_reject_byte_count_mismatch(self):
        self.reject(lambda x: x.update(byte_count=1))

    def test_reject_http_errors(self):
        self.reject(lambda x: x.update(http_status=404))

    def test_reject_nonofficial_host(self):
        self.reject(lambda x: x.update(final_url="https://www.mhlw.go.jp.evil.test/content/example.xlsx"))

    def test_reject_http(self):
        self.reject(lambda x: x.update(request_url="http://www.mhlw.go.jp/content/example.xlsx"))

    def test_reject_missing_headers(self):
        self.reject(lambda x: x.pop("response_headers"))

    def test_reject_missing_timestamp(self):
        self.reject(lambda x: x.update(observed_at_utc="2026-10-12T12:01:00"))

    def test_reject_discontinuous_redirect(self):
        self.reject(lambda x: x.update(redirects=[{"from_url": "https://www.mhlw.go.jp/other", "to_url": x["final_url"], "status": 302}]))

    def test_reject_redirect_to_third_party(self):
        def change(x):
            x["redirects"] = [{"from_url": x["request_url"], "to_url": "https://mirror.example/other", "status": 302}]
        self.reject(change)

    def test_reject_html_disguised_as_spreadsheet(self):
        self.raw.write_bytes(b"<html>error</html>")
        self.receipt["sha256"] = hashlib.sha256(self.raw.read_bytes()).hexdigest()
        self.receipt["byte_count"] = self.raw.stat().st_size
        self.reject(lambda x: None)

    def test_allow_verified_integrity_redirect_chain_without_origin_claim(self):
        original = self.receipt["request_url"]
        self.receipt["request_url"] = "https://www.mhlw.go.jp/old.xlsx"
        self.receipt["redirects"] = [{"from_url": self.receipt["request_url"], "to_url": original, "status": 302}]
        self.assertEqual(module.check_receipt(self.receipt, self.raw)["legal_currentness"], "NOT_ASSESSED")


if __name__ == "__main__":
    unittest.main()
