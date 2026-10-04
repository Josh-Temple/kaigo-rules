"""Guard the remaining service links to shared interpretation notices."""
from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SHARED = ROOT / "data/shared/standards-interpretation"
EXPECTED_SERVICES = {
    "dementia-dayservice",
    "small-scale-multifunctional",
    "dementia-group-home",
    "community-specific-facility",
    "community-elderly-facility",
    "nursing-small-scale-multifunctional",
    "elderly-welfare-facility",
    "elderly-health-facility",
    "care-medical-institution",
    "preventive-dementia-dayservice",
    "preventive-small-scale-multifunctional",
    "preventive-dementia-group-home",
}


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


class RemainingStandardsInterpretationCoverageTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source_register = load(SHARED / "remaining-source-register.json")
        cls.scopes = load(SHARED / "remaining-service-scopes.json")
        cls.relations = load(SHARED / "remaining-service-relations.json")

    def test_every_remaining_service_has_one_shared_notice_scope_and_relation(self):
        scope_rows = {row["service_id"]: row for row in self.scopes["services"]}
        relation_rows = {row["service_id"]: row for row in self.relations["relations"]}
        self.assertEqual(set(scope_rows), EXPECTED_SERVICES)
        self.assertEqual(set(relation_rows), EXPECTED_SERVICES)

        known_sources = {row["source_id"] for row in self.source_register["sources"]}
        for service_id in EXPECTED_SERVICES:
            with self.subTest(service_id=service_id):
                scope = scope_rows[service_id]
                relation = relation_rows[service_id]
                self.assertEqual(scope["source_ids"], relation["source_ids"])
                self.assertTrue(set(scope["source_ids"]) <= known_sources)
                self.assertEqual(scope["scope_state"], "SCOPE_DEFINED_NOTICE_LOCATOR_ONLY")
                expected_class = (
                    "COMMON_NOTICE_SHARED_BY_MULTIPLE_SERVICES"
                    if "rouki33" in scope["document_ids"]
                    else "SERVICE_SPECIFIC_NOTICE_IDENTIFIED_CURRENTNESS_UNCONFIRMED"
                )
                self.assertEqual(scope["discovery_classification"], expected_class)
                self.assertEqual(scope["notice_text_currentness"], "NOT_ESTABLISHED")
                self.assertTrue(scope["source_locators"])
                self.assertEqual(relation["relation_state"], "MAPPED_SOURCE_HEADING_ONLY")
                self.assertEqual(relation["applicability_verification"], "SOURCE_HEADING_MATCHED")

                config = load(ROOT / f"data/services/{service_id}.json")
                scope_path = "data/shared/standards-interpretation/remaining-service-scopes.json"
                relation_path = "data/shared/standards-interpretation/remaining-service-relations.json"
                self.assertEqual(config["scope_files"]["standards_interpretation"], scope_path)
                layer = config["ingestion_layers"]["standards_interpretation"]
                self.assertEqual(layer["service_scope"], scope_path)
                self.assertEqual(layer["relation_file"], relation_path)
                self.assertEqual(layer["item_body_verification"], "NOT_ESTABLISHED")
                self.assertEqual(layer["currentness"], "NOT_ESTABLISHED")
                self.assertEqual(layer["human_review"], "NOT_REVIEWED")
                self.assertEqual(layer["publication"], "NOT_ESTABLISHED")
                self.assertEqual(layer["route_exposure"], "BLOCKED")

    def test_source_registry_has_shared_notice_families_without_body_copies(self):
        sources = self.source_register["sources"]
        source_ids = [row["source_id"] for row in sources]
        self.assertEqual(len(source_ids), len(set(source_ids)))
        self.assertFalse(self.source_register["policy"]["service_body_duplication_allowed"])
        self.assertFalse(self.source_register["policy"]["amendment_comparison_as_integrated_current_text_allowed"])
        for row in sources:
            with self.subTest(source_id=row["source_id"]):
                self.assertIn("mhlw.go.jp", row["url"])
                self.assertFalse(row["current_integrated_text"])
                self.assertEqual(row["acquisition_state"], "OFFICIAL_SOURCE_LOCATED_NOT_SNAPSHOTTED")

    def test_coverage_projection_reports_shared_corpus_without_promoting_other_states(self):
        from scripts.build_database_coverage_matrix import build

        matrix = build()
        self.assertIn("data/shared/standards-interpretation/remaining-source-register.json", matrix["canonical_inputs"])
        rows = {row["service_id"]: row for row in matrix["services"]}
        for service_id in EXPECTED_SERVICES:
            family = next(
                row for row in rows[service_id]["source_families"]
                if row["source_family"] == "standards_interpretation_notice"
            )
            with self.subTest(service_id=service_id):
                self.assertEqual(family["corpus_availability"]["kind"], "SHARED")
                self.assertEqual(family["corpus_availability"]["state"], "AVAILABLE")
                self.assertEqual(family["service_scope"]["state"], "SCOPE_DEFINED")
                self.assertEqual(family["ingestion"]["state"], "INGESTED")
                self.assertEqual(family["item_body_verification"]["state"], "NOT_ESTABLISHED")
                self.assertEqual(family["currentness"]["state"], "NOT_ESTABLISHED")
                self.assertEqual(family["relation_verification"]["state"], "NOT_ESTABLISHED")
                self.assertEqual(family["human_review"]["state"], "NOT_REVIEWED")
                self.assertEqual(family["publication"]["state"], "BLOCKED")
                self.assertEqual(family["route_exposure"]["state"], "BLOCKED")

    def test_shared_scopes_do_not_overwrite_existing_community_dayservice_scope(self):
        existing = load(ROOT / "data/services/community-dayservice.json")
        self.assertEqual(
            existing["scope_files"]["standards_interpretation"],
            "data/services/community-dayservice/standards-interpretation-scope.json",
        )
        self.assertNotIn(
            "community-dayservice",
            {row["service_id"] for row in self.scopes["services"]},
        )


if __name__ == "__main__":
    unittest.main()
