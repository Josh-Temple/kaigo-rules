import json
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from build_service_catalog import build
from service_manifest import ROOT, validation_errors


class ServiceUniverseCatalogTests(unittest.TestCase):
    def test_repository_registers_complete_current_service_universe(self):
        manifest = json.loads((ROOT / "data/services/manifest.json").read_text(encoding="utf-8"))
        current = manifest["services"]
        self.assertEqual(39, len(current))
        self.assertEqual(39, manifest["service_universe"]["current_service_count"])
        self.assertEqual(39, len({row["service_id"] for row in current}))
        self.assertEqual(39, len({row["label"] for row in current}))
        self.assertEqual(
            23,
            len([row for row in current if row["status"] == "REGISTERED_NOT_INGESTED"]),
        )
        partial_ingestion_ids = {
            row["service_id"] for row in current if row["status"] == "PARTIAL_INGESTION"
        }
        self.assertTrue(
            {"shortstay-medical", "specific-facility", "welfare-equipment-rental"}
            <= partial_ingestion_ids
        )
        historical_ids = {row["service_id"] for row in manifest["historical_services"]}
        self.assertEqual(
            {"care-medical-facility", "preventive-homevisit", "preventive-dayservice"},
            historical_ids,
        )
        self.assertTrue(historical_ids.isdisjoint({row["service_id"] for row in current}))
        self.assertEqual(
            {"housing-renovation", "community-support-program"},
            {row["category_id"] for row in manifest["special_categories"]},
        )

    def test_registered_not_ingested_configs_fail_closed(self):
        manifest = json.loads((ROOT / "data/services/manifest.json").read_text(encoding="utf-8"))
        for descriptor in manifest["services"]:
            if descriptor["status"] != "REGISTERED_NOT_INGESTED":
                continue
            config = json.loads((ROOT / descriptor["config"]).read_text(encoding="utf-8"))
            self.assertEqual("REGISTERED_NOT_INGESTED", config["readiness"])
            self.assertEqual("REGISTERED_NOT_INGESTED", config["ingestion_state"])
            self.assertTrue(config["expected_source_families"])
            self.assertEqual([], config["verification_layer_ids"])
            for scope_path in config["scope_files"].values():
                self.assertTrue((ROOT / scope_path).exists(), scope_path)
            self.assertFalse(config["routing"]["future_service_base_enabled"])
            self.assertFalse(config["publication_gate"]["public_routes_enabled"])
            self.assertFalse(config["publication_gate"]["content_ingested"])
            self.assertFalse(config["publication_gate"]["independent_verification_complete"])
            self.assertFalse(config["publication_gate"]["human_review_complete"])

    def test_generated_catalog_matches_canonical_manifest_and_configs(self):
        generated = json.loads((ROOT / "data/services/catalog.generated.json").read_text(encoding="utf-8"))
        self.assertEqual(build(), generated)

    def test_duplicate_label_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "data/services").mkdir(parents=True)
            policies = {
                "existing_ids_are_stable": True,
                "existing_routes_are_stable": True,
                "shared_sources_are_not_duplicated_per_service": True,
                "verification_dimensions_remain_separate": True,
                "service_configs_are_isolated": True,
            }
            services = []
            for service_id in ("alpha", "beta"):
                (root / f"data/services/{service_id}.json").write_text(
                    json.dumps({
                        "format_version": 1,
                        "service_id": service_id,
                        "routing": {
                            "future_service_base_path": f"/services/{service_id}",
                            "future_service_base_enabled": False,
                            "legacy_entry_points": [],
                        },
                        "id_namespaces": {},
                        "scope_files": {},
                        "verification_layer_ids": [],
                    }, ensure_ascii=False),
                    encoding="utf-8",
                )
                services.append({
                    "service_id": service_id,
                    "label": "重複ラベル",
                    "status": "PLANNED",
                    "config": f"data/services/{service_id}.json",
                })
            (root / "data/services/manifest.json").write_text(
                json.dumps({
                    "format_version": 2,
                    "status": "FOUNDATION_ACTIVE",
                    "default_service_id": "alpha",
                    "verification_layers_file": "data/services/verification-layers.json",
                    "policies": policies,
                    "services": services,
                }, ensure_ascii=False),
                encoding="utf-8",
            )
            (root / "data/services/verification-layers.json").write_text(
                json.dumps({"format_version": 1, "layers": []}),
                encoding="utf-8",
            )
            errors = validation_errors(root, check_registry=False)
            self.assertTrue(any("duplicate service label" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
