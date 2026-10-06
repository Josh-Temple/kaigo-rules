#!/usr/bin/env python3
"""Validate Worker A residual Governing Standards currentness closure.

Currentness PASS is allowed only for an exact service x source-family identity
whose canonical source is a current official e-Gov version and whose direct
service scope resolves inside the independently reparsed current corpus.
Incorporation/read-as semantics remain outside this currentness-only decision.
"""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "data/verification/governing-standards-residual-currentness-worker-a.json"
ACTIVATION = ROOT / "data/verification/shared-source-currentness-activation.json"
AUDIT = ROOT / "data/shared/standards/independent-audit.json"
MATRIX = ROOT / "data/database-coverage-matrix.generated.json"

TARGETS = {
    "community-dayservice": ("community-based-standards", "data/services/community-dayservice/shared-corpus-scope.json", "community"),
    "regular-round": ("community-based-standards", "data/services/regular-round/shared-corpus-scope.json", "community"),
    "night-homevisit": ("community-based-standards", "data/services/night-homevisit/shared-corpus-scope.json", "community"),
    "care-management": ("care-management-standards", "data/services/care-management/governing-standards-scope.json", "dedicated"),
    "preventive-support": ("preventive-support-standards", "data/services/preventive-support/governing-standards-scope.json", "dedicated"),
    "dementia-dayservice": ("community-based-standards", "data/services/dementia-dayservice/shared-corpus-scope.json", "community"),
    "small-scale-multifunctional": ("community-based-standards", "data/services/small-scale-multifunctional/shared-corpus-scope.json", "community"),
    "dementia-group-home": ("community-based-standards", "data/services/dementia-group-home/shared-corpus-scope.json", "community"),
    "community-specific-facility": ("community-based-standards", "data/services/community-specific-facility/shared-corpus-scope.json", "community"),
    "community-elderly-facility": ("community-based-standards", "data/services/community-elderly-facility/shared-corpus-scope.json", "community"),
    "nursing-small-scale-multifunctional": ("community-based-standards", "data/services/nursing-small-scale-multifunctional/shared-corpus-scope.json", "community"),
    "elderly-welfare-facility": ("elderly-welfare-facility-standards", "data/services/elderly-welfare-facility/governing-standards-scope.json", "dedicated"),
    "elderly-health-facility": ("geriatric-health-services-facility-standards", "data/services/elderly-health-facility/governing-standards-scope.json", "dedicated"),
    "care-medical-institution": ("long-term-care-medical-facility-standards", "data/services/care-medical-institution/governing-standards-scope.json", "dedicated"),
    "preventive-dementia-dayservice": ("preventive-community-based-standards", "data/services/preventive-dementia-dayservice/standards36-scope.json", "preventive_community"),
    "preventive-small-scale-multifunctional": ("preventive-community-based-standards", "data/services/preventive-small-scale-multifunctional/standards36-scope.json", "preventive_community"),
    "preventive-dementia-group-home": ("preventive-community-based-standards", "data/services/preventive-dementia-group-home/standards36-scope.json", "preventive_community"),
}

# Legal source wording can include these established labels instead of the
# repository's display label. These are source aliases, not service merging.
SERVICE_SOURCE_ALIASES = {
    "nursing-small-scale-multifunctional": ("看護小規模多機能型居宅介護", "複合型サービス"),
    "community-elderly-facility": ("地域密着型介護老人福祉施設入所者生活介護", "地域密着型介護老人福祉施設"),
}

PASS_SOURCE_CLASSES = {"CURRENT_OFFICIAL_VERSIONED", "CURRENT_OFFICIAL_CONSOLIDATED"}
DEFERRED_TARGETS = {
    "night-homevisit": "CURRENT_CORPUS_SCOPE_ENDPOINT_NOT_RESOLVED",
    "dementia-group-home": "CURRENT_CORPUS_SCOPE_ENDPOINT_NOT_RESOLVED",
}
PROMOTED_TARGETS = set(TARGETS) - set(DEFERRED_TARGETS)


def load(path: Path | str) -> Any:
    p = Path(path)
    if not p.is_absolute():
        p = ROOT / p
    return json.loads(p.read_text(encoding="utf-8"))


def family_rows(matrix: dict[str, Any]) -> dict[str, dict[str, Any]]:
    out = {}
    for service in matrix.get("services", []):
        row = next(
            x for x in service.get("source_families", [])
            if x.get("source_family") == "governing_standards_ordinance"
        )
        out[str(service["service_id"])] = row
    return out


