#!/usr/bin/env python3
"""Validate human relation-review decisions against active batches and current evidence."""

from __future__ import annotations

import json
import re
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
DECISIONS_PATH = DATA / "relation-human-review-decisions.json"
EVIDENCE_PATH = DATA / "relation-human-review-evidence-pack.json"
BATCH_REGISTRY_PATH = DATA / "relation-human-review-batches.json"

ALLOWED_DECISIONS = {
    "CONFIRM_RELATION",
    "REJECT_RELATION",
    "NEEDS_MORE_EVIDENCE",
}
ALLOWED_STATES = {"CURRENT", "STALE_EVIDENCE", "SUPERSEDED"}
HUMAN_ATTESTATION = "HUMAN_REVIEW_COMPLETED"
HEX64 = re.compile(r"^[0-9a-f]{64}$")
OBVIOUS_AI_IDENTITIES = {
    "ai",
    "assistant",
    "automation",
    "automated",
    "chatgpt",
    "machine",
    "openai",
    "gpt",
    "gpt-5",
    "gpt-5.6",
    "gpt-5.6-sol",
}


class ReviewContractError(ValueError):
    pass


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def parse_reviewed_at(value: object) -> datetime:
    if not isinstance(value, str) or not value.strip():
        raise ReviewContractError("reviewed_at is required")
    normalized = value.strip().replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise ReviewContractError(f"reviewed_at is not valid ISO-8601: {value}") from exc


def active_batch_items(registry: dict[str, Any]) -> dict[str, dict[str, Any]]:
    active: dict[str, dict[str, Any]] = {}
    for batch in registry.get("batches", []):
        batch_id = batch.get("batch_id")
        if not isinstance(batch_id, str) or not batch_id:
            raise ReviewContractError("batch_id is required")
        for item in batch.get("items", []):
            relation_key = item.get("relation_key")
            if not isinstance(relation_key, str) or not relation_key:
                raise ReviewContractError(f"batch item relation_key missing: {batch_id}")
            if relation_key in active:
                raise ReviewContractError(
                    f"relation appears in more than one active batch: {relation_key}"
                )
            active[relation_key] = {**item, "batch_id": batch_id}
    return active


def obvious_ai_identity(value: str) -> bool:
    normalized = " ".join(value.strip().lower().split())
    return normalized in OBVIOUS_AI_IDENTITIES


