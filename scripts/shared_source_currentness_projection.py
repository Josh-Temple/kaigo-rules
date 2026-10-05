#!/usr/bin/env python3
"""Read-only applicability-aware currentness projection for shared national sources.

Worker A / 2026-10-06 activation wave. This module never mutates canonical
service state or global generated artifacts.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
INVENTORY_PATH = ROOT / "data/verification/shared-source-currentness-activation.json"
MATRIX_PATH = ROOT / "data/database-coverage-matrix.generated.json"
MANIFEST_PATH = ROOT / "data/services/manifest.json"
STANDARDS_RELATIONS_PATH = ROOT / "data/shared/standards/service-relations.generated.json"
DELEGATED_APPLICABILITY_PATH = ROOT / "data/shared/remuneration-delegated/service-applicability.json"
REMUNERATION_ASSURANCE_PATH = ROOT / "data/shared/remuneration-notification/service-item-body-assurance.json"
UNIT_PRICE_PATH = ROOT / "data/unit-price-service-multipliers.json"
QA_RELATIONS_PATH = ROOT / "data/qa-service-relations.generated.json"

TARGET_FAMILIES = (
    "care_insurance_act",
    "governing_standards_ordinance",
    "remuneration_notification",
    "delegated_remuneration_criteria",
    "unit_price_regional_classification",
    "national_qa",
    "other_national_manuals_forms",
)
PASS_ELIGIBLE_CLASSES = {"CURRENT_OFFICIAL_CONSOLIDATED", "CURRENT_OFFICIAL_VERSIONED"}
PASS_APPLICABILITY_STATES = {"PASS", "VERIFIED", "APPLICABILITY_VERIFIED", "SERVICE_VERIFIED"}


def load(path: str | Path) -> Any:
    p = Path(path)
    if not p.is_absolute():
        p = ROOT / p
    return json.loads(p.read_text(encoding="utf-8"))


def upper(value: Any) -> str:
    return str(value or "").strip().upper()


def pass_state(value: Any) -> bool:
    state = upper(value)
    return state in PASS_APPLICABILITY_STATES or state.startswith("PASS_")


def explicit_promotion_gate(value: dict[str, Any]) -> bool:
    """Require an explicit true gate; absent or false is fail-closed."""
    candidates = [
        value.get("automatic_verification_promotion_allowed"),
        (value.get("projection_policy") or {}).get("automatic_verification_promotion_allowed"),
        (value.get("corpus_policy") or {}).get("automatic_verification_promotion_allowed"),
    ]
    booleans = [x for x in candidates if isinstance(x, bool)]
    return bool(booleans) and all(booleans)


def explicit_applicability(value: dict[str, Any]) -> tuple[bool, list[str]]:
    candidates = [
        ("service_applicability", value.get("service_applicability")),
        ("applicability_verification", value.get("applicability_verification")),
        ("direct_applicability_verification", value.get("direct_applicability_verification")),
        ("verification.service_applicability", (value.get("verification") or {}).get("service_applicability")),
        ("states.service_applicability", (value.get("states") or {}).get("service_applicability")),
    ]
    evidence = [f"{key}={state}" for key, state in candidates if state is not None]
    return any(pass_state(state) for _, state in candidates), evidence


def evaluate_projection(
    *,
    existing_currentness: str,
    source_class: str,
    source_identity_complete: bool,
    applicability_verified: bool,
    scope_identified: bool,
    source_version_contains_scope: bool,
    ingestion_state: str,
    automatic_promotion_allowed: bool,
) -> dict[str, Any]:
    """Evaluate one cell without mutating canonical state."""
    not_applicable = upper(ingestion_state) == "NOT_APPLICABLE"
    conditions = {
        "source_identity_currentness_established": source_identity_complete
        and source_class in PASS_ELIGIBLE_CLASSES,
        "service_applicability_explicitly_established": applicability_verified,
        "service_scope_identified": scope_identified,
        "source_version_contains_scope": source_version_contains_scope,
        "not_applicable_is_false": not not_applicable,
        "automatic_promotion_gate": automatic_promotion_allowed,
    }
    eligible = all(conditions.values())
    projected = "PASS" if eligible else existing_currentness
    return {
        "eligible": eligible,
        "conditions": conditions,
        "projected_currentness": projected,
        "promotion_recommended": eligible and existing_currentness != "PASS",
    }


def matrix_index() -> dict[tuple[str, str], dict[str, Any]]:
    matrix = load(MATRIX_PATH)
    result: dict[tuple[str, str], dict[str, Any]] = {}
    for service in matrix.get("services", []):
        for cell in service.get("source_families", []):
            result[(service["service_id"], cell["source_family"])] = cell
    return result


def service_configs() -> dict[str, dict[str, Any]]:
    manifest = load(MANIFEST_PATH)
    return {row["service_id"]: load(row["config"]) for row in manifest.get("services", [])}


def care_act_applicability(service_id: str, config: dict[str, Any]) -> tuple[bool, bool, list[str], bool]:
    scope_files = config.get("scope_files") or {}
    path = scope_files.get("care_insurance_act") or scope_files.get("care_insurance_act_core")
    if not path or not (ROOT / path).exists():
        return False, False, [], False
    scope = load(path)
    applicable, evidence = explicit_applicability(scope)
    source_aligned = str(scope.get("law_id") or (scope.get("source_corpus") or {}).get("law_id") or "") == "409AC0000000123"
    if not source_aligned:
        source_text = json.dumps(scope, ensure_ascii=False)
        source_aligned = "409AC0000000123" in source_text or "care-insurance-act" in source_text
    return applicable, True, [path, *evidence], explicit_promotion_gate(scope) and source_aligned


def standards_applicability(service_id: str, relations: dict[str, Any]) -> tuple[bool, bool, list[str], bool, bool]:
    row = next((x for x in relations.get("service_scope_states", []) if x.get("service_id") == service_id), None)
    if not row:
        return False, False, [], False, False
    scope_defined = row.get("scope_status") == "SCOPE_DEFINED"
    applicability = pass_state(row.get("relation_verification"))
    evidence = ["data/shared/standards/service-relations.generated.json"]
    if row.get("scope_source"):
        evidence.append(str(row["scope_source"]))
    auto_gate = row.get("automatic_verification_promotion_allowed") is True
    return applicability, scope_defined, evidence, auto_gate, bool(row.get("corpus_id"))


def family_context(service_id: str, family: str, config: dict[str, Any], shared: dict[str, Any]) -> dict[str, Any]:
    if family == "care_insurance_act":
        app, scope, evidence, gate_and_alignment = care_act_applicability(service_id, config)
        return {
            "applicability_verified": app,
            "scope_identified": scope,
            "source_version_contains_scope": scope,
            "automatic_promotion_allowed": gate_and_alignment,
            "applicability_evidence": evidence,
        }
    if family == "governing_standards_ordinance":
        app, scope, evidence, gate, aligned = standards_applicability(service_id, shared["standards_relations"])
        return {
            "applicability_verified": app,
            "scope_identified": scope,
            "source_version_contains_scope": aligned and scope,
            "automatic_promotion_allowed": gate,
            "applicability_evidence": evidence,
        }
    if family == "remuneration_notification":
        row = shared["remuneration"].get(service_id) or {}
        applies = str(row.get("applicability_state") or "").startswith("APPLIES")
        return {
            "applicability_verified": False,
            "scope_identified": applies,
            "source_version_contains_scope": bool(row.get("source_fingerprint_section_id") or row.get("evidence")),
            "automatic_promotion_allowed": False,
            "applicability_evidence": ["data/shared/remuneration-notification/service-item-body-assurance.json"] + list(row.get("evidence") or []),
        }
    if family == "delegated_remuneration_criteria":
        row = shared["delegated"].get(service_id) or {}
        state = str(row.get("applicability_state") or "")
        return {
            "applicability_verified": state == "MAPPED" and str((row.get("assurance") or {}).get("service_applicability_verification") or "") == "PASS",
            "scope_identified": state in {"MAPPED", "NOT_APPLICABLE"},
            "source_version_contains_scope": bool(row.get("mapped_node_count", 0)) or state == "NOT_APPLICABLE",
            "automatic_promotion_allowed": False,
            "applicability_evidence": [f"data/shared/remuneration-delegated/service-applicability.json#{service_id}"],
        }
    if family == "unit_price_regional_classification":
        row = shared["unit_price"].get(service_id) or {}
        state = str(row.get("applicability") or "")
        return {
            "applicability_verified": state == "APPLIES",
            "scope_identified": state in {"APPLIES", "NOT_APPLICABLE"},
            "source_version_contains_scope": bool(row.get("source_locator")),
            "automatic_promotion_allowed": False,
            "applicability_evidence": [f"data/unit-price-service-multipliers.json#{service_id}"],
        }
    if family == "national_qa":
        row = shared["qa"].get(service_id) or {}
        defined = str(row.get("scope_state") or "").startswith("DEFINED")
        return {
            "applicability_verified": False,
            "scope_identified": defined,
            "source_version_contains_scope": defined,
            "automatic_promotion_allowed": False,
            "applicability_evidence": [f"data/qa-service-relations.generated.json#{service_id}"],
        }
    return {
        "applicability_verified": False,
        "scope_identified": False,
        "source_version_contains_scope": False,
        "automatic_promotion_allowed": False,
        "applicability_evidence": ["data/shared/other-national-materials/currentness-assurance.json"],
    }


def build_projection() -> dict[str, Any]:
    inventory = load(INVENTORY_PATH)
    configs = service_configs()
    cells = matrix_index()
    standards_relations = load(STANDARDS_RELATIONS_PATH)
    delegated = load(DELEGATED_APPLICABILITY_PATH)
    remuneration = load(REMUNERATION_ASSURANCE_PATH)
    unit = load(UNIT_PRICE_PATH)
    qa = load(QA_RELATIONS_PATH)
    shared = {
        "standards_relations": standards_relations,
        "delegated": {x["service_id"]: x for x in delegated.get("services", [])},
        "remuneration": {x["service_id"]: x for x in remuneration.get("services", [])},
        "unit_price": {x["service_id"]: x for x in unit.get("service_mappings", [])},
        "qa": {x["service_id"]: x for x in qa.get("services", [])},
    }
    family_inventory = inventory["source_families"]
    rows: list[dict[str, Any]] = []
    for service_id, config in configs.items():
        for family in TARGET_FAMILIES:
            cell = cells[(service_id, family)]
            source = family_inventory[family]
            context = family_context(service_id, family, config, shared)
            existing = str((cell.get("currentness") or {}).get("state") or "NOT_ESTABLISHED")
            result = evaluate_projection(
                existing_currentness=existing,
                source_class=str(source.get("currentness_class")),
                source_identity_complete=bool(source.get("source_identity_complete")),
                applicability_verified=context["applicability_verified"],
                scope_identified=context["scope_identified"],
                source_version_contains_scope=context["source_version_contains_scope"],
                ingestion_state=str((cell.get("ingestion") or {}).get("state") or "NOT_INGESTED"),
                automatic_promotion_allowed=context["automatic_promotion_allowed"],
            )
            rows.append({
                "service_id": service_id,
                "source_family": family,
                "existing_currentness": existing,
                "source_currentness_class": source.get("currentness_class"),
                "ingestion_state": (cell.get("ingestion") or {}).get("state"),
                **result,
                "provenance": {
                    "source_level_evidence": list(source.get("evidence") or []),
                    "applicability_evidence": context["applicability_evidence"],
                    "projection_rule": inventory["projection_policy"]["rule_id"],
                    "projection_timestamp": inventory["projection_snapshot_at"],
                    "generator": "scripts/shared_source_currentness_projection.py",
                    "validator": "scripts/validate_shared_source_currentness_activation.py",
                },
            })
    promotions = [r for r in rows if r["promotion_recommended"]]
    return {
        "format_version": 1,
        "projection_kind": "SHARED_SOURCE_CURRENTNESS_APPLICABILITY_AWARE_READ_ONLY",
        "source_inventory": str(INVENTORY_PATH.relative_to(ROOT)),
        "projection_snapshot_at": inventory["projection_snapshot_at"],
        "mutation": "READ_ONLY",
        "rows": rows,
        "summary": {
            "services": len(configs),
            "source_families": len(TARGET_FAMILIES),
            "cells_evaluated": len(rows),
            "promotions_recommended": len(promotions),
            "promotion_identities": [f"{r['service_id']}::{r['source_family']}" for r in promotions],
        },
        "safety": {
            "writes_canonical_state": False,
            "writes_global_generated_artifacts": False,
            "broadcast_source_currentness_to_all_services": False,
            "changes_item_body_verification": False,
            "changes_relation_verification": False,
            "changes_human_review": False,
            "changes_publication": False,
            "changes_route_exposure": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--summary-only", action="store_true")
    args = parser.parse_args()
    report = build_projection()
    print(json.dumps(report["summary"] if args.summary_only else report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
