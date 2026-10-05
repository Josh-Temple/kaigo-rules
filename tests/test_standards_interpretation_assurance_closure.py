import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR_PATH = ROOT / "scripts/validate_standards_interpretation_assurance_closure.py"
INVENTORY_PATH = (
    ROOT
    / "data/verification/standards-interpretation-item-body/assurance-closure-wave.json"
)

spec = importlib.util.spec_from_file_location(
    "validate_standards_interpretation_assurance_closure", VALIDATOR_PATH
)
validator = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(validator)


class StandardsInterpretationAssuranceClosureTest(unittest.TestCase):
    def test_inventory_contract_is_fail_closed(self):
        self.assertEqual(validator.validate(), [])

    def test_inventory_is_exactly_26_unresolved_plus_one_closed_partial(self):
        inventory = json.loads(INVENTORY_PATH.read_text(encoding="utf-8"))
        self.assertEqual(
            {row["service_id"] for row in inventory["unresolved"]},
            validator.EXPECTED_UNRESOLVED,
        )
        self.assertEqual(len(inventory["unresolved"]), 26)
        self.assertEqual(
            [row["service_id"] for row in inventory["resolved"]],
            ["preventive-support"],
        )
        self.assertEqual(
            inventory["after_worker_c"]["service_level_item_body"],
            {"PASS": 13, "PARTIAL": 0, "NOT_ESTABLISHED": 26},
        )

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
