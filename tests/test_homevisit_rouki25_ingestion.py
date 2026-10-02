import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class HomevisitRouki25IngestionContractTest(unittest.TestCase):
    def setUp(self):
        self.scope = json.loads(
            (ROOT / "data/services/homevisit/rouki25-scope.json").read_text(
                encoding="utf-8"
            )
        )

    def test_historical_scope_is_bounded_and_fail_closed(self):
        self.assertEqual(self.scope["service_id"], "homevisit")
        self.assertEqual(
            self.scope["boundary"]["start_heading"],
            "第三 訪問介護に関する基準",
        )
        self.assertEqual(
            self.scope["boundary"]["end_before_heading"],
            "第四 訪問入浴介護に関する基準",
        )
        self.assertEqual(
            self.scope["currentness_state"], "GAP_NOT_CURRENT_INTEGRATED_TEXT"
        )
        self.assertFalse(self.scope["safety"]["current_integrated_text"])
        self.assertFalse(self.scope["safety"]["human_verified"])
        self.assertFalse(self.scope["safety"]["verified_current"])
        self.assertFalse(self.scope["safety"]["automatic_promotion_allowed"])

    def test_scope_has_exact_queue_principal_item_inventory(self):
        count = 0
        for group in self.scope["groups"]:
            count += len(group.get("items", []))
            if group.get("group_body_item"):
                count += 1
        self.assertEqual(count, 35)
        self.assertEqual(
            self.scope["work_control"]["expected_principal_items"], 35
        )

    def test_group_numbers_are_unique_and_ordered(self):
        self.assertEqual(
            [group["number"] for group in self.scope["groups"]],
            ["1", "2", "3", "4"],
        )


if __name__ == "__main__":
    unittest.main()
