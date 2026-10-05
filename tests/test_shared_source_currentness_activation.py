import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "shared_source_currentness_projection",
    ROOT / "scripts" / "shared_source_currentness_projection.py",
)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)

class SharedSourceCurrentnessActivationTests(unittest.TestCase):
    def evaluate(self, **overrides):
        values = dict(
            existing_currentness="NOT_ESTABLISHED",
            source_class="CURRENT_OFFICIAL_VERSIONED",
            source_identity_complete=True,
            applicability_verified=True,
            scope_identified=True,
            source_version_contains_scope=True,
            ingestion_state="INGESTED",
            automatic_promotion_allowed=True,
        )
        values.update(overrides)
        return MODULE.evaluate_projection(**values)

    def test_complete_verified_chain_can_recommend_pass(self):
        result = self.evaluate()
        self.assertTrue(result["promotion_recommended"])
        self.assertEqual(result["projected_currentness"], "PASS")

    def test_missing_source_identity_never_promotes(self):
        result = self.evaluate(source_identity_complete=False)
        self.assertFalse(result["promotion_recommended"])
        self.assertEqual(result["projected_currentness"], "NOT_ESTABLISHED")

    def test_missing_applicability_never_promotes(self):
        self.assertFalse(self.evaluate(applicability_verified=False)["promotion_recommended"])

    def test_comparison_only_never_promotes(self):
        self.assertFalse(self.evaluate(source_class="COMPARISON_ONLY")["promotion_recommended"])

    def test_historical_only_never_promotes(self):
        self.assertFalse(self.evaluate(source_class="HISTORICAL_ONLY")["promotion_recommended"])

    def test_not_applicable_never_promotes(self):
        self.assertFalse(self.evaluate(ingestion_state="NOT_APPLICABLE")["promotion_recommended"])

    def test_explicit_gate_is_required(self):
        self.assertFalse(self.evaluate(automatic_promotion_allowed=False)["promotion_recommended"])

    def test_repository_projection_is_fail_closed(self):
        report = MODULE.build_projection()
        self.assertEqual(report["summary"]["cells_evaluated"], 39 * 7)
        self.assertEqual(report["summary"]["promotions_recommended"], 0)
        self.assertFalse(report["safety"]["writes_canonical_state"])
        self.assertFalse(report["safety"]["changes_human_review"])
        self.assertFalse(report["safety"]["changes_publication"])
        self.assertFalse(report["safety"]["changes_route_exposure"])

if __name__ == "__main__":
    unittest.main()
