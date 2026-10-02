#!/usr/bin/env python3
"""Validate pinned provenance for the fee-guidance relation audit."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
RECORD = DATA / "fee-guidance-relation-independent-audit.json"


def fail(message: str) -> None:
    raise SystemExit("fee-guidance relation audit validation failed: " + message)


def load(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        fail(f"cannot read valid JSON from {path.relative_to(ROOT)}: {exc}")


def git_blob_sha1(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def main() -> None:
    record = load(RECORD)
    if record.get("scope") != "dayservice-fee-guidance-to-remuneration-relations":
        fail("unexpected scope")
    if record.get("audit_kind") != "INDEPENDENT_PRIMARY_SOURCE_RELATION_REPARSE":
        fail("unexpected audit kind")
    if record.get("audit_result") != "PASS":
        fail("audit result is not PASS")

    run = record.get("audit_run", {})
    if not isinstance(run.get("run_id"), int) or run["run_id"] <= 0:
        fail("invalid audit run")
    if not re.fullmatch(r"[0-9a-f]{40}", str(run.get("head_sha") or "")):
        fail("invalid audited head SHA")
    if run.get("result") != "PASS":
        fail("audit run result is not PASS")

    sources = record.get("sources", {})
    for source_key in ("guidance_r6_redline", "notice19"):
        source = sources.get(source_key, {})
        if not str(source.get("url") or "").startswith("https://www.mhlw.go.jp/"):
            fail(f"{source_key}: unexpected source URL")
        if not re.fullmatch(r"[0-9a-f]{64}", str(source.get("sha256") or "")):
            fail(f"{source_key}: invalid source SHA-256")

    source_registry = {
        row["url"]: row
        for row in load(DATA / "sources.json")
        if isinstance(row, dict) and row.get("url")
    }
    for source in sources.values():
        if source.get("url") not in source_registry:
            fail(f"official source missing from sources registry: {source.get('url')}")

    safety = record.get("safety", {})
    if safety.get("human_verified") is not False:
        fail("audit must not claim HUMAN_VERIFIED")
    if safety.get("verified_current") is not False:
        fail("audit must not claim VERIFIED_CURRENT")
    if safety.get("automatic_promotion_allowed") is not False:
        fail("automatic promotion must remain disabled")
    if safety.get("promotes_guidance_text_currentness") is not False:
        fail("guidance text currentness must remain unpromoted")
    if safety.get("promotes_unlisted_relations") is not False:
        fail("unlisted relations must remain unpromoted")

    relations = load(DATA / "fee-guidance-relations.json")
    current_identities = {
        (
            str(row.get("from_guidance_id") or ""),
            str(row.get("relation") or ""),
            str(row.get("to_fee_id") or ""),
        )
        for row in relations
    }
    checks = record.get("checks", [])
    audited_identities = {
        (
            str(row.get("from_guidance_id") or ""),
            str(row.get("relation") or ""),
            str(row.get("to_fee_id") or ""),
        )
        for row in checks
    }
    if len(checks) != 24 or len(audited_identities) != 24:
        fail("expected exactly 24 unique audit checks")
    if audited_identities != current_identities:
        fail("audited relation identity set differs from committed relations")
    for check in checks:
        if check.get("result") != "PASS" or check.get("differences") != []:
            fail(f"audit check is not clean PASS: {check.get('id')}")
        if check.get("relation") != "explains_calculation_of":
            fail(f"unexpected relation type: {check.get('id')}")

    coverage = record.get("coverage", {})
    if coverage.get("relations_in_this_lane") != 24:
        fail("lane relation count changed")
    if coverage.get("relations_passed") != 24:
        fail("lane PASS count changed")

    for relative, expected_blob in record.get("input_git_blob_shas_at_audit", {}).items():
        path = ROOT / relative
        if not path.exists():
            fail(f"pinned audit input missing: {relative}")
        if git_blob_sha1(path) != expected_blob:
            fail(f"pinned audit input changed: {relative}")

    print(
        "fee-guidance relation audit: OK "
        "(24/24 primary-source relation identities PASS; no human/current promotion)"
    )


if __name__ == "__main__":
    main()
