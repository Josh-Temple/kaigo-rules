#!/usr/bin/env python3
"""Evaluate shared-source currentness projection eligibility without mutating canonical state."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
ASSURANCE_PATH = ROOT / "data/verification/shared-currentness-assurance.json"
MATRIX_PATH = ROOT / "data/database-coverage-matrix.generated.json"

TARGET_FAMILIES = (
    "care_insurance_act",
    "governing_standards_ordinance",
    "national_qa",
)
PASS_VALUES = {
    "PASS",
    "VERIFIED",
    "ESTABLISHED",
    "SERVICE_VERIFIED",
    "APPLICABILITY_VERIFIED",
}


def load(path: str | Path) -> Any:
    target = Path(path)
    if not target.is_absolute():
        target = ROOT / target
    return json.loads(target.read_text(encoding="utf-8"))


def upper(value: Any) -> str:
    return str(value or "").strip().upper()


def is_pass(value: Any) -> bool:
    return upper(value) in PASS_VALUES or upper(value).startswith("PASS_")


def get_nested(value: dict[str, Any], *path: str) -> Any:
    current: Any = value
    for key in path:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current


def first_nonempty(*values: Any) -> Any:
    for value in values:
        if value not in (None, "", [], {}):
            return value
    return None


def automatic_projection_allowed(scope: dict[str, Any], supplemental: dict[str, Any] | None = None) -> bool:
    """Fail closed: projection requires an explicit true gate, never an absent/default value."""
    candidates = [
        scope.get("automatic_verification_promotion_allowed"),
        get_nested(scope, "corpus_policy", "automatic_verification_promotion_allowed"),
        get_nested(scope, "projection_policy", "automatic_verification_promotion_allowed"),
    ]
    if supplemental:
        candidates.append(supplemental.get("automatic_verification_promotion_allowed"))
    present = [value for value in candidates if isinstance(value, bool)]
    return bool(present) and all(present)


def explicit_service_applicability(scope: dict[str, Any], supplemental: dict[str, Any] | None = None) -> tuple[bool, list[str]]:
    candidates: list[tuple[str, Any]] = [
        ("verification.service_applicability", get_nested(scope, "verification", "service_applicability")),
        ("states.service_applicability", get_nested(scope, "states", "service_applicability")),
        ("service_applicability", scope.get("service_applicability")),
        ("applicability_verification", scope.get("applicability_verification")),
        ("direct_applicability_verification", scope.get("direct_applicability_verification")),
    ]
    if supplemental:
        candidates.extend(
            [
                ("supplemental.service_applicability", supplemental.get("service_applicability")),
                ("supplemental.applicability_verification", supplemental.get("applicability_verification")),
            ]
        )
    evidence = [f"{name}={value}" for name, value in candidates if value is not None]
    return any(is_pass(value) for _, value in candidates), evidence


def revision_pins(value: Any) -> list[str]:
    pins: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            if key in {"law_revision_id", "source_revision_id", "revision_id", "pinned_revision_id"} and isinstance(child, str):
                pins.append(child)
            pins.extend(revision_pins(child))
    elif isinstance(value, list):
        for child in value:
            pins.extend(revision_pins(child))
    return pins


def contains_historical_marker(value: Any) -> bool:
    if isinstance(value, dict):
        for key, child in value.items():
            if key in {"status", "source_status", "currentness"} and isinstance(child, str):
                marker = upper(child)
                if "HISTORICAL" in marker or "REPEALED" in marker or "SUPERSEDED" in marker:
                    return True
            if contains_historical_marker(child):
                return True
    elif isinstance(value, list):
        return any(contains_historical_marker(child) for child in value)
    return False


def no_old_version_pin(scope: dict[str, Any], current_revision_id: str | None) -> tuple[bool, list[str]]:
    pins = sorted(set(revision_pins(scope)))
    if contains_historical_marker(scope):
        return False, pins
    if not pins:
        return True, []
    if not current_revision_id:
        return False, pins
    return all(pin == current_revision_id for pin in pins), pins


def matrix_currentness_index() -> dict[tuple[str, str], str]:
    matrix = load(MATRIX_PATH)
    result: dict[tuple[str, str], str] = {}
    for service in matrix.get("services", []):
        service_id = service["service_id"]
        for cell in service.get("source_families", []):
            result[(service_id, cell["source_family"])] = cell.get("currentness", {}).get(
                "state", "NOT_ESTABLISHED"
            )
    return result


def care_act_row(
    service: dict[str, Any],
    config: dict[str, Any],
    assurance: dict[str, Any],
    existing_state: str,
) -> dict[str, Any]:
    service_id = service["service_id"]
    source = assurance["source_families"]["care_insurance_act"]
    scope_files = config.get("scope_files") or {}
    scope_path = first_nonempty(
        scope_files.get("care_insurance_act"),
        scope_files.get("care_insurance_act_core"),
    )
    scope: dict[str, Any] = {}
    if scope_path and (ROOT / str(scope_path)).exists():
        scope = load(str(scope_path))

    source_current = source.get("source_level_verdict") == "CURRENT"
    scope_status = upper(scope.get("status"))
    scope_defined = bool(scope_path and scope) and (
        not scope_status
        or "SCOPE_DEFINED" in scope_status
        or scope_status in {"DEFINED", "ACTIVE"}
    )
    applicability, applicability_evidence = explicit_service_applicability(scope)
    expected_law_id = str(source.get("law_id") or "")
    observed_law_id = first_nonempty(
        scope.get("law_id"),
        get_nested(scope, "source_corpus", "law_id"),
        get_nested(scope, "shared_corpus", "law_id"),
    )
    alignment = bool(expected_law_id and observed_law_id == expected_law_id)
    current_revision_id = get_nested(source, "source_snapshot", "current_revision_id")
    no_old_pin, pins = no_old_version_pin(scope, current_revision_id)
    auto_gate = automatic_projection_allowed(scope)

    conditions = {
        "source_identity_currentness_established": source_current,
        "service_scope_established": scope_defined,
        "service_applicability_explicitly_established": applicability,
        "service_reference_aligned_with_current_source_identity": alignment,
        "no_historical_or_old_version_pin": no_old_pin,
    }
    eligible = all(conditions.values()) and auto_gate
    blockers = [name for name, passed in conditions.items() if not passed]
    if not auto_gate:
        blockers.append("automatic_verification_promotion_allowed")
    projected = "PASS" if eligible else existing_state

    return {
        "service_id": service_id,
        "source_family": "care_insurance_act",
        "source_level_verdict": source.get("source_level_verdict"),
        "scope_path": scope_path,
        "conditions": conditions,
        "automatic_projection_allowed": auto_gate,
        "applicability_evidence": applicability_evidence,
        "reference_alignment": {
            "expected_law_id": expected_law_id,
            "observed_law_id": observed_law_id,
            "revision_pins": pins,
            "current_revision_id": current_revision_id,
        },
        "existing_currentness": existing_state,
        "projected_currentness": projected,
        "promotion_applied": projected == "PASS" and existing_state != "PASS",
        "blockers": blockers,
        "evidence": "data/verification/shared-currentness-assurance.json#source_families.care_insurance_act",
    }


def standards_row(
    service: dict[str, Any],
    config: dict[str, Any],
    assurance: dict[str, Any],
    standards_map: dict[str, dict[str, Any]],
    standards_scope: dict[str, dict[str, Any]],
    existing_state: str,
) -> dict[str, Any]:
    service_id = service["service_id"]
    source = assurance["source_families"]["governing_standards_ordinance"]
    corpus_by_id = {row["corpus_id"]: row for row in source.get("corpora", [])}
    mapping = standards_map.get(service_id) or {}
    scope_state = standards_scope.get(service_id) or {}
    corpus_id = first_nonempty(mapping.get("corpus_id"), scope_state.get("corpus_id"))
    corpus = corpus_by_id.get(str(corpus_id)) if corpus_id else None

    scope_path = scope_state.get("scope_source")
    scope: dict[str, Any] = {}
    if scope_path and (ROOT / str(scope_path)).exists():
        scope = load(str(scope_path))

    source_current = bool(
        corpus
        and corpus.get("current_revision_status") == "CurrentEnforced"
        and corpus.get("repeal_status") in (None, "None")
    )
    scope_defined = (
        scope_state.get("scope_status") == "SCOPE_DEFINED"
        and bool(scope_path)
        and bool(scope)
    )
    applicability, applicability_evidence = explicit_service_applicability(
        scope,
        {
            "service_applicability": scope_state.get("service_applicability"),
            "applicability_verification": (
                scope_state.get("relation_verification")
                if is_pass(scope_state.get("relation_verification"))
                else None
            ),
        },
    )

    expected_law_id = str((corpus or {}).get("law_id") or "")
    observed_corpus_id = first_nonempty(
        get_nested(scope, "shared_corpus", "corpus_id"),
        get_nested(scope, "source_corpus", "corpus_id"),
    )
    observed_law_id = first_nonempty(
        scope.get("law_id"),
        get_nested(scope, "shared_corpus", "law_id"),
        get_nested(scope, "source_corpus", "law_id"),
    )
    corpus_alignment = (
        (observed_corpus_id == corpus_id)
        if observed_corpus_id
        else bool(expected_law_id and observed_law_id == expected_law_id)
    )
    map_alignment = bool(
        corpus_id
        and mapping.get("corpus_id") == corpus_id
        and scope_state.get("corpus_id") == corpus_id
    )
    alignment = map_alignment and corpus_alignment
    current_revision_id = (corpus or {}).get("current_revision_id")
    no_old_pin, pins = no_old_version_pin(scope, current_revision_id)
    auto_gate = automatic_projection_allowed(scope, scope_state)

    conditions = {
        "source_identity_currentness_established": source_current,
        "service_scope_established": scope_defined,
        "service_applicability_explicitly_established": applicability,
        "service_reference_aligned_with_current_source_identity": alignment,
        "no_historical_or_old_version_pin": no_old_pin,
    }
    eligible = all(conditions.values()) and auto_gate
    blockers = [name for name, passed in conditions.items() if not passed]
    if not auto_gate:
        blockers.append("automatic_verification_promotion_allowed")
    projected = "PASS" if eligible else existing_state

    return {
        "service_id": service_id,
        "source_family": "governing_standards_ordinance",
        "source_level_verdict": "CURRENT" if source_current else "NOT_ESTABLISHED",
        "corpus_id": corpus_id,
        "scope_path": scope_path,
        "conditions": conditions,
        "automatic_projection_allowed": auto_gate,
        "applicability_evidence": applicability_evidence,
        "reference_alignment": {
            "mapped_corpus_id": mapping.get("corpus_id"),
            "scope_state_corpus_id": scope_state.get("corpus_id"),
            "scope_corpus_id": observed_corpus_id,
            "expected_law_id": expected_law_id,
            "observed_law_id": observed_law_id,
            "revision_pins": pins,
            "current_revision_id": current_revision_id,
        },
        "existing_currentness": existing_state,
        "projected_currentness": projected,
        "promotion_applied": projected == "PASS" and existing_state != "PASS",
        "blockers": blockers,
        "evidence": "data/verification/shared-currentness-assurance.json#source_families.governing_standards_ordinance",
    }


def qa_row(
    service: dict[str, Any],
    assurance: dict[str, Any],
    qa_relations: dict[str, dict[str, Any]],
    qa_meta: dict[str, Any],
    existing_state: str,
) -> dict[str, Any]:
    service_id = service["service_id"]
    source = assurance["source_families"]["national_qa"]
    relation = qa_relations.get(service_id) or {}

    source_current = (
        source.get("source_level_verdict") == "CURRENT_COMPILATION_ONLY"
        and source.get("workbook") == qa_meta.get("source_workbook")
        and source.get("workbook_sha256") == qa_meta.get("source_sha256")
    )
    scope_defined = upper(relation.get("scope_state")).startswith("DEFINED")
    applicability_state = relation.get("item_applicability_verification_state")
    applicability = is_pass(applicability_state)
    alignment = bool(
        source_current
        and relation.get("candidate_query_service_codes")
        and relation.get("scope_state")
    )
    conditions = {
        "source_identity_currentness_established": source_current,
        "service_scope_established": scope_defined,
        "service_applicability_explicitly_established": applicability,
        "service_reference_aligned_with_current_source_identity": alignment,
        "no_historical_or_old_version_pin": True,
    }

    # Compilation freshness is intentionally insufficient for individual Q&A
    # currentness, even if service applicability is established later.
    auto_gate = False
    blockers = [name for name, passed in conditions.items() if not passed]
    blockers.append("individual_qa_currentness_not_established_by_compilation_freshness")
    projected = existing_state

    return {
        "service_id": service_id,
        "source_family": "national_qa",
        "source_level_verdict": source.get("source_level_verdict"),
        "conditions": conditions,
        "automatic_projection_allowed": auto_gate,
        "applicability_evidence": [
            f"item_applicability_verification_state={applicability_state}"
        ],
        "reference_alignment": {
            "workbook": qa_meta.get("source_workbook"),
            "workbook_sha256": qa_meta.get("source_sha256"),
            "candidate_query_service_codes": relation.get("candidate_query_service_codes", []),
        },
        "existing_currentness": existing_state,
        "projected_currentness": projected,
        "promotion_applied": False,
        "blockers": sorted(set(blockers)),
        "evidence": "data/verification/shared-currentness-assurance.json#source_families.national_qa",
    }


def build_projection_report() -> dict[str, Any]:
    assurance = load(ASSURANCE_PATH)
    manifest = load("data/services/manifest.json")
    matrix_index = matrix_currentness_index()

    standards_map_raw = load("data/shared/standards/service-ordinance-map.json")
    standards_rel_raw = load("data/shared/standards/service-relations.generated.json")
    qa_rel_raw = load("data/qa-service-relations.generated.json")
    qa_meta = load("data/qa-corpus-meta.json")

    standards_map = {
        row["service_id"]: row for row in standards_map_raw.get("relations", [])
    }
    standards_scope = {
        row["service_id"]: row
        for row in standards_rel_raw.get("service_scope_states", [])
    }
    qa_relations = {
        row["service_id"]: row for row in qa_rel_raw.get("services", [])
    }

    rows: list[dict[str, Any]] = []
    for service in manifest.get("services", []):
        config = load(service["config"])
        service_id = service["service_id"]
        rows.append(
            care_act_row(
                service,
                config,
                assurance,
                matrix_index.get((service_id, "care_insurance_act"), "NOT_ESTABLISHED"),
            )
        )
        rows.append(
            standards_row(
                service,
                config,
                assurance,
                standards_map,
                standards_scope,
                matrix_index.get((service_id, "governing_standards_ordinance"), "NOT_ESTABLISHED"),
            )
        )
        rows.append(
            qa_row(
                service,
                assurance,
                qa_relations,
                qa_meta,
                matrix_index.get((service_id, "national_qa"), "NOT_ESTABLISHED"),
            )
        )

    family_summary: dict[str, Any] = {}
    for family in TARGET_FAMILIES:
        family_rows = [row for row in rows if row["source_family"] == family]
        family_summary[family] = {
            "services": len(family_rows),
            "existing_currentness": dict(
                sorted(Counter(row["existing_currentness"] for row in family_rows).items())
            ),
            "projected_currentness": dict(
                sorted(Counter(row["projected_currentness"] for row in family_rows).items())
            ),
            "promotion_count": sum(bool(row["promotion_applied"]) for row in family_rows),
            "all_five_conditions_count": sum(
                all(row["conditions"].values()) for row in family_rows
            ),
            "explicit_promotion_gate_count": sum(
                bool(row["automatic_projection_allowed"]) for row in family_rows
            ),
        }

    return {
        "format_version": 1,
        "projection_kind": "SHARED_CURRENTNESS_SAFE_PROJECTION",
        "source": str(ASSURANCE_PATH.relative_to(ROOT)),
        "mutation": "READ_ONLY",
        "target_families": list(TARGET_FAMILIES),
        "rows": rows,
        "summary": {
            "services": len(manifest.get("services", [])),
            "cells_evaluated": len(rows),
            "promotions_recommended": sum(bool(row["promotion_applied"]) for row in rows),
            "source_family": family_summary,
        },
        "safety": {
            "writes_canonical_state": False,
            "writes_global_generated_artifacts": False,
            "changes_item_body_verification": False,
            "changes_relation_verification": False,
            "changes_human_review": False,
            "changes_publication": False,
            "changes_route_exposure": False,
        },
    }


def build_projection_index() -> dict[tuple[str, str], dict[str, Any]]:
    report = build_projection_report()
    return {
        (row["service_id"], row["source_family"]): row
        for row in report["rows"]
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--summary-only", action="store_true")
    args = parser.parse_args()
    report = build_projection_report()
    output = report["summary"] if args.summary_only else report
    print(json.dumps(output, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
