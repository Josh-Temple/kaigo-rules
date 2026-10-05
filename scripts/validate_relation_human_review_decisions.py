#!/usr/bin/env python3
"""Validate human relation-review decisions against the current evidence fingerprint."""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
DECISIONS_PATH = DATA / "relation-human-review-decisions.json"
EVIDENCE_PATH = DATA / "relation-human-review-evidence-pack.json"
PILOT_PATH = DATA / "relation-human-review-pilot.json"

ALLOWED_DECISIONS = {
    "CONFIRM_RELATION",
    "REJECT_RELATION",
    "NEEDS_MORE_EVIDENCE",
}
ALLOWED_STATES = {"CURRENT", "STALE_EVIDENCE"}
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
}


class ReviewContractError(ValueError):
    pass


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def parse_reviewed_at(value: object) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ReviewContractError("reviewed_at is required")
    normalized = value.strip().replace("Z", "+00:00")
    try:
        datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise ReviewContractError(f"reviewed_at is not valid ISO-8601: {value}") from exc


def validate_decisions(
    ledger: dict | None = None,
    evidence_pack: dict | None = None,
    pilot: dict | None = None,
) -> dict:
    ledger = ledger if ledger is not None else load_json(DECISIONS_PATH)
    evidence_pack = (
        evidence_pack if evidence_pack is not None else load_json(EVIDENCE_PATH)
    )
    pilot = pilot if pilot is not None else load_json(PILOT_PATH)

    if ledger.get("pilot_only") is not True:
        raise ReviewContractError("decision ledger must remain pilot_only in this wave")
    if set(ledger.get("allowed_decisions", [])) != ALLOWED_DECISIONS:
        raise ReviewContractError("decision ledger allowed_decisions drifted")

    evidence_by_key = {
        row["relation_key"]: row for row in evidence_pack.get("items", [])
    }
    pilot_by_key = {row["relation_key"]: row for row in pilot.get("items", [])}

    seen = set()
    current = 0
    stale = 0
    for row in ledger.get("decisions", []):
        relation_key = row.get("relation_key")
        if not isinstance(relation_key, str) or not relation_key:
            raise ReviewContractError("relation_key is required")
        if relation_key in seen:
            raise ReviewContractError(f"duplicate decision for relation: {relation_key}")
        seen.add(relation_key)

        evidence = evidence_by_key.get(relation_key)
        pilot_item = pilot_by_key.get(relation_key)
        if evidence is None:
            raise ReviewContractError(f"decision relation missing from evidence pack: {relation_key}")
        if pilot_item is None:
            raise ReviewContractError(f"decision relation is outside the active pilot: {relation_key}")
        if row.get("review_id") != pilot_item.get("review_id"):
            raise ReviewContractError(f"review_id mismatch: {relation_key}")

        reviewer_identity = row.get("reviewer_identity")
        if not isinstance(reviewer_identity, str) or not reviewer_identity.strip():
            raise ReviewContractError(f"reviewer_identity is required: {relation_key}")
        if reviewer_identity.strip().lower() in OBVIOUS_AI_IDENTITIES:
            raise ReviewContractError(f"AI identity cannot satisfy human review: {relation_key}")

        decision = row.get("reviewer_decision")
        if decision not in ALLOWED_DECISIONS:
            raise ReviewContractError(f"invalid reviewer_decision: {relation_key}")

        rationale = row.get("reviewer_rationale")
        if not isinstance(rationale, str) or not rationale.strip():
            raise ReviewContractError(f"reviewer_rationale is required: {relation_key}")

        parse_reviewed_at(row.get("reviewed_at"))

        if row.get("reviewer_attestation") != HUMAN_ATTESTATION:
            raise ReviewContractError(f"human reviewer attestation is required: {relation_key}")

        fingerprint = row.get("evidence_fingerprint_sha256")
        if not isinstance(fingerprint, str) or HEX64.fullmatch(fingerprint) is None:
            raise ReviewContractError(f"invalid evidence fingerprint: {relation_key}")

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
        else:
            if matches:
                raise ReviewContractError(
                    f"STALE_EVIDENCE marker has no fingerprint mismatch: {relation_key}"
                )
            stale += 1

    return {
        "pilot_items": len(pilot_by_key),
        "decision_records": len(seen),
        "current_human_decisions": current,
        "stale_evidence_decisions": stale,
        "unreviewed_pilot_items": len(pilot_by_key) - current,
    }


def main() -> None:
    result = validate_decisions()
    print(
        "relation human-review decisions: "
        f"{result['current_human_decisions']} current, "
        f"{result['stale_evidence_decisions']} stale, "
        f"{result['unreviewed_pilot_items']} pilot items awaiting human review"
    )


if __name__ == "__main__":
    main()
