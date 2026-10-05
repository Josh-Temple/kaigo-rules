#!/usr/bin/env python3
from __future__ import annotations
import importlib.util
import json
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def load(path):
    return json.loads((ROOT/path).read_text(encoding="utf-8"))

def load_builder():
    path=ROOT/"scripts/build_database_coverage_matrix.py"
    spec=importlib.util.spec_from_file_location("coverage_builder",path)
    module=importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module

class RemunerationAssuranceProjectionTest(unittest.TestCase):
    def test_projection_is_fail_closed_and_axis_separated(self):
        builder=load_builder()
        projected=builder.build()
        committed=load("data/database-coverage-matrix.generated.json")
        assurance=load("data/shared/remuneration-notification/service-item-body-assurance.json")
        by_service={row["service_id"]:row for row in assurance["services"]}
        old_rows={row["service_id"]:row for row in committed["services"]}
        new_rows={row["service_id"]:row for row in projected["services"]}

        for service_id,row in new_rows.items():
            old_cell=next(c for c in old_rows[service_id]["source_families"] if c["source_family"]=="remuneration_notification")
            new_cell=next(c for c in row["source_families"] if c["source_family"]=="remuneration_notification")
            projection=by_service[service_id]
            for axis in ("currentness","human_review","publication","route_exposure","relation_verification"):
                self.assertEqual(old_cell[axis]["state"],new_cell[axis]["state"],f"{service_id}: {axis} changed")
            if projection.get("projection_applied_to_coverage_matrix") is True:
                self.assertEqual(projection["projection_state"],new_cell["item_body_verification"]["state"])
            else:
                self.assertEqual(old_cell["item_body_verification"]["state"],new_cell["item_body_verification"]["state"])

    def test_only_full_invariant_rows_can_pass(self):
        assurance=load("data/shared/remuneration-notification/service-item-body-assurance.json")
        invariant_keys=assurance["projection_invariant"]
        for row in assurance["services"]:
            if row["projection_state"]=="PASS":
                self.assertTrue(all((row.get("invariants") or {}).get(key) is True for key in invariant_keys))

if __name__=="__main__":
    unittest.main()
