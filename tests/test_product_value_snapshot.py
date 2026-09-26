import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "build_product_value_snapshot.py"
OUTPUT = ROOT / "data" / "product-value-snapshot-v0.1.json"


def load_builder():
    spec = importlib.util.spec_from_file_location("product_value_snapshot", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


class ProductValueSnapshotTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.builder = load_builder()
        cls.snapshot = cls.builder.build_snapshot()
        cls.committed = json.loads(OUTPUT.read_text(encoding="utf-8"))

    def test_committed_snapshot_is_reproducible(self):
        self.assertEqual(self.snapshot, self.committed)

    def test_public_family_counts_reconcile(self):
        metric = self.snapshot["metrics"]["public_items_with_complete_evidence_state"]
        breakdown_total = sum(
            family["items_total"] for family in metric["breakdown"].values()
        )
        breakdown_complete = sum(
            family["items_complete"] for family in metric["breakdown"].values()
        )
        self.assertEqual(breakdown_total, metric["public_items_total"])
        self.assertEqual(breakdown_complete, metric["public_items_complete"])

    def test_enabled_public_item_families_are_all_counted(self):
        metric = self.snapshot["metrics"]["public_items_with_complete_evidence_state"]
        self.assertEqual(metric["public_items_total"], 1438)
        self.assertEqual(
            set(metric["breakdown"]),
            set(self.builder.EXPECTED_PUBLIC_FAMILIES),
        )
        self.assertEqual(
            metric["breakdown"]["care_insurance_act_articles"]["items_total"],
            11,
        )
        self.assertEqual(
            metric["breakdown"]["fee_guidance_items"]["items_total"],
            29,
        )
        self.assertEqual(
            metric["breakdown"]["unit_price_records"]["items_total"],
            435,
        )

    def test_canonical_scope_export_preserves_article8_focus_boundary(self):
        scoped = self.builder.load_canonical_service_scope("dayservice")
        node_ids = set(scoped["care_insurance_act"]["node_ids"])
        self.assertIn("careact.article.8.p.7", node_ids)
        self.assertNotIn("careact.article.8.p.2", node_ids)
        self.assertEqual(scoped["contract"], "lib/service-scope.ts")

    def test_unpublished_service_is_excluded(self):
        self.assertEqual(self.snapshot["service_id"], "dayservice")
        self.assertIn("homevisit", self.snapshot["scope"]["excluded_services"])

    def test_relation_counts_reconcile(self):
        metric = self.snapshot["metrics"]["unresolved_or_unverified_relations"]
        self.assertEqual(
            metric["relations_independently_verified"]
            + metric["relations_remaining_unverified"],
            metric["relations_total"],
        )

    def test_human_effectiveness_is_not_claimed(self):
        excluded = set(self.snapshot["claims_excluded"])
        self.assertIn("human task-time improvement", excluded)
        self.assertIn("human effectiveness improvement", excluded)


if __name__ == "__main__":
    unittest.main()
