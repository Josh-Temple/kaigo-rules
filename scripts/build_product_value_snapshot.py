#!/usr/bin/env python3
"""Build a deterministic product-value metric snapshot from repository data."""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SPEC_PATH = ROOT / "data" / "product-value-metrics-v0.1.json"
OUTPUT_PATH = ROOT / "data" / "product-value-snapshot-v0.1.json"
SCOPE_EXPORTER = ROOT / "scripts" / "export_product_value_scope.mjs"

REQUIRED_METRIC_IDS = {
    "practical_questions_with_evidence_path",
    "public_items_with_complete_evidence_state",
    "unresolved_or_unverified_relations",
}

EXPECTED_PUBLIC_FAMILIES = [
    "practical_questions",
    "care_insurance_act_articles",
    "ordinance_articles",
    "notice_items",
    "remuneration_items",
    "remuneration_delegated_criteria",
    "fee_guidance_items",
    "unit_price_records",
    "qa_corpus_items",
    "dayrehab_standard_articles",
]


def load_json(relative_path: str | Path) -> Any:
    path = relative_path if isinstance(relative_path, Path) else ROOT / relative_path
    return json.loads(path.read_text(encoding="utf-8"))


def ratio(numerator: int, denominator: int) -> float:
    return round(numerator / denominator, 6) if denominator else 0.0


def layer_state_complete(layer_by_id: dict[str, dict[str, Any]], layer_id: str) -> bool:
    layer = layer_by_id.get(layer_id) or {}
    return all(
        key in layer
        for key in ("content_verification", "currentness", "human_review")
    )


