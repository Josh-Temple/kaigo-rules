#!/usr/bin/env python3
"""Verify bounded multi-service Unit Price currentness on the official MHLW display.

The verifier keeps source-level currentness separate from service applicability.
It reparses the live official consolidated display, preserves the existing
independent day-service/hash gate, and checks only an explicit bounded set of
service rows against canonical multiplier profiles and PASS item-body evidence.
It never promotes human review, relation semantics, publication, routes, or
unselected Unit Price cells.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

import verify_unit_price_independent as independent

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
CURRENT_URL = "https://www.mhlw.go.jp/web/t_doc?dataId=82ab4582&dataType=0"
REGIONS = ["一級地", "二級地", "三級地", "四級地", "五級地", "六級地", "七級地"]

BOUNDED_SERVICE_IDS = [
    "dayservice",
    "homevisit",
    "homebath",
    "homenursing",
    "homerehab",
    "homecaremanagement",
    "shortstay-life",
    "shortstay-medical",
    "specific-facility",
    "welfare-equipment-rental",
    "preventive-homebath",
    "preventive-homenursing",
    "preventive-homerehab",
    "preventive-homecaremanagement",
    "preventive-dayrehab",
    "preventive-shortstay-life",
    "preventive-shortstay-medical",
    "preventive-specific-facility",
    "preventive-welfare-equipment-rental"
]

MARKERS = {
    "title": ("厚生労働大臣が定める一単位の単価",),
    "notice_identity": ("厚生労働省告示第九十三号", "厚生労働省告示第93号"),
    "effective_reference_date": ("令和六年四月一日", "令和6年4月1日"),
}


class TextCollector(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []

    def handle_data(self, data: str) -> None:
        value = independent.clean(data)
        if value:
            self.parts.append(value)


def load_json(name: str) -> dict[str, Any]:
    return json.loads((DATA / name).read_text(encoding="utf-8"))


def marker_check(html: str) -> dict[str, Any]:
    parser = TextCollector()
    parser.feed(html)
    parser.close()
    visible = independent.clean(" ".join(parser.parts))
    observed: dict[str, str] = {}
    missing: list[str] = []
    for key, alternatives in MARKERS.items():
        match = next((value for value in alternatives if value in visible), None)
        if match is None:
            missing.append(key)
        else:
            observed[key] = match
    return {"observed_markers": observed, "missing_markers": missing}


def service_text_from_row(row: list[str], current_region: str, ratio_text: str) -> str:
    ignored = {"地域区分", "サービス種類", "割合", current_region, ratio_text}
    return independent.clean(" ".join(cell for cell in row if cell and cell not in ignored))


def extract_rate_rows(table: list[list[str]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    current_region: str | None = None
    for row in table:
        for cell in row:
            if cell in independent.REGIONS:
                current_region = cell
        ratio_cells = [cell for cell in row if cell.startswith("千分の")]
        if not current_region or current_region not in REGIONS or not ratio_cells:
            continue
        ratio_text = ratio_cells[-1]
        ratio = independent.jp_integer(ratio_text.split("千分の", 1)[1])
        rows.append(
            {
                "region_class": current_region,
                "ratio_per_thousand": ratio,
                "ratio_text": ratio_text,
                "service_text": service_text_from_row(row, current_region, ratio_text),
            }
        )
    return rows


def expected_ratio(profile: dict[str, Any], region: str) -> int | None:
    for row in profile.get("rows") or []:
        if row.get("region_class") == region:
            value = row.get("ratio_per_thousand")
            return int(value) if value is not None else None
    return None


def verify_bounded_services(rate_rows: list[dict[str, Any]]) -> dict[str, Any]:
    mapping = load_json("unit-price-service-multipliers.json")
    item_body = load_json("unit-price-item-body-assurance.json")

    map_by_id = {row["service_id"]: row for row in mapping.get("service_mappings") or []}
    body_by_id = {
        row["service_id"]: row for row in item_body.get("service_projections") or []
    }
    profiles = {
        row["profile_id"]: row for row in mapping.get("multiplier_profiles") or []
    }

    checks: list[dict[str, Any]] = []
    failures: list[str] = []

    for service_id in BOUNDED_SERVICE_IDS:
        m = map_by_id.get(service_id)
        b = body_by_id.get(service_id)
        if not m or not b:
            failures.append(f"{service_id}: canonical mapping/item-body row missing")
            continue
        if m.get("applicability") != "APPLIES":
            failures.append(f"{service_id}: canonical applicability is not APPLIES")
            continue
        if b.get("service_level_item_body") != "PASS":
            failures.append(f"{service_id}: canonical item-body is not PASS")
            continue
        if b.get("multiplier_profile_id") != m.get("multiplier_profile_id"):
            failures.append(f"{service_id}: item-body profile differs from service mapping")
            continue
        if b.get("official_service_name") != m.get("official_service_name"):
            failures.append(f"{service_id}: item-body service name differs from service mapping")
            continue

        profile_id = str(m.get("multiplier_profile_id") or "")
        profile = profiles.get(profile_id)
        if not profile:
            failures.append(f"{service_id}: multiplier profile missing: {profile_id}")
            continue
        official_name = str(m.get("official_service_name") or "")
        if official_name not in (profile.get("official_service_names") or []):
            failures.append(f"{service_id}: official service name absent from canonical profile")
            continue

        region_checks = []
        for region in REGIONS:
            ratio = expected_ratio(profile, region)
            candidates = [
                row for row in rate_rows
                if row["region_class"] == region and row["ratio_per_thousand"] == ratio
            ]
            matched = any(official_name in row["service_text"] for row in candidates)
            region_checks.append(
                {
                    "region_class": region,
                    "expected_ratio_per_thousand": ratio,
                    "service_name_observed_in_expected_rate_row": matched,
                }
            )
            if not matched:
                failures.append(
                    f"{service_id}: {official_name} not observed in {region} ratio {ratio} row"
                )

        checks.append(
            {
                "service_id": service_id,
                "official_service_name": official_name,
                "multiplier_profile_id": profile_id,
                "item_body_state": b.get("service_level_item_body"),
                "region_checks": region_checks,
                "result": "PASS" if all(
                    row["service_name_observed_in_expected_rate_row"]
                    for row in region_checks
                ) else "FAIL",
            }
        )

    return {
        "selected_service_count": len(BOUNDED_SERVICE_IDS),
        "checks": checks,
        "failures": failures,
        "result": "PASS" if not failures and len(checks) == len(BOUNDED_SERVICE_IDS) else "FAIL",
    }


def compare() -> dict[str, Any]:
    independent_report = independent.compare()

    index_payload, index_html = independent.fetch(CURRENT_URL)
    identity = marker_check(index_html)

    page_htmls: list[str] = []
    for page in (1, 2):
        _, html = independent.fetch(independent.BASE_URL.format(page))
        page_htmls.append(html)
    tables: list[list[list[str]]] = []
    for html in page_htmls:
        tables.extend(independent.parse_tables(html))
    rate_rows = extract_rate_rows(independent.find_rate_table(tables))
    bounded = verify_bounded_services(rate_rows)

    pinned_hashes_match_live = (
        independent_report.get("result") == "PASS"
        and not (independent_report.get("differences") or {}).get("metadata")
    )
    source_identity_observed = not identity["missing_markers"]
    bounded_services_match = bounded.get("result") == "PASS"
    result = (
        "PASS"
        if pinned_hashes_match_live and source_identity_observed and bounded_services_match
        else "FAIL"
    )

    bounded_identities = [
        f"{service_id}::unit_price_regional_classification"
        for service_id in BOUNDED_SERVICE_IDS
    ]
    return {
        "format_version": 2,
        "verification_kind": "BOUNDED_MULTI_SERVICE_CURRENT_OFFICIAL_DISPLAY_REPARSE",
        "legacy_bounded_identity": "dayservice::unit_price_regional_classification",
        "bounded_identities": bounded_identities,
        "official_current_url": CURRENT_URL,
        "official_current_page_sha256": hashlib.sha256(index_payload).hexdigest(),
        "source_identity": identity,
        "independent_reparse_result": independent_report.get("result"),
        "live_page_sha256": independent_report.get("source_sha256"),
        "differences": independent_report.get("differences"),
        "bounded_service_checks": bounded,
        "result": result,
        "currentness_evidence": {
            "official_current_display_identity_observed": source_identity_observed,
            "canonical_source_hashes_match_current_live_source": pinned_hashes_match_live,
            "selected_service_rows_match_canonical_profiles": bounded_services_match,
            "supports_bounded_currentness": result == "PASS",
        },
        "safety": {
            "promotes_human_review": False,
            "promotes_relation_verification": False,
            "promotes_global_family_currentness": False,
            "supports_bounded_currentness": result == "PASS",
            "bounded_scope": bounded_identities,
            "note": (
                "PASS is limited to the explicit bounded service identities. "
                "The live source is shared, but service applicability is checked independently "
                "against canonical mappings and PASS item-body evidence. Unselected Unit Price "
                "cells remain fail-closed."
            ),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", help="Optional path for the JSON verification report")
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
