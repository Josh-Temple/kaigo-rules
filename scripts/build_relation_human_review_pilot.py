#!/usr/bin/env python3
"""Build a bounded relation human-review pilot from the evidence pack."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
DOCS = ROOT / "docs"
EVIDENCE_PATH = DATA / "relation-human-review-evidence-pack.json"
OUTPUT_JSON = DATA / "relation-human-review-pilot.json"
OUTPUT_MD = DOCS / "relation-human-review-pilot.generated.md"

PILOT_REVIEW_IDS = [
    "REL-001",
    "REL-013",
    "REL-003",
    "REL-014",
    "REL-002",
    "REL-019",
    "REL-004",
    "REL-021",
]
ALLOWED_DECISIONS = [
    "CONFIRM_RELATION",
    "REJECT_RELATION",
    "NEEDS_MORE_EVIDENCE",
]


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def pilot_unit(row: dict, index: int) -> dict:
    source = row["source_evidence"]
    target = row["target_evidence"]
    subclaims = row["machine_verifiable_subclaims"]
    return {
        "pilot_order": index + 1,
        "review_id": row["review_id"],
        "review_status": "READY_FOR_HUMAN_REVIEW",
        "identity": row["identity"],
        "relation_key": row["relation_key"],
        "classification": row["classification"],
        "asserted_relation_semantics": row["identity"]["relation"],
        "source_label": row["source_label"],
        "target_label": row["target_label"],
        "source_excerpt": source["excerpt"],
        "target_excerpt": target["excerpt"],
        "source_url": source["source_url"],
        "source_locator": source["source_locator"],
        "target_url": target["source_url"],
        "target_locator": target["source_locator"],
        "source_pointer_status": subclaims["source_pointer_status"],
        "target_pointer_status": subclaims["target_pointer_status"],
        "human_judgment_question": row["human_judgment_question"],
        "ai_proposal": row["ai_proposal"],
        "competing_interpretation_or_ambiguity": row[
            "competing_interpretation_or_ambiguity"
        ],
        "decision_options": row["decision_options"],
        "currentness_caveat": row["currentness_caveat"],
        "evidence_fingerprint_sha256": row["evidence_fingerprint_sha256"],
        "supporting_source_primary_references": row[
            "supporting_source_primary_references"
        ],
        "supporting_target_primary_references": row[
            "supporting_target_primary_references"
        ],
    }


def build() -> dict:
    evidence = load_json(EVIDENCE_PATH)
    by_id = {row["review_id"]: row for row in evidence.get("items", [])}
    missing = [review_id for review_id in PILOT_REVIEW_IDS if review_id not in by_id]
    if missing:
        raise ValueError(f"pilot review ids missing from evidence pack: {missing}")

    selected = [by_id[review_id] for review_id in PILOT_REVIEW_IDS]
    for row in selected:
        if not row.get("evidence_pack_ready"):
            raise ValueError(f"pilot item is not evidence-pack ready: {row['review_id']}")
        if row["classification"] == "SOURCE_LINK_FRESHNESS_OR_DIRECT_EVIDENCE_REQUIRED":
            raise ValueError("freshness-sensitive relation leaked into human-review pilot")
        if not row["source_evidence"].get("source_url") or not row["source_evidence"].get(
            "source_locator"
        ):
            raise ValueError(f"pilot source pointer incomplete: {row['review_id']}")
        if not row["target_evidence"].get("source_url") or not row["target_evidence"].get(
            "source_locator"
        ):
            raise ValueError(f"pilot target pointer incomplete: {row['review_id']}")

    items = [pilot_unit(row, index) for index, row in enumerate(selected)]
    source_counts = Counter(item["source_pointer_status"] for item in items)
    target_counts = Counter(item["target_pointer_status"] for item in items)
    class_counts = Counter(item["classification"] for item in items)
    direct_both = sum(
        1
        for item in items
        if item["source_pointer_status"] == "DIRECT_PRIMARY_TEXT_POINTER"
        and item["target_pointer_status"] == "DIRECT_PRIMARY_TEXT_POINTER"
    )
    reconstructed_direct = sum(
        1
        for item in items
        if item["source_pointer_status"] == "MACHINE_RECONSTRUCTED_PRIMARY_CANDIDATE"
        and item["target_pointer_status"] == "DIRECT_PRIMARY_TEXT_POINTER"
    )

    for previous, current in zip(items, items[1:]):
        if previous["asserted_relation_semantics"] == current["asserted_relation_semantics"]:
            raise ValueError("pilot order contains consecutive identical relation semantics")

    return {
        "format_version": 1,
        "generated_by": "scripts/build_relation_human_review_pilot.py",
        "source_evidence_pack": "data/relation-human-review-evidence-pack.json",
        "decision_ledger": "data/relation-human-review-decisions.json",
        "policy": (
            "This pilot activates a bounded human-review batch only. "
            "READY_FOR_HUMAN_REVIEW is not REVIEWED. AI proposals are advisory and cannot "
            "close relations. Human decisions are valid only when recorded in the decision "
            "ledger with reviewer identity, rationale, reviewed_at, and the exact evidence "
            "fingerprint reviewed."
        ),
        "selection_rationale": [
            "Prefer relations with direct primary-text pointers on both sides.",
            "Use a small eight-item batch and interleave relation types instead of processing all 58 evidence-pack items.",
            "Fill the remainder with machine-reconstructed notice candidates whose target side has a direct primary-text pointer; practical-question relations remain outside the first pilot.",
        ],
        "summary": {
            "items_total": len(items),
            "ready_for_human_review": len(items),
            "direct_primary_text_both_sides": direct_both,
            "machine_reconstructed_source_direct_target": reconstructed_direct,
            "classification_counts": dict(class_counts),
            "source_pointer_status_counts": dict(source_counts),
            "target_pointer_status_counts": dict(target_counts),
            "remaining_evidence_pack_items_not_in_pilot": len(evidence.get("items", []))
            - len(items),
        },
        "review_contract": {
            "allowed_decisions": ALLOWED_DECISIONS,
            "required_decision_fields": [
                "reviewer_identity",
                "reviewer_decision",
                "reviewer_rationale",
                "reviewed_at",
                "evidence_fingerprint_sha256",
            ],
            "reviewer_attestation_required": True,
            "reviewer_attestation_value": "HUMAN_REVIEW_COMPLETED",
            "ai_proposal_is_not_decision": True,
            "ai_only_completion_allowed": False,
            "decision_must_bind_evidence_fingerprint": True,
            "fingerprint_mismatch_invalidates_current_decision": True,
            "stale_decision_state": "STALE_EVIDENCE",
            "pilot_only": True,
        },
        "items": items,
    }


def render_markdown(pilot: dict) -> str:
    lines = [
        "# Relation Human Review Pilot",
        "",
        "> This is a bounded human-review sheet. `READY_FOR_HUMAN_REVIEW` is not `REVIEWED`. AI proposals below are advisory only and must not be copied into the decision ledger as a substitute for human judgment.",
        "",
        f"- Pilot items: **{pilot['summary']['items_total']}**",
        f"- Direct primary text on both sides: **{pilot['summary']['direct_primary_text_both_sides']}**",
        f"- Remaining evidence-pack items outside this pilot: **{pilot['summary']['remaining_evidence_pack_items_not_in_pilot']}**",
        f"- Decision ledger: `{pilot['decision_ledger']}`",
        "",
        "A valid human decision must record reviewer identity, decision, rationale, review timestamp, the exact evidence fingerprint reviewed, and `reviewer_attestation = HUMAN_REVIEW_COMPLETED`. If the evidence fingerprint changes later, the old decision is not current.",
        "",
    ]
    for item in pilot["items"]:
        lines.extend(
            [
                f"## {item['pilot_order']}. {item['review_id']}",
                "",
                f"**Status:** `{item['review_status']}`",
                "",
                f"**Relation:** {item['source_label']} — `{item['asserted_relation_semantics']}` → {item['target_label']}",
                "",
                f"**Relation key:** `{item['relation_key']}`",
                "",
                "### Source",
                "",
                f"> {item['source_excerpt'].strip()}",
                "",
                f"- URL: {str(item['source_url']).strip()}",
                f"- Locator: {str(item['source_locator']).strip()}",
                f"- Pointer status: `{item['source_pointer_status']}`",
                "",
                "### Target",
                "",
                f"> {item['target_excerpt'].strip()}",
                "",
                f"- URL: {str(item['target_url']).strip()}",
                f"- Locator: {str(item['target_locator']).strip()}",
                f"- Pointer status: `{item['target_pointer_status']}`",
                "",
                "### Judgment",
                "",
                f"**Question:** {item['human_judgment_question'].strip()}",
                "",
                f"**AI proposal:** {item['ai_proposal'].strip()}",
                "",
                f"**Competing interpretation / ambiguity:** {item['competing_interpretation_or_ambiguity'].strip()}",
                "",
                "**Decision options:** "
                + ", ".join(f"`{value}`" for value in item["decision_options"]),
                "",
                f"**Currentness caveat:** {item['currentness_caveat'].strip()}",
                "",
                f"**Evidence fingerprint:** `{item['evidence_fingerprint_sha256']}`",
                "",
            ]
        )
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    pilot = build()
    rendered_json = json.dumps(pilot, ensure_ascii=False, indent=2) + "\n"
    rendered_md = render_markdown(pilot)

    if args.check:
        if not OUTPUT_JSON.exists() or OUTPUT_JSON.read_text(encoding="utf-8") != rendered_json:
            raise SystemExit("relation human-review pilot JSON is stale; run builder")
        if not OUTPUT_MD.exists() or OUTPUT_MD.read_text(encoding="utf-8") != rendered_md:
            raise SystemExit("relation human-review pilot markdown is stale; run builder")
        print("relation human-review pilot: current")
        return

    OUTPUT_JSON.write_text(rendered_json, encoding="utf-8")
    OUTPUT_MD.write_text(rendered_md, encoding="utf-8")
    print(f"wrote {OUTPUT_JSON.relative_to(ROOT)}")
    print(f"wrote {OUTPUT_MD.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
