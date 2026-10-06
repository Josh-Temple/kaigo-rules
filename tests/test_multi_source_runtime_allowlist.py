from __future__ import annotations

import copy
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "build_bounded_publication_allowlist.py"

spec = importlib.util.spec_from_file_location(
    "build_bounded_publication_allowlist", MODULE_PATH
)
builder = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(builder)


class MultiSourceRuntimeAllowlistTest(unittest.TestCase):
    def test_builder_preserves_twenty_governing_cells_and_adds_dayservice_unit_price(self):
        artifact = builder.build()
        cells = {
            (row["service_id"], row["source_family"])
            for row in artifact["publication_cell_allowlist"]
        }
        governing = {
            cell
            for cell in cells
            if cell[1] == "governing_standards_ordinance"
        }

        self.assertEqual(len(governing), 20)
        self.assertIn(
            ("dayservice", "unit_price_regional_classification"),
            cells,
        )
        self.assertEqual(len(cells), 21)
        self.assertEqual(
            set(artifact["runtime_binding"]["supported_source_families"]),
            {
                "governing_standards_ordinance",
                "unit_price_regional_classification",
            },
        )
        self.assertEqual(
            set(artifact["runtime_binding"]["supported_source_identities"]),
            {
                "ordinance37",
                "preventive-services-standards",
                "mhlw-unit-price-current",
            },
        )

    def test_unit_price_contract_fails_closed_on_identity_and_scope_drift(self):
        payload = json.loads(
            (
                ROOT
                / "data"
                / "verification"
                / "high-value-currentness-closure-worker-b.json"
            ).read_text(encoding="utf-8")
        )
        promotion = payload["promotions"][0]
        self.assertTrue(builder.source_contract_supported(promotion))

        unsupported_identity = copy.deepcopy(promotion)
        unsupported_identity["source_identity"]["canonical_source_id"] = (
            "unsupported-source"
        )
        self.assertFalse(
            builder.source_contract_supported(unsupported_identity)
        )

        wrong_profile = copy.deepcopy(promotion)
        wrong_profile["applicability_proof"]["multiplier_profile_id"] = (
            "group-1140"
        )
        self.assertFalse(builder.source_contract_supported(wrong_profile))

        wrong_service = copy.deepcopy(promotion)
        wrong_service["service_id"] = "homevisit"
        self.assertFalse(builder.source_contract_supported(wrong_service))

        missing_currentness = copy.deepcopy(promotion)
        missing_currentness["projected_currentness_state"] = (
            "NOT_ESTABLISHED"
        )
        self.assertFalse(
            builder.source_contract_supported(missing_currentness)
        )

    def test_safe_fields_exclude_relation_and_human_review_state(self):
        artifact = builder.build()
        key = "dayservice|unit_price_regional_classification"
        self.assertEqual(
            set(artifact["field_allowlist_by_cell"][key]),
            {
                "source_text",
                "item_body",
                "source_metadata",
                "source_locator",
                "currentness_statement",
                "service_applicability_statement",
            },
        )
        serialized = json.dumps(
            artifact["field_allowlist_by_cell"][key],
            ensure_ascii=False,
        )
        self.assertNotIn("relation_verification", serialized)
        self.assertNotIn("human_review", serialized)


if __name__ == "__main__":
    unittest.main()
