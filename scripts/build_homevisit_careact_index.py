#!/usr/bin/env python3
"""Build a non-public homevisit Care Insurance Act reference index.

The index intentionally stores node IDs only. It reuses the shared legal corpus
without copying legal text and does not promote any homevisit verification state.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
SERVICE_DIR = DATA / "services" / "homevisit"
OUTPUT = SERVICE_DIR / "care-insurance-act-index.generated.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def build() -> dict:
    scope = load(SERVICE_DIR / "care-insurance-act-scope.json")
    shared_core = load(ROOT / scope["shared_core"])
    nodes = load(DATA / "care-insurance-act-nodes.json")
    meta = load(DATA / "care-insurance-act-meta.json")

    if scope["law_id"] != meta["law_id"]:
        raise ValueError("homevisit Care Insurance Act law_id differs from shared corpus")

    definition = scope["service_definition"]
    definition_article = str(definition["article"])
    definition_paragraphs = {str(value) for value in definition["paragraphs"]}

    definition_nodes = [
        row
        for row in nodes
        if str(row.get("article_num")) == definition_article
        and (
            row.get("node_type") == "article"
            or (
                row.get("node_type") == "paragraph"
                and str(row.get("paragraph_num")) in definition_paragraphs
            )
        )
    ]

    found_definition_paragraphs = {
        str(row.get("paragraph_num"))
        for row in definition_nodes
        if row.get("node_type") == "paragraph"
    }
    if found_definition_paragraphs != definition_paragraphs:
        raise ValueError(
            "homevisit service definition paragraphs missing from shared corpus: "
            f"expected={sorted(definition_paragraphs)} "
            f"found={sorted(found_definition_paragraphs)}"
        )
    if not any(row.get("node_type") == "article" for row in definition_nodes):
        raise ValueError("homevisit service definition article node missing")

    shared_articles = [str(value) for value in shared_core["articles"]]
    shared_article_set = set(shared_articles)
    shared_nodes = [
        row for row in nodes if str(row.get("article_num")) in shared_article_set
    ]
    present_shared_articles = {
        str(row.get("article_num"))
        for row in shared_nodes
        if row.get("node_type") == "article"
    }
    missing_shared_articles = [
        article for article in shared_articles if article not in present_shared_articles
    ]
    if missing_shared_articles:
        raise ValueError(
            "homevisit shared core articles missing from shared corpus: "
            + ", ".join(missing_shared_articles)
        )

    selected_ids = {
        row["id"] for row in definition_nodes + shared_nodes
    }
    all_selected_nodes = [row for row in nodes if row["id"] in selected_ids]

    return {
        "format_version": 1,
        "generated_by": "scripts/build_homevisit_careact_index.py",
        "service_id": "homevisit",
        "layer": "care_insurance_act",
        "status": "INDEXED_FROM_SHARED_CORPUS_NOT_SERVICE_VERIFIED",
        "source_corpus": {
            "nodes_file": "data/care-insurance-act-nodes.json",
            "meta_file": "data/care-insurance-act-meta.json",
            "law_id": meta["law_id"],
            "current_revision_id": meta["current_revision"]["law_revision_id"],
            "xml_sha256": meta["xml_sha256"],
            "corpus_review_status": meta.get("review_status"),
        },
        "scope_sources": {
            "service_scope": "data/services/homevisit/care-insurance-act-scope.json",
            "shared_core": scope["shared_core"],
        },
        "selectors": {
            "service_definition": {
                "article": definition_article,
                "paragraphs": sorted(definition_paragraphs, key=int),
            },
            "shared_core_articles": shared_articles,
        },
        "counts": {
            "service_definition_nodes": len(definition_nodes),
            "shared_core_nodes": len(shared_nodes),
            "selected_nodes_total": len(all_selected_nodes),
        },
        "node_ids": {
            "service_definition": [row["id"] for row in definition_nodes],
            "shared_core": [row["id"] for row in shared_nodes],
            "all": [row["id"] for row in all_selected_nodes],
        },
        "assurance": {
            "legal_text_duplicated": False,
            "service_specific_independent_verification": "NOT_RUN",
            "service_specific_currentness_verification": "NOT_RUN",
            "human_review": "NOT_RUN",
            "automatic_verification_promotion_allowed": False,
            "note": (
                "This index proves deterministic selection from the shared corpus only. "
                "It does not inherit dayservice verification or make homevisit public."
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
            raise SystemExit("homevisit Care Insurance Act index missing; run builder")
        if OUTPUT.read_text(encoding="utf-8") != rendered:
            raise SystemExit("homevisit Care Insurance Act index is stale; run builder")
        print("homevisit Care Insurance Act index: current")
        return

    OUTPUT.write_text(rendered, encoding="utf-8")
    print(f"wrote {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
