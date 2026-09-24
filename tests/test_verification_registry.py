from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from build_verification_registry import build  # noqa: E402


class VerificationRegistryTests(unittest.TestCase):
    def test_relation_coverage_is_explicit(self):
        registry = build()
        relation = registry["relation_verification"]
        summary = registry["summary"]

        self.assertEqual(relation["inventory_relations"], 163)
        self.assertEqual(relation["independently_verified_relations"], 56)
        self.assertEqual(relation["remaining_unverified_relations"], 107)
        self.assertEqual(
            sum(lane["verified_relations"] for lane in relation["lanes"]),
            relation["independently_verified_relations"],
        )
        self.assertEqual(summary["semantic_or_cross_layer_relations_remaining"], 107)
        self.assertEqual(registry["gaps"][0]["remaining"], 107)
        self.assertFalse(relation["automatic_promotion_allowed"])


if __name__ == "__main__":
    unittest.main()
