#!/usr/bin/env python3
"""Validate the regular-round standards-interpretation item-body verification receipt.

This service-specific validator checks receipt/staging identity, result counts,
source-role consistency, and fail-closed safety invariants. It does not re-fetch
official sources and does not establish currentness, human review, publication
readiness, or an integrated current interpretation-notice text.
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SERVICE_ID = "regular-round"
EXPECTED_ITEMS = 21
ALLOWED_RESULTS = {"PASS", "PARTIAL", "GAP", "FAIL"}

STAGING = ROOT / "data/services/regular-round/standards-interpretation-staging.json"
RECEIPT = ROOT / "data/verification/standards-interpretation-item-body/regular-round.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    differences: list[str] = []
    staging = load(STAGING)
    receipt = load(RECEIPT)

    if staging.get("service_id") != SERVICE_ID:
        differences.append("staging service_id mismatch")
    if receipt.get("service_id") != SERVICE_ID:
        differences.append("receipt service_id mismatch")
    if receipt.get("audit_kind") != "INDEPENDENT_ITEM_BODY_VERIFICATION":
        differences.append("unexpected audit_kind")
    if receipt.get("verification_scope") != "CONTENT_EVIDENCE_MATCH_ONLY_NOT_CURRENTNESS":
        differences.append("verification scope must remain content/evidence-only")

    staging_items = staging.get("items", [])
    receipt_items = receipt.get("items", [])
    declared = staging.get("item_count")
    if declared != EXPECTED_ITEMS or len(staging_items) != EXPECTED_ITEMS:
        differences.append(
            f"staging count mismatch: declared={declared} observed={len(staging_items)} "
            f"expected={EXPECTED_ITEMS}"
        )
    if len(receipt_items) != EXPECTED_ITEMS:
        differences.append(
            f"receipt count mismatch: observed={len(receipt_items)} expected={EXPECTED_ITEMS}"
        )

    source_catalog = {
        row.get("id"): row
        for row in receipt.get("source_catalog", [])
        if isinstance(row, dict) and row.get("id")
    }
    if not source_catalog:
        differences.append("source_catalog is empty")

    fields = ("id", "task_id", "path", "number", "heading", "content_summary")
    for index, (staged, audited) in enumerate(zip(staging_items, receipt_items), start=1):
        for field in fields:
            if staged.get(field) != audited.get(field):
                differences.append(
                    f"item {index} {field} mismatch: "
                    f"staging={staged.get(field)!r} receipt={audited.get(field)!r}"
                )

        result = audited.get("result")
        if result not in ALLOWED_RESULTS:
            differences.append(f"{audited.get('id')}: invalid result {result!r}")

        evidence = audited.get("evidence", [])
        if result == "PASS" and not evidence:
            differences.append(f"{audited.get('id')}: PASS without evidence")
        for row in evidence:
            source_id = row.get("source_id")
            source = source_catalog.get(source_id)
            if source is None:
                differences.append(f"{audited.get('id')}: unknown source_id {source_id!r}")
                continue
            if row.get("url") != source.get("url"):
                differences.append(f"{audited.get('id')}: source URL mismatch for {source_id}")
            if row.get("source_role") != source.get("role"):
                differences.append(f"{audited.get('id')}: source role mismatch for {source_id}")
            if not row.get("locator") or not row.get("support_summary"):
                differences.append(f"{audited.get('id')}: incomplete evidence locator/support")

        if audited.get("omitted_text_policy") != "NO_CURRENT_TEXT_RECONSTRUCTION":
            differences.append(f"{audited.get('id')}: omitted-text policy is not fail-closed")
        if audited.get("currentness") != "NOT_EVALUATED":
            differences.append(f"{audited.get('id')}: currentness must remain NOT_EVALUATED")

    actual_counts = Counter(
        row.get("result") for row in receipt_items if row.get("result") in ALLOWED_RESULTS
    )
    expected_counts = receipt.get("coverage", {}).get("result_counts", {})
    for status in ("PASS", "PARTIAL", "GAP", "FAIL"):
        if expected_counts.get(status) != actual_counts.get(status, 0):
            differences.append(
                f"result count mismatch for {status}: "
                f"declared={expected_counts.get(status)} actual={actual_counts.get(status, 0)}"
            )

    safety = receipt.get("safety", {})
    required_false = (
        "currentness_promoted",
        "human_review_promoted",
        "publication_permitted",
        "route_enabled",
        "current_integrated_notice_text_reconstructed",
        "staging_summary_treated_as_official_notice_text",
    )
    for key in required_false:
        if safety.get(key) is not False:
            differences.append(f"safety invariant must be false: {key}")

    expected_result = "PASS_CONTENT_EVIDENCE_MATCH_ONLY" if not differences else "FAIL"
    if receipt.get("audit_result") != expected_result:
        differences.append(
            f"audit_result mismatch: declared={receipt.get('audit_result')!r} "
            f"expected={expected_result!r}"
        )

    report = {
        "service_id": SERVICE_ID,
        "validator": Path(__file__).name,
        "expected_items": EXPECTED_ITEMS,
        "observed_items": len(receipt_items),
        "result_counts": {
            status: actual_counts.get(status, 0)
            for status in ("PASS", "PARTIAL", "GAP", "FAIL")
        },
        "validation_result": "PASS" if not differences else "FAIL",
        "differences": differences,
        "safety": {
            "proves_currentness": False,
            "proves_human_review": False,
            "permits_publication": False,
        },
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if not differences else 1


if __name__ == "__main__":
    sys.exit(main())
