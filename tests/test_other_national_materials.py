from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import validate_other_national_materials as validator


class OtherNationalMaterialsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base = ROOT / "data/shared/other-national-materials"
        cls.manifest = json.loads((cls.base / "manifest.json").read_text(encoding="utf-8"))
        cls.registry = json.loads((cls.base / "source-registry.json").read_text(encoding="utf-8"))
        cls.corpus = json.loads((cls.base / "national-corpus.json").read_text(encoding="utf-8"))
        cls.identity_map = json.loads((cls.base / "source-identity-map.json").read_text(encoding="utf-8"))
        cls.applicability = json.loads((cls.base / "service-applicability.json").read_text(encoding="utf-8"))
        cls.receipts = json.loads((cls.base / "source-observation-receipts.json").read_text(encoding="utf-8"))
        cls.service_manifest = json.loads((ROOT / "data/services/manifest.json").read_text(encoding="utf-8"))

    def test_validator_passes(self):
        self.assertEqual(validator.validate(), [])

    def test_only_accepted_candidates_are_canonicalized(self):
        accepted = {
            row["candidate_id"]
            for row in self.registry["sources"]
            if row["classification"] == "ACCEPTED_OTHER_NATIONAL_MATERIAL"
        }
        canonical = {row["candidate_id"] for row in self.corpus["sources"]}
        identities = {row["candidate_id"] for row in self.identity_map["identities"]}
        receipts = {row["candidate_id"] for row in self.receipts["receipts"]}
        self.assertEqual(canonical, accepted)
        self.assertEqual(identities, accepted)
        self.assertEqual(receipts, accepted)
        self.assertEqual(len(accepted), 4)

    def test_canonical_corpus_does_not_duplicate_source_bodies(self):
        for row in self.corpus["sources"]:
            self.assertFalse(row["body_duplicated"])
            self.assertEqual(row["content_mode"], "REFERENCE_ONLY")
            self.assertEqual(row["assurance"]["item_body_verification"], "NOT_ESTABLISHED")
            self.assertEqual(row["assurance"]["human_review"], "NOT_REVIEWED")
            self.assertEqual(row["assurance"]["publication"], "BLOCKED")
            self.assertEqual(row["assurance"]["route_exposure"], "BLOCKED")

    def test_application_forms_scope_is_primary_source_explicit_not_nationwide_inference(self):
        services = {row["service_id"] for row in self.service_manifest["services"]}
        forms = next(
            row for row in self.applicability["sources"]
            if row["canonical_source_id"] == "mhlw-application-forms"
        )
        self.assertEqual(forms["state"], "MAPPED_PRIMARY_SOURCE")
        self.assertEqual(set(forms["mapped_service_ids"]), services)
        self.assertEqual(forms["verification"], "PRIMARY_SOURCE_EXPLICIT_LIST")
        self.assertIn("explicitly enumerate", forms["note"])

    def test_electronic_application_manual_scope_stays_unestablished(self):
        row = next(
            row for row in self.applicability["sources"]
            if row["canonical_source_id"] == "mhlw-electronic-application-operator-manual-v2-50"
        )
        self.assertEqual(row["state"], "NOT_ESTABLISHED")
        self.assertEqual(row["mapped_service_ids"], [])

    def test_accident_report_keeps_recommended_broader_use_out_of_exact_mapping(self):
        row = next(
            row for row in self.applicability["sources"]
            if row["canonical_source_id"] == "mhlw-accident-report-vol1332"
        )
        self.assertEqual(row["state"], "PARTIAL_EXPLICIT_TARGET")
        self.assertEqual(
            set(row["mapped_service_ids"]),
            {
                "elderly-welfare-facility",
                "elderly-health-facility",
                "care-medical-institution",
                "dementia-group-home",
                "preventive-dementia-group-home",
                "specific-facility",
                "community-specific-facility",
                "preventive-specific-facility",
            },
        )
        self.assertIn("possible", row["note"])

    def test_financial_db_scope_partitions_direct_conditional_and_excluded_services(self):
        services = {row["service_id"] for row in self.service_manifest["services"]}
        row = next(
            row for row in self.applicability["sources"]
            if row["canonical_source_id"] == "mhlw-care-business-financial-db-manual-v1-20"
        )
        mapped = set(row["mapped_service_ids"])
        conditional = {item["service_id"] for item in row["conditional_service_ids"]}
        not_applicable = {item["service_id"] for item in row["not_applicable_service_ids"]}
        self.assertFalse(mapped & conditional)
        self.assertFalse(mapped & not_applicable)
        self.assertFalse(conditional & not_applicable)
        self.assertEqual(mapped | conditional | not_applicable, services)
        self.assertEqual(
            not_applicable,
            {"homecaremanagement", "preventive-homecaremanagement", "preventive-support"},
        )

    def test_locator_evidence_never_invents_source_byte_hashes(self):
        for row in self.receipts["receipts"]:
            self.assertIsNone(row["source_bytes_sha256"])
            self.assertEqual(row["source_bytes_state"], "NOT_CAPTURED_IN_THIS_WORKER")
            self.assertIn(row["currentness"]["state"], {"PARTIAL", "NOT_ESTABLISHED"})
            self.assertTrue(row["official_landing_url"])
            self.assertTrue(row["native_locator"])

    def test_life_and_existing_family_duplicates_are_not_promoted(self):
        canonical_candidates = {row["candidate_id"] for row in self.corpus["sources"]}
        blocked = {
            row["candidate_id"]
            for row in self.registry["sources"]
            if row["classification"] != "ACCEPTED_OTHER_NATIONAL_MATERIAL"
        }
        self.assertTrue(canonical_candidates.isdisjoint(blocked))
        self.assertNotIn("mhlw-life-manual-guidance", canonical_candidates)


if __name__ == "__main__":
    unittest.main()
