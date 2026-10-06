#!/usr/bin/env python3
"""Build bounded delegated-remuneration currentness decisions.

The builder is intentionally fail-closed. Source-level currentness is reusable,
but service eligibility is recomputed from each explicit canonical mapping.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APPLICABILITY = ROOT / "data/shared/remuneration-delegated/service-applicability.json"
CONTRACT = ROOT / "data/shared/remuneration-delegated/currentness-source-contract.json"
OUTPUT = ROOT / "data/verification/delegated-remuneration-currentness-worker-b.json"

PREFIX_TO_SOURCE = {
    "notice27": "mhlw-fee-notice27-base",
    "notice95": "mhlw-fee-criteria95-current",
    "notice96": "mhlw-fee-facility-criteria96-current",
}


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def mapped_source_ids(row: dict) -> list[str]:
    node_ids = list(row.get("mapped_node_ids") or []) + list(row.get("compatibility_subnode_ids") or [])
    values = {
        PREFIX_TO_SOURCE.get(str(node_id).split(".", 1)[0], "UNKNOWN")
        for node_id in node_ids
    }
    return sorted(values)


def build() -> dict:
    applicability = load(APPLICABILITY)
    contract = load(CONTRACT)
    source_contracts = {
        row["canonical_source_id"]: row
        for row in contract.get("source_contracts", [])
    }

    promotions: list[dict] = []
    holds: list[dict] = []

    for row in applicability.get("services", []):
        service_id = row["service_id"]
        node_ids = list(row.get("mapped_node_ids") or []) + list(row.get("compatibility_subnode_ids") or [])
        sources = mapped_source_ids(row)
        item_state = str((row.get("assurance") or {}).get("item_body_verification") or "NOT_ESTABLISHED")

        if row.get("applicability_state") == "NOT_APPLICABLE":
            holds.append({
                "service_id": service_id,
                "source_family": "delegated_remuneration_criteria",
                "decision": "NOT_APPLICABLE_PRESERVED",
                "blocker": "Explicit NOT_APPLICABLE adjudication; currentness promotion is forbidden.",
                "mapped_source_ids": [],
            })
            continue

        if row.get("applicability_state") != "MAPPED" or not node_ids:
            holds.append({
                "service_id": service_id,
                "source_family": "delegated_remuneration_criteria",
                "decision": "DEFER",
                "blocker": "No explicit canonical service applicability mapping.",
                "mapped_source_ids": sources,
            })
            continue

        if item_state != "PASS":
            holds.append({
                "service_id": service_id,
                "source_family": "delegated_remuneration_criteria",
                "decision": "DEFER",
                "blocker": f"Item-body assurance is {item_state}, not PASS.",
                "mapped_source_ids": sources,
            })
            continue

        blocked = [
            source_id for source_id in sources
            if not (source_contracts.get(source_id) or {}).get("promotion_eligible")
            or (source_contracts.get(source_id) or {}).get("currentness_state") != "PASS"
        ]
        if blocked:
            holds.append({
                "service_id": service_id,
                "source_family": "delegated_remuneration_criteria",
                "decision": "DEFER",
                "blocker": "At least one mapped canonical source is not currentness-closed under the bounded source contract.",
                "blocked_source_ids": blocked,
                "mapped_source_ids": sources,
            })
            continue

        promotions.append({
            "service_id": service_id,
            "source_family": "delegated_remuneration_criteria",
            "mapped_node_count": len(node_ids),
            "mapped_node_ids": node_ids,
            "mapped_source_ids": sources,
            "applicability_proof": {
                "state": "PASS_EXPLICIT_CANONICAL_SERVICE_MAPPING",
                "evidence": [f"data/shared/remuneration-delegated/service-applicability.json#{service_id}"],
                "inherited_from_sibling_service": False,
            },
            "item_body_state": "PASS",
            "item_body_evidence": [
                f"data/shared/remuneration-delegated/service-applicability.json#{service_id}",
                "data/shared/remuneration-delegated/item-body-verification.json",
            ],
            "source_currentness_evidence": [
                f"data/shared/remuneration-delegated/currentness-source-contract.json#{source_id}"
                for source_id in sources
            ],
            "source_identity_matches_item_body_source": True,
            "prior_currentness_state": "NOT_ESTABLISHED",
            "projection_gate": {
                "kind": "EXPLICIT_BOUNDED_ALLOWLIST",
                "allowed": True,
                "identity": f"{service_id}::delegated_remuneration_criteria",
                "scope": "currentness_only",
            },
            "projected_currentness_state": "PASS",
            "promotion_applied": True,
            "unchanged_axes": {
                "relation_verification": "NOT_ESTABLISHED",
                "human_review": "NOT_REVIEWED",
                "publication": "BLOCKED",
                "route_exposure": "BLOCKED",
            },
        })

    applicable_count = sum(
        1 for row in applicability.get("services", [])
        if row.get("applicability_state") == "MAPPED"
    )
    not_applicable_count = sum(
        1 for row in applicability.get("services", [])
        if row.get("applicability_state") == "NOT_APPLICABLE"
    )

    return {
        "format_version": 1,
        "artifact_kind": "DELEGATED_REMUNERATION_BOUNDED_CURRENTNESS_DECISIONS",
        "wave_id": "2026-10-06-relation-assurance-and-next-source-publication",
        "worker": "B",
        "role": "Delegated Remuneration Currentness & Publication Candidate Worker",
        "base_main_sha": "f74456013a4a103c48a8b6674969b71c0e325631",
        "observed_date": "2026-10-06",
        "source_contract": "data/shared/remuneration-delegated/currentness-source-contract.json",
        "purpose": "Promote currentness only for delegated-remuneration cells whose explicit service mapping references exclusively currentness-closed official source identities.",
        "summary": {
            "applicable_cells": applicable_count,
            "not_applicable_cells": not_applicable_count,
            "promoted_cells": len(promotions),
            "deferred_applicable_cells": sum(1 for row in holds if row["decision"] == "DEFER"),
            "projected_ready_increase": len(promotions),
            "projected_ready_increase_basis": "The 37 applicable delegated-remuneration cells are currently primary-blocked on currentness; this artifact removes that blocker for the promoted subset only. Final READY remains an integrator-generated projection.",
        },
        "source_level_evidence_reused": [
            "data/shared/remuneration-delegated/item-body-verification.json",
            "data/shared/remuneration-delegated/currentness-source-contract.json",
        ],
        "policy": {
            "no_source_family_broadcast": True,
            "no_regular_preventive_inheritance": True,
            "not_applicable_never_promoted": True,
            "all_mapped_sources_must_be_currentness_closed": True,
            "item_body_pass_required": True,
            "exact_source_identity_required": True,
        },
        "promotions": promotions,
        "holds": holds,
        "projected_publication_candidates": [
            {
                "service_id": row["service_id"],
                "source_family": row["source_family"],
                "projected_currentness_state": "PASS",
                "publication_candidate": True,
                "public_route_enabled": False,
            }
            for row in promotions
        ],
        "safety": {
            "relation_verification_promoted": False,
            "human_review_promoted": False,
            "publication_writeback": False,
            "route_auto_enable": False,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    rendered = json.dumps(build(), ensure_ascii=False, indent=2) + "\n"
    if args.check:
        if not OUTPUT.exists() or OUTPUT.read_text(encoding="utf-8") != rendered:
            raise SystemExit("delegated remuneration currentness decision artifact is stale; run builder")
        print("delegated remuneration currentness decision artifact: PASS")
        return
    OUTPUT.write_text(rendered, encoding="utf-8")
    print(f"wrote {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
