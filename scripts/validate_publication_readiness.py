#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MATRIX_PATH = ROOT / "data/database-coverage-matrix.generated.json"
READINESS_PATH = ROOT / "data/publication-readiness.generated.json"

def load(path):
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)

def fail(message):
    raise SystemExit(message)

matrix = load(MATRIX_PATH)
readiness = load(READINESS_PATH)

policy = readiness.get("policy", {})
for key in (
    "publication_writeback_allowed",
    "route_auto_enable_allowed",
    "readiness_implies_publication",
    "ai_review_completion_allowed",
    "single_completion_percentage_allowed",
):
    if policy.get(key) is not False:
        fail(f"unsafe publication readiness policy: {key}")

matrix_cells = {}
for service in matrix["services"]:
    for cell in service["source_families"]:
        key = (service["service_id"], cell["source_family"])
        matrix_cells[key] = cell

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
    if cell is None:
        fail(f"unknown publication readiness cell: {key}")

    if row.get("publication_observation") != (cell.get("publication") or {}).get("state", "MISSING"):
        fail(f"publication observation drift: {key}")
    if row.get("route_exposure_observation") != (cell.get("route_exposure") or {}).get("state", "MISSING"):
        fail(f"route observation drift: {key}")

    state = row.get("readiness")
    blockers = row.get("blocking_reasons")
    if not isinstance(blockers, list):
        fail(f"blocking_reasons must be a list: {key}")
    if state == "READY_FOR_PUBLICATION_REVIEW" and blockers:
        fail(f"ready cell has blockers: {key}")
    if state == "NOT_APPLICABLE" and blockers:
        fail(f"not-applicable cell has blockers: {key}")
    if state not in {"READY_FOR_PUBLICATION_REVIEW", "NOT_APPLICABLE"} and not blockers:
        fail(f"blocked cell lacks blockers: {key}")
    if blockers and state != blockers[0]:
        fail(f"primary readiness must equal first blocker: {key}")

if seen != set(matrix_cells):
    fail("publication readiness coverage mismatch")

print(f"publication readiness validation: PASS ({len(rows)} cells)")
