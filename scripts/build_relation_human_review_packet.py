#!/usr/bin/env python3
"""Build a thin human-review packet for remaining relation identities."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUTPUT = DATA / "relation-human-review-packet.json"

WORKER_D_CLASSIFICATIONS = {
    "SEMANTIC_TEXT_CHECK_REQUIRED",
    "CROSS_LAYER_HUMAN_REVIEW_REQUIRED",
    "HUMAN_SEMANTIC_REVIEW_REQUIRED",
}


def load(name: str):
    return json.loads((DATA / name).read_text(encoding="utf-8"))


def article_number(value: str) -> str | None:
    for pattern in (
        r"^ordinance37\.article\.([0-9]+(?:-[0-9]+)?)",
        r"^ordinance37\.article([0-9]+(?:-[0-9]+)?)",
    ):
        match = re.match(pattern, value)
        if match:
            return match.group(1)
    return None


def describe(
    value: str,
    *,
    questions: dict,
    notices: dict,
    fees: dict,
    ordinance_articles: dict,
    qa_items: dict,
    sources: dict,
) -> dict:
    if value.startswith("question:"):
        slug = value.split(":", 1)[1]
        row = questions.get(slug)
        return {
            "id": value,
            "kind": "practical_question",
            "label": row.get("title") if row else slug,
            "route": f"/questions/{slug}",
            "state": row.get("status") if row else None,
        }

    if value.startswith("notice."):
        row = notices.get(value)
        return {
            "id": value,
            "kind": "interpretation_notice",
            "label": (row or {}).get("title") or value,
            "route": f"/notices#{value}",
            "state": (row or {}).get("verification_status")
            or (row or {}).get("human_verification_status"),
        }

    if value.startswith("fee."):
        row = fees.get(value)
        suffix = value.replace("fee.dayservice.", "", 1)
        route = "/fees" if suffix == "root" else f"/fees/{suffix}"
        return {
            "id": value,
            "kind": "remuneration",
            "label": (row or {}).get("title") or value,
            "route": route,
            "state": (row or {}).get("verification_status"),
        }

    article = article_number(value)
    if article:
        root = ordinance_articles.get(article)
        return {
            "id": value,
            "kind": "ordinance37",
            "label": (
                f"{(root or {}).get('article_title', '第' + article + '条')} "
                f"{(root or {}).get('caption') or ''}"
            ).strip(),
            "route": f"/rules/{article}",
            "state": (root or {}).get("verification_status"),
            "article_root_id": (root or {}).get("id"),
            "resolution_note": (
                "Article-level review route. Legacy granular relation IDs are preserved "
                "verbatim and are not silently rewritten."
            ),
        }

    if value.startswith("qa."):
        row = qa_items.get(value)
        return {
            "id": value,
            "kind": "curated_qa",
            "label": (row or {}).get("question") or value,
            "route": f"/qa/{value}",
            "state": (row or {}).get("verification_status"),
        }

    if value.startswith("mhlw-"):
        row = sources.get(value)
        return {
            "id": value,
            "kind": "official_source",
            "label": (row or {}).get("title") or value,
            "route": (row or {}).get("url"),
            "state": (row or {}).get("status"),
        }

    return {
        "id": value,
        "kind": "unresolved_identifier",
        "label": value,
        "route": None,
        "state": None,
    }


def review_prompt(classification: str) -> str:
    prompts = {
        "HUMAN_SEMANTIC_REVIEW_REQUIRED": (
            "Does the target authority actually support, qualify, clarify, or answer "
            "the practical question in the way asserted by this relation?"
        ),
        "SEMANTIC_TEXT_CHECK_REQUIRED": (
            "Does the notice text actually interpret or explain the target provision, "
            "rather than merely sharing a topic or section?"
        ),
        "CROSS_LAYER_HUMAN_REVIEW_REQUIRED": (
            "Do the primary texts justify this exact cross-layer relation semantics, "
            "not just a general thematic connection?"
        ),
        "SOURCE_LINK_FRESHNESS_OR_DIRECT_EVIDENCE_REQUIRED": (
            "Is the source-link claim directly evidenced and, for a latest/current claim, "
            "is there sufficient update coverage to support freshness as of the review date?"
        ),
    }
    return prompts[classification]


def relation_key(identity: dict) -> str:
    return "|".join(
        [identity["from"], identity["relation"], identity["to"]]
    )


def ai_proposal(classification: str) -> str:
    proposals = {
        "SEMANTIC_TEXT_CHECK_REQUIRED": (
            "KEEP_OPEN. Do not treat topic overlap or reconstructed notice text as proof "
            "of interprets_or_explains; compare primary text and adjudicate the exact semantics."
        ),
        "CROSS_LAYER_HUMAN_REVIEW_REQUIRED": (
            "KEEP_OPEN. The source and target are resolved, but the exact cross-layer "
            "relation label still requires human legal-semantic judgment."
        ),
        "HUMAN_SEMANTIC_REVIEW_REQUIRED": (
            "KEEP_OPEN. The authority may be relevant to the practical question, but a "
            "human must decide whether it supports the exact relation label."
        ),
    }
    return proposals[classification]


def competing_interpretation_or_ambiguity(classification: str) -> str:
    ambiguities = {
        "SEMANTIC_TEXT_CHECK_REQUIRED": (
            "The notice and ordinance may concern the same topic without the notice "
            "actually interpreting or explaining this exact target provision."
        ),
        "CROSS_LAYER_HUMAN_REVIEW_REQUIRED": (
            "A general thematic or operational connection may exist without supporting "
            "the exact cross-layer relation asserted here."
        ),
        "HUMAN_SEMANTIC_REVIEW_REQUIRED": (
            "The cited authority may be relevant background without answering, qualifying, "
            "or otherwise supporting the practical question in the asserted way."
        ),
    }
    return ambiguities[classification]


def build() -> dict:
    queue = load("relation-verification-queue.json")
    questions = {row["slug"]: row for row in load("questions.json")}
    notice_rows = load("notice-nodes.json") + load("notice-current-skeleton.json")
    notices = {row["id"]: row for row in notice_rows}
    fees = {row["id"]: row for row in load("remuneration-current-skeleton.json")}
    ordinance_articles = {
        row["article_num"]: row
        for row in load("ordinance37-nodes.json")
        if row.get("node_type") == "article"
    }
    qa_items = {row["id"]: row for row in load("qa-items.json")}
    sources = {row["id"]: row for row in load("sources.json")}

    items = []
    for index, item in enumerate(queue.get("items", []), start=1):
        identity = item["identity"]
        classification = item["classification"]
        if classification not in WORKER_D_CLASSIFICATIONS:
            continue
        items.append(
            {
                "review_id": f"REL-{index:03d}",
                "identity": identity,
                "classification": classification,
                "relation_key": relation_key(identity),
                "source_file": item.get("source_file"),
                "source_state": item.get("source_state"),
                "source": describe(
                    identity["from"],
                    questions=questions,
                    notices=notices,
                    fees=fees,
                    ordinance_articles=ordinance_articles,
                    qa_items=qa_items,
                    sources=sources,
                ),
                "target": describe(
                    identity["to"],
                    questions=questions,
                    notices=notices,
                    fees=fees,
                    ordinance_articles=ordinance_articles,
                    qa_items=qa_items,
                    sources=sources,
                ),
                "review_prompt": review_prompt(classification),
                "human_judgment_question": review_prompt(classification),
                "ai_proposal": ai_proposal(classification),
                "competing_interpretation_or_ambiguity": competing_interpretation_or_ambiguity(
                    classification
                ),
                "existing_blockers": item.get("blockers", []),
                "decision_options": [
                    "CONFIRM_RELATION",
                    "REJECT_RELATION",
                    "NEEDS_MORE_EVIDENCE",
                ],
                "review_status": "NOT_REVIEWED",
                "reviewed_by": None,
                "reviewer_rationale": None,
                "reviewer_name": None,
                "reviewer_decision": None,
                "reviewer_note": None,
                "reviewed_at": None,
            }
        )

    counts = Counter(item["classification"] for item in items)
    expected_counts = {
        key: value
        for key, value in queue.get("classification_counts", {}).items()
        if key in WORKER_D_CLASSIFICATIONS and value
    }
    if len(items) != sum(expected_counts.values()):
        raise ValueError("Worker D review packet item count differs from owned queue classes")
    if dict(counts) != expected_counts:
        raise ValueError("Worker D review packet classification counts differ from queue")

    return {
        "format_version": 1,
        "generated_by": "scripts/build_relation_human_review_packet.py",
        "source_queue": "data/relation-verification-queue.json",
        "policy": (
            "This packet organizes only Worker D-owned unresolved relation review. "
            "Freshness-sensitive direct-evidence relations are assessed separately and excluded "
            "from this human-review packet. Blank reviewer fields must not be interpreted as rejection "
            "or approval. Packet generation never promotes independent verification, "
            "currentness, or human-review state."
        ),
        "summary": {
            "items_total": len(items),
            "classification_counts": expected_counts,
            "independently_covered_relations": queue["independently_covered_relations"],
            "inventory_relations": queue["inventory_relations"],
        },
        "review_contract": {
            "allowed_decisions": [
                "CONFIRM_RELATION",
                "REJECT_RELATION",
                "NEEDS_MORE_EVIDENCE",
            ],
            "automatic_promotion_allowed": False,
            "requires_primary_source_check": True,
            "currentness_is_separate": True,
            "ai_proposal_is_not_human_decision": True,
            "reviewer_identity_required_for_decision": True,
            "review_timestamp_required_for_decision": True,
        },
        "items": items,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    rendered = json.dumps(build(), ensure_ascii=False, indent=2) + "\n"
    if args.check:
        if not OUTPUT.exists() or OUTPUT.read_text(encoding="utf-8") != rendered:
            raise SystemExit("relation human-review packet is stale; run builder")
        print("relation human-review packet: current")
        return
    OUTPUT.write_text(rendered, encoding="utf-8")
    print(f"wrote {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
