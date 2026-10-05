#!/usr/bin/env python3
"""Validate delegated-remuneration item-body assurance and safe service projection."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
SHARED = DATA / "shared" / "remuneration-delegated"

CORPUS = SHARED / "national-corpus.json"
ITEM_BODY = SHARED / "item-body-verification.json"
APPLICABILITY = SHARED / "service-applicability.json"
RELATIONS = SHARED / "service-relations.json"
ADJUDICATIONS = SHARED / "service-applicability-adjudications.json"
LEGACY = DATA / "remuneration-delegated-nodes.json"

FORBIDDEN_SOURCE_STATUSES = {"historical", "superseded", "historical_only"}


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    corpus = load(CORPUS)
    receipt = load(ITEM_BODY)
    applicability = load(APPLICABILITY)
    relations = load(RELATIONS)
    adjudications = load(ADJUDICATIONS)
    legacy = {row["id"]: row for row in load(LEGACY)}

    errors: list[str] = []

    if receipt.get("corpus_id") != corpus.get("corpus_id"):
        errors.append("item-body receipt corpus_id mismatch")
    if receipt.get("source_family") != "delegated_remuneration_criteria":
        errors.append("item-body receipt source family mismatch")
    if receipt.get("verification_kind") != "INDEPENDENT_PRIMARY_SOURCE_BODY_COMPARISON":
        errors.append("item-body receipt verification kind is not independent primary-source comparison")

    nodes = corpus.get("nodes", [])
    node_by_id = {row["canonical_node_id"]: row for row in nodes}
    if len(node_by_id) != len(nodes):
        errors.append("canonical corpus contains duplicate node IDs")

    source_rows = receipt.get("source_verifications", [])
    passed_sources = {}
    for row in source_rows:
        source_id = row.get("source_id")
        if not source_id:
            errors.append("source verification without source_id")
            continue
        if row.get("result") != "PASS":
            continue
        if row.get("coverage_kind") != "ALL_CANONICAL_TOP_LEVEL_NODES_IN_SOURCE":
            errors.append(f"{source_id}: PASS without full canonical-node coverage")
            continue
        if row.get("currentness_claimed") is not False:
            errors.append(f"{source_id}: item-body receipt must not claim currentness")
        if str(row.get("repository_source_status", "")).lower() in FORBIDDEN_SOURCE_STATUSES:
            errors.append(f"{source_id}: historical/superseded source cannot support projection")
        pages = row.get("page_snapshots", [])
        if not pages or any(not p.get("sha256") or not p.get("page") for p in pages):
            errors.append(f"{source_id}: reproducible page snapshots missing")
        actual_count = sum(1 for node in nodes if node.get("source_id") == source_id)
        if row.get("canonical_node_count") != actual_count:
            errors.append(
                f"{source_id}: canonical node count mismatch "
                f"{row.get('canonical_node_count')} != {actual_count}"
            )
        passed_sources[source_id] = row

    corpus_sources = {row.get("source_id") for row in nodes}
    if set(passed_sources) != corpus_sources:
        errors.append(
            "PASS source coverage does not equal canonical corpus source set: "
            f"pass={sorted(passed_sources)}, corpus={sorted(corpus_sources)}"
        )

    expected_total = sum(row.get("canonical_node_count", 0) for row in passed_sources.values())
    if expected_total != len(nodes):
        errors.append(f"verified canonical node total mismatch: {expected_total} != {len(nodes)}")
    if receipt.get("coverage", {}).get("verified_canonical_top_level_nodes") != len(nodes):
        errors.append("receipt verified_canonical_top_level_nodes mismatch")

    compatibility = {
        row.get("canonical_node_id"): row
        for row in receipt.get("compatibility_node_verifications", [])
        if row.get("result") == "PASS"
    }
    for canonical_id, row in compatibility.items():
        legacy_id = row.get("legacy_node_id")
        parent_id = row.get("parent_canonical_node_id")
        if legacy_id not in legacy:
            errors.append(f"{canonical_id}: compatibility legacy node missing")
        if parent_id not in node_by_id:
            errors.append(f"{canonical_id}: compatibility parent canonical node missing")

    applicability_rows = {row["service_id"]: row for row in applicability.get("services", [])}
    relation_rows = {row["service_id"]: row for row in relations.get("services", [])}
    expected_na = {
        row["service_id"]
        for row in adjudications.get("adjudications", [])
        if row.get("applicability_state") == "NOT_APPLICABLE"
    }

    mapped_count = 0
    passed_projection_count = 0
    for service_id, row in applicability_rows.items():
        state = row.get("applicability_state")
        assurance = row.get("assurance") or {}
        item_state = assurance.get("item_body_verification")

        if assurance.get("currentness") != "NOT_ESTABLISHED":
            errors.append(f"{service_id}: currentness changed during item-body projection")
        if assurance.get("relation_verification") != "NOT_ESTABLISHED":
            errors.append(f"{service_id}: relation verification changed during item-body projection")
        if assurance.get("human_review") != "NOT_REVIEWED":
            errors.append(f"{service_id}: human review changed during item-body projection")
        if assurance.get("publication") != "BLOCKED":
            errors.append(f"{service_id}: publication changed during item-body projection")
        if assurance.get("route_exposure") != "BLOCKED":
            errors.append(f"{service_id}: route exposure changed during item-body projection")
        if assurance.get("automatic_promotion_allowed") is not False:
            errors.append(f"{service_id}: automatic promotion must remain disabled")

        relation_row = relation_rows.get(service_id) or {}
        if state == "NOT_APPLICABLE":
            if service_id not in expected_na:
                errors.append(f"{service_id}: NOT_APPLICABLE lacks explicit adjudication")
            if item_state != "NOT_ESTABLISHED":
                errors.append(f"{service_id}: NOT_APPLICABLE service must not be item-body PASS")
            if relation_row.get("relation_verification_state") != "NOT_APPLICABLE":
                errors.append(f"{service_id}: NOT_APPLICABLE relation state drift")
            continue

        if state != "MAPPED":
            errors.append(f"{service_id}: unexpected applicability state {state}")
            continue

        mapped_count += 1
        required = list(row.get("mapped_node_ids") or []) + list(row.get("compatibility_subnode_ids") or [])
        if not required:
            errors.append(f"{service_id}: MAPPED service has empty node set")
            continue

        unsupported: list[str] = []
        for canonical_id in row.get("mapped_node_ids") or []:
            node = node_by_id.get(canonical_id)
            if not node or node.get("source_id") not in passed_sources:
                unsupported.append(canonical_id)
        for canonical_id in row.get("compatibility_subnode_ids") or []:
            if canonical_id not in compatibility:
                unsupported.append(canonical_id)

        if unsupported:
            if item_state == "PASS":
                errors.append(f"{service_id}: unsupported nodes projected to PASS: {sorted(unsupported)}")
        else:
            if item_state != "PASS":
                errors.append(f"{service_id}: fully verified mapped node set did not project to PASS")
            else:
                passed_projection_count += 1
                if assurance.get("item_body_verified_node_count") != len(required):
                    errors.append(f"{service_id}: projected verified-node count mismatch")
                evidence = assurance.get("item_body_projection_evidence") or []
                if "data/shared/remuneration-delegated/item-body-verification.json" not in evidence:
                    errors.append(f"{service_id}: projection evidence missing")

    if mapped_count != 37:
        errors.append(f"mapped service count changed: {mapped_count} != 37")
    if expected_na != {"specific-welfare-equipment-sale", "specific-preventive-welfare-equipment-sale"}:
        errors.append(f"unexpected NOT_APPLICABLE adjudication set: {sorted(expected_na)}")
    if passed_projection_count != mapped_count:
        errors.append(
            f"safe projection incomplete: PASS={passed_projection_count}, MAPPED={mapped_count}"
        )

    boundaries = receipt.get("assurance_boundaries") or {}
    if boundaries.get("currentness") != "NOT_ESTABLISHED":
        errors.append("receipt improperly promotes currentness")
    if boundaries.get("service_relation_verification") != "NOT_ESTABLISHED":
        errors.append("receipt improperly promotes relation verification")
    if boundaries.get("human_review") != "NOT_REVIEWED":
        errors.append("receipt improperly promotes human review")
    if boundaries.get("publication") != "BLOCKED" or boundaries.get("route_exposure") != "BLOCKED":
        errors.append("receipt improperly promotes publication/route")
    if boundaries.get("automatic_cross_axis_promotion_allowed") is not False:
        errors.append("cross-axis automatic promotion must remain disabled")

    if errors:
        raise SystemExit("\n".join(f"ERROR: {message}" for message in errors))

    print(
        "delegated remuneration item-body assurance: PASS "
        f"({len(nodes)} canonical nodes, {len(compatibility)} compatibility subnodes, "
        f"{passed_projection_count}/{mapped_count} mapped services safely projected)"
    )


if __name__ == "__main__":
    main()
