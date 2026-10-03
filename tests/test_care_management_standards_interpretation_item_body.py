import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "data/verification/standards-interpretation-item-body/care-management.json"
VERIFIER = ROOT / "scripts/verify_care_management_standards_interpretation_item_body.py"


class CareManagementStandardsInterpretationItemBodyTest(unittest.TestCase):
    def test_service_specific_verifier_passes_offline(self):
        result = subprocess.run(
            [sys.executable, str(VERIFIER)],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("PASS_VALIDATION", result.stdout)
        self.assertIn("currentness not established", result.stdout)

    def test_bounded_outcomes_and_unresolved_gaps_are_explicit(self):
        audit = json.loads(AUDIT.read_text(encoding="utf-8"))
        self.assertEqual(audit["audit_result"], "PARTIAL_WITH_GAPS")
        self.assertEqual(
            audit["summary"]["task_results"],
            {"PASS": 28, "PARTIAL": 1, "GAP": 3, "FAIL": 0},
        )
        self.assertEqual(
            audit["summary"]["child_entry_results"],
            {"PASS": 37, "PARTIAL": 1, "GAP": 3, "FAIL": 0},
        )
        self.assertEqual(
            {row["task_id"]: row["result"] for row in audit["unresolved_gaps"]},
            {
                "KR2-09-B012": "PARTIAL",
                "KR2-09-B015": "GAP",
                "KR2-09-B017": "GAP",
                "KR2-09-B019": "GAP",
            },
        )

    def test_r6_locator_drift_is_explicit_and_b009_source_is_pinned(self):
        audit = json.loads(AUDIT.read_text(encoding="utf-8"))
        self.assertEqual(
            [row["task_id"] for row in audit["source_version_locator_differences"]],
            [
                "KR2-09-B014",
                "KR2-09-B015",
                "KR2-09-B016",
                "KR2-09-B017",
                "KR2-09-B018",
                "KR2-09-B019",
            ],
        )
        effects = {
            row["task_id"]: row["effect"]
            for row in audit["source_version_locator_differences"]
        }
        for task_id in ("KR2-09-B014", "KR2-09-B016", "KR2-09-B018"):
            self.assertEqual(effects[task_id], "PASS_VERSION_AWARE_LOCATOR_RECORDED")
        b009 = next(row for row in audit["tasks"] if row["task_id"] == "KR2-09-B009")
        c07 = next(
            row
            for row in b009["official_evidence"]
            if row["source_id"] == "historical-c07-amendment-comparison"
        )
        self.assertTrue(c07["pinned_in_source_inventory"])
        self.assertEqual(b009["result"], "PASS")

    def test_no_assurance_promotion(self):
        audit = json.loads(AUDIT.read_text(encoding="utf-8"))
        boundaries = audit["verification_boundaries"]
        self.assertFalse(boundaries["current_integrated_notice_text_established"])
        self.assertFalse(boundaries["legal_currentness_promoted"])
        self.assertFalse(boundaries["human_review_promoted"])
        self.assertFalse(boundaries["publication_permitted"])
        self.assertFalse(boundaries["omitted_text_inferred"])
        self.assertFalse(boundaries["versions_silently_merged"])


if __name__ == "__main__":
    unittest.main()