def source_inventory(activation: dict[str, Any]) -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    family = (activation.get("source_families") or {}).get("governing_standards_ordinance") or {}
    return family, {
        str(row.get("canonical_source_id")): row
        for row in family.get("sources", [])
    }


def article_rows(corpus_id: str) -> list[dict[str, Any]]:
    rows = load(f"data/shared/standards/{corpus_id}/nodes.json")
    return [row for row in rows if row.get("node_type") == "article"]


def article_range(rows: list[dict[str, Any]], start: str, end: str) -> list[dict[str, Any]]:
    positions = {str(row.get("article_num")): i for i, row in enumerate(rows)}
    if start not in positions or end not in positions or positions[start] > positions[end]:
        return []
    return rows[positions[start]:positions[end] + 1]


def source_text(rows: list[dict[str, Any]]) -> str:
    values = []
    for row in rows:
        values.extend(str(x) for x in row.get("path", []))
        values.append(str(row.get("official_text") or ""))
        values.append(str(row.get("source_locator") or ""))
    return " ".join(values)


def direct_scope_evidence(
    service_id: str,
    service_label: str,
    corpus_id: str,
    scope_path: str,
    kind: str,
) -> tuple[list[str], dict[str, Any]]:
    errors: list[str] = []
    scope = load(scope_path)
    rows = article_rows(corpus_id)
    if scope.get("service_id") != service_id:
        errors.append(f"{service_id}: scope service identity mismatch")

    meta = load(f"data/shared/standards/{corpus_id}/meta.json")
    if meta.get("corpus_id") != corpus_id:
        errors.append(f"{service_id}: corpus meta identity mismatch")

    summary: dict[str, Any] = {"scope_path": scope_path, "corpus_id": corpus_id}

    if kind == "community":
        gov = scope.get("governing_standards_ordinance") or {}
        if gov.get("corpus_id") != corpus_id:
            errors.append(f"{service_id}: scope corpus mismatch")
        if gov.get("law_id") != meta.get("law_id"):
            errors.append(f"{service_id}: scope law identity mismatch")
        ranges = gov.get("direct_article_ranges") or []
        direct = [
            r for r in ranges
            if r.get("role") not in {"common", "common_miscellaneous_electronic_records"}
        ]
        if not direct:
            errors.append(f"{service_id}: no service-specific direct range")
        resolved = []
        for r in direct:
            part = article_range(rows, str(r.get("from")), str(r.get("through")))
            if not part:
                errors.append(
                    f"{service_id}: direct range does not resolve in current corpus "
                    f"{r.get('from')}..{r.get('through')}"
                )
            resolved.extend(part)
        aliases = SERVICE_SOURCE_ALIASES.get(service_id, (service_label,))
        text = source_text(resolved)
        if resolved and not any(alias in text for alias in aliases):
            errors.append(f"{service_id}: direct current-corpus range does not identify service")
        official = [
            row for row in gov.get("source_evidence", [])
            if row.get("url") == meta.get("source_page")
        ]
        if not official:
            errors.append(f"{service_id}: exact official e-Gov service locator missing")
        summary["direct_ranges"] = direct
        summary["direct_article_count"] = len({r.get("id") for r in resolved})

    elif kind == "preventive_community":
        if scope.get("corpus_id") != corpus_id:
            errors.append(f"{service_id}: preventive-community corpus mismatch")
        if scope.get("law_id") != meta.get("law_id"):
            errors.append(f"{service_id}: preventive-community law identity mismatch")
        chapter = scope.get("service_chapter_direct_scope") or {}
        ids = [str(x) for x in chapter.get("source_node_ids", [])]
        by_id = {str(row.get("id")): row for row in rows}
        resolved = [by_id[x] for x in ids if x in by_id]
        if not ids or len(resolved) != len(ids):
            errors.append(f"{service_id}: direct service chapter nodes do not resolve")
        declared = str(chapter.get("chapter") or "")
        if service_label not in declared:
            errors.append(f"{service_id}: declared direct chapter does not identify service")
        text = source_text(resolved)
        if resolved and service_label not in text and declared not in text:
            errors.append(f"{service_id}: current corpus does not contain declared service chapter")
        if scope.get("evidence", {}).get("source_corpus_meta") != f"data/shared/standards/{corpus_id}/meta.json":
            errors.append(f"{service_id}: canonical corpus-meta evidence pointer mismatch")
        summary["chapter"] = declared
        summary["direct_article_count"] = len(resolved)

    else:
        # Dedicated regulation: source identity itself is service-specific.
        if scope.get("status") != "SCOPE_DEFINED_APPLICABILITY_NOT_VERIFIED":
            errors.append(f"{service_id}: unexpected dedicated scope status")
        law_title = str(meta.get("law_title") or "")
        aliases = SERVICE_SOURCE_ALIASES.get(service_id, (service_label,))
        if not any(alias in law_title for alias in aliases):
            errors.append(f"{service_id}: dedicated current regulation title does not identify service")
        direct_nums: list[str] = [str(x) for x in (scope.get("common_direct_scope") or {}).get("article_numbers", [])]
        for variant in scope.get("service_variants") or []:
            direct_nums.extend(str(x) for x in variant.get("article_numbers", []))
            direct_nums.extend(str(x) for x in (variant.get("direct_scope") or {}).get("article_numbers", []))
        direct_nums = list(dict.fromkeys(direct_nums))
        by_num = {str(row.get("article_num")): row for row in rows}
        missing = [num for num in direct_nums if num not in by_num]
        if not direct_nums:
            errors.append(f"{service_id}: no dedicated direct-scope articles")
        if missing:
            errors.append(f"{service_id}: direct-scope articles missing from current corpus: {missing}")
        summary["law_title"] = law_title
        summary["direct_article_count"] = len(direct_nums)

    return errors, summary


