#!/usr/bin/env python3
"""Load and validate the service catalog used by multi-service Kaigo Rules."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SERVICE_ID_RE = re.compile(r"^[a-z][a-z0-9-]*$")


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_service_catalog(root: Path = ROOT) -> dict:
    manifest_path = root / "data" / "services" / "manifest.json"
    manifest = _read_json(manifest_path)
    layer_path = root / manifest["verification_layers_file"]
    layer_catalog = _read_json(layer_path)

    configs = {}
    for descriptor in manifest.get("services", []):
        service_id = descriptor["service_id"]
        config_path = root / descriptor["config"]
        configs[service_id] = _read_json(config_path)

    return {
        "manifest": manifest,
        "layer_catalog": layer_catalog,
        "configs": configs,
    }


def derive_layer_service_ids(catalog: dict) -> dict[str, list[str]]:
    coverage: dict[str, list[str]] = {}
    for service_id, config in catalog["configs"].items():
        for layer_id in config.get("verification_layer_ids", []):
            coverage.setdefault(layer_id, []).append(service_id)
    return {layer_id: sorted(service_ids) for layer_id, service_ids in coverage.items()}


def load_normalized_verification_layers(
    catalog: dict, root: Path = ROOT
) -> list[dict]:
    layers = []
    for definition in catalog["layer_catalog"].get("layers", []):
        if definition.get("provider") != "normalized_report":
            continue
        report_ref = definition.get("report_file")
        if not report_ref:
            raise ValueError(
                f"verification layer {definition.get('id')} missing report_file"
            )
        report = _read_json(root / report_ref)
        if report.get("id") != definition.get("id"):
            raise ValueError(
                f"verification report id mismatch: {report.get('id')} != {definition.get('id')}"
            )
        required = [
            "title",
            "content_verification",
            "currentness",
            "monitoring",
            "human_review",
            "assurance",
        ]
        missing = [field for field in required if field not in report]
        if missing:
            raise ValueError(
                f"verification report {report.get('id')} missing fields: {missing}"
            )
        layers.append(report)
    return layers


def enrich_verification_layers(layers: list[dict], catalog: dict) -> list[dict]:
    layer_defs = {
        item["id"]: item
        for item in catalog["layer_catalog"].get("layers", [])
    }
    coverage = derive_layer_service_ids(catalog)

    generated_ids = {layer["id"] for layer in layers}
    declared_ids = set(layer_defs)
    if generated_ids != declared_ids:
        missing = sorted(declared_ids - generated_ids)
        extra = sorted(generated_ids - declared_ids)
        raise ValueError(
            f"verification layer catalog mismatch: missing_generated={missing} undeclared_generated={extra}"
        )

    enriched = []
    for layer in layers:
        definition = layer_defs[layer["id"]]
        service_ids = coverage.get(layer["id"], [])
        if definition["scope_kind"] != "GLOBAL" and not service_ids:
            raise ValueError(
                f"verification layer {layer['id']} has no service coverage"
            )
        enriched.append(
            {
                **layer,
                "service_ids": service_ids,
                "scope_kind": definition["scope_kind"],
            }
        )
    return enriched


def validation_errors(root: Path = ROOT, check_registry: bool = True) -> list[str]:
    errors: list[str] = []
    services_dir = root / "data" / "services"
    manifest_path = services_dir / "manifest.json"

    if not manifest_path.exists():
        return ["service catalog: manifest missing"]

    try:
        manifest = _read_json(manifest_path)
    except Exception as exc:
        return [f"service catalog: manifest unreadable: {exc}"]

    if manifest.get("format_version") != 2:
        errors.append("service catalog: manifest format_version must be 2")

    required_policies = [
        "existing_ids_are_stable",
        "existing_routes_are_stable",
        "shared_sources_are_not_duplicated_per_service",
        "verification_dimensions_remain_separate",
        "service_configs_are_isolated",
    ]
    policies = manifest.get("policies", {})
    for name in required_policies:
        if policies.get(name) is not True:
            errors.append(f"service catalog: required policy {name} must be true")

    descriptors = manifest.get("services", [])
    if not descriptors:
        errors.append("service catalog: services must not be empty")

    service_ids: set[str] = set()
    future_paths: set[str] = set()
    legacy_paths: dict[str, str] = {}
    config_refs: set[str] = set()
    namespace_prefixes: dict[str, str] = {}
    configs: dict[str, dict] = {}

    for descriptor in descriptors:
        service_id = descriptor.get("service_id")
        if not isinstance(service_id, str) or not SERVICE_ID_RE.fullmatch(service_id):
            errors.append(f"service catalog: invalid service_id {service_id!r}")
            continue
        if service_id in service_ids:
            errors.append(f"service catalog: duplicate service_id {service_id}")
            continue
        service_ids.add(service_id)

        if not descriptor.get("label"):
            errors.append(f"service catalog {service_id}: label missing")
        config_ref = descriptor.get("config")
        if not isinstance(config_ref, str) or not config_ref.startswith("data/services/"):
            errors.append(f"service catalog {service_id}: invalid config path")
            continue
        if config_ref in config_refs:
            errors.append(f"service catalog {service_id}: duplicate config path {config_ref}")
        config_refs.add(config_ref)

        config_path = root / config_ref
        if not config_path.exists():
            errors.append(f"service catalog {service_id}: config missing {config_ref}")
            continue

        try:
            config = _read_json(config_path)
        except Exception as exc:
            errors.append(f"service catalog {service_id}: config unreadable: {exc}")
            continue
        configs[service_id] = config

        if config.get("format_version") != 1:
            errors.append(f"service catalog {service_id}: config format_version must be 1")
        if config.get("service_id") != service_id:
            errors.append(f"service catalog {service_id}: config service_id mismatch")

        routing = config.get("routing", {})
        future_path = routing.get("future_service_base_path")
        expected_future_path = f"/services/{service_id}"
        if future_path != expected_future_path:
            errors.append(
                f"service catalog {service_id}: future path must be {expected_future_path}"
            )
        elif future_path in future_paths:
            errors.append(f"service catalog {service_id}: duplicate future route {future_path}")
        else:
            future_paths.add(future_path)

        for legacy_path in routing.get("legacy_entry_points", []):
            if not isinstance(legacy_path, str) or not legacy_path.startswith("/"):
                errors.append(f"service catalog {service_id}: invalid legacy route {legacy_path!r}")
                continue
            owner = legacy_paths.get(legacy_path)
            if owner and owner != service_id:
                errors.append(
                    f"service catalog: legacy route {legacy_path} shared by {owner} and {service_id}"
                )
            legacy_paths[legacy_path] = service_id

        for key, prefix in config.get("id_namespaces", {}).items():
            if not isinstance(prefix, str) or not prefix:
                errors.append(f"service catalog {service_id}: empty id namespace {key}")
                continue
            previous = namespace_prefixes.get(prefix)
            if previous and previous != service_id:
                errors.append(
                    f"service catalog: id namespace {prefix} shared by {previous} and {service_id}"
                )
            for existing_prefix, existing_service in namespace_prefixes.items():
                if existing_service != service_id and (
                    prefix.startswith(existing_prefix) or existing_prefix.startswith(prefix)
                ):
                    errors.append(
                        f"service catalog: overlapping id namespaces {existing_prefix} ({existing_service}) and {prefix} ({service_id})"
                    )
            namespace_prefixes[prefix] = service_id

        for name, relative_path in config.get("scope_files", {}).items():
            if not isinstance(relative_path, str) or not relative_path.startswith("data/"):
                errors.append(f"service catalog {service_id}: invalid scope path {name}")
                continue
            if not (root / relative_path).exists():
                errors.append(
                    f"service catalog {service_id}: scope file missing {relative_path}"
                )

    default_service_id = manifest.get("default_service_id")
    if default_service_id not in service_ids:
        errors.append("service catalog: default_service_id is not registered")
    else:
        default_descriptor = next(
            item for item in descriptors if item.get("service_id") == default_service_id
        )
        if not str(default_descriptor.get("status", "")).startswith("ACTIVE"):
            errors.append("service catalog: default service must be ACTIVE")

    layer_ref = manifest.get("verification_layers_file")
    if not isinstance(layer_ref, str):
        errors.append("service catalog: verification_layers_file missing")
        return errors

    layer_path = root / layer_ref
    if not layer_path.exists():
        errors.append(f"service catalog: verification layer catalog missing {layer_ref}")
        return errors

    try:
        layer_catalog = _read_json(layer_path)
    except Exception as exc:
        errors.append(f"service catalog: verification layer catalog unreadable: {exc}")
        return errors

    layer_defs = layer_catalog.get("layers", [])
    layer_ids: set[str] = set()
    for item in layer_defs:
        layer_id = item.get("id")
        if not layer_id:
            errors.append("service catalog: verification layer without id")
            continue
        if layer_id in layer_ids:
            errors.append(f"service catalog: duplicate verification layer {layer_id}")
        layer_ids.add(layer_id)
        if item.get("scope_kind") not in {
            "SERVICE_SPECIFIC",
            "SHARED_SOURCE_SERVICE_SCOPE",
            "SHARED_CORPUS_SERVICE_FILTER",
            "GLOBAL",
        }:
            errors.append(
                f"service catalog: invalid scope_kind for verification layer {layer_id}"
            )
        provider = item.get("provider")
        if provider not in {"legacy", "normalized_report"}:
            errors.append(
                f"service catalog: invalid provider for verification layer {layer_id}"
            )
        if provider == "normalized_report":
            report_ref = item.get("report_file")
            if not isinstance(report_ref, str) or not report_ref.startswith("data/verification/layers/"):
                errors.append(
                    f"service catalog: normalized report path invalid for {layer_id}"
                )
            elif not (root / report_ref).exists():
                errors.append(
                    f"service catalog: normalized report missing for {layer_id}: {report_ref}"
                )

    coverage: dict[str, list[str]] = {}
    for service_id, config in configs.items():
        seen_for_service: set[str] = set()
        for layer_id in config.get("verification_layer_ids", []):
            if layer_id in seen_for_service:
                errors.append(
                    f"service catalog {service_id}: duplicate verification layer {layer_id}"
                )
                continue
            seen_for_service.add(layer_id)
            if layer_id not in layer_ids:
                errors.append(
                    f"service catalog {service_id}: unknown verification layer {layer_id}"
                )
            coverage.setdefault(layer_id, []).append(service_id)

    for item in layer_defs:
        layer_id = item.get("id")
        if item.get("scope_kind") != "GLOBAL" and not coverage.get(layer_id):
            errors.append(
                f"service catalog: verification layer {layer_id} is not assigned to any service"
            )

    if check_registry:
        registry_path = root / "data" / "verification-registry.json"
        if not registry_path.exists():
            errors.append("service catalog: verification registry missing")
        else:
            registry = _read_json(registry_path)
            registry_layers = {
                item.get("id"): item
                for item in registry.get("layers", [])
                if item.get("id")
            }
            if set(registry_layers) != layer_ids:
                errors.append("service catalog: verification registry layer set differs from catalog")
            for layer_id, item in registry_layers.items():
                expected_services = sorted(coverage.get(layer_id, []))
                if sorted(item.get("service_ids", [])) != expected_services:
                    errors.append(
                        f"service catalog: verification registry service coverage stale for {layer_id}"
                    )
                definition = next(
                    (row for row in layer_defs if row.get("id") == layer_id),
                    None,
                )
                if definition and item.get("scope_kind") != definition.get("scope_kind"):
                    errors.append(
                        f"service catalog: verification registry scope_kind stale for {layer_id}"
                    )

    return errors
