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
            {"PASS": 23, "PARTIAL": 2, "GAP": 0, "FAIL": 0},
        )
        self.assertEqual(len(self.audit["items"]), 25)

    def test_partials_are_the_two_omitted_notice_body_cases(self):
        partial_ids = {
            row["id"] for row in self.audit["items"] if row["status"] == "PARTIAL"
        }
        self.assertEqual(
            partial_ids,
            {"night-homevisit.notice.002", "night-homevisit.notice.010"},
        )
        for row in self.audit["items"]:
            if row["status"] == "PARTIAL":
                self.assertTrue(row["limitation"])

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
