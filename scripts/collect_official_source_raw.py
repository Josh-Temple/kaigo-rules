#!/usr/bin/env python3
"""Opt-in, bounded HTTPS raw download from named Japanese official hosts.

NO requests are made without --execute. No source freshness or legal validity
is inferred. A separate reviewer must verify the URL was discovered from the
current official index, TLS/host provenance and item/version applicability.
Never dispatch on a scheduled workflow or use this to update canonical data.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import ssl
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin
from urllib.request import (
    HTTPSHandler, HTTPRedirectHandler, ProxyHandler, Request, build_opener,
)

from check_source_transport_receipt import ReceiptError, _official_host, check_receipt

MAX_BYTES = 32 * 1024 * 1024
MAX_REDIRECTS = 5
MAX_SECONDS = 30
SAFE_NAME = re.compile(r"^[a-z0-9][a-z0-9_-]{0,63}$")
REDIRECTS = {301, 302, 303, 307, 308}


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def _validate_url(url: str, first_host: str) -> None:
    if _official_host(url) != first_host:
        raise ReceiptError("redirect must stay on the exact official host")


def download(url: str, name: str, directory: Path, *, opener=None, max_bytes=MAX_BYTES) -> dict:
    """Download once, inspect byte integrity, and write only local raw/receipt.

    Caller must authorize outbound traffic and first independently select
    a current official-source URL. opener injection is for offline tests.
    """
    origin = _official_host(url)
    if not SAFE_NAME.fullmatch(name):
        raise ReceiptError("name must be a safe lowercase identifier")
    if not isinstance(max_bytes, int) or max_bytes <= 0 or max_bytes > MAX_BYTES:
        raise ReceiptError("invalid maximum bytes")
    if not directory.is_dir():
        raise ReceiptError("output directory must already exist")
    if (directory / f"{name}.raw").exists() or (directory / f"{name}.receipt.json").exists():
        raise ReceiptError("outputs already exist; overwrite is prohibited")
    if opener is None:
        opener = build_opener(
            ProxyHandler({}),  # do not silently trust environment proxy
            HTTPSHandler(context=ssl.create_default_context()),
            NoRedirect(),
        )

    current_url = url
    redirects = []
    response = None
    for _ in range(MAX_REDIRECTS + 1):
        _validate_url(current_url, origin)
        request = Request(
            current_url,
            headers={
                "User-Agent": "KaigoRulesSourceReceipt/1.0 (manual evidence collection)",
                "Accept": "*/*",
                "Accept-Encoding": "identity",
            },
            method="GET",
        )
        try:
            response = opener.open(request, timeout=MAX_SECONDS)
        except HTTPError as exc:
            if exc.code not in REDIRECTS:
                raise ReceiptError(f"official server returned HTTP {exc.code}") from exc
            location = exc.headers.get("Location") if exc.headers else None
            if not location:
                raise ReceiptError("redirect lacks Location") from exc
            target = urljoin(current_url, location)
            _validate_url(target, origin)
            redirects.append({"from_url": current_url, "to_url": target, "status": exc.code})
            current_url = target
            exc.close()
            continue
        except (OSError, URLError) as exc:
            raise ReceiptError(f"HTTPS transport failed: {type(exc).__name__}") from exc
        break

    if response is None:
        raise ReceiptError("too many redirects")
    raw_temp = None
    receipt_temp = None
    raw_target = directory / f"{name}.raw"
    receipt_target = directory / f"{name}.receipt.json"
    try:
        with response:
            status = response.getcode()
            if type(status) is not int or status != 200:
                raise ReceiptError("final HTTP status must be 200")
            headers = response.info()
            content_type = headers.get("Content-Type")
            if not isinstance(content_type, str) or not content_type.strip():
                raise ReceiptError("Content-Type missing")
            content_encoding = headers.get("Content-Encoding")
            if content_encoding and content_encoding.lower() != "identity":
                raise ReceiptError("compressed response is not supported")
            header_fields = {
                "Content-Type": content_type,
            }
            for key in ("Content-Length", "ETag", "Last-Modified", "Content-Encoding"):
                value = headers.get(key)
                if value is not None:
                    header_fields[key] = value
            count = 0
            sha256 = hashlib.sha256()
            with tempfile.NamedTemporaryFile(mode="wb", prefix=".official-raw-", dir=directory, delete=False) as tmp:
                raw_temp = Path(tmp.name)
                while True:
                    chunk = response.read(min(1024 * 1024, max_bytes - count + 1))
                    if not chunk:
                        break
                    count += len(chunk)
                    if count > max_bytes:
                        raise ReceiptError("download exceeded bounded limit")
                    sha256.update(chunk)
                    tmp.write(chunk)
            length = headers.get("Content-Length")
            if length is not None:
                try:
                    length_int = int(length)
                except ValueError as exc:
                    raise ReceiptError("invalid Content-Length") from exc
                if length_int != count:
                    raise ReceiptError("Content-Length differs from raw byte count")
            receipt = {
                "schema_version": 1,
                "observed_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
                "request_url": url,
                "final_url": current_url,
                "http_status": status,
                "redirects": redirects,
                "response_headers": header_fields,
                "byte_count": count,
                "sha256": sha256.hexdigest(),
                "collector": "manual-https-urllib-v1",
                "origin_authenticity": "REQUIRES_INDEPENDENT_HOST_AND_TLS_REVIEW",
                "legal_currentness": "NOT_ASSESSED",
                "publication_decision": "NOT_AUTHORIZED",
            }
            check_receipt(receipt, raw_temp)
            with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", prefix=".official-receipt-", dir=directory, delete=False) as tmp:
                receipt_temp = Path(tmp.name)
                json.dump(receipt, tmp, ensure_ascii=False, indent=2)
                tmp.write("\n")
        # Hard links fail instead of overwriting an existing target.
        os.link(raw_temp, raw_target)
        try:
            os.link(receipt_temp, receipt_target)
        except Exception:
            raw_target.unlink(missing_ok=True)
            raise
        return receipt
    finally:
        if raw_temp:
            raw_temp.unlink(missing_ok=True)
        if receipt_temp:
            receipt_temp.unlink(missing_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", required=True, help="independently checked current official URL")
    parser.add_argument("--name", required=True, help="lowercase local artifact ID")
    parser.add_argument("--output-dir", required=True, type=Path, help="existing non-repository evidence folder")
    parser.add_argument("--execute", action="store_true", help="explicitly permit one external HTTP GET sequence")
    args = parser.parse_args()
    try:
        host = _official_host(args.url)
        if not SAFE_NAME.fullmatch(args.name):
            raise ReceiptError("unsafe name")
        if not args.execute:
            print(json.dumps({
                "state": "DRY_RUN_NO_NETWORK",
                "host": host,
                "url": args.url,
                "name": args.name,
                "publication_decision": "NOT_AUTHORIZED",
            }, ensure_ascii=False))
            return 0
        receipt = download(args.url, args.name, args.output_dir)
        print(json.dumps({
            "state": "RAW_RECEIPT_INTEGRITY_ONLY",
            "sha256": receipt["sha256"],
            "byte_count": receipt["byte_count"],
            "path": str(args.output_dir / (args.name + ".raw")),
            "receipt": str(args.output_dir / (args.name + ".receipt.json")),
            "legal_currentness": "NOT_ASSESSED",
        }, ensure_ascii=False))
        return 0
    except (ReceiptError, OSError, ValueError) as exc:
        print(json.dumps({"state": "BLOCKED_NO_ADOPTION", "reason": str(exc)}, ensure_ascii=False))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
