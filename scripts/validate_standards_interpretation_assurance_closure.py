#!/usr/bin/env python3
"""Validate the standards-interpretation assurance-closure inventory.

The closure inventory is deliberately fail-closed. It records which service/source
pairs can be promoted on item-body evidence and which must remain NOT_ESTABLISHED.
It never treats scope/heading discovery as item-body equality and never promotes
currentness, human review, publication, or routing.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INVENTORY = (
    ROOT
    / "data/verification/standards-interpretation-item-body/assurance-closure-wave.json"
)
PREVENTIVE_AUDIT = (
    ROOT
    / "data/verification/standards-interpretation-item-body/preventive-support.json"
)
PREVENTIVE_SERVICE = ROOT / "data/services/preventive-support.json"
SHARED_REMAINING_SCOPE = (
    ROOT / "data/shared/standards-interpretation/remaining-service-scopes.json"
)

EXPECTED_UNRESOLVED = {
    "shortstay-medical",
    "specific-facility",
    "welfare-equipment-rental",
    "specific-welfare-equipment-sale",
    "dementia-dayservice",
    "small-scale-multifunctional",
    "dementia-group-home",
    "community-specific-facility",
    "community-elderly-facility",
    "nursing-small-scale-multifunctional",
    "elderly-welfare-facility",
    "elderly-health-facility",
    "care-medical-institution",
    "preventive-homebath",
    "preventive-homenursing",
    "preventive-homerehab",
    "preventive-homecaremanagement",
    "preventive-dayrehab",
    "preventive-shortstay-life",
    "preventive-shortstay-medical",
    "preventive-specific-facility",
    "preventive-welfare-equipment-rental",
    "specific-preventive-welfare-equipment-sale",
    "preventive-dementia-dayservice",
    "preventive-small-scale-multifunctional",
    "preventive-dementia-group-home",
}


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def validate() -> list[str]:
    errors: list[str] = []
    inventory = load(INVENTORY)

    before = inventory.get("before", {}).get("service_level_item_body")
    after = inventory.get("after_worker_c", {}).get("service_level_item_body")
    if before != {"PASS": 12, "PARTIAL": 1, "NOT_ESTABLISHED": 26}:
        errors.append(f"unexpected before inventory: {before}")
    if after != {"PASS": 13, "PARTIAL": 0, "NOT_ESTABLISHED": 26}:
        errors.append(f"unexpected post-worker inventory: {after}")

    resolved = inventory.get("resolved", [])
    if len(resolved) != 1 or resolved[0].get("service_id") != "preventive-support":
        errors.append("resolved set must contain preventive-support only")
    elif resolved[0].get("new_state") != "PASS_CONTENT_EVIDENCE_MATCH_ONLY":
        errors.append("preventive-support closure is not item-body PASS")
    else:
        for key, expected in (
            ("currentness", "NOT_ESTABLISHED"),
            ("human_review", "NOT_REVIEWED"),
        ):
            if resolved[0].get(key) != expected:
                errors.append(f"preventive-support {key} was promoted")
        if resolved[0].get("publication_allowed") is not False:
            errors.append("preventive-support publication was promoted")
        if resolved[0].get("route_enabled") is not False:
            errors.append("preventive-support route was enabled")

    unresolved = inventory.get("unresolved", [])
    by_service = {row.get("service_id"): row for row in unresolved}
    if set(by_service) != EXPECTED_UNRESOLVED:
        errors.append(
            "unresolved service set mismatch: "
            f"missing={sorted(EXPECTED_UNRESOLVED - set(by_service))} "
            f"extra={sorted(set(by_service) - EXPECTED_UNRESOLVED)}"
        )
    if len(unresolved) != 26:
        errors.append(f"unresolved count {len(unresolved)} != 26")

    shared = load(SHARED_REMAINING_SCOPE)
    shared_by_service = {
        row["service_id"]: row for row in shared.get("services", [])
    }

    for service_id, row in by_service.items():
        if row.get("item_body_state") != "NOT_ESTABLISHED":
            errors.append(f"{service_id}: item-body state was promoted")
        if row.get("staging_present") is not False:
            errors.append(f"{service_id}: staging presence overclaimed")
        if row.get("canonical_item_body_present") is not False:
            errors.append(f"{service_id}: canonical item body overclaimed")
        blockers = set(row.get("blocker_codes", []))
        if "CANONICAL_ITEM_BODY_NOT_AVAILABLE_FOR_COMPARISON" not in blockers:
            errors.append(f"{service_id}: canonical-body blocker missing")
        if "NO_ITEM_LEVEL_STAGING" not in blockers:
            errors.append(f"{service_id}: staging blocker missing")
        if "NO_ITEM_BODY_RECEIPT" not in blockers:
            errors.append(f"{service_id}: receipt blocker missing")

        if (
            ROOT
            / f"data/verification/standards-interpretation-item-body/{service_id}.json"
        ).exists():
            errors.append(f"{service_id}: receipt exists but inventory says unresolved")
        if (
            ROOT / f"data/services/{service_id}/standards-interpretation-staging.json"
        ).exists():
            errors.append(f"{service_id}: staging exists but inventory says absent")

        if row.get("scope_source") == "SERVICE_SCOPE":
            scope_path = (
                ROOT / f"data/services/{service_id}/standards-interpretation-scope.json"
            )
            if not scope_path.exists():
                errors.append(f"{service_id}: service scope file missing")
            else:
                scope = load(scope_path)
                if scope.get("item_body_verification") != "NOT_ESTABLISHED":
                    errors.append(f"{service_id}: service scope item-body state changed")
        elif row.get("scope_source") == "SHARED_REMAINING_SCOPE":
            scope = shared_by_service.get(service_id)
            if not scope:
                errors.append(f"{service_id}: shared remaining scope missing")
            elif scope.get("item_body_verification") != "NOT_ESTABLISHED":
                errors.append(f"{service_id}: shared scope item-body state changed")
            if "OFFICIAL_SOURCE_LOCATED_BUT_ITEM_BODY_SNAPSHOT_NOT_ESTABLISHED" not in blockers:
                errors.append(f"{service_id}: shared snapshot blocker missing")
        else:
            errors.append(f"{service_id}: unknown scope_source")

    preventive_audit = load(PREVENTIVE_AUDIT)
    summary = preventive_audit.get("integration_summary", {})
    if summary.get("verification_status") != "PASS_CONTENT_EVIDENCE_MATCH_ONLY":
        errors.append("preventive-support audit summary not closed")
    if summary.get("counts") != {"PASS": 34, "PARTIAL": 0, "GAP": 0, "FAIL": 0}:
        errors.append("preventive-support audit counts mismatch")
    if summary.get("currentness_state") != "NOT_ESTABLISHED":
        errors.append("preventive-support audit currentness promoted")
    if summary.get("human_review_state") != "NOT_REVIEWED":
        errors.append("preventive-support audit human review promoted")

    service = load(PREVENTIVE_SERVICE)
    layer = service.get("ingestion_layers", {}).get("standards_interpretation", {})
    if layer.get("item_body_verification") != "PASS_CONTENT_EVIDENCE_MATCH_ONLY":
        errors.append("preventive-support service item-body state mismatch")
    if service.get("routing", {}).get("future_service_base_enabled") is not False:
        errors.append("preventive-support route was enabled")
    gate = service.get("publication_gate", {})
    if any(
        gate.get(key) is not False
        for key in (
            "public_routes_enabled",
            "content_ingested",
            "independent_verification_complete",
            "human_review_complete",
        )
    ):
        errors.append("preventive-support publication gate was promoted")

    safety = inventory.get("safety", {})
    if safety.get("generated_coverage_artifacts_updated") is not False:
        errors.append("global generated coverage artifact update was claimed")
    for key in (
        "scope_heading_treated_as_item_body",
        "historical_text_treated_as_current_integrated_text",
        "currentness_auto_promoted",
        "human_review_auto_promoted",
        "publication_auto_promoted",
        "route_auto_enabled",
    ):
        if safety.get(key) is not False:
            errors.append(f"safety boundary weakened: {key}")

    return errors


def main() -> int:
    errors = validate()
    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        return 1
    print(
        "PASS standards-interpretation assurance closure: "
        "preventive-support item-body closed; 26 services remain fail-closed"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
