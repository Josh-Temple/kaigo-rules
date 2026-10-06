from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "data/verification/final-standards-residual-relation-worker-c.json"
SCRIPT = ROOT / "scripts/validate_final_standards_residual_relation_worker_c.py"


class FinalStandardsResidualRelationWorkerCTest(unittest.TestCase):
    def test_validator_passes(self) -> None:
        result = subprocess.run(
            [sys.executable, str(SCRIPT)],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        self.assertIn("Governing Standards 39/39", result.stdout)
        self.assertIn("relations 130/188", result.stdout)

    def test_human_review_stays_unresolved(self) -> None:
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        lanes = payload["residual_relations"]["audited_priority_lanes"]
        self.assertEqual(lanes["human_semantic_review"]["candidates"], 36)
        self.assertEqual(lanes["human_semantic_review"]["promoted"], 0)
        self.assertEqual(lanes["cross_layer_human_review"]["promoted"], 0)

    def test_final_two_are_bounded_passes(self) -> None:
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        decisions = payload["governing_standards"]["decisions"]
        self.assertEqual({row["service_id"] for row in decisions}, {"night-homevisit", "dementia-group-home"})
        self.assertTrue(all(row["decision"] == "PROMOTE_PASS_BOUNDED" for row in decisions))
        self.assertTrue(all(row["promotion_applied"] is True for row in decisions))


if __name__ == "__main__":
    unittest.main()
