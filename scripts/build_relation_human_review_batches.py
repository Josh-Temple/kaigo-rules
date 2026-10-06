#!/usr/bin/env python3
"""Build reproducible human-review batches without making human decisions."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
EVIDENCE_PATH = DATA / "relation-human-review-evidence-pack.json"
PILOT_PATH = DATA / "relation-human-review-pilot.json"
DECISION_LEDGER = "data/relation-human-review-decisions.json"
REGISTRY_OUTPUT = DATA / "relation-human-review-batches.json"
BATCH2_OUTPUT = DATA / "relation-human-review-batch-2.json"
BATCH2_SIZE = 10

PINNED_PILOT = [
    (1, "fee.dayservice.note.13|related_to|ordinance37.article.99", "f3984f602718ad82cd16fbb6769c692654a9a19b32196becc9896626ab7074bf"),
    (2, "notice.dayservice.equipment.dining-training-room|interprets_or_explains|ordinance37.article.95", "e6bfcabaa109a05d053cde11a6f96b380f81824e49bd49a7857265b21dbcf56d"),
    (3, "fee.dayservice.note.2|operational_basis_related_to|ordinance37.article.105", "096aecc99c772aea9cb2b58f1e1e6fa007d02ebdeb5d5cdf3428d311fe4dc9d2"),
    (4, "notice.dayservice.equipment.office|interprets_or_explains|ordinance37.article.95", "866cef28391a37db80ca4098899454a0d45ae00fcb3a25e0279d380c4b1350a6"),
    (5, "fee.dayservice.note.15|related_to|ordinance37.article.98", "a74d4b8731bd042477e4a7c1857d2dadb8607833d42c9ff28d5f6622f8d48166"),
    (6, "notice.dayservice.personnel.function-training|interprets_or_explains|ordinance37.article.93", "74d3af43386b2a0c6239a35363fb5ffa4ff6ac3d7955d46219a8738d30a0b58a"),
    (7, "fee.dayservice.note.3|operational_basis_related_to|ordinance37.article.30-2", "a116fc01dd02661d0f0fa229c39d6487e882bde8e1dd952a86ffdafc2c1fa70c"),
    (8, "notice.dayservice.personnel.manager|interprets_or_explains|ordinance37.article.94", "0a8cb98ced9fa6e976b57aa07665b728d5af696ff5eafc0ebdeb2d9e26fd0bbe"),
]

def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))

def review_number(review_id: str) -> int:
    return int(review_id.split("-", 1)[1])

def pointer_rank(row: dict[str, Any]) -> int | None:
    claims = row.get("machine_verifiable_subclaims") or {}
    source = claims.get("source_pointer_status")
    target = claims.get("target_pointer_status")
    if "PRIMARY_TEXT_POINTER_INCOMPLETE" in {source, target}:
        return None
    if source == "DIRECT_PRIMARY_TEXT_POINTER" and target == "DIRECT_PRIMARY_TEXT_POINTER":
        return 0
    if source == "MACHINE_RECONSTRUCTED_PRIMARY_CANDIDATE" and target == "DIRECT_PRIMARY_TEXT_POINTER":
        return 1
    if source == "PRACTICAL_QUESTION_CONTEXT" and target == "DIRECT_PRIMARY_TEXT_POINTER":
        return 2
    return None

def validate_pilot_immutable(pilot: dict[str, Any]) -> None:
    items = pilot.get("items", [])
    observed = [
        (
            row.get("pilot_order"),
            row.get("relation_key"),
            row.get("evidence_fingerprint_sha256"),
        )
        for row in items
    ]
    if observed != PINNED_PILOT:
        raise ValueError("existing pilot 8-item identity/order/fingerprint reference changed")
    if any(row.get("review_status") != "READY_FOR_HUMAN_REVIEW" for row in items):
        raise ValueError("existing pilot review status changed")
    if len(items) != 8:
        raise ValueError("existing pilot must remain exactly 8 items")

def choose_batch2(evidence: dict[str, Any], pilot_keys: set[str]) -> list[dict[str, Any]]:
    candidates = []
    for row in evidence.get("items", []):
        if row.get("relation_key") in pilot_keys or not row.get("evidence_pack_ready"):
            continue
        rank = pointer_rank(row)
        if rank is None:
            continue
        candidates.append((rank, review_number(row["review_id"]), row))
    candidates.sort(key=lambda value: (value[0], value[1]))

    selected: list[dict[str, Any]] = []
    seen_semantics: set[str] = set()
    # First pass: honor evidence priority while maximizing semantic diversity.
    for rank in (0, 1, 2):
        for candidate_rank, _, row in candidates:
            if candidate_rank != rank or len(selected) >= BATCH2_SIZE:
                continue
            semantics = str((row.get("identity") or {}).get("relation") or "")
            if semantics and semantics not in seen_semantics:
                selected.append(row)
                seen_semantics.add(semantics)
    # Second pass: fill only after diversity has been exhausted.
    for _, _, row in candidates:
        if len(selected) >= BATCH2_SIZE:
            break
        if row not in selected:
            selected.append(row)

    if len(selected) < 8:
        raise ValueError(
            f"only {len(selected)} eligible Batch 2 items; do not activate evidence-incomplete items"
        )
    return selected

def registry_item(
    *,
    batch_order: int,
    row: dict[str, Any],
    current_pack_by_key: dict[str, dict[str, Any]],
    fingerprint_override: str | None = None,
) -> dict[str, Any]:
    relation_key = row["relation_key"]
    fingerprint = fingerprint_override or row["evidence_fingerprint_sha256"]
    current = current_pack_by_key.get(relation_key)
    current_fingerprint = current.get("evidence_fingerprint_sha256") if current else None
    return {
        "batch_order": batch_order,
        "review_id": row["review_id"],
        "relation_identity": row["identity"],
        "relation_key": relation_key,
        "evidence_fingerprint_sha256": fingerprint,
        "evidence_readiness": (
            "READY_FOR_HUMAN_REVIEW" if row.get("evidence_pack_ready", True)
            else "EVIDENCE_NOT_READY"
        ),
        "review_status": "READY_FOR_HUMAN_REVIEW",
        "assigned_reviewer": None,
        "decision_ledger_pointer": DECISION_LEDGER + "#decisions",
        "stale_state": (
            "CURRENT_EVIDENCE"
            if current_fingerprint == fingerprint
            else "STALE_EVIDENCE"
        ),
    }

def batch2_unit(row: dict[str, Any], index: int) -> dict[str, Any]:
    source = row["source_evidence"]
    target = row["target_evidence"]
    claims = row["machine_verifiable_subclaims"]
    return {
        "batch_id": "batch-2",
        "batch_order": index + 1,
        "review_id": row["review_id"],
        "review_status": "READY_FOR_HUMAN_REVIEW",
        "assigned_reviewer": None,
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
        "source_pointer_status": claims["source_pointer_status"],
        "target_pointer_status": claims["target_pointer_status"],
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
        "stale_state": "CURRENT_EVIDENCE",
    }

def build() -> tuple[dict[str, Any], dict[str, Any]]:
    evidence = load(EVIDENCE_PATH)
    pilot = load(PILOT_PATH)
    validate_pilot_immutable(pilot)

    evidence_by_key = {row["relation_key"]: row for row in evidence.get("items", [])}
    pilot_keys = {row["relation_key"] for row in pilot["items"]}
    batch2_rows = choose_batch2(evidence, pilot_keys)

    batch2_items = [batch2_unit(row, index) for index, row in enumerate(batch2_rows)]
    batch2 = {
        "format_version": 1,
        "batch_id": "batch-2",
        "generated_by": "scripts/build_relation_human_review_batches.py",
        "source_evidence_pack": "data/relation-human-review-evidence-pack.json",
        "decision_ledger": DECISION_LEDGER,
        "policy": (
            "Batch 2 is an additional bounded human-review batch. "
            "READY_FOR_HUMAN_REVIEW is not REVIEWED. AI proposals are advisory only. "
            "Items with PRIMARY_TEXT_POINTER_INCOMPLETE on either side are excluded. "
            "Practical-question context is lower-priority than direct or reconstructed "
            "primary-source evidence and is used only after stronger remaining candidates."
        ),
        "selection_policy": {
            "batch_size_target": BATCH2_SIZE,
            "exclude_existing_pilot": True,
            "require_evidence_pack_ready": True,
            "primary_text_pointer_incomplete_eligible": False,
            "priority_order": [
                "DIRECT_PRIMARY_TEXT_POINTER + DIRECT_PRIMARY_TEXT_POINTER",
                "MACHINE_RECONSTRUCTED_PRIMARY_CANDIDATE + DIRECT_PRIMARY_TEXT_POINTER",
                "PRACTICAL_QUESTION_CONTEXT + DIRECT_PRIMARY_TEXT_POINTER",
            ],
            "semantic_diversity_first_pass": True,
        },
        "summary": {
            "items_total": len(batch2_items),
            "ready_for_human_review": len(batch2_items),
            "classification_counts": dict(Counter(x["classification"] for x in batch2_items)),
            "relation_semantics_counts": dict(Counter(x["asserted_relation_semantics"] for x in batch2_items)),
            "source_pointer_status_counts": dict(Counter(x["source_pointer_status"] for x in batch2_items)),
            "target_pointer_status_counts": dict(Counter(x["target_pointer_status"] for x in batch2_items)),
            "remaining_evidence_pack_items_outside_active_batches": (
                len(evidence.get("items", [])) - len(pilot_keys) - len(batch2_items)
            ),
        },
        "review_contract": {
            "allowed_decisions": [
                "CONFIRM_RELATION",
                "REJECT_RELATION",
                "NEEDS_MORE_EVIDENCE",
            ],
            "required_decision_fields": [
                "reviewer_identity",
                "reviewer_decision",
                "reviewer_rationale",
                "reviewed_at",
                "evidence_fingerprint_sha256",
                "reviewer_attestation",
                "decision_state",
            ],
            "reviewer_attestation_value": "HUMAN_REVIEW_COMPLETED",
            "ai_proposal_is_not_decision": True,
            "decision_must_bind_current_evidence_fingerprint": True,
        },
        "items": batch2_items,
    }

    pilot_registry_items = []
    for order, relation_key, fingerprint in PINNED_PILOT:
        source = evidence_by_key.get(relation_key)
        if source is None:
            raise ValueError(f"pilot relation identity missing from evidence pack: {relation_key}")
        pilot_row = next(
            row for row in pilot["items"] if row["relation_key"] == relation_key
        )
        pilot_registry_items.append(
            registry_item(
                batch_order=order,
                row=pilot_row,
                current_pack_by_key=evidence_by_key,
                fingerprint_override=fingerprint,
            )
        )

    batch2_registry_items = [
        registry_item(
            batch_order=index + 1,
            row=row,
            current_pack_by_key=evidence_by_key,
        )
        for index, row in enumerate(batch2_rows)
    ]

    registry = {
        "format_version": 1,
        "generated_by": "scripts/build_relation_human_review_batches.py",
        "source_evidence_pack": "data/relation-human-review-evidence-pack.json",
        "decision_ledger": DECISION_LEDGER,
        "policy": (
            "Batch membership controls decision intake only. Batch activation does not make "
            "a relation REVIEWED or verified. Pilot 1 relation identity/order/fingerprint is an immutable reference; review IDs are regenerated management identifiers. Evidence "
            "fingerprint drift is represented as STALE_EVIDENCE and never silently refreshes "
            "an existing decision."
        ),
        "batches": [
            {
                "batch_id": "pilot-1",
                "status": "ACTIVE_IMMUTABLE_REFERENCE",
                "source_artifact": "data/relation-human-review-pilot.json",
                "immutable_reference": True,
                "items_total": len(pilot_registry_items),
                "items": pilot_registry_items,
            },
            {
                "batch_id": "batch-2",
                "status": "ACTIVE_FOR_HUMAN_REVIEW",
                "source_artifact": "data/relation-human-review-batch-2.json",
                "immutable_reference": False,
                "items_total": len(batch2_registry_items),
                "items": batch2_registry_items,
            },
        ],
        "summary": {
            "batch_count": 2,
            "pilot_items": len(pilot_registry_items),
            "batch_2_items": len(batch2_registry_items),
            "active_review_items": len(pilot_registry_items) + len(batch2_registry_items),
            "stale_evidence_items": sum(
                item["stale_state"] == "STALE_EVIDENCE"
                for item in pilot_registry_items + batch2_registry_items
            ),
            "evidence_pack_items_not_active": (
                len(evidence.get("items", []))
                - len(pilot_registry_items)
                - len(batch2_registry_items)
            ),
        },
    }
    return registry, batch2

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    registry, batch2 = build()
    outputs = [
        (REGISTRY_OUTPUT, json.dumps(registry, ensure_ascii=False, indent=2) + "\n"),
        (BATCH2_OUTPUT, json.dumps(batch2, ensure_ascii=False, indent=2) + "\n"),
    ]
    if args.check:
        stale = [
            str(path.relative_to(ROOT))
            for path, rendered in outputs
            if not path.exists() or path.read_text(encoding="utf-8") != rendered
        ]
        if stale:
            raise SystemExit("human-review batch artifacts are stale: " + ", ".join(stale))
        print("relation human-review batches: current")
        return
    for path, rendered in outputs:
        path.write_text(rendered, encoding="utf-8")
        print(f"wrote {path.relative_to(ROOT)}")

if __name__ == "__main__":
    main()
