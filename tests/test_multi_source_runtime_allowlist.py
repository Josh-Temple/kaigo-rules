from __future__ import annotations

import copy
import importlib.util
import json
import tempfile
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
    def test_builder_publishes_all_supported_ready_governing_and_unit_price_cells(self):
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

        unit_price = {
            cell
            for cell in cells
            if cell[1] == "unit_price_regional_classification"
        }

        self.assertEqual(len(governing), 22)
        self.assertEqual(len(unit_price), 19)
        self.assertIn(
            ("dayservice", "unit_price_regional_classification"),
            cells,
        )
        self.assertEqual(len(cells), 41)
        unit_price_binding = artifact["runtime_source_binding_by_cell"][
            "dayservice|unit_price_regional_classification"
        ]
        self.assertEqual(
            unit_price_binding["promotion"]["source_identity"]["canonical_source_id"],
            "mhlw-unit-price-current",
        )
        self.assertEqual(
            unit_price_binding["promotion"]["applicability_proof"]["multiplier_profile_id"],
            "group-1090",
        )
        self.assertEqual(
            set(artifact["runtime_binding"]["supported_source_families"]),
            {
                "governing_standards_ordinance",
                "unit_price_regional_classification",
                "delegated_remuneration_criteria",
            },
        )
        self.assertEqual(
            set(artifact["runtime_binding"]["supported_source_identities"]),
            {
                "ordinance37",
                "preventive-services-standards",
                "mhlw-unit-price-current",
                "delegated-remuneration-national",
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

    def test_worker_c_shaped_unit_price_promotion_is_supported_without_broadcast(self):
        base = json.loads(
            (
                ROOT
                / "data"
                / "verification"
                / "high-value-currentness-closure-worker-b.json"
            ).read_text(encoding="utf-8")
        )["promotions"][0]
        promotion = {
            "service_id": "homevisit",
            "source_family": "unit_price_regional_classification",
            "canonical_source_identity": {
                "canonical_source_id": "mhlw-unit-price-current",
                "title": base["source_identity"]["title"],
                "official_source_url": base["source_identity"]["official_source_url"],
                "official_page_urls": base["source_identity"]["official_page_urls"],
                "version_id": base["source_identity"]["version_id"],
                "effective_date": "2024-04-01",
                "source_form": "OFFICIAL_CURRENT_CONSOLIDATED_DISPLAY",
                "currentness_class": "CURRENT_OFFICIAL_CONSOLIDATED",
            },
            "service_applicability_evidence": {
                "state": "PASS_DIRECT_SERVICE_SCOPE",
                "official_service_name": "訪問介護",
                "multiplier_profile_id": "group-1140",
                "source_locator": "第一号 表 / 訪問介護 / 地域区分別割合",
                "mapped_item_count": 8,
            },
            "currentness_evidence": {
                "official_source_locator": base["source_identity"]["official_source_url"],
                "observed_on": "2026-10-06",
                "effective_date": "2024-04-01",
                "supersession_check": "OFFICIAL_MHLW_CONSOLIDATED_DISPLAY_REVERIFIED",
                "live_verifier": "scripts/verify_unit_price_currentness.py",
            },
            "allowed_publication_units": [
                "SOURCE_TEXT_ITEM_BODY",
                "SOURCE_METADATA_LOCATOR",
                "CURRENTNESS_STATEMENT",
                "SERVICE_APPLICABILITY_STATEMENT",
            ],
            "ingestion_state": "INGESTED",
            "item_body_state": "PASS",
            "projected_currentness_state": "PASS",
            "promotion_applied": True,
        }

        self.assertTrue(builder.source_contract_supported(promotion))
        normalized = builder.normalize_runtime_promotion(promotion)
        self.assertEqual(
            normalized["source_identity"]["canonical_source_id"],
            "mhlw-unit-price-current",
        )
        self.assertEqual(
            normalized["applicability_proof"]["multiplier_profile_id"],
            "group-1140",
        )
        self.assertTrue(normalized["source_version_contains_scope"])

        wrong_family = copy.deepcopy(promotion)
        wrong_family["source_family"] = "governing_standards_ordinance"
        self.assertFalse(builder.source_contract_supported(wrong_family))

        missing_unit = copy.deepcopy(promotion)
        missing_unit["allowed_publication_units"].remove("CURRENTNESS_STATEMENT")
        self.assertFalse(builder.source_contract_supported(missing_unit))

    def test_delegated_remuneration_contract_binds_exact_worker_b_shape(self):
        applicability = json.loads(
            builder.DELEGATED_APPLICABILITY_PATH.read_text(encoding="utf-8")
        )
        corpus = json.loads(
            builder.DELEGATED_CORPUS_PATH.read_text(encoding="utf-8")
        )
        service = next(
            row
            for row in applicability["services"]
            if row["service_id"] == "homevisit"
        )
        node_by_id = {
            row["canonical_node_id"]: row for row in corpus["nodes"]
        }
        mapped_node_ids = list(service["mapped_node_ids"])
        mapped_source_ids = sorted(
            {
                node_by_id[node_id]["source_id"]
                for node_id in mapped_node_ids
            }
        )

        promotion = {
            "service_id": "homevisit",
            "source_family": "delegated_remuneration_criteria",
            "mapped_node_count": len(mapped_node_ids),
            "mapped_node_ids": mapped_node_ids,
            "mapped_source_ids": mapped_source_ids,
            "applicability_proof": {
                "state": "PASS_EXPLICIT_CANONICAL_SERVICE_MAPPING",
                "evidence": [
                    "data/shared/remuneration-delegated/service-applicability.json#homevisit"
                ],
                "inherited_from_sibling_service": False,
            },
            "item_body_state": "PASS",
            "source_currentness_evidence": [
                "data/shared/remuneration-delegated/currentness-source-contract.json#"
                + source_id
                for source_id in mapped_source_ids
            ],
            "source_identity_matches_item_body_source": True,
            "projection_gate": {
                "kind": "EXPLICIT_BOUNDED_ALLOWLIST",
                "allowed": True,
                "identity": "homevisit::delegated_remuneration_criteria",
                "scope": "currentness_only",
            },
            "projected_currentness_state": "PASS",
            "promotion_applied": True,
        }

        original_path = builder.DELEGATED_CURRENTNESS_CONTRACT_PATH
        with tempfile.TemporaryDirectory() as missing_tmpdir:
            builder.DELEGATED_CURRENTNESS_CONTRACT_PATH = (
                Path(missing_tmpdir) / "missing-currentness-contract.json"
            )
            self.assertFalse(builder.source_contract_supported(promotion))
        builder.DELEGATED_CURRENTNESS_CONTRACT_PATH = original_path

        self.assertTrue(
            builder.delegated_service_contract_supported("homevisit")
        )
        self.assertFalse(
            builder.delegated_service_contract_supported(
                "specific-welfare-equipment-sale"
            )
        )

        contract = {
            "observed_date": "2026-10-06",
            "source_contracts": [
                {
                    "canonical_source_id": source_id,
                    "official_source_url": (
                        "https://www.mhlw.go.jp/web/t_doc?dataId="
                        + ("82ab4584" if "criteria95" in source_id else "82ab4585")
                        + "&dataType=0"
                    ),
                    "currentness_state": "PASS",
                    "promotion_eligible": True,
                }
                for source_id in mapped_source_ids
            ],
        }

        original_path = builder.DELEGATED_CURRENTNESS_CONTRACT_PATH
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                temp_path = Path(tmpdir) / "currentness-source-contract.json"
                temp_path.write_text(
                    json.dumps(contract, ensure_ascii=False),
                    encoding="utf-8",
                )
                builder.DELEGATED_CURRENTNESS_CONTRACT_PATH = temp_path

                self.assertTrue(builder.source_contract_supported(promotion))
                normalized = builder.normalize_runtime_promotion(promotion)
                self.assertEqual(
                    normalized["source_identity"]["canonical_source_id"],
                    "delegated-remuneration-national",
                )
                self.assertTrue(normalized["source_version_contains_scope"])
                self.assertEqual(normalized["ingestion_state"], "INGESTED")
                self.assertEqual(
                    set(normalized["allowed_publication_units"]),
                    builder.REQUIRED_PUBLICATION_UNITS,
                )

                wrong_nodes = copy.deepcopy(promotion)
                wrong_nodes["mapped_node_ids"] = wrong_nodes[
                    "mapped_node_ids"
                ][1:]
                wrong_nodes["mapped_node_count"] = len(
                    wrong_nodes["mapped_node_ids"]
                )
                self.assertFalse(
                    builder.source_contract_supported(wrong_nodes)
                )

                wrong_sources = copy.deepcopy(promotion)
                wrong_sources["mapped_source_ids"] = [
                    mapped_source_ids[0]
                ]
                self.assertFalse(
                    builder.source_contract_supported(wrong_sources)
                )

                blocked_contract = copy.deepcopy(contract)
                blocked_contract["source_contracts"][0][
                    "promotion_eligible"
                ] = False
                temp_path.write_text(
                    json.dumps(blocked_contract, ensure_ascii=False),
                    encoding="utf-8",
                )
                self.assertFalse(
                    builder.source_contract_supported(promotion)
                )
        finally:
            builder.DELEGATED_CURRENTNESS_CONTRACT_PATH = original_path

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
