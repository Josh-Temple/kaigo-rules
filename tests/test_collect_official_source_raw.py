"""No-network tests for an opt-in official raw byte collector."""

from __future__ import annotations

import hashlib
import io
from pypdf import PdfWriter
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


def valid_pdf():
    out = io.BytesIO()
    writer = PdfWriter()
    writer.add_blank_page(width=72, height=72)
    writer.write(out)
    return out.getvalue()


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
        raw = valid_pdf()
        opener = FakeOpener(FakeResponse(raw, content_type="application/pdf",
                                         extra={"Content-Length": str(len(raw))}))
        result = collector.download(self.url, "sample", self.path, opener=opener)
        self.assertEqual((self.path / "sample.raw").read_bytes(), raw)
        self.assertEqual(result["sha256"], hashlib.sha256(raw).hexdigest())
        self.assertEqual(result["publication_decision"], "NOT_AUTHORIZED")
        self.assertEqual(result["legal_currentness"], "NOT_ASSESSED")
        receipt = json.loads((self.path / "sample.receipt.json").read_text())
        self.assertEqual(receipt["byte_count"], len(raw))
        self.assertEqual(opener.calls[0][0], self.url)
        self.assertGreater(opener.calls[0][1], 0)
        self.assertLessEqual(opener.calls[0][1], collector.MAX_SECONDS)

    def test_dry_run_never_needs_network_or_creates_files(self):
        # Only the explicit collector download function opens a socket;
        # print-only CLI mode can never invoke it.
        with mock.patch.object(sys, "argv", [
            "collect_official_source_raw.py",
            "--url", self.url, "--name", "sample",
            "--output-dir", str(self.path), "--expect-media-type", "application/pdf",
        ]), mock.patch.object(collector, "download") as dl:
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
        opener = FakeOpener(redirect(self.url, target), FakeResponse(valid_pdf(), content_type="application/pdf"))
        result = collector.download(self.url, "sample", self.path, opener=opener)
        self.assertEqual(result["final_url"], target)
        self.assertEqual(len(result["redirects"]), 1)

    def test_reject_missing_or_wrong_content_type(self):
        for mime in ("text/html", ""):
            opener = FakeOpener(FakeResponse(valid_pdf(), content_type=mime))
            with self.assertRaises(collector.ReceiptError):
                collector.download(self.url, "sample", self.path, opener=opener)
        self.assertFalse((self.path / "sample.raw").exists())

    def test_reject_oversized_payload_without_residual_files(self):
        opener = FakeOpener(FakeResponse(b"%PDF-large", content_type="application/pdf"))
        with self.assertRaises(collector.ReceiptError):
            collector.download(self.url, "sample", self.path, opener=opener, max_bytes=3)
        self.assertEqual(list(self.path.iterdir()), [])

    def test_reject_response_length_mismatch(self):
        opener = FakeOpener(FakeResponse(valid_pdf(), content_type="application/pdf", extra={"Content-Length": "1"}))
        with self.assertRaises(collector.ReceiptError):
            collector.download(self.url, "sample", self.path, opener=opener)
        self.assertFalse((self.path / "sample.raw").exists())

    def test_reject_compressed_response(self):
        opener = FakeOpener(FakeResponse(valid_pdf(), content_type="application/pdf", extra={"Content-Encoding": "gzip"}))
        with self.assertRaises(collector.ReceiptError):
            collector.download(self.url, "sample", self.path, opener=opener)

    def test_reject_http_status_errors(self):
        opener = FakeOpener(FakeResponse(valid_pdf(), status=203, content_type="application/pdf"))
        with self.assertRaises(collector.ReceiptError):
            collector.download(self.url, "sample", self.path, opener=opener)

    def test_reject_wrong_explicit_expected_media_type(self):
        opener = FakeOpener(FakeResponse(valid_pdf(), content_type="application/pdf"))
        with self.assertRaises(collector.ReceiptError):
            collector.download(
                self.url, "sample", self.path, opener=opener,
                expected_media_type="application/json",
            )

    def test_reject_unsupported_expected_media_type(self):
        with self.assertRaises(collector.ReceiptError):
            collector.download(
                self.url, "sample", self.path, opener=FakeOpener(),
                expected_media_type="image/svg+xml",
            )

    def test_reject_html_with_pdf_mime(self):
        opener = FakeOpener(FakeResponse(b"<html>error</html>", content_type="application/pdf"))
        with self.assertRaises(collector.ReceiptError):
            collector.download(self.url, "sample", self.path, opener=opener)



