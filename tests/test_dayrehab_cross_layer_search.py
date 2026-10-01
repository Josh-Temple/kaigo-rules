import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class DayrehabCrossLayerSearchContractTest(unittest.TestCase):
    def test_search_module_uses_all_four_public_dayrehab_layers(self):
        source = (ROOT / "lib/dayrehab-search.ts").read_text(encoding="utf-8")
        for path in [
            "../data/ordinance37-nodes.json",
            "../data/services/dayrehab/ordinance37-index.generated.json",
            "../data/services/dayrehab/rouki25-historical.generated.json",
            "../data/services/dayrehab/remuneration-index.json",
            "../data/services/dayrehab/fee-guidance-index.json",
        ]:
            self.assertIn(path, source)
        self.assertIn('"ordinance37"', source)
        self.assertIn('"rouki25"', source)
        self.assertIn('"remuneration"', source)
        self.assertIn('"fee-guidance"', source)

    def test_expected_cross_layer_destinations_exist_in_canonical_public_data(self):
        notice = json.loads(
            (ROOT / "data/services/dayrehab/rouki25-historical.generated.json").read_text(
                encoding="utf-8"
            )
        )
        remuneration = json.loads(
            (ROOT / "data/services/dayrehab/remuneration-index.json").read_text(
                encoding="utf-8"
            )
        )
        guidance = json.loads(
            (ROOT / "data/services/dayrehab/fee-guidance-index.json").read_text(
                encoding="utf-8"
            )
        )
        ordinance = json.loads((ROOT / "data/ordinance37-nodes.json").read_text(encoding="utf-8"))

        self.assertTrue(any(row["id"] == "dayrehab.rouki25.3.2" for row in notice["items"]))
        self.assertTrue(any(row["id"] == "dayrehab-remuneration-注9" for row in remuneration["items"]))
        self.assertTrue(any(row["id"] == "R6-8-12" for row in guidance["items"]))
        self.assertTrue(any(row["id"] == "ordinance37.article.116" for row in ordinance))

    def test_search_results_are_regression_gated_across_four_layers(self):
        fixture = json.loads(
            (ROOT / "data/integration-sprint-release-regression-v0.1.json").read_text(
                encoding="utf-8"
            )
        )
        cases = {row["id"]: row for row in fixture["cases"]}
        self.assertEqual(cases["IR-16"]["path"], "/services/dayrehab/search?q=入浴介助")
        self.assertIn("報酬基準", cases["IR-16"]["contains_text"])
        self.assertIn("算定上の留意事項", cases["IR-16"]["contains_text"])
        self.assertEqual(cases["IR-17"]["path"], "/services/dayrehab/search?q=管理者")
        self.assertIn("基準省令", cases["IR-17"]["contains_text"])
        self.assertIn("基準解釈通知", cases["IR-17"]["contains_text"])

    def test_remuneration_items_have_direct_anchor_targets(self):
        page = (ROOT / "app/services/dayrehab/remuneration/page.tsx").read_text(
            encoding="utf-8"
        )
        self.assertGreaterEqual(page.count('id={item.id}'), 2)


if __name__ == "__main__":
    unittest.main()
