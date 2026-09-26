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

    def test_service_isolation_has_fail_closed_and_shared_control_cases(self):
        service_cases = [
            case
            for case in self.fixture["cases"]
            if case["coverage"] == "service_isolation"
        ]
        self.assertEqual({case["expect_status"] for case in service_cases}, {200, 404})

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
