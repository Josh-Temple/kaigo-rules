import json
import unittest
from pathlib import Path

from scripts.run_integration_sprint_release_regression import (
    evaluate_case,
    resolve_url,
    validate_fixture,
)


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "data" / "integration-sprint-release-regression-v0.1.json"


class IntegrationSprintReleaseRegressionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))

    def test_fixture_covers_all_d4_release_dimensions(self):
        self.assertEqual(validate_fixture(self.fixture), [])
        self.assertEqual(
            set(self.fixture["required_coverage"]),
            {
                "service_isolation",
                "verification_wording",
                "scoped_counts",
                "faq_to_authority_expansion",
                "notice_retrieval",
            },
        )

    def test_dependencies_include_final_scope_and_count_stacks(self):
        deps = {
            row["issue"]: set(row["prs"])
            for row in self.fixture["integration_dependencies"]
        }
        self.assertTrue({179, 180, 182}.issubset(deps[170]))
        self.assertTrue({178, 181}.issubset(deps[171]))
        self.assertIn(176, deps[172])

    def test_service_isolation_has_rule_and_care_act_boundaries(self):
        service_cases = {
            case["id"]: case
            for case in self.fixture["cases"]
            if case["coverage"] == "service_isolation"
        }
        self.assertEqual(service_cases["IR-01"]["expect_status"], 200)
        self.assertIn("共有法令コーパス", service_cases["IR-01"]["contains_text"])
        self.assertEqual(service_cases["IR-02"]["expect_status"], 404)
        self.assertEqual(service_cases["IR-18"]["expect_status"], 200)
        self.assertIn(
            r"17\s*表示中の条文",
            service_cases["IR-18"]["regex_text"],
        )
        self.assertEqual(service_cases["IR-20"]["expect_status"], 404)
        self.assertIn("第十八条", service_cases["IR-18"]["not_contains_text"])
        self.assertIn(
            "この法律において「通所介護」とは",
            service_cases["IR-07"]["contains_text"],
        )
        self.assertIn(
            "この法律において「訪問介護」とは",
            service_cases["IR-07"]["not_contains_text"],
        )
        self.assertEqual(service_cases["IR-07"]["path"], "/law/8?service=dayservice")
        self.assertIn(
            "この法律において「訪問介護」とは",
            service_cases["IR-24"]["contains_text"],
        )

    def test_scoped_counts_cover_rules_and_law(self):
        count_cases = {
            case["id"]: case
            for case in self.fixture["cases"]
            if case["coverage"] == "scoped_counts"
        }
        self.assertIn(r"275\s*共有コーパス条文", count_cases["IR-04"]["regex_text"])
        self.assertIn(r"275\s*表示中の条文", count_cases["IR-04"]["regex_text"])
        self.assertIn(r"238\s*共有コーパス条文", count_cases["IR-08"]["regex_text"])
        self.assertIn(r"1671\s*共有コーパスノード", count_cases["IR-08"]["regex_text"])

    def test_faq_authority_requires_concrete_notice_source(self):
        case = next(row for row in self.fixture["cases"] if row["id"] == "IR-05")
        self.assertNotIn("/notices", case["href_contains"])
        self.assertIn(
            "https://www.mhlw.go.jp/content/12300000/000869798.pdf",
            case["href_contains"],
        )

    def test_human_effectiveness_claims_remain_disabled(self):
        contract = self.fixture["run_contract"]
        self.assertTrue(contract["machine_scope_only"])
        self.assertFalse(contract["human_effectiveness_claims_supported"])

    def test_evaluator_checks_text_regex_and_links(self):
        case = {
            "id": "T",
            "coverage": "scoped_counts",
            "title": "synthetic",
            "path": "/rules",
            "expect_status": 200,
            "contains_text": ["通所介護対象条文"],
            "regex_text": [r"40\s*通所介護対象条文"],
            "href_contains": ["/rules/10"],
        }
        body = """
        <main>
          <div><strong>40</strong><span>通所介護対象条文</span></div>
          <a href="/rules/10">shared</a>
        </main>
        """
        result = evaluate_case(case, 200, body)
        self.assertTrue(result["passed"], result["errors"])

    def test_evaluator_checks_forbidden_text(self):
        case = {
            "id": "T",
            "coverage": "service_isolation",
            "title": "synthetic",
            "path": "/law/8",
            "expect_status": 200,
            "contains_text": ["通所介護"],
            "not_contains_text": ["訪問介護"],
        }
        good = evaluate_case(case, 200, "<main>通所介護</main>")
        bad = evaluate_case(case, 200, "<main>通所介護 訪問介護</main>")
        self.assertTrue(good["passed"], good["errors"])
        self.assertFalse(bad["passed"])
        self.assertIn("forbidden text present: 訪問介護", bad["errors"])

    def test_evaluator_fails_when_expected_surface_is_missing(self):
        case = {
            "id": "T",
            "coverage": "verification_wording",
            "title": "synthetic",
            "path": "/search?q=看護師",
            "expect_status": 200,
            "contains_text": ["根拠対応確認済み"],
        }
        result = evaluate_case(case, 200, "<main>確認済み</main>")
        self.assertFalse(result["passed"])
        self.assertIn("missing text: 根拠対応確認済み", result["errors"])

    def test_resolve_url_encodes_japanese_query(self):
        url = resolve_url("https://example.test", "/search?q=看護師 外部")
        self.assertTrue(url.startswith("https://example.test/search?q="))
        self.assertNotIn("看護師", url)
        self.assertIn("%E7%9C%8B%E8%AD%B7%E5%B8%AB", url)


if __name__ == "__main__":
    unittest.main()
