#!/usr/bin/env python3
"""Independently verify existing Ordinance 37 service slices against live e-Gov XML.

This verifier is intentionally read-only with respect to canonical data. It checks
item bodies, node identity/containment, source identity, and whether each declared
direct article belongs to the declared service chapter. It does not promote
currentness, human review, publication, or route exposure.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

from verify_egov_content_independent import (
    canonical_num,
    collect_article_order,
    collect_scoped,
    elements,
    fetch,
    first_descendant,
    first_direct,
    text_of,
)

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
LAW_ID = "411M50000100037"
SOURCE_URL = f"https://laws.e-gov.go.jp/api/1/lawdata/{LAW_ID}"

TARGETS = [
    ("dayservice", "通所介護"),
    ("homevisit", "訪問介護"),
    ("homebath", "訪問入浴介護"),
    ("homenursing", "訪問看護"),
    ("homerehab", "訪問リハビリテーション"),
    ("homecaremanagement", "居宅療養管理指導"),
    ("dayrehab", "通所リハビリテーション"),
    ("shortstay-life", "短期入所生活介護"),
    ("shortstay-medical", "短期入所療養介護"),
    ("specific-facility", "特定施設入居者生活介護"),
    ("welfare-equipment-rental", "福祉用具貸与"),
    ("specific-welfare-equipment-sale", "特定福祉用具販売"),
]


def load(relative: str):
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def normalize(value: str | None) -> str:
    return " ".join(str(value or "").split())


def article_num_from_id(node_id: str) -> str:
    prefix = "ordinance37.article."
    if not node_id.startswith(prefix):
        raise ValueError(f"unexpected Ordinance 37 article id: {node_id}")
    suffix = node_id[len(prefix):]
    if not suffix or "." in suffix:
        raise ValueError(f"not an article-level Ordinance 37 id: {node_id}")
    return canonical_num(suffix)


def live_chapter_map(main_provision) -> dict[str, dict[str, str]]:
    mapping: dict[str, dict[str, str]] = {}

    def walk(node, chapter: dict[str, str] | None = None) -> None:
        current = chapter
        if getattr(node, "tagName", None) == "Chapter":
            current = {
                "number": canonical_num(node.getAttribute("Num")),
                "title": normalize(text_of(first_direct(node, "ChapterTitle"))),
            }
        for child in elements(node):
            if child.tagName in {"TOC", "SupplProvision", "AmendProvision", "NewProvision"}:
                continue
            if child.tagName == "Article":
                num = canonical_num(child.getAttribute("Num"))
                if num:
                    mapping[num] = dict(current or {})
                continue
            walk(child, current)

    walk(main_provision)
    return mapping


def resolve_homevisit_articles(main_provision, differences: list[dict]) -> list[str]:
    scope = load("data/services/homevisit/ordinance37-scope.json")
    article_range = scope.get("direct_scope", {}).get("article_range", {})
    start = canonical_num(article_range.get("start"))
    end = canonical_num(article_range.get("end"))
    order = collect_article_order(main_provision)
    positions = {num: i for i, num in enumerate(order)}
    if start not in positions or end not in positions or positions[start] > positions[end]:
        differences.append({
            "difference": "homevisit_live_range_unresolvable",
            "start": start,
            "end": end,
        })
        return []
    resolved = order[positions[start] : positions[end] + 1]

    index = load("data/services/homevisit/ordinance37-index.generated.json")
    indexed = [
        canonical_num(value)
        for value in index.get("selectors", {}).get("resolved_direct_articles", [])
    ]
    if indexed != resolved:
        differences.append({
            "difference": "homevisit_index_article_mismatch",
            "indexed": indexed,
            "live_resolved": resolved,
        })
    return resolved


def scope_for_service(service_id: str) -> dict:
    if service_id == "dayservice":
        return load("data/ordinance37-scope.json")
    return load(f"data/services/{service_id}/ordinance37-scope.json")


def declared_articles(service_id: str, main_provision, differences: list[dict]) -> list[str]:
    if service_id == "dayservice":
        scope = scope_for_service(service_id)
        articles = [canonical_num(value) for value in scope.get("direct_articles", [])]
        if not articles:
            differences.append({"difference": "declared_direct_articles_missing"})
        return articles
    if service_id == "homevisit":
        return resolve_homevisit_articles(main_provision, differences)
    scope = scope_for_service(service_id)
    direct_scope = scope.get("direct_scope", {})
    article_ids = direct_scope.get("article_ids", [])
    if article_ids:
        return [article_num_from_id(value) for value in article_ids]
    articles = [canonical_num(value) for value in direct_scope.get("article_numbers", [])]
    if not articles:
        differences.append({"difference": "declared_direct_articles_missing"})
    return articles


def chapter_matches(scope: dict, observed: dict[str, str]) -> bool:
    expected = normalize(scope.get("chapter", {}).get("title") or scope.get("service"))
    actual = normalize(observed.get("title"))
    if not expected or not actual:
        return False
    if expected == actual:
        return True
    # The legacy homevisit scope stores only the service name while e-Gov
    # ChapterTitle contains the chapter ordinal as well.
    return actual.endswith(" " + expected) or actual.endswith(expected)


def compare_service(
    service_id: str,
    service_label: str,
    main_provision,
    chapter_by_article: dict[str, dict[str, str]],
    committed_nodes: list[dict],
    committed_relations: list[dict],
    shared_source_differences: list[dict],
) -> dict:
    differences = [dict(item) for item in shared_source_differences]
    scope = scope_for_service(service_id)
    target_articles = declared_articles(service_id, main_provision, differences)
    target_set = set(target_articles)

    declared_law_id = scope.get("law_id")
    if declared_law_id is not None and declared_law_id != LAW_ID:
        differences.append({
            "difference": "service_scope_law_id_mismatch",
            "expected": LAW_ID,
            "observed": declared_law_id,
        })

    service_map = load("data/shared/standards/service-ordinance-map.json")
    mappings = [
        row for row in service_map.get("relations", [])
        if row.get("service_id") == service_id
    ]
    if len(mappings) != 1 or mappings[0].get("corpus_id") != "ordinance37":
        differences.append({
            "difference": "service_to_standards_corpus_mapping_mismatch",
            "expected": "ordinance37",
            "observed": [row.get("corpus_id") for row in mappings],
        })

    chapter_observations = {}
    for article in target_articles:
        observed_chapter = chapter_by_article.get(article, {})
        chapter_observations[article] = observed_chapter
        if not chapter_matches(scope, observed_chapter):
            differences.append({
                "difference": "declared_article_outside_declared_chapter",
                "article": article,
                "declared_chapter": scope.get("chapter"),
                "observed_chapter": observed_chapter,
            })

    expected_nodes = {
        row["id"]: row
        for row in committed_nodes
        if canonical_num(row.get("article_num")) in target_set
    }
    expected_ids = set(expected_nodes)
    expected_contains = {
        (row["from"], row["to"])
        for row in committed_relations
        if row.get("relation") == "contains"
        and row.get("from") in expected_ids
        and row.get("to") in expected_ids
    }

    if target_articles:
        observed_nodes, observed_contains = collect_scoped(
            main_provision, target_set, "ordinance37"
        )
    else:
        observed_nodes, observed_contains = {}, set()

    observed_ids = set(observed_nodes)
    for node_id in sorted(expected_ids - observed_ids):
        differences.append({"id": node_id, "difference": "missing_from_independent_reparse"})
    for node_id in sorted(observed_ids - expected_ids):
        differences.append({"id": node_id, "difference": "unexpected_in_independent_reparse"})

    for node_id in sorted(expected_ids & observed_ids):
        expected = expected_nodes[node_id]
        observed = observed_nodes[node_id]
        for field in ("node_type", "article_num", "paragraph_num", "parent_id"):
            if expected.get(field) != observed.get(field):
                differences.append({
                    "id": node_id,
                    "difference": f"{field}_mismatch",
                    "expected": expected.get(field),
                    "observed": observed.get(field),
                })
        expected_text = normalize(expected.get("official_text"))
        observed_text = normalize(observed.get("official_text"))
        if expected_text != observed_text:
            differences.append({
                "id": node_id,
                "difference": "official_text_mismatch",
                "expected_sha256": hashlib.sha256(expected_text.encode()).hexdigest(),
                "observed_sha256": hashlib.sha256(observed_text.encode()).hexdigest(),
            })

    for edge in sorted(expected_contains - observed_contains):
        differences.append({
            "from": edge[0],
            "to": edge[1],
            "difference": "missing_contains_relation",
        })
    for edge in sorted(observed_contains - expected_contains):
        differences.append({
            "from": edge[0],
            "to": edge[1],
            "difference": "unexpected_contains_relation",
        })

    return {
        "service_id": service_id,
        "service_label": service_label,
        "result": "PASS" if not differences else "FAIL",
        "target_articles": target_articles,
        "declared_chapter": scope.get("chapter"),
        "observed_chapters": sorted({
            normalize(value.get("title"))
            for value in chapter_observations.values()
            if value.get("title")
        }),
        "observed": {
            "nodes": len(observed_nodes),
            "articles": sum(
                1 for row in observed_nodes.values() if row.get("node_type") == "article"
            ),
            "paragraphs": sum(
                1 for row in observed_nodes.values() if row.get("node_type") == "paragraph"
            ),
            "items": sum(
                1 for row in observed_nodes.values() if row.get("node_type") == "item"
            ),
            "subitems": sum(
                1 for row in observed_nodes.values() if row.get("node_type") == "subitem"
            ),
            "contains_relations": len(observed_contains),
        },
        "expected": {
            "nodes": len(expected_nodes),
            "contains_relations": len(expected_contains),
        },
        "differences": differences,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report")
    args = parser.parse_args()

    meta = load("data/ordinance37-meta.json")
    committed_nodes = load("data/ordinance37-nodes.json")
    committed_relations = load("data/ordinance37-relations.json")

    payload = fetch(SOURCE_URL)
    observed_sha = hashlib.sha256(payload).hexdigest()
    document = __import__("xml.dom.minidom", fromlist=["minidom"]).parseString(payload)
    law = first_descendant(document, "Law")
    main_provision = first_descendant(law, "MainProvision") if law else None
    if main_provision is None:
        raise RuntimeError("MainProvision not found")

    source_differences = []
    if meta.get("law_id") != LAW_ID:
        source_differences.append({
            "difference": "committed_meta_law_id_mismatch",
            "expected": LAW_ID,
            "observed": meta.get("law_id"),
        })
    if observed_sha != meta.get("xml_sha256"):
        source_differences.append({
            "difference": "live_xml_sha256_differs_from_committed_meta",
            "expected": meta.get("xml_sha256"),
            "observed": observed_sha,
        })

    chapter_by_article = live_chapter_map(main_provision)
    services = [
        compare_service(
            service_id,
            label,
            main_provision,
            chapter_by_article,
            committed_nodes,
            committed_relations,
            source_differences,
        )
        for service_id, label in TARGETS
    ]

    result = "PASS" if all(row["result"] == "PASS" for row in services) else "FAIL"
    report = {
        "format_version": 1,
        "layer": "ordinance37",
        "verification_kind": "INDEPENDENT_EGOV_SERVICE_SLICE_REPARSE",
        "source": {
            "law_id": LAW_ID,
            "url": SOURCE_URL,
            "observed_xml_sha256": observed_sha,
            "committed_xml_sha256": meta.get("xml_sha256"),
            "current_revision_id": meta.get("current_revision", {}).get("law_revision_id"),
        },
        "result": result,
        "services": services,
        "summary": {
            "services_total": len(services),
            "services_pass": sum(row["result"] == "PASS" for row in services),
            "services_fail": sum(row["result"] != "PASS" for row in services),
            "discrepancies": sum(len(row["differences"]) for row in services),
        },
        "safety": {
            "promotes_currentness": False,
            "promotes_human_review": False,
            "promotes_publication": False,
            "promotes_route_exposure": False,
            "semantic_or_cross_layer_relations_audited": False,
            "automatic_promotion_allowed": False,
        },
    }
    rendered = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    print(rendered, end="")
    if args.report:
        path = Path(args.report)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(rendered, encoding="utf-8")
    return 0 if result == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
