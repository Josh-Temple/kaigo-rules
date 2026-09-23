#!/usr/bin/env python3
"""Validate the conservative currentness-source investigation for 老企第25号."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "data" / "notice-rouki25-currentness-investigation.json"

ALLOWED_KINDS = {
    "PRIMARY_SOURCE_FINAL_AMENDMENT_ROUTE",
    "OFFICIAL_PARENT_CONTEXT_DATE_CONFLICT",
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

    conflicts = data.get("source_date_provenance_conflicts", [])
    if len(conflicts) != 1:
        fail("expected one recorded source-date provenance conflict")
    conflict = conflicts[0]
    if conflict.get("source_id") != "mhlw-2026-rouki25-reference-redline":
        fail("unexpected source-date conflict target")
    if conflict.get("repository_period_claim") != "2026-03":
        fail("recorded repository period claim changed unexpectedly")
    if conflict.get("status") != "DATE_PROVENANCE_UNRESOLVED":
        fail("reference-PDF date provenance must remain unresolved until primary-source provenance is established")
    if "2026-03" not in conflict.get("safety_effect", ""):
        fail("date-provenance conflict must explicitly block use of the 2026-03 claim")
    if not conflict.get("tracking_issue", "").endswith("/issues/85"):
        fail("date-provenance conflict must remain traceable to issue 85")

    routes = data.get("routes", [])
    if len(routes) < 6:
        fail("expected the checked official/search routes including the parent-page date conflict")
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

    parent = by_id.get("mhlw-r7-abuse-manual-reference", {})
    if parent.get("kind") != "OFFICIAL_PARENT_CONTEXT_DATE_CONFLICT":
        fail("R7 parent-page context must remain recorded as a date-provenance conflict")
    if "2025-03" not in conflict.get("companion_notice_date", ""):
        fail("companion notice date is missing")
    if "即断して置換せず" not in parent.get("limitation", ""):
        fail("parent-page context must not be over-interpreted as the exact redline amendment date")

    law_db = by_id.get("mhlw-law-database-rouki25", {})
    if law_db.get("kind") != "HISTORICAL_ORIGINAL_NOT_CONSOLIDATED":
        fail("MHLW law database route must not be classified as current consolidated text")

    r8 = by_id.get("mhlw-r8-reform-page", {})
    if r8.get("kind") != "OFFICIAL_REFORM_INDEX_SUPPORTING_ONLY":
        fail("R8 reform page must remain supporting-only")
    if "不改正とは判定しない" not in r8.get("limitation", ""):
        fail("R8 reform-page omission must not be treated as proof of no amendment")

    search_route = by_id.get("mhlw-domain-exact-title-search", {})
    if search_route.get("kind") != "SEARCH_SUPPORTING_ONLY":
        fail("search route must remain supporting-only")
    if not search_route.get("queries"):
        fail("search queries must be recorded")
    if "変更不存在の証拠ではない" not in search_route.get("limitation", ""):
        fail("search absence must not be treated as proof of no change")

    policy = data.get("status_policy", {})
    if "現行性の証明ではない" not in policy.get("machine_text_match", ""):
        fail("machine text match must not be described as proof of currentness")
    if "HOLD" not in policy.get("currentness", ""):
        fail("currentness policy must preserve HOLD")
    if "時期metadataの未解決矛盾" not in policy.get("currentness", ""):
        fail("currentness policy must preserve the unresolved date-provenance blocker")

    print("rouki25 currentness investigation: OK (coverage/date provenance unresolved; 22 items remain HOLD)")


if __name__ == "__main__":
    main()