class IndependentCollectorSafetyTests(unittest.TestCase):
    setUp = OfficialCollectorTests.setUp
    def run_pdf(self,opener=None,**kw):
        return collector.download(self.url,'sample',self.path,opener=opener or FakeOpener(FakeResponse(valid_pdf(),content_type='application/pdf')),**kw)
    def test_api_default_never_builds_network_opener(self):
        with mock.patch.object(collector,'build_opener') as b,self.assertRaises(collector.ReceiptError):collector.download(self.url,'sample',self.path)
        b.assert_not_called()
    def test_duplicate_content_type_rejected(self):
        r=FakeResponse(valid_pdf(),content_type='application/pdf');r._headers['Content-Type']='text/html'
        with self.assertRaises(collector.ReceiptError):self.run_pdf(FakeOpener(r))
    def test_duplicate_content_length_rejected(self):
        r=FakeResponse(valid_pdf(),content_type='application/pdf');r._headers['Content-Length']='1';r._headers['Content-Length']='2'
        with self.assertRaises(collector.ReceiptError):self.run_pdf(FakeOpener(r))
    def test_unrecorded_opener_redirect_rejected(self):
        r=FakeResponse(valid_pdf(),content_type='application/pdf');r.geturl=lambda:'https://mirror.example/a.pdf'
        with self.assertRaises(collector.ReceiptError):self.run_pdf(FakeOpener(r))
    def test_symlink_directory_rejected(self):
        alias=self.path/'alias';alias.symlink_to(self.path,target_is_directory=True)
        with self.assertRaises(collector.ReceiptError):collector.download(self.url,'sample',alias,opener=FakeOpener())
    def test_dangling_output_symlink_preserved(self):
        target=self.path/'sample.raw';target.symlink_to(self.path/'absent')
        with self.assertRaises(collector.ReceiptError):self.run_pdf(FakeOpener())
        self.assertTrue(target.is_symlink())
    def test_repository_output_rejected(self):
        with self.assertRaises(collector.ReceiptError):collector.download(self.url,'sample',Path(collector.__file__).resolve().parent,opener=FakeOpener())
    def test_group_writable_directory_rejected(self):
        self.path.chmod(0o770)
        with self.assertRaises(collector.ReceiptError):self.run_pdf(FakeOpener())
    def test_directory_replacement_race_rejected_without_escape(self):
        original=self.path/'original';original.mkdir();backup=self.path/'backup';escape=self.path/'escape';escape.mkdir()
        class Swap(FakeOpener):
            def open(this,*a,**k):
                original.rename(backup);original.symlink_to(escape,target_is_directory=True)
                return super().open(*a,**k)
        with self.assertRaises(collector.ReceiptError):collector.download(self.url,'sample',original,opener=Swap(FakeResponse(valid_pdf(),content_type='application/pdf')))
        self.assertEqual(list(escape.iterdir()),[]);self.assertEqual(list(backup.iterdir()),[])
    def test_concurrent_name_lock_does_not_remove_other_lock(self):
        lock=self.path/'.sample.collect.lock';lock.write_bytes(b'other')
        with self.assertRaises(FileExistsError):self.run_pdf(FakeOpener())
        self.assertEqual(lock.read_bytes(),b'other')
    def test_late_receipt_collision_rolls_back_own_raw_only(self):
        import os
        real_link=os.link
        def link(src,dst,**kw):
            if dst=='sample.receipt.json':
                (self.path/dst).write_bytes(b'competitor');raise FileExistsError('late fixture')
            return real_link(src,dst,**kw)
        with mock.patch.object(collector.os,'link',side_effect=link),self.assertRaises(FileExistsError):self.run_pdf()
        self.assertFalse((self.path/'sample.raw').exists());self.assertEqual((self.path/'sample.receipt.json').read_bytes(),b'competitor')
    def test_rollback_never_deletes_replaced_raw(self):
        import os
        real_link=os.link
        def link(src,dst,**kw):
            if dst=='sample.receipt.json':
                p=self.path/'sample.raw';p.unlink();p.write_bytes(b'competitor');raise FileExistsError('late fixture')
            return real_link(src,dst,**kw)
        with mock.patch.object(collector.os,'link',side_effect=link),self.assertRaises(FileExistsError):self.run_pdf()
        self.assertEqual((self.path/'sample.raw').read_bytes(),b'competitor')
    def test_redirect_limit_rejected(self):
        urls=[self.url]+['https://www.mhlw.go.jp/a'+str(i)+'.pdf' for i in range(6)]
        opener=FakeOpener(*[redirect(a,b) for a,b in zip(urls,urls[1:])])
        with self.assertRaises(collector.ReceiptError):self.run_pdf(opener)
        self.assertEqual(len(opener.calls),6);self.assertEqual(list(self.path.iterdir()),[])
    def test_tls_and_proxy_configuration(self):
        import ssl
        opener=FakeOpener(FakeResponse(valid_pdf(),content_type='application/pdf'))
        with mock.patch.object(collector,'build_opener',return_value=opener) as b:
            collector.download(self.url,'sample',self.path,allow_network=True)
        handlers=b.call_args.args
        self.assertEqual(handlers[0].proxies,{})
        self.assertEqual(handlers[1]._context.verify_mode,ssl.CERT_REQUIRED)
        self.assertTrue(handlers[1]._context.check_hostname)
        self.assertIsInstance(handlers[2],collector.NoRedirect)
    def test_elapsed_time_rejected_and_temps_removed(self):
        with mock.patch.object(collector.time,'monotonic',side_effect=[0,0,31]),self.assertRaises(collector.ReceiptError):self.run_pdf()
        self.assertEqual(list(self.path.iterdir()),[])
    def test_excessive_declared_length_rejected(self):
        r=FakeResponse(valid_pdf(),content_type='application/pdf',extra={'Content-Length':str(collector.MAX_BYTES+1)})
        with self.assertRaises(collector.ReceiptError):self.run_pdf(FakeOpener(r))
    def test_ambiguous_http_framing_rejected(self):
        r=FakeResponse(valid_pdf(),content_type='application/pdf',extra={'Content-Length':'100','Transfer-Encoding':'chunked'})
        with self.assertRaises(collector.ReceiptError):self.run_pdf(FakeOpener(r))
    def test_dryrun_with_socket_and_opener_blocked(self):
        import socket
        from contextlib import redirect_stdout
        with mock.patch.object(sys,'argv',['collector','--url',self.url,'--name','sample','--output-dir',str(self.path),'--expect-media-type','application/pdf']),mock.patch.object(socket,'socket',side_effect=AssertionError('network forbidden')),mock.patch.object(collector,'build_opener',side_effect=AssertionError('network forbidden')),redirect_stdout(io.StringIO()):
            self.assertEqual(collector.main(),0)
        self.assertEqual(list(self.path.iterdir()),[])
    def test_parent_symlink_even_if_resolve_check_is_raced(self):
        real=self.path/'real';real.mkdir();(real/'child').mkdir()
        alias=self.path/'alias';alias.symlink_to(real,target_is_directory=True)
        with mock.patch.object(Path,'resolve',lambda p:p.absolute()),self.assertRaises(OSError):
            collector.download(self.url,'sample',alias/'child',opener=FakeOpener())
        self.assertEqual(list((real/'child').iterdir()),[])


