#!/usr/bin/env python3
"""Validate Worker A shared-source currentness activation inventory and projection."""
from __future__ import annotations

import json
from typing import Any

from shared_source_currentness_projection import (
    INVENTORY_PATH,
    PASS_ELIGIBLE_CLASSES,
    TARGET_FAMILIES,
    build_projection,
    load,
)

EXPECTED_BASE_SHA = "cb27b4658ba5dd0fee999cf9426d4b45ef0fb3a9"
REQUIRED_CLASSES = {
    "CURRENT_OFFICIAL_CONSOLIDATED",
    "CURRENT_OFFICIAL_VERSIONED",
    "CURRENTNESS_PARTIAL",
    "AMENDMENT_ONLY",
    "COMPARISON_ONLY",
    "HISTORICAL_ONLY",
    "LOCATOR_ONLY",
    "NOT_ESTABLISHED",
}
GLOBAL_ARTIFACTS = {
    "data/database-coverage-matrix.generated.json",
    "docs/database-coverage-summary.generated.md",
    "data/services/catalog.generated.json",
}

def require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)

def source_rows(family: dict[str, Any]) -> list[dict[str, Any]]:
    rows = family.get("sources")
    return rows if isinstance(rows, list) else []

def main() -> int:
    errors: list[str] = []
    inventory = load(INVENTORY_PATH)
    require(inventory.get("inventory_kind") == "SHARED_SOURCE_CURRENTNESS_ACTIVATION", "unexpected inventory_kind", errors)
    require(inventory.get("base_main_sha") == EXPECTED_BASE_SHA, "fresh-read base main SHA drifted", errors)
    require(set(inventory.get("currentness_classes") or []) == REQUIRED_CLASSES, "currentness evidence class set drifted", errors)
    require(set(inventory.get("source_families") or {}) == set(TARGET_FAMILIES), "priority source-family set drifted", errors)

    policy = inventory.get("projection_policy") or {}
    require(set(policy.get("pass_eligible_currentness_classes") or []) == PASS_ELIGIBLE_CLASSES, "PASS-eligible class policy drifted", errors)
    for key in (
        "source_identity_required",
        "explicit_service_applicability_required",
        "service_scope_required",
        "source_version_must_contain_scope",
        "not_applicable_never_promoted",
        "explicit_automatic_promotion_gate_required",
        "comparison_only_never_pass",
        "historical_only_never_pass",
        "source_level_currentness_does_not_broadcast",
    ):
        require(policy.get(key) is True, f"projection policy boundary missing: {key}", errors)

    families = inventory["source_families"]
    for family_id, family in families.items():
        currentness_class = family.get("currentness_class")
        require(currentness_class in REQUIRED_CLASSES, f"{family_id}: unknown currentness class", errors)
        require(isinstance(family.get("source_identity_complete"), bool), f"{family_id}: source_identity_complete missing", errors)
        require(isinstance(family.get("service_projection_allowed"), bool), f"{family_id}: service_projection_allowed missing", errors)
        require(bool(family.get("evidence")), f"{family_id}: evidence missing", errors)
        rows = source_rows(family)
        require(bool(rows), f"{family_id}: canonical source inventory empty", errors)
        for source in rows:
            for key in (
                "canonical_source_id",
                "official_source_url",
                "version_id",
                "effective_date",
                "verified_at",
                "fingerprint",
                "revision_lineage",
                "source_form",
                "monitoring_workflow",
            ):
                require(key in source, f"{family_id}/{source.get('canonical_source_id')}: missing inventory field {key}", errors)
            if currentness_class in PASS_ELIGIBLE_CLASSES:
                require(bool(source.get("canonical_source_id")), f"{family_id}: current source id missing", errors)
                require(bool(source.get("official_source_url")), f"{family_id}: current official URL missing", errors)
                require(bool(source.get("version_id")), f"{family_id}: current version id missing", errors)
                require(bool(source.get("effective_date")), f"{family_id}: current effective date missing", errors)
                require(bool(source.get("fingerprint")), f"{family_id}: current fingerprint missing", errors)
                require(source.get("source_form") in {"OFFICIAL_VERSIONED_CURRENT_TEXT", "OFFICIAL_CONSOLIDATED_CURRENT_TEXT"}, f"{family_id}: unsafe source form for PASS-eligible class", errors)

    care = families["care_insurance_act"]["sources"][0]
    care_meta = load("data/care-insurance-act-meta.json")
    require(care.get("version_id") == (care_meta.get("current_revision") or {}).get("law_revision_id"), "care act revision id drifted", errors)
    require(care.get("fingerprint", {}).get("xml_sha256") == care_meta.get("xml_sha256"), "care act XML fingerprint drifted", errors)
    require(care.get("effective_date") == (care_meta.get("current_revision") or {}).get("amendment_enforcement_date"), "care act effective date drifted", errors)

    standards = families["governing_standards_ordinance"]
    manifest = load("data/shared/standards/manifest.json")
    expected_corpora = {row["corpus_id"] for row in manifest.get("corpora", [])}
    observed_corpora = {row["canonical_source_id"] for row in standards.get("sources", [])}
    require(observed_corpora == expected_corpora, "governing standards current corpus inventory drifted", errors)
    for row in standards.get("sources", []):
        corpus_id = row["canonical_source_id"]
        meta_path = "data/ordinance37-meta.json" if corpus_id == "ordinance37" else f"data/shared/standards/{corpus_id}/meta.json"
        meta = load(meta_path)
        current = meta.get("current_revision") or {}
        require(row.get("version_id") == current.get("law_revision_id"), f"{corpus_id}: revision id drifted", errors)
        require(row.get("effective_date") == current.get("amendment_enforcement_date"), f"{corpus_id}: effective date drifted", errors)
        require(row.get("fingerprint", {}).get("xml_sha256") == meta.get("xml_sha256"), f"{corpus_id}: XML fingerprint drifted", errors)

    for family_id in (
        "remuneration_notification",
        "delegated_remuneration_criteria",
        "unit_price_regional_classification",
        "national_qa",
        "other_national_manuals_forms",
    ):
        family = families[family_id]
        require(family.get("currentness_class") not in PASS_ELIGIBLE_CLASSES, f"{family_id}: unsafe PASS-eligible class", errors)
        require(family.get("service_projection_allowed") is False, f"{family_id}: service projection unexpectedly enabled", errors)

    unit = families["unit_price_regional_classification"]
    require(unit.get("canonical_evidence_status") == "INTEGRATED_MAIN", "unit-price evidence still treated as parallel candidate", errors)
    require("data/unit-price-item-body-assurance.json" in unit.get("evidence", []), "unit-price integrated assurance evidence missing", errors)
    other = families["other_national_manuals_forms"]
    require(other.get("canonical_evidence_status") == "INTEGRATED_MAIN", "other-national evidence still treated as parallel candidate", errors)
    require("data/shared/other-national-materials/currentness-assurance.json" in other.get("evidence", []), "other-national currentness evidence missing", errors)

    report = build_projection()
    require(report["summary"]["cells_evaluated"] == 39 * len(TARGET_FAMILIES), "projection coverage is not 39 x priority families", errors)
    require(report["summary"]["promotions_recommended"] == 0, "unsupported blanket/currentness promotion recommended", errors)
    for row in report.get("rows", []):
        if row.get("ingestion_state") == "NOT_APPLICABLE":
            require(row.get("promotion_recommended") is False, f"{row['service_id']}/{row['source_family']}: NOT_APPLICABLE promoted", errors)
        require(bool((row.get("provenance") or {}).get("source_level_evidence")), f"{row['service_id']}/{row['source_family']}: source provenance missing", errors)
        require(bool((row.get("provenance") or {}).get("projection_rule")), f"{row['service_id']}/{row['source_family']}: projection rule missing", errors)
        require(bool((row.get("provenance") or {}).get("projection_timestamp")), f"{row['service_id']}/{row['source_family']}: projection timestamp missing", errors)

    safety = inventory.get("safety") or {}
    for key in (
        "global_generated_artifacts_updated",
        "canonical_service_currentness_mutated",
        "source_currentness_broadcast_to_all_services",
        "item_body_promoted",
        "relation_verification_promoted",
        "human_review_promoted",
        "publication_promoted",
        "route_exposure_promoted",
    ):
        require(safety.get(key) is False, f"safety boundary broken: {key}", errors)
    require(set(inventory.get("global_generated_artifacts_untouched") or []) == GLOBAL_ARTIFACTS, "global artifact guard list drifted", errors)

    result = {
        "format_version": 1,
        "validation_kind": "SHARED_SOURCE_CURRENTNESS_ACTIVATION",
        "result": "PASS" if not errors else "FAIL",
        "errors": errors,
        "observed": {
            "source_families": len(families),
            "canonical_sources": sum(len(source_rows(f)) for f in families.values()),
            "cells_evaluated": report["summary"]["cells_evaluated"],
            "promotions_recommended": report["summary"]["promotions_recommended"],
        },
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if not errors else 1

if __name__ == "__main__":
    raise SystemExit(main())
