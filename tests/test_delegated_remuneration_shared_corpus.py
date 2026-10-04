from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_delegated_remuneration_shared_corpus as shared


class DelegatedRemunerationSharedCorpusTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.outputs = shared.build()
        cls.legacy_nodes = json.loads(
            (ROOT / "data/remuneration-delegated-nodes.json").read_text(encoding="utf-8")
        )

    def test_shared_projection_is_current(self):
        for name, expected in self.outputs.items():
            actual = json.loads(
                (ROOT / "data/shared/remuneration-delegated" / name).read_text(encoding="utf-8")
            )
            self.assertEqual(actual, expected, name)

    def test_single_text_bearing_store_preserves_backward_compatibility(self):
        manifest = self.outputs["manifest.json"]
        self.assertEqual(
            manifest["canonical_node_store"],
            "data/shared/remuneration-delegated/national-corpus.json",
        )
        self.assertEqual(
            manifest["legacy_compatibility"]["legacy_text_store"],
            "data/remuneration-delegated-nodes.json",
        )
        self.assertTrue(manifest["legacy_compatibility"]["node_ids_preserved"])
        self.assertFalse(
            manifest["legacy_compatibility"]["legacy_service_scope_field_authoritative"]
        )
        for name in (
            "node-identity-map.json",
            "service-applicability.json",
            "service-relations.json",
        ):
            self.assertNotIn(
                "official_text",
                json.dumps(self.outputs[name], ensure_ascii=False),
                name,
            )

    def test_every_legacy_node_has_one_service_neutral_identity(self):
        identity = self.outputs["node-identity-map.json"]["nodes"]
        self.assertEqual(len(identity), len(self.legacy_nodes))
        self.assertEqual(
            len({row["legacy_node_id"] for row in identity}),
            len(self.legacy_nodes),
        )
        self.assertEqual(
            len({row["canonical_node_id"] for row in identity}),
            len(self.legacy_nodes),
        )
        self.assertTrue(
            all(".dayservice." not in row["canonical_node_id"] for row in identity)
        )

    def test_dayservice_mapping_is_ingested_but_assurance_stays_fail_closed(self):
        row = self.outputs["service-applicability.json"]["services"][0]
        self.assertEqual(row["service_id"], "dayservice")
        self.assertEqual(row["applicability_state"], "MAPPED")
        self.assertEqual(row["ingestion_state"], "INGESTED")
        self.assertEqual(row["mapped_node_count"], 18)
        self.assertEqual(
            row["compatibility_subnode_ids"],
            ["notice27.item.1.capacity", "notice27.item.1.staffing"],
        )
        assurance = row["assurance"]
        self.assertEqual(assurance["item_body_verification"], "NOT_ESTABLISHED")
        self.assertEqual(assurance["currentness"], "NOT_ESTABLISHED")
        self.assertEqual(assurance["relation_verification"], "NOT_ESTABLISHED")
        self.assertEqual(assurance["human_review"], "NOT_REVIEWED")
        self.assertEqual(assurance["publication"], "BLOCKED")
        self.assertEqual(assurance["route_exposure"], "BLOCKED")
        self.assertFalse(assurance["automatic_promotion_allowed"])

    def test_heading_based_applicability_expands_but_unmatched_services_stay_unmapped(self):
        applicability = {
            row["service_id"]: row
            for row in self.outputs["service-applicability.json"]["services"]
        }
        self.assertEqual(len(applicability), 34)
        self.assertEqual(
            {
                "homecaremanagement",
                "specific-welfare-equipment-sale",
                "preventive-homecaremanagement",
                "preventive-welfare-equipment-rental",
                "specific-preventive-welfare-equipment-sale",
            },
            set(shared.SERVICE_HEADING_TERMS) - set(applicability),
        )

        self.assertIn("notice95.item.84", applicability["care-management"]["mapped_node_ids"])
        self.assertIn("notice95.item.129-4", applicability["preventive-support"]["mapped_node_ids"])
        self.assertIn("notice95.item.44-4", applicability["welfare-equipment-rental"]["mapped_node_ids"])

        for row in applicability.values():
            assurance = row["assurance"]
            self.assertEqual(assurance["item_body_verification"], "NOT_ESTABLISHED")
            self.assertEqual(assurance["currentness"], "NOT_ESTABLISHED")
            self.assertEqual(assurance["relation_verification"], "NOT_ESTABLISHED")
            self.assertEqual(assurance["human_review"], "NOT_REVIEWED")
            self.assertEqual(assurance["publication"], "BLOCKED")
            self.assertEqual(assurance["route_exposure"], "BLOCKED")
            self.assertFalse(assurance["automatic_promotion_allowed"])

    def test_service_relation_mapping_never_duplicates_source_text(self):
        relation_doc = self.outputs["service-relations.json"]
        self.assertEqual(len(relation_doc["services"]), 34)
        relation_rows = [
            relation
            for service in relation_doc["services"]
            for relation in service["relations"]
        ]
        self.assertTrue(relation_rows)
        self.assertTrue(
            all(relation["verification_state"] == "NOT_ESTABLISHED" for relation in relation_rows)
        )
        self.assertNotIn(
            "official_text",
            json.dumps(relation_doc, ensure_ascii=False),
        )

    def test_verified_delegation_edges_do_not_promote_service_relations(self):
        row = self.outputs["service-relations.json"]["services"][0]
        self.assertEqual(row["relation_verification_state"], "NOT_ESTABLISHED")
        self.assertTrue(
            any(
                relation["independently_verified_delegation_edge_ids"]
                for relation in row["relations"]
            )
        )
        self.assertTrue(
            all(
                relation["verification_state"] == "NOT_ESTABLISHED"
                for relation in row["relations"]
            )
        )


if __name__ == "__main__":
    unittest.main()
