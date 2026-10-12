#!/usr/bin/env python3
"""Check offline integrity of an official-source download receipt and local bytes.

This verifies self-consistency, NOT origin authenticity, TLS, legal currentness,
source-item applicability, review acceptance or publication readiness. The
collector, its HTTPS connection, and headers need separate independent audit.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit

ALLOWED_HOSTS = {"www.mhlw.go.jp", "mhlw.go.jp", "laws.e-gov.go.jp"}
SHA256_RE = re.compile(r"^[a-f0-9]{64}$")


class ReceiptError(ValueError):
    """A receipt is incomplete or inconsistent with its local raw bytes."""


def _official_host(url: object) -> str:
    if not isinstance(url, str):
        raise ReceiptError("URL must be a string")
    try:
        parsed = urlsplit(url)
        hostname = parsed.hostname
        port = parsed.port
    except ValueError as exc:
        raise ReceiptError("invalid URL") from exc
    if (parsed.scheme != "https" or hostname not in ALLOWED_HOSTS
            or port not in (None, 443) or parsed.username or parsed.password
            or parsed.fragment or not parsed.path.startswith("/")):
        raise ReceiptError("URL is not a supported HTTPS official origin")
    return hostname


def _observed_utc(value: object) -> None:
    if not isinstance(value, str):
        raise ReceiptError("observed_at_utc is required")
    try:
        date = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ReceiptError("invalid observed_at_utc") from exc
    if date.utcoffset() != timezone.utc.utcoffset(date) or date.tzinfo is None:
        raise ReceiptError("observed_at_utc must specify UTC")


def check_receipt(receipt: dict, raw_file: Path) -> dict:
    """Return an integrity-only result; never issue an official-source verdict."""
    if not isinstance(receipt, dict) or receipt.get("schema_version") != 1:
        raise ReceiptError("unsupported receipt schema")
    _observed_utc(receipt.get("observed_at_utc"))
    requested = receipt.get("request_url")
    final = receipt.get("final_url")
    origin = _official_host(requested)
    if _official_host(final) != origin:
        raise ReceiptError("cross-origin response is outside this check")
    if receipt.get("http_status") != 200 or type(receipt.get("http_status")) is not int:
        raise ReceiptError("final HTTP status is not 200")

    redirects = receipt.get("redirects")
    if not isinstance(redirects, list):
        raise ReceiptError("redirect list is required, even when empty")
    previous = requested
    if len(redirects) > 10:
        raise ReceiptError("redirect chain too long")
    for redirect in redirects:
        if not isinstance(redirect, dict) or redirect.get("from_url") != previous:
            raise ReceiptError("redirect chain is discontinuous")
        status = redirect.get("status")
        if type(status) is not int or status not in (301, 302, 303, 307, 308):
            raise ReceiptError("invalid redirect status")
        target = redirect.get("to_url")
        if _official_host(target) != origin:
            raise ReceiptError("cross-origin redirect is outside this check")
        previous = target
    if previous != final:
        raise ReceiptError("redirect chain does not reach final_url")

    headers = receipt.get("response_headers")
    if not isinstance(headers, dict):
        raise ReceiptError("response_headers is required")
    types = [value for key, value in headers.items()
             if isinstance(key, str) and key.lower() == "content-type"]
    if len(types) != 1 or not isinstance(types[0], str) or not types[0].strip():
        raise ReceiptError("one content-type header is required")
    digest = receipt.get("sha256")
    byte_count = receipt.get("byte_count")
    if not isinstance(digest, str) or not SHA256_RE.fullmatch(digest):
        raise ReceiptError("sha256 must be a lowercase hex digest")
    if type(byte_count) is not int or byte_count <= 0:
        raise ReceiptError("positive byte_count is required")
    if not raw_file.is_file():
        raise ReceiptError("raw file does not exist")
    sha = hashlib.sha256()
    actual_count = 0
    first_chunk = b""
    with raw_file.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            if not first_chunk:
                first_chunk = chunk
            actual_count += len(chunk)
            sha.update(chunk)
    if actual_count != byte_count or sha.hexdigest() != digest:
        raise ReceiptError("raw bytes do not match byte_count and sha256")
    media_type = types[0].split(";", 1)[0].strip().lower()
    if final.lower().split("?", 1)[0].endswith(".xlsx"):
        if media_type not in (
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "application/octet-stream",
        ) or not first_chunk.startswith(b"PK\x03\x04"):
            raise ReceiptError("XLSX MIME/magic mismatch")
    if final.lower().split("?", 1)[0].endswith(".xls"):
        if media_type not in ("application/vnd.ms-excel", "application/octet-stream") or not first_chunk.startswith(b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1"):
            raise ReceiptError("XLS MIME/magic mismatch")
    if final.lower().split("?", 1)[0].endswith(".pdf"):
        if media_type not in ("application/pdf", "application/octet-stream") or not first_chunk.startswith(b"%PDF-"):
            raise ReceiptError("PDF MIME/magic mismatch")
    return {
        "raw_receipt_integrity": "CONSISTENT",
        "sha256": digest,
        "byte_count": actual_count,
        "origin_authenticity": "NOT_VERIFIED_BY_OFFLINE_CHECK",
        "legal_currentness": "NOT_ASSESSED",
        "successor_and_applicability": "NOT_ASSESSED",
        "publication_decision": "NOT_AUTHORIZED",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--receipt", required=True, type=Path)
    parser.add_argument("--raw", required=True, type=Path)
    args = parser.parse_args()
    try:
        receipt = json.loads(args.receipt.read_text(encoding="utf-8"))
        result = check_receipt(receipt, args.raw)
    except (ReceiptError, ValueError, OSError) as exc:
        print(json.dumps({"raw_receipt_integrity": "REJECTED", "reason": str(exc)}, ensure_ascii=False))
        return 1
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
