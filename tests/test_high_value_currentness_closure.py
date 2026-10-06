import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class HighValueCurrentnessClosureTest(unittest.TestCase):
    def test_validator_passes(self):
        result = subprocess.run(
            [sys.executable, "scripts/validate_high_value_currentness_closure.py"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_exact_identity_and_fail_closed_holds(self):
        artifact = json.loads(
            (ROOT / "data/verification/high-value-currentness-closure-worker-b.json").read_text(
                encoding="utf-8"
            )
        )
        promotions = artifact["promotions"]
        self.assertEqual(len(promotions), 1)
        self.assertEqual(
            (
                promotions[0]["service_id"],
                promotions[0]["source_family"],
            ),
            ("dayservice", "unit_price_regional_classification"),
        )
        selections = {row["source_family"]: row for row in artifact["target_selection"]}
        self.assertEqual(selections["national_qa"]["disposition"], "HOLD")
        self.assertEqual(
            selections["delegated_remuneration_criteria"]["disposition"], "HOLD"
        )
        self.assertFalse(artifact["policy"]["blanket_family_promotion_allowed"])
        self.assertFalse(artifact["policy"]["human_review_promoted"])
        self.assertFalse(artifact["policy"]["relation_status_promoted"])


if __name__ == "__main__":
    unittest.main()
