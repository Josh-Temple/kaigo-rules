#!/usr/bin/env python3
"""Validate Worker D relation-review packet hardening invariants."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

WORKER_D_CLASSES = {
    "SEMANTIC_TEXT_CHECK_REQUIRED",
    "CROSS_LAYER_HUMAN_REVIEW_REQUIRED",
    "HUMAN_SEMANTIC_REVIEW_REQUIRED",
}
DECISIONS = [
    "CONFIRM_RELATION",
    "REJECT_RELATION",
    "NEEDS_MORE_EVIDENCE",
]


def load(name: str):
    return json.loads((DATA / name).read_text(encoding="utf-8"))


def identity_tuple(identity: dict) -> tuple[str, str, str]:
    return identity["from"], identity["relation"], identity["to"]


def main() -> None:
    queue = load("relation-verification-queue.json")
    packet = load("relation-human-review-packet.json")
    evidence = load("relation-human-review-evidence-pack.json")
    freshness = load("relation-freshness-direct-evidence-assessment.json")

    if queue["inventory_relations"] != (
        queue["independently_covered_relations"] + queue["remaining_relations"]
    ):
        raise SystemExit("relation queue arithmetic invariant failed")

    queue_items = queue.get("items", [])
    queue_ids = [identity_tuple(row["identity"]) for row in queue_items]
    if len(queue_ids) != len(set(queue_ids)):
        raise SystemExit("duplicate relation identity in verification queue")

    owned = [
        row for row in queue_items if row.get("classification") in WORKER_D_CLASSES
    ]
    if len(owned) != 58:
        raise SystemExit(f"expected 58 human/semantic Worker D relations, got {len(owned)}")

    freshness_queue = [
        row
        for row in queue_items
        if row.get("classification")
        == "SOURCE_LINK_FRESHNESS_OR_DIRECT_EVIDENCE_REQUIRED"
    ]
    freshness_items = freshness.get("items", [])
    if len(freshness_queue) != 1 or len(freshness_items) != 1:
        raise SystemExit("expected exactly one freshness-sensitive relation")
    freshness_identity = identity_tuple(freshness_items[0]["identity"])
    if freshness_identity != identity_tuple(freshness_queue[0]["identity"]):
        raise SystemExit("freshness assessment identity differs from queue")
    if freshness_identity in {identity_tuple(row["identity"]) for row in owned}:
        raise SystemExit("freshness relation overlaps human-review packet ownership")
    if len(owned) + len(freshness_items) != queue["remaining_relations"]:
        raise SystemExit("Worker D artifacts do not account for every remaining relation")

    packet_items = packet.get("items", [])
    evidence_items = evidence.get("items", [])
    if len(packet_items) != len(owned) or len(evidence_items) != len(owned):
        raise SystemExit("packet/evidence count differs from Worker D-owned queue")

    packet_by_identity = {
        identity_tuple(row["identity"]): row for row in packet_items
    }
    evidence_by_identity = {
        identity_tuple(row["identity"]): row for row in evidence_items
    }
    if set(packet_by_identity) != set(identity_tuple(row["identity"]) for row in owned):
        raise SystemExit("human-review packet identity set differs from Worker D queue")
    if set(evidence_by_identity) != set(packet_by_identity):
        raise SystemExit("evidence pack identity set differs from review packet")

    classifications = Counter(row["classification"] for row in packet_items)
    expected = {
        "SEMANTIC_TEXT_CHECK_REQUIRED": 17,
        "CROSS_LAYER_HUMAN_REVIEW_REQUIRED": 5,
        "HUMAN_SEMANTIC_REVIEW_REQUIRED": 36,
    }
    if dict(classifications) != expected:
        raise SystemExit(
            f"unexpected Worker D classification counts: {dict(classifications)}"
        )

    if queue["classification_counts"].get(
        "SOURCE_LINK_FRESHNESS_OR_DIRECT_EVIDENCE_REQUIRED"
    ) != 1:
        raise SystemExit("freshness-sensitive relation count changed unexpectedly")

    freshness_row = freshness_items[0]
    direct = freshness_row.get("direct_evidence", {})
    if direct.get("source_exists") is not True:
        raise SystemExit("freshness relation source existence not established")
    if direct.get("exact_source_identity_match") is not True:
        raise SystemExit("freshness relation source identity is not exact")
    if direct.get("amendment_semantics_supported") is not True:
        raise SystemExit("freshness relation amendment semantics not supported")
    if freshness_row.get("freshness", {}).get("state") != "NOT_ESTABLISHED":
        raise SystemExit("freshness was promoted without successor-absence proof")
    if freshness_row.get("closure_assessment") != "KEEP_OPEN":
        raise SystemExit("freshness-sensitive relation was unsafely closed")

    relation_keys = []
    for row in packet_items:
        identity = row["identity"]
        expected_key = "|".join(identity_tuple(identity))
        if row.get("relation_key") != expected_key:
            raise SystemExit(f"unstable relation_key for {row['review_id']}")
        relation_keys.append(expected_key)

        if row.get("review_status") != "NOT_REVIEWED":
            raise SystemExit(f"AI packet changed human review state: {row['review_id']}")
        if any(
            row.get(field) is not None
            for field in ("reviewer_name", "reviewer_decision", "reviewer_note", "reviewed_at")
        ):
            raise SystemExit(f"reviewer field populated by machine: {row['review_id']}")
        if row.get("decision_options") != DECISIONS:
            raise SystemExit(f"decision options changed: {row['review_id']}")
        if not str(row.get("ai_proposal", "")).startswith("KEEP_OPEN."):
            raise SystemExit(f"AI proposal is not fail-closed: {row['review_id']}")
        if not row.get("human_judgment_question"):
            raise SystemExit(f"human judgment question missing: {row['review_id']}")
        if not row.get("competing_interpretation_or_ambiguity"):
            raise SystemExit(f"ambiguity field missing: {row['review_id']}")

    if len(relation_keys) != len(set(relation_keys)):
        raise SystemExit("duplicate stable relation_key in human-review packet")

    semantic_pointer_counts = Counter()
    for row in evidence_items:
        review_id = row["review_id"]
        packet_row = packet_by_identity[identity_tuple(row["identity"])]
        if row.get("relation_key") != packet_row.get("relation_key"):
            raise SystemExit(f"evidence relation_key drift: {review_id}")
        if row.get("review_status") != "NOT_REVIEWED":
            raise SystemExit(f"evidence pack changed human review state: {review_id}")
        if row.get("closure_assessment") != "KEEP_OPEN":
            raise SystemExit(f"unsafe automatic closure: {review_id}")
        if row.get("machine_verifiable_subclaims", {}).get(
            "relation_semantics_verified"
        ) is not False:
            raise SystemExit(f"machine asserted semantic verification: {review_id}")
        if any(
            row.get(field) is not None
            for field in ("reviewer_name", "reviewer_decision", "reviewer_note", "reviewed_at")
        ):
            raise SystemExit(f"evidence reviewer field populated by machine: {review_id}")

        source = row["source_evidence"]
        target = row["target_evidence"]
        if not source.get("canonical_ids") or not target.get("canonical_ids"):
            raise SystemExit(f"unresolved canonical identity: {review_id}")
        if not source.get("excerpt") or not target.get("excerpt"):
            raise SystemExit(f"missing review excerpt: {review_id}")

        if row["classification"] == "SEMANTIC_TEXT_CHECK_REQUIRED":
            status = row["machine_verifiable_subclaims"]["source_pointer_status"]
            semantic_pointer_counts[status] += 1
            if status == "DIRECT_PRIMARY_TEXT_POINTER":
                raise SystemExit(
                    f"semantic relation unexpectedly auto-closable without adjudication: {review_id}"
                )

    expected_semantic_pointers = {
        "MACHINE_RECONSTRUCTED_PRIMARY_CANDIDATE": 5,
        "PRIMARY_TEXT_POINTER_INCOMPLETE": 12,
    }
    if dict(semantic_pointer_counts) != expected_semantic_pointers:
        raise SystemExit(
            "semantic-text source pointer inventory changed: "
            + repr(dict(semantic_pointer_counts))
        )

    summary = evidence["summary"]
    if summary.get("machine_safe_closures") != 0:
        raise SystemExit("machine_safe_closures must remain zero")
    if summary.get("closure_assessment_counts") != {"KEEP_OPEN": 58}:
        raise SystemExit("closure assessment summary is not fail-closed")

    contract = packet["review_contract"]
    if contract.get("automatic_promotion_allowed") is not False:
        raise SystemExit("packet allows automatic promotion")
    if contract.get("ai_proposal_is_not_human_decision") is not True:
        raise SystemExit("AI proposal/human decision separation missing")
    if contract.get("reviewer_identity_required_for_decision") is not True:
        raise SystemExit("reviewer identity requirement missing")
    if contract.get("review_timestamp_required_for_decision") is not True:
        raise SystemExit("review timestamp requirement missing")

    print(
        "relation review packet hardening: PASS "
        f"(inventory={queue['inventory_relations']}, "
        f"independent={queue['independently_covered_relations']}, "
        f"remaining={queue['remaining_relations']}, "
        f"worker_d_human_semantic={len(owned)}, freshness_sensitive=1, "
        "machine_safe_closures=0)"
    )


if __name__ == "__main__":
    main()
