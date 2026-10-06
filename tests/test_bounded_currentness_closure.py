import copy
import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/validate_bounded_currentness_closure.py"
ARTIFACT = ROOT / "data/verification/bounded-currentness-closure-worker-b.json"
ACTIVATION = ROOT / "data/verification/shared-source-currentness-activation.json"
ORD37_AUDIT = ROOT / "data/verification/existing-ordinance37-service-slices-independent-audit.json"
SHARED_AUDIT = ROOT / "data/shared/standards/independent-audit.json"
MATRIX = ROOT / "data/database-coverage-matrix.generated.json"
PREVENTIVE_NODES = ROOT / "data/shared/standards/preventive-services-standards/nodes.json"

spec = importlib.util.spec_from_file_location("bounded_currentness", SCRIPT)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(module)


class BoundedCurrentnessClosureTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        cls.activation = json.loads(ACTIVATION.read_text(encoding="utf-8"))
        cls.ord37_audit = json.loads(ORD37_AUDIT.read_text(encoding="utf-8"))
        cls.shared_audit = json.loads(SHARED_AUDIT.read_text(encoding="utf-8"))
        cls.matrix = json.loads(MATRIX.read_text(encoding="utf-8"))
        cls.preventive_nodes = json.loads(PREVENTIVE_NODES.read_text(encoding="utf-8"))

    def errors_for(self, artifact):
        return module.validate_payload(
            artifact,
            self.activation,
            self.ord37_audit,
            self.shared_audit,
            self.matrix,
            self.preventive_nodes,
        )

    def test_repository_contract_passes(self):
        self.assertEqual(self.errors_for(self.artifact), [])

    def test_two_residual_and_twenty_two_cumulative_promotions(self):
        standards = self.artifact["priority_1"]["governing_standards_ordinance"]
        self.assertEqual(standards["new_promotions_this_wave"], 2)
        self.assertEqual(standards["cumulative_promotions"], 22)
        self.assertEqual(
            standards["after"],
            {"NOT_ESTABLISHED": 17, "PASS": 22},
        )
        new_ids = set(standards["newly_promoted_service_ids"])
        self.assertEqual(new_ids, {"dayservice", "dayrehab"})

    def test_preventive_promotions_are_currentness_only_direct_scope(self):
        new_ids = set(module.PREVENTIVE_SCOPE_PATHS)
        rows = {
            row["service_id"]: row
            for row in self.artifact["promotions"]
            if row["service_id"] in new_ids
        }
        self.assertEqual(set(rows), new_ids)
        for service_id, row in rows.items():
            self.assertEqual(
                row["source_identity"]["canonical_source_id"],
                "preventive-services-standards",
            )
            self.assertEqual(
                row["applicability_proof"]["state"],
                "PASS_DIRECT_SERVICE_SCOPE",
            )
            self.assertTrue(
                row["applicability_proof"][
                    "incorporation_wrappers_excluded_from_semantic_expansion"
                ]
            )
            self.assertEqual(row["projection_gate"]["scope"], "currentness_only")
            self.assertEqual(row["projected_currentness_state"], "PASS")

    def test_residual_promotions_are_exact_currentness_only_direct_chapters(self):
        new_ids = {"dayservice", "dayrehab"}
        rows = {
            row["service_id"]: row
            for row in self.artifact["promotions"]
            if row["service_id"] in new_ids
        }
        self.assertEqual(set(rows), new_ids)
        for service_id, row in rows.items():
            self.assertEqual(row["prior_currentness_state"], "PARTIAL")
            self.assertEqual(
                row["source_identity"]["canonical_source_id"],
                "ordinance37",
            )
            self.assertEqual(
                row["applicability_proof"]["state"],
                "PASS_DIRECT_SERVICE_CHAPTER",
            )
            self.assertTrue(
                row["applicability_proof"][
                    "incorporation_scope_excluded_from_semantic_expansion"
                ]
            )
            self.assertTrue(
                row["applicability_proof"]["live_service_slice_reverification_required"]
            )
            self.assertEqual(row["projection_gate"]["scope"], "currentness_only")
            self.assertEqual(row["projected_currentness_state"], "PASS")

    def test_remaining_seventeen_are_explicitly_deferred(self):
        inventory = {
            row["service_id"]: row
            for row in self.artifact["residual_target_inventory"]
        }
        promoted = {
            service_id
            for service_id, row in inventory.items()
            if row["decision"] == "PROMOTE_PASS_BOUNDED"
        }
        deferred = {
            service_id
            for service_id, row in inventory.items()
            if row["decision"] == "DEFER"
        }
        self.assertEqual(promoted, {"dayservice", "dayrehab"})
        self.assertEqual(len(deferred), 17)
        for service_id in deferred:
            self.assertEqual(
                inventory[service_id]["blocker"],
                "NO_SERVICE_SPECIFIC_CURRENT_VERSION_APPLICABILITY_PROOF",
            )

    def test_all_preventive_scopes_resolve_against_current_corpus(self):
        for service_id, path in module.PREVENTIVE_SCOPE_PATHS.items():
            with self.subTest(service_id=service_id):
                errors, summary = module.validate_preventive_scope(
                    service_id, path, self.preventive_nodes
                )
                self.assertEqual(errors, [])
                self.assertGreater(summary["primary_range"]["article_count"], 0)

    def test_care_act_remains_held(self):
        care = self.artifact["priority_1"]["care_insurance_act"]
        self.assertEqual(care["promotions"], 0)
        self.assertEqual(care["before"], care["after"])
        self.assertEqual(care["disposition"], "HOLD")

    def test_incomplete_latestness_families_remain_held(self):
        holds = self.artifact["high_yield_holds"]
        self.assertEqual(
            holds["delegated_remuneration_criteria"]["disposition"], "HOLD"
        )
        self.assertEqual(
            holds["unit_price_regional_classification"]["disposition"], "HOLD"
        )

    def test_source_current_without_applicability_never_promotes(self):
        self.assertFalse(
            module.evaluate_projection(
                source_family="governing_standards_ordinance",
                source_class="CURRENT_OFFICIAL_VERSIONED",
                source_identity_complete=True,
                applicability_verified=False,
                canonical_scope_identified=True,
                source_version_contains_scope=True,
                ingestion_state="INGESTED",
                item_body_state="PASS",
                explicit_gate=True,
            )
        )

    def test_item_body_must_pass(self):
        self.assertFalse(
            module.evaluate_projection(
                source_family="governing_standards_ordinance",
                source_class="CURRENT_OFFICIAL_VERSIONED",
                source_identity_complete=True,
                applicability_verified=True,
                canonical_scope_identified=True,
                source_version_contains_scope=True,
                ingestion_state="INGESTED",
                item_body_state="PARTIAL",
                explicit_gate=True,
            )
        )

    def test_national_qa_compilation_freshness_never_projects(self):
        self.assertFalse(
            module.evaluate_projection(
                source_family="national_qa",
                source_class="CURRENT_OFFICIAL_VERSIONED",
                source_identity_complete=True,
                applicability_verified=True,
                canonical_scope_identified=True,
                source_version_contains_scope=True,
                ingestion_state="INGESTED",
                item_body_state="PASS",
                explicit_gate=True,
            )
        )

    def test_fingerprint_drift_fails_closed(self):
        mutated = copy.deepcopy(self.artifact)
        new_ids = set(module.PREVENTIVE_SCOPE_PATHS)
        row = next(r for r in mutated["promotions"] if r["service_id"] in new_ids)
        row["source_identity"]["fingerprint"]["xml_sha256"] = "0" * 64
        errors = self.errors_for(mutated)
        self.assertTrue(
            any("preventive standards source fingerprint drift" in error for error in errors),
            errors,
        )

    def test_missing_explicit_gate_fails_closed(self):
        mutated = copy.deepcopy(self.artifact)
        mutated["promotions"][-1]["projection_gate"]["allowed"] = False
        errors = self.errors_for(mutated)
        self.assertTrue(
            any("bounded prerequisites" in error for error in errors),
            errors,
        )

    def test_validator_cli_passes(self):
        result = subprocess.run(
            [sys.executable, str(SCRIPT)],
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("2 new and 22 cumulative", result.stdout)


if __name__ == "__main__":
    unittest.main()
