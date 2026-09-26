import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "data" / "product-value-metrics-v0.1.json"


class ProductValueMetricSpecTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.payload = json.loads(SPEC.read_text(encoding="utf-8"))
        cls.metrics = {row["id"]: row for row in cls.payload["metrics"]}

    def test_exact_metric_set(self):
        self.assertEqual(
            set(self.metrics),
            {
                "practical_questions_with_evidence_path",
                "public_items_with_complete_evidence_state",
                "unresolved_or_unverified_relations",
            },
        )

    def test_metrics_define_denominator_numerator_and_report_fields(self):
        for metric in self.metrics.values():
            self.assertIn("denominator", metric)
            self.assertIn("numerator", metric)
            self.assertTrue(metric["report_fields"])
            self.assertTrue(metric["guards"])

    def test_question_metric_does_not_equate_verified_with_evidence(self):
        guards = " ".join(
            self.metrics["practical_questions_with_evidence_path"]["guards"]
        )
        self.assertIn("status=verified alone does not satisfy", guards)

    def test_public_completeness_keeps_verification_dimensions_explicit(self):
        metric = self.metrics["public_items_with_complete_evidence_state"]
        criterion = metric["numerator"]["criterion"]
        self.assertIn("source_complete", criterion)
        self.assertIn("scope_complete", criterion)
        self.assertIn("verification_state_complete", criterion)
        guards = " ".join(metric["guards"])
        self.assertIn("PASS is not required", guards)
        self.assertIn("service scope must not be inferred", guards)

    def test_relation_metric_uses_registry_remaining_count(self):
        metric = self.metrics["unresolved_or_unverified_relations"]
        self.assertEqual(
            metric["denominator"]["field"],
            "relation_verification.inventory_relations",
        )
        self.assertEqual(
            metric["numerator"]["field"],
            "relation_verification.remaining_unverified_relations",
        )
        guards = " ".join(metric["guards"])
        self.assertIn("does not mean known-wrong", guards)
        self.assertIn("automatic promotion to verified is forbidden", guards)


if __name__ == "__main__":
    unittest.main()
