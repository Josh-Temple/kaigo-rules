from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "scripts/validate_preventive_support_standards_interpretation_currentness.py"
RECEIPT = ROOT / "data/verification/standards-interpretation-currentness/preventive-support.json"


class PreventiveSupportStandardsInterpretationCurrentnessTest(unittest.TestCase):
    def test_fail_closed_validator_passes(self) -> None:
        result = subprocess.run(
            [sys.executable, str(VALIDATOR)],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("NOT_ESTABLISHED", result.stdout)
        self.assertIn("fail-closed", result.stdout)

    def test_receipt_keeps_gates_separate(self) -> None:
        data = json.loads(RECEIPT.read_text(encoding="utf-8"))
        self.assertEqual(data["audit_result"], "NOT_ESTABLISHED")
        self.assertFalse(data["conclusion"]["currentness_pass"])
        self.assertFalse(data["source_version_assessment"]["amendment_chain_closed"])
        self.assertFalse(
            data["source_version_assessment"]["current_integrated_official_interpretation_notice"]["found"]
        )
        safety = data["safety"]
        self.assertTrue(safety["currentness_only"])
        self.assertFalse(safety["currentness_promoted"])
        self.assertFalse(safety["human_review_promoted"])
        self.assertFalse(safety["publication_permitted"])
        self.assertFalse(safety["route_enabled"])
        self.assertFalse(safety["negative_search_treated_as_no_amendment_proof"])


if __name__ == "__main__":
    unittest.main()
