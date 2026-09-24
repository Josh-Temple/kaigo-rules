#!/usr/bin/env python3
"""Validate pinned provenance for the 老企第25号 currentness ledger.

This validator detects stale evidence inputs; it does not prove that a search
index is complete or that an unindexed amendment does not exist.
"""
from __future__ import annotations

import hashlib
import json
from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
LEDGER_PATH = ROOT / "data" / "notice-rouki25-currentness-ledger.json"
PACKET_PATH = ROOT / "data" / "notice-review-packet.json"
EVENTS_PATH = ROOT / "data" / "notice-amendment-events.json"
SNAPSHOTS_PATH = ROOT / "data" / "notice-operation-modern-source-snapshots.json"
EXPECTED_CHECKPOINT_SOURCE = "mhlw-2024-interpretation-redline"
EXPECTED_R6_EVENT_IDS = {
    "rouki25.r6.dayservice.bcp-update",
    "rouki25.r6.dayservice.hygiene-transition-expiry",
    "rouki25.r6.dayservice.incorporation-web",
    "rouki25.r6.dayservice.physical-restraint",
}
EXPECTED_ITEM_COUNT = 22


def fail(message: str) -> None:
    raise SystemExit("rouki25 currentness ledger validation failed: " + message)


def load_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        fail(f"cannot read valid JSON from {path.relative_to(ROOT)}: {exc}")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_sha256(value) -> str:
    encoded = json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return sha256(encoded)


