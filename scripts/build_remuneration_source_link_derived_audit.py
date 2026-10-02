#!/usr/bin/env python3
"""Build source-level relation coverage derived from an independent remuneration audit."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUTPUT = DATA / "remuneration-source-link-derived-audit.json"

DERIVATIONS = [
    {
        "from_id": "fee.dayservice.note.1",
        "relation": "staffing_calculation_delegated_to",
        "to_source_id": "mhlw-fee-notice27-base",
        "basis_targets": [
            "calc27.dayservice.1.capacity",
            "calc27.dayservice.1.staffing",
        ],
        "audit_source_key": "notice27",
    },
    {
        "from_id": "fee.dayservice.service-provision",
        "relation": "delegated_criteria_to",
        "to_source_id": "mhlw-fee-criteria95-current",
        "basis_targets": ["criteria95.dayservice.23"],
        "audit_source_key": "notice95",
    },
    {
        "from_id": "fee.dayservice.treatment-improvement",
        "relation": "delegated_criteria_to",
        "to_source_id": "mhlw-fee-criteria95-current",
        "basis_targets": ["criteria95.dayservice.24"],
        "audit_source_key": "notice95",
    },
]


def load(name: str):
    return json.loads((DATA / name).read_text(encoding="utf-8"))


def build() -> dict:
    relation_rows = load("remuneration-relations.json")
    delegated_nodes = {row["id"]: row for row in load("remuneration-delegated-nodes.json")}
    basis_audit = load("remuneration-delegation-relation-independent-audit.json")
    if basis_audit.get("audit_result") != "PASS":
        raise ValueError("basis remuneration-delegation audit is not PASS")

    basis_checks = {
        (row.get("from_id"), row.get("to_id")): row
        for row in basis_audit.get("checks", [])
    }
    checks = []

    for spec in DERIVATIONS:
        differences = []
        relation_matches = [
            row for row in relation_rows
            if row.get("from_fee_id") == spec["from_id"]
            and row.get("relation") == spec["relation"]
            and row.get("to_source_id") == spec["to_source_id"]
        ]
        if len(relation_matches) != 1:
            differences.append("source-level relation row missing or duplicated")

        basis_ids = []
        for target_id in spec["basis_targets"]:
            check = basis_checks.get((spec["from_id"], target_id))
            if not check:
                differences.append(f"independent basis check missing: {target_id}")
                continue
            basis_ids.append(check.get("id"))
            if check.get("result") != "PASS" or check.get("differences") != []:
                differences.append(f"independent basis check is not clean PASS: {target_id}")
            node = delegated_nodes.get(target_id)
            if not node:
                differences.append(f"delegated target node missing: {target_id}")
                continue
            if node.get("source_id") != spec["to_source_id"]:
                differences.append(
                    f"delegated target source mismatch: {target_id} -> {node.get('source_id')}"
                )
            source = basis_audit.get("sources", {}).get(spec["audit_source_key"], {})
            if node.get("source_url") != source.get("url"):
                differences.append(f"audited source URL mismatch: {target_id}")

        checks.append(
            {
                "id": f"{spec['from_id']}-to-{spec['to_source_id']}",
                "from_id": spec["from_id"],
                "relation": spec["relation"],
                "to_source_id": spec["to_source_id"],
                "basis_relation_targets": spec["basis_targets"],
                "basis_audit_checks": basis_ids,
                "result": "PASS" if not differences else "FAIL",
                "differences": differences,
            }
        )

    result = "PASS" if all(row["result"] == "PASS" for row in checks) else "FAIL"
    return {
        "format_version": 1,
        "audit_kind": "DERIVED_FROM_INDEPENDENT_PRIMARY_SOURCE_RELATION_AUDIT",
        "audit_result": result,
        "basis_audit": "data/remuneration-delegation-relation-independent-audit.json",
        "method": (
            "A source-level relation is covered only when an independently audited finer-grained "
            "relation from the same fee node is PASS and every audited target belongs to the same "
            "committed official source named by the source-level relation."
        ),
        "checks": checks,
        "coverage": {
            "relations_in_this_lane": len(checks),
            "relations_passed": sum(row["result"] == "PASS" for row in checks),
        },
        "limitations": [
            "This is derived coverage from an existing independent primary-source audit; it is not a second live-source parse.",
            "Only the three listed source-level relations are covered.",
            "No HUMAN_VERIFIED or VERIFIED_CURRENT state is promoted.",
        ],
        "safety": {
            "human_verified": False,
            "verified_current": False,
            "automatic_promotion_allowed": False,
            "promotes_unlisted_relations": False,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    rendered = json.dumps(build(), ensure_ascii=False, indent=2) + "\n"
    if args.check:
        if not OUTPUT.exists() or OUTPUT.read_text(encoding="utf-8") != rendered:
            raise SystemExit("remuneration source-link derived audit is stale; run builder")
        print("remuneration source-link derived audit: current")
        return
    OUTPUT.write_text(rendered, encoding="utf-8")
    print(f"wrote {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
