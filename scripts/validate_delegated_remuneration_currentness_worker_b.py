#!/usr/bin/env python3
"""Validate Worker B delegated-remuneration residual currentness closure."""
from __future__ import annotations

import json
from pathlib import Path

from build_delegated_remuneration_currentness_worker_b import (
    PRIOR_PROMOTED_SERVICE_IDS,
    build,
)

ROOT = Path(__file__).resolve().parents[1]
SHARED = ROOT / "data/shared/remuneration-delegated"
DECISIONS = ROOT / "data/verification/delegated-remuneration-currentness-worker-b.json"
NOTICE27_EVIDENCE = SHARED / "notice27-currentness-evidence.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    errors: list[str] = []
    applicability = load(SHARED / "service-applicability.json")
    receipt = load(SHARED / "item-body-verification.json")
    contract = load(SHARED / "currentness-source-contract.json")
    evidence27 = load(NOTICE27_EVIDENCE)
    sources = load(ROOT / "data/sources.json")
    committed = load(DECISIONS)
    rebuilt = build()

    if committed != rebuilt:
        errors.append(
            "committed decision artifact is not reproducible from canonical inputs"
        )

    rows = {
        row["service_id"]: row for row in applicability.get("services", [])
    }
    receipt_sources = {
        row["source_id"]: row for row in receipt.get("source_verifications", [])
    }
    contracts = {
        row["canonical_source_id"]: row
        for row in contract.get("source_contracts", [])
    }
    source_registry = {row["id"]: row for row in sources}
    promotions = committed.get("promotions", [])
    promotion_ids = {row["service_id"] for row in promotions}
    new_promotions = [
        row for row in promotions if row.get("newly_promoted") is True
    ]
    new_ids = {row["service_id"] for row in new_promotions}
    holds = committed.get("holds", [])
    residual = committed.get("residual_decisions", [])

    if len(rows) != 39:
        errors.append(f"service applicability row count drifted: {len(rows)} != 39")
    if len(promotions) != 37:
        errors.append(
            f"currentness PASS cell count drifted: {len(promotions)} != 37"
        )
    if len(new_promotions) != 22:
        errors.append(
            f"new residual promotion count drifted: {len(new_promotions)} != 22"
        )
    if sum(1 for row in holds if row.get("decision") == "DEFER") != 0:
        errors.append(
            "no applicable delegated-remuneration cell may remain deferred "
            "after Notice 27 closure"
        )
    if (
        sum(
            1
            for row in holds
            if row.get("decision") == "NOT_APPLICABLE_PRESERVED"
        )
        != 2
    ):
        errors.append("NOT_APPLICABLE hold count must remain 2")

    expected_na = {
        service_id
        for service_id, row in rows.items()
        if row.get("applicability_state") == "NOT_APPLICABLE"
    }
    expected_na_ids = {
        "specific-welfare-equipment-sale",
        "specific-preventive-welfare-equipment-sale",
    }
    if expected_na != expected_na_ids:
        errors.append(f"unexpected NOT_APPLICABLE set: {sorted(expected_na)}")
    if expected_na & promotion_ids:
        errors.append("NOT_APPLICABLE service was promoted")

    mapped_ids = {
        service_id
        for service_id, row in rows.items()
        if row.get("applicability_state") == "MAPPED"
    }
    expected_residual = mapped_ids - PRIOR_PROMOTED_SERVICE_IDS
    if new_ids != expected_residual:
        errors.append(
            "newly promoted set differs from the 22-cell starting residual: "
            f"new={sorted(new_ids)} expected={sorted(expected_residual)}"
        )
    if PRIOR_PROMOTED_SERVICE_IDS - promotion_ids:
        errors.append(
            "one or more existing 15 READY delegated-remuneration cells regressed"
        )

    eligible_sources = {
        source_id
        for source_id, row in contracts.items()
        if row.get("promotion_eligible") is True
        and row.get("currentness_state") == "PASS"
    }
    expected_eligible = {
        "mhlw-fee-criteria95-current",
        "mhlw-fee-facility-criteria96-current",
        "mhlw-fee-notice27-base",
    }
    if eligible_sources != expected_eligible:
        errors.append(
            f"unexpected promotion-eligible source set: {sorted(eligible_sources)}"
        )

    notice27 = contracts.get("mhlw-fee-notice27-base") or {}
    if (
        notice27.get("promotion_eligible") is not True
        or notice27.get("currentness_state") != "PASS"
    ):
        errors.append("Notice 27 currentness closure is not explicit PASS")
    if (
        notice27.get("closure_evidence")
        != "data/shared/remuneration-delegated/notice27-currentness-evidence.json"
    ):
        errors.append("Notice 27 closure evidence pointer missing")
    if (
        evidence27.get("decision") != "PASS"
        or evidence27.get("promotion_eligible") is not True
    ):
        errors.append("Notice 27 evidence artifact does not record PASS")
    if (
        (evidence27.get("current_body_identity") or {}).get("body_identity_match")
        != "PASS"
    ):
        errors.append(
            "Notice 27 current body identity is not matched to repository "
            "item-body evidence"
        )

    expected_registry_status = {
        "mhlw-fee-criteria95-current": "current_official_source",
        "mhlw-fee-facility-criteria96-current": "current_official_source",
        "mhlw-fee-notice27-base": "current_official_source",
    }
    for source_id, expected_status in expected_registry_status.items():
        registry_row = source_registry.get(source_id) or {}
        if registry_row.get("status") != expected_status:
            errors.append(
                f"{source_id}: canonical source registry status drifted "
                f"{registry_row.get('status')} != {expected_status}"
            )
        source_contract = contracts.get(source_id) or {}
        if source_contract.get("official_source_url") != registry_row.get("url"):
            errors.append(
                f"{source_id}: source contract URL differs from canonical "
                "source registry"
            )

    amendment87 = source_registry.get("mhlw-r8-fee-amendment87") or {}
    if amendment87.get("publisher") != "厚生労働省":
        errors.append("R8 amendment 87 official publisher identity missing")
    source95_lineage = (
        contracts.get("mhlw-fee-criteria95-current") or {}
    ).get("amendment_lineage") or {}
    if (
        source95_lineage.get("latest_confirmed_amendment")
        != "令和8年厚生労働省告示第87号"
    ):
        errors.append("Notice 95 latest confirmed amendment identity drifted")
    if source95_lineage.get("effective_date") != "2026-06-01":
        errors.append("Notice 95 R8 amendment effective date drifted")

    for source_id in eligible_sources:
        source_contract = contracts[source_id]
        receipt_source = receipt_sources.get(source_id) or {}
        if (
            source_contract.get("official_source_url")
            != receipt_source.get("official_url")
        ):
            errors.append(
                f"{source_id}: currentness source URL differs from item-body "
                "source URL"
            )
        snapshots = (source_contract.get("version_model") or {}).get(
            "page_snapshots"
        )
        if snapshots != receipt_source.get("page_snapshots"):
            errors.append(
                f"{source_id}: currentness snapshot identity differs from "
                "item-body snapshot identity"
            )
        if (
            source_contract.get("repository_source_status")
            != "current_official_source"
        ):
            errors.append(
                f"{source_id}: promotion source is not registered as "
                "current_official_source"
            )

    for decision in promotions:
        service_id = decision["service_id"]
        canonical = rows.get(service_id) or {}
        expected_nodes = list(canonical.get("mapped_node_ids") or []) + list(
            canonical.get("compatibility_subnode_ids") or []
        )
        if canonical.get("applicability_state") != "MAPPED":
            errors.append(f"{service_id}: promotion lacks MAPPED applicability")
        if (
            (canonical.get("assurance") or {}).get("item_body_verification")
            != "PASS"
        ):
            errors.append(f"{service_id}: promotion lacks item-body PASS")
        if decision.get("mapped_node_ids") != expected_nodes:
            errors.append(
                f"{service_id}: decision node set differs from canonical "
                "service mapping"
            )
        if (
            (decision.get("applicability_proof") or {}).get(
                "inherited_from_sibling_service"
            )
            is not False
        ):
            errors.append(
                f"{service_id}: regular/preventive inheritance is not allowed"
            )
        expected_evidence = (
            "data/shared/remuneration-delegated/"
            f"service-applicability.json#{service_id}"
        )
        if expected_evidence not in (
            decision.get("applicability_proof") or {}
        ).get("evidence", []):
            errors.append(
                f"{service_id}: service-specific applicability evidence missing"
            )
        mapped_sources = set(decision.get("mapped_source_ids") or [])
        if not mapped_sources or not mapped_sources <= eligible_sources:
            errors.append(
                f"{service_id}: promotion includes non-current source identity"
            )
        if decision.get("source_identity_matches_item_body_source") is not True:
            errors.append(
                f"{service_id}: source identity equality is not asserted"
            )
        if (
            decision.get("projected_currentness_state") != "PASS"
            or decision.get("promotion_applied") is not True
        ):
            errors.append(
                f"{service_id}: promotion state is not explicit PASS"
            )
        unchanged = decision.get("unchanged_axes") or {}
        if unchanged != {
            "relation_verification": "NOT_ESTABLISHED",
            "human_review": "NOT_REVIEWED",
            "publication": "BLOCKED",
            "route_exposure": "BLOCKED",
        }:
            errors.append(f"{service_id}: unrelated assurance axes changed")

    if len(residual) != 22:
        errors.append(
            f"residual decision artifact must contain 22 starting cells, "
            f"got {len(residual)}"
        )
    for row in residual:
        if row.get("starting_state") != "BLOCKED_CURRENTNESS":
            errors.append(
                f"{row.get('service_id')}: residual starting state drift"
            )
        if row.get("decision") != "PROMOTE_CURRENTNESS":
            errors.append(
                f"{row.get('service_id')}: residual cell did not close after "
                "source-level PASS"
            )
        if row.get("currentness_decision") != "PASS":
            errors.append(
                f"{row.get('service_id')}: residual cell currentness is not PASS"
            )

    summary = committed.get("summary") or {}
    expected_summary = {
        "applicable_cells": 37,
        "not_applicable_cells": 2,
        "starting_ready_cells": 15,
        "starting_deferred_applicable_cells": 22,
        "currentness_pass_cells": 37,
        "newly_promoted_cells": 22,
        "deferred_applicable_cells": 0,
        "projected_ready_increase": 22,
        "projected_ready_count_after_integration": 37,
    }
    for key, value in expected_summary.items():
        if summary.get(key) != value:
            errors.append(
                f"summary {key} drifted: {summary.get(key)} != {value}"
            )

    safety = committed.get("safety") or {}
    if any(
        safety.get(key) is not False
        for key in (
            "relation_verification_promoted",
            "human_review_promoted",
            "publication_writeback",
            "route_auto_enable",
        )
    ):
        errors.append(
            "currentness decision artifact crossed a protected assurance boundary"
        )

    if errors:
        raise SystemExit(
            "\n".join(f"ERROR: {message}" for message in errors)
        )

    print(
        "delegated remuneration residual currentness: PASS "
        "(15 prior READY preserved, 22 residual cells promoted, "
        "0 applicable deferred, 2 NOT_APPLICABLE preserved)"
    )


if __name__ == "__main__":
    main()
