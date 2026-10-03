import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

CASES = {
    "homenursing": {
        "start": "第五 訪問看護に関する基準",
        "end": "第六 訪問リハビリテーションに関する基準",
        "count": 12,
    },
    "homerehab": {
        "start": "第六 訪問リハビリテーションに関する基準",
        "end": "第七 居宅療養管理指導に関する基準",
        "count": 7,
    },
    "homecaremanagement": {
        "start": "第七 居宅療養管理指導に関する基準",
        "end": "第八 通所介護に関する基準",
        "count": 9,
    },
}


class NextWaveRouki25IngestionContractTest(unittest.TestCase):
    def test_scopes_are_bounded_and_fail_closed(self):
        for service_id, expected in CASES.items():
            with self.subTest(service_id=service_id):
                scope = json.loads(
                    (
                        ROOT
                        / f"data/services/{service_id}/rouki25-scope.json"
                    ).read_text(encoding="utf-8")
                )
                self.assertEqual(scope["service_id"], service_id)
                self.assertEqual(scope["boundary"]["start_heading"], expected["start"])
                self.assertEqual(scope["boundary"]["end_before_heading"], expected["end"])
                self.assertEqual(
                    scope["currentness_state"], "GAP_NOT_CURRENT_INTEGRATED_TEXT"
                )
                self.assertFalse(scope["safety"]["current_integrated_text"])
                self.assertFalse(scope["safety"]["human_verified"])
                self.assertFalse(scope["safety"]["verified_current"])
                self.assertFalse(scope["safety"]["automatic_promotion_allowed"])

    def test_scopes_match_accepted_principal_item_counts(self):
        for service_id, expected in CASES.items():
            with self.subTest(service_id=service_id):
                scope = json.loads(
                    (
                        ROOT
                        / f"data/services/{service_id}/rouki25-scope.json"
                    ).read_text(encoding="utf-8")
                )
                count = 0
                for group in scope["groups"]:
                    count += len(group.get("items", []))
                    if group.get("group_body_item"):
                        count += 1
                self.assertEqual(count, expected["count"])
                self.assertEqual(
                    scope["work_control"]["expected_principal_items"],
                    expected["count"],
                )


if __name__ == "__main__":
    unittest.main()
