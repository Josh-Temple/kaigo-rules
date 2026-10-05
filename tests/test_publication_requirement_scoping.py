from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / "scripts/build_publication_requirement_scoping.py"
ARTIFACT = ROOT / "data/publication-requirement-scoping.json"

spec = importlib.util.spec_from_file_location("publication_requirement_scoping", BUILDER)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(module)


class PublicationRequirementScopingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        cls.definitions = {
            row["unit_type"]: row
            for row in cls.artifact["publication_unit_definitions"]
        }

    def complete_axes(self, **overrides):
        axes = {
            "corpus_availability": "AVAILABLE",
            "service_scope": "SCOPE_DEFINED",
            "ingestion": "INGESTED",
            "item_body_verification": "PASS",
            "currentness": "PASS",
            "relation_verification": "NOT_ESTABLISHED",
            "human_review": "NOT_REVIEWED",
            "publication": "BLOCKED",
            "route_exposure": "BLOCKED",
        }
        axes.update(overrides)
        return axes

    def evaluate(self, unit_type, **axis_overrides):
        return module.evaluate_publication_unit(
            self.complete_axes(**axis_overrides),
            self.definitions[unit_type],
        )

    def test_committed_artifact_matches_builder(self):
        self.assertEqual(self.artifact, module.build_artifact())
        self.assertEqual(self.artifact["summary"]["service_source_family_cells"], 351)
        self.assertEqual(self.artifact["summary"]["publication_units_total"], 2457)

    def test_not_reviewed_is_not_converted_to_reviewed_when_review_not_required(self):
        result = self.evaluate("SOURCE_METADATA_LOCATOR", human_review="NOT_REVIEWED")
        self.assertEqual(result["canonical_human_review_state_observed"], "NOT_REVIEWED")
        self.assertEqual(result["human_review_requirement"], "NOT_REQUIRED")
        self.assertNotIn("BLOCKED_HUMAN_REVIEW", result["blocking_reasons"])
        self.assertEqual(result["readiness"], "READY_FOR_PUBLICATION_REVIEW")

    def test_relation_not_required_does_not_convert_relation_to_pass(self):
        result = self.evaluate("SOURCE_TEXT_ITEM_BODY", relation_verification="NOT_ESTABLISHED")
        self.assertEqual(result["canonical_relation_state_observed"], "NOT_ESTABLISHED")
        self.assertEqual(result["relation_requirement"], "NOT_REQUIRED")
        self.assertNotIn("BLOCKED_RELATION", result["blocking_reasons"])
        self.assertEqual(result["readiness"], "READY_FOR_PUBLICATION_REVIEW")

    def test_relation_assertion_requires_relation_verification(self):
        result = self.evaluate("CROSS_LAYER_RELATION_LINK", relation_verification="NOT_ESTABLISHED")
        self.assertEqual(result["relation_requirement"], "REQUIRED")
        self.assertIn("BLOCKED_RELATION", result["blocking_reasons"])
        self.assertNotEqual(result["readiness"], "READY_FOR_PUBLICATION_REVIEW")

    def test_review_dependent_explanation_requires_human_review(self):
        result = self.evaluate("REVIEW_DEPENDENT_EXPLANATORY_TEXT", human_review="NOT_REVIEWED")
        self.assertEqual(result["human_review_requirement"], "REQUIRED")
        self.assertIn("BLOCKED_HUMAN_REVIEW", result["blocking_reasons"])
        self.assertNotEqual(result["readiness"], "READY_FOR_PUBLICATION_REVIEW")

    def test_interpretive_relation_requires_both_relation_and_human_review(self):
        result = self.evaluate(
            "INTERPRETIVE_RELATION_EXPLANATION",
            relation_verification="NOT_ESTABLISHED",
            human_review="NOT_REVIEWED",
        )
        self.assertIn("BLOCKED_RELATION", result["blocking_reasons"])
        self.assertIn("BLOCKED_HUMAN_REVIEW", result["blocking_reasons"])

    def test_unresolved_currentness_blocks_even_safe_metadata_unit(self):
        result = self.evaluate("SOURCE_METADATA_LOCATOR", currentness="PARTIAL")
        self.assertIn("BLOCKED_CURRENTNESS", result["blocking_reasons"])
        self.assertNotEqual(result["readiness"], "READY_FOR_PUBLICATION_REVIEW")

    def test_safe_field_allowlists_exclude_relation_and_review_fields(self):
        relation_fields = {"relation_identity", "relation_label", "target_url", "target_locator"}
        review_fields = {"reviewed_explanatory_text", "review_decision_reference"}
        for definition in self.artifact["publication_unit_definitions"]:
            fields = set(definition["field_allowlist"])
            if definition["relation_requirement"] == "NOT_REQUIRED":
                self.assertFalse(fields & relation_fields, definition["unit_type"])
            if definition["human_review_requirement"] == "NOT_REQUIRED":
                self.assertFalse(fields & review_fields, definition["unit_type"])
            self.assertTrue(fields <= module.ALL_PUBLICATION_FIELDS)

    def test_current_main_has_no_ready_candidate_for_explainable_reason(self):
        summary = self.artifact["summary"]
        self.assertEqual(summary["ready_for_publication_review_candidates"], 0)
        self.assertGreater(summary["blocking_reason_counts"].get("BLOCKED_CURRENTNESS", 0), 0)

    def test_projection_cannot_publish_or_enable_routes(self):
        policy = self.artifact["policy"]
        self.assertFalse(policy["publication_writeback_allowed"])
        self.assertFalse(policy["route_auto_enable_allowed"])
        self.assertFalse(policy["canonical_relation_writeback_allowed"])
        self.assertFalse(policy["canonical_human_review_writeback_allowed"])


if __name__ == "__main__":
    unittest.main()
