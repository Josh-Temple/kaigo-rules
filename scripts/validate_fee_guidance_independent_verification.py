#!/usr/bin/env python3
"""Validate provenance for the 老企第36号 day-service independent audit record."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECORD_PATH = ROOT / "data" / "fee-guidance-independent-verification.json"
CANDIDATES_PATH = ROOT / "data" / "fee-guidance-current-text-candidates.json"
EXPECTED_COUNT = 8


def fail(message: str) -> None:
    raise SystemExit("fee-guidance independent verification validation failed: " + message)


def load_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        fail(f"cannot read valid JSON from {path.relative_to(ROOT)}: {exc}")


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def git_blob_sha1(path: Path) -> str:
    data = path.read_bytes()
    header = f"blob {len(data)}\0".encode("ascii")
    return hashlib.sha1(header + data).hexdigest()


def main() -> None:
    record = load_json(RECORD_PATH)
    candidates = load_json(CANDIDATES_PATH)

    if record.get("scope") != "rouki36-dayservice-8":
        fail("unexpected scope")
    if record.get("audit_result") != "TEXT_RECONSTRUCTION_PASS":
        fail("audit result must remain TEXT_RECONSTRUCTION_PASS")
    if record.get("verified_through") != "2026-09-22":
        fail("verified_through changed; refresh the audit record")
    if record.get("audited_main_sha") != "2503a08579dda3c24cb3efa3f58856da9d9172e8":
        fail("audited main SHA changed unexpectedly")
    if record.get("audit_issue", {}).get("number") != 72:
        fail("audit provenance must remain traceable to issue #72")

    safety = record.get("safety", {})
    if safety.get("human_verified") is not False:
        fail("independent audit must not claim HUMAN_VERIFIED")
    if safety.get("verified_current") is not False:
        fail("independent audit must not claim VERIFIED_CURRENT")
    if safety.get("automatic_promotion_allowed") is not False:
        fail("automatic promotion must remain disabled")

    candidate_items = candidates.get("items", [])
    record_items = record.get("items", [])
    if len(candidate_items) != EXPECTED_COUNT or len(record_items) != EXPECTED_COUNT:
        fail("expected exactly eight candidate and audit items")

    current = {row.get("guidance_id"): row for row in candidate_items}
    audited = {row.get("guidance_id"): row for row in record_items}
    if len(current) != EXPECTED_COUNT or set(current) != set(audited):
        fail("candidate IDs differ from the independent audit record")

    for guidance_id, candidate in current.items():
        actual_hash = sha256_text(candidate.get("candidate_text", ""))
        declared_hash = candidate.get("candidate_text_sha256")
        audited_hash = audited[guidance_id].get("candidate_text_sha256")
        if actual_hash != declared_hash:
            fail(f"{guidance_id}: candidate text does not match its declared hash")
        if actual_hash != audited_hash:
            fail(f"{guidance_id}: candidate changed since independent audit")
        if audited[guidance_id].get("result") != "PASS":
            fail(f"{guidance_id}: audit item is not PASS")
        if candidate.get("reconstruction_status") != "MACHINE_RECONSTRUCTED_NEEDS_HUMAN_CHECK":
            fail(f"{guidance_id}: unexpected reconstruction status")

    for relative, expected_blob in record.get("input_git_blob_shas_at_audit", {}).items():
        path = ROOT / relative
        if not path.exists():
            fail(f"pinned audit input missing: {relative}")
        observed = git_blob_sha1(path)
        if observed != expected_blob:
            fail(f"audit input changed since issue #72: {relative}")

    print("fee-guidance independent verification: OK (8/8 text reconstruction PASS; no human/current promotion)")


if __name__ == "__main__":
    main()
