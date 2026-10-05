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
        self.assertGreaterEqual(row["mapped_node_count"], 18)
        self.assertEqual(
            row["compatibility_subnode_ids"],
            ["notice27.item.1.capacity", "notice27.item.1.staffing"],
        )
        assurance = row["assurance"]
        self.assertEqual(assurance["item_body_verification"], "PASS")
        self.assertEqual(
            assurance["item_body_verified_node_count"],
            row["mapped_node_count"] + len(row["compatibility_subnode_ids"]),
        )
        self.assertIn(
            "data/shared/remuneration-delegated/item-body-verification.json",
            assurance["item_body_projection_evidence"],
        )
        self.assertEqual(assurance["currentness"], "NOT_ESTABLISHED")
        self.assertEqual(assurance["relation_verification"], "NOT_ESTABLISHED")
        self.assertEqual(assurance["human_review"], "NOT_REVIEWED")
        self.assertEqual(assurance["publication"], "BLOCKED")
        self.assertEqual(assurance["route_exposure"], "BLOCKED")
        self.assertFalse(assurance["automatic_promotion_allowed"])

    def test_heading_mapping_and_evidence_based_adjudications_cover_remaining_services(self):
        applicability = {
            row["service_id"]: row
            for row in self.outputs["service-applicability.json"]["services"]
        }
        self.assertEqual(len(applicability), len(shared.SERVICE_HEADING_TERMS))
        self.assertEqual(
            {key for key, row in applicability.items() if row["applicability_state"] == "UNKNOWN"},
            set(),
        )
        residual_expected = {
            "homecaremanagement": "notice96.item.4-4",
            "preventive-homecaremanagement": "notice96.item.71-2",
            "preventive-welfare-equipment-rental": "notice95.item.121-3-2",
        }
        for service_id, expected_node_id in residual_expected.items():
            row = applicability[service_id]
            self.assertEqual(row["applicability_state"], "MAPPED")
            self.assertEqual(row["ingestion_state"], "INGESTED")
            self.assertIn(expected_node_id, row["mapped_node_ids"])
        self.assertEqual(
            {key for key, row in applicability.items() if row["applicability_state"] == "NOT_APPLICABLE"},
            {"specific-welfare-equipment-sale", "specific-preventive-welfare-equipment-sale"},
        )
        for service_id, row in applicability.items():
            if row["applicability_state"] in {"UNKNOWN", "NOT_APPLICABLE"}:
                self.assertEqual(row["mapped_node_ids"], [])
                self.assertGreaterEqual(len(row["adjudication"]["official_primary_sources"]), 1)
                self.assertIn("rationale", row["adjudication"])
                self.assertEqual(row["ingestion_state"], "NOT_INGESTED" if row["applicability_state"] == "UNKNOWN" else "NOT_APPLICABLE")

        self.assertIn("notice95.item.84", applicability["care-management"]["mapped_node_ids"])
        self.assertIn("notice95.item.129-4", applicability["preventive-support"]["mapped_node_ids"])
        self.assertIn("notice95.item.44-4", applicability["welfare-equipment-rental"]["mapped_node_ids"])
        for row in applicability.values():
            assurance = row["assurance"]
            if row["applicability_state"] == "MAPPED":
                self.assertEqual(assurance["item_body_verification"], "PASS")
                self.assertEqual(
                    assurance["item_body_verified_node_count"],
                    row["mapped_node_count"] + len(row["compatibility_subnode_ids"]),
                )
                self.assertIn(
                    "data/shared/remuneration-delegated/item-body-verification.json",
                    assurance["item_body_projection_evidence"],
                )
            else:
                self.assertEqual(assurance["item_body_verification"], "NOT_ESTABLISHED")
            self.assertEqual(assurance["currentness"], "NOT_ESTABLISHED")
            self.assertEqual(assurance["relation_verification"], "NOT_ESTABLISHED")
            self.assertEqual(assurance["human_review"], "NOT_REVIEWED")
            self.assertEqual(assurance["publication"], "BLOCKED")
            self.assertEqual(assurance["route_exposure"], "BLOCKED")
            self.assertFalse(assurance["automatic_promotion_allowed"])

    def test_purchase_benefit_exclusions_are_tied_to_canonical_act_articles(self):
        act_nodes = {
            row["id"]: row
            for row in json.loads((ROOT / "data/care-insurance-act-nodes.json").read_text(encoding="utf-8"))
        }
        self.assertIn("特定福祉用具の購入に要した費用を除き", act_nodes["careact.article.41"]["official_text"])
        self.assertIn("特定福祉用具販売", act_nodes["careact.article.44"]["official_text"])
        self.assertIn("特定介護予防福祉用具販売", act_nodes["careact.article.56"]["official_text"])

    def test_service_relation_mapping_never_duplicates_source_text(self):
        relation_doc = self.outputs["service-relations.json"]
        self.assertEqual(len(relation_doc["services"]), 39)
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
        self.assertEqual(
            {row["service_id"] for row in relation_doc["services"] if row.get("applicability_state") == "UNKNOWN"},
            set(),
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
