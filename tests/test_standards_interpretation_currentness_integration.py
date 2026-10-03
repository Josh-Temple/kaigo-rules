import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "scripts/validate_standards_interpretation_currentness.py"

spec = importlib.util.spec_from_file_location(
    "validate_standards_interpretation_currentness", VALIDATOR
)
validator = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(validator)


class StandardsInterpretationCurrentnessIntegrationTest(unittest.TestCase):
    def setUp(self):
        self.state = validator.load(validator.STATE)
        self.rows = {row["service_id"]: row for row in self.state["services"]}

    def test_common_gate_contract(self):
        self.assertEqual(validator.validate(), [])

    def test_currentness_verification_is_distinct_from_currentness_state(self):
        for service_id in (
            "community-dayservice",
            "regular-round",
            "night-homevisit",
            "care-management",
            "preventive-support",
        ):
            self.assertTrue(self.rows[service_id]["currentness"]["verification_performed"])
            self.assertIsNotNone(self.rows[service_id]["currentness"]["receipt"])
            self.assertEqual(self.rows[service_id]["currentness"]["state"], "NOT_ESTABLISHED")

    def test_downstream_gates_are_not_promoted(self):
        for row in self.state["services"]:
            self.assertEqual(row["human_review"]["state"], "NOT_REVIEWED")
            self.assertFalse(row["publication"]["allowed"])
            self.assertFalse(row["route"]["enabled"])

    def test_preventive_support_package_blocker_remains(self):
        row = self.rows["preventive-support"]
        self.assertEqual(row["item_body"]["counts"]["PARTIAL"], 1)
        self.assertEqual(row["package"]["blocker_state"], "BLOCKED_KR2-10-E006")
        self.assertEqual(row["package"]["blocker_task_id"], "KR2-10-E006")


if __name__ == "__main__":
    unittest.main()
