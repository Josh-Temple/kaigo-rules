import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class QaServiceRelationsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.groups = json.loads((ROOT / "data/qa-group-relations.json").read_text(encoding="utf-8"))
        cls.generated = json.loads((ROOT / "data/qa-service-relations.generated.json").read_text(encoding="utf-8"))
        cls.manifest = json.loads((ROOT / "data/services/manifest.json").read_text(encoding="utf-8"))

    def test_projection_is_current(self):
        result = subprocess.run(
            [sys.executable, "scripts/build_qa_service_relations.py", "--check"],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_validator_passes(self):
        result = subprocess.run(
            [sys.executable, "scripts/validate_qa_service_relations.py"],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("Q&A service relations: OK", result.stdout)

    def test_group_membership_is_explicit_and_bounded(self):
        by_code = {g["service_code"]: g for g in self.groups["group_memberships"]}
        self.assertEqual(set(by_code), {"01", "02", "03", "04", "05", "06"})
        self.assertEqual(sum(len(g["member_service_ids"]) for g in by_code.values()), 74)
        self.assertEqual(
            set(by_code["05"]["member_service_ids"]),
            {"homevisit", "homebath", "homenursing", "homerehab", "homecaremanagement", "regular-round", "night-homevisit"},
        )
        self.assertEqual(
            set(by_code["06"]["member_service_ids"]),
            {"dayservice", "dayrehab", "dementia-dayservice", "community-dayservice"},
        )

    def test_services_without_direct_code_still_have_shared_scope(self):
        rows = {row["service_id"]: row for row in self.generated["services"]}
        no_direct = [row for row in rows.values() if not row["direct_individual_service_codes"]]
        self.assertEqual(len(no_direct), 13)
        for row in no_direct:
            self.assertEqual(row["individual_mapping_state"], "NO_INDIVIDUAL_QA_CODE")
            self.assertIn("01", row["candidate_query_service_codes"])
            self.assertEqual(row["scope_state"], "DEFINED_BY_DIRECT_OR_SHARED_GROUP")
            self.assertEqual(row["item_applicability_verification_state"], "NOT_ESTABLISHED")

    def test_direct_and_group_codes_are_deduplicated(self):
        for row in self.generated["services"]:
            codes = row["candidate_query_service_codes"]
            self.assertEqual(codes, sorted(set(codes)))
            expected = set(row["direct_individual_service_codes"])
            expected.update(rel["service_code"] for rel in row["shared_group_relations"])
            self.assertEqual(set(codes), expected)

    def test_qualified_variants_are_resolved_or_fail_closed(self):
        summary = self.generated["summary"]
        self.assertEqual(summary["qualified_or_variant_rows"], 297)
        self.assertEqual(summary["auto_resolved_qualified_or_variant_rows"], 295)
        self.assertEqual(summary["unresolved_fail_closed_rows"], 2)
        unresolved = {
            rule["raw_label"]
            for rule in self.groups["qualified_raw_label_rules"]
            if rule["resolution_state"] == "FAIL_CLOSED"
        }
        self.assertEqual(unresolved, {"4 施設サービス共通", "5 施設サービス共通"})

    def test_historical_and_special_codes_do_not_enter_service_query_index(self):
        forbidden = {"26", "27", "50", "51"}
        for row in self.generated["services"]:
            self.assertTrue(forbidden.isdisjoint(row["candidate_query_service_codes"]))

    def test_relation_artifacts_do_not_duplicate_qa_bodies(self):
        raw = (
            (ROOT / "data/qa-group-relations.json").read_text(encoding="utf-8")
            + (ROOT / "data/qa-service-relations.generated.json").read_text(encoding="utf-8")
        )
        self.assertNotIn('"question":', raw)
        self.assertNotIn('"answer":', raw)

    def test_no_verification_currentness_or_publication_promotion(self):
        policy = self.groups["policy"]
        self.assertTrue(policy["verification_state_is_not_promoted"])
        self.assertTrue(policy["currentness_state_is_not_promoted"])
        self.assertTrue(policy["human_review_state_is_not_promoted"])
        self.assertTrue(policy["publication_or_route_state_is_not_promoted"])
        for group in self.groups["group_memberships"]:
            self.assertEqual(group["applicability_verification_state"], "NOT_ESTABLISHED")


if __name__ == "__main__":
    unittest.main()
