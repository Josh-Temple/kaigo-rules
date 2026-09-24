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
    "OFFICIAL_INTERNAL_SEARCH_SUPPORTING_ONLY",
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

    pdf_scan = data.get("post_r6_pdf_body_scan", {})
    if pdf_scan.get("fresh_main_sha_at_start") != "ff2cbf9fb92735a7fef726334010305fb164827d":
        fail("post-R6 PDF-body scan must record the fresh main SHA used at start")
    if pdf_scan.get("decision_effect") != "HOLD_UNCHANGED":
        fail("post-R6 PDF-body scan must not lift HOLD")
    search_result = pdf_scan.get("search_result", {})
    if search_result.get("verified_post_r6_amendment_candidates") != []:
        fail("no verified post-R6 amendment candidate is currently established")
    if search_result.get("exact_amendment_searches_for_r7_r8_returned_verified_candidate") is not False:
        fail("R7/R8 amendment search result must remain conservative")

    evidence = {item.get("evidence_id"): item for item in pdf_scan.get("evidence", [])}
    required_pdf_evidence = {
        "r6-baseline-vol1213": "R6_BASELINE_AMENDMENT",
        "r7-vol1455-current-reference": "POST_R6_REFERENCE_NON_AMENDMENT",
        "recent-content-url-historical-redline": "HISTORICAL_REDLINE_BODY_MATCH",
    }
    for evidence_id, classification in required_pdf_evidence.items():
        if evidence.get(evidence_id, {}).get("classification") != classification:
            fail(f"{evidence_id}: missing or unsafe PDF-body classification")

    r7_reference = evidence["r7-vol1455-current-reference"]
    if r7_reference.get("document_date") != "2025-12-26":
        fail("Vol.1455 reference date must remain explicit")
    if "改正する旨は記載していない" not in r7_reference.get("observation", ""):
        fail("Vol.1455 must not be misclassified as an amendment")

    historical = evidence["recent-content-url-historical-redline"]
    if historical.get("comparison_scope") != "TEXT_AND_PAGE_STRUCTURE_MATCH_NOT_BYTE_HASH":
        fail("historical redline comparison scope must remain bounded")
    if "改正日を意味しない" not in historical.get("limitation", ""):
        fail("recent content URL must not be treated as amendment-date evidence")

    if "改正不存在の証明にしない" not in pdf_scan.get("inference_limit", ""):
        fail("PDF search absence must not be treated as proof of no amendment")
    if not pdf_scan.get("next_blocker"):
        fail("post-R6 PDF-body scan must preserve the remaining currentness blocker")

    lawdb = data.get("mhlw_law_database_coverage_check", {})
    if lawdb.get("fresh_main_sha_at_start") != "81439978d45a10189118a077d81da9d3b2f1f880":
        fail("MHLW law-database coverage check must record its fresh main SHA")
    official_db = lawdb.get("official_database", {})
    if official_db.get("notification_scope") != "厚生労働省所管の主な訓令、通知、公示等":
        fail("MHLW notification database scope must remain explicit")
    if official_db.get("update_frequency") != "MONTHLY":
        fail("MHLW notification database update frequency must remain explicit")
    if official_db.get("latest_notification_amendment_count") != 7:
        fail("latest checked notification amendment-list count must remain traceable")
    if "主な" not in official_db.get("coverage_limit", "") or "証明しない" not in official_db.get("coverage_limit", ""):
        fail("MHLW law database must not be treated as exhaustive")
    if official_db.get("coverage_notice_url") != "https://www.mhlw.go.jp/hourei/readme.html":
        fail("MHLW law database non-exhaustive notice URL must remain pinned")
    coverage_notice = official_db.get("coverage_notice_statement", "")
    if "全て" not in coverage_notice or "網羅しているわけではありません" not in coverage_notice:
        fail("MHLW law database official non-exhaustive notice must remain explicit")
    if official_db.get("systematic_search_url") != "https://www.mhlw.go.jp/hourei/html/tsuchi/contents.html":
        fail("MHLW notification systematic-search route must remain explicit")
    if "完全な改正履歴にはならない" not in official_db.get("systematic_search_observation", ""):
        fail("MHLW systematic search must not be treated as exhaustive")

    original = lawdb.get("original_record_check", {})
    if original.get("classification") != "HISTORICAL_ORIGINAL_NOT_CONSOLIDATED":
        fail("MHLW old企25 database record must remain historical-only")
    if original.get("current_markers_found") != []:
        fail("historical old企25 record must not be represented as current integrated text")

    r6_redline = lawdb.get("r6_official_redline_check", {})
    if r6_redline.get("classification") != "R6_AMENDMENT_REDLINE_NOT_CONSOLIDATED":
        fail("R6 official target PDF must remain classified as a redline, not consolidated text")
    if "現行統合全文ではない" not in r6_redline.get("observation", ""):
        fail("R6 redline limitation must remain explicit")

    lawdb_result = lawdb.get("result", {})
    if lawdb_result.get("official_discovery_coverage_strengthened") is not True:
        fail("MHLW law database coverage work must record strengthened discovery coverage")
    if lawdb_result.get("database_is_exhaustive_for_all_notifications") is not False:
        fail("MHLW law database must not be represented as exhaustive for all notifications")
    if lawdb_result.get("current_integrated_text_found") is not False:
        fail("no authoritative current integrated text has been established")
    if lawdb_result.get("verified_post_r6_amendment_candidate_identified") is not False:
        fail("no verified post-R6 amendment candidate is established by the law database check")
    if lawdb_result.get("decision_effect") != "HOLD_UNCHANGED":
        fail("MHLW law database check must not lift HOLD")

    matrix = {row.get("lane"): row for row in lawdb.get("coverage_matrix", [])}
    required_lanes = {
        "R6_BASELINE",
        "KAIGO_LATEST_INFO_AND_R8_REFORM",
        "MHLW_LAW_DB_REGISTERED_MAIN_NOTICES",
        "MHLW_LAW_DB_PENDING_MAIN_NOTICES",
        "MHLW_LAW_DB_SYSTEMATIC_SEARCH",
        "CURRENT_INTEGRATED_TEXT",
    }
    if set(matrix) != required_lanes:
        fail("MHLW currentness coverage matrix is incomplete or changed")
    if matrix["MHLW_LAW_DB_SYSTEMATIC_SEARCH"].get("status") != "SEARCHED_SUPPORTING_ONLY":
        fail("MHLW systematic search must remain supporting-only")
    if matrix["CURRENT_INTEGRATED_TEXT"].get("status") != "NOT_FOUND":
        fail("current integrated text must remain unresolved")
    if "網羅的証明にはしない" not in lawdb.get("inference_limit", ""):
        fail("law-database absence must not be treated as exhaustive proof")
    if not lawdb.get("next_blocker"):
        fail("law-database coverage check must preserve the final blocker")

    followups = {row.get("checked_at"): row for row in data.get("follow_up_checks", [])}
    follow = followups.get("2026-09-24", {})
    if follow.get("fresh_main_sha_at_start") != "b802b013213b485f26f54ca187b0bf53d79e8c18":
        fail("2026-09-24 follow-up must record the fresh main SHA")
    if follow.get("verified_post_r6_amendment_candidate_identified") is not False:
        fail("2026-09-24 follow-up must not promote a post-R6 amendment candidate")
    if follow.get("current_integrated_text_found") is not False:
        fail("2026-09-24 follow-up must keep current integrated text unresolved")
    if follow.get("decision_effect") != "HOLD_UNCHANGED":
        fail("2026-09-24 follow-up must preserve HOLD")
    if "2026-09-19から2026-09-24" not in follow.get("unresolved_gap", ""):
        fail("2026-09-24 follow-up must record the remaining publication gap")
    if not follow.get("next_blocker"):
        fail("2026-09-24 follow-up must preserve the next blocker")

    policy = data.get("status_policy", {})
    if "現行性の証明ではない" not in policy.get("machine_text_match", ""):
        fail("machine text match must not be described as proof of currentness")
    if "HOLD" not in policy.get("currentness", ""):
        fail("currentness policy must preserve HOLD")
    if "2025-03へ訂正済み" not in policy.get("currentness", ""):
        fail("currentness policy must record the corrected reference period")

    print("rouki25 currentness investigation: OK (post-R6 index/PDF/law-database systematic coverage recorded; official non-exhaustive limit pinned; 22 items remain HOLD)")


if __name__ == "__main__":
    main()
