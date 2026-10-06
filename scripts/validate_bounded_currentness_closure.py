#!/usr/bin/env python3
"""Validate cumulative bounded service-level currentness closure.

Worker B may promote currentness only for exact service x source-family identities
where current official source identity, service applicability, canonical scope,
source-version containment, ingestion, item-body assurance, and an explicit gate
are independently established. Relation semantics, human review, publication,
and route exposure remain separate axes.
"""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "data/verification/bounded-currentness-closure-worker-b.json"
ACTIVATION = ROOT / "data/verification/shared-source-currentness-activation.json"
ORD37_AUDIT = ROOT / "data/verification/existing-ordinance37-service-slices-independent-audit.json"
SHARED_AUDIT = ROOT / "data/shared/standards/independent-audit.json"
MATRIX = ROOT / "data/database-coverage-matrix.generated.json"
PREVENTIVE_NODES = ROOT / "data/shared/standards/preventive-services-standards/nodes.json"

PASS_ELIGIBLE_SOURCE_CLASSES = {
    "CURRENT_OFFICIAL_CONSOLIDATED",
    "CURRENT_OFFICIAL_VERSIONED",
}

PREVENTIVE_SCOPE_PATHS = {
    "preventive-homebath": "data/services/preventive-homebath/standards-scope.json",
    "preventive-homenursing": "data/services/preventive-homenursing/standards-scope.json",
    "preventive-homerehab": "data/services/preventive-homerehab/standards-scope.json",
    "preventive-homecaremanagement": "data/services/preventive-homecaremanagement/standards-scope.json",
    "preventive-dayrehab": "data/services/preventive-dayrehab/standards-scope.json",
    "preventive-shortstay-life": "data/services/preventive-shortstay-life/standards-scope.json",
    "preventive-shortstay-medical": "data/services/preventive-shortstay-medical/standards-scope.json",
    "preventive-specific-facility": "data/services/preventive-specific-facility/standards-scope.json",
    "preventive-welfare-equipment-rental": "data/services/preventive-welfare-equipment-rental/standards-scope.json",
    "specific-preventive-welfare-equipment-sale": "data/services/specific-preventive-welfare-equipment-sale/standards-scope.json",
}


def load(path: Path | str) -> dict[str, Any] | list[Any]:
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
    item_body_state: str = "PASS",
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
            item_body_state == "PASS",
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


def source_by_id(activation: dict[str, Any], canonical_source_id: str) -> tuple[dict[str, Any], dict[str, Any]]:
    family = (activation.get("source_families") or {}).get("governing_standards_ordinance") or {}
    source = next(
        (row for row in family.get("sources", []) if row.get("canonical_source_id") == canonical_source_id),
        None,
    )
    if source is None:
        raise KeyError(canonical_source_id)
    return family, source


def _article_order(nodes: list[dict[str, Any]]) -> tuple[list[str], dict[str, dict[str, Any]]]:
    articles = [row for row in nodes if row.get("node_type") == "article"]
    by_id = {str(row.get("id")): row for row in articles}
    return [str(row.get("id")) for row in articles], by_id


def _resolve_range(
    order: list[str],
    by_id: dict[str, dict[str, Any]],
    start: str | None,
    end: str | None,
) -> list[dict[str, Any]]:
    if not start or not end or start not in by_id or end not in by_id:
        return []
    positions = {node_id: i for i, node_id in enumerate(order)}
    if positions[start] > positions[end]:
        return []
    return [by_id[node_id] for node_id in order[positions[start] : positions[end] + 1]]


