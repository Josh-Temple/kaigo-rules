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
AUDIT = ROOT / "data/verification/existing-ordinance37-service-slices-independent-audit.json"
MATRIX = ROOT / "data/database-coverage-matrix.generated.json"

spec = importlib.util.spec_from_file_location("bounded_currentness", SCRIPT)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(module)


class BoundedCurrentnessClosureTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        cls.activation = json.loads(ACTIVATION.read_text(encoding="utf-8"))
        cls.audit = json.loads(AUDIT.read_text(encoding="utf-8"))
        cls.matrix = json.loads(MATRIX.read_text(encoding="utf-8"))

    def errors_for(self, artifact):
        return module.validate_payload(
            artifact, self.activation, self.audit, self.matrix
        )

    def test_repository_contract_passes(self):
        self.assertEqual(self.errors_for(self.artifact), [])

    def test_exact_ten_governing_standards_cells_are_bounded_promotions(self):
        self.assertEqual(len(self.artifact["promotions"]), 10)
        self.assertTrue(
            all(
                row["source_family"] == "governing_standards_ordinance"
                and row["projected_currentness_state"] == "PASS"
                and row["projection_gate"]["kind"] == "EXPLICIT_BOUNDED_ALLOWLIST"
                for row in self.artifact["promotions"]
            )
        )
        self.assertEqual(
            self.artifact["priority_1"]["governing_standards_ordinance"]["after"],
            {"PARTIAL": 2, "NOT_ESTABLISHED": 27, "PASS": 10},
        )

    def test_care_act_remains_held(self):
        care = self.artifact["priority_1"]["care_insurance_act"]
        self.assertEqual(care["promotions"], 0)
        self.assertEqual(care["before"], care["after"])
        self.assertEqual(care["disposition"], "HOLD")

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
                explicit_gate=True,
            )
        )

    def test_ambiguous_scope_never_promotes(self):
        self.assertFalse(
            module.evaluate_projection(
                source_family="governing_standards_ordinance",
                source_class="CURRENT_OFFICIAL_VERSIONED",
                source_identity_complete=True,
                applicability_verified=True,
                canonical_scope_identified=False,
                source_version_contains_scope=True,
                ingestion_state="INGESTED",
                explicit_gate=True,
            )
        )

    def test_source_version_must_contain_scope(self):
        self.assertFalse(
            module.evaluate_projection(
                source_family="governing_standards_ordinance",
                source_class="CURRENT_OFFICIAL_VERSIONED",
                source_identity_complete=True,
                applicability_verified=True,
                canonical_scope_identified=True,
                source_version_contains_scope=False,
                ingestion_state="INGESTED",
                explicit_gate=True,
            )
        )

    def test_comparison_amendment_historical_classes_never_promote(self):
        for source_class in ("COMPARISON_ONLY", "AMENDMENT_ONLY", "HISTORICAL_ONLY"):
            with self.subTest(source_class=source_class):
                self.assertFalse(
                    module.evaluate_projection(
                        source_family="governing_standards_ordinance",
                        source_class=source_class,
                        source_identity_complete=True,
                        applicability_verified=True,
                        canonical_scope_identified=True,
                        source_version_contains_scope=True,
                        ingestion_state="INGESTED",
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
                explicit_gate=True,
            )
        )

    def test_not_applicable_is_preserved(self):
        self.assertFalse(
            module.evaluate_projection(
                source_family="governing_standards_ordinance",
                source_class="CURRENT_OFFICIAL_VERSIONED",
                source_identity_complete=True,
                applicability_verified=True,
                canonical_scope_identified=True,
                source_version_contains_scope=True,
                ingestion_state="NOT_APPLICABLE",
                explicit_gate=True,
            )
        )

    def test_missing_explicit_gate_never_promotes(self):
        self.assertFalse(
            module.evaluate_projection(
                source_family="governing_standards_ordinance",
                source_class="CURRENT_OFFICIAL_VERSIONED",
                source_identity_complete=True,
                applicability_verified=True,
                canonical_scope_identified=True,
                source_version_contains_scope=True,
                ingestion_state="INGESTED",
                explicit_gate=False,
            )
        )

    def test_fingerprint_drift_fails_closed(self):
        mutated = copy.deepcopy(self.artifact)
        mutated["promotions"][0]["source_identity"]["fingerprint"]["xml_sha256"] = "0" * 64
        errors = self.errors_for(mutated)
        self.assertTrue(any("source fingerprint drift" in error for error in errors), errors)

    def test_relation_human_publication_route_are_not_promoted(self):
        for row in self.artifact["promotions"]:
            unchanged = row["unchanged_axes"]
            self.assertNotEqual(unchanged["relation_verification"], "PASS")
            self.assertNotEqual(unchanged["human_review"], "PASS")
            self.assertNotEqual(unchanged["publication"], "AVAILABLE")
            self.assertFalse(self.artifact["safety"]["publication_changed"])
            self.assertFalse(self.artifact["safety"]["route_exposure_changed"])

    def test_validator_cli_passes(self):
        result = subprocess.run(
            [sys.executable, str(SCRIPT)],
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("10 exact governing-standards service cells", result.stdout)


if __name__ == "__main__":
    unittest.main()
