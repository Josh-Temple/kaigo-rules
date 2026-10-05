import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR_PATH = ROOT / "scripts/validate_standards_interpretation_residual_item_body.py"
INVENTORY_PATH = ROOT / "data/verification/standards-interpretation-item-body/core-item-body-assurance-expansion-worker-a.json"

spec = importlib.util.spec_from_file_location("residual_item_body_validator", VALIDATOR_PATH)
validator = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(validator)


class StandardsInterpretationResidualItemBodyTest(unittest.TestCase):
    def test_validator_passes(self):
        self.assertEqual(validator.validate(), [])

    def test_all_residuals_remain_fail_closed(self):
        data = json.loads(INVENTORY_PATH.read_text(encoding="utf-8"))
        rows = data["inventory"]
        self.assertEqual(len(rows), 26)
        self.assertTrue(all(row["item_body_state"] == "NOT_ESTABLISHED" for row in rows))
        self.assertTrue(all(row["service_level_projection_eligible"] is False for row in rows))
        self.assertEqual(data["service_projection"]["projected_to_pass"], 0)

    def test_assurance_axes_are_not_promoted(self):
        data = json.loads(INVENTORY_PATH.read_text(encoding="utf-8"))
        for row in data["inventory"]:
            with self.subTest(service_id=row["service_id"]):
                self.assertEqual(row["safety"]["currentness"], "NOT_ESTABLISHED")
                self.assertEqual(row["safety"]["human_review"], "NOT_REVIEWED")
                self.assertFalse(row["safety"]["publication_promoted"])
                self.assertFalse(row["safety"]["route_promoted"])

    def test_pinned_snapshots_are_shared_not_service_copies(self):
        data = json.loads(INVENTORY_PATH.read_text(encoding="utf-8"))
        snapshots = {
            path
            for row in data["inventory"]
            for path in row["pinned_source_body_snapshots"]
        }
        self.assertTrue(snapshots)
        self.assertTrue(all(path.startswith("data/shared/standards-interpretation/source-snapshots/") for path in snapshots))


if __name__ == "__main__":
    unittest.main()
