import copy
import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR_PATH = ROOT / "scripts/validate_standards_interpretation_current_integrated_body.py"
ARTIFACT_PATH = ROOT / "data/verification/standards-interpretation-item-body/currentness-human-review-activation-worker-b.json"
MATRIX_PATH = ROOT / "data/database-coverage-matrix.generated.json"

spec = importlib.util.spec_from_file_location(
    "validate_standards_interpretation_current_integrated_body",
    VALIDATOR_PATH,
)
validator = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(validator)


class StandardsInterpretationCurrentIntegratedBodyTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.artifact = json.loads(ARTIFACT_PATH.read_text(encoding="utf-8"))
        cls.matrix = json.loads(MATRIX_PATH.read_text(encoding="utf-8"))

    def errors_for(self, artifact):
        return validator.validate_payload(artifact, self.matrix, ROOT)

    def test_worker_b_contract_passes(self):
        self.assertEqual(self.errors_for(self.artifact), [])

    def test_all_26_residuals_are_classified_without_promotion(self):
        self.assertEqual(len(self.artifact["inventory"]), 26)
        self.assertEqual(
            self.artifact["evidence_classification_summary"],
            {
                "official current integrated text available": 0,
                "official historical text + amendment materials available": 26,
                "official comparison table only": 0,
                "locator/fingerprint only": 0,
                "source identity unresolved": 0,
                "source body unavailable": 0,
            },
        )
        self.assertTrue(
            all(
                row["item_body_state_after_worker_b"] == "NOT_ESTABLISHED"
                and row["currentness_state_after_worker_b"] == "NOT_ESTABLISHED"
                for row in self.artifact["inventory"]
            )
        )

    def test_historical_match_alone_cannot_promote_currentness(self):
        mutated = copy.deepcopy(self.artifact)
        mutated["inventory"][0]["currentness_state_after_worker_b"] = "PASS"
        errors = self.errors_for(mutated)
        self.assertTrue(
            any("historical/amendment evidence was used to promote currentness" in e for e in errors),
            errors,
        )

    def test_comparison_material_cannot_promote_integrated_item_body(self):
        mutated = copy.deepcopy(self.artifact)
        mutated["inventory"][0]["evidence_class"] = "official comparison table only"
        mutated["inventory"][0]["item_body_state_after_worker_b"] = "PASS"
        errors = self.errors_for(mutated)
        self.assertTrue(
            any("item-body was promoted without verified integrated body" in e for e in errors),
            errors,
        )

    def test_incomplete_amendment_chain_cannot_be_reconstructed(self):
        mutated = copy.deepcopy(self.artifact)
        mutated["inventory"][0]["integrated_body_reconstruction"]["attempted"] = True
        mutated["inventory"][0]["integrated_body_reconstruction"]["reconstructed_text_committed"] = True
        errors = self.errors_for(mutated)
        self.assertTrue(
            any("reconstruction attempted despite incomplete evidence chain" in e for e in errors),
            errors,
        )
        self.assertTrue(
            any("reconstructed text committed despite incomplete evidence chain" in e for e in errors),
            errors,
        )

    def test_source_fingerprint_mismatch_fails_closed(self):
        mutated = copy.deepcopy(self.artifact)
        mutated["inventory"][0]["pinned_versioned_source_body_evidence"][0]["git_blob_sha"] = "0" * 40
        errors = self.errors_for(mutated)
        self.assertTrue(any("source fingerprint mismatch" in e for e in errors), errors)

    def test_validator_cli_passes(self):
        result = subprocess.run(
            [sys.executable, str(VALIDATOR_PATH)],
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("classified all 26 Standards Interpretation residuals", result.stdout)


if __name__ == "__main__":
    unittest.main()
