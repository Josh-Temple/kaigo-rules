"""Offline tests for integrity-only source transport receipt validation."""

from __future__ import annotations

import hashlib
import io
import zipfile
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


def valid_xlsx():
    out = io.BytesIO()
    ns = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
    with zipfile.ZipFile(out, "w") as z:
        z.writestr("[Content_Types].xml", '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"/>')
        z.writestr("_rels/.rels", '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"/>')
        z.writestr("xl/_rels/workbook.xml.rels", '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"/>')
        z.writestr("xl/workbook.xml", f'<workbook xmlns="{ns}"><sheets><sheet name="Test" sheetId="1"/></sheets></workbook>')
        z.writestr("xl/worksheets/sheet1.xml", f'<worksheet xmlns="{ns}"><sheetData/></worksheet>')
    return out.getvalue()


class ReceiptIntegrityTests(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        self.raw = Path(self.folder.name) / "original.bin"
        self.bytes = valid_xlsx()
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

    def test_reject_legacy_xls_html_payload_even_with_matching_hash(self):
        self.receipt["request_url"] = "https://www.mhlw.go.jp/content/example.xls"
        self.receipt["final_url"] = self.receipt["request_url"]
        self.receipt["response_headers"]["Content-Type"] = "application/vnd.ms-excel"
        self.raw.write_bytes(b"<html>not excel</html>")
        self.receipt["sha256"] = hashlib.sha256(self.raw.read_bytes()).hexdigest()
        self.receipt["byte_count"] = self.raw.stat().st_size
        with self.assertRaises(module.ReceiptError):
            module.check_receipt(self.receipt, self.raw)

    def test_reject_legacy_xls_cfb_signature_without_workbook(self):
        self.receipt["request_url"] = "https://www.mhlw.go.jp/content/example.xls"
        self.receipt["final_url"] = self.receipt["request_url"]
        self.receipt["response_headers"]["Content-Type"] = "application/vnd.ms-excel"
        self.raw.write_bytes(bytes.fromhex("D0CF11E0A1B11AE1") + b"test-fixture")
        self.receipt["sha256"] = hashlib.sha256(self.raw.read_bytes()).hexdigest()
        self.receipt["byte_count"] = self.raw.stat().st_size
        with self.assertRaises(module.ReceiptError):
            module.check_receipt(self.receipt, self.raw)

    def test_allow_verified_integrity_redirect_chain_without_origin_claim(self):
        original = self.receipt["request_url"]
        self.receipt["request_url"] = "https://www.mhlw.go.jp/old.xlsx"
        self.receipt["redirects"] = [{"from_url": self.receipt["request_url"], "to_url": original, "status": 302}]
        self.assertEqual(module.check_receipt(self.receipt, self.raw)["legal_currentness"], "NOT_ASSESSED")



class IndependentReceiptSafetyTests(unittest.TestCase):
    setUp = ReceiptIntegrityTests.setUp
    reject = ReceiptIntegrityTests.reject
    # Reuse setup, not the baseline test methods, below (base class is changed).
    def test_empty_url_userinfo_rejected(self):
        with self.assertRaises(module.ReceiptError): module._official_host('https://@www.mhlw.go.jp/a.pdf')
    def test_url_controls_and_fragments_rejected(self):
        for u in ['https://www.mhlw.go.jp\n/a.pdf', 'https://www.mhlw.go.jp/a.pdf#', 'https://www.mhlw.go.jp:0443/a.pdf']:
            with self.subTest(url=u), self.assertRaises(module.ReceiptError): module._official_host(u)
    def test_bool_schema_rejected(self): self.reject(lambda r:r.update(schema_version=True))
    def test_corrupt_xlsx_container_rejected(self):
        self.raw.write_bytes(b'PK\x03\x04broken')
        self.receipt.update(byte_count=self.raw.stat().st_size,sha256=hashlib.sha256(self.raw.read_bytes()).hexdigest())
        self.reject(lambda r:None)
    def test_extensionless_pdf_html_rejected(self):
        with self.assertRaises(module.ReceiptError): module._format_check(b'<html>fake</html>', 'application/pdf')
    def test_corrupt_pdf_signature_rejected(self):
        with self.assertRaises(module.ReceiptError): module._format_check(b'%PDF-fake', 'application/pdf')
    def test_unsupported_mime_rejected(self): self.reject(lambda r:r['response_headers'].update({'Content-Type':'image/png'}))
    def test_wrong_offline_content_length_rejected(self): self.reject(lambda r:r['response_headers'].update({'Content-Length':'1'}))
    def test_offline_compressed_response_rejected(self): self.reject(lambda r:r['response_headers'].update({'Content-Encoding':'gzip'}))
    def test_offline_size_bound_rejected(self):
        from unittest.mock import patch
        with patch.object(module,'MAX_BYTES',len(self.bytes)-1):self.reject(lambda r:None)
    def test_raw_symlink_rejected(self):
        p=Path(self.folder.name)/'alias';p.symlink_to(self.raw)
        with self.assertRaises(module.ReceiptError):module.check_receipt(self.receipt,p)
    def test_header_case_duplicate_rejected(self): self.reject(lambda r:r['response_headers'].update({'content-type':'text/html'}))
    def test_xml_entity_declarations_rejected(self):
        for data in [b'<!DOCTYPE a [<!ENTITY x "bad">]><a>&x;</a>', '<!DOCTYPE a><a/>'.encode('utf-16')]:
            with self.assertRaises(module.ReceiptError):module._format_check(data,'application/xml')
    def test_invalid_json_rejected(self):
        for data in [b'{broken}',b'{"x":NaN}']:
            with self.assertRaises(module.ReceiptError):module._format_check(data,'application/json')
    def test_json_xml_html_positive_scopes(self):
        for data,mime in [(b'{"a":1}','application/json'),(b'<Law/>','application/xml'),(b'<html><body>test</body></html>','text/html')]:
            self.assertIsInstance(module._format_check(data,mime),str)
    def test_xlsx_crc_corruption_rejected(self):
        data=valid_xlsx().replace(b'<sheetData/>',b'<sheetDatz/>',1)
        with self.assertRaises(module.ReceiptError):module._format_check(data,module.XLSX_MIME)
    def test_xlsx_expansion_budget_rejected(self):
        from unittest.mock import patch
        with patch.object(module,'MAX_EXPANDED_BYTES',1),self.assertRaises(module.ReceiptError):module._format_check(valid_xlsx(),module.XLSX_MIME)
    def test_xlsx_traversal_member_rejected(self):
        data=io.BytesIO(valid_xlsx())
        with zipfile.ZipFile(data,'a') as z:z.writestr('../escape.xml','<a/>')
        with self.assertRaises(module.ReceiptError):module._format_check(data.getvalue(),module.XLSX_MIME)
    def test_missing_pdf_parser_fails_closed(self):
        import builtins
        from unittest.mock import patch
        from test_collect_official_source_raw import valid_pdf
        data=valid_pdf();old_import=builtins.__import__
        def imp(name,*args,**kwargs):
            if name=='pypdf':raise ImportError('offline missing parser fixture')
            return old_import(name,*args,**kwargs)
        with patch.object(builtins,'__import__',side_effect=imp), self.assertRaises(module.ReceiptError):module._format_check(data,'application/pdf')
    def test_real_legacy_biff_fixture_parsed(self):
        data=bytes.fromhex('090004000200100003000f000000000000000000000000000045400a000000')
        self.assertEqual(module._format_check(data,'application/vnd.ms-excel'),'XLS_WORKBOOK_PARSED')


if __name__ == "__main__":
    unittest.main()
