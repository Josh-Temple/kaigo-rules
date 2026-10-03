#!/usr/bin/env python3
"""Build the service -> national Q&A direct/group relation index.

The generated file is a projection. Canonical inputs are:
- data/qa-service-mapping.json
- data/qa-group-relations.json
- data/services/manifest.json

The builder intentionally does not infer applicability from service names and does
not promote verification/currentness/human-review/publication state.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
MAPPING = DATA / "qa-service-mapping.json"
GROUPS = DATA / "qa-group-relations.json"
MANIFEST = DATA / "services" / "manifest.json"
OUTPUT = DATA / "qa-service-relations.generated.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def build() -> dict:
    mapping = load(MAPPING)
    group_model = load(GROUPS)
    manifest = load(MANIFEST)

    service_ids = [item["service_id"] for item in manifest["services"]]
    direct_by_service: dict[str, list[str]] = {service_id: [] for service_id in service_ids}
    for entry in mapping["codes"]:
        cm = entry.get("catalog_mapping", {})
        if (
            entry.get("classification") == "INDIVIDUAL_SERVICE"
            and cm.get("state") == "MAPPED_CURRENT_CATALOG"
            and cm.get("service_id") in direct_by_service
        ):
            direct_by_service[cm["service_id"]].append(entry["service_code"])

    groups_by_service: dict[str, list[dict]] = {service_id: [] for service_id in service_ids}
    membership_count = 0
    for group in group_model["group_memberships"]:
        for service_id in group["member_service_ids"]:
            if service_id not in groups_by_service:
                raise ValueError(f"group {group['group_id']} references unknown service {service_id}")
            groups_by_service[service_id].append(
                {
                    "service_code": group["service_code"],
                    "group_id": group["group_id"],
                    "scope_state": group["scope_state"],
                    "applicability_verification_state": group["applicability_verification_state"],
                }
            )
            membership_count += 1

    rules = group_model["qualified_raw_label_rules"]
    qualified_rows = sum(int(rule["row_count"]) for rule in rules)
    auto_rows = sum(
        int(rule["row_count"])
        for rule in rules
        if rule["resolution_state"] == "AUTO_RESOLVED"
    )
    unresolved_rows = qualified_rows - auto_rows

    services = []
    for service_id in service_ids:
        direct_codes = sorted(set(direct_by_service[service_id]))
        group_relations = sorted(groups_by_service[service_id], key=lambda x: x["service_code"])
        group_codes = [item["service_code"] for item in group_relations]
        candidate_codes = sorted(set(direct_codes + group_codes))
        services.append(
            {
                "service_id": service_id,
                "direct_individual_service_codes": direct_codes,
                "individual_mapping_state": (
                    "MAPPED_CURRENT_CATALOG" if direct_codes else "NO_INDIVIDUAL_QA_CODE"
                ),
                "shared_group_relations": group_relations,
                "candidate_query_service_codes": candidate_codes,
                "scope_state": "DEFINED_BY_DIRECT_OR_SHARED_GROUP",
                "item_applicability_verification_state": "NOT_ESTABLISHED",
            }
        )

    return {
        "format_version": 1,
        "purpose": "MHLW_QA_SERVICE_QUERY_RELATION_INDEX",
        "generated_from": {
            "qa_service_mapping": "data/qa-service-mapping.json",
            "qa_group_relations": "data/qa-group-relations.json",
            "service_manifest": "data/services/manifest.json",
        },
        "semantics": {
            "candidate_query_service_codes": (
                "Union of direct individual Q&A code(s) and explicit shared-group code(s). "
                "Callers must still enforce row-level current_service_scope and qualified raw-label rules."
            ),
            "no_individual_code": "Does not mean Q&A NOT_APPLICABLE.",
            "scope_vs_applicability": "A defined group relation does not establish item-level applicability.",
        },
        "summary": {
            "services_total": len(service_ids),
            "individual_service_mappings": sum(bool(v) for v in direct_by_service.values()),
            "services_without_individual_qa_code": sum(not bool(v) for v in direct_by_service.values()),
            "shared_groups": len(group_model["group_memberships"]),
            "group_membership_relations": membership_count,
            "qualified_or_variant_rows": qualified_rows,
            "auto_resolved_qualified_or_variant_rows": auto_rows,
            "unresolved_fail_closed_rows": unresolved_rows,
        },
        "services": services,
    }


def render(data: dict) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    expected = render(build())
    if args.check:
        current = OUTPUT.read_text(encoding="utf-8") if OUTPUT.exists() else ""
        if current != expected:
            raise SystemExit("Q&A service relation projection is stale; run scripts/build_qa_service_relations.py")
        print("Q&A service relation projection: current")
        return
    OUTPUT.write_text(expected, encoding="utf-8")
    print(f"Wrote {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
