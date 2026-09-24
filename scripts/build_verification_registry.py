#!/usr/bin/env python3
"""Build a deterministic cross-layer verification registry."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUTPUT = DATA / "verification-registry.json"


def load(name: str):
    return json.loads((DATA / name).read_text(encoding="utf-8"))


def build() -> dict:
    notice_verify = load("notice-rouki25-independent-verification.json")
    notice_current = load("notice-rouki25-currentness-ledger.json")
    notice_packet = load("notice-review-packet.json")
    fee_verify = load("fee-guidance-independent-verification.json")
    fee_review = load("fee-guidance-review.json")
    rem = load("remuneration-independent-audit.json")
    rem_review = load("remuneration-review.json")
    unit = load("unit-price-independent-audit.json")
    unit_review = load("unit-price-review.json")
    ordinance = load("ordinance37-meta.json")
    care = load("care-insurance-act-meta.json")
    qa = load("qa-corpus-meta.json")
    qa_audit = load("qa-corpus-independent-audit.json")
    egov_audit = load("egov-content-independent-audit.json")
    egov_checks = {row["id"]: row for row in egov_audit.get("checks", [])}
    relation_semantic = load("relation-semantic-independent-audit.json")
    careact_relations = load("careact-internal-relation-independent-audit.json")
    cross_layer_relations = load("cross-layer-source-chain-independent-audit.json")
    remuneration_relations = load("remuneration-delegation-relation-independent-audit.json")

    notice_reviewed = sum(
        1
        for item in notice_packet.get("items", [])
        if item.get("reviewer_decision")
        and item.get("reviewed_candidate_sha256") == item.get("candidate_text_sha256")
    )
    current_counts = notice_current["final_audit_classification"]["counts"]

    layers = [
        {
            "id": "rouki25-dayservice",
            "title": "老企第25号 通所介護 22項目",
            "content_verification": {
                "status": notice_verify["result"],
                "kind": "INDEPENDENT_MACHINE_RECONSTRUCTION",
                "items": len(notice_verify.get("candidate_sha256", {})),
                "evidence": "data/notice-rouki25-independent-verification.json",
            },
            "currentness": {
                "status": notice_current["final_audit_classification"]["decision"],
                "hold_items": current_counts["HOLD"],
                "mismatch_items": current_counts["MISMATCH"],
                "coverage_end": notice_current["search_coverage"]["coverage_end"],
                "evidence": "data/notice-rouki25-currentness-ledger.json",
            },
            "monitoring": {
                "status": "ACTIVE",
                "workflow": ".github/workflows/watch-notice-rouki25-currentness.yml",
            },
            "human_review": {
                "status": "NOT_REVIEWED" if notice_reviewed == 0 else "PARTIAL",
                "reviewed_items": notice_reviewed,
                "total_items": len(notice_packet.get("items", [])),
            },
            "assurance": "INDEPENDENT_TEXT_PASS_CURRENTNESS_HOLD",
        },
        {
            "id": "rouki36-dayservice",
            "title": "老企第36号 7 通所介護費 8項目",
            "content_verification": {
                "status": "PASS" if fee_verify["audit_result"] == "TEXT_RECONSTRUCTION_PASS" else fee_verify["audit_result"],
                "kind": "INDEPENDENT_PRIMARY_SOURCE_RECONSTRUCTION",
                "items": len(fee_verify.get("items", [])),
                "verified_through": fee_verify["verified_through"],
                "evidence": "data/fee-guidance-independent-verification.json",
            },
            "currentness": {"status": "MONITORED_NOT_HUMAN_VERIFIED"},
            "monitoring": {
                "status": "ACTIVE",
                "workflow": ".github/workflows/watch-fee-guidance-currentness.yml",
            },
            "human_review": {
                "status": fee_review["review_status"],
                "reviewed_items": len(fee_review.get("reviewed_nodes", [])),
                "total_items": len(fee_verify.get("items", [])),
            },
            "assurance": "INDEPENDENT_TEXT_PASS_PLUS_WATCH",
        },
        {
            "id": "remuneration-notices",
            "title": "報酬告示19号・27号・95号",
            "content_verification": {
                "status": rem["audit_result"],
                "kind": "INDEPENDENT_MACHINE_REPARSE",
                "notice19_records": rem["observed_counts"]["notice19_records"],
                "notice27_nodes": rem["observed_counts"]["notice27_nodes"],
                "notice95_nodes": rem["observed_counts"]["notice95_nodes"],
                "evidence": "data/remuneration-independent-audit.json",
            },
            "currentness": {"status": "LIVE_SOURCE_REPARSE_SCHEDULED"},
            "monitoring": {
                "status": "ACTIVE",
                "workflow": ".github/workflows/verify-remuneration-independent.yml",
            },
            "human_review": {"status": rem_review["review_status"]},
            "assurance": "INDEPENDENT_AUDIT_PLUS_LIVE_SOURCE_REPARSE",
        },
        {
            "id": "unit-price",
            "title": "通所介護 一単位単価・地域区分",
            "content_verification": {
                "status": unit["audit_result"],
                "kind": "INDEPENDENT_MACHINE_REPARSE",
                "rate_count": unit["observed_counts"]["rate_count"],
                "explicit_assignment_count": unit["observed_counts"]["explicit_assignment_count"],
                "evidence": "data/unit-price-independent-audit.json",
            },
            "currentness": {
                "status": "LIVE_SOURCE_REPARSE_SCHEDULED",
                "effective_reference_date": unit["effective_reference_date"],
            },
            "monitoring": {
                "status": "ACTIVE",
                "workflow": ".github/workflows/verify-unit-price-independent.yml",
            },
            "human_review": {"status": unit_review["review_status"]},
            "assurance": "INDEPENDENT_AUDIT_PLUS_LIVE_SOURCE_REPARSE",
        },
        {
            "id": "ordinance37",
            "title": ordinance["law_title"] + "（省令37号）",
            "content_verification": {
                "status": egov_checks["ordinance37"]["result"],
                "kind": "INDEPENDENT_EGOV_CONTENT_REPARSE",
                "nodes": egov_checks["ordinance37"]["observed"]["nodes"],
                "articles": egov_checks["ordinance37"]["observed"]["articles"],
                "contains_relations": egov_checks["ordinance37"]["observed"]["contains_relations"],
                "evidence": "data/egov-content-independent-audit.json",
            },
            "currentness": {
                "status": "LIVE_SOURCE_REPARSE_SCHEDULED",
                "current_revision_id": ordinance["current_revision"]["law_revision_id"],
            },
            "monitoring": {
                "status": "ACTIVE",
                "workflow": ".github/workflows/verify-egov-content-independent.yml",
                "additional_workflow": ".github/workflows/verify-egov-source-freshness.yml",
            },
            "human_review": {"status": ordinance["review_status"]},
            "assurance": "INDEPENDENT_AUDIT_PLUS_LIVE_SOURCE_REPARSE",
        },
        {
            "id": "care-insurance-act",
            "title": care["law_title"],
            "content_verification": {
                "status": egov_checks["care-insurance-act"]["result"],
                "kind": "INDEPENDENT_EGOV_CONTENT_REPARSE",
                "nodes": egov_checks["care-insurance-act"]["observed"]["nodes"],
                "articles": egov_checks["care-insurance-act"]["observed"]["articles"],
                "contains_relations": egov_checks["care-insurance-act"]["observed"]["contains_relations"],
                "evidence": "data/egov-content-independent-audit.json",
            },
            "currentness": {
                "status": "LIVE_SOURCE_REPARSE_SCHEDULED",
                "current_revision_id": care["current_revision"]["law_revision_id"],
            },
            "monitoring": {
                "status": "ACTIVE",
                "workflow": ".github/workflows/verify-egov-content-independent.yml",
                "additional_workflow": ".github/workflows/verify-egov-source-freshness.yml",
            },
            "human_review": {"status": care["review_status"]},
            "assurance": "INDEPENDENT_AUDIT_PLUS_LIVE_SOURCE_REPARSE",
        },
        {
            "id": "qa-corpus",
            "title": "厚生労働省 介護サービスQ&A",
            "content_verification": {
                "status": qa_audit["audit_result"],
                "kind": qa_audit["audit_kind"],
                "rows_scanned": qa_audit["observed"]["rows_scanned"],
                "rows_included": qa_audit["observed"]["rows_included"],
                "counts_by_service": qa_audit["observed"]["counts_by_service"],
                "evidence": "data/qa-corpus-independent-audit.json",
            },
            "currentness": {
                "status": "LIVE_SOURCE_REPARSE_SCHEDULED",
                "source_sha256": qa["source_sha256"],
            },
            "monitoring": {
                "status": "ACTIVE",
                "workflow": ".github/workflows/verify-qa-corpus-independent.yml",
                "additional_workflow": ".github/workflows/verify-qa-source-freshness.yml",
            },
            "human_review": {"status": qa["review_status"]},
            "assurance": "INDEPENDENT_AUDIT_PLUS_LIVE_SOURCE_REPARSE",
        },
    ]

    relation_coverage = build_relation_coverage()
    relation_inventory = len(relation_coverage["inventory"])
    relation_verified = len(relation_coverage["verified"])
    relation_remaining = len(relation_coverage["remaining"])
    relation_lanes = relation_coverage["lanes"]

    declared_inventory = relation_semantic["coverage"]["non_contains_semantic_or_cross_layer_relations"]
    if relation_inventory != declared_inventory:
        raise ValueError(
            f"canonical semantic/cross-layer inventory changed: {relation_inventory} != {declared_inventory}"
        )

    relation_verification = {
        "status": "PASS" if relation_remaining == 0 else "PARTIAL",
        "inventory_relations": relation_inventory,
        "independently_verified_relations": relation_verified,
        "remaining_unverified_relations": relation_remaining,
        "lanes": relation_lanes,
        "automatic_promotion_allowed": False,
        "assurance": "INDEPENDENT_RELATION_AUDIT_PARTIAL" if relation_remaining else "INDEPENDENT_RELATION_AUDIT_COMPLETE",
    }

    gaps = []
    if relation_remaining:
        gaps.append(
            {
                "id": "semantic-cross-layer-relations",
                "status": "PARTIAL",
                "independently_verified": relation_verified,
                "total": relation_inventory,
                "remaining": relation_remaining,
                "note": "Remaining semantic/cross-layer relations are not independently verified and are not auto-promoted.",
            }
        )

    return {
        "format_version": 1,
        "generated_by": "scripts/build_verification_registry.py",
        "policy": "Verification layers are reported separately. Independent machine/AI audit, source freshness/currentness monitoring, and human verification are never collapsed into one status.",
        "layers": layers,
        "relation_verification": relation_verification,
        "gaps": gaps,
        "summary": {
            "layers_total": len(layers),
            "independent_audit_or_reconstruction": sum(
                1 for layer in layers
                if layer["content_verification"]["status"] == "PASS"
            ),
            "currentness_or_live_source_monitoring_active": sum(
                1 for layer in layers if layer["monitoring"]["status"] == "ACTIVE"
            ),
            "source_freshness_only_without_independent_content_audit": sum(
                1 for layer in layers if layer["assurance"] == "SOURCE_FRESHNESS_ONLY"
            ),
            "human_verified_layers": 0,
            "semantic_or_cross_layer_relations_total": relation_inventory,
            "semantic_or_cross_layer_relations_independently_verified": relation_verified,
            "semantic_or_cross_layer_relations_remaining": relation_remaining,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    rendered = json.dumps(build(), ensure_ascii=False, indent=2) + "\n"
    if args.check:
        if not OUTPUT.exists():
            raise SystemExit("verification registry missing; run builder")
        if OUTPUT.read_text(encoding="utf-8") != rendered:
            raise SystemExit("verification registry is stale; run builder")
        print("verification registry: current")
        return

    OUTPUT.write_text(rendered, encoding="utf-8")
    print(f"wrote {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
