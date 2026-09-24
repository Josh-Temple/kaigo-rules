import json
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from service_manifest import validation_errors


class ServiceManifestTests(unittest.TestCase):
    def _write(self, root: Path, relative: str, payload) -> None:
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(payload, str):
            path.write_text(payload, encoding="utf-8")
        else:
            path.write_text(
                json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )

    def _fixture(self, root: Path, service_count: int = 20) -> None:
        layer_ids = ["shared-law", "shared-qa"]
        services = []
        registry_layers = []

        for index in range(service_count):
            service_id = f"service-{index}"
            services.append(
                {
                    "service_id": service_id,
                    "label": f"サービス{index}",
                    "status": "PLANNED",
                    "config": f"data/services/{service_id}.json",
                }
            )
            scope_path = f"data/scopes/{service_id}.json"
            self._write(root, scope_path, {"service_id": service_id})
            self._write(
                root,
                f"data/services/{service_id}.json",
                {
                    "format_version": 1,
                    "service_id": service_id,
                    "routing": {
                        "future_service_base_path": f"/services/{service_id}",
                        "future_service_base_enabled": False,
                        "legacy_entry_points": [],
                    },
                    "id_namespaces": {
                        "fee": f"fee.{service_id}.",
                    },
                    "scope_files": {"primary": scope_path},
                    "verification_layer_ids": layer_ids,
                },
            )

        self._write(
            root,
            "data/services/manifest.json",
            {
                "format_version": 2,
                "status": "FOUNDATION_ACTIVE",
                "default_service_id": "service-0",
                "verification_layers_file": "data/services/verification-layers.json",
                "policies": {
                    "existing_ids_are_stable": True,
                    "existing_routes_are_stable": True,
                    "shared_sources_are_not_duplicated_per_service": True,
                    "verification_dimensions_remain_separate": True,
                    "service_configs_are_isolated": True,
                },
                "services": services,
            },
        )
        self._write(
            root,
            "data/services/verification-layers.json",
            {
                "format_version": 1,
                "layers": [
                    {"id": "shared-law", "scope_kind": "SHARED_SOURCE_SERVICE_SCOPE", "provider": "legacy"},
                    {"id": "shared-qa", "scope_kind": "SHARED_CORPUS_SERVICE_FILTER", "provider": "legacy"},
                ],
            },
        )
        for layer_id, scope_kind in [
            ("shared-law", "SHARED_SOURCE_SERVICE_SCOPE"),
            ("shared-qa", "SHARED_CORPUS_SERVICE_FILTER"),
        ]:
            registry_layers.append(
                {
                    "id": layer_id,
                    "service_ids": [f"service-{i}" for i in range(service_count)],
                    "scope_kind": scope_kind,
                }
            )
        self._write(
            root,
            "data/verification-registry.json",
            {"layers": registry_layers},
        )

    def test_catalog_scales_without_service_specific_validator_changes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._fixture(root, service_count=20)
            self.assertEqual([], validation_errors(root, check_registry=True))

    def test_duplicate_namespace_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._fixture(root, service_count=2)
            path = root / "data/services/service-1.json"
            config = json.loads(path.read_text(encoding="utf-8"))
            config["id_namespaces"]["fee"] = "fee.service-0."
            self._write(root, "data/services/service-1.json", config)
            errors = validation_errors(root, check_registry=True)
            self.assertTrue(any("id namespace" in error for error in errors))

    def test_registry_service_coverage_drift_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._fixture(root, service_count=3)
            registry_path = root / "data/verification-registry.json"
            registry = json.loads(registry_path.read_text(encoding="utf-8"))
            registry["layers"][0]["service_ids"] = ["service-0"]
            self._write(root, "data/verification-registry.json", registry)
            errors = validation_errors(root, check_registry=True)
            self.assertTrue(any("coverage stale" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
