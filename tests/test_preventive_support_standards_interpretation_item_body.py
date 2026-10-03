import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SERVICE_ID = "preventive-support"
AUDIT = (
    ROOT
    / "data/verification/standards-interpretation-item-body/preventive-support.json"
)
STAGING = (
    ROOT
    / "data/services/preventive-support/standards-interpretation-staging.json"
)
SCOPE = ROOT / "data/services/preventive-support/standards-interpretation-scope.json"
SERVICE = ROOT / "data/services/preventive-support.json"
SOURCE_INVENTORY = (
    ROOT
    / "data/verification/standards-interpretation-source-inventory/preventive-support.json"
)


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


class PreventiveSupportStandardsInterpretationItemBodyTest(unittest.TestCase):
    def setUp(self):
        self.audit = load(AUDIT)
        self.staging = load(STAGING)
        self.scope = load(SCOPE)
        self.service = load(SERVICE)

    def test_audit_coverage_and_verdicts(self):
        self.assertEqual(
            self.audit["audit_kind"],
            "INDEPENDENT_STANDARDS_INTERPRETATION_ITEM_BODY_VERIFICATION",
        )
        self.assertEqual(self.audit["audit_result"], "PARTIAL_WITH_GAPS")
        coverage = self.audit["coverage"]
        self.assertEqual(coverage["task_total"], 34)
        self.assertEqual(coverage["structured_text_raw_entries"], 34)
        self.assertEqual(coverage["numbered_child_units_checked"], 55)
        self.assertEqual(
            coverage["verdicts"],
            {"PASS": 20, "PARTIAL": 13, "GAP": 1, "FAIL": 0},
        )
        self.assertEqual(len(self.audit["items"]), 34)
        self.assertEqual(
            [row["task_id"] for row in self.audit["items"] if row["verdict"] == "GAP"],
            ["KR2-10-B005"],
        )
        self.assertFalse(
            [row for row in self.audit["items"] if row["verdict"] == "FAIL"]
        )

    def test_audit_rows_are_bound_to_staging_without_rewriting_it(self):
        staging_by_task = {row["task_id"]: row for row in self.staging["items"]}
        self.assertEqual(set(staging_by_task), {row["task_id"] for row in self.audit["items"]})
        manifest_by_url = {
            row["url"]: row["id"] for row in self.scope["source_manifest"]
        }
        child_count = 0
        for row in self.audit["items"]:
            source = staging_by_task[row["task_id"]]
            with self.subTest(task_id=row["task_id"]):
                self.assertEqual(row["staging_id"], source["id"])
                self.assertEqual(row["path"], source["path"])
                self.assertEqual(row["heading"], source["heading"])
                self.assertEqual(row["source_locator"], source["source_locator"])
                self.assertEqual(row["stored_source_urls"], source["source_urls"])
                self.assertEqual(
                    row["stored_source_manifest_ids"],
                    [manifest_by_url[url] for url in source["source_urls"]],
                )
                self.assertEqual(row["source_url_check"], "PASS")
                self.assertFalse(row["current_integrated_notice_body_claimed"])
                self.assertGreaterEqual(row["numbered_child_units_checked"], 1)
                self.assertEqual(
                    row["numbered_child_units_checked"],
                    len(row["checked_child_locators"]),
                )
                child_count += row["numbered_child_units_checked"]
        self.assertEqual(child_count, 55)

    def test_fail_closed_boundaries_remain_intact(self):
        for key, value in self.audit["safety"].items():
            with self.subTest(safety_key=key):
                self.assertFalse(value)

        self.assertEqual(self.staging["publication_state"], "NOT_PUBLIC")
        self.assertEqual(self.staging["currentness_state"], "NOT_ESTABLISHED")
        self.assertEqual(self.staging["human_review_state"], "NOT_REVIEWED")
        self.assertEqual(
            self.staging["service_package_state"],
            "SEPARATE_PRECHECK_BLOCKER_PRESERVED",
        )

        publication = self.service["publication_gate"]
        self.assertFalse(publication["public_routes_enabled"])
        self.assertFalse(publication["content_ingested"])
        self.assertFalse(publication["independent_verification_complete"])
        self.assertFalse(publication["human_review_complete"])

        work_control = self.audit["work_control_observation"]
        self.assertEqual(work_control["task_id"], "KR2-10-E006")
        self.assertEqual(work_control["observed_status"], "BLOCKED")
        self.assertEqual(
            work_control["separation_rule"],
            "NOTICE_ITEM_BODY_VERIFICATION_DOES_NOT_CLEAR_PACKAGE_BLOCKER",
        )

    def test_source_versions_are_kept_separate(self):
        roles = {
            row["source_manifest_id"]: row["audit_role"]
            for row in self.audit["source_versions"]
        }
        self.assertEqual(
            roles["r6-final-comparison"],
            "PRIMARY_R6_ITEM_BODY_CHANGE_EVIDENCE_NOT_INTEGRATED_CURRENT_TEXT",
        )
        self.assertEqual(
            roles["work-control-source-4"],
            "HISTORICAL_2006_FULL_NOTICE_REFERENCE",
        )
        self.assertEqual(
            roles["work-control-source-5"],
            "UNDERLYING_STANDARD_HTML_REFERENCE_NOT_NOTICE_BODY",
        )
        self.assertEqual(
            roles["r6-amendment-page"],
            "OFFICIAL_DISCOVERY_INDEX_ONLY",
        )

    def test_service_specific_verifier_passes(self):
        result = subprocess.run(
            [
                sys.executable,
                str(
                    ROOT
                    / "scripts/verify_preventive_support_standards_interpretation_item_body.py"
                ),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("PARTIAL_WITH_GAPS", result.stdout)
        self.assertIn("34 tasks", result.stdout)
        self.assertIn("55 child units", result.stdout)

    def test_scope_observations_do_not_expand_staging(self):
        observations = self.audit["out_of_staging_source_observations"]
        self.assertEqual(len(observations), 1)
        self.assertIn("㉗", observations[0]["locator"])
        self.assertEqual(
            observations[0]["action"],
            "INTEGRATOR_FOLLOWUP_ONLY_NO_SCOPE_EXPANSION_IN_THIS_BRANCH",
        )
        self.assertEqual(self.staging["task_count"], 34)


if __name__ == "__main__":
    unittest.main()
