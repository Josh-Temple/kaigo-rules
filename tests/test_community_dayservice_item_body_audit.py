import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR_PATH = ROOT / "scripts/validate_community_dayservice_item_body_audit.py"

spec = importlib.util.spec_from_file_location(
    "validate_community_dayservice_item_body_audit", VALIDATOR_PATH
)
validator = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(validator)


class CommunityDayserviceItemBodyAuditTest(unittest.TestCase):
    def test_item_body_audit_contract(self):
        self.assertEqual(validator.validate(), [])

    def test_statuses_are_content_only_not_currentness(self):
        audit = validator.load(validator.AUDIT)
        self.assertEqual(
            audit["counts"],
            {"PASS": 21, "PARTIAL": 0, "GAP": 0, "FAIL": 0},
        )
        self.assertFalse(audit["safety"]["currentness_promoted"])
        self.assertFalse(audit["safety"]["omitted_text_reconstructed"])
        self.assertFalse(audit["safety"]["integrated_current_text_claimed"])

    def test_stale_local_source_is_non_blocking(self):
        audit = validator.load(validator.AUDIT)
        sources = {row["id"]: row for row in audit["sources"]}
        local = sources["yokohama-local-crosscheck"]
        self.assertEqual(local["authority"], "OFFICIAL_LOCAL_SUPPLEMENTAL")
        self.assertEqual(local["availability_state"], "STALE_URL_404_2026-10-03")
        self.assertFalse(local["required_for_item_body_verification"])


if __name__ == "__main__":
    unittest.main()
