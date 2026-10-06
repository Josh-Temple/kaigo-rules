from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_database_coverage_matrix as coverage
import build_cross_layer_source_chain_independent_audit as cross_audit_builder

EXPECTED = {
    "regular-round": ("1", "1　定期巡回・随時対応型訪問介護看護費", "2　夜間対応型訪問介護費"),
    "night-homevisit": ("2", "2　夜間対応型訪問介護費", "2の2　地域密着型通所介護費"),
    "community-dayservice": ("2-2", "2の2　地域密着型通所介護費", "3　認知症対応型通所介護費"),
    "dementia-dayservice": ("3", "3　認知症対応型通所介護費", "4　小規模多機能型居宅介護費"),
    "small-scale-multifunctional": ("4", "4　小規模多機能型居宅介護費", "5　認知症対応型共同生活介護費"),
    "dementia-group-home": ("5", "5　認知症対応型共同生活介護費", "6　地域密着型特定施設入居者生活介護費"),
    "community-specific-facility": ("6", "6　地域密着型特定施設入居者生活介護費", "7　地域密着型介護老人福祉施設入所者生活介護費"),
    "community-elderly-facility": ("7", "7　地域密着型介護老人福祉施設入所者生活介護費", "8　複合型サービス費"),
    "nursing-small-scale-multifunctional": ("8", "8　複合型サービス費", "別表末尾"),
}
SOURCE_ID = "mhlw-community-fee-notice126-current"
SOURCE_URL = "https://www.mhlw.go.jp/web/t_doc?dataId=82aa7862&dataType=0"


