#!/usr/bin/env python3
"""Validate the pinned independent audit record for day-service unit prices."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECORD = ROOT / "data" / "unit-price-independent-audit.json"
DAY_META = ROOT / "data" / "unit-price-dayservice-meta.json"
REGION_META = ROOT / "data" / "unit-price-region-assignments-meta.json"


def fail(message: str) -> None:
    raise SystemExit("unit-price independent audit validation failed: " + message)


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
    day = load(DAY_META)
    region = load(REGION_META)

    if record.get("scope") != "dayservice-unit-price-and-427-region-assignments":
        fail("unexpected scope")
    if record.get("audit_result") != "PASS":
        fail("audit result is not PASS")
    if record.get("audit_issue", {}).get("number") != 73:
        fail("audit provenance must point to issue #73")
    if record.get("full_verification_run", {}).get("run_id") != 35738301404:
        fail("unexpected full verification run")

    safety = record.get("safety", {})
    if safety.get("human_verified") is not False or safety.get("verified_current") is not False:
        fail("independent audit must not claim human/current verification")
    if safety.get("automatic_promotion_allowed") is not False:
        fail("automatic promotion must remain disabled")

    expected_urls = [row["url"] for row in record.get("sources", [])]
    expected_hashes = [row["sha256"] for row in record.get("sources", [])]
    if day.get("source_urls") != expected_urls:
        fail("unit-price source URLs differ from audit record")
    if day.get("source_sha256") != expected_hashes:
        fail("unit-price source hashes differ from audit record")
    if region.get("source_urls") != expected_urls:
        fail("region-assignment source URLs differ from audit record")
    if region.get("source_sha256") != expected_hashes:
        fail("region-assignment source hashes differ from audit record")

    counts = record.get("observed_counts", {})
    if day.get("rate_count") != counts.get("rate_count"):
        fail("rate count differs from audit")
    if region.get("explicit_assignment_count") != counts.get("explicit_assignment_count"):
        fail("explicit assignment count differs from audit")
    if region.get("default_rule_present") is not counts.get("default_rule_present"):
        fail("default-rule state differs from audit")
    if region.get("effective_reference_date") != record.get("effective_reference_date"):
        fail("effective reference date differs from audit")

    for relative, expected in record.get("input_git_blob_shas_at_audit", {}).items():
        path = ROOT / relative
        if not path.exists():
            fail(f"pinned audit input missing: {relative}")
        if git_blob_sha1(path) != expected:
            fail(f"pinned audit input changed: {relative}")

    print("unit-price independent audit: OK (8 rates + 427 assignments PASS; scheduled live verifier remains authoritative for drift)")


if __name__ == "__main__":
    main()
