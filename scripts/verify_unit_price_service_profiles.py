#!/usr/bin/env python3
"""Independently verify all unit-price service profiles against the official MHLW table.

This verifier reuses only the independent stdlib HTML parser/fetch primitives from
verify_unit_price_independent.py. It does not import the production importer.
It verifies the pinned source identity, every regional multiplier row, and every
service-to-profile mapping without promoting currentness or human review.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

from verify_unit_price_independent import (
    BASE_URL,
    REGIONS,
    clean,
    fetch,
    find_rate_table,
    jp_integer,
    parse_tables,
)

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"


def load(name: str):
    return json.loads((DATA / name).read_text(encoding="utf-8"))


def row_service_text(row: list[str], current_region: str, ratio_text: str) -> str:
    values = [
        cell
        for cell in row
        if cell
        and cell != current_region
        and cell != ratio_text
        and cell not in {"地域区分", "サービス種類", "割合"}
    ]
    return "".join(clean(value).replace(" ", "") for value in values)


def compare() -> dict:
    index = load("unit-price-service-multipliers.json")
    meta = load("unit-price-dayservice-meta.json")

    urls = [BASE_URL.format(1), BASE_URL.format(2)]
    payloads: list[bytes] = []
    htmls: list[str] = []
    for url in urls:
        payload, html = fetch(url)
        payloads.append(payload)
        htmls.append(html)

    source_sha256 = [hashlib.sha256(payload).hexdigest() for payload in payloads]
    source_differences: list[str] = []
    if meta.get("source_urls") != urls:
        source_differences.append("pinned source URLs differ from verifier URLs")
    if meta.get("source_sha256") != source_sha256:
        source_differences.append("pinned source SHA-256 differs from live identified source version")

    table = find_rate_table(parse_tables(htmls[0]))
    profiles = {row["profile_id"]: row for row in index.get("multiplier_profiles", [])}
    observed: dict[str, dict[str, dict]] = {profile_id: {} for profile_id in profiles}
    current_region: str | None = None
    table_differences: list[dict] = []

    for row in table:
        for cell in row:
            if cell in REGIONS:
                current_region = cell

        ratio_cells = [cell for cell in row if cell.startswith("千分の")]
        if not current_region or not ratio_cells:
            continue

        ratio_text = ratio_cells[-1]
        ratio = jp_integer(ratio_text.split("千分の", 1)[1])
        service_text = row_service_text(row, current_region, ratio_text)

        if current_region == "その他":
            if "全てのサービス" not in service_text:
                continue
            for profile_id in profiles:
                observed[profile_id][current_region] = {
                    "ratio_per_thousand": ratio,
                    "service_text": service_text,
                }
            continue

        for profile_id, profile in profiles.items():
            names = [str(name).replace(" ", "") for name in profile.get("official_service_names", [])]
            if names and all(name in service_text for name in names):
                if current_region in observed[profile_id]:
                    table_differences.append({
                        "profile_id": profile_id,
                        "region_class": current_region,
                        "error": "duplicate matching source row",
                    })
                observed[profile_id][current_region] = {
                    "ratio_per_thousand": ratio,
                    "service_text": service_text,
                }

    for profile_id, profile in profiles.items():
        expected_rows = {row["region_class"]: row for row in profile.get("rows", [])}
        for region in REGIONS:
            expected = expected_rows.get(region)
            actual = observed[profile_id].get(region)
            if expected is None or actual is None:
                table_differences.append({
                    "profile_id": profile_id,
                    "region_class": region,
                    "error": "missing expected or observed row",
                    "expected": expected,
                    "observed": actual,
                })
                continue
            if actual["ratio_per_thousand"] != expected.get("ratio_per_thousand"):
                table_differences.append({
                    "profile_id": profile_id,
                    "region_class": region,
                    "error": "multiplier differs",
                    "expected": expected.get("ratio_per_thousand"),
                    "observed": actual["ratio_per_thousand"],
                })

    mapping_differences: list[dict] = []
    for mapping in index.get("service_mappings", []):
        if mapping.get("applicability") != "APPLIES":
            continue
        profile_id = mapping.get("multiplier_profile_id")
        profile = profiles.get(profile_id)
        if not profile:
            mapping_differences.append({
                "service_id": mapping.get("service_id"),
                "error": "missing multiplier profile",
                "profile_id": profile_id,
            })
            continue
        official_name = str(mapping.get("official_service_name") or "").replace(" ", "")
        if official_name not in [str(name).replace(" ", "") for name in profile.get("official_service_names", [])]:
            mapping_differences.append({
                "service_id": mapping.get("service_id"),
                "error": "official service name not declared by mapped profile",
                "profile_id": profile_id,
                "official_service_name": mapping.get("official_service_name"),
            })
            continue
        for region in REGIONS[:-1]:
            source_text = observed.get(profile_id, {}).get(region, {}).get("service_text", "")
            if official_name not in source_text:
                mapping_differences.append({
                    "service_id": mapping.get("service_id"),
                    "profile_id": profile_id,
                    "region_class": region,
                    "error": "official service name absent from directly reparsed source row",
                })

    result = "PASS" if not (source_differences or table_differences or mapping_differences) else "FAIL"
    return {
        "format_version": 1,
        "verification_kind": "INDEPENDENT_MACHINE_REPARSE_ALL_UNIT_PRICE_PROFILES",
        "source_urls": urls,
        "source_sha256": source_sha256,
        "result": result,
        "observed": {
            "profile_count": len(profiles),
            "applicable_service_count": sum(
                1 for row in index.get("service_mappings", [])
                if row.get("applicability") == "APPLIES"
            ),
            "regions_per_profile": {
                profile_id: sorted(rows)
                for profile_id, rows in observed.items()
            },
        },
        "differences": {
            "source": source_differences,
            "table": table_differences,
            "service_mappings": mapping_differences,
        },
        "safety": {
            "promotes_currentness": False,
            "promotes_human_review": False,
            "promotes_publication": False,
            "promotes_route_exposure": False,
            "note": "PASS is bounded to item-body equality for the pinned official source version.",
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report")
    args = parser.parse_args()
    report = compare()
    rendered = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    print(rendered, end="")
    if args.report:
        path = Path(args.report)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(rendered, encoding="utf-8")
    return 0 if report["result"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
