import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"


def load(relative):
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


class SharedCareInsuranceActCorpusTest(unittest.TestCase):
    def test_shared_corpus_scope_is_explicit_and_bounded(self):
        scope = load("data/care-insurance-act-corpus-scope.json")
        self.assertEqual(scope["scope_kind"], "SHARED_SOURCE_CORPUS")
        self.assertFalse(scope["automatic_verification_promotion_allowed"])
        self.assertGreaterEqual(len(scope["selection_groups"]), 5)
        self.assertTrue(scope["deliberately_not_selected"])
        self.assertFalse(
            scope["service_applicability"]["corpus_presence_implies_applicability"]
        )
        self.assertFalse(
            scope["service_applicability"]["corpus_verification_implies_service_verification"]
        )

    def test_generated_meta_points_to_shared_corpus_scope(self):
        meta = load("data/care-insurance-act-meta.json")
        self.assertEqual(meta["scope"]["kind"], "SHARED_SOURCE_CORPUS")
        self.assertEqual(
            meta["scope"]["scope_file"],
            "data/care-insurance-act-corpus-scope.json",
        )
        self.assertFalse(meta["automatic_verification_promotion_allowed"])
        self.assertGreater(meta["counts"]["articles_total"], 11)

    def test_existing_ids_survive_and_new_shared_boundaries_are_present(self):
        nodes = load("data/care-insurance-act-nodes.json")
        ids = [row["id"] for row in nodes]
        self.assertEqual(len(ids), len(set(ids)))

        id_set = set(ids)
        legacy_roots = {
            "careact.article.8",
            "careact.article.41",
            "careact.article.70",
            "careact.article.70-2",
            "careact.article.73",
            "careact.article.74",
            "careact.article.75",
            "careact.article.76",
            "careact.article.76-2",
            "careact.article.77",
            "careact.article.78",
        }
        self.assertTrue(legacy_roots <= id_set)

        shared_boundary_roots = {
            "careact.article.1",
            "careact.article.8-2",
            "careact.article.18",
            "careact.article.26",
            "careact.article.40",
            "careact.article.61-4",
            "careact.article.69-2",
            "careact.article.115-44",
            "careact.article.115-45",
            "careact.article.115-49",
        }
        self.assertTrue(shared_boundary_roots <= id_set)

    def test_source_nodes_do_not_assert_service_applicability(self):
        nodes = load("data/care-insurance-act-nodes.json")
        self.assertTrue(nodes)
        for row in nodes:
            self.assertEqual(row.get("service_scope"), "SHARED_CORPUS")
            self.assertEqual(
                row.get("source_scope_id"),
                "care-insurance-act.shared-service-foundation",
            )
            self.assertNotIn("service_id", row)

    def test_contains_relations_are_source_structure_only(self):
        nodes = load("data/care-insurance-act-nodes.json")
        node_ids = {row["id"] for row in nodes}
        relations = load("data/care-insurance-act-relations.json")

        contains = [row for row in relations if row.get("relation") == "contains"]
        self.assertTrue(contains)
        for row in contains:
            self.assertIn(row["from"], node_ids)
            self.assertIn(row["to"], node_ids)
            self.assertEqual(row.get("relation_scope"), "SOURCE_STRUCTURE")
            self.assertNotIn("service_id", row)

        semantic = [row for row in relations if row.get("relation") != "contains"]
        self.assertTrue(semantic)
        for row in semantic:
            self.assertIn(
                row.get("relation_scope"),
                {"SERVICE_SPECIFIC", "SHARED_DESIGNATED_HOME_SERVICE_STRUCTURE"},
            )
            if row.get("relation_scope") == "SERVICE_SPECIFIC":
                self.assertEqual(row.get("service_id"), "dayservice")
            else:
                self.assertNotIn("service_id", row)

    def test_existing_service_scopes_reference_shared_text_without_copying_it(self):
        nodes = load("data/care-insurance-act-nodes.json")
        node_ids = {row["id"] for row in nodes}

        dayservice = load("data/care-insurance-act-scope.json")
        for article in dayservice["articles"]:
            self.assertIn(f"careact.article.{article}", node_ids)

        homevisit = load(
            "data/services/homevisit/care-insurance-act-index.generated.json"
        )
        self.assertFalse(homevisit["assurance"]["legal_text_duplicated"])
        self.assertFalse(
            homevisit["assurance"]["automatic_verification_promotion_allowed"]
        )
        for node_id in homevisit["node_ids"]["all"]:
            self.assertIn(node_id, node_ids)

    def test_independent_receipt_does_not_promote_service_state(self):
        receipt = load("data/egov-content-independent-audit.json")
        self.assertEqual(receipt["audit_result"], "PASS")
        self.assertFalse(receipt["safety"]["human_verified"])
        self.assertFalse(receipt["safety"]["verified_current"])
        self.assertFalse(receipt["safety"]["service_applicability_verified"])
        self.assertFalse(receipt["safety"]["automatic_promotion_allowed"])


if __name__ == "__main__":
    unittest.main()
