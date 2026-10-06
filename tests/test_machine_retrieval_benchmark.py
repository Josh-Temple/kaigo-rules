import unittest

from scripts.run_machine_retrieval_benchmark import (
    build_evaluation_domains,
    evaluate_publication_context,
    question_link_order,
    require_expected_sha,
)


class MachineRetrievalParserTest(unittest.TestCase):
    def test_question_links_are_deduplicated_in_document_order(self):
        body = """
        <a href="/questions/a">A</a>
        <a href="/rules/93">Rule</a>
        <a href="/questions/b?from=search">B</a>
        <a href="/questions/a">A again</a>
        """
        self.assertEqual(question_link_order(body), ["a", "b"])

    def test_ignores_non_question_links(self):
        body = '<a href="/search">Search</a><a href="https://example.test/">External</a>'
        self.assertEqual(question_link_order(body), [])

    def test_expected_sha_must_match(self):
        sha = "a" * 40
        require_expected_sha(sha, sha)
        with self.assertRaises(RuntimeError):
            require_expected_sha(sha, "b" * 40)

    def test_expected_sha_must_be_full_lowercase_sha(self):
        with self.assertRaises(ValueError):
            require_expected_sha("a" * 40, "abc")

    def test_publication_context_accepts_only_safe_allowlisted_payload(self):
        payload = {
            "service": {"id": "homevisit", "label": "訪問介護"},
            "source_family": "governing_standards_ordinance",
            "items": [
                {
                    "source_text": "本文",
                    "item_body": {"article_num": "18"},
                    "source_metadata": {"service_id": "homevisit"},
                    "source_locator": {"url": "https://laws.e-gov.go.jp/law/411M50000100037"},
                    "currentness_statement": {"label": "現行本文を確認済み"},
                    "service_applicability_statement": {"label": "直接適用章"},
                }
            ],
        }
        result = evaluate_publication_context(
            200,
            __import__("json").dumps(payload, ensure_ascii=False),
            "homevisit",
            "18",
            "PUBLISHED",
        )
        self.assertTrue(result["pass"])
        self.assertEqual(result["errors"], [])

    def test_publication_context_rejects_management_field_leak(self):
        payload = {
            "service": {"id": "homevisit"},
            "items": [
                {
                    "source_text": "本文",
                    "item_body": {"article_num": "18"},
                    "source_metadata": {
                        "service_id": "homevisit",
                        "human_review": "NOT_REVIEWED",
                    },
                    "source_locator": {"url": "https://laws.e-gov.go.jp/law/411M50000100037"},
                    "currentness_statement": {},
                    "service_applicability_statement": {},
                }
            ],
        }
        result = evaluate_publication_context(
            200,
            __import__("json").dumps(payload, ensure_ascii=False),
            "homevisit",
            "18",
            "PUBLISHED",
        )
        self.assertFalse(result["pass"])
        self.assertTrue(
            any("forbidden management field leaked" in error for error in result["errors"])
        )

    def test_publication_context_requires_404_for_blocked_case(self):
        self.assertTrue(
            evaluate_publication_context(
                404, "{}", "care-management", "18", "BLOCKED"
            )["pass"]
        )
        self.assertFalse(
            evaluate_publication_context(
                200, "{}", "care-management", "18", "BLOCKED"
            )["pass"]
        )

    def test_machine_and_human_evaluation_domains_are_separate(self):
        benchmark = {
            "reporting_contract": {
                "machine_retrieval": {
                    "evaluation_kind": "FIXED_QUERY_MACHINE_RETRIEVAL",
                    "claims_supported": ["fixed-query top-3 rate"],
                },
                "human_effectiveness": {
                    "status": "NOT_EVALUATED",
                    "metrics": [],
                    "claims_not_supported": [
                        "human task-time improvement",
                        "human usability improvement",
                    ],
                    "required_evidence": "separate human field validation",
                },
            }
        }
        metrics = {"top3_hit_rate": 1.0}

        domains = build_evaluation_domains(benchmark, metrics)

        self.assertEqual(domains["machine_retrieval"]["status"], "MEASURED")
        self.assertEqual(domains["machine_retrieval"]["metrics"], metrics)
        self.assertEqual(domains["human_effectiveness"]["status"], "NOT_EVALUATED")
        self.assertEqual(domains["human_effectiveness"]["metrics"], {})
        self.assertEqual(domains["human_effectiveness"]["claims_supported"], [])


if __name__ == "__main__":
    unittest.main()