def main() -> None:
    ledger = load_json(LEDGER_PATH)
    packet = load_json(PACKET_PATH)
    events = load_json(EVENTS_PATH)
    snapshots = load_json(SNAPSHOTS_PATH)

    if ledger.get("scope") != "老企第25号「指定居宅サービス等及び指定介護予防サービス等に関する基準について」第3・六（通所介護）22 candidateのcurrentness":
        fail("unexpected scope")
    if ledger.get("checked_at") != "2026-09-23":
        fail("checked_at changed; refresh the research and report")
    if ledger.get("checkpoint", {}).get("status") != "NOT_FULLTEXT":
        fail("the R6 redline must not be represented as a full-text checkpoint")
    if ledger.get("checkpoint", {}).get("label_applied") is not None:
        fail("R6_OFFICIAL_FULLTEXT_CHECKPOINT must not be applied to an excerpt/redline")
    if ledger.get("checkpoint", {}).get("full_integrated_text") is not False:
        fail("checkpoint full-text assessment must remain false")

    checkpoint = ledger["checkpoint"]

    secondary = ledger.get("secondary_reference_context", {})
    if secondary.get("previous_repository_period_claim") != "2026-03":
        fail("previous reference-period claim must remain traceable")
    if secondary.get("repository_claimed_period") != "2025-03":
        fail("reference period must match earliest confirmed official parent publication context")
    if secondary.get("period_semantics") != "earliest_confirmed_official_parent_publication_context":
        fail("reference-period semantics are missing")
    if secondary.get("same_pdf_url_reused_across_r7_and_r8_parent_pages") is not True:
        fail("R7/R8 same-PDF reuse must remain explicit")
    if secondary.get("underlying_redline_amendment_date") != "UNRESOLVED_NOT_USED_AS_REFERENCE_PERIOD":
        fail("underlying redline amendment date must not be inferred")

    scan = ledger.get("post_r6_official_index_scan", {})
    if scan.get("decision_effect") != "HOLD_UNCHANGED":
        fail("post-R6 scan must not lift HOLD")
    if scan.get("candidate_post_r6_amendment_identified") is not False:
        fail("unexpected post-R6 amendment candidate state")
    required_scan_routes = {
        "mhlw-kaigo-latest-info-current",
        "mhlw-kaigo-latest-info-adjacent-index-31",
        "mhlw-kaigo-latest-info-adjacent-index-29",
        "mhlw-r8-reform-notification-list",
        "mhlw-r6-reform-baseline",
    }
    if {row.get("route_id") for row in scan.get("checked_routes", [])} != required_scan_routes:
        fail("post-R6 official index scan route set changed")
    source_rows = snapshots.get("sources", [])
    source = next((row for row in source_rows if row.get("source_id") == EXPECTED_CHECKPOINT_SOURCE), None)
    if source is None:
        fail("R6 checkpoint source is missing from the source snapshot manifest")
    if source.get("sha256") != checkpoint.get("pdf_sha256"):
        fail("R6 PDF hash differs from the recorded checkpoint hash")
    if source.get("url") != checkpoint.get("pdf_url"):
        fail("R6 PDF URL differs from the source snapshot manifest")
    if source.get("sha256") != checkpoint.get("source_manifest_sha256"):
        fail("checkpoint source-manifest hash pin differs")

    packet_items = packet.get("items", [])
    ledger_items = ledger.get("items", [])
    if len(packet_items) != EXPECTED_ITEM_COUNT or len(ledger_items) != EXPECTED_ITEM_COUNT:
        fail("expected exactly 22 packet and ledger items")
    packet_by_id = {item.get("notice_id"): item for item in packet_items}
    ledger_by_id = {item.get("notice_id"): item for item in ledger_items}
    if len(packet_by_id) != EXPECTED_ITEM_COUNT or set(packet_by_id) != set(ledger_by_id):
        fail("candidate notice IDs differ from the ledger")

    for notice_id, candidate in packet_by_id.items():
        item = ledger_by_id[notice_id]
        actual_candidate_hash = sha256(candidate.get("candidate_text", "").encode("utf-8"))
        if actual_candidate_hash != candidate.get("candidate_text_sha256"):
            fail(f"{notice_id}: packet candidate text does not match its declared hash")
        if actual_candidate_hash != item.get("candidate_text_sha256"):
            fail(f"{notice_id}: candidate hash changed since currentness review; refresh ledger")
        if candidate.get("human_verification_status") != "NOT_REVIEWED":
            fail(f"{notice_id}: human review status changed; update audit without auto-promotion")
        if item.get("audit_classification") != "HOLD":
            fail(f"{notice_id}: this investigation may not auto-promote an item")

    if ledger.get("final_audit_classification", {}).get("counts") != {
        "AUDIT_PASS": 0,
        "AUDIT_PASS_WITH_LIMITATION": 0,
        "HOLD": EXPECTED_ITEM_COUNT,
        "MISMATCH": 0,
    }:
        fail("final classification counts must remain 0/0/22/0")
    final = ledger["final_audit_classification"]
    if final.get("human_verified") is not False or final.get("verified_current") is not False:
        fail("HUMAN_VERIFIED and VERIFIED_CURRENT must remain false")
    if final.get("automatic_promotion_allowed") is not False:
        fail("automatic promotion must remain disabled")

    # The R6 changes are represented in the checkpoint itself. Any changed or
    # newly-added event dated on/after its effective date forces a fresh review.
    r6_events = [event for event in events if event.get("effective_from", "") >= "2024-04-01"]
    actual_ids = {event.get("id") for event in r6_events}
    if actual_ids != EXPECTED_R6_EVENT_IDS:
        fail("checkpoint-era or later amendment event set changed; review new/changed events")
    if set(ledger.get("validator_provenance", {}).get("r6_embedded_event_ids", [])) != EXPECTED_R6_EVENT_IDS:
        fail("ledger R6 event ID pin differs")
    actual_event_hash = canonical_sha256(sorted(r6_events, key=lambda event: event.get("id", "")))
    pinned_event_hash = ledger.get("validator_provenance", {}).get("r6_embedded_events_canonical_sha256")
    if actual_event_hash != pinned_event_hash:
        fail("checkpoint-era amendment event content changed; refresh currentness review")
    actual_event_file_hash = sha256(EVENTS_PATH.read_bytes())
    if actual_event_file_hash != ledger.get("validator_provenance", {}).get("amendment_events_file_sha256_at_audit"):
        fail("amendment-events file changed; inspect and refresh currentness review")

    coverage_end = date.fromisoformat(ledger["search_coverage"]["coverage_end"])
    today = datetime.now(ZoneInfo("Asia/Tokyo")).date()
    pass_count = final["counts"]["AUDIT_PASS"] + final["counts"]["AUDIT_PASS_WITH_LIMITATION"]
    if today > coverage_end:
        if pass_count:
            fail("coverage end is in the past; PASS currentness decision has expired")
        print(
            f"WARNING: currentness evidence expired on {coverage_end.isoformat()}; "
            "22 items remain HOLD and require new coverage."
        )
    else:
        print(f"currentness coverage is not past its end date ({coverage_end.isoformat()})")

    print("rouki25 currentness ledger: OK (provenance pinned; 22 HOLD; no automatic promotion)")


if __name__ == "__main__":
    main()
