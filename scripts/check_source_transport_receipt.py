#!/usr/bin/env python3
"""Check bounded offline receipt/file integrity, not origin or legal validity.

PDF/XLS parsing requires source-collector-requirements.txt. Parsers do not execute
macros, render active content, authenticate sources or establish currentness.
Missing parsers fail closed. This is not a malware or complete format audit.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import re
import stat
import zipfile
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from urllib.parse import urlsplit
from xml.etree import ElementTree as ET

ALLOWED_HOSTS = {"www.mhlw.go.jp", "mhlw.go.jp", "laws.e-gov.go.jp"}
SHA256_RE = re.compile(r"^[a-f0-9]{64}$")
MAX_BYTES = 32 * 1024 * 1024
MAX_EXPANDED_BYTES = 128 * 1024 * 1024
XLSX_MIME = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
SUPPORTED_MEDIA_TYPES = {"application/json", "application/xml", "text/xml", "text/html",
                         "application/pdf", "application/vnd.ms-excel", XLSX_MIME}


class ReceiptError(ValueError):
    """A receipt or its local file fails a bounded integrity check."""


def _official_host(url: object) -> str:
    if (not isinstance(url, str) or not url or any(ord(c) <= 32 or ord(c) >= 127 for c in url)
            or "\\" in url or "#" in url):
        raise ReceiptError("URL must be an ASCII HTTPS URL without controls or fragment")
    try:
        p = urlsplit(url)
        host = p.hostname
        port = p.port
    except ValueError as exc:
        raise ReceiptError("invalid URL") from exc
    if (p.scheme != "https" or host not in ALLOWED_HOSTS or port not in (None, 443)
            or p.username is not None or p.password is not None
            or p.netloc.lower() not in (host, host + ":443") or not p.path.startswith("/")):
        raise ReceiptError("URL is not a supported HTTPS official origin")
    return host


def _observed_utc(value: object) -> None:
    if not isinstance(value, str):
        raise ReceiptError("observed_at_utc is required")
    try:
        date = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ReceiptError("invalid observed_at_utc") from exc
    if date.tzinfo is None or date.utcoffset() != timezone.utc.utcoffset(date):
        raise ReceiptError("observed_at_utc must specify UTC")


def _xml(data: bytes):
    screen = data.replace(b"\x00", b"").upper()
    if b"<!DOCTYPE" in screen or b"<!ENTITY" in screen:
        raise ReceiptError("DTD/entity declarations are not supported")
    return ET.fromstring(data)


def _format_check(data: bytes, media_type: str) -> str:
    """Bounded structural parse only; not semantic correctness or safe rendering."""
    try:
        if media_type == XLSX_MIME:
            with zipfile.ZipFile(io.BytesIO(data)) as z:
                entries = z.infolist()
                names = [e.filename for e in entries]
                if len(entries) > 4096 or len(set(names)) != len(names):
                    raise ReceiptError("XLSX has too many or duplicate entries")
                if sum(e.file_size for e in entries) > MAX_EXPANDED_BYTES:
                    raise ReceiptError("XLSX expanded size exceeds limit")
                for e in entries:
                    p = PurePosixPath(e.filename)
                    if (p.is_absolute() or ".." in p.parts or "\\" in e.filename
                            or e.flag_bits & 1 or stat.S_ISLNK(e.external_attr >> 16)):
                        raise ReceiptError("unsafe/encrypted XLSX member")
                    with z.open(e) as stream:
                        while stream.read(1024 * 1024):
                            pass  # consume all members so CRC and truncation are checked
                required = {"[Content_Types].xml", "_rels/.rels", "xl/workbook.xml",
                            "xl/_rels/workbook.xml.rels"}
                if not required.issubset(names):
                    raise ReceiptError("XLSX workbook container is incomplete")
                ns = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
                workbook = _xml(z.read("xl/workbook.xml"))
                if workbook.tag != ns + "workbook" or not workbook.findall(ns + "sheets/" + ns + "sheet"):
                    raise ReceiptError("XLSX workbook/sheet structure missing")
                worksheets = [n for n in names if n.startswith("xl/worksheets/") and n.endswith(".xml")]
                if not worksheets:
                    raise ReceiptError("XLSX worksheet missing")
                for name in names:
                    if name.endswith((".xml", ".rels")):
                        root = _xml(z.read(name))
                        if name in worksheets and root.tag != ns + "worksheet":
                            raise ReceiptError("XLSX worksheet root mismatch")
            return "XLSX_CONTAINER_AND_XML_PARSED"
        if media_type == "application/pdf":
            if not data.startswith(b"%PDF-") or not data.rstrip().endswith(b"%%EOF"):
                raise ReceiptError("PDF header/end marker missing")
            try:
                from pypdf import PdfReader
            except ImportError as exc:
                raise ReceiptError("PDF parser unavailable; install collector requirements") from exc
            reader = PdfReader(io.BytesIO(data), strict=True)
            if reader.is_encrypted or not 0 < len(reader.pages) <= 10000:
                raise ReceiptError("encrypted/empty/oversized PDF page tree")
            for page in reader.pages:
                _ = page.mediabox  # force page object resolution without rendering/decompressing content
            return "PDF_XREF_AND_PAGE_TREE_PARSED"
        if media_type == "application/vnd.ms-excel":
            try:
                import xlrd
            except ImportError as exc:
                raise ReceiptError("XLS parser unavailable; install collector requirements") from exc
            book = xlrd.open_workbook(file_contents=data, logfile=io.StringIO(),
                                      on_demand=True, ignore_workbook_corruption=False)
            try:
                if not 0 < book.nsheets <= 4096:
                    raise ReceiptError("XLS workbook sheets missing/excessive")
                for index in range(book.nsheets):
                    book.sheet_by_index(index)
                    book.unload_sheet(index)
            finally:
                book.release_resources()
            return "XLS_WORKBOOK_PARSED"
        if media_type == "application/json":
            def reject_constant(value):
                raise ReceiptError("non-standard JSON numeric constant")
            json.loads(data.decode("utf-8-sig"), parse_constant=reject_constant)
            return "JSON_PARSED"
        if media_type in ("application/xml", "text/xml"):
            _xml(data)
            return "XML_PARSED_NO_DTD"
        if media_type == "text/html":
            # HTML is kept as a raw document; this screen is not document identity proof.
            if not re.search(br"<\s*(?:!doctype\s+html|html|body)(?:\s|>)", data[:8192], re.I):
                raise ReceiptError("HTML document marker missing")
            return "HTML_MARKER_SCREEN_ONLY"
    except ReceiptError:
        raise
    except Exception as exc:
        raise ReceiptError("file format parse failed: " + type(exc).__name__) from exc
    raise ReceiptError("unsupported media type")


def check_receipt(receipt: dict, raw_file: Path, *, _directory_fd=None) -> dict:
    """Verify self-consistency. The private fd option pins collector temp reads."""
    if (not isinstance(receipt, dict) or type(receipt.get("schema_version")) is not int
            or receipt.get("schema_version") != 1):
        raise ReceiptError("unsupported receipt schema")
    _observed_utc(receipt.get("observed_at_utc"))
    requested, final = receipt.get("request_url"), receipt.get("final_url")
    origin = _official_host(requested)
    if _official_host(final) != origin:
        raise ReceiptError("cross-origin final response")
    if type(receipt.get("http_status")) is not int or receipt["http_status"] != 200:
        raise ReceiptError("final HTTP status is not 200")
    redirects = receipt.get("redirects")
    if not isinstance(redirects, list) or len(redirects) > 5:
        raise ReceiptError("redirect list missing/too long")
    previous = requested
    for r in redirects:
        if (not isinstance(r, dict) or r.get("from_url") != previous
                or type(r.get("status")) is not int or r["status"] not in (301, 302, 303, 307, 308)
                or _official_host(r.get("to_url")) != origin):
            raise ReceiptError("invalid/discontinuous redirect")
        previous = r["to_url"]
    if previous != final:
        raise ReceiptError("redirect chain does not reach final URL")
    headers = receipt.get("response_headers")
    if not isinstance(headers, dict) or any(not isinstance(k, str) or not isinstance(v, str) for k, v in headers.items()):
        raise ReceiptError("response headers must be string pairs")
    h = {}
    for key, value in headers.items():
        key = key.lower()
        if key in h or "\r" in value or "\n" in value:
            raise ReceiptError("duplicate/invalid response header")
        h[key] = value
    media_type = h.get("content-type", "").split(";", 1)[0].strip().lower()
    suffix = Path(urlsplit(final).path).suffix.lower()
    expected = {".xlsx": XLSX_MIME, ".xls": "application/vnd.ms-excel", ".pdf": "application/pdf"}.get(suffix)
    if media_type == "application/octet-stream" and expected:
        media_type = expected
    if media_type not in SUPPORTED_MEDIA_TYPES or (expected and media_type != expected):
        raise ReceiptError("unsupported or URL/MIME mismatched format")
    if h.get("content-encoding", "identity").strip().lower() != "identity":
        raise ReceiptError("encoded response is unsupported")
    if "transfer-encoding" in h and (h["transfer-encoding"].strip().lower() != "chunked" or "content-length" in h):
        raise ReceiptError("unsupported/ambiguous response framing")
    digest, count = receipt.get("sha256"), receipt.get("byte_count")
    if (not isinstance(digest, str) or not SHA256_RE.fullmatch(digest)
            or type(count) is not int or not 0 < count <= MAX_BYTES):
        raise ReceiptError("invalid digest or bounded byte count")
    if "content-length" in h and (not re.fullmatch(r"[0-9]+", h["content-length"]) or int(h["content-length"]) != count):
        raise ReceiptError("Content-Length differs from raw byte count")
    if _directory_fd is not None and (raw_file.name != str(raw_file) or not raw_file.name):
        raise ReceiptError("pinned raw filename must be a basename")
    try:
        fd = os.open(raw_file, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=_directory_fd)
        with os.fdopen(fd, "rb") as stream:
            before = os.fstat(stream.fileno())
            if not stat.S_ISREG(before.st_mode) or before.st_size > MAX_BYTES:
                raise ReceiptError("raw must be a bounded regular file, not a symlink/device")
            data = stream.read(MAX_BYTES + 1)
            after = os.fstat(stream.fileno())
        if (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns) != (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns):
            raise ReceiptError("raw changed while being checked")
    except OSError as exc:
        raise ReceiptError("cannot safely open raw file") from exc
    if len(data) != count or hashlib.sha256(data).hexdigest() != digest:
        raise ReceiptError("raw bytes do not match byte count and SHA-256")
    checked = _format_check(data, media_type)
    return {"raw_receipt_integrity": "CONSISTENT", "sha256": digest, "byte_count": len(data),
            "format_check": checked, "origin_authenticity": "NOT_VERIFIED_BY_OFFLINE_CHECK",
            "legal_currentness": "NOT_ASSESSED", "successor_and_applicability": "NOT_ASSESSED",
            "publication_decision": "NOT_AUTHORIZED"}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--receipt", required=True, type=Path)
    parser.add_argument("--raw", required=True, type=Path)
    args = parser.parse_args()
    try:
        result = check_receipt(json.loads(args.receipt.read_text(encoding="utf-8")), args.raw)
    except (ReceiptError, ValueError, OSError) as exc:
        print(json.dumps({"raw_receipt_integrity": "REJECTED", "reason": str(exc)}, ensure_ascii=False))
        return 1
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
