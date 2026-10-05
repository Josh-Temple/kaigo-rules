import copy
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SHARED = ROOT / "data" / "shared" / "remuneration-delegated"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


SPEC = importlib.util.spec_from_file_location(
    "delegated_builder",
    ROOT / "scripts" / "build_delegated_remuneration_shared_corpus.py",
)
BUILDER = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(BUILDER)


class DelegatedRemunerationItemBodyAssuranceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.receipt = load(SHARED / "item-body-verification.json")
        cls.corpus = load(SHARED / "national-corpus.json")
        cls.applicability = load(SHARED / "service-applicability.json")
        cls.relations = load(SHARED / "service-relations.json")
        cls.node_by_id = {
            row["canonical_node_id"]: row for row in cls.corpus["nodes"]
        }

    def test_source_level_receipt_covers_entire_canonical_corpus(self):
        passed = {
            row["source_id"]: row
            for row in self.receipt["source_verifications"]
            if row["result"] == "PASS"
        }
        self.assertEqual(
            set(passed),
            {row["source_id"] for row in self.corpus["nodes"]},
        )
        self.assertEqual(
            sum(row["canonical_node_count"] for row in passed.values()),
            len(self.corpus["nodes"]),
        )
        self.assertEqual(len(self.corpus["nodes"]), 497)

    def test_mapped_services_project_item_body_only(self):
        mapped = [
            row for row in self.applicability["services"]
            if row["applicability_state"] == "MAPPED"
        ]
        self.assertEqual(len(mapped), 37)
        for row in mapped:
            assurance = row["assurance"]
            required = len(row["mapped_node_ids"]) + len(row["compatibility_subnode_ids"])
            self.assertEqual(assurance["item_body_verification"], "PASS")
            self.assertEqual(assurance["item_body_verified_node_count"], required)
            self.assertEqual(assurance["currentness"], "NOT_ESTABLISHED")
            self.assertEqual(assurance["relation_verification"], "NOT_ESTABLISHED")
            self.assertEqual(assurance["human_review"], "NOT_REVIEWED")
            self.assertEqual(assurance["publication"], "BLOCKED")
            self.assertEqual(assurance["route_exposure"], "BLOCKED")
            self.assertFalse(assurance["automatic_promotion_allowed"])

    def test_not_applicable_services_are_not_promoted(self):
        rows = {
            row["service_id"]: row for row in self.applicability["services"]
            if row["applicability_state"] == "NOT_APPLICABLE"
        }
        self.assertEqual(
            set(rows),
            {"specific-welfare-equipment-sale", "specific-preventive-welfare-equipment-sale"},
        )
        for row in rows.values():
            self.assertEqual(row["assurance"]["item_body_verification"], "NOT_ESTABLISHED")
            self.assertEqual(row["ingestion_state"], "NOT_APPLICABLE")

    def test_projection_fails_closed_when_one_source_loses_pass(self):
        dayservice = next(
            row for row in self.applicability["services"]
            if row["service_id"] == "dayservice"
        )
        receipt = copy.deepcopy(self.receipt)
        for source in receipt["source_verifications"]:
            if source["source_id"] == "mhlw-fee-criteria95-current":
                source["result"] = "NOT_ESTABLISHED"
        assurance = BUILDER.item_body_assurance_for_service(
            applicability_state="MAPPED",
            mapped_node_ids=dayservice["mapped_node_ids"],
            compatibility_subnode_ids=dayservice["compatibility_subnode_ids"],
            national_by_id=self.node_by_id,
            item_body_doc=receipt,
        )
        self.assertEqual(assurance["item_body_verification"], "NOT_ESTABLISHED")
        self.assertTrue(assurance.get("item_body_projection_blockers"))

    def test_projection_fails_closed_when_compatibility_body_is_unverified(self):
        dayservice = next(
            row for row in self.applicability["services"]
            if row["service_id"] == "dayservice"
        )
        receipt = copy.deepcopy(self.receipt)
        receipt["compatibility_node_verifications"][0]["result"] = "NOT_ESTABLISHED"
        assurance = BUILDER.item_body_assurance_for_service(
            applicability_state="MAPPED",
            mapped_node_ids=dayservice["mapped_node_ids"],
            compatibility_subnode_ids=dayservice["compatibility_subnode_ids"],
            national_by_id=self.node_by_id,
            item_body_doc=receipt,
        )
        self.assertEqual(assurance["item_body_verification"], "NOT_ESTABLISHED")

    def test_relation_axis_remains_separate(self):
        rows = {row["service_id"]: row for row in self.relations["services"]}
        for service in self.applicability["services"]:
            relation = rows[service["service_id"]]
            if service["applicability_state"] == "MAPPED":
                self.assertEqual(relation["relation_verification_state"], "NOT_ESTABLISHED")
            else:
                self.assertEqual(relation["relation_verification_state"], "NOT_APPLICABLE")


if __name__ == "__main__":
    unittest.main()
