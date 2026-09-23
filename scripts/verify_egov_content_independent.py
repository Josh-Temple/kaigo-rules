#!/usr/bin/env python3
"""Independently reparse scoped e-Gov law content with xml.dom.minidom.

Production importers use xml.etree.ElementTree. This verifier intentionally uses
another XML implementation and reconstructs only source-derived node text and
containment edges. Hand-authored cross-layer/legal-semantic relations are out
of scope and remain separately reviewable.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import urllib.request
from pathlib import Path
from xml.dom import Node, minidom

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

TARGETS = [
    {
        "id": "ordinance37",
        "prefix": "ordinance37",
        "scope_file": "ordinance37-scope.json",
        "nodes_file": "ordinance37-nodes.json",
        "relations_file": "ordinance37-relations.json",
        "meta_file": "ordinance37-meta.json",
        "law_id": "411M50000100037",
    },
    {
        "id": "care-insurance-act",
        "prefix": "careact",
        "scope_file": "care-insurance-act-scope.json",
        "nodes_file": "care-insurance-act-nodes.json",
        "relations_file": "care-insurance-act-relations.json",
        "meta_file": "care-insurance-act-meta.json",
        "law_id": "409AC0000000123",
    },
]

SKIP_TAGS = {"TOC", "SupplProvision", "AmendProvision", "NewProvision"}


def fetch(url: str) -> bytes:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "kaigo-rules-independent-egov-verifier/1.0 (+https://github.com/Josh-Temple/kaigo-rules)"
        },
    )
    with urllib.request.urlopen(req, timeout=90) as response:
        return response.read()


def load(name: str):
    return json.loads((DATA / name).read_text(encoding="utf-8"))


def elements(node, name: str | None = None):
    return [
        child
        for child in node.childNodes
        if child.nodeType == Node.ELEMENT_NODE and (name is None or child.tagName == name)
    ]


def first_direct(node, name: str):
    for child in elements(node):
        if child.tagName == name:
            return child
    return None


def first_descendant(node, name: str):
    found = node.getElementsByTagName(name)
    return found[0] if found else None


def text_of(node) -> str:
    if node is None:
        return ""
    chunks: list[str] = []

    def walk(current):
        for child in current.childNodes:
            if child.nodeType in (Node.TEXT_NODE, Node.CDATA_SECTION_NODE):
                chunks.append(child.data)
            elif child.nodeType == Node.ELEMENT_NODE:
                walk(child)

    walk(node)
    return " ".join("".join(chunks).split())


def canonical_num(value: str | None) -> str:
    return str(value or "").strip().replace("_", "-")


def body_from(container, sentence_tag: str) -> str:
    return text_of(first_direct(container, sentence_tag))


def add_item_tree(parent, parent_id: str, article: str, paragraph: str, nodes: dict, contains: set):
    tag_levels = {f"Subitem{i}": f"s{i}" for i in range(1, 11)}
    for child in elements(parent):
        if child.tagName == "Item":
            level = "i"
            sentence_tag = "ItemSentence"
            node_type = "item"
        elif child.tagName in tag_levels:
            level = tag_levels[child.tagName]
            sentence_tag = child.tagName + "Sentence"
            node_type = "subitem"
        else:
            continue

        num = canonical_num(child.getAttribute("Num"))
        node_id = f"{parent_id}.{level}.{num}"
        body = body_from(child, sentence_tag) or text_of(child)
        nodes[node_id] = {
            "id": node_id,
            "node_type": node_type,
            "article_num": article,
            "paragraph_num": paragraph,
            "official_text": body,
            "parent_id": parent_id,
        }
        contains.add((parent_id, node_id))
        add_item_tree(child, node_id, article, paragraph, nodes, contains)


def parse_article(article, prefix: str, nodes: dict, contains: set):
    article_num = canonical_num(article.getAttribute("Num"))
    article_id = f"{prefix}.article.{article_num}"
    nodes[article_id] = {
        "id": article_id,
        "node_type": "article",
        "article_num": article_num,
        "paragraph_num": None,
        "official_text": text_of(article),
        "parent_id": None,
    }

    for paragraph in elements(article, "Paragraph"):
        pnum = canonical_num(paragraph.getAttribute("Num"))
        paragraph_id = f"{article_id}.p.{pnum}"
        body = body_from(paragraph, "ParagraphSentence")
        nodes[paragraph_id] = {
            "id": paragraph_id,
            "node_type": "paragraph",
            "article_num": article_num,
            "paragraph_num": pnum,
            "official_text": body,
            "parent_id": article_id,
        }
        contains.add((article_id, paragraph_id))
        add_item_tree(paragraph, paragraph_id, article_num, pnum, nodes, contains)


def collect_scoped(main_provision, target_articles: set[str], prefix: str):
    nodes: dict[str, dict] = {}
    contains: set[tuple[str, str]] = set()
    found: set[str] = set()

    def walk(node):
        for child in elements(node):
            if child.tagName in SKIP_TAGS:
                continue
            if child.tagName == "Article":
                num = canonical_num(child.getAttribute("Num"))
                if num in target_articles:
                    parse_article(child, prefix, nodes, contains)
                    found.add(num)
                continue
            walk(child)

    walk(main_provision)
    missing = sorted(target_articles - found)
    if missing:
        raise RuntimeError("target articles missing from live e-Gov XML: " + ", ".join(missing))
    return nodes, contains


def compare_target(config: dict) -> dict:
    scope = load(config["scope_file"])
    meta = load(config["meta_file"])
    expected_nodes = load(config["nodes_file"])
    expected_relations = load(config["relations_file"])

    if config["id"] == "ordinance37":
        target_articles = set(scope["direct_articles"]) | set(scope["incorporated_articles"])
    else:
        target_articles = set(scope["articles"])

    url = f"https://laws.e-gov.go.jp/api/1/lawdata/{config['law_id']}"
    payload = fetch(url)
    observed_sha = hashlib.sha256(payload).hexdigest()
    document = minidom.parseString(payload)
    law = first_descendant(document, "Law")
    if law is None:
        raise RuntimeError("Law element not found")
    main_provision = first_descendant(law, "MainProvision")
    if main_provision is None:
        raise RuntimeError("MainProvision not found")

    observed_nodes, observed_contains = collect_scoped(
        main_provision, target_articles, config["prefix"]
    )
    expected_by_id = {row["id"]: row for row in expected_nodes}
    expected_contains = {
        (row["from"], row["to"])
        for row in expected_relations
        if row.get("relation") == "contains"
    }

    differences: list[dict] = []
    observed_ids = set(observed_nodes)
    expected_ids = set(expected_by_id)

    for node_id in sorted(expected_ids - observed_ids):
        differences.append({"id": node_id, "difference": "missing_from_independent_reparse"})
    for node_id in sorted(observed_ids - expected_ids):
        differences.append({"id": node_id, "difference": "unexpected_in_independent_reparse"})

    for node_id in sorted(observed_ids & expected_ids):
        observed = observed_nodes[node_id]
        expected = expected_by_id[node_id]
        for field in ("node_type", "article_num", "paragraph_num", "parent_id"):
            if observed.get(field) != expected.get(field):
                differences.append(
                    {
                        "id": node_id,
                        "difference": f"{field}_mismatch",
                        "expected": expected.get(field),
                        "observed": observed.get(field),
                    }
                )
        expected_text = " ".join(str(expected.get("official_text", "")).split())
        if observed["official_text"] != expected_text:
            differences.append(
                {
                    "id": node_id,
                    "difference": "official_text_mismatch",
                    "expected_sha256": hashlib.sha256(expected_text.encode("utf-8")).hexdigest(),
                    "observed_sha256": hashlib.sha256(observed["official_text"].encode("utf-8")).hexdigest(),
                }
            )

    missing_contains = sorted(expected_contains - observed_contains)
    unexpected_contains = sorted(observed_contains - expected_contains)
    for parent, child in missing_contains:
        differences.append(
            {"from": parent, "to": child, "difference": "missing_contains_relation"}
        )
    for parent, child in unexpected_contains:
        differences.append(
            {"from": parent, "to": child, "difference": "unexpected_contains_relation"}
        )

    if observed_sha != meta.get("xml_sha256"):
        differences.append(
            {
                "difference": "live_xml_sha256_differs_from_committed_meta",
                "expected": meta.get("xml_sha256"),
                "observed": observed_sha,
            }
        )

    result = "PASS" if not differences else "FAIL"
    return {
        "id": config["id"],
        "law_id": config["law_id"],
        "source_url": url,
        "observed_xml_sha256": observed_sha,
        "result": result,
        "observed": {
            "nodes": len(observed_nodes),
            "articles": sum(1 for row in observed_nodes.values() if row["node_type"] == "article"),
            "paragraphs": sum(1 for row in observed_nodes.values() if row["node_type"] == "paragraph"),
            "items": sum(1 for row in observed_nodes.values() if row["node_type"] == "item"),
            "subitems": sum(1 for row in observed_nodes.values() if row["node_type"] == "subitem"),
            "contains_relations": len(observed_contains),
        },
        "expected": {
            "nodes": len(expected_nodes),
            "contains_relations": len(expected_contains),
        },
        "differences": differences,
        "excluded_from_audit": {
            "non_contains_relations": len(expected_relations) - len(expected_contains),
            "reason": "Hand-authored legal-semantic/cross-layer mappings are not source-derived XML containment and are not promoted by this audit.",
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", help="Optional JSON report path")
    args = parser.parse_args()

    checks = []
    errors = []
    for config in TARGETS:
        try:
            checks.append(compare_target(config))
        except Exception as exc:
            errors.append({"id": config["id"], "error": str(exc)})

    result = (
        "PASS"
        if not errors and len(checks) == len(TARGETS) and all(row["result"] == "PASS" for row in checks)
        else "FAIL"
    )
    report = {
        "format_version": 1,
        "verification_kind": "INDEPENDENT_EGOV_CONTENT_REPARSE",
        "parser": "python_xml_dom_minidom",
        "result": result,
        "checks": checks,
        "errors": errors,
        "safety": {
            "promotes_human_review": False,
            "promotes_verified_current": False,
            "semantic_relations_audited": False,
            "note": "This verifier independently checks live e-Gov scoped text and containment only.",
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
