#!/usr/bin/env python3
"""Build the non-duplicating shortstay-life Ordinance 37 index from the shared corpus."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
SERVICE_DIR = DATA / "services" / "shortstay-life"
SHARED_SCOPE = DATA / "ordinance37-scope.json"
SERVICE_SCOPE = SERVICE_DIR / "ordinance37-scope.json"
OUTPUT = SERVICE_DIR / "ordinance37-index.generated.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def article_key(value: str):
    return tuple(int(part) for part in str(value).split("-"))


def build() -> dict:
    shared_scope = load(SHARED_SCOPE)
    service_scope = load(SERVICE_SCOPE)
    nodes = load(DATA / "ordinance37-nodes.json")
    meta = load(DATA / "ordinance37-meta.json")

    entries = [
        item
        for item in shared_scope.get("additional_service_direct_scopes", [])
        if item.get("service_id") == "shortstay-life"
    ]
    if len(entries) != 1:
        raise ValueError(
            "shared Ordinance 37 scope must contain exactly one shortstay-life direct scope"
        )

    current_articles = [
        str(value)
        for value in service_scope["direct_scope"]["current_text_articles"]
    ]
    deleted_slots = [
        str(value)
        for value in service_scope["direct_scope"]["deleted_article_slots"]
    ]
    if entries[0].get("articles") != current_articles:
        raise ValueError("shared and service-specific shortstay-life current article lists differ")
    if len(current_articles) != 42 or len(set(current_articles)) != 42:
        raise ValueError("shortstay-life must contain 42 unique current-text articles")
    if deleted_slots != [f"140-{value}" for value in range(16, 26)]:
        raise ValueError("shortstay-life deleted slots must be 140-16 through 140-25")
    if set(current_articles) & set(deleted_slots):
        raise ValueError("current and deleted shortstay-life article slots overlap")

    current_set = set(current_articles)
    selected = [
        row for row in nodes if str(row.get("article_num")) in current_set
    ]
    article_nodes = [row for row in selected if row.get("node_type") == "article"]
    observed = {str(row.get("article_num")) for row in article_nodes}
    if observed != current_set:
        raise ValueError(
            "shortstay-life Ordinance 37 coverage mismatch: "
            f"missing={sorted(current_set-observed, key=article_key)} "
            f"extra={sorted(observed-current_set, key=article_key)}"
        )

    wrong_chapter = [
        row["id"]
        for row in article_nodes
        if not row.get("path") or row["path"][0] != "第九章 短期入所生活介護"
    ]
    if wrong_chapter:
        raise ValueError(
            "shortstay-life Ordinance 37 article outside Chapter 9: "
            + ", ".join(wrong_chapter)
        )

    by_type = {}
    for row in selected:
        by_type[row["node_type"]] = by_type.get(row["node_type"], 0) + 1

    return {
        "format_version": 1,
        "generated_by": "scripts/build_shortstay_life_ordinance37_index.py",
        "service_id": "shortstay-life",
        "layer": "ordinance37",
        "status": "DIRECT_TEXT_INDEXED_FROM_SHARED_CORPUS_RELATIONS_UNVERIFIED",
        "source_corpus": {
            "nodes_file": "data/ordinance37-nodes.json",
            "meta_file": "data/ordinance37-meta.json",
            "law_id": meta["law_id"],
            "current_revision_id": meta["current_revision"]["law_revision_id"],
            "xml_sha256": meta["xml_sha256"],
            "corpus_review_status": meta.get("review_status"),
        },
        "scope_sources": {
            "service_scope": "data/services/shortstay-life/ordinance37-scope.json",
            "shared_corpus_scope": "data/ordinance37-scope.json",
        },
        "selectors": {
            "chapter": service_scope["chapter"],
            "resolved_current_text_articles": current_articles,
            "deleted_article_slots": deleted_slots,
        },
        "counts": {
            "addressable_article_slots": len(current_articles) + len(deleted_slots),
            "current_text_articles": len(article_nodes),
            "deleted_article_slots": len(deleted_slots),
            "selected_nodes_total": len(selected),
            "by_type": by_type,
        },
        "node_ids": [row["id"] for row in selected],
        "assurance": {
            "legal_text_duplicated": False,
            "deleted_historical_text_fabricated": False,
            "shared_corpus_independent_verification": "data/egov-content-independent-audit.json",
            "service_specific_relation_verification": "NOT_RUN",
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
            raise SystemExit("shortstay-life Ordinance 37 index is stale; run builder")
        print("shortstay-life Ordinance 37 index: current")
        return
    OUTPUT.write_text(rendered, encoding="utf-8")
    print(f"wrote {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
