#!/usr/bin/env python3
"""Read-only evaluator for the national-source currentness expansion worker."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
LEDGER_PATH = ROOT / "data/verification/national-source-currentness-expansion.json"
MATRIX_PATH = ROOT / "data/database-coverage-matrix.generated.json"

TARGET_FAMILIES = (
    "delegated_remuneration_criteria",
    "remuneration_notification",
    "fee_calculation_guidance",
    "unit_price_regional_classification",
    "standards_interpretation_notice",
    "national_qa",
    "other_national_manuals_forms",
)

CURRENT_SOURCE_VERDICTS = {"CURRENT", "CURRENT_BY_CORPUS"}


def load(path: str | Path) -> Any:
    target = Path(path)
    if not target.is_absolute():
        target = ROOT / target
    return json.loads(target.read_text(encoding="utf-8"))


def matrix_rows() -> list[dict[str, Any]]:
    matrix = load(MATRIX_PATH)
    rows: list[dict[str, Any]] = []
    for service in matrix.get("services", []):
        for family in service.get("source_families", []):
            if family.get("source_family") in TARGET_FAMILIES:
                rows.append(
                    {
                        "service_id": service.get("service_id"),
                        "source_family": family.get("source_family"),
                        "service_scope": family.get("service_scope") or {},
                        "ingestion": family.get("ingestion") or {},
                        "item_body_verification": family.get("item_body_verification") or {},
                        "currentness": family.get("currentness") or {},
                    }
                )
    return rows


def delegated_applicability() -> dict[str, dict[str, Any]]:
    doc = load("data/shared/remuneration-delegated/service-applicability.json")
    return {row["service_id"]: row for row in doc.get("services", [])}


def fee_applicability() -> dict[str, dict[str, Any]]:
    doc = load("data/shared/fee-guidance/service-applicability.json")
    return {row["service_id"]: row for row in doc.get("services", [])}


def conditions_for(
    row: dict[str, Any],
    source: dict[str, Any],
    delegated: dict[str, dict[str, Any]],
    fee: dict[str, dict[str, Any]],
) -> dict[str, bool]:
    family = row["source_family"]
    service_id = row["service_id"]
    source_verdict = source.get("source_level_verdict")
    source_current = source_verdict in CURRENT_SOURCE_VERDICTS

    canonical_fixed = bool(
        source.get("canonical_manifest")
        or source.get("canonical_fingerprints")
        or source.get("source_registry")
        or source.get("inherited_evidence")
    )
    exact_version_fixed = False
    effective_metadata = False
    amendment_chain = False
    successor_current = False
    reference_aligned = False
    no_ambiguity = False
    applicability = False

    if family == "delegated_remuneration_criteria":
        canonical_fixed = True
        exact_version_fixed = all(
            bool(doc.get("official_url")) and bool(doc.get("page_sha256"))
            for doc in source.get("source_documents", [])
        )
        app = delegated.get(service_id) or {}
        applicability = app.get("applicability_state") in {"MAPPED", "NOT_APPLICABLE"}
        # The source bodies are pinned, but latestness/successor absence is not.
        no_ambiguity = True
    elif family == "remuneration_notification":
        canonical_fixed = True
        exact_version_fixed = all(
            bool(doc.get("document_key")) and bool(doc.get("pages"))
            for doc in source.get("source_documents", [])
        )
        # Existing source snapshots do not independently prove the successor chain.
        no_ambiguity = True
    elif family == "fee_calculation_guidance":
        canonical_fixed = True
        exact_version_fixed = all(bool(doc.get("official_url")) for doc in source.get("source_documents", []))
        no_ambiguity = bool(source.get("integrated_current_body_established"))
        app = fee.get(service_id) or {}
        applicability = (
            app.get("state") == "NOT_APPLICABLE"
            or (app.get("assurance") or {}).get("service_applicability_verification")
            in {"PASS", "ESTABLISHED", "VERIFIED"}
        )
    elif family == "national_qa":
        canonical_fixed = True
        exact_version_fixed = True
        no_ambiguity = False
        applicability = False
    elif family in {"unit_price_regional_classification", "other_national_manuals_forms"}:
        # Parallel-worker candidate evidence is deliberately not canonical main evidence.
        canonical_fixed = False
        exact_version_fixed = False
        no_ambiguity = False
    elif family == "standards_interpretation_notice":
        canonical_fixed = True
        no_ambiguity = False

    scope_defined = (row.get("service_scope") or {}).get("state") == "SCOPE_DEFINED"

    return {
        "canonical_source_identity_fixed": canonical_fixed,
        "exact_version_identity_fixed": exact_version_fixed,
        "issue_revision_effective_metadata_established": effective_metadata,
        "predecessor_successor_amendment_chain_established": amendment_chain,
        "successor_absence_or_current_revision_status_established": successor_current,
        "service_scope_defined": scope_defined,
        "service_applicability_established": applicability,
        "service_reference_aligned_to_current_source": reference_aligned and source_current,
        "no_historical_or_comparison_body_ambiguity": no_ambiguity,
    }


def build_projection_report() -> dict[str, Any]:
    ledger = load(LEDGER_PATH)
    delegated = delegated_applicability()
    fee = fee_applicability()

    rows: list[dict[str, Any]] = []
    for row in matrix_rows():
        source = (ledger.get("source_families") or {}).get(row["source_family"], {})
        conditions = conditions_for(row, source, delegated, fee)
        existing = (row.get("currentness") or {}).get("state") or "NOT_ESTABLISHED"
        source_current = source.get("source_level_verdict") in CURRENT_SOURCE_VERDICTS
        allowed = source.get("service_projection_allowed") is True
        eligible = source_current and allowed and all(conditions.values())
        projected = "PASS" if eligible else existing
        rows.append(
            {
                "service_id": row["service_id"],
                "source_family": row["source_family"],
                "source_level_verdict": source.get("source_level_verdict"),
                "existing_currentness": existing,
                "projected_currentness": projected,
                "promotion_recommended": eligible and existing != "PASS",
                "item_body_state": (row.get("item_body_verification") or {}).get("state"),
                "conditions": conditions,
                "blockers": [key for key, value in conditions.items() if not value],
                "service_projection_allowed": allowed,
            }
        )

    family_summary: dict[str, Any] = {}
    for family in TARGET_FAMILIES:
        subset = [row for row in rows if row["source_family"] == family]
        family_summary[family] = {
            "services": len(subset),
            "existing_currentness": dict(sorted(Counter(row["existing_currentness"] for row in subset).items())),
            "projected_currentness": dict(sorted(Counter(row["projected_currentness"] for row in subset).items())),
            "promotions_recommended": sum(bool(row["promotion_recommended"]) for row in subset),
        }

    return {
        "format_version": 1,
        "projection_kind": "NATIONAL_SOURCE_CURRENTNESS_READ_ONLY_PROJECTION",
        "source": str(LEDGER_PATH.relative_to(ROOT)),
        "mutation": "READ_ONLY",
        "target_families": list(TARGET_FAMILIES),
        "rows": rows,
        "summary": {
            "cells_evaluated": len(rows),
            "promotions_recommended": sum(bool(row["promotion_recommended"]) for row in rows),
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


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--summary-only", action="store_true")
    args = parser.parse_args()
    report = build_projection_report()
    print(json.dumps(report["summary"] if args.summary_only else report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
