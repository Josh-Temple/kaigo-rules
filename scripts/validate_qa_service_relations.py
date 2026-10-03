#!/usr/bin/env python3
"""Validate national Q&A shared-category scope relations.

This validation is deliberately fail-closed. It proves structure and relation
integrity, not substantive current applicability of each Q&A item.
"""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"


def fail(message: str) -> None:
    raise SystemExit("Q&A service relation validation failed: " + message)


def load(name: str):
    path = DATA / name
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        fail(f"cannot read {name}: {exc}")


def walk_keys(value):
    if isinstance(value, dict):
        for key, child in value.items():
            yield str(key)
            yield from walk_keys(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk_keys(child)


def main() -> None:
    mapping = load("qa-service-mapping.json")
    groups = load("qa-group-relations.json")
    generated = load("qa-service-relations.generated.json")
    manifest = load("services/manifest.json")
    catalog = load("services/catalog.generated.json")

    if groups.get("purpose") != "MHLW_QA_SHARED_CATEGORY_SCOPE_RELATIONS":
        fail("unexpected group relation purpose")
    if generated.get("purpose") != "MHLW_QA_SERVICE_QUERY_RELATION_INDEX":
        fail("unexpected generated relation purpose")

    policy = groups.get("policy", {})
    for key in (
        "relation_is_search_scope_not_item_applicability",
        "qa_body_is_not_duplicated",
        "row_current_service_scope_is_preserved",
        "qualified_raw_label_must_be_resolved_or_fail_closed",
        "similar_service_names_do_not_create_membership",
        "no_individual_code_does_not_mean_not_applicable",
        "verification_state_is_not_promoted",
        "currentness_state_is_not_promoted",
        "human_review_state_is_not_promoted",
        "publication_or_route_state_is_not_promoted",
    ):
        if policy.get(key) is not True:
            fail(f"required fail-closed policy is missing: {key}")

    manifest_services = manifest.get("services", [])
    manifest_ids = [item["service_id"] for item in manifest_services]
    manifest_set = set(manifest_ids)
    catalog_set = {item["service_id"] for item in catalog.get("services", [])}
    if manifest_set != catalog_set:
        fail("manifest and generated catalog service IDs differ")

    by_class: dict[str, set[str]] = {}
    for service in manifest_services:
        by_class.setdefault(service["service_class"], set()).add(service["service_id"])

    group_entries = groups.get("group_memberships", [])
    if len(group_entries) != 6:
        fail("expected exactly six official shared Q&A groups")
    if {g["service_code"] for g in group_entries} != {"01", "02", "03", "04", "05", "06"}:
        fail("shared group code set is not 01-06")
    if len({g["group_id"] for g in group_entries}) != 6:
        fail("shared group IDs are not unique")

    group_by_code = {g["service_code"]: g for g in group_entries}
    expected_class_membership = {
        "02": by_class.get("HOME_SERVICE", set()),
        "03": by_class.get("FACILITY_SERVICE", set()),
        "04": by_class.get("COMMUNITY_BASED_SERVICE", set()),
    }
    if set(group_by_code["01"]["member_service_ids"]) != manifest_set:
        fail("all-services group must contain the complete current service universe")
    for code, expected in expected_class_membership.items():
        if set(group_by_code[code]["member_service_ids"]) != expected:
            fail(f"group {code} membership differs from manifest service class")

    expected_visit = {
        "homevisit", "homebath", "homenursing", "homerehab",
        "homecaremanagement", "regular-round", "night-homevisit",
    }
    expected_day = {
        "dayservice", "dayrehab", "dementia-dayservice", "community-dayservice",
    }
    if set(group_by_code["05"]["member_service_ids"]) != expected_visit:
        fail("visit-service group differs from explicit audited Q&A family")
    if set(group_by_code["06"]["member_service_ids"]) != expected_day:
        fail("day-service group differs from explicit audited Q&A family")

    membership_relations = 0
    for group in group_entries:
        members = group.get("member_service_ids", [])
        if len(members) != len(set(members)):
            fail(f"duplicate member in {group['group_id']}")
        if not set(members).issubset(manifest_set):
            fail(f"unknown member in {group['group_id']}")
        if group.get("scope_state") != "DEFINED":
            fail(f"group {group['group_id']} scope is not explicit")
        if group.get("applicability_verification_state") != "NOT_ESTABLISHED":
            fail(f"group {group['group_id']} promoted item applicability")
        membership_relations += len(members)

    # Shared-category metadata must point to the explicit relation model, without
    # converting a group into an individual service mapping.
    mapping_shared = [
        entry for entry in mapping.get("codes", [])
        if entry.get("classification") == "SHARED_COMMON_CATEGORY"
    ]
    if len(mapping_shared) != 6:
        fail("mapping does not contain six shared categories")
    for entry in mapping_shared:
        relation = entry.get("scope_relation", {})
        if relation.get("membership_state") != "EXPLICIT_RELATION_MODEL":
            fail(f"shared category {entry['service_code']} does not point to explicit relations")
        if relation.get("relation_model") != "data/qa-group-relations.json":
            fail(f"shared category {entry['service_code']} has wrong relation model")
        if entry.get("catalog_mapping", {}).get("service_id") is not None:
            fail(f"shared category {entry['service_code']} was converted to an individual mapping")

    # Qualified raw labels must exactly account for every variant recorded in the
    # source-derived mapping. No unlisted variant may be silently expanded.
    recorded_variant_counts = Counter()
    for entry in mapping.get("codes", []):
        for item in entry.get("row_scope", {}).get("raw_label_variants", []):
            recorded_variant_counts[item["raw_label"]] += int(item["count"])

    rules = groups.get("qualified_raw_label_rules", [])
    rule_counts = Counter({rule["raw_label"]: int(rule["row_count"]) for rule in rules})
    if rule_counts != recorded_variant_counts:
        fail("qualified raw-label rule inventory differs from source-derived variants")

    allowed_states = {"AUTO_RESOLVED", "FAIL_CLOSED"}
    if any(rule.get("resolution_state") not in allowed_states for rule in rules):
        fail("unsupported qualified raw-label resolution state")
    unresolved = [rule for rule in rules if rule["resolution_state"] == "FAIL_CLOSED"]
    if len(unresolved) != 2 or sum(rule["row_count"] for rule in unresolved) != 2:
        fail("expected the two ambiguous facility-prefix rows to remain fail-closed")
    if {rule["raw_label"] for rule in unresolved} != {"4 施設サービス共通", "5 施設サービス共通"}:
        fail("unexpected qualified rows were left unresolved")

    # Special/historical codes may be preserved as provenance/theme metadata but
    # must never enter direct service mappings or group membership.
    forbidden_direct_codes = {"26", "27", "50", "51"}
    direct_codes = {
        entry["service_code"]
        for entry in mapping.get("codes", [])
        if entry.get("catalog_mapping", {}).get("state") == "MAPPED_CURRENT_CATALOG"
    }
    if direct_codes & forbidden_direct_codes:
        fail("historical/special Q&A code contaminated current direct mappings")

    generated_services = generated.get("services", [])
    if [item["service_id"] for item in generated_services] != manifest_ids:
        fail("generated relation service order/universe differs from manifest")
    if len({item["service_id"] for item in generated_services}) != len(manifest_ids):
        fail("duplicate service in generated relation index")

    mapped_service_count = 0
    no_code_count = 0
    for item in generated_services:
        direct = item.get("direct_individual_service_codes", [])
        shared = item.get("shared_group_relations", [])
        candidate = item.get("candidate_query_service_codes", [])
        expected_candidate = sorted(set(direct + [r["service_code"] for r in shared]))
        if candidate != expected_candidate:
            fail(f"candidate code dedup/order mismatch for {item['service_id']}")
        if item.get("scope_state") != "DEFINED_BY_DIRECT_OR_SHARED_GROUP":
            fail(f"unexpected scope state for {item['service_id']}")
        if item.get("item_applicability_verification_state") != "NOT_ESTABLISHED":
            fail(f"generated relation promoted applicability for {item['service_id']}")
        if direct:
            mapped_service_count += 1
            if item.get("individual_mapping_state") != "MAPPED_CURRENT_CATALOG":
                fail(f"mapped service state mismatch for {item['service_id']}")
        else:
            no_code_count += 1
            if item.get("individual_mapping_state") != "NO_INDIVIDUAL_QA_CODE":
                fail(f"missing direct-code state mismatch for {item['service_id']}")
            if "01" not in candidate:
                fail(f"service without individual code lost shared-category access: {item['service_id']}")

    summary = generated.get("summary", {})
    expected_summary = {
        "services_total": len(manifest_ids),
        "individual_service_mappings": mapped_service_count,
        "services_without_individual_qa_code": no_code_count,
        "shared_groups": len(group_entries),
        "group_membership_relations": membership_relations,
        "qualified_or_variant_rows": sum(rule["row_count"] for rule in rules),
        "auto_resolved_qualified_or_variant_rows": sum(
            rule["row_count"] for rule in rules if rule["resolution_state"] == "AUTO_RESOLVED"
        ),
        "unresolved_fail_closed_rows": sum(
            rule["row_count"] for rule in rules if rule["resolution_state"] == "FAIL_CLOSED"
        ),
    }
    if summary != expected_summary:
        fail(f"generated summary mismatch: {summary} != {expected_summary}")

    # Relation files must never contain copied Q&A bodies.
    forbidden_body_keys = {"question", "answer"}
    if forbidden_body_keys & set(walk_keys(groups)):
        fail("canonical relation model contains Q&A body fields")
    if forbidden_body_keys & set(walk_keys(generated)):
        fail("generated relation projection contains Q&A body fields")

    print(
        "Q&A service relations: OK "
        f"({mapped_service_count} direct / {len(group_entries)} groups / "
        f"{membership_relations} memberships / {expected_summary['qualified_or_variant_rows']} qualified rows / "
        f"{expected_summary['auto_resolved_qualified_or_variant_rows']} auto / "
        f"{expected_summary['unresolved_fail_closed_rows']} fail-closed)"
    )


if __name__ == "__main__":
    main()
