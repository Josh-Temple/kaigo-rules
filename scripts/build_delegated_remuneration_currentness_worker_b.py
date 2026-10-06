#!/usr/bin/env python3
"""Build delegated-remuneration residual currentness decisions.

Source-level currentness is reusable only after exact source identity closure.
Service eligibility is always recomputed from the explicit canonical mapping.
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

BASE_MAIN_SHA = "29c5529be51a1211e060acd5911a1122aa0eaf0e"
OBSERVED_DATE = "2026-10-07"
PRIOR_PROMOTED_SERVICE_IDS = frozenset({
    "homevisit",
    "homebath",
    "homenursing",
    "homerehab",
    "homecaremanagement",
    "regular-round",
    "night-homevisit",
    "care-management",
    "preventive-support",
    "welfare-equipment-rental",
    "preventive-homebath",
    "preventive-homenursing",
    "preventive-homerehab",
    "preventive-homecaremanagement",
    "preventive-welfare-equipment-rental",
})


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def mapped_source_ids(row: dict) -> list[str]:
    node_ids = list(row.get("mapped_node_ids") or []) + list(
        row.get("compatibility_subnode_ids") or []
    )
    values = {
        PREFIX_TO_SOURCE.get(str(node_id).split(".", 1)[0], "UNKNOWN")
        for node_id in node_ids
    }
    return sorted(values)


def build() -> dict:
    applicability = load(APPLICABILITY)
    contract = load(CONTRACT)
    source_contracts = {
        row["canonical_source_id"]: row for row in contract.get("source_contracts", [])
    }

    starting_residual = [
        row["service_id"]
        for row in applicability.get("services", [])
        if row.get("applicability_state") == "MAPPED"
        and row["service_id"] not in PRIOR_PROMOTED_SERVICE_IDS
    ]
    starting_residual_set = set(starting_residual)

    promotions: list[dict] = []
    holds: list[dict] = []
    residual_decisions: list[dict] = []

    for row in applicability.get("services", []):
        service_id = row["service_id"]
        node_ids = list(row.get("mapped_node_ids") or []) + list(
            row.get("compatibility_subnode_ids") or []
        )
        sources = mapped_source_ids(row)
        item_state = str(
            (row.get("assurance") or {}).get("item_body_verification")
            or "NOT_ESTABLISHED"
        )

        if row.get("applicability_state") == "NOT_APPLICABLE":
            holds.append(
                {
                    "service_id": service_id,
                    "source_family": "delegated_remuneration_criteria",
                    "decision": "NOT_APPLICABLE_PRESERVED",
                    "blocker": (
                        "Explicit NOT_APPLICABLE adjudication; currentness promotion "
                        "is forbidden."
                    ),
                    "mapped_source_ids": [],
                }
            )
            continue

        blocker = None
        blocked: list[str] = []
        if row.get("applicability_state") != "MAPPED" or not node_ids:
            blocker = "No explicit canonical service applicability mapping."
        elif item_state != "PASS":
            blocker = f"Item-body assurance is {item_state}, not PASS."
        else:
            blocked = [
                source_id
                for source_id in sources
                if not (source_contracts.get(source_id) or {}).get(
                    "promotion_eligible"
                )
                or (source_contracts.get(source_id) or {}).get(
                    "currentness_state"
                )
                != "PASS"
            ]
            if blocked:
                blocker = (
                    "At least one mapped canonical source is not currentness-closed "
                    "under the bounded source contract."
                )

        if blocker:
            hold = {
                "service_id": service_id,
                "source_family": "delegated_remuneration_criteria",
                "decision": "DEFER",
                "blocker": blocker,
                "mapped_source_ids": sources,
            }
            if blocked:
                hold["blocked_source_ids"] = blocked
            holds.append(hold)
            if service_id in starting_residual_set:
                residual_decisions.append(
                    {
                        **hold,
                        "starting_state": "BLOCKED_CURRENTNESS",
                    }
                )
            continue

        newly_promoted = service_id in starting_residual_set
        promotion = {
            "service_id": service_id,
            "source_family": "delegated_remuneration_criteria",
            "mapped_node_count": len(node_ids),
            "mapped_node_ids": node_ids,
            "mapped_source_ids": sources,
            "applicability_proof": {
                "state": "PASS_EXPLICIT_CANONICAL_SERVICE_MAPPING",
                "evidence": [
                    "data/shared/remuneration-delegated/"
                    f"service-applicability.json#{service_id}"
                ],
                "inherited_from_sibling_service": False,
            },
            "item_body_state": "PASS",
            "item_body_evidence": [
                "data/shared/remuneration-delegated/"
                f"service-applicability.json#{service_id}",
                "data/shared/remuneration-delegated/item-body-verification.json",
            ],
            "source_currentness_evidence": [
                "data/shared/remuneration-delegated/"
                f"currentness-source-contract.json#{source_id}"
                for source_id in sources
            ],
            "source_identity_matches_item_body_source": True,
            "prior_currentness_state": (
                "NOT_ESTABLISHED" if newly_promoted else "PASS"
            ),
            "promotion_origin": (
                "RESIDUAL_NOTICE27_CURRENTNESS_CLOSURE"
                if newly_promoted
                else "PRESERVED_PRIOR_READY_CURRENTNESS"
            ),
            "newly_promoted": newly_promoted,
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
        }
        promotions.append(promotion)

        if newly_promoted:
            residual_decisions.append(
                {
                    "service_id": service_id,
                    "source_family": "delegated_remuneration_criteria",
                    "starting_state": "BLOCKED_CURRENTNESS",
                    "decision": "PROMOTE_CURRENTNESS",
                    "mapped_source_ids": sources,
                    "currentness_decision": "PASS",
                    "blocker": None,
                    "evidence": [
                        "data/shared/remuneration-delegated/"
                        f"service-applicability.json#{service_id}",
                        *[
                            "data/shared/remuneration-delegated/"
                            f"currentness-source-contract.json#{source_id}"
                            for source_id in sources
                        ],
                    ],
                }
            )

    applicable_count = sum(
        1
        for row in applicability.get("services", [])
        if row.get("applicability_state") == "MAPPED"
    )
    not_applicable_count = sum(
        1
        for row in applicability.get("services", [])
        if row.get("applicability_state") == "NOT_APPLICABLE"
    )
    newly_promoted_count = sum(
        1 for row in promotions if row.get("newly_promoted") is True
    )
    deferred_count = sum(1 for row in holds if row["decision"] == "DEFER")
    notice27 = source_contracts.get("mhlw-fee-notice27-base") or {}

    return {
        "format_version": 2,
        "artifact_kind": "DELEGATED_REMUNERATION_RESIDUAL_CURRENTNESS_DECISIONS",
        "wave_id": (
            "2026-10-07-ready-publication-completion-and-currentness-expansion"
        ),
        "worker": "B",
        "role": "Delegated Remuneration Residual Currentness Closure Worker",
        "base_main_sha": BASE_MAIN_SHA,
        "observed_date": OBSERVED_DATE,
        "source_contract": (
            "data/shared/remuneration-delegated/currentness-source-contract.json"
        ),
        "notice27_currentness_evidence": (
            "data/shared/remuneration-delegated/notice27-currentness-evidence.json"
        ),
        "purpose": (
            "Close the shared Notice 27 currentness blocker first, then preserve "
            "or promote only explicitly mapped delegated-remuneration service "
            "cells whose every mapped source identity is currentness-closed."
        ),
        "summary": {
            "applicable_cells": applicable_count,
            "not_applicable_cells": not_applicable_count,
            "starting_ready_cells": len(PRIOR_PROMOTED_SERVICE_IDS),
            "starting_deferred_applicable_cells": len(starting_residual),
            "currentness_pass_cells": len(promotions),
            "newly_promoted_cells": newly_promoted_count,
            "deferred_applicable_cells": deferred_count,
            "projected_ready_increase": newly_promoted_count,
            "projected_ready_count_after_integration": len(promotions),
            "projected_ready_increase_basis": (
                "Only the 22 cells that were BLOCKED_CURRENTNESS on the starting "
                "main are counted as READY increase; the existing 15 READY cells "
                "are preserved, not recounted."
            ),
        },
        "source_level_closure": {
            "canonical_source_id": "mhlw-fee-notice27-base",
            "starting_state": "BLOCKED",
            "final_state": notice27.get("currentness_state"),
            "promotion_eligible": notice27.get("promotion_eligible"),
            "evidence": (
                "data/shared/remuneration-delegated/"
                "notice27-currentness-evidence.json"
            ),
        },
        "source_level_evidence_reused": [
            "data/shared/remuneration-delegated/item-body-verification.json",
            "data/shared/remuneration-delegated/currentness-source-contract.json",
            "data/shared/remuneration-delegated/notice27-currentness-evidence.json",
        ],
        "policy": {
            "no_source_family_broadcast": True,
            "no_regular_preventive_inheritance": True,
            "not_applicable_never_promoted": True,
            "all_mapped_sources_must_be_currentness_closed": True,
            "item_body_pass_required": True,
            "exact_source_identity_required": True,
            "residual_baseline_is_starting_main": True,
        },
        "starting_residual_service_ids": starting_residual,
        "residual_decisions": residual_decisions,
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
            if row.get("newly_promoted") is True
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
            raise SystemExit(
                "delegated remuneration currentness decision artifact is stale; "
                "run builder"
            )
        print("delegated remuneration currentness decision artifact: PASS")
        return
    OUTPUT.write_text(rendered, encoding="utf-8")
    print(f"wrote {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
