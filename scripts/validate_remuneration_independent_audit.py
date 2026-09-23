#!/usr/bin/env python3
"""Validate the pinned independent audit record for remuneration notices 19/27/95."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECORD = ROOT / "data" / "remuneration-independent-audit.json"
CURRENT_META = ROOT / "data" / "remuneration-current-text-meta.json"
DELEGATED_META = ROOT / "data" / "remuneration-delegated-meta.json"


def fail(message: str) -> None:
    raise SystemExit("remuneration independent audit validation failed: " + message)


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
    current = load(CURRENT_META)
    delegated = load(DELEGATED_META)

    if record.get("scope") != "dayservice-remuneration-notices-19-27-95":
        fail("unexpected scope")
    if record.get("audit_result") != "PASS":
        fail("audit result is not PASS")
    if record.get("audit_issue", {}).get("number") != 74:
        fail("audit provenance must point to issue #74")
    if record.get("full_verification_run", {}).get("run_id") != 35738301488:
        fail("unexpected full verification run")

    safety = record.get("safety", {})
    if safety.get("human_verified") is not False or safety.get("verified_current") is not False:
        fail("independent audit must not claim human/current verification")
    if safety.get("automatic_promotion_allowed") is not False:
        fail("automatic promotion must remain disabled")

    sources = record.get("sources", {})
    if current.get("source_url") != sources.get("notice19", {}).get("url"):
        fail("notice19 URL differs from audit record")
    if current.get("source_sha256") != sources.get("notice19", {}).get("sha256"):
        fail("notice19 source hash differs from audit record")

    d_sources = delegated.get("sources", {})
    for key in ("notice27", "notice95"):
        if d_sources.get(key, {}).get("url") != sources.get(key, {}).get("url"):
            fail(f"{key} URL differs from audit record")
        if d_sources.get(key, {}).get("sha256") != sources.get(key, {}).get("sha256"):
            fail(f"{key} source hash differs from audit record")

    counts = record.get("observed_counts", {})
    if current.get("record_count") != counts.get("notice19_records"):
        fail("notice19 record count differs from audit")
    d_counts = delegated.get("counts", {})
    if d_counts.get("notice27_nodes") != counts.get("notice27_nodes"):
        fail("notice27 node count differs from audit")
    if d_counts.get("notice95_nodes") != counts.get("notice95_nodes"):
        fail("notice95 node count differs from audit")
    if d_counts.get("nodes") != counts.get("delegated_nodes_total"):
        fail("delegated node total differs from audit")

    for relative, expected in record.get("input_git_blob_shas_at_audit", {}).items():
        path = ROOT / relative
        if not path.exists():
            fail(f"pinned audit input missing: {relative}")
        if git_blob_sha1(path) != expected:
            fail(f"pinned audit input changed: {relative}")

    print("remuneration independent audit: OK (notice19/27/95 PASS; scheduled live verifier remains authoritative for drift)")


if __name__ == "__main__":
    main()
