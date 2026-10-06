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

PILOT_RELATION_KEYS = [
    "fee.dayservice.note.13|related_to|ordinance37.article.99",
    "notice.dayservice.equipment.dining-training-room|interprets_or_explains|ordinance37.article.95",
    "fee.dayservice.note.2|operational_basis_related_to|ordinance37.article.105",
    "notice.dayservice.equipment.office|interprets_or_explains|ordinance37.article.95",
    "fee.dayservice.note.15|related_to|ordinance37.article.98",
    "notice.dayservice.personnel.function-training|interprets_or_explains|ordinance37.article.93",
    "fee.dayservice.note.3|operational_basis_related_to|ordinance37.article.30-2",
    "notice.dayservice.personnel.manager|interprets_or_explains|ordinance37.article.94",
]
IMMUTABLE_EVIDENCE_PACK_ITEMS_AT_ACTIVATION = 58
IMMUTABLE_PILOT = [
    (1, "REL-001", PILOT_RELATION_KEYS[0], "f3984f602718ad82cd16fbb6769c692654a9a19b32196becc9896626ab7074bf"),
    (2, "REL-013", PILOT_RELATION_KEYS[1], "e6bfcabaa109a05d053cde11a6f96b380f81824e49bd49a7857265b21dbcf56d"),
    (3, "REL-003", PILOT_RELATION_KEYS[2], "096aecc99c772aea9cb2b58f1e1e6fa007d02ebdeb5d5cdf3428d311fe4dc9d2"),
    (4, "REL-014", PILOT_RELATION_KEYS[3], "866cef28391a37db80ca4098899454a0d45ae00fcb3a25e0279d380c4b1350a6"),
    (5, "REL-002", PILOT_RELATION_KEYS[4], "a74d4b8731bd042477e4a7c1857d2dadb8607833d42c9ff28d5f6622f8d48166"),
    (6, "REL-019", PILOT_RELATION_KEYS[5], "74d3af43386b2a0c6239a35363fb5ffa4ff6ac3d7955d46219a8738d30a0b58a"),
    (7, "REL-004", PILOT_RELATION_KEYS[6], "a116fc01dd02661d0f0fa229c39d6487e882bde8e1dd952a86ffdafc2c1fa70c"),
    (8, "REL-021", PILOT_RELATION_KEYS[7], "0a8cb98ced9fa6e976b57aa07665b728d5af696ff5eafc0ebdeb2d9e26fd0bbe"),
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
        "review_id": IMMUTABLE_PILOT[index][1],
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
    by_key = {row["relation_key"]: row for row in evidence.get("items", [])}
    missing = [
        relation_key
        for relation_key in PILOT_RELATION_KEYS
        if relation_key not in by_key
    ]
    if missing:
        raise ValueError(f"pilot relation identities missing from evidence pack: {missing}")

    selected = [by_key[relation_key] for relation_key in PILOT_RELATION_KEYS]
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
            "remaining_evidence_pack_items_not_in_pilot": (
            IMMUTABLE_EVIDENCE_PACK_ITEMS_AT_ACTIVATION - len(items)
        ),
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


def validate_immutable_pilot(pilot: dict, evidence: dict) -> None:
    observed = [
        (
            row.get("pilot_order"),
            row.get("review_id"),
            row.get("relation_key"),
            row.get("evidence_fingerprint_sha256"),
        )
        for row in pilot.get("items", [])
    ]
    if observed != IMMUTABLE_PILOT:
        raise ValueError("immutable pilot identity/order/review-id/fingerprint snapshot changed")
    if pilot.get("summary", {}).get("items_total") != 8:
        raise ValueError("immutable pilot must remain exactly eight items")
    if any(row.get("review_status") != "READY_FOR_HUMAN_REVIEW" for row in pilot.get("items", [])):
        raise ValueError("immutable pilot review status changed")

    current_by_key = {
        row.get("relation_key"): row
        for row in evidence.get("items", [])
    }
    for _, _, relation_key, fingerprint in IMMUTABLE_PILOT:
        current = current_by_key.get(relation_key)
        if current is None:
            raise ValueError(f"immutable pilot relation missing from current evidence pack: {relation_key}")
        if current.get("evidence_fingerprint_sha256") != fingerprint:
            raise ValueError(f"immutable pilot evidence fingerprint drifted: {relation_key}")


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

    if OUTPUT_JSON.exists() and OUTPUT_MD.exists():
        pilot = load_json(OUTPUT_JSON)
        evidence = load_json(EVIDENCE_PATH)
        try:
            validate_immutable_pilot(pilot, evidence)
        except ValueError as exc:
            raise SystemExit(str(exc)) from exc
        rendered_md = render_markdown(pilot)
        if OUTPUT_MD.read_text(encoding="utf-8") != rendered_md:
            raise SystemExit("immutable relation human-review pilot markdown drifted")
        print("relation human-review pilot: immutable snapshot current")
        return

    if args.check:
        raise SystemExit("immutable relation human-review pilot artifact is missing")

    pilot = build()
    rendered_json = json.dumps(pilot, ensure_ascii=False, indent=2) + "\n"
    rendered_md = render_markdown(pilot)
    OUTPUT_JSON.write_text(rendered_json, encoding="utf-8")
    OUTPUT_MD.write_text(rendered_md, encoding="utf-8")
    print(f"wrote {OUTPUT_JSON.relative_to(ROOT)}")
    print(f"wrote {OUTPUT_MD.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
