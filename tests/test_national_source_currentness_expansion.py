import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "national_currentness_projection",
    ROOT / "scripts" / "national_source_currentness_projection.py",
)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


class NationalSourceCurrentnessExpansionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ledger = MODULE.load(MODULE.LEDGER_PATH)
        cls.report = MODULE.build_projection_report()

    def test_read_only_projection_recommends_no_unsupported_promotion(self):
        self.assertEqual(self.report["summary"]["promotions_recommended"], 0)
        for row in self.report["rows"]:
            self.assertEqual(row["projected_currentness"], row["existing_currentness"])
            self.assertFalse(row["promotion_recommended"])

    def test_item_body_pass_does_not_establish_currentness(self):
        delegated = [
            row for row in self.report["rows"]
            if row["source_family"] == "delegated_remuneration_criteria"
            and row["item_body_state"] == "PASS"
        ]
        self.assertGreater(len(delegated), 0)
        for row in delegated:
            self.assertFalse(row["promotion_recommended"])
            self.assertNotEqual(row["projected_currentness"], "PASS")

    def test_fee_guidance_comparison_is_not_integrated_current_body(self):
        fee = self.ledger["source_families"]["fee_calculation_guidance"]
        self.assertEqual(fee["source_level_verdict"], "NOT_ESTABLISHED")
        self.assertFalse(fee["integrated_current_body_established"])
        self.assertFalse(fee["service_projection_allowed"])

    def test_qa_compilation_freshness_does_not_promote_individual_items(self):
        qa = self.ledger["source_families"]["national_qa"]
        self.assertEqual(qa["source_level_verdict"], "CURRENT_COMPILATION_ONLY")
        self.assertEqual(
            qa["individual_item_currentness"],
            "NOT_ESTABLISHED_BY_COMPILATION_FRESHNESS",
        )
        qa_rows = [
            row for row in self.report["rows"] if row["source_family"] == "national_qa"
        ]
        self.assertEqual(len(qa_rows), 39)
        self.assertTrue(all(not row["promotion_recommended"] for row in qa_rows))

    def test_parallel_worker_evidence_stays_noncanonical_for_currentness(self):
        for family in (
            "unit_price_regional_classification",
            "other_national_manuals_forms",
        ):
            source = self.ledger["source_families"][family]
            self.assertTrue(source["parallel_worker_candidate_only"])
            self.assertEqual(source["source_level_verdict"], "NOT_ESTABLISHED")
            self.assertFalse(source["service_projection_allowed"])

    def test_assurance_axes_remain_separate(self):
        safety = self.ledger["safety"]
        self.assertFalse(safety["canonical_currentness_states_mutated"])
        self.assertFalse(safety["item_body_promoted"])
        self.assertFalse(safety["relation_verification_promoted"])
        self.assertFalse(safety["human_review_promoted"])
        self.assertFalse(safety["publication_promoted"])
        self.assertFalse(safety["route_exposure_promoted"])


if __name__ == "__main__":
    unittest.main()
