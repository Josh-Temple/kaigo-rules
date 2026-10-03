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

    def test_public_denominator_enumerates_every_service_item_family(self):
        families = self.metrics[
            "public_items_with_complete_evidence_state"
        ]["denominator"]["included_public_families"]
        self.assertEqual(
            families,
            [
                "practical_questions",
                "care_insurance_act_articles",
                "ordinance_articles",
                "notice_items",
                "remuneration_items",
                "remuneration_delegated_criteria",
                "fee_guidance_items",
                "unit_price_records",
                "qa_corpus_items",
                "homevisit_notice_items",
                "homebath_notice_items",
                "dayrehab_standard_articles",
                "dayrehab_notice_items",
                "dayrehab_remuneration_items",
                "dayrehab_fee_guidance_items",
            ],
        )

    def test_shared_legal_scope_must_use_canonical_contract(self):
        metric = self.metrics["public_items_with_complete_evidence_state"]
        boundary = metric["denominator"]["service_boundary"]
        self.assertIn("lib/service-scope.ts", boundary)
        guards = " ".join(metric["guards"])
        self.assertIn("Article 8 paragraph membership", guards)

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
