#!/usr/bin/env python3
"""Build bounded Care Insurance Act service-identity relation coverage."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUTPUT = DATA / "careact-service-identity-derived-audit.json"

EXPECTED = [
    ("careact.article.8.p.7", "defines_service_for", "fee.dayservice.root"),
    ("careact.article.8.p.7", "defines_service_for", "ordinance37.article.92"),
]


def load(name: str):
    return json.loads((DATA / name).read_text(encoding="utf-8"))


def build() -> dict:
    egov = load("egov-content-independent-audit.json")
    remuneration = load("remuneration-independent-audit.json")
    if egov.get("audit_result") != "PASS":
        raise ValueError("e-Gov content audit is not PASS")
    if remuneration.get("audit_result") != "PASS":
        raise ValueError("remuneration audit is not PASS")

    egov_checks = {row.get("id"): row for row in egov.get("checks", [])}
    for layer in ("care-insurance-act", "ordinance37"):
        if egov_checks.get(layer, {}).get("result") != "PASS":
            raise ValueError(f"{layer} independent e-Gov check is not PASS")

    care_nodes = {row["id"]: row for row in load("care-insurance-act-nodes.json")}
    ordinance_nodes = {row["id"]: row for row in load("ordinance37-nodes.json")}
    fee_nodes = {row["id"]: row for row in load("remuneration-current-skeleton.json")}
    relations = load("care-insurance-act-relations.json")

    care = care_nodes.get("careact.article.8.p.7")
    ordinance = ordinance_nodes.get("ordinance37.article.92")
    fee = fee_nodes.get("fee.dayservice.root")

    checks = []
    for source_id, relation, target_id in EXPECTED:
        differences = []
        matches = [
            row for row in relations
            if row.get("from") == source_id
            and row.get("relation") == relation
            and row.get("to") == target_id
        ]
        if len(matches) != 1:
            differences.append("committed relation identity missing or duplicated")

        if not care or "この法律において「通所介護」とは" not in str(care.get("official_text") or ""):
            differences.append("Care Insurance Act Article 8 paragraph 7 explicit service definition missing")

        if target_id == "ordinance37.article.92":
            if not ordinance:
                differences.append("Ordinance 37 Article 92 node missing")
            else:
                text = str(ordinance.get("official_text") or "")
                if "指定居宅サービスに該当する通所介護" not in text:
                    differences.append("Ordinance 37 Article 92 explicit 通所介護 identity missing")
        elif target_id == "fee.dayservice.root":
            if not fee:
                differences.append("day-service remuneration root missing")
            else:
                if fee.get("title") != "通所介護費":
                    differences.append("remuneration root title is not 通所介護費")
                if fee.get("service_scope") != "通所介護":
                    differences.append("remuneration root service scope is not 通所介護")
                if fee.get("source_id") != "mhlw-fee-notice19-base":
                    differences.append("remuneration root does not point to Notice 19")
        else:
            differences.append("unsupported target")

        checks.append(
            {
                "id": f"{source_id}-to-{target_id}",
                "from_id": source_id,
                "relation": relation,
                "to_id": target_id,
                "service_identity": "通所介護",
                "result": "PASS" if not differences else "FAIL",
                "differences": differences,
            }
        )

    result = "PASS" if all(row["result"] == "PASS" for row in checks) else "FAIL"
    return {
        "format_version": 1,
        "audit_kind": "DERIVED_FROM_INDEPENDENT_SOURCE_SERVICE_IDENTITY",
        "audit_result": result,
        "basis": {
            "egov_content_audit": "data/egov-content-independent-audit.json",
            "remuneration_audit": "data/remuneration-independent-audit.json",
        },
        "method": (
            "Covers only the two fixed cross-layer identities where Care Insurance Act "
            "Article 8 paragraph 7 explicitly defines 通所介護 and the target layer explicitly "
            "names the same service. This verifies service-identity continuity only."
        ),
        "checks": checks,
        "coverage": {
            "relations_in_this_lane": len(checks),
            "relations_passed": sum(row["result"] == "PASS" for row in checks),
        },
        "limitations": [
            "This audit does not establish broader legal effect, priority, currentness, or applicability beyond the two listed identities.",
            "It does not verify other semantic remuneration-to-ordinance mappings.",
            "No HUMAN_VERIFIED or VERIFIED_CURRENT state is promoted.",
        ],
        "safety": {
            "human_verified": False,
            "verified_current": False,
            "automatic_promotion_allowed": False,
            "promotes_unlisted_relations": False,
            "service_identity_only": True,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    rendered = json.dumps(build(), ensure_ascii=False, indent=2) + "\n"
    if args.check:
        if not OUTPUT.exists() or OUTPUT.read_text(encoding="utf-8") != rendered:
            raise SystemExit("Care Act service-identity derived audit is stale; run builder")
        print("Care Act service-identity derived audit: current")
        return
    OUTPUT.write_text(rendered, encoding="utf-8")
    print(f"wrote {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
