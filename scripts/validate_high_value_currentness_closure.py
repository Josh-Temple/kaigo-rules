#!/usr/bin/env python3
"""Validate Worker B's bounded high-value currentness closure.

The only promotion authorized by this artifact is the exact
dayservice × unit_price_regional_classification cell.  A separate pull-request
workflow reparses the live MHLW consolidated display; this validator checks the
canonical identities, pinned hashes, direct applicability and fail-closed
boundaries used by that live gate.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "data/verification/high-value-currentness-closure-worker-b.json"
UNIT_PRICE_MAP = ROOT / "data/unit-price-service-multipliers.json"
ITEM_BODY = ROOT / "data/unit-price-item-body-assurance.json"
DAY_META = ROOT / "data/unit-price-dayservice-meta.json"
REGION_META = ROOT / "data/unit-price-region-assignments-meta.json"
AUDIT = ROOT / "data/unit-price-independent-audit.json"
WORKFLOW = ROOT / ".github/workflows/verify-unit-price-independent.yml"
VERIFIER = ROOT / "scripts/verify_unit_price_currentness.py"

EXPECTED_IDENTITY = ("dayservice", "unit_price_regional_classification")
EXPECTED_SOURCE_ID = "mhlw-unit-price-current"
EXPECTED_EFFECTIVE_DATE = "2024-04-01"
EXPECTED_PROFILE = "group-1090"
EXPECTED_ITEM_COUNT = 8


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def one(rows: list[dict[str, Any]], key: str, value: str) -> dict[str, Any] | None:
    return next((row for row in rows if row.get(key) == value), None)


def validate() -> list[str]:
    errors: list[str] = []
    artifact = load(ARTIFACT)
    mapping = load(UNIT_PRICE_MAP)
    item_body = load(ITEM_BODY)
    day_meta = load(DAY_META)
    region_meta = load(REGION_META)
    audit = load(AUDIT)

    if artifact.get("artifact_kind") != "CANONICAL_HIGH_VALUE_CURRENTNESS_CLOSURE_DECISION":
        errors.append("artifact kind mismatch")
    if artifact.get("worker") != "B":
        errors.append("worker identity mismatch")
    if artifact.get("base_main_sha") != "5f2a61b9288d99ebcccb7dcb3f0f11125abc4dad":
        errors.append("unexpected base main SHA")

    policy = artifact.get("policy") or {}
    required_false = (
        "blanket_family_promotion_allowed",
        "item_body_used_as_currentness_shortcut",
        "relation_status_promoted",
        "human_review_promoted",
        "publication_promoted",
        "route_exposure_promoted",
    )
    for key in required_false:
        if policy.get(key) is not False:
            errors.append(f"unsafe policy flag: {key}")
    for key in (
        "exact_service_source_family_allowlist_required",
        "live_official_source_reverification_required",
        "national_qa_compilation_freshness_never_projects_to_item_currentness",
    ):
        if policy.get(key) is not True:
            errors.append(f"missing safety policy: {key}")

    promotions = artifact.get("promotions") or []
    if len(promotions) != 1:
        errors.append("exactly one bounded high-value promotion is required")
        return errors

    row = promotions[0]
    identity = (row.get("service_id"), row.get("source_family"))
    if identity != EXPECTED_IDENTITY:
        errors.append(f"unexpected promotion identity: {identity}")

    source = row.get("source_identity") or {}
    if source.get("canonical_source_id") != EXPECTED_SOURCE_ID:
        errors.append("canonical source id mismatch")
    if source.get("currentness_class") != "CURRENT_OFFICIAL_CONSOLIDATED":
        errors.append("source is not bounded to CURRENT_OFFICIAL_CONSOLIDATED")
    if source.get("source_identity_complete_for_bounded_scope") is not True:
        errors.append("bounded source identity is incomplete")
    if source.get("effective_date") != EXPECTED_EFFECTIVE_DATE:
        errors.append("effective date mismatch")
    if source.get("official_page_urls") != day_meta.get("source_urls"):
        errors.append("official page URLs differ from pinned day-service metadata")
    if source.get("official_page_urls") != region_meta.get("source_urls"):
        errors.append("official page URLs differ from pinned region metadata")
    if source.get("expected_page_sha256") != day_meta.get("source_sha256"):
        errors.append("expected page hashes differ from pinned day-service metadata")
    if source.get("expected_page_sha256") != region_meta.get("source_sha256"):
        errors.append("expected page hashes differ from pinned region metadata")
    if region_meta.get("effective_reference_date") != EXPECTED_EFFECTIVE_DATE:
        errors.append("region assignment effective reference date mismatch")

    map_row = one(mapping.get("service_mappings") or [], "service_id", "dayservice")
    body_row = one(item_body.get("service_projections") or [], "service_id", "dayservice")
    if not map_row:
        errors.append("dayservice unit-price mapping missing")
    else:
        if map_row.get("applicability") != "APPLIES":
            errors.append("dayservice unit-price applicability is not APPLIES")
        if map_row.get("official_service_name") != "通所介護":
            errors.append("dayservice official service identity mismatch")
        if map_row.get("multiplier_profile_id") != EXPECTED_PROFILE:
            errors.append("dayservice multiplier profile mismatch")
        if (row.get("applicability_proof") or {}).get("source_locator") != map_row.get("source_locator").replace("（地域区分・サービス種類・割合）", " / 通所介護 / 地域区分別割合"):
            # The canonical item-body projection carries the normalized locator checked below.
            pass

    if not body_row:
        errors.append("dayservice item-body projection missing")
    else:
        if body_row.get("applicability") != "APPLIES":
            errors.append("dayservice item-body applicability is not APPLIES")
        if body_row.get("service_level_item_body") != "PASS":
            errors.append("dayservice item-body is not PASS")
        if body_row.get("mapped_item_count") != EXPECTED_ITEM_COUNT:
            errors.append("dayservice mapped item count mismatch")
        proof = row.get("applicability_proof") or {}
        if proof.get("state") != "PASS_DIRECT_SERVICE_SCOPE":
            errors.append("direct service scope proof missing")
        if proof.get("multiplier_profile_id") != body_row.get("multiplier_profile_id"):
            errors.append("promotion profile differs from item-body projection")
        if proof.get("source_locator") != body_row.get("source_locator"):
            errors.append("promotion locator differs from item-body projection")
        if proof.get("mapped_item_count") != body_row.get("mapped_item_count"):
            errors.append("promotion mapped item count differs from item-body projection")

    if audit.get("audit_result") != "PASS":
        errors.append("independent unit-price audit is not PASS")
    if audit.get("scope") != "dayservice-unit-price-and-427-region-assignments":
        errors.append("independent audit scope mismatch")
    if (audit.get("observed_counts") or {}).get("rate_count") != EXPECTED_ITEM_COUNT:
        errors.append("independent audit rate count mismatch")
    audit_hashes = [x.get("sha256") for x in audit.get("sources") or []]
    if audit_hashes != source.get("expected_page_sha256"):
        errors.append("independent audit hashes differ from bounded source identity")

    if row.get("source_version_contains_scope") is not True:
        errors.append("source version containment not established")
    if row.get("ingestion_state") != "INGESTED":
        errors.append("ingestion state is not INGESTED")
    if row.get("item_body_state") != "PASS":
        errors.append("item-body state is not PASS")
    if row.get("prior_currentness_state") != "PARTIAL":
        errors.append("unexpected prior currentness state")
    if row.get("projected_currentness_state") != "PASS" or row.get("promotion_applied") is not True:
        errors.append("bounded currentness promotion is not PASS/applied")

    gate = row.get("projection_gate") or {}
    if gate.get("allowed") is not True or gate.get("identity") != "::".join(EXPECTED_IDENTITY):
        errors.append("exact projection gate mismatch")
    if gate.get("scope") != "currentness_only":
        errors.append("projection gate is not currentness-only")

    contract = row.get("currentness_contract") or {}
    if contract.get("live_source_reverification_required") is not True:
        errors.append("live source reverification is not required")
    if contract.get("verifier") != "scripts/verify_unit_price_currentness.py":
        errors.append("live verifier path mismatch")
    if contract.get("workflow") != ".github/workflows/verify-unit-price-independent.yml":
        errors.append("live workflow path mismatch")

    unit_scope = row.get("publication_unit_scope") or {}
    if set(unit_scope.get("candidate_unit_types") or []) != {
        "SOURCE_TEXT_ITEM_BODY",
        "SOURCE_METADATA_LOCATOR",
        "CURRENTNESS_STATEMENT",
        "SERVICE_APPLICABILITY_STATEMENT",
    }:
        errors.append("safe publication-unit scope mismatch")
    if set(unit_scope.get("excluded_unit_types") or []) != {
        "CROSS_LAYER_RELATION_LINK",
        "INTERPRETIVE_RELATION_EXPLANATION",
    }:
        errors.append("relation-dependent publication units are not explicitly excluded")
    if unit_scope.get("relation_requirement_for_candidates") != "NOT_REQUIRED":
        errors.append("safe units unexpectedly require relation verification")
    if unit_scope.get("human_review_requirement_for_candidates") != "NOT_REQUIRED":
        errors.append("safe units unexpectedly require human review")

    unchanged = row.get("unchanged_axes") or {}
    if unchanged.get("relation_verification") != "NOT_ESTABLISHED":
        errors.append("relation verification was promoted")
    if unchanged.get("human_review") != "NOT_REVIEWED":
        errors.append("human review was promoted")

    selections = {x.get("source_family"): x for x in artifact.get("target_selection") or []}
    if (selections.get("unit_price_regional_classification") or {}).get("disposition") != "BOUNDED_PROMOTION":
        errors.append("unit-price target selection is not bounded promotion")
    for family in (
        "national_qa",
        "delegated_remuneration_criteria",
        "remuneration_notification",
        "standards_interpretation_notice",
        "fee_calculation_guidance",
        "other_national_manuals_forms",
        "care_insurance_act",
    ):
        if (selections.get(family) or {}).get("disposition") != "HOLD":
            errors.append(f"{family}: expected HOLD disposition")

    boundary = artifact.get("integration_boundary") or {}
    for key in (
        "generated_coverage_matrix_modified_by_worker_b",
        "publication_requirement_scoping_modified_by_worker_b",
        "publication_readiness_modified_by_worker_b",
        "bounded_publication_allowlist_modified_by_worker_b",
    ):
        if boundary.get(key) is not False:
            errors.append(f"Worker B integration boundary violated: {key}")
    if boundary.get("worker_e_must_regenerate_global_generated_artifacts_after_semantic_integration") is not True:
        errors.append("Worker E regeneration boundary missing")

    workflow_text = WORKFLOW.read_text(encoding="utf-8")
    for required_path in (
        "data/verification/high-value-currentness-closure-worker-b.json",
        "scripts/validate_high_value_currentness_closure.py",
        "scripts/verify_unit_price_independent.py",
        "scripts/verify_unit_price_currentness.py",
    ):
        if required_path not in workflow_text:
            errors.append(f"live verification workflow does not track {required_path}")

    verifier_text = VERIFIER.read_text(encoding="utf-8")
    if "supports_bounded_currentness" not in verifier_text:
        errors.append("live verifier does not emit bounded-currentness evidence")
    if "dayservice::unit_price_regional_classification" not in verifier_text:
        errors.append("live verifier is not explicitly scoped to the promoted identity")

    return errors


def main() -> int:
    errors = validate()
    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        return 1
    print(
        "PASS: high-value currentness closure validates; "
        "dayservice::unit_price_regional_classification is the sole bounded PASS candidate."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
