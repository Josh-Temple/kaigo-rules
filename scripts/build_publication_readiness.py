#!/usr/bin/env python3
import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MATRIX_PATH = ROOT / "data/database-coverage-matrix.generated.json"
PILOT_PATH = ROOT / "data/relation-human-review-pilot.json"
DECISIONS_PATH = ROOT / "data/relation-human-review-decisions.json"
OUTPUT_PATH = ROOT / "data/publication-readiness.generated.json"

CURRENTNESS_PASS = {"PASS", "CURRENT", "CURRENT_OFFICIAL_CONSOLIDATED", "CURRENT_OFFICIAL_VERSIONED"}
RELATION_PASS = {"PASS", "VERIFIED", "NOT_APPLICABLE"}
HUMAN_REVIEW_PASS = {"REVIEWED", "PASS", "NOT_APPLICABLE"}

def _load(path):
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)

def _state(cell, axis):
    value = cell.get(axis) or {}
    return value.get("state", "MISSING")

def classify_cell(cell):
    axis_states = {
        "corpus_availability": _state(cell, "corpus_availability"),
        "service_scope": _state(cell, "service_scope"),
        "ingestion": _state(cell, "ingestion"),
        "item_body_verification": _state(cell, "item_body_verification"),
        "currentness": _state(cell, "currentness"),
        "relation_verification": _state(cell, "relation_verification"),
        "human_review": _state(cell, "human_review"),
    }

    if any(axis_states[key] == "NOT_APPLICABLE" for key in ("ingestion", "item_body_verification", "currentness")):
        return "NOT_APPLICABLE", [], axis_states

    blockers = []
    if axis_states["corpus_availability"] != "AVAILABLE":
        blockers.append("BLOCKED_CORPUS")
    if axis_states["service_scope"] != "SCOPE_DEFINED":
        blockers.append("BLOCKED_SCOPE")
    if axis_states["ingestion"] != "INGESTED":
        blockers.append("BLOCKED_INGESTION")
    if axis_states["item_body_verification"] != "PASS":
        blockers.append("BLOCKED_ITEM_BODY")
    if axis_states["currentness"] not in CURRENTNESS_PASS:
        blockers.append("BLOCKED_CURRENTNESS")
    if axis_states["relation_verification"] not in RELATION_PASS:
        blockers.append("BLOCKED_RELATION")
    if axis_states["human_review"] not in HUMAN_REVIEW_PASS:
        blockers.append("BLOCKED_HUMAN_REVIEW")

    return (blockers[0] if blockers else "READY_FOR_PUBLICATION_REVIEW"), blockers, axis_states

def _review_items(pilot):
    for key in ("items", "review_items", "pilot_items"):
        value = pilot.get(key)
        if isinstance(value, list):
            return value
    return []

def build_artifact():
    matrix = _load(MATRIX_PATH)
    pilot = _load(PILOT_PATH) if PILOT_PATH.exists() else {}
    decisions = _load(DECISIONS_PATH) if DECISIONS_PATH.exists() else {"decisions": []}

    rows = []
    primary = Counter()
    blocker_counts = Counter()
    family_counts = defaultdict(Counter)

    for service in matrix["services"]:
        for cell in service["source_families"]:
            readiness, blockers, axis_states = classify_cell(cell)
            primary[readiness] += 1
            family_counts[cell["source_family"]][readiness] += 1
            blocker_counts.update(blockers)
            rows.append({
                "service_id": service["service_id"],
                "service_label": service.get("label"),
                "source_family": cell["source_family"],
                "source_family_label": cell.get("label"),
                "readiness": readiness,
                "blocking_reasons": blockers,
                "axis_states": axis_states,
                "publication_observation": _state(cell, "publication"),
                "route_exposure_observation": _state(cell, "route_exposure"),
            })

    pilot_items = _review_items(pilot)
    stored_decisions = decisions.get("decisions") if isinstance(decisions.get("decisions"), list) else []
    decision_state_counts = Counter(
        d.get("decision_status", d.get("evidence_status", "UNSPECIFIED")) for d in stored_decisions
    )

    return {
        "format_version": 1,
        "generated_by": "scripts/build_publication_readiness.py",
        "projection_only": True,
        "policy": {
            "publication_writeback_allowed": False,
            "route_auto_enable_allowed": False,
            "readiness_implies_publication": False,
            "ai_review_completion_allowed": False,
            "single_completion_percentage_allowed": False,
        },
        "canonical_inputs": [
            "data/database-coverage-matrix.generated.json",
            "data/relation-human-review-pilot.json",
            "data/relation-human-review-decisions.json",
        ],
        "summary": {
            "total_cells": len(rows),
            "primary_readiness": dict(sorted(primary.items())),
            "blocking_axis_counts": dict(sorted(blocker_counts.items())),
            "by_source_family": {
                family: dict(sorted(counts.items()))
                for family, counts in sorted(family_counts.items())
            },
            "human_review_pilot": {
                "pilot_items": len(pilot_items),
                "ready_for_human_review": sum(
                    1 for item in pilot_items if item.get("review_status") == "READY_FOR_HUMAN_REVIEW"
                ),
                "stored_decisions": len(stored_decisions),
                "decision_state_counts": dict(sorted(decision_state_counts.items())),
            },
        },
        "cells": rows,
    }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    artifact = build_artifact()

    if args.check:
        if not OUTPUT_PATH.exists():
            raise SystemExit("publication readiness artifact missing; run builder")
        current = _load(OUTPUT_PATH)
        if current != artifact:
            raise SystemExit("publication readiness artifact is stale; run builder")
        print("publication readiness artifact: PASS")
        return

    OUTPUT_PATH.write_text(
        json.dumps(artifact, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"wrote {OUTPUT_PATH.relative_to(ROOT)}")

if __name__ == "__main__":
    main()
