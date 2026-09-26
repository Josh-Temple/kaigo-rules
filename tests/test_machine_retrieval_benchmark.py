import unittest

from scripts.run_machine_retrieval_benchmark import (
    build_evaluation_domains,
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
