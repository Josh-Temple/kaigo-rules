"""Verify validate_data fast/full mode contracts and handbook reader enhancement registry."""
import unittest

from scripts.handbook_reader_enhancements import READER_ENHANCEMENTS, SOURCE_VALIDATORS
from scripts.validate_data import CHECKS, FAST_CHECKS, parse_args


class ValidateDataModesTest(unittest.TestCase):
    def test_fast_checks_are_strict_subset_of_full_checks(self):
        self.assertGreater(len(FAST_CHECKS), 0)
        self.assertLess(len(FAST_CHECKS), len(CHECKS))
        full_set = set(CHECKS)
        for check in FAST_CHECKS:
            self.assertIn(check, full_set)

    def test_default_mode_is_full_and_fast_mode_is_supported(self):
        self.assertEqual(parse_args([]).mode, "full")
        self.assertEqual(parse_args(["--mode", "fast"]).mode, "fast")
        self.assertEqual(parse_args(["--mode", "full"]).mode, "full")


class HandbookReaderEnhancementsRegistryTest(unittest.TestCase):
    def test_registry_has_unique_keys_and_valid_expected_counts(self):
        keys = [item.key for item in READER_ENHANCEMENTS]
        self.assertEqual(len(keys), len(set(keys)))
        self.assertEqual(len(keys), 14)
        self.assertGreaterEqual(len(SOURCE_VALIDATORS), 2)
        for item in READER_ENHANCEMENTS:
            self.assertGreaterEqual(item.expected_count, 1)
            self.assertTrue(callable(item.transform))
            self.assertTrue(item.failure_message())


if __name__ == "__main__":
    unittest.main()
