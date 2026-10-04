from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import validate_other_national_materials as validator


class OtherNationalMaterialsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base = ROOT / "data/shared/other-national-materials"
        cls.manifest = json.loads(
            (cls.base / "manifest.json").read_text(encoding="utf-8")
        )
        cls.registry = json.loads(
            (cls.base / "source-registry.json").read_text(encoding="utf-8")
        )

    def test_validator_passes(self):
        self.assertEqual(validator.validate(), [])

    def test_no_service_mapping_is_claimed(self):
        for row in self.registry["sources"]:
            self.assertEqual(
                row["applicability"],
                {"state": "NOT_ESTABLISHED", "service_ids": []},
            )
            self.assertFalse(row["projection_ready"])

    def test_existing_family_duplicates_are_explicit(self):
        duplicates = [
            row
            for row in self.registry["sources"]
            if row["classification"] == "DUPLICATE_OF_EXISTING_SOURCE_FAMILY"
        ]
        self.assertGreaterEqual(len(duplicates), 1)
        existing = set(self.manifest["existing_source_families"])
        self.assertTrue(
            all(row["overlap_source_family"] in existing for row in duplicates)
        )

    def test_accepted_candidates_are_official_national_sources(self):
        accepted = [
            row
            for row in self.registry["sources"]
            if row["classification"] == "ACCEPTED_OTHER_NATIONAL_MATERIAL"
        ]
        self.assertGreaterEqual(len(accepted), 1)
        for row in accepted:
            self.assertIn("厚生労働省", row["issuing_authority"])
            self.assertIsNone(row["overlap_source_family"])
            self.assertEqual(row["currentness_state"], "NOT_ESTABLISHED")


if __name__ == "__main__":
    unittest.main()