def validate_preventive_scope(
    service_id: str,
    scope_path: str,
    nodes: list[dict[str, Any]],
) -> tuple[list[str], dict[str, Any]]:
    errors: list[str] = []
    scope = load(scope_path)
    assert isinstance(scope, dict)
    order, by_id = _article_order(nodes)

    if scope.get("service_id") != service_id:
        errors.append(f"{service_id}: scope service identity mismatch")
    if scope.get("status") != "SCOPE_DEFINED_APPLICABILITY_NOT_VERIFIED":
        errors.append(f"{service_id}: unexpected scope status")

    corpus = scope.get("source_corpus") or {}
    if corpus.get("corpus_id") != "preventive-services-standards":
        errors.append(f"{service_id}: preventive standards corpus mismatch")
    if corpus.get("law_id") != "418M60000100035":
        errors.append(f"{service_id}: preventive standards law identity mismatch")

    common = scope.get("common_scope") or {}
    common_ids = common.get("source_node_ids") or []
    if common.get("relation") != "direct_applicability_candidate" or not common_ids:
        errors.append(f"{service_id}: common direct scope missing")
    for node_id in common_ids:
        if node_id not in by_id:
            errors.append(f"{service_id}: common scope node missing from current corpus: {node_id}")

    primary = scope.get("primary_scope") or {}
    if primary.get("relation") != "direct_applicability_candidate":
        errors.append(f"{service_id}: primary direct scope missing")
    primary_rows = _resolve_range(
        order,
        by_id,
        primary.get("from_node_id"),
        primary.get("through_node_id"),
    )
    if not primary_rows:
        errors.append(f"{service_id}: primary scope range does not resolve in current corpus")

    service_name = str(scope.get("service_name") or "")
    primary_path_text = " ".join(
        " ".join(str(x) for x in (row.get("path") or []))
        for row in primary_rows
    )
    if not service_name or service_name not in primary_path_text:
        errors.append(
            f"{service_id}: primary current-corpus chapter does not identify the declared service"
        )

    variant_summaries = []
    for variant in scope.get("service_variants") or []:
        relation = variant.get("relation")
        if relation not in {"separate_variant_scope", "direct_applicability", "direct_applicability_candidate"}:
            errors.append(f"{service_id}: unsupported direct variant relation: {relation}")
            continue
        rows = _resolve_range(
            order,
            by_id,
            variant.get("from_node_id"),
            variant.get("through_node_id"),
        )
        if not rows:
            errors.append(f"{service_id}: variant scope range does not resolve in current corpus")
            continue
        variant_summaries.append(
            {
                "applicability_kind": variant.get("applicability_kind"),
                "from_node_id": variant.get("from_node_id"),
                "through_node_id": variant.get("through_node_id"),
                "article_count": len(rows),
            }
        )

    wrappers = scope.get("incorporation_wrappers") or []
    for wrapper in wrappers:
        node_id = wrapper.get("node_id")
        if node_id not in by_id:
            errors.append(f"{service_id}: incorporation wrapper missing from current corpus: {node_id}")
        if wrapper.get("target_resolution_state") != "NOT_EXPANDED_FAIL_CLOSED":
            errors.append(f"{service_id}: incorporation wrapper target is not fail-closed")
        if wrapper.get("substitution_resolution_state") != "NOT_EXPANDED_FAIL_CLOSED":
            errors.append(f"{service_id}: incorporation wrapper substitution is not fail-closed")

    summary = {
        "common_source_node_ids": common_ids,
        "primary_range": {
            "from_node_id": primary.get("from_node_id"),
            "through_node_id": primary.get("through_node_id"),
            "article_count": len(primary_rows),
        },
        "variant_ranges": variant_summaries,
        "incorporation_wrapper_count": len(wrappers),
    }
    return errors, summary


