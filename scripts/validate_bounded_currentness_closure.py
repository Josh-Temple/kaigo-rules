#!/usr/bin/env python3
"""Validate Worker B bounded service-level currentness closure.

This validator keeps currentness independent from item-body, relation verification,
human review, publication, and route exposure. It accepts only exact service x
source-family identities whose current source and service applicability are
independently established.
"""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "data/verification/bounded-currentness-closure-worker-b.json"
ACTIVATION = ROOT / "data/verification/shared-source-currentness-activation.json"
AUDIT = ROOT / "data/verification/existing-ordinance37-service-slices-independent-audit.json"
MATRIX = ROOT / "data/database-coverage-matrix.generated.json"

PASS_ELIGIBLE_SOURCE_CLASSES = {
    "CURRENT_OFFICIAL_CONSOLIDATED",
    "CURRENT_OFFICIAL_VERSIONED",
}


def load(path: Path | str) -> dict[str, Any]:
    p = Path(path)
    if not p.is_absolute():
        p = ROOT / p
    return json.loads(p.read_text(encoding="utf-8"))


def evaluate_projection(
    *,
    source_family: str,
    source_class: str,
    source_identity_complete: bool,
    applicability_verified: bool,
    canonical_scope_identified: bool,
    source_version_contains_scope: bool,
    ingestion_state: str,
    explicit_gate: bool,
) -> bool:
    if source_family == "national_qa":
        return False
    if ingestion_state == "NOT_APPLICABLE":
        return False
    return all(
        (
            source_class in PASS_ELIGIBLE_SOURCE_CLASSES,
            source_identity_complete,
            applicability_verified,
            canonical_scope_identified,
            source_version_contains_scope,
            ingestion_state in {"INGESTED", "PARTIAL"},
            explicit_gate,
        )
    )


def family_rows(matrix: dict[str, Any], family: str) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for service in matrix.get("services", []):
        cell = next(
            row
            for row in service.get("source_families", [])
            if row.get("source_family") == family
        )
        result[service["service_id"]] = cell
    return result


def state_counts(rows: dict[str, dict[str, Any]]) -> dict[str, int]:
    return dict(
        Counter(
            str((row.get("currentness") or {}).get("state") or "NOT_ESTABLISHED")
            for row in rows.values()
        )
    )


