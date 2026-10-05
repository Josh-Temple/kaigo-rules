#!/usr/bin/env python3
"""Project valid human-review decisions into relation closure effects without mutating canonical relations."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

from validate_relation_human_review_decisions import (
    DECISIONS_PATH,
    ROOT,
    load_json,
    validate_decisions,
)

OUTPUT = ROOT / "data/relation-human-review-decision-effects.generated.json"


def build() -> dict[str, Any]:
    ledger = load_json(DECISIONS_PATH)
    validation = validate_decisions(ledger=ledger)
    effects: list[dict[str, Any]] = []

    for row in validation["validated_decisions"]:
        state = row.get("decision_state")
        if state != "CURRENT":
            continue
        decision = row["reviewer_decision"]
        if decision == "CONFIRM_RELATION":
            effect = "CONFIRM_RELATION_CANDIDATE"
            closes_relation_review = True
        elif decision == "REJECT_RELATION":
            effect = "REJECT_RELATION_CANDIDATE"
            closes_relation_review = True
        else:
            effect = "KEEP_OPEN_NEEDS_MORE_EVIDENCE"
            closes_relation_review = False

        effects.append(
            {
                "decision_id": row["decision_id"],
                "batch_id": row["batch_id"],
                "review_id": row["review_id"],
                "relation_key": row["relation_key"],
                "reviewer_decision": decision,
                "decision_effect": effect,
                "closes_relation_review": closes_relation_review,
                "evidence_fingerprint_sha256": row[
                    "evidence_fingerprint_sha256"
                ],
                "reviewed_at": row["reviewed_at"],
                "canonical_relation_mutation_applied": False,
                "canonical_mutation_owner": "existing relation generator / integrator",
            }
        )

    counts = Counter(effect["decision_effect"] for effect in effects)
    closure_candidates = sum(
        bool(effect["closes_relation_review"]) for effect in effects
    )

    return {
        "format_version": 1,
        "generated_by": "scripts/build_relation_human_review_decision_effects.py",
        "source_decision_ledger": "data/relation-human-review-decisions.json",
        "source_batch_registry": "data/relation-human-review-batches.json",
        "policy": (
            "This is a projection/receipt only. CONFIRM_RELATION and REJECT_RELATION "
            "may produce closure candidates for the canonical relation owner. "
            "NEEDS_MORE_EVIDENCE never closes a relation. STALE_EVIDENCE and SUPERSEDED "
            "records have no current effect. No canonical relation is mutated here."
        ),
        "summary": {
            "decision_records": validation["decision_records"],
            "current_human_decisions": validation["current_human_decisions"],
            "stale_evidence_decisions": validation["stale_evidence_decisions"],
            "superseded_decisions": validation["superseded_decisions"],
            "current_needs_more_evidence": validation[
                "current_needs_more_evidence"
            ],
            "effect_records": len(effects),
            "closure_candidates": closure_candidates,
            "effect_counts": dict(counts),
        },
        "effects": effects,
        "safety": {
            "ai_decision_generated": False,
            "canonical_relation_mutated": False,
            "needs_more_evidence_counted_as_closure": False,
            "stale_decision_counted_as_current": False,
            "superseded_decision_counted_as_current": False,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    rendered = json.dumps(build(), ensure_ascii=False, indent=2) + "\n"
    if args.check:
        committed = OUTPUT.read_text(encoding="utf-8") if OUTPUT.exists() else ""
        if committed != rendered:
            raise SystemExit(
                "relation human-review decision effects are stale; run builder"
            )
        print("relation human-review decision effects: current")
        return
    OUTPUT.write_text(rendered, encoding="utf-8")
    print(f"wrote {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
