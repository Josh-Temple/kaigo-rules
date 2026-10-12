"""No-network tests for an opt-in official raw byte collector."""

from __future__ import annotations

import hashlib
import io
import json
import sys
import tempfile
import unittest
from unittest import mock
from email.message import Message
from pathlib import Path
from urllib.error import HTTPError

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import collect_official_source_raw as collector


class FakeResponse(io.BytesIO):
    def __init__(self, data, *, status=200, content_type="text/html", extra=None):
        super().__init__(data)
        self._status = status
        self._headers = Message()
        self._headers["Content-Type"] = content_type
        for key, value in (extra or {}).items():
            self._headers[key] = value

    def getcode(self):
        return self._status

    def info(self):
        return self._headers


class FakeOpener:
    def __init__(self, *responses):
        self.responses = list(responses)
        self.calls = []

    def open(self, request, timeout):
        self.calls.append((request.full_url, timeout))
        item = self.responses.pop(0)
        if isinstance(item, Exception):
            raise item
        return item


def redirect(url, to):
    headers = Message()
    headers["Location"] = to
    return HTTPError(url, 302, "Found", headers, None)


class OfficialCollectorTests(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        self.path = Path(self.folder.name)
        self.url = "https://www.mhlw.go.jp/content/test.pdf"

    def test_valid_offline_fixture_has_both_files_and_no_legal_approval(self):
        raw = b"%PDF-fixture"
        opener = FakeOpener(FakeResponse(raw, content_type="application/pdf",
                                         extra={"Content-Length": str(len(raw))}))
        result = collector.download(self.url, "sample", self.path, opener=opener)
        self.assertEqual((self.path / "sample.raw").read_bytes(), raw)
        self.assertEqual(result["sha256"], hashlib.sha256(raw).hexdigest())
        self.assertEqual(result["publication_decision"], "NOT_AUTHORIZED")
        self.assertEqual(result["legal_currentness"], "NOT_ASSESSED")
        receipt = json.loads((self.path / "sample.receipt.json").read_text())
        self.assertEqual(receipt["byte_count"], len(raw))
        self.assertEqual(opener.calls, [(self.url, collector.MAX_SECONDS)])

    def test_dry_run_never_needs_network_or_creates_files(self):
        # Only the explicit collector download function opens a socket;
        # print-only CLI mode can never invoke it.
        with mock.patch.object(sys, "argv", [
            "collect_official_source_raw.py",
            "--url", self.url, "--name", "sample",
            "--output-dir", str(self.path),
        ]), unittest.mock.patch.object(collector, "download") as dl:
            from contextlib import redirect_stdout
            with redirect_stdout(io.StringIO()) as output:
                self.assertEqual(collector.main(), 0)
            self.assertIn("DRY_RUN_NO_NETWORK", output.getvalue())
            dl.assert_not_called()

    def test_reject_official_host_spoofing(self):
        with self.assertRaises(collector.ReceiptError):
            collector.download("https://www.mhlw.go.jp.evil.example/a", "sample", self.path, opener=FakeOpener())

    def test_reject_http_downgrade(self):
        with self.assertRaises(collector.ReceiptError):
            collector.download("http://www.mhlw.go.jp/a", "sample", self.path, opener=FakeOpener())

    def test_reject_unsafe_name(self):
        with self.assertRaises(collector.ReceiptError):
            collector.download(self.url, "../sample", self.path, opener=FakeOpener())

    def test_reject_duplicate_output_without_overwrite(self):
        (self.path / "sample.raw").write_bytes(b"keep")
        with self.assertRaises(collector.ReceiptError):
            collector.download(self.url, "sample", self.path, opener=FakeOpener())
        self.assertEqual((self.path / "sample.raw").read_bytes(), b"keep")

    def test_reject_redirect_to_other_host(self):
        opener = FakeOpener(redirect(self.url, "https://laws.e-gov.go.jp/other"))
        with self.assertRaises(collector.ReceiptError):
            collector.download(self.url, "sample", self.path, opener=opener)

    def test_accept_same_host_redirect_and_record_chain(self):
        target = "https://www.mhlw.go.jp/content/new.pdf"
        opener = FakeOpener(redirect(self.url, target), FakeResponse(b"%PDF-ok", content_type="application/pdf"))
        result = collector.download(self.url, "sample", self.path, opener=opener)
        self.assertEqual(result["final_url"], target)
        self.assertEqual(len(result["redirects"]), 1)

    def test_reject_missing_or_wrong_content_type(self):
        for mime in ("text/html", ""):
            opener = FakeOpener(FakeResponse(b"%PDF-ok", content_type=mime))
            with self.assertRaises(collector.ReceiptError):
                collector.download(self.url, "sample", self.path, opener=opener)
        self.assertFalse((self.path / "sample.raw").exists())

    def test_reject_oversized_payload_without_residual_files(self):
        opener = FakeOpener(FakeResponse(b"%PDF-large", content_type="application/pdf"))
        with self.assertRaises(collector.ReceiptError):
            collector.download(self.url, "sample", self.path, opener=opener, max_bytes=3)
        self.assertEqual(list(self.path.iterdir()), [])

    def test_reject_response_length_mismatch(self):
        opener = FakeOpener(FakeResponse(b"%PDF-ok", content_type="application/pdf", extra={"Content-Length": "1"}))
        with self.assertRaises(collector.ReceiptError):
            collector.download(self.url, "sample", self.path, opener=opener)
        self.assertFalse((self.path / "sample.raw").exists())

    def test_reject_compressed_response(self):
        opener = FakeOpener(FakeResponse(b"%PDF-ok", content_type="application/pdf", extra={"Content-Encoding": "gzip"}))
        with self.assertRaises(collector.ReceiptError):
            collector.download(self.url, "sample", self.path, opener=opener)

    def test_reject_http_status_errors(self):
        opener = FakeOpener(FakeResponse(b"%PDF-ok", status=203, content_type="application/pdf"))
        with self.assertRaises(collector.ReceiptError):
            collector.download(self.url, "sample", self.path, opener=opener)

    def test_reject_html_with_pdf_mime(self):
        opener = FakeOpener(FakeResponse(b"<html>error</html>", content_type="application/pdf"))
        with self.assertRaises(collector.ReceiptError):
            collector.download(self.url, "sample", self.path, opener=opener)


if __name__ == "__main__":
    unittest.main()
