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
        services.append(
            {
                "service_id": service_id,
                "label": descriptor["label"],
                "status": descriptor["status"],
                "routing": config.get("routing", {}),
                "id_namespaces": config.get("id_namespaces", {}),
            }
        )

    return {
        "format_version": 1,
        "generated_by": "scripts/build_service_catalog.py",
        "default_service_id": manifest["default_service_id"],
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
