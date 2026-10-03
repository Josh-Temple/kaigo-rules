from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "scripts/validate_regular_round_standards_interpretation_currentness.py"
RECEIPT = ROOT / "data/verification/standards-interpretation-currentness/regular-round.json"


class RegularRoundCurrentnessVerificationTest(unittest.TestCase):
    def test_fail_closed_receipt_validator_passes(self) -> None:
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
        self.assertIn('"receipt_result": "NOT_ESTABLISHED"', result.stdout)
        self.assertIn('"amendment_chain_closed": false', result.stdout)
        self.assertIn('"current_integrated_text_found": false', result.stdout)

    def test_receipt_keeps_currentness_separate_from_item_body(self) -> None:
        receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))
        self.assertEqual(receipt["audit_result"], "NOT_ESTABLISHED")
        self.assertFalse(receipt["conclusion"]["currentness_pass"])
        self.assertEqual(
            receipt["conclusion"]["item_body_result_unchanged"],
            "PASS_CONTENT_EVIDENCE_MATCH_ONLY",
        )
        self.assertFalse(
            receipt["official_sources"][
                next(
                    index
                    for index, source in enumerate(receipt["official_sources"])
                    if source["id"] == "current-standards-ordinance-html"
                )
            ]["counts_as_current_integrated_text"]
        )


if __name__ == "__main__":
    unittest.main()
