#!/usr/bin/env python3
"""Validate Worker B delegated-remuneration bounded currentness decisions."""
from __future__ import annotations

import json
from pathlib import Path

from build_delegated_remuneration_currentness_worker_b import build

ROOT = Path(__file__).resolve().parents[1]
SHARED = ROOT / "data/shared/remuneration-delegated"
DECISIONS = ROOT / "data/verification/delegated-remuneration-currentness-worker-b.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    errors: list[str] = []
    applicability = load(SHARED / "service-applicability.json")
    receipt = load(SHARED / "item-body-verification.json")
    contract = load(SHARED / "currentness-source-contract.json")
    committed = load(DECISIONS)
    rebuilt = build()

    if committed != rebuilt:
        errors.append("committed decision artifact is not reproducible from canonical inputs")

    rows = {row["service_id"]: row for row in applicability.get("services", [])}
    receipt_sources = {
        row["source_id"]: row for row in receipt.get("source_verifications", [])
    }
    contracts = {
        row["canonical_source_id"]: row for row in contract.get("source_contracts", [])
    }
    promotions = committed.get("promotions", [])
    promotion_ids = {row["service_id"] for row in promotions}
    holds = committed.get("holds", [])

    if len(rows) != 39:
        errors.append(f"service applicability row count drifted: {len(rows)} != 39")
    if len(promotions) != 15:
        errors.append(f"bounded promotion count drifted: {len(promotions)} != 15")
    if sum(1 for row in holds if row.get("decision") == "DEFER") != 22:
        errors.append("deferred applicable cell count must remain 22")
    if sum(1 for row in holds if row.get("decision") == "NOT_APPLICABLE_PRESERVED") != 2:
        errors.append("NOT_APPLICABLE hold count must remain 2")

    expected_na = {
        service_id for service_id, row in rows.items()
        if row.get("applicability_state") == "NOT_APPLICABLE"
    }
    if expected_na != {"specific-welfare-equipment-sale", "specific-preventive-welfare-equipment-sale"}:
        errors.append(f"unexpected NOT_APPLICABLE set: {sorted(expected_na)}")
    if expected_na & promotion_ids:
        errors.append("NOT_APPLICABLE service was promoted")

    eligible_sources = {
        source_id for source_id, row in contracts.items()
        if row.get("promotion_eligible") is True and row.get("currentness_state") == "PASS"
    }
    if eligible_sources != {
        "mhlw-fee-criteria95-current",
        "mhlw-fee-facility-criteria96-current",
    }:
        errors.append(f"unexpected promotion-eligible source set: {sorted(eligible_sources)}")
    blocked27 = contracts.get("mhlw-fee-notice27-base") or {}
    if blocked27.get("promotion_eligible") is not False or blocked27.get("currentness_state") != "BLOCKED":
        errors.append("Notice 27 must remain fail-closed")

    for source_id in eligible_sources:
        source_contract = contracts[source_id]
        receipt_source = receipt_sources.get(source_id) or {}
        if source_contract.get("official_source_url") != receipt_source.get("official_url"):
            errors.append(f"{source_id}: currentness source URL differs from item-body source URL")
        snapshots = (source_contract.get("version_model") or {}).get("page_snapshots")
        if snapshots != receipt_source.get("page_snapshots"):
            errors.append(f"{source_id}: currentness snapshot identity differs from item-body snapshot identity")
        if source_contract.get("repository_source_status") != "current_official_source":
            errors.append(f"{source_id}: promotion source is not registered as current_official_source")

    for decision in promotions:
        service_id = decision["service_id"]
        canonical = rows.get(service_id) or {}
        expected_nodes = list(canonical.get("mapped_node_ids") or []) + list(canonical.get("compatibility_subnode_ids") or [])
        if canonical.get("applicability_state") != "MAPPED":
            errors.append(f"{service_id}: promotion lacks MAPPED applicability")
        if (canonical.get("assurance") or {}).get("item_body_verification") != "PASS":
            errors.append(f"{service_id}: promotion lacks item-body PASS")
        if decision.get("mapped_node_ids") != expected_nodes:
            errors.append(f"{service_id}: decision node set differs from canonical service mapping")
        if (decision.get("applicability_proof") or {}).get("inherited_from_sibling_service") is not False:
            errors.append(f"{service_id}: regular/preventive inheritance is not allowed")
        expected_evidence = f"data/shared/remuneration-delegated/service-applicability.json#{service_id}"
        if expected_evidence not in (decision.get("applicability_proof") or {}).get("evidence", []):
            errors.append(f"{service_id}: service-specific applicability evidence missing")
        mapped_sources = set(decision.get("mapped_source_ids") or [])
        if not mapped_sources or not mapped_sources <= eligible_sources:
            errors.append(f"{service_id}: promotion includes non-current source identity")
        if "mhlw-fee-notice27-base" in mapped_sources:
            errors.append(f"{service_id}: Notice 27 dependent cell was promoted")
        if decision.get("source_identity_matches_item_body_source") is not True:
            errors.append(f"{service_id}: source identity equality is not asserted")
        if decision.get("projected_currentness_state") != "PASS" or decision.get("promotion_applied") is not True:
            errors.append(f"{service_id}: promotion state is not explicit PASS")
        unchanged = decision.get("unchanged_axes") or {}
        if unchanged != {
            "relation_verification": "NOT_ESTABLISHED",
            "human_review": "NOT_REVIEWED",
            "publication": "BLOCKED",
            "route_exposure": "BLOCKED",
        }:
            errors.append(f"{service_id}: unrelated assurance axes changed")

    for hold in holds:
        service_id = hold["service_id"]
        if hold.get("decision") == "DEFER" and service_id in promotion_ids:
            errors.append(f"{service_id}: deferred cell also appears in promotions")
        if "mhlw-fee-notice27-base" in (hold.get("mapped_source_ids") or []):
            if "mhlw-fee-notice27-base" not in (hold.get("blocked_source_ids") or []):
                errors.append(f"{service_id}: Notice 27 hold lacks exact blocked source identity")

    summary = committed.get("summary") or {}
    if summary.get("applicable_cells") != 37 or summary.get("not_applicable_cells") != 2:
        errors.append("summary applicability counts drifted")
    if summary.get("projected_ready_increase") != len(promotions):
        errors.append("projected READY increase must equal the bounded promoted subset")

    safety = committed.get("safety") or {}
    if any(safety.get(key) is not False for key in (
        "relation_verification_promoted",
        "human_review_promoted",
        "publication_writeback",
        "route_auto_enable",
    )):
        errors.append("currentness decision artifact crossed a protected assurance boundary")

    if errors:
        raise SystemExit("\n".join(f"ERROR: {message}" for message in errors))

    print(
        "delegated remuneration bounded currentness: PASS "
        f"({len(promotions)} promoted, 22 deferred, 2 NOT_APPLICABLE preserved)"
    )


if __name__ == "__main__":
    main()
