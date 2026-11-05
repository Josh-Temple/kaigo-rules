#!/usr/bin/env python3
"""Read-only, fail-closed inventory of B's scoped PRIVATE review candidate.

The generator's PRIVATE_ACCEPTANCE_ONLY manifest is not publication authority.
This tool never writes content into a public checkout, log or artifact.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import re
from collections import Counter
from pathlib import Path
from urllib.parse import unquote

try:
    from scripts.audit_github_pages_scope_gate import (
        _References, _check_local_reference, HASH, SENSITIVE, INTERNAL,
    )
except ModuleNotFoundError:  # executable as python scripts/audit_...py
    from audit_github_pages_scope_gate import (
        _References, _check_local_reference, HASH, SENSITIVE, INTERNAL,
    )

SHA = re.compile(r"^[0-9a-f]{40}$")
QA_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,120}$")
WARNING = "試験用の審査候補です。制度の現行性・適用条件は国の原典と指定権者で確認してください。"
ROOT_FILES = {
    "index.html", "style.css", "search/index.html", "search/app.mjs",
    "search/rows.json", "search/rows.json.gz",
}


def _read_json(path: Path, errors: list[str]):
    try:
        if path.is_symlink() or not path.is_file():
            raise ValueError("missing or symlink")
        return json.loads(path.read_text(encoding="utf-8"))
    except (ValueError, UnicodeError, OSError):
        errors.append("INVALID_INPUT_JSON")
        return None


def _paths_from_scope(scope: object, errors: list[str]):
    if not isinstance(scope, dict) or scope.get("schema") != "kaigo-reviewed-scope-v1":
        errors.append("INVALID_SCOPE_SCHEMA")
        return {}, set()
    if scope.get("purpose") != "PRIVATE_ACCEPTANCE_ONLY":
        errors.append("UNSUPPORTED_SCOPE_PURPOSE")
    approvals = scope.get("approvals")
    if not isinstance(approvals, list) or not approvals:
        errors.append("EMPTY_SCOPE")
        return {}, set()
    expected = {}
    pairs = set()
    for item in approvals:
        if not isinstance(item, dict):
            errors.append("INVALID_APPROVAL_ROW")
            continue
        kind, record_id = item.get("kind"), item.get("id")
        if (kind not in ("qa", "legal") or not isinstance(record_id, str)
                or not record_id or len(record_id) > 2048
                or any(ord(c) < 32 or c in "/\\" for c in record_id)
                or (kind == "qa" and not QA_ID.fullmatch(record_id))):
            errors.append("INVALID_SCOPE_ID")
            continue
        pair = (kind, record_id)
        if pair in pairs or any(existing_id == record_id for _, existing_id in pairs):
            errors.append("DUPLICATE_SCOPE_ID")
            continue
        pairs.add(pair)
        if item.get("publish_approved") is not True or item.get("state") != "APPROVED_FOR_SCOPED_REVIEW":
            errors.append("UNAPPROVED_SCOPE_ID")
        for field in ("row_sha256", "source_url", "approved_by", "approval_reference",
                      "evidence_reference", "period_start", "period_end"):
            if not isinstance(item.get(field), str) or not item[field]:
                errors.append("MISSING_SCOPE_FIELD")
        if not isinstance(item.get("row_sha256"), str) or not HASH.fullmatch(item["row_sha256"]):
            errors.append("INVALID_SOURCE_ROW_HASH")
        if kind == "qa":
            path = "qa/" + record_id + "/index.html"
        else:
            path = ("legislation/record/" +
                    hashlib.sha256(record_id.encode("utf-8")).hexdigest() + ".html")
        expected[pair] = path
    return expected, pairs


def inspect(root: Path, *, source_sha: str, scope: object,
            receipt: object = None, mode: str = "private",
            trusted_receipt_sha256: str | None = None,
            receipt_byte_sha256: str | None = None):
    if not SHA.fullmatch(source_sha) or mode not in {"private", "beta", "public"}:
        raise ValueError("Invalid fixed SHA or mode")
    if not root.is_dir() or root.is_symlink():
        raise ValueError("Missing or symlinked site")
    root = root.resolve(strict=True)
    errors = []
    expected, approved_pairs = _paths_from_scope(scope, errors)
    if mode in {"beta", "public"} and (
            not isinstance(scope, dict) or scope.get("source_sha") != source_sha):
        errors.append("REVIEWED_SCOPE_SOURCE_SHA_NOT_VERIFIED")
    entries = list(root.rglob("*"))
    if any(p.is_symlink() for p in entries):
        errors.append("SYMLINK_IN_DISTRIBUTION")
    files = sorted(p for p in entries if p.is_file() and not p.is_symlink())
    names = {p.relative_to(root).as_posix() for p in files}
    allowed = ROOT_FILES | set(expected.values()) | ({".nojekyll"} if mode != "private" else set())
    if names != allowed:
        if names - allowed:
            errors.append("UNAPPROVED_DISTRIBUTION_PATH")
        if allowed - names:
            errors.append("MISSING_REQUIRED_DISTRIBUTION_PATH")
    if mode in {"beta", "public"}:
        # B currently produces private-only noindex preview bytes; no public
        # release can be authorized by changing JSON flags or a workflow variable.
        errors.append("PRIVATE_REVIEW_GENERATOR_NOT_PUBLICATION_READY")
        if (not isinstance(trusted_receipt_sha256, str)
                or not HASH.fullmatch(trusted_receipt_sha256)
                or receipt_byte_sha256 != trusted_receipt_sha256):
            errors.append("INDEPENDENT_RECEIPT_DIGEST_NOT_VERIFIED")
    counts = Counter()
    hashes = {}
    total_bytes = html_count = noindex_count = warning_count = 0
    legacy = Counter()
    for file in files:
        relative = file.relative_to(root).as_posix()
        raw = file.read_bytes()
        total_bytes += len(raw)
        hashes[relative] = hashlib.sha256(raw).hexdigest()
        counts[file.suffix.lower() or "(none)"] += 1
        if relative.endswith(".gz"):
            original = file.with_suffix("")
            try:
                if not original.is_file() or original.is_symlink():
                    raise ValueError("Missing gzip counterpart")
                with gzip.open(file, "rb") as stream:
                    decoded = stream.read(original.stat().st_size + 1)
                if decoded != original.read_bytes():
                    raise ValueError("Mismatch")
            except (ValueError, OSError, EOFError):
                errors.append("GZIP_MISMATCH")
            continue
        if SENSITIVE.search(raw):
            errors.append("POSSIBLE_SECRET")
        if any(marker in raw for marker in INTERNAL):
            errors.append("INTERNAL_OR_UNREVIEWED_MARKER")
        if b"kaigo-rules.vercel.app" in raw:
            legacy[file.suffix.lower()] += raw.count(b"kaigo-rules.vercel.app")
            errors.append("LEGACY_PRODUCTION_URL")
        if file.suffix.lower() in {".html", ".json", ".mjs", ".js", ".css", ".svg", ".xml"}:
            try:
                value = raw.decode("utf-8")
            except UnicodeDecodeError:
                errors.append("INVALID_UTF8")
                continue
            if file.suffix.lower() == ".html":
                html_count += 1
                if 'name="robots" content="noindex' in value:
                    noindex_count += 1
                else:
                    errors.append("MISSING_NOINDEX")
                if WARNING in value:
                    warning_count += 1
                else:
                    errors.append("MISSING_REVIEW_WARNING")
                refs = _References()
                refs.feed(value)
                for reference in refs.references:
                    _check_local_reference(root, file, reference, errors)
            elif file.suffix.lower() == ".css" and "url(" in value:
                errors.append("UNREVIEWED_CSS_URL")
    if not files or total_bytes >= 1_000_000_000:
        errors.append("EMPTY_OR_OVERSIZED_SITE")
    rows = _read_json(root / "search/rows.json", errors)
    observed_pairs = set()
    if not isinstance(rows, dict) or not isinstance(rows.get("rows"), list):
        errors.append("INVALID_SEARCH_ROWS")
    else:
        for row in rows["rows"]:
            if not isinstance(row, dict) or not isinstance(row.get("id"), str):
                errors.append("INVALID_SEARCH_ROW")
                continue
            pair = (row.get("kind"), row["id"])
            if pair in observed_pairs:
                errors.append("DUPLICATE_SEARCH_ROW")
            observed_pairs.add(pair)
            path = expected.get(pair)
            if (path is None or row.get("href") != "../" + path
                    or not isinstance(row.get("title"), str) or not row["title"]
                    or not isinstance(row.get("excerpt"), str)):
                errors.append("SEARCH_ROW_OUTSIDE_APPROVED_SCOPE")
    if observed_pairs != approved_pairs:
        errors.append("SEARCH_APPROVED_ID_MISMATCH")
    if html_count != len(expected) + 2:
        errors.append("DETAIL_HTML_COUNT_MISMATCH")
    tree_hash = hashlib.sha256(
        "".join(path + "\0" + hashes[path] + "\n" for path in sorted(hashes)).encode()
    ).hexdigest()
    if receipt is not None:
        if (not isinstance(receipt, dict)
                or receipt.get("source_sha") != source_sha
                or receipt.get("distribution_tree_sha256") != tree_hash
                or receipt.get("file_sha256") != hashes):
            errors.append("DISTRIBUTION_RECEIPT_MISMATCH")
    if mode in {"beta", "public"} and receipt is None:
        errors.append("MISSING_INDEPENDENT_BYTE_RECEIPT")
    # The receipt digest is not itself evidence that its author had authority;
    # the final public decision remains with an independent reviewer.
    return {
        "status": "HOLD_NO_DEPLOY" if errors else "PRIVATE_AUDIT_ONLY",
        "source_sha": source_sha,
        "mode": mode,
        "file_count": len(files),
        "html_count": html_count,
        "total_bytes": total_bytes,
        "extension_counts": dict(sorted(counts.items())),
        "noindex_html_count": noindex_count,
        "review_warning_html_count": warning_count,
        "scoped_id_count": len(approved_pairs),
        "search_id_count": len(observed_pairs),
        "distribution_tree_sha256": tree_hash,
        "legacy_urls_by_extension": dict(sorted(legacy.items())),
        "reviewer_authority_independently_proven": False,
        "deploy_approved": False,
        "error_codes": dict(sorted(Counter(errors).items())),
    }, hashes


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("site", type=Path)
    p.add_argument("--source-sha", required=True)
    p.add_argument("--manifest", required=True, type=Path)
    p.add_argument("--receipt", type=Path, help="Separate independent byte review, never generated here")
    p.add_argument("--trusted-receipt-sha256",
                   help="Reviewer-supplied receipt SHA256 from outside the checkout")
    p.add_argument("--mode", choices=["private", "beta", "public"], default="private")
    args = p.parse_args()
    site = args.site.resolve(strict=True)
    for source in filter(None, (args.manifest, args.receipt)):
        input_path = source.resolve(strict=True)
        if input_path == site or site in input_path.parents:
            raise SystemExit("Approval inputs must be outside the distribution tree")
    scope = json.loads(args.manifest.read_text(encoding="utf-8"))
    raw_receipt = args.receipt.read_bytes() if args.receipt else None
    receipt = json.loads(raw_receipt.decode("utf-8")) if raw_receipt else None
    report, _ = inspect(
        site, source_sha=args.source_sha, scope=scope, receipt=receipt,
        mode=args.mode, trusted_receipt_sha256=args.trusted_receipt_sha256,
        receipt_byte_sha256=hashlib.sha256(raw_receipt).hexdigest()
        if raw_receipt is not None else None,
    )
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))
    return 0 if report["status"] == "PRIVATE_AUDIT_ONLY" else 2


if __name__ == "__main__":
    raise SystemExit(main())
