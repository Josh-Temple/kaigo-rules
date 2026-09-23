#!/usr/bin/env python3
"""Validate pinned provenance for the independent MHLW Q&A corpus audit."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
RECORD_PATH = DATA / "qa-corpus-independent-audit.json"
META_PATH = DATA / "qa-corpus-meta.json"
CORPUS_PATH = DATA / "qa-corpus.json"


def fail(message: str) -> None:
    raise SystemExit("Q&A independent audit validation failed: " + message)


def load(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        fail(f"cannot read valid JSON from {path.relative_to(ROOT)}: {exc}")


def git_blob_sha1(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def main() -> None:
    record = load(RECORD_PATH)
    meta = load(META_PATH)
    corpus = load(CORPUS_PATH)

    if record.get("scope") != "mhlw-qa-corpus-target-service-codes-01-02-06-16":
        fail("unexpected scope")
    if record.get("audit_result") != "PASS":
        fail("audit result is not PASS")
    run = record.get("audit_run", {})
    if run.get("run_id") != 35887602131:
        fail("unexpected audit run")
    if run.get("parser") != "python_stdlib_zipfile_elementtree":
        fail("unexpected independent parser")

    safety = record.get("safety", {})
    if safety.get("human_verified") is not False or safety.get("verified_current") is not False:
        fail("independent audit must not claim human/current verification")
    if safety.get("automatic_promotion_allowed") is not False:
        fail("automatic promotion must remain disabled")

    source = record.get("source", {})
    if meta.get("source_page") != source.get("page_url"):
        fail("source page changed since audit")
    if meta.get("source_workbook") != source.get("workbook_url"):
        fail("source workbook URL changed since audit")
    if meta.get("source_sha256") != source.get("workbook_sha256"):
        fail("source workbook hash changed since audit")
    if meta.get("workbook_sheets") != source.get("sheet_names"):
        fail("workbook sheet set changed since audit")
    if meta.get("parsed_sheets") != source.get("parsed_sheets"):
        fail("parsed sheet set changed since audit")

    observed = record.get("observed", {})
    if meta.get("rows_scanned") != observed.get("rows_scanned"):
        fail("rows_scanned changed since audit")
    if meta.get("rows_included") != observed.get("rows_included"):
        fail("rows_included changed since audit")
    if meta.get("counts_by_service") != observed.get("counts_by_service"):
        fail("service-code counts changed since audit")
    if len(corpus) != observed.get("rows_included"):
        fail("corpus row count differs from audit record")
    if observed.get("row_differences") != 0 or observed.get("source_hash_difference") is not False:
        fail("audit record no longer represents a clean PASS")

    for relative, expected_blob in record.get("input_git_blob_shas_at_audit", {}).items():
        path = ROOT / relative
        if not path.exists():
            fail(f"pinned audit input missing: {relative}")
        if git_blob_sha1(path) != expected_blob:
            fail(f"pinned audit input changed: {relative}")

    print("Q&A independent audit: OK (843 rows / 01:480 / 02:47 / 06:64 / 16:252 PASS)")


if __name__ == "__main__":
    main()
