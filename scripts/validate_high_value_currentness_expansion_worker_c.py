#!/usr/bin/env python3
"""Validate Worker C bounded high-value currentness expansion."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "data/verification/high-value-currentness-expansion-worker-c.json"
MAPPING = ROOT / "data/unit-price-service-multipliers.json"
ITEM_BODY = ROOT / "data/unit-price-item-body-assurance.json"

EXPECTED_IDS = [
    "homevisit",
    "homebath",
    "homenursing",
    "homerehab",
    "homecaremanagement",
    "shortstay-life",
    "shortstay-medical",
    "specific-facility",
    "welfare-equipment-rental",
    "preventive-homebath",
    "preventive-homenursing",
    "preventive-homerehab",
    "preventive-homecaremanagement",
    "preventive-dayrehab",
    "preventive-shortstay-life",
    "preventive-shortstay-medical",
    "preventive-specific-facility",
    "preventive-welfare-equipment-rental"
]
EXPECTED_FAMILY = "unit_price_regional_classification"


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def fail(message: str) -> None:
    raise SystemExit("high-value currentness expansion invalid: " + message)


def main() -> None:
    artifact = load(ARTIFACT)
    mapping = load(MAPPING)
    item_body = load(ITEM_BODY)

    if artifact.get("artifact_kind") != "CANONICAL_HIGH_VALUE_CURRENTNESS_EXPANSION_DECISION":
        fail("artifact kind mismatch")
    if artifact.get("worker") != "C":
        fail("worker identity mismatch")

    policy = artifact.get("policy") or {}
    for key in (
        "blanket_family_promotion_allowed",
        "item_body_used_as_currentness_shortcut",
        "relation_status_promoted",
        "human_review_promoted",
        "publication_promoted",
        "route_exposure_promoted",
    ):
        if policy.get(key) is not False:
            fail(f"unsafe policy flag: {key}")
    for key in (
        "exact_service_source_family_allowlist_required",
        "live_official_source_reverification_required",
        "shared_source_currentness_separated_from_service_applicability",
    ):
        if policy.get(key) is not True:
            fail(f"missing safety policy: {key}")

    selections = {row.get("source_family"): row for row in artifact.get("target_selection") or []}
    unit = selections.get(EXPECTED_FAMILY) or {}
    if unit.get("disposition") != "BOUNDED_PROMOTION":
        fail("unit-price selection must be BOUNDED_PROMOTION")
    if unit.get("selected_service_ids") != EXPECTED_IDS:
        fail("bounded target set changed")
    care = selections.get("care_insurance_act") or {}
    if care.get("disposition") != "HOLD":
        fail("Care Insurance Act must remain HOLD")

    promotions = artifact.get("promotions") or []
    if [row.get("service_id") for row in promotions] != EXPECTED_IDS:
        fail("promotion identity order/set mismatch")
    if len(set(EXPECTED_IDS)) != len(EXPECTED_IDS):
        fail("duplicate expected service ids")

    map_by_id = {row["service_id"]: row for row in mapping.get("service_mappings") or []}
    body_by_id = {row["service_id"]: row for row in item_body.get("service_projections") or []}

    for row in promotions:
        service_id = row.get("service_id")
        if row.get("source_family") != EXPECTED_FAMILY:
            fail(f"{service_id}: source family mismatch")
        m = map_by_id.get(service_id)
        b = body_by_id.get(service_id)
        if not m or not b:
            fail(f"{service_id}: canonical mapping/item-body row missing")
        if m.get("applicability") != "APPLIES" or b.get("applicability") != "APPLIES":
            fail(f"{service_id}: applicability not APPLIES")
        if b.get("service_level_item_body") != "PASS":
            fail(f"{service_id}: item-body is not PASS")
        proof = row.get("service_applicability_evidence") or {}
        if proof.get("state") != "PASS_DIRECT_SERVICE_SCOPE":
            fail(f"{service_id}: direct service scope proof missing")
        for key in ("official_service_name", "multiplier_profile_id"):
            if proof.get(key) != m.get(key):
                fail(f"{service_id}: {key} differs from canonical mapping")
        if proof.get("source_locator") != b.get("source_locator"):
            fail(f"{service_id}: source locator differs from item-body projection")
        if proof.get("mapped_item_count") != b.get("mapped_item_count"):
            fail(f"{service_id}: mapped item count differs from item-body projection")
        if row.get("ingestion_state") != "INGESTED" or row.get("item_body_state") != "PASS":
            fail(f"{service_id}: ingestion/item-body promotion prerequisite mismatch")
        if row.get("prior_currentness_state") != "NOT_ESTABLISHED":
            fail(f"{service_id}: unexpected prior currentness state")
        gate = row.get("projection_gate") or {}
        if gate.get("allowed") is not True:
            fail(f"{service_id}: projection gate not allowed")
        if gate.get("identity") != f"{service_id}::{EXPECTED_FAMILY}":
            fail(f"{service_id}: projection identity mismatch")
        if gate.get("scope") != "currentness_only":
            fail(f"{service_id}: projection must remain currentness_only")
        if row.get("projected_currentness_state") != "PASS" or row.get("promotion_applied") is not True:
            fail(f"{service_id}: bounded currentness promotion not applied")
        units = set(row.get("allowed_publication_units") or [])
        if units != {
            "SOURCE_TEXT_ITEM_BODY",
            "SOURCE_METADATA_LOCATOR",
            "CURRENTNESS_STATEMENT",
            "SERVICE_APPLICABILITY_STATEMENT",
        }:
            fail(f"{service_id}: safe publication units mismatch")
        unchanged = row.get("unchanged_axes") or {}
        if unchanged.get("relation_verification") != "NOT_ESTABLISHED":
            fail(f"{service_id}: relation was promoted")
        if unchanged.get("human_review") != "NOT_REVIEWED":
            fail(f"{service_id}: human review was promoted")

    effect = artifact.get("projected_effect") or {}
    if effect.get("additional_unit_price_currentness_pass_cells") != len(EXPECTED_IDS):
        fail("projected added PASS count mismatch")
    if effect.get("projected_unit_price_pass_cells") != 19:
        fail("projected Unit Price PASS total must be 19")
    if effect.get("unselected_applicable_unit_price_cells_remain_unestablished") != 18:
        fail("remaining applicable Unit Price count must be 18")
    if effect.get("care_insurance_act_promotions") != 0:
        fail("Care Insurance Act promotion must remain zero")

    boundary = artifact.get("integration_boundary") or {}
    for key in (
        "generated_coverage_matrix_modified_by_worker_c",
        "publication_requirement_scoping_modified_by_worker_c",
        "publication_readiness_modified_by_worker_c",
        "bounded_publication_allowlist_modified_by_worker_c",
    ):
        if boundary.get(key) is not False:
            fail(f"Worker C modified forbidden global generated artifact: {key}")

    safety = artifact.get("safety") or {}
    for key in (
        "promotions_are_exact_identity_allowlisted",
        "human_review_not_faked",
        "relation_verification_not_faked",
        "source_level_currentness_not_blanket_projected",
        "care_insurance_act_not_promoted_from_source_level_currentness",
        "unsupported_or_unselected_cells_fail_closed",
    ):
        if safety.get(key) is not True:
            fail(f"missing safety invariant: {key}")

    print(f"high-value currentness expansion: PASS ({len(EXPECTED_IDS)} bounded Unit Price promotions; Care Act held)")


if __name__ == "__main__":
    main()
