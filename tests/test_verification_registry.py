from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from build_verification_registry import build  # noqa: E402
from relation_verification_coverage import build_relation_coverage  # noqa: E402


class VerificationRegistryTests(unittest.TestCase):
    def test_relation_coverage_is_identity_derived(self):
        coverage = build_relation_coverage()
        registry = build()
        relation = registry["relation_verification"]
        summary = registry["summary"]

        self.assertEqual(len(coverage["inventory"]), 163)
        self.assertEqual(len(coverage["verified"]), 56)
        self.assertEqual(len(coverage["remaining"]), 107)
        self.assertEqual(coverage["overlap_relations"], 0)
        self.assertEqual(coverage["identity_validation"], "PASS")
        self.assertTrue(coverage["verified"].issubset(coverage["inventory"]))

        self.assertEqual(relation["inventory_relations"], 163)
        self.assertEqual(relation["independently_verified_relations"], 56)
        self.assertEqual(relation["remaining_unverified_relations"], 107)
        self.assertEqual(
            sum(lane["verified_relations"] for lane in relation["lanes"]),
            len(coverage["verified"]),
        )
        self.assertEqual(summary["semantic_or_cross_layer_relations_remaining"], 107)
        self.assertEqual(registry["gaps"][0]["remaining"], 107)
        self.assertFalse(relation["automatic_promotion_allowed"])


if __name__ == "__main__":
    unittest.main()
