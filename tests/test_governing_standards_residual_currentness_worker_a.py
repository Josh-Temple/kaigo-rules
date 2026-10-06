import copy
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/validate_governing_standards_residual_currentness_worker_a.py"
ARTIFACT = ROOT / "data/verification/governing-standards-residual-currentness-worker-a.json"
ACTIVATION = ROOT / "data/verification/shared-source-currentness-activation.json"
AUDIT = ROOT / "data/shared/standards/independent-audit.json"
MATRIX = ROOT / "data/database-coverage-matrix.generated.json"

spec = importlib.util.spec_from_file_location("worker_a_currentness", SCRIPT)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(module)


class GoverningStandardsResidualCurrentnessWorkerATest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        cls.activation = json.loads(ACTIVATION.read_text(encoding="utf-8"))
        cls.audit = json.loads(AUDIT.read_text(encoding="utf-8"))
        cls.matrix = json.loads(MATRIX.read_text(encoding="utf-8"))

    def errors_for(self, artifact=None, activation=None):
        return module.validate_payload(
            copy.deepcopy(artifact or self.artifact),
            copy.deepcopy(activation or self.activation),
            copy.deepcopy(self.audit),
            copy.deepcopy(self.matrix),
        )

    def test_repository_contract_passes(self):
        self.assertEqual(self.errors_for(), [])

    def test_exact_seventeen_residual_cells_are_bounded(self):
        decisions = self.artifact["decisions"]
        self.assertEqual(len(decisions), 17)
        self.assertEqual(
            {row["service_id"] for row in decisions},
            set(module.TARGETS),
        )
        self.assertTrue(all(row["decision"] == "PROMOTE_PASS_BOUNDED" for row in decisions))
        self.assertTrue(all(row["projected_currentness_state"] == "PASS" for row in decisions))

    def test_regular_and_preventive_source_identities_remain_distinct(self):
        by_id = {row["service_id"]: row for row in self.artifact["decisions"]}
        pairs = (
            ("dementia-dayservice", "preventive-dementia-dayservice"),
            ("small-scale-multifunctional", "preventive-small-scale-multifunctional"),
            ("dementia-group-home", "preventive-dementia-group-home"),
        )
        for regular, preventive in pairs:
            self.assertEqual(by_id[regular]["canonical_source_id"], "community-based-standards")
            self.assertEqual(
                by_id[preventive]["canonical_source_id"],
                "preventive-community-based-standards",
            )
            self.assertNotEqual(
                by_id[regular]["canonical_source_id"],
                by_id[preventive]["canonical_source_id"],
            )

    def test_preventive_support_is_independent(self):
        by_id = {row["service_id"]: row for row in self.artifact["decisions"]}
        self.assertEqual(
            by_id["preventive-support"]["canonical_source_id"],
            "preventive-support-standards",
        )

    def test_source_identity_mismatch_fails_closed(self):
        mutated = copy.deepcopy(self.artifact)
        row = next(x for x in mutated["decisions"] if x["service_id"] == "regular-round")
        row["canonical_source_id"] = "preventive-community-based-standards"
        errors = self.errors_for(mutated)
        self.assertTrue(any("regular-round: source identity mismatch" in e for e in errors), errors)

    def test_regular_preventive_inheritance_flag_fails_closed(self):
        mutated = copy.deepcopy(self.artifact)
        row = next(
            x for x in mutated["decisions"]
            if x["service_id"] == "preventive-dementia-dayservice"
        )
        row["applicability_proof"]["regular_preventive_inheritance_used"] = True
        errors = self.errors_for(mutated)
        self.assertTrue(any("regular/preventive inheritance is forbidden" in e for e in errors), errors)

    def test_stale_or_superseded_source_fails_closed(self):
        activation = copy.deepcopy(self.activation)
        family = activation["source_families"]["governing_standards_ordinance"]
        source = next(
            x for x in family["sources"]
            if x["canonical_source_id"] == "community-based-standards"
        )
        source["revision_lineage"]["current_revision_status"] = "PendingEnforcement"
        source["revision_lineage"]["repeal_status"] = "Repealed"
        errors = self.errors_for(activation=activation)
        self.assertTrue(any("not CurrentEnforced" in e for e in errors), errors)
        self.assertTrue(any("repealed/superseded" in e for e in errors), errors)

    def test_fingerprint_drift_fails_closed(self):
        mutated = copy.deepcopy(self.artifact)
        mutated["source_evidence"]["community-based-standards"]["fingerprint"]["xml_sha256"] = "0" * 64
        errors = self.errors_for(mutated)
        self.assertTrue(any("recorded source evidence drift: fingerprint" in e for e in errors), errors)

    def test_missing_explicit_gate_fails_closed(self):
        mutated = copy.deepcopy(self.artifact)
        mutated["decisions"][0]["projection_gate"]["allowed"] = False
        errors = self.errors_for(mutated)
        self.assertTrue(any("explicit bounded gate missing" in e for e in errors), errors)


if __name__ == "__main__":
    unittest.main()
