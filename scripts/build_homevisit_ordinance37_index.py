#!/usr/bin/env python3
"""Build a non-public homevisit Ordinance 37 reference index.

The index stores node IDs only. Legal text remains in the shared Ordinance 37
corpus, and no homevisit verification/publication state is promoted.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
SERVICE_DIR = DATA / "services" / "homevisit"
SHARED_SCOPE = DATA / "ordinance37-scope.json"
OUTPUT = SERVICE_DIR / "ordinance37-index.generated.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def build() -> dict:
    service_scope = load(SERVICE_DIR / "ordinance37-scope.json")
    nodes = load(DATA / "ordinance37-nodes.json")
    meta = load(DATA / "ordinance37-meta.json")

    article_range = service_scope.get("direct_scope", {}).get("article_range", {})
    start = str(article_range.get("start", ""))
    end = str(article_range.get("end", ""))
    if not start or not end or article_range.get("include_inserted_articles") is not True:
        raise ValueError("homevisit service scope must declare an inserted-article range")

    def article_key(value: str) -> tuple[int, ...]:
        try:
            return tuple(int(part) for part in value.split("-"))
        except ValueError as exc:
            raise ValueError(f"homevisit non-numeric article number: {value}") from exc

    start_key = article_key(start)
    end_key = article_key(end)
    article_numbers = sorted(
        {
            str(row.get("article_num"))
            for row in nodes
            if row.get("node_type") == "article"
            and row.get("path")
            and row["path"][0] == "第二章 訪問介護"
            and start_key <= article_key(str(row.get("article_num"))) <= end_key
        },
        key=article_key,
    )
    if not article_numbers:
        raise ValueError("homevisit direct article range resolved to no shared-corpus articles")

    selected = [
        row for row in nodes if str(row.get("article_num")) in set(article_numbers)
    ]
    articles = [row for row in selected if row.get("node_type") == "article"]
    observed_articles = {str(row.get("article_num")) for row in articles}
    expected_articles = set(article_numbers)
    if observed_articles != expected_articles:
        raise ValueError(
            "homevisit Ordinance 37 article coverage mismatch: "
            f"missing={sorted(expected_articles - observed_articles)} "
            f"extra={sorted(observed_articles - expected_articles)}"
        )

    wrong_chapter = [
        row["id"]
        for row in articles
        if not row.get("path") or row["path"][0] != "第二章 訪問介護"
    ]
    if wrong_chapter:
        raise ValueError(
            "homevisit Ordinance 37 article outside Chapter 2: "
            + ", ".join(wrong_chapter)
        )

    if service_scope.get("chapter", {}).get("number") != "2":
        raise ValueError("homevisit service scope chapter changed from Chapter 2")

    by_type = {}
    for row in selected:
        by_type[row["node_type"]] = by_type.get(row["node_type"], 0) + 1

    return {
        "format_version": 1,
        "generated_by": "scripts/build_homevisit_ordinance37_index.py",
        "service_id": "homevisit",
        "layer": "ordinance37",
        "status": "INDEXED_FROM_SHARED_CORPUS_NOT_SERVICE_VERIFIED",
        "source_corpus": {
            "nodes_file": "data/ordinance37-nodes.json",
            "meta_file": "data/ordinance37-meta.json",
            "law_id": meta["law_id"],
            "current_revision_id": meta["current_revision"]["law_revision_id"],
            "xml_sha256": meta["xml_sha256"],
            "corpus_review_status": meta.get("review_status"),
        },
        "scope_sources": {
            "service_scope": "data/services/homevisit/ordinance37-scope.json",
            "shared_corpus_nodes": "data/ordinance37-nodes.json",
        },
        "selectors": {
            "chapter": service_scope["chapter"],
            "resolved_direct_articles": article_numbers,
        },
        "counts": {
            "selected_nodes_total": len(selected),
            "selected_articles": len(articles),
            "by_type": by_type,
        },
        "node_ids": [row["id"] for row in selected],
        "assurance": {
            "legal_text_duplicated": False,
            "service_specific_independent_verification": "NOT_RUN",
            "service_specific_currentness_verification": "NOT_RUN",
            "human_review": "NOT_RUN",
            "automatic_verification_promotion_allowed": False,
            "note": (
                "The shared corpus has an independent e-Gov content audit lane, "
                "but this index alone does not promote homevisit verification."
            ),
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
        if not OUTPUT.exists():
            raise SystemExit("homevisit Ordinance 37 index missing; run builder")
        if OUTPUT.read_text(encoding="utf-8") != rendered:
            raise SystemExit("homevisit Ordinance 37 index is stale; run builder")
        print("homevisit Ordinance 37 index: current")
        return

    OUTPUT.write_text(rendered, encoding="utf-8")
    print(f"wrote {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
