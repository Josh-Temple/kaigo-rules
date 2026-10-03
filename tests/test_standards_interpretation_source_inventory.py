import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

CASES = {
    "community-dayservice": "地域密着型通所介護",
    "regular-round": "定期巡回・随時対応型訪問介護看護",
    "night-homevisit": "夜間対応型訪問介護",
    "care-management": "居宅介護支援",
    "preventive-support": "介護予防支援",
}


class StandardsInterpretationSourceInventoryContractTest(unittest.TestCase):
    def test_inventory_checks_are_bounded_and_non_publishing(self):
        for service_id, anchor in CASES.items():
            with self.subTest(service_id=service_id):
                scope = json.loads(
                    (
                        ROOT
                        / f"data/services/{service_id}/standards-interpretation-scope.json"
                    ).read_text(encoding="utf-8")
                )
                check = scope["independent_source_inventory"]
                self.assertEqual(
                    check["check_level"],
                    "SOURCE_AVAILABILITY_AND_SERVICE_ANCHOR_ONLY",
                )
                self.assertEqual(check["service_anchor"], anchor)
                self.assertTrue(check["require_all_required_sources_fetchable"])
                self.assertTrue(check["require_anchor_in_at_least_one_source"])
                self.assertFalse(check["proves_item_body_match"])
                self.assertFalse(check["proves_currentness"])
                self.assertFalse(check["permits_publication"])

    def test_pinned_receipts_cover_every_manifest_required_source(self):
        for service_id in CASES:
            with self.subTest(service_id=service_id):
                scope = json.loads(
                    (
                        ROOT
                        / f"data/services/{service_id}/standards-interpretation-scope.json"
                    ).read_text(encoding="utf-8")
                )
                receipt = json.loads(
                    (
                        ROOT
                        / "data/verification/standards-interpretation-source-inventory"
                        / f"{service_id}.json"
                    ).read_text(encoding="utf-8")
                )
                required_urls = {
                    row["url"]
                    for row in scope.get("source_manifest", [])
                    if row.get("url")
                    and row.get("required_for_source_inventory") is True
                }
                source_rows = {
                    row["url"]: row
                    for row in receipt.get("sources", [])
                    if row.get("url")
                }
                self.assertEqual(
                    receipt["coverage"]["manifest_required_sources"],
                    len(required_urls),
                )
                self.assertEqual(
                    receipt["coverage"]["required_sources"],
                    len(required_urls),
                )
                self.assertTrue(required_urls.issubset(source_rows))
                for url in required_urls:
                    self.assertTrue(
                        source_rows[url]["required_for_source_inventory"],
                        url,
                    )
                    self.assertEqual(source_rows[url]["fetch"], "PASS", url)


if __name__ == "__main__":
    unittest.main()
