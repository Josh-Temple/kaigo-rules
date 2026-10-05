import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "publication_readiness_builder",
    ROOT / "scripts/build_publication_readiness.py",
)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)

class PublicationReadinessTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.matrix = json.loads((ROOT / "data/database-coverage-matrix.generated.json").read_text(encoding="utf-8"))
        cls.artifact = MODULE.build_artifact()

    def test_covers_every_service_family_cell_once(self):
        expected = sum(len(service["source_families"]) for service in self.matrix["services"])
        self.assertEqual(expected, 351)
        self.assertEqual(len(self.artifact["cells"]), expected)
        keys = {(row["service_id"], row["source_family"]) for row in self.artifact["cells"]}
        self.assertEqual(len(keys), expected)

    def test_no_readiness_can_enable_publication_or_routes(self):
        policy = self.artifact["policy"]
        self.assertFalse(policy["publication_writeback_allowed"])
        self.assertFalse(policy["route_auto_enable_allowed"])
        self.assertFalse(policy["readiness_implies_publication"])

    def test_unresolved_currentness_never_becomes_ready(self):
        for row in self.artifact["cells"]:
            if row["axis_states"]["currentness"] not in MODULE.CURRENTNESS_PASS and row["readiness"] != "NOT_APPLICABLE":
                self.assertIn("BLOCKED_CURRENTNESS", row["blocking_reasons"])
                self.assertNotEqual(row["readiness"], "READY_FOR_PUBLICATION_REVIEW")

    def test_human_review_is_a_separate_blocker(self):
        for row in self.artifact["cells"]:
            if row["axis_states"]["human_review"] == "NOT_REVIEWED" and row["readiness"] != "NOT_APPLICABLE":
                self.assertIn("BLOCKED_HUMAN_REVIEW", row["blocking_reasons"])

    def test_not_applicable_prevents_false_blocker_promotion(self):
        for row in self.artifact["cells"]:
            if row["readiness"] == "NOT_APPLICABLE":
                self.assertEqual(row["blocking_reasons"], [])

if __name__ == "__main__":
    unittest.main()
