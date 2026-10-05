import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR_PATH = ROOT / "scripts/validate_standards_interpretation_residual_assurance_readiness.py"
ARTIFACT_PATH = ROOT / "data/verification/standards-interpretation-item-body/residual-assurance-human-review-readiness-worker-a.json"

spec = importlib.util.spec_from_file_location(
    "validate_standards_interpretation_residual_assurance_readiness",
    VALIDATOR_PATH,
)
validator = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(validator)


class StandardsInterpretationResidualAssuranceReadinessTest(unittest.TestCase):
    def test_fail_closed_contract(self):
        self.assertEqual(validator.validate(), [])

    def test_all_26_services_remain_not_established(self):
        artifact = json.loads(ARTIFACT_PATH.read_text(encoding="utf-8"))
        self.assertEqual(len(artifact["inventory"]), 26)
        self.assertEqual(artifact["result"]["promoted_to_pass"], 0)
        self.assertTrue(
            all(
                row["item_body_state_after_worker_a"] == "NOT_ESTABLISHED"
                and row["axis_preservation"]["currentness"] == "NOT_ESTABLISHED"
                and row["axis_preservation"]["human_review"] == "NOT_REVIEWED"
                and row["axis_preservation"]["publication_promoted"] is False
                and row["axis_preservation"]["route_promoted"] is False
                for row in artifact["inventory"]
            )
        )

    def test_snapshot_fingerprints_are_reproducible(self):
        artifact = json.loads(ARTIFACT_PATH.read_text(encoding="utf-8"))
        checked = 0
        for row in artifact["inventory"]:
            for fp in row["pinned_versioned_source_body_evidence"]:
                checked += 1
                self.assertEqual(
                    validator.git_blob_sha(ROOT / fp["snapshot_path"]),
                    fp["git_blob_sha"],
                )
        self.assertGreater(checked, 0)

    def test_validator_cli_passes(self):
        result = subprocess.run(
            [sys.executable, str(VALIDATOR_PATH)],
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("26 services remain fail-closed", result.stdout)


if __name__ == "__main__":
    unittest.main()
