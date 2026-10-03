#!/usr/bin/env python3
"""Validate the community-dayservice standards-interpretation item-body audit.

This validator is deliberately service-specific. It verifies the pinned audit
contract and safety boundaries; it does not promote currentness, reconstruct
omitted notice text, or publish the staging dataset.
"""
from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SERVICE_ID = "community-dayservice"
EXPECTED_ITEMS = 21

SCOPE = ROOT / "data/services/community-dayservice/standards-interpretation-scope.json"
STAGING = ROOT / "data/services/community-dayservice/standards-interpretation-staging.json"
SOURCE_INVENTORY = (
    ROOT
    / "data/verification/standards-interpretation-source-inventory/community-dayservice.json"
)
AUDIT = (
    ROOT
    / "data/verification/standards-interpretation-item-body/community-dayservice.json"
)


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def git_blob_sha(path: Path) -> str:
    body = path.read_bytes()
    header = f"blob {len(body)}\0".encode("ascii")
    return hashlib.sha1(header + body).hexdigest()


def validate() -> list[str]:
    errors: list[str] = []
    staging = load(STAGING)
    audit = load(AUDIT)

    if staging.get("service_id") != SERVICE_ID:
        errors.append("staging service_id mismatch")
    if staging.get("item_count") != EXPECTED_ITEMS:
        errors.append("staging declared item_count mismatch")
    staging_items = staging.get("items", [])
    if len(staging_items) != EXPECTED_ITEMS:
        errors.append("staging observed item count mismatch")

    if audit.get("service_id") != SERVICE_ID:
        errors.append("audit service_id mismatch")
    if audit.get("audit_kind") != "INDEPENDENT_STANDARDS_INTERPRETATION_ITEM_BODY_VERIFICATION":
        errors.append("unexpected audit_kind")
    if audit.get("audit_result") != "PASS_WITH_ITEM_LEVEL_EVIDENCE":
        errors.append("unexpected audit_result")

    scope = audit.get("scope", {})
    if scope.get("expected_items") != EXPECTED_ITEMS or scope.get("observed_items") != EXPECTED_ITEMS:
        errors.append("audit scope item count mismatch")
    if "currentness" not in scope.get("does_not_verify", []):
        errors.append("audit must explicitly exclude currentness")

    allowed_statuses = {"PASS", "PARTIAL", "GAP", "FAIL"}
    audit_items = audit.get("items", [])
    if len(audit_items) != EXPECTED_ITEMS:
        errors.append("audit item count mismatch")

    staging_by_id = {item.get("id"): item for item in staging_items}
    audit_by_id = {item.get("id"): item for item in audit_items}
    if set(staging_by_id) != set(audit_by_id):
        errors.append("audit/staging item-id set mismatch")

    sources = {row.get("id"): row for row in audit.get("sources", [])}
    if len(sources) != len(audit.get("sources", [])):
        errors.append("duplicate or missing source id")

    observed_counts: Counter[str] = Counter()
    for item_id, row in audit_by_id.items():
        status = row.get("status")
        if status not in allowed_statuses:
            errors.append(f"{item_id}: invalid status {status!r}")
            continue
        observed_counts[status] += 1

        original = staging_by_id.get(item_id, {})
        for field in ("path", "number", "heading"):
            if row.get(field) != original.get(field):
                errors.append(f"{item_id}: {field} drifted from staging")

        evidence = row.get("evidence", [])
        if not evidence:
            errors.append(f"{item_id}: evidence missing")
            continue

        evidence_sources = []
        for ev in evidence:
            source_id = ev.get("source_id")
            source = sources.get(source_id)
            if source is None:
                errors.append(f"{item_id}: unknown evidence source {source_id!r}")
                continue
            evidence_sources.append(source)
            if not ev.get("locator") or not ev.get("support"):
                errors.append(f"{item_id}: evidence locator/support incomplete")

        if status in {"PASS", "PARTIAL"}:
            if not any(source.get("authority") == "MHLW_PRIMARY" for source in evidence_sources):
                errors.append(f"{item_id}: {status} lacks MHLW primary evidence")

        if not row.get("gap_resolution"):
            errors.append(f"{item_id}: gap_resolution missing")

    declared_counts = audit.get("counts", {})
    normalized_counts = {key: observed_counts.get(key, 0) for key in ("PASS", "PARTIAL", "GAP", "FAIL")}
    if declared_counts != normalized_counts:
        errors.append(
            f"status counts mismatch: declared={declared_counts!r} observed={normalized_counts!r}"
        )

    local = sources.get("yokohama-local-crosscheck", {})
    if local.get("authority") != "OFFICIAL_LOCAL_SUPPLEMENTAL":
        errors.append("Yokohama source must remain supplemental")
    if local.get("availability_state") != "STALE_URL_404_2026-10-03":
        errors.append("Yokohama stale-URL state missing")
    if local.get("required_for_item_body_verification") is not False:
        errors.append("Yokohama stale source must not be required for item-body verification")

    stale = audit.get("stale_sources", [])
    if not any(
        row.get("source_id") == "yokohama-local-crosscheck"
        and row.get("effect_on_verification") == "NON_BLOCKING"
        for row in stale
    ):
        errors.append("stale supplemental source disposition missing")

    safety = audit.get("safety", {})
    for key in (
        "currentness_promoted",
        "human_review_promoted",
        "publication_permitted",
        "public_route_enabled",
        "omitted_text_reconstructed",
        "integrated_current_text_claimed",
    ):
        if safety.get(key) is not False:
            errors.append(f"safety boundary weakened: {key}")

    expected_blobs = {
        str(SCOPE.relative_to(ROOT)): git_blob_sha(SCOPE),
        str(STAGING.relative_to(ROOT)): git_blob_sha(STAGING),
        str(SOURCE_INVENTORY.relative_to(ROOT)): git_blob_sha(SOURCE_INVENTORY),
    }
    if audit.get("input_git_blob_shas_at_audit") != expected_blobs:
        errors.append("audit input blob SHAs are stale")

    return errors


def main() -> int:
    errors = validate()
    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        return 1

    audit = load(AUDIT)
    counts = audit["counts"]
    print(
        "community-dayservice item-body audit: PASS "
        f"({EXPECTED_ITEMS} items; PASS={counts['PASS']} PARTIAL={counts['PARTIAL']} "
        f"GAP={counts['GAP']} FAIL={counts['FAIL']}; currentness not promoted)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
