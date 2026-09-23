#!/usr/bin/env python3
"""Validate the conservative currentness-source investigation for 老企第25号."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "data" / "notice-rouki25-currentness-investigation.json"

ALLOWED_KINDS = {
    "PRIMARY_SOURCE_FINAL_AMENDMENT_ROUTE",
    "OFFICIAL_PARENT_PUBLICATION_CONTEXT",
    "OFFICIAL_REPUBLICATION_CONTEXT",
    "OFFICIAL_REFORM_INDEX_SUPPORTING_ONLY",
    "OFFICIAL_INDEX_SUPPORTING_ONLY",
    "HISTORICAL_ORIGINAL_NOT_CONSOLIDATED",
    "SEARCH_SUPPORTING_ONLY",
}


def fail(message: str) -> None:
    raise SystemExit("rouki25 currentness investigation validation failed: " + message)


def main() -> None:
    try:
        data = json.loads(PATH.read_text(encoding="utf-8"))
    except Exception as exc:
        fail(f"cannot read valid JSON: {exc}")

    if data.get("scope") != "rouki25-dayservice-22-currentness":
        fail("unexpected scope")
    if data.get("conclusion") != "UNRESOLVED_EXHAUSTIVE_COVERAGE":
        fail("currentness must remain unresolved until exhaustive primary-source coverage is established")
    if data.get("effect_on_22_items") != "KEEP_HOLD":
        fail("22 items must remain HOLD")
    if data.get("automatic_promotion_allowed") is not False:
        fail("automatic promotion must remain disabled")
    if not data.get("blocking_requirement"):
        fail("blocking requirement is missing")

    resolution = data.get("source_date_provenance_resolution", {})
    if resolution.get("source_id") != "mhlw-2026-rouki25-reference-redline":
        fail("unexpected reference-period resolution target")
    if resolution.get("previous_repository_period_claim") != "2026-03":
        fail("previous period claim must remain traceable")
    if resolution.get("corrected_reference_period") != "2025-03":
        fail("reference period must be corrected to earliest confirmed official parent publication context")
    if resolution.get("period_semantics") != "earliest_confirmed_official_parent_publication_context":
        fail("reference-period semantics are missing")
    if resolution.get("official_r7_notice_date") != "2025-03-25":
        fail("R7 parent publication evidence is incomplete")
    if resolution.get("official_r8_notice_date") != "2026-03-31":
        fail("R8 republication evidence is incomplete")
    if resolution.get("same_pdf_url_reused_across_r7_and_r8_parent_pages") is not True:
        fail("same-PDF reuse across R7/R8 parent pages must be explicit")
    if resolution.get("underlying_redline_amendment_date") != "UNRESOLVED_NOT_USED_AS_REFERENCE_PERIOD":
        fail("underlying redline amendment date must not be inferred from parent-page publication")
    if resolution.get("status") != "RESOLVED_FOR_REFERENCE_PERIOD":
        fail("reference-period provenance resolution is not closed")
    if not resolution.get("tracking_issue", "").endswith("/issues/85"):
        fail("resolution must remain traceable to issue 85")

    routes = data.get("routes", [])
    if len(routes) < 7:
        fail("expected official/search routes including R7 publication and R8 republication contexts")
    route_ids = [route.get("route_id") for route in routes]
    if len(route_ids) != len(set(route_ids)):
        fail("duplicate route_id")

    by_id = {route["route_id"]: route for route in routes}
    for route in routes:
        if route.get("kind") not in ALLOWED_KINDS:
            fail(f"{route.get('route_id')}: unsupported route kind")
        url = route.get("url", "")
        if not url.startswith("https://www.mhlw.go.jp/"):
            fail(f"{route.get('route_id')}: route must be an MHLW URL")
        if not route.get("observation") or not route.get("use") or not route.get("limitation"):
            fail(f"{route.get('route_id')}: observation/use/limitation must be explicit")

    r7 = by_id.get("mhlw-r7-manual-reference", {})
    if r7.get("kind") != "OFFICIAL_PARENT_PUBLICATION_CONTEXT":
        fail("R7 manual page must establish the 2025-03 parent publication context")
    if "正式な改正日を意味しない" not in r7.get("limitation", ""):
        fail("parent publication must not be conflated with the redline amendment date")

    r8 = by_id.get("mhlw-r8-manual-reference-reuse", {})
    if r8.get("kind") != "OFFICIAL_REPUBLICATION_CONTEXT":
        fail("R8 manual page must be recorded as republication context")
    if "網羅的証明にはならない" not in r8.get("limitation", ""):
        fail("R8 republication must not be treated as proof of no later amendment")

    reform = by_id.get("mhlw-r8-reform-page", {})
    if reform.get("kind") != "OFFICIAL_REFORM_INDEX_SUPPORTING_ONLY":
        fail("R8 reform page must remain supporting-only")
    if "不改正とは判定しない" not in reform.get("limitation", ""):
        fail("R8 reform-page omission must not be treated as proof of no amendment")

    law_db = by_id.get("mhlw-law-database-rouki25", {})
    if law_db.get("kind") != "HISTORICAL_ORIGINAL_NOT_CONSOLIDATED":
        fail("MHLW law database route must not be classified as current consolidated text")

    search_route = by_id.get("mhlw-domain-exact-title-search", {})
    if search_route.get("kind") != "SEARCH_SUPPORTING_ONLY":
        fail("search route must remain supporting-only")
    if not search_route.get("queries"):
        fail("search queries must be recorded")
    if "変更不存在の証拠ではない" not in search_route.get("limitation", ""):
        fail("search absence must not be treated as proof of no change")

    scan = data.get("post_r6_official_index_scan", {})
    if scan.get("candidate_post_r6_amendment_identified") is not False:
        fail("post-R6 index scan must not claim an amendment candidate unless evidence is recorded")
    if scan.get("decision_effect") != "HOLD_UNCHANGED":
        fail("post-R6 index scan must not lift HOLD")
    if scan.get("exact_title_page_text_match_after_r6") is not False:
        fail("unexpected exact-title match state")
    if scan.get("rouki25_page_text_match_after_r6") is not False:
        fail("unexpected 老企第25号 match state")
    checked = scan.get("checked_routes", [])
    required_scan_routes = {
        "mhlw-kaigo-latest-info-current",
        "mhlw-kaigo-latest-info-adjacent-index-31",
        "mhlw-kaigo-latest-info-adjacent-index-29",
        "mhlw-r8-reform-notification-list",
        "mhlw-r6-reform-baseline",
    }
    if {item.get("route_id") for item in checked} != required_scan_routes:
        fail("post-R6 official index scan route set is incomplete or changed")
    if "存在しないことの証明にはならない" not in scan.get("inference_limit", ""):
        fail("official-index absence must not be treated as proof of no amendment")
    if not scan.get("next_blocker"):
        fail("post-R6 scan must preserve the remaining currentness blocker")

    policy = data.get("status_policy", {})
    if "現行性の証明ではない" not in policy.get("machine_text_match", ""):
        fail("machine text match must not be described as proof of currentness")
    if "HOLD" not in policy.get("currentness", ""):
        fail("currentness policy must preserve HOLD")
    if "2025-03へ訂正済み" not in policy.get("currentness", ""):
        fail("currentness policy must record the corrected reference period")

    print("rouki25 currentness investigation: OK (reference period corrected; post-R6 official index scan recorded; exhaustive coverage unresolved; 22 items remain HOLD)")


if __name__ == "__main__":
    main()
