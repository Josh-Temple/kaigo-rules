#!/usr/bin/env python3
"""Validate the integrated public-value currentness expansion after Worker E writeback."""
from __future__ import annotations
import json
from pathlib import Path
import build_publication_requirement_scoping as publication

ROOT = Path(__file__).resolve().parents[1]
MATRIX = ROOT / "data/database-coverage-matrix.generated.json"
READINESS = ROOT / "data/publication-readiness.generated.json"
CANONICAL = ROOT / "data/verification/bounded-currentness-closure-worker-b.json"
TARGETS = {
    "preventive-homebath","preventive-homenursing","preventive-homerehab",
    "preventive-homecaremanagement","preventive-dayrehab","preventive-shortstay-life",
    "preventive-shortstay-medical","preventive-specific-facility",
    "preventive-welfare-equipment-rental","specific-preventive-welfare-equipment-sale",
}
FAMILY = "governing_standards_ordinance"
EXPECTED_UNITS = {
    "SOURCE_TEXT_ITEM_BODY","SOURCE_METADATA_LOCATOR",
    "CURRENTNESS_STATEMENT","SERVICE_APPLICABILITY_STATEMENT",
}

def load(path):
    return json.loads(path.read_text(encoding="utf-8"))

def main() -> int:
    matrix, readiness, canonical = load(MATRIX), load(READINESS), load(CANONICAL)
    failures = []
    cells = {(s["service_id"], c["source_family"]): c for s in matrix["services"] for c in s["source_families"]}
    ready = {(r["service_id"], r["source_family"]): r for r in readiness["cells"]}
    coverage = matrix["summary"]["source_family_coverage"][FAMILY]["currentness"]
    if coverage != {"NOT_ESTABLISHED": 17, "PARTIAL": 2, "PASS": 20}:
        failures.append(f"governing-standards currentness mismatch: {coverage}")
    if len(matrix["summary"]["currentness_gaps"]) != 323:
        failures.append(f"expected 323 currentness gaps, got {len(matrix['summary']['currentness_gaps'])}")
    new_ids = set(canonical["priority_1"][FAMILY]["newly_promoted_service_ids"])
    if new_ids != TARGETS:
        failures.append(f"canonical promoted target mismatch: {sorted(new_ids)}")
    for sid in sorted(TARGETS):
        cell = cells[(sid, FAMILY)]
        if (cell.get("currentness") or {}).get("state") != "PASS":
            failures.append(f"{sid}: integrated currentness is not PASS")
        row = ready[(sid, FAMILY)]
        if row.get("readiness") != "READY_FOR_PUBLICATION_REVIEW":
            failures.append(f"{sid}: integrated readiness is {row.get('readiness')}")
        if set(row.get("ready_publication_units") or []) != EXPECTED_UNITS:
            failures.append(f"{sid}: ready units mismatch")
    print(json.dumps({"result":"PASS" if not failures else "FAIL","integrated":True,"new_currentness_pass_cells":10,"expected_ready_units":40,"failures":failures},ensure_ascii=False,indent=2))
    return 0 if not failures else 1

if __name__ == "__main__":
    raise SystemExit(main())
