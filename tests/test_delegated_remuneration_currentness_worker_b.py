import copy
import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_delegated_remuneration_currentness_worker_b as builder


class DelegatedRemunerationCurrentnessWorkerBTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.applicability = json.loads(
            builder.APPLICABILITY.read_text(encoding="utf-8")
        )
        cls.contract = json.loads(builder.CONTRACT.read_text(encoding="utf-8"))
        cls.receipt = json.loads(
            (
                ROOT
                / "data/shared/remuneration-delegated/item-body-verification.json"
            ).read_text(encoding="utf-8")
        )

    def build_with(self, applicability=None, contract=None):
        app = copy.deepcopy(applicability or self.applicability)
        source_contract = copy.deepcopy(contract or self.contract)

        def fake_load(path):
            if path == builder.APPLICABILITY:
                return copy.deepcopy(app)
            if path == builder.CONTRACT:
                return copy.deepcopy(source_contract)
            raise AssertionError(f"unexpected load path: {path}")

        with patch.object(builder, "load", side_effect=fake_load):
            return builder.build()

    def test_committed_artifact_is_deterministic(self):
        committed = json.loads(builder.OUTPUT.read_text(encoding="utf-8"))
        self.assertEqual(committed, builder.build())

    def test_residual_closure_counts(self):
        artifact = builder.build()
        self.assertEqual(artifact["summary"]["applicable_cells"], 37)
        self.assertEqual(artifact["summary"]["not_applicable_cells"], 2)
        self.assertEqual(artifact["summary"]["starting_ready_cells"], 15)
        self.assertEqual(
            artifact["summary"]["starting_deferred_applicable_cells"], 22
        )
        self.assertEqual(artifact["summary"]["currentness_pass_cells"], 37)
        self.assertEqual(artifact["summary"]["newly_promoted_cells"], 22)
        self.assertEqual(artifact["summary"]["deferred_applicable_cells"], 0)
        self.assertEqual(artifact["summary"]["projected_ready_increase"], 22)
        self.assertEqual(
            artifact["summary"]["projected_ready_count_after_integration"], 37
        )

    def test_existing_15_ready_cells_do_not_regress(self):
        artifact = builder.build()
        by_id = {
            row["service_id"]: row for row in artifact["promotions"]
        }
        self.assertTrue(builder.PRIOR_PROMOTED_SERVICE_IDS <= set(by_id))
        for service_id in builder.PRIOR_PROMOTED_SERVICE_IDS:
            self.assertFalse(by_id[service_id]["newly_promoted"])
            self.assertEqual(
                by_id[service_id]["prior_currentness_state"], "PASS"
            )

    def test_not_applicable_services_are_never_promoted(self):
        artifact = builder.build()
        promoted = {row["service_id"] for row in artifact["promotions"]}
        self.assertNotIn("specific-welfare-equipment-sale", promoted)
        self.assertNotIn(
            "specific-preventive-welfare-equipment-sale", promoted
        )

    def test_notice27_dependent_residual_cells_promote_after_source_closure(self):
        artifact = builder.build()
        by_id = {
            row["service_id"]: row for row in artifact["promotions"]
        }
        residual = set(artifact["starting_residual_service_ids"])
        self.assertEqual(len(residual), 22)
        for row in self.applicability["services"]:
            mapped = list(row.get("mapped_node_ids") or []) + list(
                row.get("compatibility_subnode_ids") or []
            )
            if row["service_id"] in residual:
                self.assertTrue(
                    any(node_id.startswith("notice27.") for node_id in mapped)
                )
                self.assertTrue(
                    by_id[row["service_id"]]["newly_promoted"]
                )

    def test_missing_cell_applicability_stays_blocked(self):
        applicability = copy.deepcopy(self.applicability)
        dayservice = next(
            row
            for row in applicability["services"]
            if row["service_id"] == "dayservice"
        )
        dayservice["applicability_state"] = "NOT_ESTABLISHED"
        artifact = self.build_with(applicability=applicability)
        promoted = {row["service_id"] for row in artifact["promotions"]}
        self.assertNotIn("dayservice", promoted)
        hold = next(
            row
            for row in artifact["holds"]
            if row["service_id"] == "dayservice"
        )
        self.assertEqual(hold["decision"], "DEFER")
        self.assertEqual(
            hold["blocker"],
            "No explicit canonical service applicability mapping.",
        )

    def test_stale_or_blocked_notice27_never_yields_pass(self):
        contract = copy.deepcopy(self.contract)
        source27 = next(
            row
            for row in contract["source_contracts"]
            if row["canonical_source_id"] == "mhlw-fee-notice27-base"
        )
        source27["currentness_state"] = "BLOCKED"
        source27["promotion_eligible"] = False
        artifact = self.build_with(contract=contract)
        promoted = {row["service_id"] for row in artifact["promotions"]}
        for row in self.applicability["services"]:
            mapped = list(row.get("mapped_node_ids") or []) + list(
                row.get("compatibility_subnode_ids") or []
            )
            if any(node_id.startswith("notice27.") for node_id in mapped):
                self.assertNotIn(row["service_id"], promoted)

    def test_currentness_source_identity_matches_item_body_source_identity(self):
        receipt_by_id = {
            row["source_id"]: row
            for row in self.receipt["source_verifications"]
        }
        for source in self.contract["source_contracts"]:
            if source.get("promotion_eligible") is not True:
                continue
            receipt = receipt_by_id[source["canonical_source_id"]]
            self.assertEqual(
                source["official_source_url"], receipt["official_url"]
            )
            self.assertEqual(
                source["version_model"]["page_snapshots"],
                receipt["page_snapshots"],
            )

    def test_no_regular_preventive_inheritance(self):
        artifact = builder.build()
        for row in artifact["promotions"]:
            self.assertFalse(
                row["applicability_proof"][
                    "inherited_from_sibling_service"
                ]
            )
            self.assertIn(
                (
                    "data/shared/remuneration-delegated/"
                    f"service-applicability.json#{row['service_id']}"
                ),
                row["applicability_proof"]["evidence"],
            )

    def test_source_level_currentness_still_requires_cell_mapping(self):
        applicability = copy.deepcopy(self.applicability)
        homevisit = next(
            row
            for row in applicability["services"]
            if row["service_id"] == "homevisit"
        )
        homevisit["mapped_node_ids"] = []
        artifact = self.build_with(applicability=applicability)
        promoted = {row["service_id"] for row in artifact["promotions"]}
        self.assertNotIn("homevisit", promoted)

    def test_coverage_matrix_projects_all_37_applicable_cells_only(self):
        import build_database_coverage_matrix as matrix_builder

        matrix = matrix_builder.build()
        delegated = {
            service["service_id"]: next(
                cell
                for cell in service["source_families"]
                if cell["source_family"]
                == "delegated_remuneration_criteria"
            )
            for service in matrix["services"]
        }
        promoted = {
            service_id
            for service_id, cell in delegated.items()
            if cell["currentness"]["state"] == "PASS"
        }
        expected = {
            row["service_id"] for row in builder.build()["promotions"]
        }
        self.assertEqual(promoted, expected)
        self.assertEqual(len(promoted), 37)
        for service_id in (
            "specific-welfare-equipment-sale",
            "specific-preventive-welfare-equipment-sale",
        ):
            self.assertNotEqual(
                delegated[service_id]["currentness"]["state"], "PASS"
            )


if __name__ == "__main__":
    unittest.main()