def validate_decisions(
    ledger: dict[str, Any] | None = None,
    evidence_pack: dict[str, Any] | None = None,
    batch_registry: dict[str, Any] | None = None,
) -> dict[str, Any]:
    ledger = ledger if ledger is not None else load_json(DECISIONS_PATH)
    evidence_pack = (
        evidence_pack if evidence_pack is not None else load_json(EVIDENCE_PATH)
    )
    batch_registry = (
        batch_registry
        if batch_registry is not None
        else load_json(BATCH_REGISTRY_PATH)
    )

    if ledger.get("batch_membership_required") is not True:
        raise ReviewContractError("decision ledger must require active batch membership")
    if ledger.get("pilot_only") is not False:
        raise ReviewContractError("decision ledger must support active batches beyond pilot 1")
    if set(ledger.get("allowed_decisions", [])) != ALLOWED_DECISIONS:
        raise ReviewContractError("decision ledger allowed_decisions drifted")
    if set(ledger.get("allowed_decision_states", [])) != ALLOWED_STATES:
        raise ReviewContractError("decision ledger allowed_decision_states drifted")

    evidence_by_key = {
        row["relation_key"]: row for row in evidence_pack.get("items", [])
    }
    active_by_key = active_batch_items(batch_registry)

    decisions = ledger.get("decisions", [])
    decision_by_id: dict[str, dict[str, Any]] = {}
    relation_records: dict[str, list[dict[str, Any]]] = defaultdict(list)

    current = 0
    stale = 0
    superseded = 0
    needs_more = 0

    for row in decisions:
        decision_id = row.get("decision_id")
        if not isinstance(decision_id, str) or not decision_id.strip():
            raise ReviewContractError("decision_id is required")
        if decision_id in decision_by_id:
            raise ReviewContractError(f"duplicate decision_id: {decision_id}")
        decision_by_id[decision_id] = row

        relation_key = row.get("relation_key")
        if not isinstance(relation_key, str) or not relation_key:
            raise ReviewContractError(f"relation_key is required: {decision_id}")
        evidence = evidence_by_key.get(relation_key)
        active_item = active_by_key.get(relation_key)
        if evidence is None:
            raise ReviewContractError(
                f"decision relation missing from evidence pack: {relation_key}"
            )
        if active_item is None:
            raise ReviewContractError(
                f"decision relation is outside active review batches: {relation_key}"
            )
        if row.get("review_id") != active_item.get("review_id"):
            raise ReviewContractError(f"review_id mismatch: {relation_key}")
        if row.get("batch_id") != active_item.get("batch_id"):
            raise ReviewContractError(f"batch_id mismatch: {relation_key}")

        reviewer_identity = row.get("reviewer_identity")
        if not isinstance(reviewer_identity, str) or not reviewer_identity.strip():
            raise ReviewContractError(
                f"reviewer_identity is required: {relation_key}"
            )
        if obvious_ai_identity(reviewer_identity):
            raise ReviewContractError(
                f"AI identity cannot satisfy human review: {relation_key}"
            )

        decision = row.get("reviewer_decision")
        if decision not in ALLOWED_DECISIONS:
            raise ReviewContractError(f"invalid reviewer_decision: {relation_key}")

        rationale = row.get("reviewer_rationale")
        if not isinstance(rationale, str) or not rationale.strip():
            raise ReviewContractError(
                f"reviewer_rationale is required: {relation_key}"
            )

        reviewed_at = parse_reviewed_at(row.get("reviewed_at"))

        if row.get("reviewer_attestation") != HUMAN_ATTESTATION:
            raise ReviewContractError(
                f"human reviewer attestation is required: {relation_key}"
            )

        fingerprint = row.get("evidence_fingerprint_sha256")
        if not isinstance(fingerprint, str) or HEX64.fullmatch(fingerprint) is None:
            raise ReviewContractError(
                f"invalid evidence fingerprint: {relation_key}"
            )

        state = row.get("decision_state")
        if state not in ALLOWED_STATES:
            raise ReviewContractError(f"invalid decision_state: {relation_key}")

        current_fingerprint = evidence.get("evidence_fingerprint_sha256")
        matches = fingerprint == current_fingerprint
        if state == "CURRENT":
            if not matches:
                raise ReviewContractError(
                    f"stale evidence decision marked CURRENT: {relation_key}; "
                    "re-review or mark STALE_EVIDENCE"
                )
            current += 1
            if decision == "NEEDS_MORE_EVIDENCE":
                needs_more += 1
        elif state == "STALE_EVIDENCE":
            if matches:
                raise ReviewContractError(
                    f"STALE_EVIDENCE marker has no fingerprint mismatch: {relation_key}"
                )
            stale += 1
        else:
            replacement = row.get("superseded_by_decision_id")
            if not isinstance(replacement, str) or not replacement.strip():
                raise ReviewContractError(
                    f"SUPERSEDED decision requires superseded_by_decision_id: {relation_key}"
                )
            superseded += 1

        relation_records[relation_key].append(
            {
                **row,
                "_reviewed_at": reviewed_at,
                "_fingerprint_matches_current": matches,
            }
        )

    # Validate replacement chains and allow at most one non-superseded record per relation.
    for relation_key, records in relation_records.items():
        live_records = [
            row for row in records if row.get("decision_state") != "SUPERSEDED"
        ]
        if len(live_records) > 1:
            raise ReviewContractError(
                f"multiple non-superseded decisions for relation: {relation_key}"
            )
        for row in records:
            if row.get("decision_state") != "SUPERSEDED":
                continue
            replacement_id = row["superseded_by_decision_id"]
            replacement = decision_by_id.get(replacement_id)
            if replacement is None:
                raise ReviewContractError(
                    f"superseding decision does not exist: {replacement_id}"
                )
            if replacement.get("relation_key") != relation_key:
                raise ReviewContractError(
                    f"superseding decision targets a different relation: {replacement_id}"
                )
            replacement_time = parse_reviewed_at(replacement.get("reviewed_at"))
            if replacement_time < row["_reviewed_at"]:
                raise ReviewContractError(
                    f"superseding decision predates replaced decision: {replacement_id}"
                )

    reviewed_relations = {
        relation_key
        for relation_key, records in relation_records.items()
        if any(row.get("decision_state") == "CURRENT" for row in records)
    }

    return {
        "active_batch_items": len(active_by_key),
        "decision_records": len(decision_by_id),
        "current_human_decisions": current,
        "stale_evidence_decisions": stale,
        "superseded_decisions": superseded,
        "current_needs_more_evidence": needs_more,
        "unreviewed_active_items": len(active_by_key) - len(reviewed_relations),
        "validated_decisions": [
            {
                key: value
                for key, value in row.items()
                if not key.startswith("_")
            }
            for records in relation_records.values()
            for row in records
        ],
    }


def main() -> None:
    result = validate_decisions()
    print(
        "relation human-review decisions: "
        f"{result['current_human_decisions']} current, "
        f"{result['stale_evidence_decisions']} stale, "
        f"{result['superseded_decisions']} superseded, "
        f"{result['unreviewed_active_items']} active items awaiting human review"
    )


if __name__ == "__main__":
    main()
