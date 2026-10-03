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

    def test_all_item_bodies_are_evidence_matched_without_assurance_promotion(self):
        audit = json.loads(AUDIT.read_text(encoding="utf-8"))
        self.assertEqual(audit["audit_result"], "PASS_CONTENT_EVIDENCE_MATCH_ONLY")
        self.assertEqual(
            audit["summary"]["task_results"],
            {"PASS": 32, "PARTIAL": 0, "GAP": 0, "FAIL": 0},
        )
        self.assertEqual(
            audit["summary"]["child_entry_results"],
            {"PASS": 51, "PARTIAL": 0, "GAP": 0, "FAIL": 0},
        )
        self.assertEqual(audit["unresolved_gaps"], [])

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
        for task_id in ("KR2-09-B015", "KR2-09-B017", "KR2-09-B019"):
            self.assertEqual(
                effects[task_id],
                "PASS_HISTORICAL_BODY_AND_VERSION_AWARE_LOCATORS_RECORDED",
            )
        resolved = {row["id"]: row for row in audit["resolved_source_findings"]}
        self.assertEqual(
            set(resolved),
            {
                "historical-c07-amendment-comparison",
                "historical-2015-amendment-comparison",
                "historical-2018-amendment-comparison",
            },
        )
        self.assertEqual(
            resolved["historical-2015-amendment-comparison"]["supports"],
            ["KR2-09-B012", "KR2-09-B015", "KR2-09-B017", "KR2-09-B019"],
        )
        self.assertEqual(
            resolved["historical-2018-amendment-comparison"]["supports"],
            ["KR2-09-B015", "KR2-09-B017", "KR2-09-B019"],
        )
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
