from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from validate_bounded_publication_allowlist import BoundedPublicationError, validate  # noqa: E402


class BoundedPublicationAllowlistTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.allowlist = json.loads(
            (ROOT / "data/bounded-publication-allowlist.json").read_text(encoding="utf-8")
        )
        cls.readiness = json.loads(
            (ROOT / "data/publication-readiness.generated.json").read_text(encoding="utf-8")
        )
        cls.currentness = json.loads(
            (ROOT / "data/verification/bounded-currentness-closure-worker-b.json").read_text(
                encoding="utf-8"
            )
        )
        cls.readiness_sha = cls.allowlist["source_readiness"]["git_blob_sha"]
        cls.currentness_sha = cls.allowlist["source_currentness"]["git_blob_sha"]

    def validate(self, allowlist=None, readiness=None):
        return validate(
            allowlist if allowlist is not None else self.allowlist,
            readiness if readiness is not None else self.readiness,
            readiness_blob_sha=self.readiness_sha,
        )

    def test_current_decision_is_progressive_publication(self):
        result = self.validate()
        expected = len(self.allowlist["publication_cell_allowlist"])
        self.assertEqual(result["publication_allowlist_cells"], expected)
        self.assertEqual(result["route_allowlist_cells"], expected)
        self.assertEqual(result["field_allowlist_cells"], expected)
        self.assertEqual(result["runtime_binding_cells"], expected)
        self.assertTrue(result["runtime_binding_established"])
        self.assertFalse(self.allowlist["summary"]["existing_public_surfaces_changed"])
        self.assertEqual(
            self.allowlist["summary"]["decision"],
            "PUBLISH_BOUNDED_READY_UNITS",
        )

    def test_preventive_ready_cells_are_explicitly_published(self):
        expected = {
            "preventive-homebath",
            "preventive-homenursing",
            "preventive-homerehab",
            "preventive-homecaremanagement",
            "preventive-dayrehab",
            "preventive-shortstay-life",
            "preventive-shortstay-medical",
            "preventive-specific-facility",
            "preventive-welfare-equipment-rental",
            "specific-preventive-welfare-equipment-sale",
        }
        published = {
            row["service_id"]
            for row in self.allowlist["publication_cell_allowlist"]
        }
        self.assertTrue(expected.issubset(published))

    def test_blocked_cell_cannot_be_published(self):
        mutated = copy.deepcopy(self.allowlist)
        row = next(
            row
            for row in self.readiness["cells"]
            if row["readiness"]
            not in {"READY_FOR_PUBLICATION_REVIEW", "NOT_APPLICABLE"}
        )
        mutated["publication_cell_allowlist"] = [
            {
                "service_id": row["service_id"],
                "source_family": row["source_family"],
            }
        ]
        mutated["summary"]["published_cells_added"] = 1
        with self.assertRaises(BoundedPublicationError):
            self.validate(allowlist=mutated)

    def test_ready_cell_still_requires_runtime_binding_to_publish(self):
        ready = next(
            (
                row
                for row in self.readiness["cells"]
                if row["readiness"] == "READY_FOR_PUBLICATION_REVIEW"
            ),
            None,
        )
        if ready is None:
            self.skipTest("no ready candidate in this snapshot")
        mutated = copy.deepcopy(self.allowlist)
        mutated["runtime_binding"]["established"] = False
        mutated["publication_cell_allowlist"] = [
            {
                "service_id": ready["service_id"],
                "source_family": ready["source_family"],
            }
        ]
        mutated["summary"]["published_cells_added"] = 1
        with self.assertRaises(BoundedPublicationError):
            self.validate(allowlist=mutated)

    def test_every_published_cell_has_only_safe_fields(self):
        expected = set(self.allowlist["safe_publication_fields"])
        self.assertEqual(len(expected), 6)
        for cell in self.allowlist["publication_cell_allowlist"]:
            key = f"{cell['service_id']}|{cell['source_family']}"
            self.assertEqual(
                set(self.allowlist["field_allowlist_by_cell"][key]),
                expected,
            )

    def test_publication_does_not_auto_enable_route(self):
        mutated = copy.deepcopy(self.allowlist)
        mutated["route_allowlist"] = [
            {"service_id": "dayservice", "source_family": "care_insurance_act"}
        ]
        mutated["summary"]["routes_added"] = 1
        with self.assertRaises(BoundedPublicationError):
            self.validate(allowlist=mutated)

    def test_unverified_relation_or_review_fields_cannot_be_exposed(self):
        mutated = copy.deepcopy(self.allowlist)
        mutated["field_allowlist_by_cell"] = {
            "dayservice|care_insurance_act": [
                "unverified_relation_assertion",
                "review_dependent_explanatory_text",
            ]
        }
        with self.assertRaises(BoundedPublicationError):
            self.validate(allowlist=mutated)

    def test_readiness_change_invalidates_selection(self):
        with self.assertRaises(BoundedPublicationError):
            validate(
                self.allowlist,
                self.readiness,
                readiness_blob_sha="0" * 40,
            )

    def test_currentness_change_invalidates_selection(self):
        mutated = copy.deepcopy(self.allowlist)
        mutated["source_currentness"]["git_blob_sha"] = "0" * 40
        with self.assertRaises(BoundedPublicationError):
            self.validate(allowlist=mutated)

    def test_unsupported_source_identity_fails_closed(self):
        mutated = copy.deepcopy(self.allowlist)
        key = next(
            key
            for key, binding in mutated["runtime_source_binding_by_cell"].items()
            if binding["promotion"]["service_id"] == "preventive-homebath"
        )
        mutated["runtime_source_binding_by_cell"][key]["promotion"]["source_identity"][
            "canonical_source_id"
        ] = "unsupported-source"
        with self.assertRaises(BoundedPublicationError):
            self.validate(allowlist=mutated)

    def test_wrong_applicability_contract_fails_closed(self):
        mutated = copy.deepcopy(self.allowlist)
        key = next(
            key
            for key, binding in mutated["runtime_source_binding_by_cell"].items()
            if binding["promotion"]["service_id"] == "preventive-homebath"
        )
        mutated["runtime_source_binding_by_cell"][key]["promotion"]["applicability_proof"][
            "state"
        ] = "PASS_DIRECT_SERVICE_CHAPTER"
        with self.assertRaises(BoundedPublicationError):
            self.validate(allowlist=mutated)

    def test_preventive_presentation_policy_is_explicit(self):
        policy = self.allowlist["policy"]
        self.assertTrue(policy["preventive_services_group_with_non_preventive_counterpart"])
        self.assertTrue(policy["preventive_support_is_standalone"])


if __name__ == "__main__":
    unittest.main()
