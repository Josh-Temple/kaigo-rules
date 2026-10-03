#!/usr/bin/env python3
"""Build the runtime service catalog from isolated service configs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from service_manifest import ROOT, load_service_catalog, validation_errors

OUTPUT = ROOT / "data" / "services" / "catalog.generated.json"


def build() -> dict:
    errors = validation_errors(ROOT, check_registry=False)
    if errors:
        raise ValueError("\n".join(errors))

    catalog = load_service_catalog(ROOT)
    manifest = catalog["manifest"]
    configs = catalog["configs"]

    services = []
    for descriptor in manifest.get("services", []):
        service_id = descriptor["service_id"]
        config = configs[service_id]
        item = {
            "service_id": service_id,
            "label": descriptor["label"],
            "status": descriptor["status"],
            "service_class": descriptor.get("service_class"),
            "routing": config.get("routing", {}),
            "id_namespaces": config.get("id_namespaces", {}),
            "scope_files": config.get("scope_files", {}),
            "publication_gate": config.get("publication_gate", {}),
            "ingestion_layers": config.get("ingestion_layers", {}),
            "verification_layer_ids": config.get("verification_layer_ids", []),
        }
        if "identity" in config:
            item["identity"] = config["identity"]
        if "expected_source_families" in config:
            item["expected_source_families"] = config["expected_source_families"]
        if "ingestion_state" in config:
            item["ingestion_state"] = config["ingestion_state"]
        services.append(item)

    return {
        "format_version": 1,
        "generated_by": "scripts/build_service_catalog.py",
        "default_service_id": manifest["default_service_id"],
        "service_universe": manifest.get("service_universe", {}),
        "historical_services": manifest.get("historical_services", []),
        "special_categories": manifest.get("special_categories", []),
        "services": services,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    rendered = json.dumps(build(), ensure_ascii=False, indent=2) + "\n"
    if args.check:
        if not OUTPUT.exists():
            raise SystemExit("runtime service catalog missing; run builder")
        if OUTPUT.read_text(encoding="utf-8") != rendered:
            raise SystemExit("runtime service catalog is stale; run builder")
        print("runtime service catalog: current")
        return

    OUTPUT.write_text(rendered, encoding="utf-8")
    print(f"wrote {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