def validate_payload(
    artifact: dict[str, Any],
    activation: dict[str, Any],
    audit: dict[str, Any],
    matrix: dict[str, Any],
) -> list[str]:
    errors: list[str] = []
    if artifact.get("artifact_kind") != "GOVERNING_STANDARDS_RESIDUAL_CURRENTNESS_CLOSURE":
        errors.append("artifact kind mismatch")
    if artifact.get("worker") != "A":
        errors.append("worker identity mismatch")
    if artifact.get("format_version") != 1:
        errors.append("artifact format_version mismatch")

    policy = artifact.get("policy") or {}
    false_flags = (
        "source_level_currentness_broadcast_allowed",
        "regular_preventive_inheritance_allowed",
        "unresolved_incorporation_semantics_promoted",
        "relation_verification_promoted",
        "human_review_promoted",
        "publication_promoted",
        "route_exposure_promoted",
        "stale_or_superseded_source_can_pass",
    )
    for key in false_flags:
        if policy.get(key) is not False:
            errors.append(f"unsafe policy flag: {key}")
    for key in (
        "service_specific_applicability_required",
        "source_identity_match_required",
        "source_version_scope_containment_required",
        "item_body_pass_required",
    ):
        if policy.get(key) is not True:
            errors.append(f"missing required policy: {key}")

    matrix_rows = family_rows(matrix)
    target_ids = set(TARGETS)
    current_pass = {
        sid for sid, row in matrix_rows.items()
        if (row.get("currentness") or {}).get("state") == "PASS"
    }
    target_states = {
        sid: (matrix_rows[sid].get("currentness") or {}).get("state")
        for sid in target_ids
    }
    preintegration = all(state == "NOT_ESTABLISHED" for state in target_states.values())
    integrated = (
        all(target_states[sid] == "PASS" for sid in PROMOTED_TARGETS)
        and all(target_states[sid] == "NOT_ESTABLISHED" for sid in DEFERRED_TARGETS)
    )
    if not preintegration and not integrated:
        errors.append(f"target currentness is neither exact preintegration nor integrated state: {target_states}")
    if preintegration and len(current_pass) != 22:
        errors.append(f"existing READY/currentness PASS baseline regressed or drifted: {len(current_pass)}")
    if integrated and len(current_pass) != 37:
        errors.append(f"integrated governing standards PASS count must be 37, got {len(current_pass)}")

    starting = artifact.get("starting_inventory") or {}
    if starting.get("ready") != 22 or starting.get("blocked_currentness") != 17:
        errors.append("starting inventory must preserve fresh 22 READY / 17 blocked baseline")
    if set(starting.get("targeted_service_ids") or []) != target_ids:
        errors.append("starting residual target inventory mismatch")

    family, source_by_id = source_inventory(activation)
    if family.get("currentness_class") not in PASS_SOURCE_CLASSES:
        errors.append("governing standards source family is not current-version PASS eligible")
    if family.get("source_identity_complete") is not True:
        errors.append("governing standards source identity inventory incomplete")
    audit_rows = {str(r.get("id")): r for r in audit.get("checks", [])}
    if audit.get("audit_result") != "PASS":
        errors.append("shared standards independent audit is not PASS")

    source_evidence = artifact.get("source_evidence") or {}
    for corpus_id in sorted({v[0] for v in TARGETS.values()}):
        source = source_by_id.get(corpus_id)
        recorded = source_evidence.get(corpus_id)
        audited = audit_rows.get(corpus_id)
        if not source or not recorded or not audited:
            errors.append(f"{corpus_id}: source/currentness/audit evidence incomplete")
            continue
        if source.get("source_form") != "OFFICIAL_VERSIONED_CURRENT_TEXT":
            errors.append(f"{corpus_id}: source is not official versioned current text")
        lineage = source.get("revision_lineage") or {}
        if lineage.get("current_revision_status") != "CurrentEnforced":
            errors.append(f"{corpus_id}: source revision is not CurrentEnforced")
        if lineage.get("repeal_status") != "None":
            errors.append(f"{corpus_id}: source is repealed/superseded")
        if audited.get("result") != "PASS":
            errors.append(f"{corpus_id}: independent current-body audit is not PASS")
        observed_hash = audited.get("observed_xml_sha256")
        expected_hash = (source.get("fingerprint") or {}).get("xml_sha256")
        if observed_hash != expected_hash:
            errors.append(f"{corpus_id}: independent audit fingerprint differs from current source")
        for key in ("canonical_source_id", "official_source_url", "version_id", "effective_date", "fingerprint", "revision_lineage"):
            if recorded.get(key) != source.get(key):
                errors.append(f"{corpus_id}: recorded source evidence drift: {key}")

    decisions = artifact.get("decisions") or []
    by_id = {str(row.get("service_id")): row for row in decisions}
    if set(by_id) != target_ids or len(by_id) != len(decisions):
        errors.append("decision inventory must contain each residual service exactly once")

    for service_id, (corpus_id, scope_path, kind) in TARGETS.items():
        row = by_id.get(service_id) or {}
        matrix_row = matrix_rows[service_id]
        service_label = str(row.get("service_label") or "")
        if row.get("source_family") != "governing_standards_ordinance":
            errors.append(f"{service_id}: source-family mismatch")
        if row.get("canonical_source_id") != corpus_id:
            errors.append(f"{service_id}: source identity mismatch")
        if row.get("scope_path") != scope_path:
            errors.append(f"{service_id}: scope evidence pointer mismatch")
        if row.get("ingestion_state") != "INGESTED" or row.get("item_body_state") != "PASS":
            errors.append(f"{service_id}: ingestion/item-body prerequisite not satisfied")
        if (matrix_row.get("item_body_verification") or {}).get("state") != "PASS":
            errors.append(f"{service_id}: canonical item-body PASS disappeared")
        if (matrix_row.get("ingestion") or {}).get("state") != "INGESTED":
            errors.append(f"{service_id}: canonical ingestion state drift")
        gate = row.get("projection_gate") or {}
        if gate.get("identity") != f"{service_id}::governing_standards_ordinance":
            errors.append(f"{service_id}: gate identity mismatch")
        proof = row.get("applicability_proof") or {}
        if proof.get("regular_preventive_inheritance_used") is not False:
            errors.append(f"{service_id}: regular/preventive inheritance is forbidden")
        if proof.get("incorporation_or_read_as_semantics_promoted") is not False:
            errors.append(f"{service_id}: unresolved relation semantics leaked into currentness")

        scope_errors, resolved = direct_scope_evidence(
            service_id, service_label, corpus_id, scope_path, kind
        )
        if service_id in DEFERRED_TARGETS:
            expected_blocker = DEFERRED_TARGETS[service_id]
            if row.get("decision") != "DEFER" or row.get("promotion_applied") is not False:
                errors.append(f"{service_id}: unresolved current-version scope must remain deferred")
            if row.get("blocker") != expected_blocker:
                errors.append(f"{service_id}: deferred blocker mismatch")
            if row.get("projected_currentness_state") != "NOT_ESTABLISHED":
                errors.append(f"{service_id}: deferred currentness must remain NOT_ESTABLISHED")
            if row.get("source_version_contains_scope") is not False:
                errors.append(f"{service_id}: unresolved scope cannot claim version containment")
            if gate.get("kind") != "EXPLICIT_BOUNDED_ALLOWLIST" or gate.get("allowed") is not False:
                errors.append(f"{service_id}: deferred cell gate must remain closed")
            if proof.get("state") != "NOT_ESTABLISHED_CURRENT_VERSION_SCOPE_ENDPOINT":
                errors.append(f"{service_id}: unresolved scope proof state mismatch")
            if not any("direct range does not resolve in current corpus" in e for e in scope_errors):
                errors.append(f"{service_id}: recorded endpoint blocker no longer reproduces")
            if resolved.get("direct_article_count"):
                errors.append(f"{service_id}: deferred scope unexpectedly resolved direct articles")
        else:
            if row.get("decision") != "PROMOTE_PASS_BOUNDED" or row.get("promotion_applied") is not True:
                errors.append(f"{service_id}: bounded promotion decision missing")
            if row.get("blocker") is not None:
                errors.append(f"{service_id}: promoted cell cannot retain blocker")
            if row.get("projected_currentness_state") != "PASS":
                errors.append(f"{service_id}: projected currentness must be PASS")
            if row.get("source_version_contains_scope") is not True:
                errors.append(f"{service_id}: current source-version containment not established")
            if gate.get("kind") != "EXPLICIT_BOUNDED_ALLOWLIST" or gate.get("allowed") is not True:
                errors.append(f"{service_id}: explicit bounded gate missing")
            if proof.get("state") != "PASS_DIRECT_SCOPE_CURRENT_VERSION":
                errors.append(f"{service_id}: service-specific direct-scope proof missing")
            errors.extend(scope_errors)
            if not resolved.get("direct_article_count"):
                errors.append(f"{service_id}: no exact direct current-version evidence resolved")

    # Explicitly prove preventive-support remains its own source identity.
    if (by_id.get("preventive-support") or {}).get("canonical_source_id") != "preventive-support-standards":
        errors.append("preventive-support must not be merged into another service/source identity")
    for preventive_id in (
        "preventive-dementia-dayservice",
        "preventive-small-scale-multifunctional",
        "preventive-dementia-group-home",
    ):
        if (by_id.get(preventive_id) or {}).get("canonical_source_id") != "preventive-community-based-standards":
            errors.append(f"{preventive_id}: preventive source identity must remain distinct")
    for regular_id in (
        "dementia-dayservice",
        "small-scale-multifunctional",
        "dementia-group-home",
    ):
        if (by_id.get(regular_id) or {}).get("canonical_source_id") != "community-based-standards":
            errors.append(f"{regular_id}: regular source identity must remain distinct")

    summary = artifact.get("summary") or {}
    if summary.get("targeted_cells") != 17:
        errors.append("targeted cell count mismatch")
    if summary.get("promoted_cells") != len(PROMOTED_TARGETS):
        errors.append("promoted cell count mismatch")
    if summary.get("deferred_cells") != len(DEFERRED_TARGETS):
        errors.append("deferred cell count mismatch")
    if set(summary.get("deferred_service_ids") or []) != set(DEFERRED_TARGETS):
        errors.append("deferred service inventory mismatch")
    if summary.get("projected_ready_increase") != len(PROMOTED_TARGETS):
        errors.append("projected READY increase mismatch")
    if summary.get("projected_governing_standards_ready") != 37:
        errors.append("projected governing standards READY count mismatch")

    boundary = artifact.get("integration_boundary") or {}
    for key in (
        "generated_coverage_matrix_modified_by_worker_a",
        "publication_readiness_modified_by_worker_a",
        "bounded_publication_allowlist_modified_by_worker_a",
    ):
        if boundary.get(key) is not False:
            errors.append(f"Worker A integration boundary broken: {key}")
    if boundary.get("worker_e_must_regenerate_global_generated_artifacts_after_semantic_integration") is not True:
        errors.append("Worker E regeneration boundary missing")
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
    summary = artifact["summary"]
    print(
        "PASS: Worker A residual governing-standards currentness closure validates; "
        f"{summary['promoted_cells']} exact service cells are bounded PASS candidates, "
        f"projecting {summary['projected_governing_standards_ready']} / 39 READY."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
