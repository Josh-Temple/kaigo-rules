#!/usr/bin/env python3
"""Validate Worker C national-source currentness evidence and projection safety."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from national_source_currentness_projection import (
    LEDGER_PATH,
    ROOT,
    TARGET_FAMILIES,
    build_projection_report,
    load,
)

EXPECTED_BASE_SHA = "46e27f31ef618f31d45d33d7f841927ea5a564dd"


def require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def page_hash_pairs(source: dict[str, Any]) -> list[tuple[str, str]]:
    return [
        (str(page.get("url") or page.get("page") or ""), str(page.get("sha256") or ""))
        for page in source.get("pages", source.get("page_sha256", []))
    ]


def main() -> int:
    errors: list[str] = []
    ledger = load(LEDGER_PATH)

    require(
        ledger.get("assurance_kind") == "NATIONAL_SOURCE_CURRENTNESS_EVIDENCE_EXPANSION",
        "unexpected assurance_kind",
        errors,
    )
    require(ledger.get("base_main_sha") == EXPECTED_BASE_SHA, "base main SHA drifted", errors)

    policy = ledger.get("policy") or {}
    for key in (
        "item_body_verification_does_not_establish_currentness",
        "official_page_presence_alone_is_insufficient",
        "negative_search_is_not_conclusive_successor_absence_evidence",
        "comparison_or_redline_is_not_integrated_current_body",
        "source_level_currentness_does_not_broadcast_to_all_services",
        "currentness_projection_is_read_only_in_this_worker",
    ):
        require(policy.get(key) is True, f"policy boundary missing: {key}", errors)

    families = ledger.get("source_families") or {}
    require(set(families) == set(TARGET_FAMILIES), "source family set drifted", errors)

    # Delegated remuneration: exact identified document versions are pinned, but
    # currentness must remain partial until successor/latestness is independently closed.
    delegated = families["delegated_remuneration_criteria"]
    canonical_delegated = load("data/shared/remuneration-delegated/manifest.json")
    canonical_docs = {row["source_id"]: row for row in canonical_delegated.get("source_documents", [])}
    ledger_docs = {row["source_id"]: row for row in delegated.get("source_documents", [])}
    require(set(ledger_docs) == set(canonical_docs), "delegated source identity set drifted", errors)
    for source_id, canonical in canonical_docs.items():
        observed = ledger_docs.get(source_id) or {}
        require(observed.get("official_url") == canonical.get("official_url"), f"{source_id}: official URL drifted", errors)
        canonical_hashes = [(str(p.get("page")), str(p.get("sha256"))) for p in canonical.get("page_sha256", [])]
        observed_hashes = [(str(p.get("page")), str(p.get("sha256"))) for p in observed.get("page_sha256", [])]
        require(observed_hashes == canonical_hashes, f"{source_id}: page hash set drifted", errors)
    require(delegated.get("source_level_verdict") == "PARTIAL", "delegated currentness must remain PARTIAL", errors)
    require(delegated.get("service_projection_allowed") is False, "delegated service projection unexpectedly enabled", errors)
    require(
        (canonical_delegated.get("assurance") or {}).get("currentness") == "NOT_ESTABLISHED",
        "canonical delegated currentness was promoted outside Worker C",
        errors,
    )

    # Remuneration notification: source snapshots may be strong item-body evidence,
    # but every canonical source currently disclaims a currentness claim.
    remuneration = families["remuneration_notification"]
    canonical_rem = load("data/shared/remuneration-notification/body-fingerprints.json")
    canonical_rem_docs = {row["source_id"]: row for row in canonical_rem.get("source_documents", [])}
    ledger_rem_docs = {row["source_id"]: row for row in remuneration.get("source_documents", [])}
    require(set(ledger_rem_docs) == set(canonical_rem_docs), "remuneration source identity set drifted", errors)
    require(remuneration.get("source_count") == len(canonical_rem_docs), "remuneration source count drifted", errors)
    for source_id, canonical in canonical_rem_docs.items():
        observed = ledger_rem_docs.get(source_id) or {}
        require(observed.get("document_key") == canonical.get("document_key"), f"{source_id}: document identity drifted", errors)
        require(page_hash_pairs(observed) == page_hash_pairs(canonical), f"{source_id}: page hash set drifted", errors)
        require(canonical.get("currentness_claimed") is False, f"{source_id}: canonical source unexpectedly claims currentness", errors)
        require(observed.get("currentness_claimed") is False, f"{source_id}: ledger unexpectedly claims currentness", errors)
    require(remuneration.get("source_level_verdict") == "PARTIAL", "remuneration currentness must remain PARTIAL", errors)
    require(remuneration.get("service_projection_allowed") is False, "remuneration service projection unexpectedly enabled", errors)

    # Fee guidance: comparison/redline/locator evidence must never masquerade as
    # an integrated current body.
    fee = families["fee_calculation_guidance"]
    canonical_fee = load("data/shared/fee-guidance/source-registry.json")
    canonical_fee_docs = {row["id"]: row for row in canonical_fee.get("sources", [])}
    ledger_fee_docs = {row["source_id"]: row for row in fee.get("source_documents", [])}
    require(set(ledger_fee_docs) == set(canonical_fee_docs), "fee-guidance source identity set drifted", errors)
    require(fee.get("integrated_current_body_established") is False, "fee guidance integrated current body was inferred", errors)
    require(fee.get("source_level_verdict") == "NOT_ESTABLISHED", "fee guidance currentness improperly promoted", errors)
    require(fee.get("service_projection_allowed") is False, "fee guidance service projection unexpectedly enabled", errors)
    for source_id, canonical in canonical_fee_docs.items():
        require(canonical.get("currentness") == "NOT_ESTABLISHED", f"{source_id}: fee source unexpectedly claims currentness", errors)
        observed = ledger_fee_docs.get(source_id) or {}
        require(observed.get("source_kind") == canonical.get("source_kind"), f"{source_id}: source kind drifted", errors)
        require(observed.get("warning") == canonical.get("warning"), f"{source_id}: safety warning drifted", errors)

    # Parallel-worker evidence is informative only. It must not become canonical
    # currentness before integration and independent currentness proof.
    unit = families["unit_price_regional_classification"]
    unit_candidate = unit.get("candidate_source_identity") or {}
    require(unit.get("parallel_worker_candidate_only") is True, "unit-price candidate lost candidate-only boundary", errors)
    require(unit_candidate.get("currentness_claim") is False, "unit-price candidate unexpectedly claims currentness", errors)
    require(unit.get("source_level_verdict") == "NOT_ESTABLISHED", "unit-price currentness promoted from parallel branch", errors)
    require(unit.get("service_projection_allowed") is False, "unit-price service projection unexpectedly enabled", errors)

    other = families["other_national_manuals_forms"]
    require(other.get("parallel_worker_candidate_only") is True, "other-national candidate lost candidate-only boundary", errors)
    for source in other.get("candidate_currentness_claims", []):
        require(source.get("currentness_claimed") is False, f"{source.get('canonical_source_id')}: candidate currentness unexpectedly claimed", errors)
    require(other.get("source_level_verdict") == "NOT_ESTABLISHED", "other-national currentness improperly promoted", errors)
    require(other.get("service_projection_allowed") is False, "other-national service projection unexpectedly enabled", errors)

    qa = families["national_qa"]
    require(qa.get("source_level_verdict") == "CURRENT_COMPILATION_ONLY", "Q&A compilation boundary drifted", errors)
    require(
        qa.get("individual_item_currentness") == "NOT_ESTABLISHED_BY_COMPILATION_FRESHNESS",
        "Q&A individual item currentness was inferred from compilation freshness",
        errors,
    )
    require(qa.get("service_projection_allowed") is False, "Q&A service projection unexpectedly enabled", errors)

    notice = families["standards_interpretation_notice"]
    require(notice.get("source_level_verdict") == "HOLD_PRESERVED", "standards-interpretation HOLD was weakened", errors)
    require(notice.get("service_projection_allowed") is False, "standards-interpretation service projection unexpectedly enabled", errors)

    report = build_projection_report()
    expected_services = len(load("data/services/manifest.json").get("services", []))
    require(
        report["summary"]["cells_evaluated"] == expected_services * len(TARGET_FAMILIES),
        "projection did not cover every service x target-family cell",
        errors,
    )
    require(report["summary"]["promotions_recommended"] == 0, "unsupported service currentness promotion recommended", errors)
    for row in report.get("rows", []):
        require(
            row.get("projected_currentness") == row.get("existing_currentness"),
            f"{row.get('service_id')}/{row.get('source_family')}: currentness changed in read-only projection",
            errors,
        )
        if row.get("item_body_state") == "PASS":
            require(
                row.get("promotion_recommended") is False,
                f"{row.get('service_id')}/{row.get('source_family')}: item-body PASS leaked into currentness",
                errors,
            )

    safety = ledger.get("safety") or {}
    for key in (
        "global_generated_artifacts_updated",
        "canonical_currentness_states_mutated",
        "source_currentness_broadcast_to_all_services",
        "item_body_promoted",
        "relation_verification_promoted",
        "human_review_promoted",
        "publication_promoted",
        "route_exposure_promoted",
    ):
        require(safety.get(key) is False, f"safety boundary broken: {key}", errors)

    output = {
        "format_version": 1,
        "validation_kind": "NATIONAL_SOURCE_CURRENTNESS_EVIDENCE_EXPANSION",
        "result": "PASS" if not errors else "FAIL",
        "errors": errors,
        "observed": {
            "services": expected_services,
            "cells_evaluated": report["summary"]["cells_evaluated"],
            "promotions_recommended": report["summary"]["promotions_recommended"],
            "delegated_sources": len(canonical_docs),
            "remuneration_sources": len(canonical_rem_docs),
            "fee_guidance_sources": len(canonical_fee_docs),
        },
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
