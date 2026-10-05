#!/usr/bin/env python3
"""Build cell-level publication readiness from publication-unit requirements.

This is a projection only. A READY cell means at least one explicitly scoped
publication unit is ready for review; it never writes publication or route state.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MATRIX_PATH = ROOT / "data/database-coverage-matrix.generated.json"
SCOPING_PATH = ROOT / "data/publication-requirement-scoping.json"
PILOT_PATH = ROOT / "data/relation-human-review-pilot.json"
BATCHES_PATH = ROOT / "data/relation-human-review-batches.json"
DECISIONS_PATH = ROOT / "data/relation-human-review-decisions.json"
OUTPUT_PATH = ROOT / "data/publication-readiness.generated.json"

BLOCKER_ORDER = (
    "BLOCKED_CORPUS",
    "BLOCKED_SCOPE",
    "BLOCKED_INGESTION",
    "BLOCKED_ITEM_BODY",
    "BLOCKED_CURRENTNESS",
    "BLOCKED_RELATION_REQUIREMENT_UNRESOLVED",
    "BLOCKED_RELATION",
    "BLOCKED_HUMAN_REVIEW_REQUIREMENT_UNRESOLVED",
    "BLOCKED_HUMAN_REVIEW",
)

def _load(path: Path):
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)

def _state(cell: dict, axis: str) -> str:
    return str((cell.get(axis) or {}).get("state", "MISSING"))

def _review_items(payload: dict) -> list[dict]:
    for key in ("items", "review_items", "pilot_items"):
        value = payload.get(key)
        if isinstance(value, list):
            return value
    return []

def _batch_rows(payload: dict) -> list[dict]:
    value = payload.get("batches")
    return value if isinstance(value, list) else []

def _ordered_blockers(values: set[str]) -> list[str]:
    known = [value for value in BLOCKER_ORDER if value in values]
    unknown = sorted(values - set(BLOCKER_ORDER))
    return known + unknown

def build_artifact() -> dict:
    matrix = _load(MATRIX_PATH)
    scoping = _load(SCOPING_PATH)
    pilot = _load(PILOT_PATH) if PILOT_PATH.exists() else {}
    batches = _load(BATCHES_PATH) if BATCHES_PATH.exists() else {"batches": []}
    decisions = _load(DECISIONS_PATH) if DECISIONS_PATH.exists() else {"decisions": []}

    matrix_cells = {}
    for service in matrix["services"]:
        for cell in service["source_families"]:
            matrix_cells[(service["service_id"], cell["source_family"])] = (service, cell)

    scoped_cells = {
        (row["service_id"], row["source_family"]): row
        for row in scoping.get("cells", [])
    }
    if set(scoped_cells) != set(matrix_cells):
        raise ValueError("publication requirement scoping does not cover the current matrix exactly")

    definitions = {
        row["unit_type"]: row
        for row in scoping.get("publication_unit_definitions", [])
    }

    rows = []
    primary = Counter()
    blocked_cell_reasons = Counter()
    unit_blockers = Counter()
    family_counts = defaultdict(Counter)
    ready_unit_counts = Counter()

    for key, (service, cell) in matrix_cells.items():
        scoped = scoped_cells[key]
        units = scoped.get("publication_units") or []
        ready_units = [
            row["unit_type"]
            for row in units
            if row.get("readiness") == "READY_FOR_PUBLICATION_REVIEW"
        ]
        not_applicable = bool(units) and all(
            row.get("readiness") == "NOT_APPLICABLE" for row in units
        )
        blocker_set = {
            reason
            for row in units
            for reason in (row.get("blocking_reasons") or [])
        }
        unit_blockers.update(
            reason
            for row in units
            for reason in (row.get("blocking_reasons") or [])
        )

        if ready_units:
            readiness = "READY_FOR_PUBLICATION_REVIEW"
            blocking_reasons = []
        elif not_applicable:
            readiness = "NOT_APPLICABLE"
            blocking_reasons = []
        else:
            blocking_reasons = _ordered_blockers(blocker_set)
            readiness = blocking_reasons[0] if blocking_reasons else "BLOCKED_REQUIREMENT_UNRESOLVED"
            blocked_cell_reasons.update(blocking_reasons)

        ready_fields = sorted({
            field
            for unit_type in ready_units
            for field in (definitions.get(unit_type, {}).get("field_allowlist") or [])
        })
        for unit_type in ready_units:
            ready_unit_counts[unit_type] += 1

        axis_states = {
            "corpus_availability": _state(cell, "corpus_availability"),
            "service_scope": _state(cell, "service_scope"),
            "ingestion": _state(cell, "ingestion"),
            "item_body_verification": _state(cell, "item_body_verification"),
            "currentness": _state(cell, "currentness"),
            "relation_verification": _state(cell, "relation_verification"),
            "human_review": _state(cell, "human_review"),
        }
        primary[readiness] += 1
        family_counts[cell["source_family"]][readiness] += 1
        rows.append({
            "service_id": service["service_id"],
            "service_label": service.get("label"),
            "source_family": cell["source_family"],
            "source_family_label": cell.get("label"),
            "readiness": readiness,
            "blocking_reasons": blocking_reasons,
            "ready_publication_units": ready_units,
            "publication_field_allowlist": ready_fields,
            "axis_states": axis_states,
            "publication_observation": _state(cell, "publication"),
            "route_exposure_observation": _state(cell, "route_exposure"),
        })

    pilot_items = _review_items(pilot)
    stored_decisions = decisions.get("decisions") if isinstance(decisions.get("decisions"), list) else []
    batch_rows = _batch_rows(batches)
    decision_state_counts = Counter(
        d.get("decision_status", d.get("evidence_status", "UNSPECIFIED"))
        for d in stored_decisions
    )

    return {
        "format_version": 2,
        "generated_by": "scripts/build_publication_readiness.py",
        "projection_only": True,
        "policy": {
            "publication_writeback_allowed": False,
            "route_auto_enable_allowed": False,
            "readiness_implies_publication": False,
            "ai_review_completion_allowed": False,
            "single_completion_percentage_allowed": False,
            "not_required_means_canonical_pass": False,
            "unit_requirement_scoping_required": True,
        },
        "canonical_inputs": [
            "data/database-coverage-matrix.generated.json",
            "data/publication-requirement-scoping.json",
            "data/relation-human-review-pilot.json",
            "data/relation-human-review-batches.json",
            "data/relation-human-review-decisions.json",
        ],
        "summary": {
            "total_cells": len(rows),
            "ready_candidates": primary.get("READY_FOR_PUBLICATION_REVIEW", 0),
            "primary_readiness": dict(sorted(primary.items())),
            "blocking_axis_counts": dict(sorted(blocked_cell_reasons.items())),
            "publication_unit_blocking_counts": dict(sorted(unit_blockers.items())),
            "ready_publication_units": dict(sorted(ready_unit_counts.items())),
            "by_source_family": {
                family: dict(sorted(counts.items()))
                for family, counts in sorted(family_counts.items())
            },
            "human_review": {
                "pilot_items": len(pilot_items),
                "pilot_ready_for_human_review": sum(
                    1 for item in pilot_items
                    if item.get("review_status") == "READY_FOR_HUMAN_REVIEW"
                ),
                "active_batches": len(batch_rows),
                "stored_decisions": len(stored_decisions),
                "decision_state_counts": dict(sorted(decision_state_counts.items())),
            },
        },
        "cells": rows,
    }

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    artifact = build_artifact()
    rendered = json.dumps(artifact, ensure_ascii=False, indent=2) + "\n"
    if args.check:
        if not OUTPUT_PATH.exists() or OUTPUT_PATH.read_text(encoding="utf-8") != rendered:
            raise SystemExit("publication readiness artifact is stale; run builder")
        print("publication readiness artifact: PASS")
        return
    OUTPUT_PATH.write_text(rendered, encoding="utf-8")
    print(f"wrote {OUTPUT_PATH.relative_to(ROOT)}")

if __name__ == "__main__":
    main()
