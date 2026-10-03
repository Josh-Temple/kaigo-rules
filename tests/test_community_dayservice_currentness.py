import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR_PATH = ROOT / "scripts/validate_community_dayservice_currentness.py"

spec = importlib.util.spec_from_file_location(
    "validate_community_dayservice_currentness", VALIDATOR_PATH
)
validator = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(validator)


class CommunityDayserviceCurrentnessTest(unittest.TestCase):
    def test_fail_closed_currentness_contract(self):
        self.assertEqual(validator.validate(), [])

    def test_item_body_pass_does_not_promote_currentness(self):
        receipt = validator.load(validator.CURRENTNESS)
        self.assertEqual(receipt["item_body_precondition"]["counts"]["PASS"], 21)
        self.assertFalse(receipt["item_body_precondition"]["proves_currentness"])
        self.assertEqual(receipt["conclusion"]["currentness_state"], "NOT_ESTABLISHED")
        self.assertEqual(receipt["conclusion"]["decision"], "HOLD")
        self.assertFalse(receipt["conclusion"]["pass"])

    def test_r6_comparison_and_ordinance_are_not_integrated_notice_text(self):
        receipt = validator.load(validator.CURRENTNESS)
        sources = {row["id"]: row for row in receipt["official_sources"]}
        self.assertFalse(sources["mhlw-r6-final-comparison"]["current_integrated_text"])
        self.assertEqual(
            sources["mhlw-current-standard-ordinance"]["category"],
            "CURRENT_ORDINANCE_NOT_INTERPRETATION_NOTICE",
        )
        self.assertFalse(
            receipt["integrated_current_text"]["official_current_integrated_text_identified"]
        )

    def test_negative_search_cannot_close_post_r6_chain(self):
        receipt = validator.load(validator.CURRENTNESS)
        self.assertFalse(receipt["post_r6_discovery"]["negative_search_is_proof_of_no_change"])
        self.assertFalse(receipt["amendment_coverage"]["post_r6_amendment_chain_closed"])
        self.assertFalse(receipt["amendment_coverage"]["sufficiently_closed_amendment_chain"])


if __name__ == "__main__":
    unittest.main()
