import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "data/verification/standards-interpretation-item-body/night-homevisit.json"
SCRIPT = ROOT / "scripts/verify_night_homevisit_standards_interpretation_item_body.py"


class NightHomevisitItemBodyAuditTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.audit = json.loads(AUDIT.read_text(encoding="utf-8"))

    def test_all_25_items_are_covered_with_bounded_results(self):
        self.assertEqual(self.audit["coverage"]["expected_items"], 25)
        self.assertEqual(self.audit["coverage"]["observed_items"], 25)
        self.assertEqual(
            self.audit["coverage"]["counts"],
            {"PASS": 25, "PARTIAL": 0, "GAP": 0, "FAIL": 0},
        )
        self.assertEqual(len(self.audit["items"]), 25)

    def test_all_item_body_gaps_are_closed_with_direct_notice_evidence(self):
        self.assertFalse(self.audit["unresolved_gaps"])
        partial_ids = {
            row["id"] for row in self.audit["items"] if row["status"] == "PARTIAL"
        }
        self.assertFalse(partial_ids)
        source = self.audit["source_roles"]["h27-full-notice-comparison"]
        self.assertEqual(source["role"], "HISTORICAL_FULL_NOTICE_BODY_EVIDENCE")
        by_id = {row["id"]: row for row in self.audit["items"]}
        for item_id in ("night-homevisit.notice.002", "night-homevisit.notice.010"):
            self.assertEqual(by_id[item_id]["status"], "PASS")
            self.assertTrue(
                any(
                    evidence["source_id"] == "h27-full-notice-comparison"
                    for evidence in by_id[item_id]["evidence"]
                )
            )

    def test_official_html_is_not_misclassified_as_notice_body(self):
        self.assertEqual(
            self.audit["source_roles"]["historical-official-html"]["role"],
            "ORDINANCE_TEXT_CROSSCHECK_NOT_NOTICE_BODY",
        )

    def test_currentness_and_publication_stay_false(self):
        safety = self.audit["safety"]
        for key in (
            "currentness_proven",
            "integrated_current_text_constructed",
            "omitted_text_auto_composed",
            "human_review_promoted",
            "publication_permitted",
            "public_route_enabled",
        ):
            self.assertFalse(safety[key], key)

    def test_service_specific_verifier_passes_offline(self):
        result = subprocess.run(
            [sys.executable, str(SCRIPT)],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
