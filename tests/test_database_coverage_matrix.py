from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_database_coverage_matrix as coverage


class DatabaseCoverageMatrixTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.matrix = coverage.build()
        cls.by_service = {
            row["service_id"]: row
            for row in cls.matrix["services"]
        }
        cls.remuneration_assurance = {
            row["service_id"]: row
            for row in coverage.load("data/shared/remuneration-notification/service-item-body-assurance.json")["services"]
        }
        cls.delegated_applicability = {
            row["service_id"]: row
            for row in coverage.load("data/shared/remuneration-delegated/service-applicability.json")["services"]
        }

    def cell(self, service_id: str, family_id: str) -> dict:
        return next(
            cell for cell in self.by_service[service_id]["source_families"]
            if cell["source_family"] == family_id
        )

    def test_manifest_drives_rows(self):
        manifest = coverage.load("data/services/manifest.json")
        self.assertEqual(
            [row["service_id"] for row in self.matrix["services"]],
            [row["service_id"] for row in manifest["services"]],
        )

    def test_shared_corpus_and_service_scope_are_separate_dimensions(self):
        cell = self.cell("community-dayservice", "care_insurance_act")
        self.assertEqual(cell["corpus_availability"]["state"], "AVAILABLE")
        self.assertEqual(cell["corpus_availability"]["kind"], "SHARED")
        self.assertEqual(cell["service_scope"]["state"], "SCOPE_DEFINED")

    def test_scope_wave_projects_all_shared_major_source_families(self):
        family_ids = {
            "care_insurance_act",
            "governing_standards_ordinance",
            "remuneration_notification",
            "delegated_remuneration_criteria",
            "unit_price_regional_classification",
            "national_qa",
        }
        for row in self.matrix["services"]:
            states = {
                cell["source_family"]: cell["service_scope"]["state"]
                for cell in row["source_families"]
                if cell["source_family"] in family_ids
            }
            self.assertEqual(family_ids, set(states), row["service_id"])
            self.assertTrue(
                all(state == "SCOPE_DEFINED" for state in states.values()),
                row["service_id"],
            )

    def test_delegated_criteria_applicability_is_separate_from_assurance(self):
        dayservice = self.cell("dayservice", "delegated_remuneration_criteria")
        dayrehab = self.cell("dayrehab", "delegated_remuneration_criteria")

        self.assertEqual(dayservice["service_scope"]["state"], "SCOPE_DEFINED")
        self.assertEqual(dayservice["service_applicability"]["state"], "MAPPED")
        self.assertGreater(dayservice["service_applicability"]["mapped_node_count"], 0)
        self.assertEqual(dayservice["ingestion"]["state"], "INGESTED")
        self.assertEqual(
            dayservice["item_body_verification"]["state"],
            self.delegated_applicability["dayservice"]["assurance"]["item_body_verification"],
        )
        self.assertEqual(dayservice["currentness"]["state"], "NOT_ESTABLISHED")
        self.assertEqual(dayservice["human_review"]["state"], "NOT_REVIEWED")
        self.assertEqual(dayservice["publication"]["state"], "BLOCKED")
        self.assertEqual(dayservice["route_exposure"]["state"], "BLOCKED")

        self.assertEqual(dayrehab["service_scope"]["state"], "SCOPE_DEFINED")
        self.assertEqual(dayrehab["service_applicability"]["state"], "MAPPED")
        self.assertGreater(dayrehab["service_applicability"]["mapped_node_count"], 0)
        self.assertEqual(dayrehab["ingestion"]["state"], "INGESTED")
        self.assertEqual(
            dayrehab["item_body_verification"]["state"],
            self.delegated_applicability["dayrehab"]["assurance"]["item_body_verification"],
        )
        self.assertEqual(dayrehab["currentness"]["state"], "NOT_ESTABLISHED")

    def test_homevisit_remuneration_ingestion_stays_fail_closed(self):
        remuneration = self.cell("homevisit", "remuneration_notification")
        delegated = self.cell("homevisit", "delegated_remuneration_criteria")
        self.assertEqual(remuneration["service_scope"]["state"], "SCOPE_DEFINED")
        self.assertEqual(remuneration["ingestion"]["state"], "INGESTED")
        self.assertEqual(
            remuneration["item_body_verification"]["state"],
            self.remuneration_assurance["homevisit"]["projection_state"],
        )
        self.assertEqual(remuneration["currentness"]["state"], "NOT_ESTABLISHED")
        self.assertEqual(remuneration["publication"]["state"], "BLOCKED")
        self.assertEqual(remuneration["route_exposure"]["state"], "BLOCKED")
        self.assertEqual(delegated["service_applicability"]["state"], "MAPPED")
        self.assertGreater(delegated["service_applicability"]["mapped_node_count"], 0)
        self.assertEqual(delegated["ingestion"]["state"], "INGESTED")
        self.assertEqual(
            delegated["item_body_verification"]["state"],
            self.delegated_applicability["homevisit"]["assurance"]["item_body_verification"],
        )
        self.assertEqual(delegated["currentness"]["state"], "PASS")
        self.assertIn(
            "data/verification/delegated-remuneration-currentness-worker-b.json#homevisit::delegated_remuneration_criteria",
            delegated["currentness"]["evidence"],
        )
        self.assertEqual(delegated["relation_verification"]["state"], "NOT_ESTABLISHED")
        self.assertEqual(delegated["human_review"]["state"], "NOT_REVIEWED")
        self.assertEqual(delegated["publication"]["state"], "BLOCKED")
        self.assertEqual(delegated["route_exposure"]["state"], "BLOCKED")

    def test_unit_price_item_body_projection_uses_service_specific_primary_source_evidence(self):
        homevisit = self.cell("homevisit", "unit_price_regional_classification")
        dayservice = self.cell("dayservice", "unit_price_regional_classification")
        dayrehab = self.cell("dayrehab", "unit_price_regional_classification")
        sale = self.cell("specific-welfare-equipment-sale", "unit_price_regional_classification")

        self.assertEqual(homevisit["service_scope"]["state"], "SCOPE_DEFINED")
        self.assertEqual(homevisit["ingestion"]["state"], "INGESTED")
        self.assertEqual(homevisit["item_body_verification"]["state"], "PASS")
        self.assertIn(
            "data/unit-price-item-body-assurance.json#homevisit",
            homevisit["item_body_verification"]["evidence"],
        )
        self.assertEqual(homevisit["currentness"]["state"], "PASS")
        self.assertIn(
            "data/verification/high-value-currentness-expansion-worker-c.json#homevisit::unit_price_regional_classification",
            homevisit["currentness"]["evidence"],
        )
        self.assertEqual(homevisit["publication"]["state"], "BLOCKED")
        self.assertEqual(homevisit["route_exposure"]["state"], "BLOCKED")

        self.assertEqual(dayservice["item_body_verification"]["state"], "PASS")
        self.assertIn(
            "data/unit-price-independent-audit.json",
            dayservice["item_body_verification"]["evidence"],
        )
        self.assertEqual(dayservice["currentness"]["state"], "PASS")

        # An applicable but unselected cell stays fail-closed: shared-source
        # currentness is never broadcast to the rest of the family.
        self.assertEqual(dayrehab["item_body_verification"]["state"], "PASS")
        self.assertEqual(dayrehab["currentness"]["state"], "NOT_ESTABLISHED")

        self.assertEqual(sale["item_body_verification"]["state"], "NOT_APPLICABLE")
        self.assertEqual(sale["currentness"]["state"], "NOT_APPLICABLE")

    def test_other_national_item_body_projection_is_partial_and_cross_axis_fail_closed(self):
        for row in self.matrix["services"]:
            cell = self.cell(row["service_id"], "other_national_manuals_forms")
            self.assertEqual(cell["item_body_verification"]["state"], "PARTIAL", row["service_id"])
            self.assertIn(
                f"data/shared/other-national-materials/item-body-assurance.json#{row['service_id']}",
                cell["item_body_verification"]["evidence"],
                row["service_id"],
            )
            self.assertEqual(cell["currentness"]["state"], "NOT_ESTABLISHED", row["service_id"])
            self.assertEqual(cell["human_review"]["state"], "NOT_REVIEWED", row["service_id"])
            self.assertEqual(cell["publication"]["state"], "BLOCKED", row["service_id"])
            self.assertEqual(cell["route_exposure"]["state"], "BLOCKED", row["service_id"])

    def test_shared_care_act_item_body_pass_does_not_promote_other_assurance_layers(self):
        for row in self.matrix["services"]:
            cell = self.cell(row["service_id"], "care_insurance_act")
            self.assertEqual(
                cell["item_body_verification"]["state"],
                "PASS",
                row["service_id"],
            )
            self.assertIn(
                "data/egov-content-independent-audit.json",
                cell["item_body_verification"]["evidence"],
                row["service_id"],
            )
            self.assertEqual(
                cell["service_scope"]["state"],
                "SCOPE_DEFINED",
                row["service_id"],
            )
            self.assertEqual(
                cell["ingestion"]["state"],
                "INGESTED",
                row["service_id"],
            )
            self.assertEqual(
                cell["human_review"]["state"],
                "NOT_REVIEWED",
                row["service_id"],
            )

        dayservice = self.cell("dayservice", "care_insurance_act")
        homevisit = self.cell("homevisit", "care_insurance_act")
        self.assertEqual(dayservice["currentness"]["state"], "PARTIAL")
        self.assertEqual(homevisit["currentness"]["state"], "NOT_ESTABLISHED")
        self.assertEqual(homevisit["publication"]["state"], "BLOCKED")
        self.assertEqual(homevisit["route_exposure"]["state"], "BLOCKED")

    def test_item_body_pass_does_not_promote_currentness(self):
        cell = self.cell("community-dayservice", "standards_interpretation_notice")
        self.assertEqual(cell["item_body_verification"]["state"], "PASS")
        self.assertEqual(cell["currentness"]["state"], "NOT_ESTABLISHED")

    def test_direct_qa_mapping_defines_scope_without_enabling_route(self):
        cell = self.cell("shortstay-medical", "national_qa")
        self.assertEqual(cell["corpus_availability"]["state"], "AVAILABLE")
        self.assertEqual(cell["service_scope"]["state"], "SCOPE_DEFINED")
        self.assertEqual(cell["route_exposure"]["state"], "BLOCKED")
        self.assertEqual(cell["publication"]["state"], "BLOCKED")

    def test_projection_is_fail_closed(self):
        policy = self.matrix["policy"]
        self.assertFalse(policy["canonical_status_writeback_allowed"])
        self.assertFalse(policy["verification_auto_promotion_allowed"])
        self.assertFalse(policy["currentness_auto_promotion_allowed"])
        self.assertFalse(policy["human_review_auto_promotion_allowed"])
        self.assertFalse(policy["route_auto_enable_allowed"])
        self.assertFalse(policy["single_completion_percentage_allowed"])

    def test_no_single_completion_percentage(self):
        def keys(value):
            if isinstance(value, dict):
                for key, child in value.items():
                    yield key
                    yield from keys(child)
            elif isinstance(value, list):
                for child in value:
                    yield from keys(child)
        forbidden = {
            "completion_rate",
            "completion_percentage",
            "overall_completion_rate",
            "overall_completion_percentage",
        }
        self.assertTrue(forbidden.isdisjoint(set(keys(self.matrix))))


if __name__ == "__main__":
    unittest.main()
