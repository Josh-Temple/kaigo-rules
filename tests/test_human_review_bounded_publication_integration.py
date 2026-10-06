import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

class HumanReviewBoundedPublicationIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.matrix = load("data/database-coverage-matrix.generated.json")
        cls.bounded = load("data/verification/bounded-currentness-closure-worker-b.json")
        cls.high_value = load("data/verification/high-value-currentness-closure-worker-b.json")
        cls.scoping = load("data/publication-requirement-scoping.json")
        cls.readiness = load("data/publication-readiness.generated.json")
        cls.allowlist = load("data/bounded-publication-allowlist.json")

    def test_structural_coverage_does_not_regress(self):
        cells = [
            cell
            for service in self.matrix["services"]
            for cell in service["source_families"]
        ]
        self.assertEqual(len(self.matrix["services"]), 39)
        self.assertEqual(len(self.matrix["source_families"]), 9)
        self.assertEqual(len(cells), 351)
        self.assertEqual(sum(c["corpus_availability"]["state"] == "AVAILABLE" for c in cells), 351)
        self.assertEqual(sum(c["service_scope"]["state"] == "SCOPE_DEFINED" for c in cells), 351)

    def test_exact_bounded_currentness_promotions_are_projected(self):
        expected = {
            (row["service_id"], row["source_family"])
            for row in self.bounded["promotions"]
            if row.get("promotion_applied") is True
        }
        self.assertEqual(len(expected), 20)
        actual = set()
        for service in self.matrix["services"]:
            for cell in service["source_families"]:
                if (
                    cell["source_family"] == "governing_standards_ordinance"
                    and cell["currentness"]["state"] == "PASS"
                ):
                    actual.add((service["service_id"], cell["source_family"]))
        self.assertEqual(actual, expected)

    def test_ready_candidates_are_only_canonical_bounded_currentness_cells(self):
        expected = {
            (row["service_id"], row["source_family"])
            for artifact in (self.bounded, self.high_value)
            for row in artifact["promotions"]
            if row.get("promotion_applied") is True
        }
        ready = {
            (row["service_id"], row["source_family"])
            for row in self.readiness["cells"]
            if row["readiness"] == "READY_FOR_PUBLICATION_REVIEW"
        }
        self.assertEqual(ready, expected)

    def test_safe_units_do_not_promote_relation_or_human_review(self):
        for row in self.readiness["cells"]:
            if row["readiness"] != "READY_FOR_PUBLICATION_REVIEW":
                continue
            self.assertIn("SOURCE_METADATA_LOCATOR", row["ready_publication_units"])
            self.assertIn("CURRENTNESS_STATEMENT", row["ready_publication_units"])
            self.assertIn("SERVICE_APPLICABILITY_STATEMENT", row["ready_publication_units"])
            self.assertNotIn("CROSS_LAYER_RELATION_LINK", row["ready_publication_units"])
            self.assertNotIn("INTERPRETIVE_RELATION_EXPLANATION", row["ready_publication_units"])
            self.assertNotIn("REVIEW_DEPENDENT_EXPLANATORY_TEXT", row["ready_publication_units"])
            self.assertNotIn(row["axis_states"]["relation_verification"], {"PASS", "VERIFIED"})
            self.assertNotIn(row["axis_states"]["human_review"], {"PASS", "REVIEWED"})

    def test_runtime_binding_publishes_only_runtime_supported_ready_cells(self):
        ready = {
            (row["service_id"], row["source_family"])
            for row in self.readiness["cells"]
            if row["readiness"] == "READY_FOR_PUBLICATION_REVIEW"
        }
        supported_contracts = {
            "ordinance37": (
                "PASS_DIRECT_SERVICE_CHAPTER",
                "direct_service_chapter_verified",
            ),
            "preventive-services-standards": (
                "PASS_DIRECT_SERVICE_SCOPE",
                "direct_service_scope_verified",
            ),
        }
        runtime_supported = set()
        for row in self.bounded["promotions"]:
            source_id = (row.get("source_identity") or {}).get("canonical_source_id")
            contract = supported_contracts.get(source_id)
            proof = row.get("applicability_proof") or {}
            if (
                row.get("promotion_applied") is True
                and contract is not None
                and proof.get("state") == contract[0]
                and proof.get(contract[1]) is True
                and proof.get("discrepancies") == 0
            ):
                runtime_supported.add((row["service_id"], row["source_family"]))
        published = {
            (row["service_id"], row["source_family"])
            for row in self.allowlist["publication_cell_allowlist"]
        }
        routed = {
            (row["service_id"], row["source_family"])
            for row in self.allowlist["route_allowlist"]
        }

        expected_ready = {
            (row["service_id"], row["source_family"])
            for artifact in (self.bounded, self.high_value)
            for row in artifact["promotions"]
            if row.get("promotion_applied") is True
        }
        self.assertEqual(ready, expected_ready)
        self.assertEqual(len(ready), 21)
        self.assertEqual(len(runtime_supported), 20)
        self.assertTrue(runtime_supported.issubset(ready))
        self.assertEqual(published, runtime_supported)
        self.assertEqual(routed, runtime_supported)
        self.assertIn(("dayservice", "unit_price_regional_classification"), ready)
        self.assertNotIn(("dayservice", "unit_price_regional_classification"), published)
        self.assertEqual(len(self.allowlist["field_allowlist_by_cell"]), len(runtime_supported))
        self.assertTrue(self.allowlist["runtime_binding"]["established"])
        self.assertEqual(
            self.allowlist["runtime_binding"]["policy_module"],
            "lib/publication-policy.ts",
        )
        self.assertEqual(
            self.allowlist["summary"]["decision"],
            "PUBLISH_BOUNDED_READY_UNITS",
        )

if __name__ == "__main__":
    unittest.main()
