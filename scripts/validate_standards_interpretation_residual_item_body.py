#!/usr/bin/env python3
"""Validate Worker A residual Standards Interpretation item-body assurance.

This validator is deliberately fail-closed. It verifies that every current
NOT_ESTABLISHED service is classified, that shared source-body snapshots are
pinned only as source-level evidence, and that no service-level PASS or
downstream assurance axis is inferred without canonical item-level comparison.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INVENTORY = ROOT / "data/verification/standards-interpretation-item-body/core-item-body-assurance-expansion-worker-a.json"
MATRIX = ROOT / "data/database-coverage-matrix.generated.json"
SOURCE_REGISTER = ROOT / "data/shared/standards-interpretation/remaining-source-register.json"
ROUKI25_MANIFEST = ROOT / "data/shared/standards-interpretation/manifest.json"

REQUIRED_DIRECT_SOURCE_IDS = {
    "mhlw-regional-community-rouki33-original-direct-notice",
    "mhlw-elderly-welfare-facility-rouki43-notice",
    "mhlw-elderly-health-facility-rouki44-notice",
    "mhlw-care-medical-institution-notice",
}


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def current_residual_ids(matrix: dict) -> set[str]:
    result: set[str] = set()
    for service in matrix.get("services", []):
        family = next(
            (
                row
                for row in service.get("source_families", [])
                if row.get("source_family") == "standards_interpretation_notice"
            ),
            None,
        )
        if family and family.get("item_body_verification", {}).get("state") == "NOT_ESTABLISHED":
            result.add(service["service_id"])
    return result


def validate() -> list[str]:
    errors: list[str] = []
    inventory = load(INVENTORY)
    matrix = load(MATRIX)
    register = load(SOURCE_REGISTER)
    manifest = load(ROUKI25_MANIFEST)

    if inventory.get("source_family") != "standards_interpretation_notice":
        errors.append("inventory source family mismatch")

    rows = inventory.get("inventory", [])
    if len(rows) != 26:
        errors.append(f"expected 26 residual rows, got {len(rows)}")

    by_id = {row.get("service_id"): row for row in rows}
    if len(by_id) != len(rows) or None in by_id:
        errors.append("duplicate or missing service_id in residual inventory")

    expected = current_residual_ids(matrix)
    if set(by_id) != expected:
        errors.append(
            "residual inventory differs from current coverage matrix: "
            f"missing={sorted(expected - set(by_id))} extra={sorted(set(by_id) - expected)}"
        )

    for service_id, row in by_id.items():
        if row.get("prior_item_body_state") != "NOT_ESTABLISHED":
            errors.append(f"{service_id}: prior item-body state changed")
        if row.get("item_body_state") != "NOT_ESTABLISHED":
            errors.append(f"{service_id}: unsafe item-body promotion")
        if row.get("service_level_projection_eligible") is not False:
            errors.append(f"{service_id}: projection unexpectedly eligible")
        if row.get("item_level_staging_exists") is not False:
            errors.append(f"{service_id}: staging existence changed without canonical artifact")
        if row.get("canonical_item_body_exists") is not False:
            errors.append(f"{service_id}: canonical item body unexpectedly claimed")
        if row.get("direct_body_comparison_possible") is not False:
            errors.append(f"{service_id}: direct body comparison unexpectedly claimed")

        invariant = row.get("projection_invariant", {})
        for key in (
            "official_primary_source_identity_fixed",
            "source_version_identified",
            "service_scope_explicit",
            "omitted_text_not_treated_as_body",
            "other_axes_not_promoted",
        ):
            if invariant.get(key) is not True:
                errors.append(f"{service_id}: invariant {key} must be true")
        for key in (
            "canonical_body_compared_to_official",
            "full_referenced_node_range_verified",
            "non_historical_non_superseded_pin",
        ):
            if invariant.get(key) is not False:
                errors.append(f"{service_id}: invariant {key} must remain false")

        blockers = set(row.get("blocker_codes", []))
        for required in (
            "CANONICAL_ITEM_BODY_NOT_AVAILABLE_FOR_COMPARISON",
            "NO_ITEM_LEVEL_STAGING",
            "SERVICE_LEVEL_BODY_COMPARISON_NOT_POSSIBLE",
        ):
            if required not in blockers:
                errors.append(f"{service_id}: missing blocker {required}")

        safety = row.get("safety", {})
        if safety.get("currentness") != "NOT_ESTABLISHED":
            errors.append(f"{service_id}: currentness promoted")
        if safety.get("human_review") != "NOT_REVIEWED":
            errors.append(f"{service_id}: human review promoted")
        if safety.get("publication_promoted") is not False:
            errors.append(f"{service_id}: publication promoted")
        if safety.get("route_promoted") is not False:
            errors.append(f"{service_id}: route promoted")

        snapshots = row.get("pinned_source_body_snapshots", [])
        if row.get("local_or_pinned_snapshot_available") != bool(snapshots):
            errors.append(f"{service_id}: snapshot availability mismatch")
        for relative in snapshots:
            path = ROOT / relative
            if not path.exists():
                errors.append(f"{service_id}: snapshot missing: {relative}")
                continue
            text = path.read_text(encoding="utf-8")
            if "currentness_proof: false" not in text:
                errors.append(f"{service_id}: snapshot does not preserve currentness separation: {relative}")
            if "observed_date: 2026-10-05" not in text:
                errors.append(f"{service_id}: snapshot observed date missing: {relative}")

    projection = inventory.get("service_projection", {})
    if projection.get("projected_to_pass") != 0:
        errors.append("service-level projected PASS must remain zero")
    if projection.get("kept_not_established") != 26:
        errors.append("kept_not_established must remain 26")

    safety = inventory.get("safety", {})
    for key in (
        "heading_only_never_promoted",
        "historical_body_never_treated_as_current_integrated_text",
        "comparison_only_never_treated_as_current_integrated_text",
        "omitted_text_never_treated_as_body_match",
    ):
        if safety.get(key) is not True:
            errors.append(f"wave safety flag weakened: {key}")
    for key in (
        "currentness_promotions",
        "human_review_promotions",
        "publication_promotions",
        "route_promotions",
    ):
        if safety.get(key) != 0:
            errors.append(f"wave safety promotion count nonzero: {key}")
    if safety.get("global_generated_artifacts_modified") is not False:
        errors.append("global generated artifact mutation claimed")

    source_by_id = {row.get("source_id"): row for row in register.get("sources", [])}
    for source_id in REQUIRED_DIRECT_SOURCE_IDS:
        source = source_by_id.get(source_id)
        if not source:
            errors.append(f"direct source not registered: {source_id}")
            continue
        snap = source.get("body_snapshot", {})
        relative = snap.get("path")
        if source.get("acquisition_state") != "OFFICIAL_BODY_SNAPSHOT_PINNED":
            errors.append(f"{source_id}: acquisition state not pinned")
        if not relative or not (ROOT / relative).exists():
            errors.append(f"{source_id}: registered snapshot missing")
        if not snap.get("git_blob_sha"):
            errors.append(f"{source_id}: snapshot git blob sha missing")
        if snap.get("currentness_proof") is not False:
            errors.append(f"{source_id}: snapshot improperly proves currentness")

    rouki25 = next(
        (row for row in manifest.get("sources", []) if row.get("source_id") == "rouki25-mhlw-direct-display"),
        None,
    )
    if not rouki25:
        errors.append("rouki25 direct body display source missing")
    else:
        snapshots = rouki25.get("body_snapshots", [])
        if len(snapshots) != 2:
            errors.append("rouki25 expected two pinned display snapshots")
        for snap in snapshots:
            relative = snap.get("path")
            if not relative or not (ROOT / relative).exists():
                errors.append("rouki25 pinned display snapshot missing")
            if not snap.get("git_blob_sha"):
                errors.append("rouki25 pinned display blob sha missing")
        if rouki25.get("current_integrated_text") is not False:
            errors.append("rouki25 direct display was promoted to current integrated text")

    return errors


def main() -> int:
    errors = validate()
    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        return 1
    print("PASS: Standards Interpretation residual item-body assurance remains fail-closed (26 classified; 0 unsafe projections).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
