#!/usr/bin/env python3
"""Validate Worker C publication requirement scoping and fail-closed readiness semantics."""
from __future__ import annotations

import importlib.util
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUILDER_PATH = ROOT / "scripts/build_publication_requirement_scoping.py"
ARTIFACT_PATH = ROOT / "data/publication-requirement-scoping.json"

spec = importlib.util.spec_from_file_location("publication_requirement_scoping_builder", BUILDER_PATH)
builder = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(builder)


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def fail(message: str):
    raise SystemExit(f"publication requirement scoping validation failed: {message}")


def validate() -> dict:
    artifact = load(ARTIFACT_PATH)
    rebuilt = builder.build_artifact()
    if artifact != rebuilt:
        fail("artifact is stale or does not match canonical inputs")

    policy = artifact.get("policy") or {}
    must_be_false = (
        "canonical_relation_writeback_allowed",
        "canonical_human_review_writeback_allowed",
        "publication_writeback_allowed",
        "route_auto_enable_allowed",
        "readiness_implies_publication",
        "not_required_means_pass",
        "unverified_relations_may_influence_safe_units",
        "unreviewed_explanations_may_influence_safe_units",
    )
    for key in must_be_false:
        if policy.get(key) is not False:
            fail(f"unsafe policy flag: {key}")
    if policy.get("currentness_required_for_every_publication_unit") is not True:
        fail("currentness must remain required for every publication unit")
    if policy.get("field_allowlist_is_exhaustive") is not True:
        fail("publication field allowlists must be exhaustive")

    definitions = artifact.get("publication_unit_definitions")
    if not isinstance(definitions, list) or not definitions:
        fail("publication unit definitions missing")
    by_type = {row.get("unit_type"): row for row in definitions}
    if len(by_type) != len(definitions):
        fail("duplicate publication unit type")

    relation_fields = {"relation_identity", "relation_label", "target_url", "target_locator"}
    review_fields = {"reviewed_explanatory_text", "review_decision_reference"}
    for unit_type, definition in by_type.items():
        relation_requirement = definition.get("relation_requirement")
        human_requirement = definition.get("human_review_requirement")
        if relation_requirement not in builder.REQUIREMENT_VALUES:
            fail(f"{unit_type}: unsupported relation requirement")
        if human_requirement not in builder.REQUIREMENT_VALUES:
            fail(f"{unit_type}: unsupported human-review requirement")
        fields = definition.get("field_allowlist")
        if not isinstance(fields, list) or not fields:
            fail(f"{unit_type}: field allowlist missing")
        if len(fields) != len(set(fields)):
            fail(f"{unit_type}: duplicate field in allowlist")
        if set(fields) - builder.ALL_PUBLICATION_FIELDS:
            fail(f"{unit_type}: unknown field in allowlist")
        if relation_requirement == "NOT_REQUIRED" and set(fields) & relation_fields:
            fail(f"{unit_type}: relation field exposed despite relation NOT_REQUIRED")
        if human_requirement == "NOT_REQUIRED" and set(fields) & review_fields:
            fail(f"{unit_type}: review-dependent field exposed despite human review NOT_REQUIRED")

    if by_type.get("CROSS_LAYER_RELATION_LINK", {}).get("relation_requirement") != "REQUIRED":
        fail("cross-layer relation assertion must require relation verification")
    interpretive = by_type.get("INTERPRETIVE_RELATION_EXPLANATION") or {}
    if interpretive.get("relation_requirement") != "REQUIRED":
        fail("interpretive relation explanation must require relation verification")
    if interpretive.get("human_review_requirement") != "REQUIRED":
        fail("interpretive relation explanation must require human review")
    review_only = by_type.get("REVIEW_DEPENDENT_EXPLANATORY_TEXT") or {}
    if review_only.get("human_review_requirement") != "REQUIRED":
        fail("review-dependent explanatory text must require human review")

    cells = artifact.get("cells")
    if not isinstance(cells, list) or len(cells) != 351:
        fail("expected exactly 351 service x source-family cells")

    seen_cells = set()
    candidate_count = 0
    blocker_counts = Counter()
    for cell in cells:
        cell_key = (cell.get("service_id"), cell.get("source_family"))
        if cell_key in seen_cells:
            fail(f"duplicate cell: {cell_key}")
        seen_cells.add(cell_key)
        axes = cell.get("canonical_axis_observations") or {}
        units = cell.get("publication_units")
        if not isinstance(units, list) or len(units) != len(definitions):
            fail(f"{cell_key}: publication unit count mismatch")
        if {row.get("unit_type") for row in units} != set(by_type):
            fail(f"{cell_key}: publication unit coverage mismatch")

        for unit in units:
            unit_type = unit.get("unit_type")
            definition = by_type[unit_type]
            blockers = unit.get("blocking_reasons")
            if not isinstance(blockers, list):
                fail(f"{cell_key}/{unit_type}: blockers must be a list")
            blocker_counts.update(blockers)
            if unit.get("canonical_relation_state_observed") != axes.get("relation_verification"):
                fail(f"{cell_key}/{unit_type}: canonical relation observation changed")
            if unit.get("canonical_human_review_state_observed") != axes.get("human_review"):
                fail(f"{cell_key}/{unit_type}: canonical human-review observation changed")
            if unit.get("relation_requirement") != definition.get("relation_requirement"):
                fail(f"{cell_key}/{unit_type}: relation requirement drift")
            if unit.get("human_review_requirement") != definition.get("human_review_requirement"):
                fail(f"{cell_key}/{unit_type}: human-review requirement drift")
            if unit.get("field_allowlist_ref") != unit_type:
                fail(f"{cell_key}/{unit_type}: invalid field allowlist reference")

            if definition["relation_requirement"] == "NOT_REQUIRED" and "BLOCKED_RELATION" in blockers:
                fail(f"{cell_key}/{unit_type}: irrelevant relation blocker retained")
            if definition["human_review_requirement"] == "NOT_REQUIRED" and "BLOCKED_HUMAN_REVIEW" in blockers:
                fail(f"{cell_key}/{unit_type}: irrelevant human-review blocker retained")

            state = unit.get("readiness")
            if state == "READY_FOR_PUBLICATION_REVIEW":
                candidate_count += 1
                if blockers:
                    fail(f"{cell_key}/{unit_type}: ready unit has blockers")
                if axes.get("currentness") not in builder.CURRENTNESS_PASS:
                    fail(f"{cell_key}/{unit_type}: unresolved currentness became ready")
            elif state == "NOT_APPLICABLE":
                if blockers:
                    fail(f"{cell_key}/{unit_type}: not-applicable unit has blockers")
            else:
                if not blockers:
                    fail(f"{cell_key}/{unit_type}: blocked unit lacks blockers")
                if state != blockers[0]:
                    fail(f"{cell_key}/{unit_type}: primary readiness is not first blocker")

    summary = artifact.get("summary") or {}
    if summary.get("service_source_family_cells") != 351:
        fail("summary cell count mismatch")
    if summary.get("publication_units_total") != 351 * len(definitions):
        fail("summary publication unit count mismatch")
    if summary.get("ready_for_publication_review_candidates") != candidate_count:
        fail("summary candidate count mismatch")
    if summary.get("blocking_reason_counts") != dict(sorted(blocker_counts.items())):
        fail("summary blocker counts mismatch")

    return {
        "cells": len(cells),
        "unit_types": len(definitions),
        "publication_units": 351 * len(definitions),
        "ready_candidates": candidate_count,
        "blockers": dict(sorted(blocker_counts.items())),
    }


if __name__ == "__main__":
    print(json.dumps({"result": "PASS", **validate()}, ensure_ascii=False))
