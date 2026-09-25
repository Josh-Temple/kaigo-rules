import unittest

from scripts.validate_faq_evidence_support import (
    legacy_rule_article_num,
    validate,
)


class FaqEvidenceSupportContractTest(unittest.TestCase):
    def test_legacy_rule_article_num(self):
        self.assertEqual(
            legacy_rule_article_num("ordinance37.article93.1.2"),
            "93",
        )
        self.assertEqual(
            legacy_rule_article_num("ordinance37.article30-2.2"),
            "30-2",
        )
        self.assertIsNone(legacy_rule_article_num("notice.dayservice.root"))

    def test_repository_contract(self):
        self.assertEqual(validate(), [])


if __name__ == "__main__":
    unittest.main()