class PostCommitRaceRegressionTests(unittest.TestCase):
    """Same-UID synthetic interference; does not claim hostile-user isolation."""

    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        self.path = Path(self.folder.name)
        self.url = 'https://www.mhlw.go.jp/content/test.pdf'

    def run_pdf(self):
        return collector.download(self.url, 'sample', self.path,
            opener=FakeOpener(FakeResponse(valid_pdf(), content_type='application/pdf')))

    def test_reject_directory_renamed_during_first_publish_link(self):
        original = self.path / 'published'; original.mkdir(mode=0o700)
        moved = self.path / 'moved'
        real_link = collector.os.link
        seen = {'done': False}
        def racing_link(*a, **kw):
            if not seen['done']:
                original.rename(moved)
                original.mkdir(mode=0o700)
                seen['done'] = True
            return real_link(*a, **kw)
        with mock.patch.object(collector.os, 'link', side_effect=racing_link):
            with self.assertRaisesRegex(collector.ReceiptError, 'directory changed'):
                collector.download(self.url, 'sample', original,
                                   opener=FakeOpener(FakeResponse(valid_pdf(), content_type='application/pdf')))
        self.assertEqual(list(original.iterdir()), [])
        self.assertFalse((moved / 'sample.raw').exists())
        self.assertFalse((moved / 'sample.receipt.json').exists())

    def test_reject_raw_substitution_between_pair_links(self):
        real_link = collector.os.link
        def racing_link(*a, **kw):
            result = real_link(*a, **kw)
            if a[1] == 'sample.raw':
                name = self.path / a[1]
                name.unlink()
                name.write_bytes(b'COMPETING RAW')
            return result
        with mock.patch.object(collector.os, 'link', side_effect=racing_link):
            with self.assertRaisesRegex(collector.ReceiptError, 'raw identity/size changed'):
                self.run_pdf()
        self.assertEqual((self.path / 'sample.raw').read_bytes(), b'COMPETING RAW')
        self.assertFalse((self.path / 'sample.receipt.json').exists())

    def test_reject_receipt_substitution_after_second_link(self):
        real_link = collector.os.link
        def racing_link(*a, **kw):
            result = real_link(*a, **kw)
            if a[1] == 'sample.receipt.json':
                name = self.path / a[1]
                name.unlink()
                name.write_bytes(b'COMPETING RECEIPT')
            return result
        with mock.patch.object(collector.os, 'link', side_effect=racing_link):
            with self.assertRaisesRegex(collector.ReceiptError, 'receipt identity/size changed'):
                self.run_pdf()
        self.assertEqual((self.path / 'sample.receipt.json').read_bytes(), b'COMPETING RECEIPT')
        self.assertFalse((self.path / 'sample.raw').exists())

    def test_competing_lock_replacement_is_not_deleted(self):
        real_link = collector.os.link
        lock = self.path / '.sample.collect.lock'
        def racing_link(*a, **kw):
            if a[1] == 'sample.raw':
                lock.unlink()
                lock.write_bytes(b'COMPETING LOCK')
            return real_link(*a, **kw)
        with mock.patch.object(collector.os, 'link', side_effect=racing_link):
            self.run_pdf()
        self.assertEqual(lock.read_bytes(), b'COMPETING LOCK')

if __name__ == "__main__":
    unittest.main()