def load_canonical_service_scope(service_id: str) -> dict[str, Any]:
    completed = subprocess.run(
        [
            "node",
            "--experimental-strip-types",
            str(SCOPE_EXPORTER),
            "--service-id",
            service_id,
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(completed.stdout)
    if payload.get("contract") != "lib/service-scope.ts":
        raise RuntimeError("canonical service-scope exporter contract drifted")
    if payload.get("service_id") != service_id:
        raise RuntimeError("canonical service-scope exporter returned wrong service")
    return payload


def question_has_evidence_path(
    question: dict[str, Any],
    source_ids: set[str],
    rule_nodes: dict[str, dict[str, Any]],
    notice_nodes: dict[str, dict[str, Any]],
    qa_items: dict[str, dict[str, Any]],
) -> bool:
    if any(
        ref.get("source_id") in source_ids
        for ref in question.get("source_refs", [])
        if isinstance(ref, dict)
    ):
        return True

    for node_id in question.get("rule_node_ids", []):
        node = rule_nodes.get(node_id) or {}
        if node.get("source_id") in source_ids:
            return True

    for node_id in question.get("notice_node_ids", []):
        node = notice_nodes.get(node_id) or {}
        if any(source_id in source_ids for source_id in node.get("source_ids", [])):
            return True

    for item_id in question.get("qa_item_ids", []):
        item = qa_items.get(item_id) or {}
        if item.get("source_id") in source_ids:
            return True

    return False


def question_state_complete(
    question: dict[str, Any],
    layer_by_id: dict[str, dict[str, Any]],
) -> bool:
    required_layers: set[str] = set()
    if question.get("rule_node_ids"):
        required_layers.add("ordinance37")
    if question.get("notice_node_ids"):
        required_layers.add("rouki25-dayservice")
    if question.get("qa_item_ids"):
        required_layers.add("qa-corpus")

    return bool(required_layers) and all(
        layer_state_complete(layer_by_id, layer_id)
        for layer_id in required_layers
    )


def row(
    item_id: str,
    *,
    source_complete: bool,
    scope_complete: bool,
    verification_state_complete: bool,
) -> dict[str, Any]:
    return {
        "id": item_id,
        "source_complete": bool(source_complete),
        "scope_complete": bool(scope_complete),
        "verification_state_complete": bool(verification_state_complete),
    }


def build_snapshot() -> dict[str, Any]:
    spec = load_json(SPEC_PATH)
    metrics_by_id = {metric["id"]: metric for metric in spec["metrics"]}
    if set(metrics_by_id) != REQUIRED_METRIC_IDS:
        raise RuntimeError(
            f"metric spec mismatch: expected {sorted(REQUIRED_METRIC_IDS)}, "
            f"got {sorted(metrics_by_id)}"
        )
    public_spec = metrics_by_id["public_items_with_complete_evidence_state"]
    included_families = public_spec["denominator"].get("included_public_families")
    if included_families != EXPECTED_PUBLIC_FAMILIES:
        raise RuntimeError(
            "public family contract drifted: "
            f"expected {EXPECTED_PUBLIC_FAMILIES}, got {included_families}"
        )

    service_manifest = load_json("data/services/manifest.json")
    default_service_id = service_manifest["default_service_id"]
    service_entry = next(
        item for item in service_manifest["services"]
        if item["service_id"] == default_service_id
    )
    service_config_path = service_entry["config"]
    service_config = load_json(service_config_path)
    routing = service_config["routing"]
    public_route_enabled = (
        routing.get("current_mode") == "LEGACY_ROOT"
        or bool(routing.get("future_service_base_enabled"))
    )
    if not public_route_enabled:
        raise RuntimeError(f"default service public route is disabled: {default_service_id}")

    canonical_scope = load_canonical_service_scope(default_service_id)

    questions = load_json("data/questions.json")
    sources = load_json("data/sources.json")
    faq_rule_nodes = load_json("data/rule-nodes.json")
    faq_notice_nodes = load_json("data/notice-nodes.json")
    faq_qa_items = load_json("data/qa-items.json")
    verification_registry = load_json("data/verification-registry.json")

    source_ids = {item["id"] for item in sources}
    rule_node_by_id = {item["id"]: item for item in faq_rule_nodes}
    notice_node_by_id = {item["id"]: item for item in faq_notice_nodes}
    qa_item_by_id = {item["id"]: item for item in faq_qa_items}
    layer_by_id = {item["id"]: item for item in verification_registry["layers"]}

    question_evidence = {
        item["slug"]: question_has_evidence_path(
            item,
            source_ids,
            rule_node_by_id,
            notice_node_by_id,
            qa_item_by_id,
        )
        for item in questions
    }
    questions_with_evidence = sum(question_evidence.values())
    missing_question_slugs = sorted(
        slug for slug, ok in question_evidence.items() if not ok
    )

    question_scope_complete = (
        service_config.get("scope_files", {}).get("questions")
        == "data/questions.json"
    )
    question_public_rows = [
        row(
            f"question:{item['slug']}",
            source_complete=question_evidence[item["slug"]],
            scope_complete=question_scope_complete,
            verification_state_complete=question_state_complete(item, layer_by_id),
        )
        for item in questions
    ]

    care_act_nodes = load_json("data/care-insurance-act-nodes.json")
    care_act_article_ids = set(
        canonical_scope["care_insurance_act"]["article_ids"]
    )
    care_act_items = [
        item
        for item in care_act_nodes
        if item.get("node_type") == "article" and item.get("id") in care_act_article_ids
    ]
    care_act_state_complete = layer_state_complete(
        layer_by_id, "care-insurance-act"
    )
    care_act_public_rows = [
        row(
            f"law:{item['id']}",
            source_complete=bool(item.get("source_url")),
            scope_complete=True,
            verification_state_complete=care_act_state_complete,
        )
        for item in care_act_items
    ]

    ordinance_nodes = load_json("data/ordinance37-nodes.json")
    ordinance_article_ids = set(canonical_scope["ordinance37"]["article_ids"])
    rule_items = [
        item
        for item in ordinance_nodes
        if item.get("node_type") == "article" and item.get("id") in ordinance_article_ids
    ]
    rule_state_complete = layer_state_complete(layer_by_id, "ordinance37")
    rule_public_rows = [
        row(
            f"rule:{item['id']}",
            source_complete=bool(item.get("source_url")),
            scope_complete=True,
            verification_state_complete=rule_state_complete,
        )
        for item in rule_items
    ]

    notice_packet = load_json("data/notice-review-packet.json")
    notice_items = notice_packet.get("items", [])
    notice_scope_complete = (
        service_config.get("scope_files", {}).get("notice_review_packet")
        == "data/notice-review-packet.json"
    )
    notice_state_complete = layer_state_complete(layer_by_id, "rouki25-dayservice")
    notice_public_rows = []
    for item in notice_items:
        source_complete = any(
            isinstance(evidence, dict)
            and evidence.get("source_id") in source_ids
            and bool(evidence.get("source_url"))
            for evidence in item.get("source_evidence", [])
        )
        notice_public_rows.append(
            row(
                f"notice:{item['notice_id']}",
                source_complete=source_complete,
                scope_complete=notice_scope_complete,
                verification_state_complete=notice_state_complete,
            )
        )

    fee_nodes = load_json("data/remuneration-current-skeleton.json")
    fee_meta = load_json("data/remuneration-current-meta.json")
    fee_items = [item for item in fee_nodes if item.get("id") != "fee.dayservice.root"]
    fee_namespace = service_config.get("id_namespaces", {}).get("fee", "")
    fee_source_complete = (
        bool(fee_meta.get("current_official_source"))
        and fee_meta["current_official_source"] in source_ids
    )
    fee_state_complete = layer_state_complete(layer_by_id, "remuneration-notices")
    fee_public_rows = [
        row(
            f"fee:{item['id']}",
            source_complete=fee_source_complete,
            scope_complete=bool(fee_namespace and item["id"].startswith(fee_namespace)),
            verification_state_complete=fee_state_complete,
        )
        for item in fee_items
    ]

    delegated_nodes = load_json("data/remuneration-delegated-nodes.json")
    delegated_public_rows = [
        row(
            f"fee-criteria:{item['id']}",
            source_complete=(
                item.get("source_id") in source_ids and bool(item.get("source_url"))
            ),
            scope_complete=bool(str(item.get("service_scope") or "").strip()),
            verification_state_complete=fee_state_complete,
        )
        for item in delegated_nodes
    ]

    guidance_nodes = load_json("data/fee-guidance-current-skeleton.json")
    guidance_scope_complete = (
        service_config.get("scope_files", {}).get("fee_guidance")
        == "data/fee-guidance-current-skeleton.json"
    )
    guidance_state_complete = layer_state_complete(
        layer_by_id, "rouki36-dayservice"
    )
    guidance_public_rows = []
    for item in guidance_nodes:
        evidence = item.get("evidence", [])
        source_complete = bool(evidence) and all(
            isinstance(entry, dict) and entry.get("source_id") in source_ids
            for entry in evidence
        )
        guidance_public_rows.append(
            row(
                f"fee-guidance:{item['id']}",
                source_complete=source_complete,
                scope_complete=(
                    guidance_scope_complete
                    and bool(str(item.get("service_scope") or "").strip())
                ),
                verification_state_complete=guidance_state_complete,
            )
        )

    unit_rates = load_json("data/unit-price-dayservice.json")
    unit_assignments = load_json("data/unit-price-region-assignments.json")
    rate_ids = {item["id"] for item in unit_rates}
    unit_state_complete = layer_state_complete(layer_by_id, "unit-price")
    unit_price_public_rows = [
        row(
            f"unit-price:{item['id']}",
            source_complete=item.get("source_id") in source_ids,
            scope_complete=item.get("service") == "通所介護",
            verification_state_complete=unit_state_complete,
        )
        for item in unit_rates
    ]
    unit_price_public_rows.extend(
        row(
            f"unit-region:{item['id']}",
            source_complete=item.get("source_id") in source_ids,
            scope_complete=item.get("unit_price_id") in rate_ids,
            verification_state_complete=unit_state_complete,
        )
        for item in unit_assignments
    )

    qa_corpus = load_json("data/qa-corpus.json")
    qa_meta = load_json("data/qa-corpus-meta.json")
    qa_source_complete = bool(
        qa_meta.get("source_workbook") and qa_meta.get("source_sha256")
    )
    target_codes = qa_meta.get("target_service_codes", [])
    scope_by_code = qa_meta.get("scope_by_code", {})
    qa_scope_complete = (
        service_config.get("scope_files", {}).get("qa_corpus") == "data/qa-corpus.json"
        and "16" in target_codes
        and all(code in scope_by_code for code in target_codes)
    )
    qa_state_complete = layer_state_complete(layer_by_id, "qa-corpus")
    qa_public_rows = [
        row(
            f"qa-corpus:{index + 1}",
            source_complete=qa_source_complete,
            scope_complete=qa_scope_complete,
            verification_state_complete=qa_state_complete,
        )
        for index in range(len(qa_corpus))
    ]

    dayrehab_public_rows = []
    dayrehab_entry = next(
        (item for item in service_manifest["services"] if item["service_id"] == "dayrehab"),
        None,
    )
    if dayrehab_entry:
        dayrehab_config = load_json(dayrehab_entry["config"])
        if dayrehab_config.get("routing", {}).get("future_service_base_enabled"):
            index_ref = dayrehab_config.get("scope_files", {}).get("standards_index")
            if not index_ref:
                raise RuntimeError("enabled dayrehab route missing standards_index scope")
            dayrehab_index = load_json(index_ref)
            if dayrehab_index.get("service_id") != "dayrehab":
                raise RuntimeError("dayrehab standards index service_id mismatch")
            state_complete = layer_state_complete(
                layer_by_id, "ordinance37-dayrehab-preview"
            )
            source_complete = bool(dayrehab_index.get("sources"))
            dayrehab_public_rows = [
                row(
                    f"dayrehab-standard:{item['article_number']}",
                    source_complete=(source_complete and bool(item.get("source_locator"))),
                    scope_complete=True,
                    verification_state_complete=state_complete,
                )
                for item in dayrehab_index.get("articles", [])
            ]

    families = {
        "practical_questions": question_public_rows,
        "care_insurance_act_articles": care_act_public_rows,
        "ordinance_articles": rule_public_rows,
        "notice_items": notice_public_rows,
        "remuneration_items": fee_public_rows,
        "remuneration_delegated_criteria": delegated_public_rows,
        "fee_guidance_items": guidance_public_rows,
        "unit_price_records": unit_price_public_rows,
        "qa_corpus_items": qa_public_rows,
        "dayrehab_standard_articles": dayrehab_public_rows,
    }
    if list(families) != EXPECTED_PUBLIC_FAMILIES:
        raise RuntimeError("builder public family order/contract drifted")

    all_public_rows = [item for rows in families.values() for item in rows]

    def is_complete(item: dict[str, Any]) -> bool:
        return all(
            item[key]
            for key in (
                "source_complete",
                "scope_complete",
                "verification_state_complete",
            )
        )

    public_total = len(all_public_rows)
    public_complete = sum(1 for item in all_public_rows if is_complete(item))
    missing_source = sorted(
        item["id"] for item in all_public_rows if not item["source_complete"]
    )
    missing_scope = sorted(
        item["id"] for item in all_public_rows if not item["scope_complete"]
    )
    missing_state = sorted(
        item["id"]
        for item in all_public_rows
        if not item["verification_state_complete"]
    )

    public_breakdown = {}
    for family, rows in families.items():
        public_breakdown[family] = {
            "items_total": len(rows),
            "items_complete": sum(1 for item in rows if is_complete(item)),
            "source_complete": sum(1 for item in rows if item["source_complete"]),
            "scope_complete": sum(1 for item in rows if item["scope_complete"]),
            "verification_state_complete": sum(
                1 for item in rows if item["verification_state_complete"]
            ),
        }

    relation = verification_registry["relation_verification"]
    relations_total = int(relation["inventory_relations"])
    relations_verified = int(relation["independently_verified_relations"])
    relations_remaining = int(relation["remaining_unverified_relations"])
    if relations_verified + relations_remaining != relations_total:
        raise RuntimeError("relation verification counts do not reconcile")

    return {
        "format_version": 1,
        "generated_by": "scripts/build_product_value_snapshot.py",
        "metric_spec": "data/product-value-metrics-v0.1.json",
        "service_id": default_service_id,
        "scope": {
            "public_route_mode": routing.get("current_mode"),
            "service_config": service_config_path,
            "canonical_service_scope_contract": canonical_scope["contract"],
            "public_item_families": EXPECTED_PUBLIC_FAMILIES,
            "excluded_services": [
                item["service_id"]
                for item in service_manifest["services"]
                if item["service_id"] != default_service_id
                and not bool(
                    load_json(item["config"])["routing"].get(
                        "future_service_base_enabled"
                    )
                )
            ],
        },
        "metrics": {
            "practical_questions_with_evidence_path": {
                "questions_total": len(questions),
                "questions_with_evidence_path": questions_with_evidence,
                "coverage_rate": ratio(questions_with_evidence, len(questions)),
                "missing_question_slugs": missing_question_slugs,
            },
            "public_items_with_complete_evidence_state": {
                "public_items_total": public_total,
                "public_items_complete": public_complete,
                "coverage_rate": ratio(public_complete, public_total),
                "missing_source_items": missing_source,
                "missing_scope_items": missing_scope,
                "missing_verification_state_items": missing_state,
                "breakdown": public_breakdown,
            },
            "unresolved_or_unverified_relations": {
                "relations_total": relations_total,
                "relations_independently_verified": relations_verified,
                "relations_remaining_unverified": relations_remaining,
                "remaining_rate": ratio(relations_remaining, relations_total),
                "lane_breakdown": relation.get("lanes", []),
            },
        },
        "claims_excluded": [
            "human task-time improvement",
            "human effectiveness improvement",
            "legal correctness beyond the recorded verification states",
            "verification or publication inheritance across services",
        ],
    }


def render_snapshot() -> str:
    return json.dumps(build_snapshot(), ensure_ascii=False, indent=2) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    rendered = render_snapshot()
    if args.check:
        if not OUTPUT_PATH.exists() or OUTPUT_PATH.read_text(encoding="utf-8") != rendered:
            raise SystemExit("product-value snapshot is stale; run builder")
        print("product-value snapshot: current")
        return

    OUTPUT_PATH.write_text(rendered, encoding="utf-8")
    print(f"wrote {OUTPUT_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
