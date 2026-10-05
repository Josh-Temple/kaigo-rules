#!/usr/bin/env python3
"""Validate Worker B's projected publication-readiness impact without writing generated artifacts."""
from __future__ import annotations

import json
from pathlib import Path

import build_database_coverage_matrix as coverage
import build_publication_requirement_scoping as publication

ROOT = Path(__file__).resolve().parents[1]
BASE_MATRIX = ROOT / "data/database-coverage-matrix.generated.json"

TARGETS = {
    "preventive-homebath",
    "preventive-homenursing",
    "preventive-homerehab",
    "preventive-homecaremanagement",
    "preventive-dayrehab",
    "preventive-shortstay-life",
    "preventive-shortstay-medical",
    "preventive-specific-facility",
    "preventive-welfare-equipment-rental",
    "specific-preventive-welfare-equipment-sale",
}
FAMILY = "governing_standards_ordinance"
EXPECTED_SAFE_UNITS = {
    "SOURCE_TEXT_ITEM_BODY",
    "SOURCE_METADATA_LOCATOR",
    "CURRENTNESS_STATEMENT",
    "SERVICE_APPLICABILITY_STATEMENT",
}


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def cells(matrix: dict):
    return {
        (service["service_id"], cell["source_family"]): cell
        for service in matrix["services"]
        for cell in service["source_families"]
    }


def ready_units(cell: dict) -> set[str]:
    axes = publication.axis_observations(cell)
    result = set()
    for definition in publication.PUBLICATION_UNIT_DEFINITIONS:
        evaluated = publication.evaluate_publication_unit(axes, definition)
        if evaluated["readiness"] == "READY_FOR_PUBLICATION_REVIEW":
            result.add(evaluated["unit_type"])
    return result


def main() -> int:
    base = load(BASE_MATRIX)
    projected = coverage.build()
    base_cells = cells(base)
    projected_cells = cells(projected)

    failures = []
    newly_ready_units = 0
    impact = []

    base_gaps = len(base["summary"]["currentness_gaps"])
    projected_gaps = len(projected["summary"]["currentness_gaps"])
    if base_gaps - projected_gaps != len(TARGETS):
        failures.append(
            f"currentness gap reduction mismatch: before={base_gaps} after={projected_gaps}"
        )

    projected_coverage = (
        projected["summary"]["source_family_coverage"][FAMILY]["currentness"]
    )
    if projected_coverage != {"NOT_ESTABLISHED": 17, "PARTIAL": 2, "PASS": 20}:
        failures.append(
            f"governing-standards projected currentness mismatch: {projected_coverage}"
        )

    for service_id in sorted(TARGETS):
        before = base_cells[(service_id, FAMILY)]
        after = projected_cells[(service_id, FAMILY)]
        before_ready = ready_units(before)
        after_ready = ready_units(after)
        newly_ready = after_ready - before_ready

        if (before.get("currentness") or {}).get("state") == "PASS":
            failures.append(f"{service_id}: target was already currentness PASS")
        if (after.get("currentness") or {}).get("state") != "PASS":
            failures.append(f"{service_id}: projected currentness is not PASS")
        if before_ready:
            failures.append(f"{service_id}: unexpected base ready units: {sorted(before_ready)}")
        if newly_ready != EXPECTED_SAFE_UNITS:
            failures.append(
                f"{service_id}: newly ready units mismatch: {sorted(newly_ready)}"
            )

        for axis in ("relation_verification", "human_review", "publication", "route_exposure"):
            if before.get(axis) != after.get(axis):
                failures.append(f"{service_id}: {axis} changed during currentness-only projection")

        newly_ready_units += len(newly_ready)
        impact.append(
            {
                "service_id": service_id,
                "currentness_before": (before.get("currentness") or {}).get("state"),
                "currentness_after": (after.get("currentness") or {}).get("state"),
                "newly_ready_publication_units": sorted(newly_ready),
            }
        )

    if newly_ready_units != 40:
        failures.append(f"expected 40 newly ready publication units, got {newly_ready_units}")

    report = {
        "result": "PASS" if not failures else "FAIL",
        "projection_only": True,
        "canonical_writeback": False,
        "new_currentness_pass_cells": len(TARGETS),
        "newly_ready_for_publication_review_units": newly_ready_units,
        "currentness_gaps_before": base_gaps,
        "currentness_gaps_projected": projected_gaps,
        "runtime_publication_changed": False,
        "route_exposure_changed": False,
        "impact": impact,
        "failures": failures,
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