def load(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


class CommunityBasedRemunerationIndexesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = load("data/services/manifest.json")
        cls.matrix = coverage.build()
        cls.by_service = {row["service_id"]: row for row in cls.matrix["services"]}
        cls.remuneration_assurance = {
            row["service_id"]: row
            for row in load("data/shared/remuneration-notification/service-item-body-assurance.json")["services"]
        }
        cls.delegated_applicability = {
            row["service_id"]: row
            for row in load("data/shared/remuneration-delegated/service-applicability.json")["services"]
        }
        cls.delegated_currentness_promoted = {
            row["service_id"]
            for row in load(
                "data/verification/delegated-remuneration-currentness-worker-b.json"
            )["promotions"]
            if row.get("promotion_applied") is True
        }

    def cell(self, service_id: str, family_id: str) -> dict:
        return next(
            cell for cell in self.by_service[service_id]["source_families"]
            if cell["source_family"] == family_id
        )

    def test_targets_come_from_current_service_taxonomy(self):
        actual = {
            row["service_id"]
            for row in self.manifest["services"]
            if row["service_class"] == "COMMUNITY_BASED_SERVICE"
        }
        self.assertEqual(actual, set(EXPECTED))

    def test_shared_notice_source_is_registered_once(self):
        matches = [row for row in load("data/sources.json") if row["id"] == SOURCE_ID]
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0]["publisher"], "厚生労働省")
        self.assertEqual(matches[0]["url"], SOURCE_URL)

    def test_source_registry_growth_does_not_byte_pin_unrelated_cross_layer_audit(self):
        self.assertNotIn("data/sources.json", cross_audit_builder.PINNED_INPUTS)

    def test_each_service_has_bounded_index_without_legal_text_copy(self):
        for service_id, (section, start, end) in EXPECTED.items():
            index = load(f"data/services/{service_id}/remuneration-index.json")
            self.assertEqual(index["service_scope"]["source_section"], section)
            self.assertEqual(index["service_scope"]["start_marker"], start)
            self.assertEqual(index["service_scope"]["end_marker"], end)
            self.assertFalse(index["service_scope"]["legal_text_duplicated"])
            self.assertGreaterEqual(len(index["top_level_items"]), 4)
            self.assertGreater(len(index["numeric_child_items"]), 0)
            self.assertFalse(index["coverage"]["item_body_complete"])
            self.assertEqual(
                index["coverage"]["total_index_entries"],
                len(index["top_level_items"]) + len(index["numeric_child_items"]),
            )
            self.assertTrue(all(
                row["source_locator"].startswith("別表 指定地域密着型サービス介護給付費単位数表")
                for row in index["top_level_items"] + index["numeric_child_items"]
            ))
            self.assertEqual(index["canonical_sources"][0]["id"], SOURCE_ID)
            self.assertEqual(index["canonical_sources"][0]["url"], SOURCE_URL)

    def test_assurance_layers_remain_independent_and_fail_closed(self):
        for service_id in EXPECTED:
            cfg = load(f"data/services/{service_id}.json")
            index = load(f"data/services/{service_id}/remuneration-index.json")
            self.assertEqual(
                cfg["ingestion_indexes"]["remuneration"],
                f"data/services/{service_id}/remuneration-index.json",
            )
            layer = cfg["ingestion_layers"]["remuneration"]
            self.assertEqual(layer["status"], "INDEXED_CURRENT_MHLW_DISPLAY_NOT_SERVICE_VERIFIED")
            self.assertEqual(layer["source_family"], "remuneration_notification")
            self.assertEqual(layer["currentness"], "NOT_ESTABLISHED")
            self.assertEqual(layer["human_review"], "NOT_REVIEWED")
            assurance = index["assurance"]
            self.assertEqual(assurance["item_body_verification"], "NOT_ESTABLISHED")
            self.assertEqual(assurance["currentness"], "NOT_ESTABLISHED")
            self.assertEqual(assurance["relation_verification"], "NOT_ESTABLISHED")
            self.assertEqual(assurance["human_review"], "NOT_REVIEWED")
            self.assertEqual(assurance["publication"], "BLOCKED")
            self.assertEqual(assurance["route_exposure"], "BLOCKED")
            self.assertFalse(assurance["automatic_verification_promotion_allowed"])
            self.assertFalse(cfg["publication_gate"]["public_routes_enabled"])
            self.assertFalse(cfg["routing"]["future_service_base_enabled"])

    def test_coverage_projects_remuneration_and_mapped_delegated_criteria_as_ingested(self):
        for service_id in EXPECTED:
            remuneration = self.cell(service_id, "remuneration_notification")
            delegated = self.cell(service_id, "delegated_remuneration_criteria")
            guidance = self.cell(service_id, "fee_calculation_guidance")
            self.assertEqual(remuneration["service_scope"]["state"], "SCOPE_DEFINED")
            self.assertEqual(remuneration["ingestion"]["state"], "INGESTED")
            self.assertEqual(
                remuneration["item_body_verification"]["state"],
                self.remuneration_assurance[service_id]["projection_state"],
            )
            self.assertEqual(remuneration["currentness"]["state"], "NOT_ESTABLISHED")
            self.assertEqual(remuneration["human_review"]["state"], "NOT_REVIEWED")
            self.assertEqual(remuneration["publication"]["state"], "BLOCKED")
            self.assertEqual(remuneration["route_exposure"]["state"], "BLOCKED")
            self.assertEqual(delegated["service_applicability"]["state"], "MAPPED")
            self.assertEqual(delegated["ingestion"]["state"], "INGESTED")
            self.assertEqual(
                delegated["item_body_verification"]["state"],
                self.delegated_applicability[service_id]["assurance"]["item_body_verification"],
            )
            self.assertEqual(
                delegated["currentness"]["state"],
                "PASS"
                if service_id in self.delegated_currentness_promoted
                else "NOT_ESTABLISHED",
            )
            self.assertEqual(delegated["publication"]["state"], "BLOCKED")
            self.assertEqual(delegated["route_exposure"]["state"], "BLOCKED")
            self.assertEqual(guidance["service_scope"]["state"], "SCOPE_DEFINED")
            self.assertEqual(guidance["ingestion"]["state"], "PARTIAL")
            self.assertEqual(guidance["item_body_verification"]["state"], "NOT_ESTABLISHED")
            self.assertEqual(guidance["currentness"]["state"], "NOT_ESTABLISHED")
            self.assertEqual(guidance["human_review"]["state"], "NOT_REVIEWED")
            self.assertEqual(guidance["publication"]["state"], "BLOCKED")
            self.assertEqual(guidance["route_exposure"]["state"], "BLOCKED")

    def test_existing_standards_interpretation_verification_is_not_regressed(self):
        for service_id in ("community-dayservice", "regular-round", "night-homevisit"):
            standards = self.cell(service_id, "standards_interpretation_notice")
            self.assertEqual(standards["item_body_verification"]["state"], "PASS")
            self.assertEqual(standards["currentness"]["state"], "NOT_ESTABLISHED")


if __name__ == "__main__":
    unittest.main()
