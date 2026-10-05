from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from validate_bounded_publication_allowlist import (  # noqa: E402
    BoundedPublicationError,
    validate,
)


class BoundedPublicationAllowlistTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.allowlist = json.loads(
            (ROOT / "data/bounded-publication-allowlist.json").read_text(
                encoding="utf-8"
            )
        )
        cls.readiness = json.loads(
            (ROOT / "data/publication-readiness.generated.json").read_text(
                encoding="utf-8"
            )
        )
        cls.readiness_sha = cls.allowlist["source_readiness"]["git_blob_sha"]

    def test_zero_candidate_snapshot_is_fail_closed(self):
        result = validate(
            self.allowlist, self.readiness, readiness_blob_sha=self.readiness_sha
        )
        self.assertEqual(result["ready_candidates"], 0)
        self.assertEqual(result["publication_allowlist_cells"], 0)
        self.assertEqual(result["route_allowlist_cells"], 0)
        self.assertEqual(result["field_allowlist_cells"], 0)
        self.assertFalse(result["existing_public_surfaces_changed"])

    def test_blocked_cell_cannot_be_published(self):
        mutated = copy.deepcopy(self.allowlist)
        row = next(
            row
            for row in self.readiness["cells"]
            if row["readiness"] not in {
                "READY_FOR_PUBLICATION_REVIEW",
                "NOT_APPLICABLE",
            }
        )
        mutated["publication_cell_allowlist"] = [
            {
                "service_id": row["service_id"],
                "source_family": row["source_family"],
            }
        ]
        with self.assertRaises(BoundedPublicationError):
            validate(mutated, self.readiness, readiness_blob_sha=self.readiness_sha)

    def test_publication_does_not_auto_enable_route(self):
        mutated = copy.deepcopy(self.allowlist)
        mutated["route_allowlist"] = [
            {
                "service_id": "dayservice",
                "source_family": "care_insurance_act",
            }
        ]
        with self.assertRaises(BoundedPublicationError):
            validate(mutated, self.readiness, readiness_blob_sha=self.readiness_sha)

    def test_unverified_relation_or_review_fields_cannot_be_exposed(self):
        mutated = copy.deepcopy(self.allowlist)
        mutated["field_allowlist_by_cell"] = {
            "dayservice|care_insurance_act": [
                "unverified_relation_assertion",
                "review_dependent_explanatory_text",
            ]
        }
        with self.assertRaises(BoundedPublicationError):
            validate(mutated, self.readiness, readiness_blob_sha=self.readiness_sha)

    def test_readiness_change_invalidates_worker_d_selection(self):
        with self.assertRaises(BoundedPublicationError):
            validate(
                self.allowlist,
                self.readiness,
                readiness_blob_sha="0" * 40,
            )

    def test_preventive_presentation_policy_is_explicit(self):
        policy = self.allowlist["policy"]
        self.assertTrue(
            policy["preventive_services_group_with_non_preventive_counterpart"]
        )
        self.assertTrue(policy["preventive_support_is_standalone"])


if __name__ == "__main__":
    unittest.main()
