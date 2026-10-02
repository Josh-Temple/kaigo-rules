#!/usr/bin/env python3
"""Validate the pinned independent remuneration source-link audit."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
RECORD = DATA / "remuneration-source-link-independent-audit.json"


def fail(message: str) -> None:
    raise SystemExit("remuneration source-link audit validation failed: " + message)


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
    if record.get("scope") != "dayservice-remuneration-source-links":
        fail("unexpected scope")
    if record.get("audit_kind") != "INDEPENDENT_MHLW_SOURCE_LINK_REPARSE":
        fail("unexpected audit kind")
    if record.get("audit_result") != "PASS":
        fail("audit result is not PASS")

    run = record.get("audit_run", {})
    if not isinstance(run.get("run_id"), int) or run["run_id"] <= 0:
        fail("invalid audit run")
    if not re.fullmatch(r"[0-9a-f]{40}", str(run.get("head_sha") or "")):
        fail("invalid audited head SHA")
    if run.get("result") != "PASS":
        fail("audit run is not PASS")

    checks = record.get("checks", [])
    if len(checks) != 2:
        fail("expected exactly two checks")
    identities = {
        (
            str(row.get("from_id") or ""),
            str(row.get("relation") or ""),
            str(row.get("to_source_id") or ""),
        )
        for row in checks
    }
    expected = {
        ("fee.dayservice.root", "currency_conversion_uses", "mhlw-unit-price-current"),
        (
            "fee.dayservice.root",
            "historically_interpreted_by",
            "mhlw-fee-interpretation-historical",
        ),
    }
    if identities != expected:
        fail("audited identity set changed")
    for check in checks:
        if check.get("result") != "PASS" or check.get("differences") != []:
            fail(f"check is not clean PASS: {check.get('id')}")

    relations = load(DATA / "remuneration-relations.json")
    committed = {
        (
            str(row.get("from_fee_id") or ""),
            str(row.get("relation") or ""),
            str(row.get("to_source_id") or ""),
        )
        for row in relations
        if row.get("to_source_id")
    }
    if not identities.issubset(committed):
        fail("audited source-link identity missing from committed relations")

    excluded = record.get("excluded_relation", {}).get("identity", {})
    excluded_identity = (
        str(excluded.get("from") or ""),
        str(excluded.get("relation") or ""),
        str(excluded.get("to") or ""),
    )
    expected_excluded = (
        "fee.dayservice.root",
        "latest_interpretation_amendment_evidence",
        "mhlw-r8-fee-guidance-may-amendment",
    )
    if excluded_identity != expected_excluded:
        fail("freshness-sensitive excluded relation changed")
    if expected_excluded not in committed:
        fail("excluded latest-amendment relation is missing from committed relations")
    if expected_excluded in identities:
        fail("freshness-sensitive latest relation must not be audited here")

    coverage = record.get("coverage", {})
    if coverage.get("relations_in_this_lane") != 2 or coverage.get("relations_passed") != 2:
        fail("coverage changed")

    sources = load(DATA / "sources.json")
    source_rows = {row["id"]: row for row in sources if isinstance(row, dict) and row.get("id")}
    for source_id in ("mhlw-unit-price-current", "mhlw-fee-interpretation-historical"):
        row = source_rows.get(source_id)
        if not row:
            fail(f"source registry entry missing: {source_id}")
        if row.get("publisher") != "厚生労働省":
            fail(f"source publisher changed: {source_id}")
        if not str(row.get("url") or "").startswith("https://www.mhlw.go.jp/"):
            fail(f"source URL changed away from MHLW: {source_id}")

    safety = record.get("safety", {})
    for key in (
        "human_verified",
        "verified_current",
        "automatic_promotion_allowed",
        "promotes_latest_claim",
        "promotes_unlisted_relations",
    ):
        if safety.get(key) is not False:
            fail(f"safety flag must remain false: {key}")

    for relative, expected_blob in record.get("input_git_blob_shas_at_audit", {}).items():
        path = ROOT / relative
        if not path.exists():
            fail(f"pinned input missing: {relative}")
        if git_blob_sha1(path) != expected_blob:
            fail(f"pinned input changed: {relative}")

    print(
        "remuneration source-link audit: OK "
        "(2/2 direct source links PASS; latest-amendment relation excluded)"
    )


if __name__ == "__main__":
    main()
