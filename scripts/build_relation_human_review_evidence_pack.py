#!/usr/bin/env python3
"""Build evidence excerpts and canonical resolutions for unresolved relation review."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUTPUT = DATA / "relation-human-review-evidence-pack.json"
MAX_EXCERPT = 700


def load(name: str):
    return json.loads((DATA / name).read_text(encoding="utf-8"))


def compact(value: str | None) -> str:
    return " ".join(str(value or "").split())


def excerpt(value: str | None) -> str:
    text = compact(value)
    return text if len(text) <= MAX_EXCERPT else text[:MAX_EXCERPT] + "…"


def resolve_ordinance_nodes(
    value: str,
    ordinance_by_id: dict[str, dict],
    legacy_by_id: dict[str, dict],
) -> list[dict]:
    if value in ordinance_by_id:
        return [ordinance_by_id[value]]
    if value in legacy_by_id:
        return [legacy_by_id[value]]

    match = re.match(
        r"^ordinance37\.article([0-9]+(?:-[0-9]+)?)(?:\.(.+))?$",
        value,
    )
    if not match:
        return []

    article = match.group(1)
    suffix = match.group(2)
    root = f"ordinance37.article.{article}"
    if not suffix:
        return [ordinance_by_id[root]] if root in ordinance_by_id else []

    parts = suffix.split(".")
    if len(parts) == 2:
        candidate = f"{root}.p.{parts[0]}.i.{parts[1]}"
        return [ordinance_by_id[candidate]] if candidate in ordinance_by_id else []

    if len(parts) != 1:
        return []

    token = parts[0]
    paragraph = f"{root}.p.{token}"
    if paragraph in ordinance_by_id:
        return [ordinance_by_id[paragraph]]

    range_match = re.fullmatch(r"(\d+)-(\d+)", token)
    if range_match:
        start, end = map(int, range_match.groups())
        if start <= end:
            rows = [
                ordinance_by_id.get(f"{root}.p.{number}")
                for number in range(start, end + 1)
            ]
            if all(rows):
                return [row for row in rows if row]
        item = f"{root}.p.{range_match.group(1)}.i.{range_match.group(2)}"
        if item in ordinance_by_id:
            return [ordinance_by_id[item]]

    # Some legacy IDs use ".3" for an item when the article has one paragraph.
    single_paragraph_item = f"{root}.p.1.i.{token}"
    if single_paragraph_item in ordinance_by_id:
        return [ordinance_by_id[single_paragraph_item]]
    return []


def evidence(
    value: str,
    *,
    questions: dict[str, dict],
    notices: dict[str, dict],
    notice_reviews: dict[str, dict],
    fee_nodes: dict[str, dict],
    fee_text: dict[str, dict],
    ordinance_by_id: dict[str, dict],
    legacy_by_id: dict[str, dict],
    qa_items: dict[str, dict],
    sources: dict[str, dict],
) -> dict:
    if value.startswith("question:"):
        slug = value.split(":", 1)[1]
        row = questions.get(slug, {})
        return {
            "resolution_kind": "QUESTION",
            "canonical_ids": [f"question:{slug}"],
            "excerpt_kind": "question_title_and_short_answer",
            "excerpt": excerpt(
                f"{row.get('title', '')} {row.get('short_answer', '')}"
            ),
            "source_url": f"/questions/{slug}",
            "source_locator": None,
            "text_hashes": [],
        }

    if value.startswith("notice."):
        review = notice_reviews.get(value)
        row = notices.get(value, {})
        if review:
            text = review.get("candidate_text")
            kind = "machine_reconstructed_candidate"
            hashes = [review.get("candidate_text_sha256")]
            source_url = (review.get("source_evidence") or [{}])[0].get("source_url")
            locator = (review.get("source_evidence") or [{}])[0].get("note")
        else:
            text = row.get("official_text") or row.get("editorial_summary")
            kind = (
                "official_text"
                if row.get("official_text")
                else "editorial_summary_not_primary_text"
            )
            hashes = [row.get("text_sha256")] if row.get("text_sha256") else []
            source_url = None
            locator = " > ".join(row.get("path") or [])
        return {
            "resolution_kind": "NOTICE",
            "canonical_ids": [value],
            "excerpt_kind": kind,
            "excerpt": excerpt(text or row.get("title")),
            "source_url": source_url,
            "source_locator": locator,
            "text_hashes": [item for item in hashes if item],
        }

    if value.startswith("fee."):
        node = fee_nodes.get(value, {})
        text_row = fee_text.get(value, {})
        text = text_row.get("official_text") or node.get("title")
        return {
            "resolution_kind": "REMUNERATION",
            "canonical_ids": [value],
            "excerpt_kind": (
                "official_current_source_text"
                if text_row.get("official_text")
                else "structure_label_only"
            ),
            "excerpt": excerpt(text),
            "source_url": text_row.get("source_url"),
            "source_locator": text_row.get("source_locator") or node.get("source_locator"),
            "text_hashes": [
                item
                for item in [text_row.get("text_sha256")]
                if item
            ],
        }

    if value.startswith("ordinance37."):
        rows = resolve_ordinance_nodes(value, ordinance_by_id, legacy_by_id)
        return {
            "resolution_kind": (
                "ORDINANCE_CANONICAL_NODE"
                if rows and rows[0].get("id") in ordinance_by_id
                else "ORDINANCE_LEGACY_VERIFIED_NODE"
                if rows
                else "ORDINANCE_UNRESOLVED"
            ),
            "canonical_ids": [row.get("id") for row in rows],
            "excerpt_kind": "official_text" if rows else "unresolved",
            "excerpt": excerpt(" ".join(compact(row.get("official_text")) for row in rows)),
            "source_url": next(
                (row.get("source_url") for row in rows if row.get("source_url")),
                None,
            ),
            "source_locator": " | ".join(
                row.get("source_locator") or " > ".join(row.get("path") or [])
                for row in rows
            ) or None,
            "text_hashes": [
                row.get("text_sha256")
                for row in rows
                if row.get("text_sha256")
            ],
        }

    if value.startswith("qa."):
        row = qa_items.get(value, {})
        return {
            "resolution_kind": "CURATED_QA",
            "canonical_ids": [value],
            "excerpt_kind": "structured_question_and_answer_summary",
            "excerpt": excerpt(
                f"{row.get('question_summary', '')} {row.get('answer_summary', '')}"
            ),
            "source_url": None,
            "source_locator": " / ".join(
                part
                for part in [row.get("source_document"), row.get("source_number")]
                if part
            ) or None,
            "text_hashes": [],
        }

    if value.startswith("mhlw-"):
        row = sources.get(value, {})
        return {
            "resolution_kind": "OFFICIAL_SOURCE_REGISTRY",
            "canonical_ids": [value],
            "excerpt_kind": "source_registry_metadata",
            "excerpt": excerpt(
                " ".join(
                    part
                    for part in [
                        row.get("title"),
                        row.get("note"),
                        row.get("scope"),
                    ]
                    if part
                )
            ),
            "source_url": row.get("url"),
            "source_locator": None,
            "text_hashes": [
                item
                for item in [row.get("sha256"), row.get("source_sha256")]
                if item
            ],
        }

    return {
        "resolution_kind": "UNRESOLVED",
        "canonical_ids": [],
        "excerpt_kind": "unresolved",
        "excerpt": "",
        "source_url": None,
        "source_locator": None,
        "text_hashes": [],
    }


def build() -> dict:
    packet = load("relation-human-review-packet.json")
    questions = {row["slug"]: row for row in load("questions.json")}
    notices = {
        row["id"]: row
        for row in load("notice-current-skeleton.json") + load("notice-nodes.json")
    }
    notice_reviews = {
        row["notice_id"]: row for row in load("notice-review-packet.json").get("items", [])
    }
    fee_nodes = {row["id"]: row for row in load("remuneration-current-skeleton.json")}
    fee_text = {row["fee_id"]: row for row in load("remuneration-current-text.json")}
    ordinance_nodes = load("ordinance37-nodes.json")
    ordinance_by_id = {row["id"]: row for row in ordinance_nodes}
    legacy_by_id = {row["id"]: row for row in load("rule-nodes.json")}
    qa_items = {row["id"]: row for row in load("qa-items.json")}
    sources = {row["id"]: row for row in load("sources.json")}

    items = []
    for item in packet.get("items", []):
        identity = item["identity"]
        source = evidence(
            identity["from"],
            questions=questions,
            notices=notices,
            notice_reviews=notice_reviews,
            fee_nodes=fee_nodes,
            fee_text=fee_text,
            ordinance_by_id=ordinance_by_id,
            legacy_by_id=legacy_by_id,
            qa_items=qa_items,
            sources=sources,
        )
        target = evidence(
            identity["to"],
            questions=questions,
            notices=notices,
            notice_reviews=notice_reviews,
            fee_nodes=fee_nodes,
            fee_text=fee_text,
            ordinance_by_id=ordinance_by_id,
            legacy_by_id=legacy_by_id,
            qa_items=qa_items,
            sources=sources,
        )
        items.append(
            {
                "review_id": item["review_id"],
                "identity": identity,
                "classification": item["classification"],
                "source_evidence": source,
                "target_evidence": target,
                "reviewer_decision": None,
                "reviewer_note": None,
            }
        )

    resolution_counts = Counter(
        row["target_evidence"]["resolution_kind"] for row in items
    )
    unresolved = [
        row["review_id"]
        for row in items
        if row["source_evidence"]["resolution_kind"] == "UNRESOLVED"
        or row["target_evidence"]["resolution_kind"]
        in {"UNRESOLVED", "ORDINANCE_UNRESOLVED"}
    ]
    if len(items) != packet.get("summary", {}).get("items_total"):
        raise ValueError("evidence pack item count differs from review packet")
    if unresolved:
        raise ValueError("unresolved evidence descriptors: " + ", ".join(unresolved))

    return {
        "format_version": 1,
        "generated_by": "scripts/build_relation_human_review_evidence_pack.py",
        "source_packet": "data/relation-human-review-packet.json",
        "policy": (
            "This file supplies review excerpts and canonical resolution only. Excerpts may "
            "include machine-reconstructed candidates or editorial summaries where primary "
            "text is not committed. It never makes or promotes a semantic review decision."
        ),
        "summary": {
            "items_total": len(items),
            "unresolved_items": 0,
            "target_resolution_counts": dict(sorted(resolution_counts.items())),
        },
        "review_contract": {
            "semantic_decision_included": False,
            "automatic_promotion_allowed": False,
            "primary_source_check_still_required": True,
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
            raise SystemExit("relation human-review evidence pack is stale; run builder")
        print("relation human-review evidence pack: current")
        return
    OUTPUT.write_text(rendered, encoding="utf-8")
    print(f"wrote {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
