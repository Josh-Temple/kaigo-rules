#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MATRIX_PATH = ROOT / "data/database-coverage-matrix.generated.json"
SCOPING_PATH = ROOT / "data/publication-requirement-scoping.json"
READINESS_PATH = ROOT / "data/publication-readiness.generated.json"

def load(path):
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)

def fail(message):
    raise SystemExit(message)

matrix = load(MATRIX_PATH)
scoping = load(SCOPING_PATH)
readiness = load(READINESS_PATH)

policy = readiness.get("policy", {})
for key in (
    "publication_writeback_allowed",
    "route_auto_enable_allowed",
    "readiness_implies_publication",
    "ai_review_completion_allowed",
    "single_completion_percentage_allowed",
    "not_required_means_canonical_pass",
):
    if policy.get(key) is not False:
        fail(f"unsafe publication readiness policy: {key}")
if policy.get("unit_requirement_scoping_required") is not True:
    fail("unit requirement scoping must remain required")

matrix_cells = {}
for service in matrix["services"]:
    for cell in service["source_families"]:
        matrix_cells[(service["service_id"], cell["source_family"])] = cell

scoped_cells = {
    (row["service_id"], row["source_family"]): row
    for row in scoping.get("cells", [])
}
if set(scoped_cells) != set(matrix_cells):
    fail("publication scoping coverage mismatch")

definitions = {
    row["unit_type"]: set(row.get("field_allowlist") or [])
    for row in scoping.get("publication_unit_definitions", [])
}

rows = readiness.get("cells")
if not isinstance(rows, list) or len(rows) != len(matrix_cells):
    fail("publication readiness cell count mismatch")

seen = set()
for row in rows:
    key = (row.get("service_id"), row.get("source_family"))
    if key in seen:
        fail(f"duplicate publication readiness cell: {key}")
    seen.add(key)
    cell = matrix_cells.get(key)
    scoped = scoped_cells.get(key)
    if cell is None or scoped is None:
        fail(f"unknown publication readiness cell: {key}")

    if row.get("publication_observation") != (cell.get("publication") or {}).get("state", "MISSING"):
        fail(f"publication observation drift: {key}")
    if row.get("route_exposure_observation") != (cell.get("route_exposure") or {}).get("state", "MISSING"):
        fail(f"route observation drift: {key}")

    ready_units_expected = [
        unit["unit_type"]
        for unit in scoped.get("publication_units", [])
        if unit.get("readiness") == "READY_FOR_PUBLICATION_REVIEW"
    ]
    if row.get("ready_publication_units") != ready_units_expected:
        fail(f"ready unit projection drift: {key}")

    expected_fields = sorted({
        field
        for unit_type in ready_units_expected
        for field in definitions.get(unit_type, set())
    })
    if row.get("publication_field_allowlist") != expected_fields:
        fail(f"publication field allowlist drift: {key}")

    state = row.get("readiness")
    blockers = row.get("blocking_reasons")
    if not isinstance(blockers, list):
        fail(f"blocking_reasons must be a list: {key}")
    if ready_units_expected:
        if state != "READY_FOR_PUBLICATION_REVIEW" or blockers:
            fail(f"ready publication unit not reflected at cell level: {key}")
    elif state == "READY_FOR_PUBLICATION_REVIEW":
        fail(f"cell ready without a ready publication unit: {key}")

    units = scoped.get("publication_units", [])
    if units and all(unit.get("readiness") == "NOT_APPLICABLE" for unit in units):
        if state != "NOT_APPLICABLE" or blockers:
            fail(f"not-applicable unit set projected incorrectly: {key}")

    if state not in {"READY_FOR_PUBLICATION_REVIEW", "NOT_APPLICABLE"} and not blockers:
        fail(f"blocked cell lacks blockers: {key}")
    if blockers and state != blockers[0]:
        fail(f"primary readiness must equal first blocker: {key}")

    # Requirement scoping may remove a publication blocker, but may never
    # rewrite the canonical relation or human-review state.
    axes = row.get("axis_states") or {}
    if axes.get("relation_verification") != (cell.get("relation_verification") or {}).get("state", "MISSING"):
        fail(f"canonical relation state drift: {key}")
    if axes.get("human_review") != (cell.get("human_review") or {}).get("state", "MISSING"):
        fail(f"canonical human-review state drift: {key}")

if seen != set(matrix_cells):
    fail("publication readiness coverage mismatch")

print(f"publication readiness validation: PASS ({len(rows)} cells)")