def validate_payload(
    artifact: dict[str, Any],
    activation: dict[str, Any],
    audit: dict[str, Any],
    matrix: dict[str, Any],
) -> list[str]:
    errors: list[str] = []

    if artifact.get("artifact_kind") != "CANONICAL_BOUNDED_CURRENTNESS_CLOSURE_DECISION":
        errors.append("artifact kind mismatch")
    if artifact.get("worker") != "B":
        errors.append("worker identity mismatch")

    policy = artifact.get("policy") or {}
    for key in (
        "blanket_family_promotion_allowed",
        "relation_status_promoted",
        "human_review_promoted",
        "publication_promoted",
        "route_exposure_promoted",
    ):
        if policy.get(key) is not False:
            errors.append(f"unsafe policy flag: {key}")
    for key in (
        "national_qa_compilation_freshness_never_projects_to_item_currentness",
        "comparison_amendment_historical_only_never_pass",
        "not_applicable_never_promoted",
    ):
        if policy.get(key) is not True:
            errors.append(f"missing fail-closed policy: {key}")

    source_family = (activation.get("source_families") or {}).get(
        "governing_standards_ordinance"
    ) or {}
    source = next(
        (
            row
            for row in source_family.get("sources", [])
            if row.get("canonical_source_id") == "ordinance37"
        ),
        None,
    )
    if source is None:
        errors.append("ordinance37 current source identity missing from activation inventory")
        source = {}

    if source_family.get("currentness_class") not in PASS_ELIGIBLE_SOURCE_CLASSES:
        errors.append("ordinance37 family is not PASS-eligible current source class")
    if source_family.get("source_identity_complete") is not True:
        errors.append("ordinance37 source identity is incomplete")

    audit_source = audit.get("source") or {}
    if audit.get("audit_result") != "PASS":
        errors.append("committed independent ordinance37 service-slice audit is not PASS")
    if audit_source.get("current_revision_id") != source.get("version_id"):
        errors.append("independent audit revision does not match current source version")
    if audit_source.get("observed_xml_sha256") != (source.get("fingerprint") or {}).get("xml_sha256"):
        errors.append("independent audit source fingerprint does not match activation inventory")
    if audit_source.get("committed_xml_sha256") != audit_source.get("observed_xml_sha256"):
        errors.append("independent audit observed and committed ordinance37 fingerprints differ")

    audit_services = {
        row["service_id"]: row
        for row in audit.get("services", [])
        if row.get("result") == "PASS"
    }
    expected_promoted_ids = set(audit_services)

    standards_matrix = family_rows(matrix, "governing_standards_ordinance")
    care_matrix = family_rows(matrix, "care_insurance_act")
    before_standards = state_counts(standards_matrix)
    before_care = state_counts(care_matrix)

    priority = artifact.get("priority_1") or {}
    care = priority.get("care_insurance_act") or {}
    standards = priority.get("governing_standards_ordinance") or {}

    if care.get("before") != before_care or care.get("after") != before_care:
        errors.append("Care Act before/after counts must remain unchanged")
    if care.get("promotions") != 0 or care.get("disposition") != "HOLD":
        errors.append("Care Act must remain held without independent applicability proof")
    if set(care.get("blocked_service_ids") or []) != set(care_matrix):
        errors.append("Care Act blocked service inventory must cover all services")

    promotions = artifact.get("promotions") or []
    by_identity = {
        (row.get("service_id"), row.get("source_family")): row for row in promotions
    }
    if len(by_identity) != len(promotions):
        errors.append("duplicate promotion identity")
    promoted_ids = {
        row.get("service_id")
        for row in promotions
        if row.get("source_family") == "governing_standards_ordinance"
    }
    if promoted_ids != expected_promoted_ids:
        errors.append(
            "bounded governing-standards promotion set differs from independently audited services"
        )
    if standards.get("promotions") != len(expected_promoted_ids):
        errors.append("governing standards promotion count mismatch")
    if set(standards.get("promoted_service_ids") or []) != expected_promoted_ids:
        errors.append("governing standards promoted service list mismatch")
    if set(standards.get("remaining_blocked_service_ids") or []) != (
        set(standards_matrix) - expected_promoted_ids
    ):
        errors.append("governing standards remaining blocked set mismatch")
    matrix_preintegration = before_standards == standards.get("before")
    matrix_integrated = before_standards == standards.get("after")
    if not matrix_preintegration and not matrix_integrated:
        errors.append(
            "governing standards matrix counts match neither the recorded pre-integration nor integrated state"
        )

    expected_after = dict(standards.get("before") or {})
    for row in promotions:
        if row.get("source_family") != "governing_standards_ordinance":
            continue
        prior = str(row.get("prior_currentness_state") or "NOT_ESTABLISHED")
        expected_after[prior] = expected_after.get(prior, 0) - 1
        expected_after["PASS"] = expected_after.get("PASS", 0) + 1
    expected_after = {k: v for k, v in expected_after.items() if v}
    if standards.get("after") != expected_after:
        errors.append(
            f"governing standards after counts mismatch: recorded={standards.get('after')} expected={expected_after}"
        )

    for service_id in sorted(expected_promoted_ids):
        row = by_identity.get((service_id, "governing_standards_ordinance"))
        if row is None:
            continue
        audit_row = audit_services[service_id]
        matrix_row = standards_matrix[service_id]
        proof = row.get("applicability_proof") or {}
        gate = row.get("projection_gate") or {}
        identity = row.get("source_identity") or {}

        if identity.get("canonical_source_id") != "ordinance37":
            errors.append(f"{service_id}: wrong source identity")
        if identity.get("version_id") != source.get("version_id"):
            errors.append(f"{service_id}: version id drift")
        if identity.get("effective_date") != source.get("effective_date"):
            errors.append(f"{service_id}: effective date drift")
        if (identity.get("fingerprint") or {}).get("xml_sha256") != (
            source.get("fingerprint") or {}
        ).get("xml_sha256"):
            errors.append(f"{service_id}: source fingerprint drift")

        if proof.get("state") != "PASS_DIRECT_SERVICE_CHAPTER":
            errors.append(f"{service_id}: applicability proof state is not bounded PASS")
        if proof.get("direct_service_chapter_verified") is not True:
            errors.append(f"{service_id}: direct service chapter not independently verified")
        if proof.get("target_articles") != audit_row.get("target_articles"):
            errors.append(f"{service_id}: target article set differs from independent audit")
        if proof.get("discrepancies") != 0 or audit_row.get("differences"):
            errors.append(f"{service_id}: independent applicability/body discrepancies remain")
        for evidence in proof.get("evidence") or []:
            if evidence.startswith("data/services/") and not (ROOT / evidence).exists():
                errors.append(f"{service_id}: scope evidence missing: {evidence}")

        if row.get("source_version_contains_scope") is not True:
            errors.append(f"{service_id}: source-version scope containment not established")
        if row.get("ingestion_state") != (matrix_row.get("ingestion") or {}).get("state"):
            errors.append(f"{service_id}: ingestion state drift")
        if row.get("item_body_state") != (matrix_row.get("item_body_verification") or {}).get("state"):
            errors.append(f"{service_id}: item-body state drift")
        matrix_currentness = matrix_row.get("currentness") or {}
        if matrix_preintegration:
            if row.get("prior_currentness_state") != matrix_currentness.get("state"):
                errors.append(f"{service_id}: prior currentness drift")
        elif matrix_integrated:
            if matrix_currentness.get("state") != row.get("projected_currentness_state"):
                errors.append(f"{service_id}: integrated currentness projection drift")
            if "PASS_BOUNDED_VERIFIED" not in (matrix_currentness.get("raw_status") or []):
                errors.append(f"{service_id}: integrated bounded currentness marker missing")
            expected_pointer = (
                f"data/verification/bounded-currentness-closure-worker-b.json#"
                f"{service_id}::governing_standards_ordinance"
            )
            if expected_pointer not in (matrix_currentness.get("evidence") or []):
                errors.append(f"{service_id}: integrated bounded currentness evidence pointer missing")
        if row.get("projected_currentness_state") != "PASS" or row.get("promotion_applied") is not True:
            errors.append(f"{service_id}: bounded promotion decision missing")

        eligible = evaluate_projection(
            source_family="governing_standards_ordinance",
            source_class=str(source_family.get("currentness_class")),
            source_identity_complete=bool(source_family.get("source_identity_complete")),
            applicability_verified=proof.get("state") == "PASS_DIRECT_SERVICE_CHAPTER",
            canonical_scope_identified=bool(proof.get("target_articles")),
            source_version_contains_scope=bool(row.get("source_version_contains_scope")),
            ingestion_state=str(row.get("ingestion_state")),
            explicit_gate=gate.get("allowed") is True
            and gate.get("kind") == "EXPLICIT_BOUNDED_ALLOWLIST",
        )
        if not eligible:
            errors.append(f"{service_id}: promotion does not satisfy bounded projection prerequisites")

        unchanged = row.get("unchanged_axes") or {}
        if unchanged.get("relation_verification") != (
            matrix_row.get("relation_verification") or {}
        ).get("state"):
            errors.append(f"{service_id}: relation verification was altered")
        if unchanged.get("human_review") != (matrix_row.get("human_review") or {}).get("state"):
            errors.append(f"{service_id}: human review was altered")
        if unchanged.get("publication") != (matrix_row.get("publication") or {}).get("state"):
            errors.append(f"{service_id}: publication was altered")
        if unchanged.get("route_exposure") != (matrix_row.get("route_exposure") or {}).get("state"):
            errors.append(f"{service_id}: route exposure was altered")

        provenance = row.get("projection_provenance") or {}
        for key in (
            "source_level_evidence",
            "applicability_evidence",
            "projection_rule",
            "projection_timestamp",
            "validator",
            "live_reverification_workflow",
        ):
            if not provenance.get(key):
                errors.append(f"{service_id}: missing projection provenance {key}")

    holds = artifact.get("holds") or {}
    if holds.get("national_qa", {}).get("disposition") != "HOLD":
        errors.append("National Q&A must remain held")
    if "compilation" not in str(holds.get("national_qa", {}).get("reason", "")).lower():
        errors.append("National Q&A hold must preserve compilation/currentness separation")

    boundary = artifact.get("integration_boundary") or {}
    if boundary.get("generated_coverage_matrix_modified_by_worker_b") is not False:
        errors.append("Worker B must not claim global generated Coverage Matrix modification")
    if boundary.get("publication_readiness_modified_by_worker_b") is not False:
        errors.append("Worker B must not modify publication readiness")
    if boundary.get("worker_e_must_regenerate_global_generated_artifacts_after_semantic_integration") is not True:
        errors.append("Worker E regeneration boundary missing")

    safety = artifact.get("safety") or {}
    if safety.get("promotions_are_exact_identity_allowlisted") is not True:
        errors.append("exact-identity allowlist safety missing")
    for key in (
        "source_identity_to_service_blanket_projection",
        "item_body_used_as_currentness_shortcut",
        "relation_verification_changed",
        "human_review_changed",
        "publication_changed",
        "route_exposure_changed",
    ):
        if safety.get(key) is not False:
            errors.append(f"safety boundary broken: {key}")

    return errors


def validate() -> list[str]:
    return validate_payload(load(ARTIFACT), load(ACTIVATION), load(AUDIT), load(MATRIX))


def main() -> int:
    errors = validate()
    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        return 1
    artifact = load(ARTIFACT)
    promoted = len(artifact.get("promotions") or [])
    print(
        f"PASS: Worker B bounded currentness closure validates; {promoted} exact "
        "governing-standards service cells are eligible for PASS and Care Act remains held."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
