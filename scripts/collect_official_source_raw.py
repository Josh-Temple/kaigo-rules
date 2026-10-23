#!/usr/bin/env python3
"""Explicit opt-in manual HTTPS collection; default CLI and API do no network.

Use an independently selected current URL and an owned, non-writable-by-others
POSIX evidence directory outside the repository. This records integrity only,
not independent TLS attestation, source identity, legal validity or publication.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import secrets
import ssl
import stat
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin
from urllib.request import HTTPSHandler, HTTPRedirectHandler, ProxyHandler, Request, build_opener

from check_source_transport_receipt import (
    ReceiptError, _official_host, check_receipt, MAX_BYTES, SUPPORTED_MEDIA_TYPES,
)

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


def _open_directory(directory: Path):
    absolute = directory.absolute()
    if ".." in directory.parts or absolute != directory.resolve():
        raise ReceiptError("output directory must not contain traversal or symlinks")
    repository_root = Path(__file__).resolve().parents[1]
    if absolute.is_relative_to(repository_root):
        raise ReceiptError("raw evidence must be stored outside the repository")
    # Walk every component with O_NOFOLLOW. A parent symlink swapped after the
    # resolve check must not redirect writes into a different directory.
    flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
    fd = os.open(absolute.anchor, flags)
    try:
        for part in absolute.parts[1:]:
            child = os.open(part, flags, dir_fd=fd)
            os.close(fd)
            fd = child
    except Exception:
        os.close(fd)
        raise
    s = os.fstat(fd)
    if s.st_uid != os.geteuid() or s.st_mode & 0o022:
        os.close(fd)
        raise ReceiptError("output directory must be owned and not group/world writable")
    return fd, absolute, s


def _same_directory(directory: Path, original) -> bool:
    try:
        s = directory.stat(follow_symlinks=False)
        return stat.S_ISDIR(s.st_mode) and (s.st_dev, s.st_ino) == (original.st_dev, original.st_ino)
    except OSError:
        return False


def _unlink_if_owned(fd: int, name: str, identity) -> None:
    """Never remove a name that has been replaced by a concurrent writer."""
    if identity is None:
        return
    try:
        current = os.stat(name, dir_fd=fd, follow_symlinks=False)
        if (current.st_dev, current.st_ino, current.st_ctime_ns) == (identity.st_dev, identity.st_ino, identity.st_ctime_ns):
            os.unlink(name, dir_fd=fd)
    except FileNotFoundError:
        pass


def _verify_published_pair(fd: int, directory: Path, original_dir,
                           raw_name: str, receipt_name: str,
                           raw_identity, receipt_identity, expected: dict) -> None:
    """Best-effort final check of committed names, bytes, and directory identity.

    Caller must not claim protection from an arbitrary same-UID writer after
    this check; access control on the output directory remains mandatory.
    """
    if not _same_directory(directory, original_dir):
        raise ReceiptError("output directory changed during final publication")
    sha = hashlib.sha256()
    try:
        raw_fd = os.open(raw_name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=fd)
        with os.fdopen(raw_fd, "rb") as raw:
            identity = os.fstat(raw.fileno())
            if (not stat.S_ISREG(identity.st_mode) or
                    (identity.st_dev, identity.st_ino, identity.st_ctime_ns) != (raw_identity.st_dev, raw_identity.st_ino, raw_identity.st_ctime_ns) or
                    identity.st_size != expected["byte_count"]):
                raise ReceiptError("published raw identity/size changed")
            while True:
                data = raw.read(1024 * 1024)
                if not data:
                    break
                sha.update(data)
        if sha.hexdigest() != expected["sha256"]:
            raise ReceiptError("published raw checksum changed")
        receipt_fd = os.open(receipt_name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=fd)
        with os.fdopen(receipt_fd, "rb") as source:
            identity = os.fstat(source.fileno())
            if (not stat.S_ISREG(identity.st_mode) or
                    (identity.st_dev, identity.st_ino, identity.st_ctime_ns) != (receipt_identity.st_dev, receipt_identity.st_ino, receipt_identity.st_ctime_ns) or
                    identity.st_size > 65536):
                raise ReceiptError("published receipt identity/size changed")
            try:
                observed = json.loads(source.read().decode("utf-8"))
            except (UnicodeError, ValueError) as exc:
                raise ReceiptError("published receipt JSON invalid") from exc
        if observed != expected:
            raise ReceiptError("published receipt differs from original")
    except (FileNotFoundError, IsADirectoryError, NotADirectoryError, PermissionError) as exc:
        raise ReceiptError("published files cannot be read securely") from exc
    if not _same_directory(directory, original_dir):
        raise ReceiptError("output directory changed during final verification")


def _new_temp(fd: int, prefix: str):
    name = prefix + secrets.token_hex(16)
    handle = os.open(name, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
                     0o600, dir_fd=fd)
    return name, handle


def _headers(message):
    captured = {}
    for key in ("Content-Type", "Content-Length", "ETag", "Last-Modified", "Content-Encoding", "Transfer-Encoding"):
        values = message.get_all(key, [])
        if len(values) > 1:
            raise ReceiptError("duplicate response header: " + key)
        if values:
            value = values[0]
            if not isinstance(value, str) or "\r" in value or "\n" in value:
                raise ReceiptError("invalid response header")
            captured[key] = value
    mime = captured.get("Content-Type", "").split(";", 1)[0].strip().lower()
    if mime not in SUPPORTED_MEDIA_TYPES:
        raise ReceiptError("missing or unsupported Content-Type")
    if captured.get("Content-Encoding", "identity").strip().lower() != "identity":
        raise ReceiptError("compressed response is not supported")
    if "Transfer-Encoding" in captured and (captured["Transfer-Encoding"].strip().lower() != "chunked" or "Content-Length" in captured):
        raise ReceiptError("ambiguous/unsupported response framing")
    length = captured.get("Content-Length")
    if length is not None and (not re.fullmatch(r"[0-9]+", length) or int(length) > MAX_BYTES):
        raise ReceiptError("invalid or excessive Content-Length")
    return captured, mime


def download(url: str, name: str, directory: Path, *, opener=None, max_bytes=MAX_BYTES,
             expected_media_type=None, allow_network=False) -> dict:
    """An injected opener is offline-test-only. Real network also needs opt-in.

    Per-call socket inactivity timeout and elapsed-time checks are used. This is
    not an OS network sandbox or a hard wall-clock bound on DNS/parser calls.
    """
    origin = _official_host(url)
    if not isinstance(name, str) or not SAFE_NAME.fullmatch(name):
        raise ReceiptError("unsafe lowercase artifact identifier")
    if type(max_bytes) is not int or not 0 < max_bytes <= MAX_BYTES:
        raise ReceiptError("invalid maximum bytes")
    if expected_media_type is not None and expected_media_type not in SUPPORTED_MEDIA_TYPES:
        raise ReceiptError("unsupported expected media type")
    if opener is None and allow_network is not True:
        raise ReceiptError("real outbound network needs explicit allow_network=True")
    fd, directory, original_dir = _open_directory(directory)
    raw_name, receipt_name = name + ".raw", name + ".receipt.json"
    lock_name = "." + name + ".collect.lock"
    lock_created = False
    raw_temp = receipt_temp = None
    raw_installed = receipt_installed = lock_identity = None
    try:
        # Cooperating concurrent collectors cannot publish the same pair.
        lock_fd = os.open(lock_name, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
                          0o600, dir_fd=fd)
        lock_identity = os.fstat(lock_fd)
        os.close(lock_fd)
        lock_created = True
        for target in (raw_name, receipt_name):
            try:
                os.stat(target, dir_fd=fd, follow_symlinks=False)
            except FileNotFoundError:
                pass
            else:
                raise ReceiptError("outputs exist; overwriting is prohibited")
        if opener is None:
            opener = build_opener(ProxyHandler({}), HTTPSHandler(context=ssl.create_default_context()), NoRedirect())
        current = url
        redirects = []
        response = None
        deadline = time.monotonic() + MAX_SECONDS
        for hop in range(MAX_REDIRECTS + 1):
            _validate_url(current, origin)
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise ReceiptError("elapsed transport limit exceeded")
            request = Request(current, headers={"User-Agent": "KaigoRulesSourceReceipt/1.0 (manual evidence collection)",
                              "Accept": "*/*", "Accept-Encoding": "identity"}, method="GET")
            try:
                response = opener.open(request, timeout=min(MAX_SECONDS, remaining))
            except HTTPError as exc:
                try:
                    if exc.code not in REDIRECTS:
                        raise ReceiptError("official server returned HTTP " + str(exc.code)) from exc
                    if hop == MAX_REDIRECTS:
                        raise ReceiptError("too many redirects")
                    locations = exc.headers.get_all("Location", []) if exc.headers else []
                    if len(locations) != 1 or not locations[0]:
                        raise ReceiptError("redirect needs exactly one Location")
                    # Inspect raw Location too: urljoin silently removes some controls.
                    if any(ord(c) <= 32 or ord(c) >= 127 for c in locations[0]) or "\\" in locations[0]:
                        raise ReceiptError("invalid redirect Location")
                    target = urljoin(current, locations[0])
                    _validate_url(target, origin)
                    redirects.append({"from_url": current, "to_url": target, "status": exc.code})
                    current = target
                finally:
                    exc.close()
                continue
            except (OSError, URLError) as exc:
                raise ReceiptError("HTTPS transport failed: " + type(exc).__name__) from exc
            break
        if response is None:
            raise ReceiptError("no final response")
        with response:
            if type(response.getcode()) is not int or response.getcode() != 200:
                raise ReceiptError("final HTTP status must be 200")
            observed_url = response.geturl() if hasattr(response, "geturl") else current
            if observed_url != current:
                raise ReceiptError("opener changed final URL without recorded redirect")
            captured, mime = _headers(response.info())
            if expected_media_type is not None and mime != expected_media_type:
                raise ReceiptError("Content-Type differs from explicitly expected source type")
            length = captured.get("Content-Length")
            if length is not None and int(length) > max_bytes:
                raise ReceiptError("Content-Length exceeds caller limit")
            raw_temp, handle = _new_temp(fd, ".official-raw-")
            count = 0
            sha = hashlib.sha256()
            with os.fdopen(handle, "wb") as stream:
                read = getattr(response, "read1", response.read)
                while True:
                    if time.monotonic() > deadline:
                        raise ReceiptError("elapsed transport limit exceeded")
                    chunk = read(min(1024 * 1024, max_bytes - count + 1))
                    if time.monotonic() > deadline:
                        raise ReceiptError("elapsed transport limit exceeded")
                    if not chunk:
                        break
                    count += len(chunk)
                    if count > max_bytes:
                        raise ReceiptError("download exceeded byte limit")
                    sha.update(chunk)
                    stream.write(chunk)
            if length is not None and int(length) != count:
                raise ReceiptError("Content-Length differs from raw byte count")
            receipt = {"schema_version": 1, "observed_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
                       "request_url": url, "final_url": current, "http_status": 200, "redirects": redirects,
                       "response_headers": captured, "byte_count": count, "sha256": sha.hexdigest(),
                       "collector": "manual-https-urllib-v2", "origin_authenticity": "REQUIRES_INDEPENDENT_HOST_AND_TLS_REVIEW",
                       "legal_currentness": "NOT_ASSESSED", "publication_decision": "NOT_AUTHORIZED"}
            checked = check_receipt(receipt, Path(raw_temp), _directory_fd=fd)
            receipt["format_check"] = checked["format_check"]
            receipt_temp, handle = _new_temp(fd, ".official-receipt-")
            with os.fdopen(handle, "w", encoding="utf-8") as stream:
                json.dump(receipt, stream, ensure_ascii=False, indent=2)
                stream.write("\n")
        if not _same_directory(directory, original_dir):
            raise ReceiptError("output directory changed during collection")
        try:
            os.link(raw_temp, raw_name, src_dir_fd=fd, dst_dir_fd=fd, follow_symlinks=False)
            # The unique temporary inode is still owned by this call even if
            # another actor swaps the public filename immediately afterward.
            raw_installed = os.stat(raw_temp, dir_fd=fd, follow_symlinks=False)
            os.link(receipt_temp, receipt_name, src_dir_fd=fd, dst_dir_fd=fd, follow_symlinks=False)
            receipt_installed = os.stat(receipt_temp, dir_fd=fd, follow_symlinks=False)
            _verify_published_pair(fd, directory, original_dir, raw_name,
                                   receipt_name, raw_installed, receipt_installed, receipt)
        except Exception:
            _unlink_if_owned(fd, receipt_name, receipt_installed)
            _unlink_if_owned(fd, raw_name, raw_installed)
            raise
        return receipt
    finally:
        for temporary in (raw_temp, receipt_temp):
            if temporary:
                try:
                    os.unlink(temporary, dir_fd=fd)
                except FileNotFoundError:
                    pass
        if lock_created:
            _unlink_if_owned(fd, lock_name, lock_identity)
        os.close(fd)


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--url", required=True)
    p.add_argument("--name", required=True)
    p.add_argument("--output-dir", required=True, type=Path)
    p.add_argument("--expect-media-type", required=True, choices=sorted(SUPPORTED_MEDIA_TYPES))
    p.add_argument("--execute", action="store_true", help="explicitly authorize real outbound GET")
    args = p.parse_args()
    try:
        host = _official_host(args.url)
        if not SAFE_NAME.fullmatch(args.name):
            raise ReceiptError("unsafe name")
        if not args.execute:
            print(json.dumps({"state": "DRY_RUN_NO_NETWORK", "host": host, "url": args.url,
                              "name": args.name, "publication_decision": "NOT_AUTHORIZED"}, ensure_ascii=False))
            return 0
        r = download(args.url, args.name, args.output_dir, expected_media_type=args.expect_media_type, allow_network=True)
        print(json.dumps({"state": "RAW_RECEIPT_INTEGRITY_ONLY", "sha256": r["sha256"], "byte_count": r["byte_count"],
                          "path": str(args.output_dir / (args.name + ".raw")),
                          "receipt": str(args.output_dir / (args.name + ".receipt.json")), "legal_currentness": "NOT_ASSESSED"}))
        return 0
    except (ReceiptError, OSError, ValueError) as exc:
        print(json.dumps({"state": "BLOCKED_NO_ADOPTION", "reason": str(exc)}, ensure_ascii=False))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
