"""Verify canonical parsing against HTML shape and malformed/duplicated metadata."""
import unittest
from scripts.verify_canonical_markup import canonical_urls


class CanonicalMarkupTests(unittest.TestCase):
    def test_rel_before_href(self):
        self.assertEqual(canonical_urls('<link rel="canonical" href="https://site.test/">'),
                         ["https://site.test/"])

    def test_href_before_rel(self):
        self.assertEqual(canonical_urls('<link href="https://site.test/law" rel="canonical"/>'),
                         ["https://site.test/law"])

    def test_ignores_noncanonical(self):
        self.assertEqual(canonical_urls('<link rel="stylesheet" href="/app.css">'), [])

    def test_duplicate_not_silently_ignored(self):
        self.assertEqual(canonical_urls('<link href="/a" rel="canonical"><link rel="canonical" href="/b">'),
                         ["/a", "/b"])


if __name__ == "__main__":
    unittest.main()
