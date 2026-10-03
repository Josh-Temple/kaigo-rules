from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RECEIPT = (
    ROOT
    / "data/verification/standards-interpretation-currentness/night-homevisit.json"
)


class NightHomevisitStandardsInterpretationCurrentnessTest(unittest.TestCase):
    def test_dedicated_validator_passes(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                str(
                    ROOT
                    / "scripts/validate_night_homevisit_standards_interpretation_currentness.py"
                ),
            ],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("NOT_ESTABLISHED", result.stdout)
        self.assertIn("25/25", result.stdout)

    def test_receipt_is_fail_closed_and_currentness_only(self) -> None:
        data = json.loads(RECEIPT.read_text(encoding="utf-8"))

        self.assertEqual(data["audit_result"], "NOT_ESTABLISHED")
        self.assertEqual(data["effect"], "KEEP_HOLD")
        self.assertFalse(data["current_integrated_official_text"]["available"])
        self.assertFalse(data["amendment_coverage"]["sufficiently_closed_chain"])

        by_id = {row["id"]: row for row in data["versions_checked"]}
        self.assertEqual(
            by_id["r3-amendment-comparison"]["classification"],
            "R3_AMENDMENT_COMPARISON_NOT_INTEGRATED",
        )
        self.assertEqual(
            by_id["r6-final-comparison"]["classification"],
            "R6_FINAL_AMENDMENT_COMPARISON_NOT_INTEGRATED",
        )
        self.assertEqual(
            by_id["underlying-current-ordinance"]["classification"],
            "UNDERLYING_STANDARD_ORDINANCE_NOT_NOTICE",
        )

        safety = data["safety_boundary"]
        self.assertTrue(safety["currentness_only"])
        self.assertFalse(safety["item_body_status_changed"])
        self.assertFalse(safety["human_review_promoted"])
        self.assertFalse(safety["publication_promoted"])
        self.assertFalse(safety["public_route_promoted"])
        self.assertFalse(safety["automatic_promotion_allowed"])


if __name__ == "__main__":
    unittest.main()
