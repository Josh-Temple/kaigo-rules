#!/usr/bin/env python3
"""Build a deterministic registry for independently audited semantic relations.

Individual audit records remain immutable lane-level evidence. This registry is
the only place that aggregates coverage across lanes, avoiding validator chains
where refreshing one audit forces unrelated later audits to be repinned.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUTPUT = DATA / "relation-verification-registry.json"

RELATION_FILES = [
    "care-insurance-act-relations.json",
    "fee-guidance-relations.json",
    "notice-ordinance-relations.json",
    "ordinance37-relations.json",
    "relationships.json",
    "remuneration-delegated-relations.json",
    "remuneration-relations.json",
]

LANES = [
    {
        "id": "ordinance37-article105-explicit-references",
        "audit_file": "relation-semantic-independent-audit.json",
        "audit_kind": "INDEPENDENT_EXPLICIT_LEGAL_REFERENCE_AUDIT",
        "count_path": ("coverage", "explicit_legal_reference_relations_independently_verified"),
    },
    {
        "id": "careact-internal-article74-relations",
        "audit_file": "careact-internal-relation-independent-audit.json",
        "audit_kind": "INDEPENDENT_CAREACT_INTERNAL_RELATION_AUDIT",
        "count_path": ("coverage", "relations_passed"),
    },
    {
        "id": "careact-cross-layer-source-chains",
        "audit_file": "cross-layer-source-chain-independent-audit.json",
        "audit_kind": "INDEPENDENT_CROSS_LAYER_SOURCE_CHAIN_AUDIT",
        "count_path": ("coverage", "relations_passed"),
    },
    {
        "id": "remuneration-delegation-relations",
        "audit_file": "remuneration-delegation-relation-independent-audit.json",
        "audit_kind": "INDEPENDENT_REMUNERATION_DELEGATION_RELATION_AUDIT",
        "count_path": ("coverage", "relations_passed"),
    },
]


def load(name: str):
    return json.loads((DATA / name).read_text(encoding="utf-8"))


def get_path(value, path):
    for key in path:
        value = value[key]
    return value


def inventory_count() -> int:
    total = 0
    for name in RELATION_FILES:
        rows = load(name)
        total += sum(1 for row in rows if row.get("relation") != "contains")
    return total


def build() -> dict:
    lanes = []
    verified = 0

    for config in LANES:
        audit = load(config["audit_file"])
        if audit.get("audit_result") != "PASS":
            raise RuntimeError(f"{config['audit_file']}: audit_result is not PASS")
        if audit.get("audit_kind") != config["audit_kind"]:
            raise RuntimeError(f"{config['audit_file']}: audit_kind changed")

        count = int(get_path(audit, config["count_path"]))
        verified += count
        lanes.append(
            {
                "id": config["id"],
                "status": "PASS",
                "audit_kind": config["audit_kind"],
                "verified_relations": count,
                "evidence": f"data/{config['audit_file']}",
                "audited_at": audit.get("audited_at"),
                "human_verified": False,
                "verified_current": False,
            }
        )

    inventory = inventory_count()
    if verified > inventory:
        raise RuntimeError("verified relation count exceeds current inventory")

    remaining = inventory - verified
    return {
        "format_version": 1,
        "generated_by": "scripts/build_relation_verification_registry.py",
        "policy": (
            "Lane-level audits are independently pinned. Aggregate coverage is "
            "computed here and never promotes HUMAN_VERIFIED or VERIFIED_CURRENT."
        ),
        "lanes": lanes,
        "summary": {
            "non_contains_semantic_or_cross_layer_relations": inventory,
            "independently_verified_relations": verified,
            "remaining_not_independently_verified": remaining,
            "coverage_percent": round((verified / inventory * 100) if inventory else 100.0, 2),
            "human_verified_relations": 0,
        },
        "gaps": (
            []
            if remaining == 0
            else [
                {
                    "kind": "RELATION_INDEPENDENT_AUDIT_INCOMPLETE",
                    "remaining_relations": remaining,
                    "note": "Uncovered relations remain unpromoted and require separate independent audit lanes.",
                }
            ]
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    rendered = json.dumps(build(), ensure_ascii=False, indent=2) + "\n"
    if args.check:
        if not OUTPUT.exists():
            raise SystemExit("relation verification registry missing; run builder")
        if OUTPUT.read_text(encoding="utf-8") != rendered:
            raise SystemExit("relation verification registry is stale; run builder")
        print("relation verification registry: current")
        return

    OUTPUT.write_text(rendered, encoding="utf-8")
    print(f"wrote {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
