from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from build_relation_verification_registry import build  # noqa: E402


class RelationVerificationRegistryTests(unittest.TestCase):
    def test_current_aggregate_coverage(self):
        registry = build()
        summary = registry["summary"]

        self.assertEqual(summary["non_contains_semantic_or_cross_layer_relations"], 163)
        self.assertEqual(summary["independently_verified_relations"], 56)
        self.assertEqual(summary["remaining_not_independently_verified"], 107)
        self.assertEqual(
            sum(lane["verified_relations"] for lane in registry["lanes"]),
            summary["independently_verified_relations"],
        )
        self.assertEqual(registry["gaps"][0]["remaining_relations"], 107)

    def test_no_lane_promotes_human_or_current_verification(self):
        registry = build()
        for lane in registry["lanes"]:
            self.assertFalse(lane["human_verified"])
            self.assertFalse(lane["verified_current"])


if __name__ == "__main__":
    unittest.main()
