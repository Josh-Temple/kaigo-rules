import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class ShortstayLifeRouki25IngestionContractTest(unittest.TestCase):
    def setUp(self):
        self.scope = json.loads(
            (ROOT / "data/services/shortstay-life/rouki25-scope.json").read_text(
                encoding="utf-8"
            )
        )

    def test_historical_scope_is_bounded_and_fail_closed(self):
        self.assertEqual(self.scope["service_id"], "shortstay-life")
        self.assertEqual(
            self.scope["boundary"]["start_heading"],
            "第一〇 短期入所生活介護",
        )
        self.assertEqual(
            self.scope["boundary"]["end_before_heading"],
            "第一一 短期入所療養介護",
        )
        self.assertEqual(
            self.scope["currentness_state"], "GAP_NOT_CURRENT_INTEGRATED_TEXT"
        )
        self.assertFalse(self.scope["safety"]["current_integrated_text"])
        self.assertFalse(self.scope["safety"]["human_verified"])
        self.assertFalse(self.scope["safety"]["verified_current"])
        self.assertFalse(self.scope["safety"]["automatic_promotion_allowed"])

    def test_scope_preserves_accepted_34_primary_item_inventory(self):
        group_counts = []
        for group in self.scope["groups"]:
            count = len(group.get("items", []))
            if group.get("group_body_item"):
                count += 1
            group_counts.append(count)
        self.assertEqual(group_counts, [6, 9, 15, 4])
        self.assertEqual(sum(group_counts), 34)
        self.assertEqual(
            self.scope["work_control"]["expected_principal_items"], 34
        )
        self.assertIn(
            "49 explicit child nodes",
            self.scope["work_control"]["accepted_inventory"],
        )


if __name__ == "__main__":
    unittest.main()
