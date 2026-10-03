from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "scripts/verify_regular_round_standards_interpretation_item_body.py"


class RegularRoundItemBodyVerificationTest(unittest.TestCase):
    def test_receipt_validator_passes(self) -> None:
        result = subprocess.run(
            [sys.executable, str(VALIDATOR)],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(
            result.returncode,
            0,
            msg=f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}",
        )
        self.assertIn('"validation_result": "PASS"', result.stdout)
        self.assertIn('"PASS": 21', result.stdout)


if __name__ == "__main__":
    unittest.main()
