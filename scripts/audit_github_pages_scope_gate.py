#!/usr/bin/env python3
"""Fail-closed, read-only audit of *exact* unpublished Pages distribution bytes.

An approval is a separate human-reviewed, private input, NEVER generated from
the candidate. Hash matching proves byte identity, not legal correctness.
No site files, secrets, approved record text or approval manifest are uploaded.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

SHA = re.compile(r"^[0-9a-f]{40}$")
HASH = re.compile(r"^[0-9a-f]{64}$")
SENSITIVE = re.compile(
    rb"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|"
    rb"github_pat_[A-Za-z0-9_]{16,}|gh[pousr]_[A-Za-z0-9]{20,}|"
    rb"sk-proj-[A-Za-z0-9_-]{16,}|AKIA[0-9A-Z]{16}|"
    rb"xox[baprs]-[A-Za-z0-9-]{15,}"
)
INTERNAL = (b"INGESTED_UNREVIEWED", b"source_file", b"BEGIN PRIVATE KEY")
TEXT_SUFFIXES = {".html", ".json", ".js", ".mjs", ".css", ".txt", ".svg", ".xml"}
FORBIDDEN_DIRS = {".git", ".github", ".next", "node_modules", "private",
                  "handbook-preview", "__pycache__"}
BETA_LABEL = "Kaigo Rules 試験公開版"
PUBLIC_LABEL = "介護制度資料の参考閲覧版"
PRIVATE_LABEL = "静的移行の検証版（一般公開していません）"


def _ids(rows, context, errors):
    found = []
    if not isinstance(rows, list):
        errors.append("INVALID_ROWS_" + context)
        return set()
    for row in rows:
        if not isinstance(row, dict) or not isinstance(row.get("id"), str) or not row["id"]:
            errors.append("MISSING_ID_" + context)
        else:
            found.append(row["id"])
    if len(found) != len(set(found)):
        errors.append("DUPLICATE_ID_" + context)
    return set(found)


def _reviewed_ids(rows, kind, errors):
    ids = _ids(rows, "APPROVAL_" + kind, errors)
    if not isinstance(rows, list):
        return ids
    for row in rows:
        if not isinstance(row, dict):
            continue
        if (row.get("publish_approved") is not True
                or row.get("state") != "APPROVED_FOR_PUBLICATION"
                or not isinstance(row.get("source_url"), str)
                or not row["source_url"].startswith("https://")):
            errors.append("UNAPPROVED_OR_UNSOURCED_" + kind)
    return ids


def _json(root, relative, errors):
    path = root / relative
    if not path.is_file() or path.is_symlink():
        errors.append("MISSING_REQUIRED_JSON_" + relative.replace("/", "_"))
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (ValueError, UnicodeError, OSError):
        errors.append("INVALID_JSON_" + relative.replace("/", "_"))
        return None


def _scope(root, approval, errors):
    records = approval.get("records", {}) if isinstance(approval, dict) else {}
    if not isinstance(records, dict):
        errors.append("INVALID_APPROVAL_RECORDS")
        return {}
    legal = _reviewed_ids(records.get("legal"), "LEGAL", errors)
    docs = _reviewed_ids(records.get("documents"), "DOCUMENT", errors)
    qa = _reviewed_ids(records.get("qa"), "QA", errors)
    if not legal or not docs or not qa:
        errors.append("EMPTY_APPROVED_RECORD_SET")
    leg = _json(root, "legislation/records.json", errors)
    idx = _json(root, "legislation/record-index.json", errors)
    expected_legal_paths = set()
    if isinstance(leg, dict):
        actual = _ids(leg.get("records"), "LEGAL", errors)
        observed_docs = _ids(leg.get("docs"), "DOCUMENTS", errors)
        if actual != legal or observed_docs != docs:
            errors.append("LEGAL_ALLOWLIST_MISMATCH")
        for row in leg.get("records", []):
            if isinstance(row, dict) and isinstance(row.get("id"), str):
                expected_legal_paths.add("legislation/record/" +
                    hashlib.sha256(row["id"].encode("utf-8")).hexdigest() + ".html")
                if row.get("document") not in docs:
                    errors.append("UNAPPROVED_LEGAL_DOCUMENT")
    else:
        errors.append("INVALID_LEGISLATION_MANIFEST")
    if not isinstance(idx, dict) or set(idx) != legal:
        errors.append("LEGAL_INDEX_MISMATCH")
    observed_legal_paths = {p.relative_to(root).as_posix()
        for p in (root / "legislation/record").glob("*.html")}
    if observed_legal_paths != expected_legal_paths:
        errors.append("LEGAL_DIRECT_URL_MISMATCH")

    search = records.get("search")
    if not isinstance(search, dict) or not search:
        errors.append("MISSING_SEARCH_ALLOWLIST")
        search = {}
    base = root / "databases/search"
    datasets = ["global.json"]
    services = _json(root, "databases/search/services.json", errors)
    if isinstance(services, list):
        service_files = []
        for service in services:
            if (not isinstance(service, dict)
                    or not isinstance(service.get("id"), str)
                    or not re.fullmatch(r"[a-z0-9-]+", service["id"])
                    or service.get("file") != "service-" + service["id"] + ".json"):
                errors.append("INVALID_SERVICE_DATASET")
                continue
            service_files.append(service["file"])
        if len(service_files) != len(set(service_files)):
            errors.append("DUPLICATE_SERVICE_DATASET")
        datasets.extend(service_files)
        existing = {p.name for p in base.glob("service-*.json")}
        if existing != set(service_files):
            errors.append("SERVICE_DATASET_MISMATCH")
    else:
        errors.append("INVALID_SERVICE_MANIFEST")
    all_qa_search_ids = set()
    observed_search = set()
    for dataset in datasets:
        path = "databases/search/" + dataset
        groups = _json(root, path, errors)
        if not isinstance(groups, dict):
            errors.append("INVALID_SEARCH_DATASET")
            continue
        for group, rows in groups.items():
            key = dataset + ":" + group
            observed_search.add(key)
            actual = _ids(rows, "SEARCH", errors)
            expected = _reviewed_ids(search.get(key), "SEARCH", errors)
            if actual != expected:
                errors.append("SEARCH_ALLOWLIST_MISMATCH")
            if dataset == "global.json" and group == "qa":
                all_qa_search_ids = actual
    if observed_search != set(search):
        errors.append("SEARCH_DATASET_ALLOWLIST_MISMATCH")
    if not all_qa_search_ids or not all_qa_search_ids.issubset(qa):
        errors.append("QA_SEARCH_ALLOWLIST_MISMATCH")
    details_root = base / "qa-details"
    actual_qa_paths = {p.relative_to(root).as_posix() for p in details_root.rglob("*.html")}
    approved_qa_paths = {"databases/search/qa-details/" + identifier + "/" + name
        for identifier in qa for name in ("index.html", "reader.html")}
    if actual_qa_paths != approved_qa_paths:
        errors.append("QA_DIRECT_URL_MISMATCH")
    return {"legal": len(legal), "documents": len(docs), "qa": len(qa),
            "search_groups": len(observed_search),
            "search_rows": sum(len(v) for v in search.values() if isinstance(v, list))}


def inspect(root: Path, *, source_sha: str, approval=None, mode="beta"):
    if not SHA.fullmatch(source_sha):
        raise ValueError("Expected exact 40-character source SHA")
    if mode not in {"beta", "private", "public"}:
        raise ValueError("Invalid mode")
    if not root.is_dir() or root.is_symlink():
        raise ValueError("Missing or symlinked candidate")
    root = root.resolve(strict=True)
    entries = list(root.rglob("*"))
    paths = sorted(p for p in entries if p.is_file() and not p.is_symlink())
    errors = []
    if not paths:
        errors.append("EMPTY_SITE")
    if any(p.is_symlink() for p in entries):
        errors.append("SYMLINK_IN_DISTRIBUTION")
    if any(FORBIDDEN_DIRS.intersection(p.relative_to(root).parts)
           or p.name.startswith(".env") for p in paths):
        errors.append("FORBIDDEN_FILE_OR_DIRECTORY")
    if not (root / "index.html").is_file():
        errors.append("MISSING_INDEX")
    bytes_total = sum(p.stat().st_size for p in paths)
    if bytes_total >= 1_000_000_000:
        errors.append("PAGES_SIZE_BUDGET")
    hashes = {}
    counts = Counter()
    html_count = noindex_count = beta_count = 0
    legacy = Counter()
    for p in paths:
        rel = p.relative_to(root).as_posix()
        raw = p.read_bytes()
        hashes[rel] = hashlib.sha256(raw).hexdigest()
        counts[p.suffix.lower() or "(none)"] += 1
        if p.suffix.lower() == ".gz":
            original = p.with_suffix("")
            try:
                if not original.is_file():
                    raise ValueError("no counterpart")
                with gzip.open(p, "rb") as f:
                    decoded = f.read(original.stat().st_size + 1)
                if decoded != original.read_bytes():
                    raise ValueError("not identical")
            except (OSError, EOFError, ValueError):
                errors.append("GZIP_MISMATCH_OR_OVERSIZE")
            continue
        if p.suffix.lower() not in TEXT_SUFFIXES:
            continue
        if SENSITIVE.search(raw):
            errors.append("POSSIBLE_SECRET")
        for value in INTERNAL:
            if value in raw:
                errors.append("INTERNAL_SOURCE_MARKER")
        try:
            content = raw.decode("utf-8")
        except UnicodeDecodeError:
            errors.append("INVALID_UTF8_TEXT")
            continue
        if PRIVATE_LABEL in content and mode in {"beta", "public"}:
            errors.append("PRIVATE_PREVIEW_LABEL_IN_DISTRIBUTION")
        if "handbook-preview" in content:
            errors.append("PRIVATE_PREVIEW_ROUTE_REFERENCE")
        if p.suffix.lower() == ".html":
            html_count += 1
            if re.search(r'<meta\s+name=["\']robots["\']\s+content=["\'][^"\']*noindex', content, re.I):
                noindex_count += 1
            elif mode != "public":
                errors.append("HTML_NOINDEX_MISSING")
            if mode == "public" and "noindex" in content.lower():
                errors.append("PUBLIC_HTML_NOINDEX_REMAINING")
            if BETA_LABEL in content:
                beta_count += 1
            elif mode == "beta":
                errors.append("BETA_BANNER_MISSING")
            if mode == "public" and BETA_LABEL in content:
                errors.append("BETA_LABEL_IN_PUBLIC_RELEASE")
        if "kaigo-rules.vercel.app" in content:
            legacy[p.suffix.lower()] += content.count("kaigo-rules.vercel.app")
    record_count = {}
    if approval is None:
        errors.append("NO_INDEPENDENT_APPROVAL")
    elif not isinstance(approval, dict):
        errors.append("INVALID_APPROVAL")
    else:
        if (approval.get("schema_version") != 1
                or approval.get("source_sha") != source_sha
                or approval.get("decision") != "D_ACCEPTED_SCOPED"):
            errors.append("INVALID_APPROVAL_STATE_OR_SHA")
        expected_hashes = approval.get("file_sha256")
        if not isinstance(expected_hashes, dict) or not expected_hashes:
            errors.append("NO_APPROVED_FILE_HASHES")
        elif (set(hashes) != set(expected_hashes)
              or any(not isinstance(v, str) or not HASH.fullmatch(v)
                     for v in expected_hashes.values())
              or hashes != expected_hashes):
            errors.append("DISTRIBUTION_BYTES_NOT_APPROVED")
        record_count = _scope(root, approval, errors)
    tree_hash = hashlib.sha256(
        "".join(path + "\0" + hashes[path] + "\n" for path in sorted(hashes)).encode()
    ).hexdigest()
    return {
        "status": "PASS_SCOPED_BYTES_ONLY" if not errors else "HOLD_NO_DEPLOY",
        "source_sha": source_sha, "mode": mode,
        "file_count": len(paths), "html_count": html_count, "total_bytes": bytes_total,
        "noindex_html_count": noindex_count, "beta_banner_html_count": beta_count,
        "distribution_tree_sha256": tree_hash,
        "extension_counts": dict(sorted(counts.items())),
        "legacy_text_occurrences_by_type": dict(sorted(legacy.items())),
        "approved_scope_counts": record_count,
        "error_codes": dict(sorted(Counter(errors).items())),
        # Hash inventory deliberately excluded from stdout. It is only returned
        # internally, for separately protected reviewer evidence.
    }, hashes


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("site", type=Path)
    parser.add_argument("--source-sha", required=True)
    parser.add_argument("--approval", type=Path, help="Private, independently reviewed exact-byte approval JSON")
    parser.add_argument("--mode", choices=["private", "beta", "public"], default="beta")
    parser.add_argument("--hash-inventory", type=Path,
                        help="Optional PRIVATE local evidence destination outside distribution")
    args = parser.parse_args()
    root = args.site.resolve(strict=True)
    approval = None
    if args.approval:
        auth = args.approval.resolve(strict=True)
        if auth == root or root in auth.parents:
            raise SystemExit("Approval must be outside the distribution directory")
        approval = json.loads(auth.read_text(encoding="utf-8"))
    report, hashes = inspect(root, source_sha=args.source_sha, approval=approval, mode=args.mode)
    if args.hash_inventory:
        target = args.hash_inventory.resolve()
        if target == root or root in target.parents:
            raise SystemExit("Hash inventory must be outside the distribution directory")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps({"source_sha": args.source_sha, "file_sha256": hashes},
                         ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))
    return 0 if report["status"] == "PASS_SCOPED_BYTES_ONLY" else 2


if __name__ == "__main__":
    raise SystemExit(main())
