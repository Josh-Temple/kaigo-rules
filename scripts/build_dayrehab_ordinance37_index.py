#!/usr/bin/env python3
"""Build the non-duplicating dayrehab Ordinance 37 index from the shared corpus."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
SERVICE_DIR = DATA / "services" / "dayrehab"
SHARED_SCOPE = DATA / "ordinance37-scope.json"
SERVICE_SCOPE = SERVICE_DIR / "ordinance37-scope.json"
OUTPUT = SERVICE_DIR / "ordinance37-index.generated.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def build() -> dict:
    shared_scope = load(SHARED_SCOPE)
    service_scope = load(SERVICE_SCOPE)
    nodes = load(DATA / "ordinance37-nodes.json")
    meta = load(DATA / "ordinance37-meta.json")

    entries = [
        item
        for item in shared_scope.get("additional_service_direct_scopes", [])
        if item.get("service_id") == "dayrehab"
    ]
    if len(entries) != 1:
        raise ValueError("shared Ordinance 37 scope must contain exactly one dayrehab direct scope")

    entry = entries[0]
    expected_articles = [str(value) for value in service_scope["direct_scope"]["article_numbers"]]
    if entry.get("articles") != expected_articles:
        raise ValueError("shared and service-specific dayrehab article lists differ")
    if entry.get("source_scope") != "data/services/dayrehab/ordinance37-scope.json":
        raise ValueError("dayrehab scope source reference changed")

    expected_set = set(expected_articles)
    selected = [row for row in nodes if str(row.get("article_num")) in expected_set]
    articles = [row for row in selected if row.get("node_type") == "article"]
    observed_articles = {str(row.get("article_num")) for row in articles}
    if observed_articles != expected_set:
        raise ValueError(
            "dayrehab Ordinance 37 article coverage mismatch: "
            f"missing={sorted(expected_set - observed_articles)} "
            f"extra={sorted(observed_articles - expected_set)}"
        )

    wrong_chapter = [
        row["id"]
        for row in articles
        if not row.get("path") or row["path"][0] != "第八章 通所リハビリテーション"
    ]
    if wrong_chapter:
        raise ValueError("dayrehab article outside Chapter 8: " + ", ".join(wrong_chapter))

    bad_applicability = [
        row["id"] for row in selected if row.get("applicable_via") is not None
    ]
    if bad_applicability:
        raise ValueError(
            "dayrehab direct-scope node unexpectedly has applicable_via: "
            + ", ".join(bad_applicability[:10])
        )

    by_type = {}
    for row in selected:
        by_type[row["node_type"]] = by_type.get(row["node_type"], 0) + 1

    return {
        "format_version": 1,
        "generated_by": "scripts/build_dayrehab_ordinance37_index.py",
        "service_id": "dayrehab",
        "layer": "ordinance37",
        "status": "INDEXED_FROM_SHARED_CORPUS",
        "source_corpus": {
            "nodes_file": "data/ordinance37-nodes.json",
            "meta_file": "data/ordinance37-meta.json",
            "law_id": meta["law_id"],
            "current_revision_id": meta["current_revision"]["law_revision_id"],
            "xml_sha256": meta["xml_sha256"],
            "corpus_review_status": meta.get("review_status"),
        },
        "scope_sources": {
            "service_scope": "data/services/dayrehab/ordinance37-scope.json",
            "shared_corpus_scope": "data/ordinance37-scope.json",
        },
        "selectors": {
            "chapter": service_scope["chapter"],
            "resolved_direct_articles": expected_articles,
        },
        "counts": {
            "selected_nodes_total": len(selected),
            "selected_articles": len(articles),
            "by_type": by_type,
        },
        "node_ids": [row["id"] for row in selected],
        "assurance": {
            "legal_text_duplicated": False,
            "service_specific_independent_verification": "SEPARATE_LANE",
            "human_review": "NOT_REVIEWED",
            "automatic_verification_promotion_allowed": False,
        },
    }


def render(payload: dict) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    rendered = render(build())
    if args.check:
        if not OUTPUT.exists() or OUTPUT.read_text(encoding="utf-8") != rendered:
            raise SystemExit("dayrehab Ordinance 37 index is stale; run builder")
        print("dayrehab Ordinance 37 index: current")
        return
    OUTPUT.write_text(rendered, encoding="utf-8")
    print(f"wrote {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
