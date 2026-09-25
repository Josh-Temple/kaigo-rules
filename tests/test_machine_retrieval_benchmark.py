import unittest

from scripts.run_machine_retrieval_benchmark import question_link_order


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


if __name__ == "__main__":
    unittest.main()
