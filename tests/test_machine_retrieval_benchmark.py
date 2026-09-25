import unittest

from scripts.run_machine_retrieval_benchmark import (
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


if __name__ == "__main__":
    unittest.main()
