import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR_PATH = ROOT / "scripts/validate_standards_interpretation_item_body.py"

spec = importlib.util.spec_from_file_location(
    "validate_standards_interpretation_item_body", VALIDATOR_PATH
)
validator = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(validator)


class StandardsInterpretationItemBodyIntegrationTest(unittest.TestCase):
    def test_all_five_common_contracts_validate(self):
        for service_id in validator.SERVICES:
            with self.subTest(service_id=service_id):
                self.assertEqual(validator.validate_service(service_id), [])

    def test_aggregate_bounded_results(self):
        totals = {"PASS": 0, "PARTIAL": 0, "GAP": 0, "FAIL": 0}
        for service_id in validator.SERVICES:
            receipt = json.loads(
                (
                    ROOT
                    / "data/verification/standards-interpretation-item-body"
                    / f"{service_id}.json"
                ).read_text(encoding="utf-8")
            )
            counts = receipt["integration_summary"]["counts"]
            for key in totals:
                totals[key] += counts[key]
        self.assertEqual(totals, {"PASS": 115, "PARTIAL": 14, "GAP": 4, "FAIL": 0})

    def test_preventive_support_package_blocker_is_separate(self):
        receipt = json.loads(
            (
                ROOT
                / "data/verification/standards-interpretation-item-body/preventive-support.json"
            ).read_text(encoding="utf-8")
        )
        staging = json.loads(
            (
                ROOT
                / "data/services/preventive-support/standards-interpretation-staging.json"
            ).read_text(encoding="utf-8")
        )
        self.assertEqual(
            receipt["integration_summary"]["package_blocker_state"],
            "BLOCKED_KR2-10-E006",
        )
        self.assertEqual(
            staging["service_package_state"],
            "SEPARATE_PRECHECK_BLOCKER_PRESERVED",
        )


if __name__ == "__main__":
    unittest.main()
