#!/usr/bin/env python3
"""Validate the generated database coverage matrix without promoting state."""
from __future__ import annotations

import json
from pathlib import Path

from build_database_coverage_matrix import AXES, OUTPUT, SOURCE_FAMILIES, build, render_summary, SUMMARY_OUTPUT

ROOT = Path(__file__).resolve().parents[1]

ALLOWED = {
    "corpus_availability": {"AVAILABLE", "NOT_AVAILABLE", "NOT_APPLICABLE"},
    "service_scope": {"SCOPE_DEFINED", "SCOPE_PARTIAL", "SCOPE_NOT_DEFINED", "NOT_APPLICABLE"},
    "ingestion": {"INGESTED", "PARTIAL", "NOT_INGESTED", "NOT_APPLICABLE"},
    "item_body_verification": {"PASS", "PARTIAL", "NOT_ESTABLISHED", "NOT_APPLICABLE", "BLOCKED"},
    "currentness": {"PASS", "PARTIAL", "NOT_ESTABLISHED", "NOT_APPLICABLE", "BLOCKED"},
    "relation_verification": {"PASS", "PARTIAL", "NOT_ESTABLISHED", "NOT_APPLICABLE", "BLOCKED"},
    "human_review": {"PASS", "NOT_REVIEWED", "NOT_APPLICABLE", "BLOCKED"},
    "publication": {"AVAILABLE", "NOT_ESTABLISHED", "NOT_APPLICABLE", "BLOCKED"},
    "route_exposure": {"AVAILABLE", "NOT_ESTABLISHED", "NOT_APPLICABLE", "BLOCKED"},
}

FORBIDDEN_SINGLE_SCORE_KEYS = {
    "completion_rate",
    "completion_percentage",
    "overall_completion_rate",
    "overall_completion_percentage",
}

def fail(message: str) -> None:
    raise SystemExit("database coverage matrix invalid: " + message)

def walk_keys(value):
    if isinstance(value, dict):
        for key, child in value.items():
            yield key
            yield from walk_keys(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk_keys(child)

def main() -> None:
    if not OUTPUT.exists():
        fail("generated matrix missing")
    if not SUMMARY_OUTPUT.exists():
        fail("generated summary missing")

    actual = json.loads(OUTPUT.read_text(encoding="utf-8"))
    expected = build()
    if actual != expected:
        fail("generated matrix is stale; run scripts/build_database_coverage_matrix.py")
    if SUMMARY_OUTPUT.read_text(encoding="utf-8") != render_summary(expected):
        fail("generated summary is stale; run scripts/build_database_coverage_matrix.py")

    if actual.get("projection_only") is not True:
        fail("matrix must be explicitly projection-only")
    policy = actual.get("policy", {})
    for key in (
        "canonical_status_writeback_allowed",
        "verification_auto_promotion_allowed",
        "currentness_auto_promotion_allowed",
        "human_review_auto_promotion_allowed",
        "route_auto_enable_allowed",
        "single_completion_percentage_allowed",
    ):
        if policy.get(key) is not False:
            fail(f"fail-closed policy changed: {key}")

    manifest = json.loads((ROOT / "data/services/manifest.json").read_text(encoding="utf-8"))
    expected_services = [row["service_id"] for row in manifest.get("services", [])]
    observed_services = [row["service_id"] for row in actual.get("services", [])]
    if observed_services != expected_services:
        fail("service rows do not match manifest order")

    expected_families = [family["id"] for family in SOURCE_FAMILIES]
    for row in actual.get("services", []):
        observed_families = [cell["source_family"] for cell in row.get("source_families", [])]
        if observed_families != expected_families:
            fail(f"{row['service_id']}: source-family set/order mismatch")
        for cell in row["source_families"]:
            for axis in AXES:
                if axis not in cell:
                    fail(f"{row['service_id']}/{cell['source_family']}: missing {axis}")
                state = cell[axis].get("state")
                if state not in ALLOWED[axis]:
                    fail(f"{row['service_id']}/{cell['source_family']}: invalid {axis}={state}")
            if cell["source_family"] == "delegated_remuneration_criteria":
                applicability = cell.get("service_applicability")
                if not isinstance(applicability, dict):
                    fail(f"{row['service_id']}/delegated_remuneration_criteria: missing service_applicability")
                if applicability.get("state") not in {"MAPPED", "NOT_MAPPED", "NOT_APPLICABLE", "UNKNOWN"}:
                    fail(f"{row['service_id']}/delegated_remuneration_criteria: invalid applicability state")
                if (
                    cell["ingestion"]["state"] in {"INGESTED", "PARTIAL"}
                    and applicability.get("state") != "MAPPED"
                ):
                    fail(f"{row['service_id']}/delegated_remuneration_criteria: ingestion without applicability mapping")

    forbidden = FORBIDDEN_SINGLE_SCORE_KEYS.intersection(set(walk_keys(actual)))
    if forbidden:
        fail(f"single completion score is forbidden: {sorted(forbidden)}")

    relation_summary = actual["summary"]["relation_verification"]
    queue = json.loads((ROOT / "data/relation-verification-queue.json").read_text(encoding="utf-8"))
    if relation_summary.get("remaining_relations") != queue.get("remaining_relations"):
        fail("relation queue remaining count drifted")
    if relation_summary.get("inventory_relations") != queue.get("inventory_relations"):
        fail("relation queue inventory count drifted")

    print(
        "database coverage matrix: PASS "
        f"({actual['summary']['services_total']} services x "
        f"{actual['summary']['source_families_total']} source families)"
    )

if __name__ == "__main__":
    main()