def validate_payload(
    artifact: dict[str, Any],
    activation: dict[str, Any],
    ord37_audit: dict[str, Any],
    shared_audit: dict[str, Any],
    matrix: dict[str, Any],
    preventive_nodes: list[dict[str, Any]],
) -> list[str]:
    errors: list[str] = []

    if artifact.get("artifact_kind") != "CANONICAL_BOUNDED_CURRENTNESS_CLOSURE_DECISION":
        errors.append("artifact kind mismatch")
    if artifact.get("worker") != "B":
        errors.append("worker identity mismatch")
    if artifact.get("format_version") != 2:
        errors.append("expected bounded currentness artifact format_version 2")

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

    standards_matrix = family_rows(matrix, "governing_standards_ordinance")
    care_matrix = family_rows(matrix, "care_insurance_act")
    current_standards = state_counts(standards_matrix)
    current_care = state_counts(care_matrix)

    priority = artifact.get("priority_1") or {}
    care = priority.get("care_insurance_act") or {}
    standards = priority.get("governing_standards_ordinance") or {}

    if care.get("before") != current_care or care.get("after") != current_care:
        errors.append("Care Act before/after counts must remain unchanged")
    if care.get("promotions") != 0 or care.get("disposition") != "HOLD":
        errors.append("Care Act must remain held without independent applicability proof")

    promotions = artifact.get("promotions") or []
    by_identity = {
        (row.get("service_id"), row.get("source_family")): row for row in promotions
    }
    if len(by_identity) != len(promotions):
        errors.append("duplicate promotion identity")
    if any(row.get("source_family") != "governing_standards_ordinance" for row in promotions):
        errors.append("unexpected source family in bounded promotion inventory")

    old_ids = {
        row["service_id"]
        for row in ord37_audit.get("services", [])
        if row.get("result") == "PASS"
    }
    preventive_ids = set(PREVENTIVE_SCOPE_PATHS)
    residual_new_ids = {"dayservice", "dayrehab"}
    baseline_ids = old_ids | preventive_ids
    expected_ids = baseline_ids | residual_new_ids
    promoted_ids = {str(row.get("service_id")) for row in promotions}
    if promoted_ids != expected_ids:
        errors.append("cumulative bounded promotion set differs from the exact audited/validated set")
    if standards.get("cumulative_promotions") != len(expected_ids):
        errors.append("cumulative promotion count mismatch")
    if standards.get("new_promotions_this_wave") != len(residual_new_ids):
        errors.append("new promotion count mismatch")
    if set(standards.get("newly_promoted_service_ids") or []) != residual_new_ids:
        errors.append("new promotion service inventory mismatch")
    if set(standards.get("promoted_service_ids") or []) != expected_ids:
        errors.append("cumulative promoted service inventory mismatch")
    if set(standards.get("remaining_blocked_service_ids") or []) != set(standards_matrix) - expected_ids:
        errors.append("remaining governing-standards blocked inventory mismatch")

    matrix_preintegration = current_standards == standards.get("before")
    matrix_integrated = current_standards == standards.get("after")
    if not matrix_preintegration and not matrix_integrated:
        errors.append("governing standards matrix matches neither wave before nor after state")

    expected_after = dict(standards.get("before") or {})
    for service_id in residual_new_ids:
        row = by_identity.get((service_id, "governing_standards_ordinance")) or {}
        prior = str(row.get("prior_currentness_state") or "NOT_ESTABLISHED")
        expected_after[prior] = expected_after.get(prior, 0) - 1
        expected_after["PASS"] = expected_after.get("PASS", 0) + 1
    expected_after = {key: value for key, value in expected_after.items() if value}
    if standards.get("after") != expected_after:
        errors.append(
            f"governing standards after counts mismatch: recorded={standards.get('after')} expected={expected_after}"
        )

    try:
        standards_family, ord37_source = source_by_id(activation, "ordinance37")
        _, preventive_source = source_by_id(activation, "preventive-services-standards")
    except KeyError as exc:
        errors.append(f"current official standards source identity missing: {exc}")
        return errors

    if standards_family.get("currentness_class") not in PASS_ELIGIBLE_SOURCE_CLASSES:
        errors.append("governing standards family is not PASS-eligible current source class")
    if standards_family.get("source_identity_complete") is not True:
        errors.append("governing standards source identity inventory is incomplete")

    if ord37_audit.get("audit_result") != "PASS":
        errors.append("Ordinance 37 service-slice audit is not PASS")
    audit_source = ord37_audit.get("source") or {}
    if audit_source.get("current_revision_id") != ord37_source.get("version_id"):
        errors.append("Ordinance 37 audit revision does not match current source identity")
    if audit_source.get("observed_xml_sha256") != (ord37_source.get("fingerprint") or {}).get("xml_sha256"):
        errors.append("Ordinance 37 audit fingerprint does not match current source identity")

    shared_check = next(
        (row for row in shared_audit.get("checks", []) if row.get("id") == "preventive-services-standards"),
        None,
    )
    if not shared_check or shared_check.get("result") != "PASS":
        errors.append("preventive-services shared-corpus independent audit is not PASS")
    elif shared_check.get("observed_xml_sha256") != (preventive_source.get("fingerprint") or {}).get("xml_sha256"):
        errors.append("preventive-services audit fingerprint does not match current source identity")

    ord37_rows = {
        row["service_id"]: row
        for row in ord37_audit.get("services", [])
        if row.get("result") == "PASS"
    }
    for service_id in sorted(old_ids):
        row = by_identity.get((service_id, "governing_standards_ordinance"))
        if row is None:
            continue
        identity = row.get("source_identity") or {}
        proof = row.get("applicability_proof") or {}
        audit_row = ord37_rows[service_id]
        matrix_row = standards_matrix[service_id]

        if identity.get("canonical_source_id") != "ordinance37":
            errors.append(f"{service_id}: wrong Ordinance 37 source identity")
        if identity.get("version_id") != ord37_source.get("version_id"):
            errors.append(f"{service_id}: Ordinance 37 version drift")
        if (identity.get("fingerprint") or {}).get("xml_sha256") != (
            ord37_source.get("fingerprint") or {}
        ).get("xml_sha256"):
            errors.append(f"{service_id}: Ordinance 37 source fingerprint drift")
        if proof.get("state") != "PASS_DIRECT_SERVICE_CHAPTER":
            errors.append(f"{service_id}: direct service chapter proof missing")
        if proof.get("target_articles") != audit_row.get("target_articles"):
            errors.append(f"{service_id}: target articles differ from independent audit")
        if matrix_integrated and (matrix_row.get("currentness") or {}).get("state") != "PASS":
            errors.append(f"{service_id}: integrated currentness is not PASS")
        if matrix_preintegration and (matrix_row.get("currentness") or {}).get("state") != "PASS":
            errors.append(f"{service_id}: prior cumulative promotion disappeared from base matrix")

    for service_id in sorted(preventive_ids):
        row = by_identity.get((service_id, "governing_standards_ordinance"))
        if row is None:
            continue
        identity = row.get("source_identity") or {}
        proof = row.get("applicability_proof") or {}
        matrix_row = standards_matrix[service_id]
        scope_path = PREVENTIVE_SCOPE_PATHS[service_id]

        if identity.get("canonical_source_id") != "preventive-services-standards":
            errors.append(f"{service_id}: wrong preventive standards source identity")
        if identity.get("version_id") != preventive_source.get("version_id"):
            errors.append(f"{service_id}: preventive standards version drift")
        if identity.get("effective_date") != preventive_source.get("effective_date"):
            errors.append(f"{service_id}: preventive standards effective-date drift")
        if (identity.get("fingerprint") or {}).get("xml_sha256") != (
            preventive_source.get("fingerprint") or {}
        ).get("xml_sha256"):
            errors.append(f"{service_id}: preventive standards source fingerprint drift")
        if proof.get("state") != "PASS_DIRECT_SERVICE_SCOPE":
            errors.append(f"{service_id}: direct preventive service scope proof missing")
        scope_errors, resolved = validate_preventive_scope(service_id, scope_path, preventive_nodes)
        errors.extend(scope_errors)
        if proof.get("common_source_node_ids") != resolved.get("common_source_node_ids"):
            errors.append(f"{service_id}: common scope evidence drift")
        recorded_primary = proof.get("primary_range") or {}
        resolved_primary = resolved.get("primary_range") or {}
        for key in ("from_node_id", "through_node_id"):
            if recorded_primary.get(key) != resolved_primary.get(key):
                errors.append(f"{service_id}: primary scope {key} drift")
        recorded_variants = [
            (r.get("from_node_id"), r.get("through_node_id"))
            for r in proof.get("variant_ranges") or []
        ]
        resolved_variants = [
            (r.get("from_node_id"), r.get("through_node_id"))
            for r in resolved.get("variant_ranges") or []
        ]
        if recorded_variants != resolved_variants:
            errors.append(f"{service_id}: variant scope range drift")
        if proof.get("incorporation_wrappers_excluded_from_semantic_expansion") is not True:
            errors.append(f"{service_id}: unresolved incorporation semantics are not explicitly excluded")
        if row.get("source_version_contains_scope") is not True:
            errors.append(f"{service_id}: source-version scope containment not established")
        if row.get("ingestion_state") != "INGESTED" or row.get("item_body_state") != "PASS":
            errors.append(f"{service_id}: ingestion/item-body prerequisite not satisfied")
        if matrix_preintegration:
            if row.get("prior_currentness_state") != (matrix_row.get("currentness") or {}).get("state"):
                errors.append(f"{service_id}: recorded prior currentness does not match base matrix")
        elif (matrix_row.get("currentness") or {}).get("state") != "PASS":
            errors.append(f"{service_id}: integrated currentness is not PASS")

    egov_content_audit = load("data/egov-content-independent-audit.json")
    dayservice_scope = load("data/ordinance37-scope.json")
    dayrehab_scope = load("data/services/dayrehab/ordinance37-scope.json")
    dayrehab_audit = load("data/dayrehab-ordinance37-independent-audit.json")
    dayrehab_index = load("data/services/dayrehab/ordinance37-index.generated.json")
    verifier_text = (ROOT / "scripts/verify_existing_ordinance37_service_slices.py").read_text(encoding="utf-8")
    workflow_text = (ROOT / ".github/workflows/verify-existing-ordinance37-service-slices.yml").read_text(encoding="utf-8")

    egov_ord37 = next(
        (row for row in egov_content_audit.get("checks", []) if row.get("id") == "ordinance37"),
        None,
    )
    if not egov_ord37 or egov_ord37.get("result") != "PASS":
        errors.append("dayservice: shared Ordinance 37 independent content audit is not PASS")
    elif egov_ord37.get("observed_xml_sha256") != (ord37_source.get("fingerprint") or {}).get("xml_sha256"):
        errors.append("dayservice: shared Ordinance 37 audit fingerprint drift")

    residual_expected = {
        "dayservice": {
            "target_articles": [str(value) for value in dayservice_scope.get("direct_articles", [])],
            "chapter": str(dayservice_scope.get("service") or ""),
        },
        "dayrehab": {
            "target_articles": [str(value) for value in dayrehab_audit.get("target_articles", [])],
            "chapter": str((dayrehab_scope.get("chapter") or {}).get("title") or ""),
        },
    }
    if dayservice_scope.get("law_id") != ord37_source.get("law_id"):
        errors.append("dayservice: scope law identity differs from current source")
    if dayrehab_scope.get("law_id") != ord37_source.get("law_id"):
        errors.append("dayrehab: scope law identity differs from current source")
    if dayrehab_audit.get("audit_result") != "PASS":
        errors.append("dayrehab: independent service-slice audit is not PASS")
    dayrehab_source = dayrehab_audit.get("source") or {}
    if dayrehab_source.get("current_revision_id") != ord37_source.get("version_id"):
        errors.append("dayrehab: independent audit revision differs from current source")
    if dayrehab_source.get("observed_xml_sha256") != (ord37_source.get("fingerprint") or {}).get("xml_sha256"):
        errors.append("dayrehab: independent audit fingerprint differs from current source")
    if [str(value) for value in (dayrehab_scope.get("direct_scope") or {}).get("article_numbers", [])] != residual_expected["dayrehab"]["target_articles"]:
        errors.append("dayrehab: canonical direct scope differs from independent audit")
    index_source = dayrehab_index.get("source_corpus") or {}
    if index_source.get("current_revision_id") != ord37_source.get("version_id"):
        errors.append("dayrehab: generated index revision differs from current source")
    if index_source.get("xml_sha256") != (ord37_source.get("fingerprint") or {}).get("xml_sha256"):
        errors.append("dayrehab: generated index fingerprint differs from current source")
    if [str(value) for value in (dayrehab_index.get("selectors") or {}).get("resolved_direct_articles", [])] != residual_expected["dayrehab"]["target_articles"]:
        errors.append("dayrehab: generated direct article selector differs from canonical scope")

    for service_id in sorted(residual_new_ids):
        row = by_identity.get((service_id, "governing_standards_ordinance"))
        if row is None:
            continue
        identity = row.get("source_identity") or {}
        proof = row.get("applicability_proof") or {}
        matrix_row = standards_matrix[service_id]
        expected = residual_expected[service_id]
        if identity.get("canonical_source_id") != "ordinance37":
            errors.append(f"{service_id}: residual promotion must use Ordinance 37 identity")
        if identity.get("version_id") != ord37_source.get("version_id"):
            errors.append(f"{service_id}: residual promotion source version drift")
        if identity.get("effective_date") != ord37_source.get("effective_date"):
            errors.append(f"{service_id}: residual promotion effective-date drift")
        if (identity.get("fingerprint") or {}).get("xml_sha256") != (ord37_source.get("fingerprint") or {}).get("xml_sha256"):
            errors.append(f"{service_id}: residual promotion source fingerprint drift")
        if proof.get("state") != "PASS_DIRECT_SERVICE_CHAPTER":
            errors.append(f"{service_id}: direct service chapter proof missing")
        if [str(value) for value in proof.get("target_articles", [])] != expected["target_articles"]:
            errors.append(f"{service_id}: target articles differ from canonical direct scope")
        if proof.get("declared_chapter") != expected["chapter"]:
            errors.append(f"{service_id}: declared service chapter drift")
        if proof.get("incorporation_scope_excluded_from_semantic_expansion") is not True:
            errors.append(f"{service_id}: incorporated semantics are not explicitly excluded")
        if proof.get("live_service_slice_reverification_required") is not True:
            errors.append(f"{service_id}: live service-slice reverification gate missing")
        if row.get("source_version_contains_scope") is not True:
            errors.append(f"{service_id}: current source version containment not established")
        if row.get("ingestion_state") != "INGESTED" or row.get("item_body_state") != "PASS":
            errors.append(f"{service_id}: ingestion/item-body prerequisite not satisfied")
        if matrix_preintegration:
            if row.get("prior_currentness_state") != (matrix_row.get("currentness") or {}).get("state"):
                errors.append(f"{service_id}: recorded prior currentness differs from base matrix")
            if row.get("prior_currentness_state") != "PARTIAL":
                errors.append(f"{service_id}: residual promotion must originate from PARTIAL")
        elif (matrix_row.get("currentness") or {}).get("state") != "PASS":
            errors.append(f"{service_id}: integrated currentness is not PASS")
        tuple_literal = f'("{service_id}", "{matrix_row.get("service_label", "")}")'
        label = "通所介護" if service_id == "dayservice" else "通所リハビリテーション"
        if f'("{service_id}", "{label}")' not in verifier_text:
            errors.append(f"{service_id}: live e-Gov verifier target missing")
        if f'"{service_id}"' not in workflow_text:
            errors.append(f"{service_id}: live e-Gov workflow projection target missing")

    inventory = artifact.get("residual_target_inventory") or []
    inventory_by_id = {str(row.get("service_id")): row for row in inventory}
    residual_target_ids = set(standards_matrix) - baseline_ids
    if set(inventory_by_id) != residual_target_ids:
        errors.append("residual target inventory must cover the exact 19 non-baseline services")
    for service_id in residual_target_ids:
        entry = inventory_by_id.get(service_id) or {}
        if service_id in residual_new_ids:
            if entry.get("decision") != "PROMOTE_PASS_BOUNDED" or entry.get("blocker") is not None:
                errors.append(f"{service_id}: residual promotion inventory decision mismatch")
        else:
            if entry.get("decision") != "DEFER":
                errors.append(f"{service_id}: unverified residual service must remain deferred")
            if entry.get("blocker") != "NO_SERVICE_SPECIFIC_CURRENT_VERSION_APPLICABILITY_PROOF":
                errors.append(f"{service_id}: deferred blocker is not explicit")

    if standards.get("projected_ready_increase") != len(residual_new_ids):
        errors.append("projected READY increase must equal bounded residual promotions")

    for row in promotions:
        service_id = str(row.get("service_id"))
        gate = row.get("projection_gate") or {}
        proof = row.get("applicability_proof") or {}
        canonical_source_id = (row.get("source_identity") or {}).get("canonical_source_id")
        source_class = standards_family.get("currentness_class")
        eligible = evaluate_projection(
            source_family="governing_standards_ordinance",
            source_class=str(source_class),
            source_identity_complete=bool(standards_family.get("source_identity_complete")),
            applicability_verified=proof.get("state") in {
                "PASS_DIRECT_SERVICE_CHAPTER",
                "PASS_DIRECT_SERVICE_SCOPE",
            },
            canonical_scope_identified=bool(
                proof.get("target_articles")
                or proof.get("primary_range")
            ),
            source_version_contains_scope=bool(row.get("source_version_contains_scope")),
            ingestion_state=str(row.get("ingestion_state")),
            item_body_state=str(row.get("item_body_state")),
            explicit_gate=gate.get("allowed") is True
            and gate.get("kind") == "EXPLICIT_BOUNDED_ALLOWLIST",
        )
        if not eligible:
            errors.append(f"{service_id}: promotion does not satisfy bounded prerequisites")
        if row.get("projected_currentness_state") != "PASS" or row.get("promotion_applied") is not True:
            errors.append(f"{service_id}: bounded PASS decision missing")
        if gate.get("identity") != f"{service_id}::governing_standards_ordinance":
            errors.append(f"{service_id}: explicit gate identity mismatch")
        if canonical_source_id not in {"ordinance37", "preventive-services-standards"}:
            errors.append(f"{service_id}: source identity is outside bounded promotion set")
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

    holds = artifact.get("high_yield_holds") or {}
    for family_id in ("delegated_remuneration_criteria", "unit_price_regional_classification"):
        if (holds.get(family_id) or {}).get("disposition") != "HOLD":
            errors.append(f"{family_id}: unsafe high-yield currentness promotion")

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
    if safety.get("new_promotions_are_direct_scope_only") is not True:
        errors.append("direct-scope-only promotion safety missing")
    if safety.get("residual_promotions_require_live_service_slice_reverification") is not True:
        errors.append("live service-slice reverification safety missing")
    if safety.get("unverified_residual_services_deferred") is not True:
        errors.append("unverified residual deferral safety missing")
    if safety.get("unresolved_incorporation_semantics_excluded") is not True:
        errors.append("unresolved incorporation semantics exclusion missing")
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
    artifact = load(ARTIFACT)
    activation = load(ACTIVATION)
    ord37_audit = load(ORD37_AUDIT)
    shared_audit = load(SHARED_AUDIT)
    matrix = load(MATRIX)
    preventive_nodes = load(PREVENTIVE_NODES)
    assert isinstance(artifact, dict)
    assert isinstance(activation, dict)
    assert isinstance(ord37_audit, dict)
    assert isinstance(shared_audit, dict)
    assert isinstance(matrix, dict)
    assert isinstance(preventive_nodes, list)
    return validate_payload(
        artifact,
        activation,
        ord37_audit,
        shared_audit,
        matrix,
        preventive_nodes,
    )


def main() -> int:
    errors = validate()
    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        return 1
    artifact = load(ARTIFACT)
    assert isinstance(artifact, dict)
    standards = (artifact.get("priority_1") or {}).get("governing_standards_ordinance") or {}
    print(
        "PASS: Worker B bounded currentness closure validates; "
        f"{standards.get('new_promotions_this_wave')} new and "
        f"{standards.get('cumulative_promotions')} cumulative governing-standards "
        "service cells are exact-identity PASS candidates."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
