#!/usr/bin/env python3
"""Validate fail-closed hardening of unresolved relation review artifacts."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from relation_verification_coverage import build_relation_coverage

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

WORKER_D_CLASSIFICATIONS = {
    "SEMANTIC_TEXT_CHECK_REQUIRED",
    "CROSS_LAYER_HUMAN_REVIEW_REQUIRED",
    "HUMAN_SEMANTIC_REVIEW_REQUIRED",
}
HUMAN_ONLY_CLASSIFICATIONS = {
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


def identity_key(identity: dict) -> str:
    return "|".join([identity["from"], identity["relation"], identity["to"]])


def validate() -> dict:
    queue = load("relation-verification-queue.json")
    packet = load("relation-human-review-packet.json")
    evidence = load("relation-human-review-evidence-pack.json")
    freshness_assessment = load("relation-freshness-direct-evidence-assessment.json")
    coverage = build_relation_coverage()

    inventory = queue["inventory_relations"]
    independently_covered = queue["independently_covered_relations"]
    remaining = queue["remaining_relations"]
    if inventory != independently_covered + remaining:
        raise ValueError(
            "relation queue arithmetic invariant failed: "
            f"{inventory} != {independently_covered} + {remaining}"
        )
    if inventory != len(coverage["inventory"]):
        raise ValueError("queue inventory count differs from canonical relation coverage")
    if independently_covered != len(coverage["verified"]):
        raise ValueError("queue independent coverage count differs from audit lanes")
    if remaining != len(coverage["remaining"]):
        raise ValueError("queue remaining count differs from canonical relation coverage")

    queue_owned = [
        row for row in queue["items"]
        if row["classification"] in WORKER_D_CLASSIFICATIONS
    ]
    queue_keys = [identity_key(row["identity"]) for row in queue_owned]
    packet_keys = [row["relation_key"] for row in packet["items"]]
    evidence_keys = [row["relation_key"] for row in evidence["items"]]

    for label, keys in (
        ("queue", queue_keys),
        ("packet", packet_keys),
        ("evidence", evidence_keys),
    ):
        if len(keys) != len(set(keys)):
            raise ValueError(f"duplicate relation identity in {label}")

    if packet_keys != queue_keys:
        raise ValueError("review packet identities/order differ from Worker D queue")
    if evidence_keys != packet_keys:
        raise ValueError("evidence pack identities/order differ from review packet")

    if packet["summary"]["items_total"] != len(queue_owned):
        raise ValueError("review packet item count differs from Worker D queue")
    if evidence["summary"]["items_total"] != len(queue_owned):
        raise ValueError("evidence pack item count differs from Worker D queue")
    if len(queue_owned) != 58:
        raise ValueError(f"unexpected Worker D queue size: {len(queue_owned)}")

    freshness = [
        row for row in queue["items"]
        if row["classification"] == "SOURCE_LINK_FRESHNESS_OR_DIRECT_EVIDENCE_REQUIRED"
    ]
    if len(freshness) != 1:
        raise ValueError("expected exactly one freshness-sensitive relation")
    if any(
        row["classification"] == "SOURCE_LINK_FRESHNESS_OR_DIRECT_EVIDENCE_REQUIRED"
        for row in packet["items"]
    ):
        raise ValueError("freshness relation leaked into human-review packet")

    freshness_items = freshness_assessment.get("items", [])
    if len(freshness_items) != 1:
        raise ValueError("freshness assessment must contain exactly one relation")
    freshness_item = freshness_items[0]
    if identity_key(freshness_item["identity"]) != identity_key(freshness[0]["identity"]):
        raise ValueError("freshness assessment identity differs from verification queue")
    if len(queue_owned) + len(freshness_items) != remaining:
        raise ValueError("Worker D artifacts do not account for all remaining relations")
    direct = freshness_item.get("direct_evidence", {})
    if not direct.get("source_exists"):
        raise ValueError("freshness-sensitive source existence is not established")
    if not direct.get("exact_source_identity_match"):
        raise ValueError("freshness-sensitive source identity is not exact")
    if not direct.get("amendment_semantics_supported"):
        raise ValueError("freshness-sensitive amendment semantics are not supported")
    if freshness_item.get("freshness", {}).get("state") != "NOT_ESTABLISHED":
        raise ValueError("freshness was promoted without successor-absence proof")
    if freshness_item.get("closure_assessment") != "KEEP_OPEN":
        raise ValueError("freshness-sensitive relation was closed automatically")

    if packet["review_contract"]["automatic_promotion_allowed"]:
        raise ValueError("review packet must prohibit automatic promotion")
    if evidence["review_contract"]["automatic_promotion_allowed"]:
        raise ValueError("evidence pack must prohibit automatic promotion")
    for contract in (packet["review_contract"], evidence["review_contract"]):
        if not contract["ai_proposal_is_not_human_decision"]:
            raise ValueError("AI proposal / human decision separation is not explicit")
        if not contract["reviewer_identity_required_for_decision"]:
            raise ValueError("reviewer identity requirement is missing")
        if not contract["review_timestamp_required_for_decision"]:
            raise ValueError("review timestamp requirement is missing")

    packet_by_key = {row["relation_key"]: row for row in packet["items"]}
    source_pointer_counts = Counter()
    semantic_pointer_counts = Counter()
    human_only_count = 0

    for row in evidence["items"]:
        key = row["relation_key"]
        packet_row = packet_by_key[key]
        if key != identity_key(row["identity"]):
            raise ValueError(f"unstable relation identity: {key}")
        if packet_row["identity"] != row["identity"]:
            raise ValueError(f"packet/evidence identity mismatch: {key}")
        if row["decision_options"] != DECISIONS:
            raise ValueError(f"review decision options changed: {key}")
        if not row["ai_proposal"].startswith("KEEP_OPEN."):
            raise ValueError(f"AI proposal must remain explicitly non-closing: {key}")
        if not row["human_judgment_question"]:
            raise ValueError(f"missing human judgment question: {key}")
        if not row["competing_interpretation_or_ambiguity"]:
            raise ValueError(f"missing ambiguity statement: {key}")
        if row["closure_assessment"] != "KEEP_OPEN":
            raise ValueError(f"unreviewed relation was closed automatically: {key}")
        if row["review_status"] != "NOT_REVIEWED":
            raise ValueError(f"AI-generated packet changed human review state: {key}")
        for field in (
            "reviewed_by",
            "reviewer_rationale",
            "reviewer_name",
            "reviewer_decision",
            "reviewer_note",
            "reviewed_at",
        ):
            if row[field] is not None:
                raise ValueError(f"{field} must stay blank before real human review: {key}")
        if row.get("source_file") != packet_row.get("source_file"):
            raise ValueError(f"source_file provenance mismatch: {key}")
        if row.get("source_state") != packet_row.get("source_state"):
            raise ValueError(f"source_state provenance mismatch: {key}")
        if not row.get("currentness_caveat"):
            raise ValueError(f"currentness caveat is missing: {key}")
        if row.get("unresolved_semantic_question") != row["human_judgment_question"]:
            raise ValueError(f"unresolved semantic question drifted: {key}")
        if row.get("proposed_decision_options") != DECISIONS:
            raise ValueError(f"proposed decision options changed: {key}")
        if not row.get("evidence_pack_ready"):
            raise ValueError(f"evidence pack is not human-review ready: {key}")
        fingerprint = row.get("evidence_fingerprint_sha256", "")
        if len(fingerprint) != 64 or any(
            char not in "0123456789abcdef" for char in fingerprint
        ):
            raise ValueError(f"invalid evidence fingerprint: {key}")
        if not row.get("source_primary_source_locators"):
            raise ValueError(f"source primary-source locator is missing: {key}")
        if not row.get("target_primary_source_locators"):
            raise ValueError(f"target primary-source locator is missing: {key}")

        subclaims = row["machine_verifiable_subclaims"]
        if not subclaims["source_identity_resolved"]:
            raise ValueError(f"source identity is unresolved: {key}")
        if not subclaims["target_identity_resolved"]:
            raise ValueError(f"target identity is unresolved: {key}")
        if subclaims["relation_semantics_verified"]:
            raise ValueError(f"machine subclaim illegally verifies relation semantics: {key}")

        source_status = subclaims["source_pointer_status"]
        source_pointer_counts[source_status] += 1
        if row["classification"] == "SEMANTIC_TEXT_CHECK_REQUIRED":
            semantic_pointer_counts[source_status] += 1

        if source_status == "DIRECT_PRIMARY_TEXT_POINTER":
            source = row["source_evidence"]
            if not (source.get("source_url") and source.get("source_locator")):
                raise ValueError(f"direct primary pointer is incomplete: {key}")
            if not subclaims["source_fingerprint_present"]:
                raise ValueError(f"direct primary pointer lacks a text fingerprint: {key}")
        elif source_status == "MACHINE_RECONSTRUCTED_PRIMARY_CANDIDATE":
            source = row["source_evidence"]
            if not source.get("source_url"):
                raise ValueError(f"reconstructed candidate lacks source URL: {key}")
            if not subclaims["source_fingerprint_present"]:
                raise ValueError(f"reconstructed candidate lacks a text fingerprint: {key}")

        if row["classification"] in HUMAN_ONLY_CLASSIFICATIONS:
            human_only_count += 1
            if row["closure_assessment"] != "KEEP_OPEN":
                raise ValueError(f"human-only relation auto-closed: {key}")

    expected_semantic = {
        "MACHINE_RECONSTRUCTED_PRIMARY_CANDIDATE": 5,
        "PRIMARY_TEXT_POINTER_INCOMPLETE": 12,
    }
    if dict(semantic_pointer_counts) != expected_semantic:
        raise ValueError(
            "semantic-text evidence snapshot changed; re-adjudicate before promotion: "
            f"{dict(semantic_pointer_counts)}"
        )
    if human_only_count != 41:
        raise ValueError(f"unexpected human-only relation count: {human_only_count}")

    expected_source_counts = dict(sorted(source_pointer_counts.items()))
    if evidence["summary"]["source_pointer_status_counts"] != expected_source_counts:
        raise ValueError("source pointer summary is stale")
    if (
        evidence["summary"]["semantic_text_source_pointer_status_counts"]
        != dict(sorted(semantic_pointer_counts.items()))
    ):
        raise ValueError("semantic source pointer summary is stale")
    if evidence["summary"]["closure_assessment_counts"] != {"KEEP_OPEN": 58}:
        raise ValueError("closure assessment summary is not fail-closed")
    if evidence["summary"]["machine_safe_closures"] != 0:
        raise ValueError("machine-safe closures must remain zero for this snapshot")
    if evidence["summary"].get("evidence_pack_ready_items") != len(queue_owned):
        raise ValueError("not all Worker D relations have a review-ready evidence pack")
    if evidence["summary"].get("evidence_pack_not_ready_items") != 0:
        raise ValueError("evidence pack contains non-ready Worker D relations")

    return {
        "inventory_relations": inventory,
        "independently_covered_relations": independently_covered,
        "remaining_relations": remaining,
        "worker_d_review_items": len(queue_owned),
        "freshness_sensitive_relations": len(freshness_items),
        "all_remaining_relations_accounted_for": len(queue_owned) + len(freshness_items),
        "freshness_state": freshness_item["freshness"]["state"],
        "human_only_relations": human_only_count,
        "semantic_text_relations": sum(semantic_pointer_counts.values()),
        "semantic_text_source_pointer_status_counts": dict(
            sorted(semantic_pointer_counts.items())
        ),
        "machine_safe_closures": 0,
        "evidence_pack_ready_items": evidence["summary"]["evidence_pack_ready_items"],
        "review_state": "NOT_REVIEWED",
    }


def main() -> None:
    result = validate()
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
