#!/usr/bin/env python3
"""Validate the existing-service currentness wave without promoting downstream gates."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECEIPT_PATH = ROOT / "data/verification/existing-service-currentness-wave.json"
REGISTRY_PATH = ROOT / "data/verification-registry.json"
GATES_PATH = ROOT / "data/verification/standards-interpretation-gates.json"
EVIDENCE = "data/verification/existing-service-currentness-wave.json"
ROUKI25_WATCH = ".github/workflows/watch-notice-rouki25-currentness.yml"

EXPECTED_CELLS = {
    ("dayservice", "standards_interpretation_notice"),
    ("dayservice", "fee_calculation_guidance"),
    ("homevisit", "standards_interpretation_notice"),
    ("homebath", "standards_interpretation_notice"),
    ("homenursing", "standards_interpretation_notice"),
    ("homerehab", "standards_interpretation_notice"),
    ("homecaremanagement", "standards_interpretation_notice"),
    ("dayrehab", "governing_standards_ordinance"),
    ("dayrehab", "standards_interpretation_notice"),
    ("dayrehab", "remuneration_notification"),
    ("dayrehab", "delegated_remuneration_criteria"),
    ("dayrehab", "fee_calculation_guidance"),
    ("shortstay-life", "standards_interpretation_notice"),
    ("community-dayservice", "standards_interpretation_notice"),
    ("regular-round", "standards_interpretation_notice"),
    ("night-homevisit", "standards_interpretation_notice"),
    ("care-management", "standards_interpretation_notice"),
    ("preventive-support", "standards_interpretation_notice"),
}

EVIDENCE_LINKED_LAYERS = {
    "rouki36-dayservice": "MONITORED_NOT_HUMAN_VERIFIED",
    "rouki25-homevisit": "GAP_HISTORICAL_SOURCE_ONLY",
    "rouki25-homebath": "GAP_HISTORICAL_SOURCE_ONLY",
    "rouki25-homenursing": "GAP_HISTORICAL_SOURCE_ONLY",
    "rouki25-homerehab": "GAP_HISTORICAL_SOURCE_ONLY",
    "rouki25-homecaremanagement": "GAP_HISTORICAL_SOURCE_ONLY",
    "rouki25-dayrehab": "GAP_HISTORICAL_SOURCE_ONLY",
    "rouki25-shortstay-life": "GAP_HISTORICAL_SOURCE_ONLY",
    "ordinance37-dayrehab": "LIVE_SOURCE_REPARSE_SCHEDULED",
    "remuneration-dayrehab": "GAP",
    "fee-guidance-dayrehab": "GAP",
}

FAMILY_WATCH_LAYERS = {
    "rouki25-homevisit",
    "rouki25-homebath",
    "rouki25-homenursing",
    "rouki25-homerehab",
    "rouki25-homecaremanagement",
    "rouki25-dayrehab",
    "rouki25-shortstay-life",
}


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    errors: list[str] = []
    receipt = load(RECEIPT_PATH)
    registry = load(REGISTRY_PATH)
    gates = load(GATES_PATH)

    rows = receipt.get("cells", [])
    identities = {(row.get("service_id"), row.get("source_family")) for row in rows}
    if identities != EXPECTED_CELLS:
        errors.append("target cell set differs from the mechanically extracted 18-cell wave")
    if receipt.get("target_selection", {}).get("target_cells") != 18:
        errors.append("target cell count must remain 18")
    if receipt.get("target_selection", {}).get("service_count") != 13:
        errors.append("target service count must remain 13")

    summary = receipt.get("summary", {})
    required_summary = {
        "target_cells": 18,
        "currentness_established": 0,
        "hold_or_gap_maintained": 18,
        "source_disappeared": 0,
        "superseded_confirmed": 0,
        "unresolved": 18,
    }
    for key, expected in required_summary.items():
        if summary.get(key) != expected:
            errors.append(f"summary {key} drifted: {summary.get(key)!r} != {expected!r}")

    for row in rows:
        if row.get("currentness_after") != row.get("currentness_before"):
            errors.append(
                f"{row.get('service_id')}/{row.get('source_family')}: currentness changed in evidence-only wave"
            )
        if row.get("currentness_after") == "PASS":
            errors.append(
                f"{row.get('service_id')}/{row.get('source_family')}: currentness unexpectedly promoted"
            )

    safety = receipt.get("safety", {})
    for key in (
        "service_scope_changed",
        "item_body_promoted",
        "currentness_auto_promoted",
        "human_review_promoted",
        "publication_promoted",
        "route_enabled",
        "negative_search_used_as_proof",
    ):
        if safety.get(key) is not False:
            errors.append(f"safety boundary broken: {key}")

    observations = {row.get("id"): row for row in receipt.get("official_source_observations", [])}
    for source_id in ("mhlw-rouki25-lawdb-html", "mhlw-rouki36-lawdb-html"):
        if observations.get(source_id, {}).get("classification") != (
            "HISTORICAL_OR_STALE_OFFICIAL_HTML_NOT_CURRENT_INTEGRATED_TEXT"
        ):
            errors.append(f"{source_id}: stale official HTML must remain non-current evidence")
    if observations.get("mhlw-kaigo-info-vol1545", {}).get(
        "negative_discovery_proves_no_change"
    ) is not False:
        errors.append("Vol.1545 negative discovery must not be proof of no change")
    if observations.get("mhlw-r8-reform-index", {}).get(
        "negative_discovery_proves_no_change"
    ) is not False:
        errors.append("R8 index negative discovery must not be proof of no change")

    registry_layers = {row["id"]: row for row in registry.get("layers", [])}
    for layer_id, expected_status in EVIDENCE_LINKED_LAYERS.items():
        layer = registry_layers.get(layer_id)
        if not layer:
            errors.append(f"registry layer missing: {layer_id}")
            continue
        currentness = layer.get("currentness", {})
        if currentness.get("status") != expected_status:
            errors.append(
                f"{layer_id}: currentness status changed: {currentness.get('status')!r}"
            )
        if currentness.get("evidence") != EVIDENCE:
            errors.append(f"{layer_id}: wave currentness evidence not linked")
        human_state = str(layer.get("human_review", {}).get("status", ""))
        if "VERIFIED" in human_state:
            errors.append(f"{layer_id}: human review unexpectedly promoted")

    for layer_id in FAMILY_WATCH_LAYERS:
        monitoring = registry_layers.get(layer_id, {}).get("monitoring", {})
        workflows = {monitoring.get("workflow"), monitoring.get("additional_workflow")}
        if monitoring.get("status") != "ACTIVE" or ROUKI25_WATCH not in workflows:
            errors.append(f"{layer_id}: family-level currentness watch not active")

    dayservice = registry_layers.get("rouki25-dayservice", {})
    if dayservice.get("currentness", {}).get("status") != "HOLD":
        errors.append("rouki25-dayservice: HOLD must remain unchanged")

    gate_rows = {row["service_id"]: row for row in gates.get("services", [])}
    for service_id in (
        "community-dayservice",
        "regular-round",
        "night-homevisit",
        "care-management",
        "preventive-support",
    ):
        row = gate_rows.get(service_id)
        if not row:
            errors.append(f"missing standards gate: {service_id}")
            continue
        if row.get("currentness", {}).get("state") != "NOT_ESTABLISHED":
            errors.append(f"{service_id}: standards currentness unexpectedly promoted")
        if row.get("human_review", {}).get("state") != "NOT_REVIEWED":
            errors.append(f"{service_id}: human review unexpectedly promoted")
        if row.get("publication", {}).get("allowed") is not False:
            errors.append(f"{service_id}: publication unexpectedly promoted")
        if row.get("route", {}).get("enabled") is not False:
            errors.append(f"{service_id}: route unexpectedly enabled")

    if errors:
        for error in errors:
            print("FAIL existing-service currentness wave:", error)
        return 1
    print("PASS existing-service currentness wave: 18 cells remain fail-closed with stronger evidence")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
