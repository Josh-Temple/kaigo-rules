#!/usr/bin/env python3
"""Independently verify the dayrehab Ordinance 37 shared-corpus slice against live e-Gov XML."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from xml.dom import minidom

from verify_egov_content_independent import (
    collect_scoped,
    fetch,
    first_descendant,
)

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
LAW_ID = "411M50000100037"


def load(relative: str):
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report")
    args = parser.parse_args()

    scope = load("data/services/dayrehab/ordinance37-scope.json")
    index = load("data/services/dayrehab/ordinance37-index.generated.json")
    nodes = load("data/ordinance37-nodes.json")
    relations = load("data/ordinance37-relations.json")
    meta = load("data/ordinance37-meta.json")

    target_articles = set(scope["direct_scope"]["article_numbers"])
    indexed_ids = set(index["node_ids"])
    expected_nodes = {row["id"]: row for row in nodes if row["id"] in indexed_ids}
    expected_contains = {
        (row["from"], row["to"])
        for row in relations
        if row.get("relation") == "contains"
        and row.get("from") in indexed_ids
        and row.get("to") in indexed_ids
    }

    url = f"https://laws.e-gov.go.jp/api/1/lawdata/{LAW_ID}"
    payload = fetch(url)
    observed_sha = hashlib.sha256(payload).hexdigest()
    document = minidom.parseString(payload)
    law = first_descendant(document, "Law")
    main_provision = first_descendant(law, "MainProvision") if law else None
    if main_provision is None:
        raise RuntimeError("MainProvision not found")

    observed_nodes, observed_contains = collect_scoped(
        main_provision, target_articles, "ordinance37"
    )

    differences = []
    expected_ids = set(expected_nodes)
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
        expected_text = " ".join(str(expected.get("official_text", "")).split())
        if expected_text != observed["official_text"]:
            differences.append({
                "id": node_id,
                "difference": "official_text_mismatch",
                "expected_sha256": hashlib.sha256(expected_text.encode()).hexdigest(),
                "observed_sha256": hashlib.sha256(observed["official_text"].encode()).hexdigest(),
            })

    for edge in sorted(expected_contains - observed_contains):
        differences.append({"from": edge[0], "to": edge[1], "difference": "missing_contains_relation"})
    for edge in sorted(observed_contains - expected_contains):
        differences.append({"from": edge[0], "to": edge[1], "difference": "unexpected_contains_relation"})

    if observed_sha != meta.get("xml_sha256"):
        differences.append({
            "difference": "live_xml_sha256_differs_from_committed_meta",
            "expected": meta.get("xml_sha256"),
            "observed": observed_sha,
        })

    result = "PASS" if not differences else "FAIL"
    report = {
        "format_version": 1,
        "service_id": "dayrehab",
        "layer": "ordinance37",
        "verification_kind": "INDEPENDENT_EGOV_CONTENT_REPARSE",
        "parser": "python_xml_dom_minidom",
        "source_url": url,
        "result": result,
        "target_articles": scope["direct_scope"]["article_numbers"],
        "observed_xml_sha256": observed_sha,
        "current_revision_id": meta["current_revision"]["law_revision_id"],
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
        "safety": {
            "promotes_human_review": False,
            "promotes_verified_current": False,
            "semantic_relations_audited": False,
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
