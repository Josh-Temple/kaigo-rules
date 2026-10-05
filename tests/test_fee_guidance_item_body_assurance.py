import importlib.util
import json
import shutil
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "fee_guidance_item_body_assurance",
    ROOT / "scripts/validate_fee_guidance_item_body_assurance.py",
)
validator = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(validator)


class FeeGuidanceItemBodyAssuranceTest(unittest.TestCase):
    def test_assurance_inventory_is_fail_closed(self):
        result = validator.validate()
        self.assertEqual(result["services"], 39)
        self.assertEqual(
            result["evidence_classes"],
            {
                "VERSIONED_BODY_AVAILABLE_NOT_CURRENTNESS_PROOF": 1,
                "COMPARISON_BODY_ONLY": 9,
                "LOCATOR_ONLY": 27,
                "NOT_APPLICABLE": 2,
            },
        )
        self.assertEqual(
            result["item_body_states"],
            {"PARTIAL": 1, "NOT_ESTABLISHED": 36, "NOT_APPLICABLE": 2},
        )
        self.assertEqual(result["verified_nodes"], 8)

    def test_r8_bounded_amendment_evidence_does_not_promote_full_section(self):
        data = json.loads(
            (ROOT / "data/shared/fee-guidance/item-body-assurance.json").read_text(encoding="utf-8")
        )
        rows = {row["service_id"]: row for row in data["service_projections"]}
        for service_id in (
            "homenursing",
            "homerehab",
            "care-management",
            "preventive-homenursing",
            "preventive-homerehab",
            "preventive-support",
        ):
            row = rows[service_id]
            self.assertEqual(row["evidence_class"], "COMPARISON_BODY_ONLY")
            self.assertEqual(row["service_level_item_body"], "NOT_ESTABLISHED")
            self.assertEqual(row["verified_node_count"], 0)
            self.assertFalse(row["projection_to_pass_permitted"])
            evidence = row["bounded_direct_amendment_evidence"]
            self.assertTrue(evidence["verified_item_range_only"])
            self.assertFalse(evidence["full_scoped_node_verified"])
            self.assertFalse(evidence["current_integrated_body_established"])
            self.assertFalse(evidence["currentness_established"])

    def test_comparison_only_cannot_be_promoted_to_pass(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            shutil.copytree(ROOT / "data", root / "data")
            target = root / "data/shared/fee-guidance/item-body-assurance.json"
            data = json.loads(target.read_text(encoding="utf-8"))
            row = next(x for x in data["service_projections"] if x["service_id"] == "homevisit")
            row["service_level_item_body"] = "PASS"
            row["projection_to_pass_permitted"] = True
            target.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
            with self.assertRaises(AssertionError):
                validator.validate(root)

    def test_dayservice_is_partial_and_dayrehab_is_not_item_body_pass(self):
        data = json.loads(
            (ROOT / "data/shared/fee-guidance/item-body-assurance.json").read_text(encoding="utf-8")
        )
        rows = {row["service_id"]: row for row in data["service_projections"]}
        self.assertEqual(rows["dayservice"]["service_level_item_body"], "PARTIAL")
        self.assertEqual(rows["dayservice"]["verified_node_count"], 8)
        self.assertEqual(rows["dayservice"]["scoped_node_count"], 29)
        self.assertEqual(rows["dayrehab"]["service_level_item_body"], "NOT_ESTABLISHED")
        self.assertEqual(rows["dayrehab"]["verified_node_count"], 0)
        self.assertEqual(rows["specific-welfare-equipment-sale"]["service_level_item_body"], "NOT_APPLICABLE")
        self.assertEqual(rows["specific-preventive-welfare-equipment-sale"]["service_level_item_body"], "NOT_APPLICABLE")

    def test_coverage_projection_uses_service_level_assurance(self):
        builder_spec = importlib.util.spec_from_file_location(
            "coverage_matrix",
            ROOT / "scripts/build_database_coverage_matrix.py",
        )
        builder = importlib.util.module_from_spec(builder_spec)
        assert builder_spec.loader is not None
        builder_spec.loader.exec_module(builder)
        matrix = builder.build()
        rows = {
            row["service_id"]: next(
                family for family in row["source_families"]
                if family["source_family"] == "fee_calculation_guidance"
            )
            for row in matrix["services"]
        }
        self.assertEqual(rows["dayservice"]["item_body_verification"]["state"], "PARTIAL")
        self.assertEqual(rows["dayrehab"]["item_body_verification"]["state"], "NOT_ESTABLISHED")
        self.assertEqual(
            rows["specific-welfare-equipment-sale"]["item_body_verification"]["state"],
            "NOT_APPLICABLE",
        )
        self.assertEqual(
            rows["specific-preventive-welfare-equipment-sale"]["item_body_verification"]["state"],
            "NOT_APPLICABLE",
        )
        for service_id in ("homevisit", "homebath", "homenursing", "homerehab"):
            self.assertEqual(
                rows[service_id]["item_body_verification"]["state"],
                "NOT_ESTABLISHED",
            )
            self.assertEqual(rows[service_id]["currentness"]["state"], "NOT_ESTABLISHED")
            self.assertEqual(rows[service_id]["human_review"]["state"], "NOT_REVIEWED")
            self.assertEqual(rows[service_id]["publication"]["state"], "BLOCKED")
            self.assertEqual(rows[service_id]["route_exposure"]["state"], "BLOCKED")


if __name__ == "__main__":
    unittest.main()
