#!/usr/bin/env python3
"""Validate the bounded durable receipt for the latest 老企第25号 currentness watch."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
RECEIPT = DATA / "notice-rouki25-watch-latest.json"
CONFIG = DATA / "notice-rouki25-watch-config.json"
LEDGER = DATA / "notice-rouki25-currentness-ledger.json"


def fail(message: str) -> None:
    raise SystemExit("rouki25 watch receipt validation failed: " + message)


def load(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        fail(f"cannot read valid JSON from {path.relative_to(ROOT)}: {exc}")


def main() -> None:
    receipt = load(RECEIPT)
    config = load(CONFIG)
    ledger = load(LEDGER)

    if receipt.get("verification_kind") != "ROUKI25_CURRENTNESS_WATCH_RECEIPT":
        fail("unexpected receipt kind")
    if receipt.get("result") != "PASS":
        fail("receipt result is not PASS")
    if receipt.get("source_errors") != []:
        fail("receipt contains source errors")
    if receipt.get("review_triggers") != []:
        fail("receipt contains review triggers")

    run = receipt.get("source_run", {})
    if run.get("result") != "PASS":
        fail("source workflow result is not PASS")
    if not isinstance(run.get("run_id"), int) or run["run_id"] <= 0:
        fail("invalid source workflow run id")
    if not isinstance(run.get("artifact_id"), int) or run["artifact_id"] <= 0:
        fail("invalid source artifact id")
    if not re.fullmatch(r"[0-9a-f]{40}", str(run.get("head_sha") or "")):
        fail("invalid source head sha")
    if not re.fullmatch(r"[0-9a-f]{64}", str(run.get("artifact_sha256") or "")):
        fail("invalid artifact sha256")

    before = receipt.get("baseline_before", {})
    observed = receipt.get("observed", {})
    latest = observed.get("latest_kaigo_info", {})
    effect = receipt.get("effect", {})
    baseline = config.get("baseline", {})

    if before.get("latest_confirmed_kaigo_info_volume") != 1544:
        fail("historical baseline before the receipt changed")
    if latest.get("volume") != 1545:
        fail("expected Vol.1545 as the newly observed entry")
    if latest.get("listed_date") != "2026-10-02":
        fail("unexpected Vol.1545 listed date")
    if latest.get("body_scan") != "OK" or latest.get("target_term_matches") != []:
        fail("Vol.1545 was not cleanly scanned")
    if "Vol.1545" not in str(latest.get("title") or ""):
        fail("Vol.1545 title missing")

    if baseline.get("latest_confirmed_kaigo_info_volume") != latest.get("volume"):
        fail("watch baseline volume is not aligned to the durable receipt")
    if baseline.get("latest_confirmed_kaigo_info_date") != latest.get("listed_date"):
        fail("watch baseline date is not aligned to the durable receipt")
    if effect.get("baseline_advanced_to_volume") != latest.get("volume"):
        fail("receipt baseline effect volume changed")
    if effect.get("baseline_advanced_to_date") != latest.get("listed_date"):
        fail("receipt baseline effect date changed")

    pinned = observed.get("pinned_pdf_checks", [])
    if len(pinned) != 2:
        fail("expected two pinned PDF checks")
    by_label = {row.get("label"): row for row in pinned}
    expected_hashes = {
        "R6 redline": ledger.get("checkpoint", {}).get("pdf_sha256"),
        "secondary reference": ledger.get("secondary_reference_context", {}).get("sha256"),
    }
    for label, expected_hash in expected_hashes.items():
        row = by_label.get(label)
        if not row:
            fail(f"missing pinned PDF check: {label}")
        if row.get("match") is not True:
            fail(f"pinned PDF mismatch: {label}")
        if row.get("expected_sha256") != expected_hash:
            fail(f"pinned PDF expected hash differs from currentness ledger: {label}")
        if row.get("observed_sha256") != expected_hash:
            fail(f"pinned PDF observed hash differs from currentness ledger: {label}")

    pages = observed.get("watched_official_pages", [])
    if {row.get("id") for row in pages} != {
        "r8_reform_notifications",
        "notification_new_index",
    }:
        fail("watched official page set changed")
    if any(row.get("target_term_matches") != [] for row in pages):
        fail("watched official page contains a target term trigger")

    amendment = observed.get("law_database_amendment_list", {})
    if amendment.get("scan") != "OK":
        fail("law-database amendment list was not scanned")
    if amendment.get("target_term_matches") != []:
        fail("law-database amendment list contains a target trigger")

    final = ledger.get("final_audit_classification", {})
    if final.get("decision") != "HOLD":
        fail("underlying currentness ledger no longer remains HOLD")
    if final.get("counts", {}).get("HOLD") != 22:
        fail("expected all 22 day-service candidates to remain HOLD")
    if final.get("human_verified") is not False:
        fail("currentness ledger must not claim human verification")
    if final.get("verified_current") is not False:
        fail("currentness ledger must not claim verified current")
    if final.get("automatic_promotion_allowed") is not False:
        fail("currentness ledger automatic promotion must remain disabled")

    safety = receipt.get("safety", {})
    for key in ("human_verified", "verified_current", "automatic_promotion_allowed", "hold_changed"):
        if safety.get(key) is not False:
            fail(f"receipt safety flag must remain false: {key}")
    if effect.get("currentness_decision") != "HOLD_UNCHANGED":
        fail("receipt must not change the currentness decision")

    policy = config.get("policy", {})
    if policy.get("read_only") is not True:
        fail("watch policy must remain read-only")
    if policy.get("automatic_promotion_allowed") is not False:
        fail("watch policy automatic promotion must remain disabled")

    print(
        "rouki25 watch receipt: OK "
        "(Vol.1545 scanned cleanly; baseline advanced; HOLD unchanged)"
    )


if __name__ == "__main__":
    main()
