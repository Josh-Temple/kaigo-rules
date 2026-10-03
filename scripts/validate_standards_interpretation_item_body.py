#!/usr/bin/env python3
"""Validate integrated standards-interpretation item-body verification receipts."""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ALLOWED = ("PASS", "PARTIAL", "GAP", "FAIL")
SERVICES = {
    "community-dayservice": 21,
    "regular-round": 21,
    "night-homevisit": 25,
    "care-management": 32,
    "preventive-support": 34,
}


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def observed_counts(receipt: dict) -> dict[str, int]:
    rows = receipt.get("items")
    key = "status"
    if rows is None:
        rows = receipt.get("tasks")
        key = "result"
    if rows is None:
        raise ValueError("receipt has neither items nor tasks")
    counts = Counter(row.get(key) for row in rows)
    unknown = sorted(value for value in counts if value not in ALLOWED)
    if unknown:
        raise ValueError(f"unknown verdicts: {unknown}")
    return {name: counts.get(name, 0) for name in ALLOWED}


def expected_status(counts: dict[str, int]) -> str:
    if counts["FAIL"]:
        return "FAIL"
    if counts["PARTIAL"] or counts["GAP"]:
        return "PARTIAL_WITH_GAPS"
    return "PASS_CONTENT_EVIDENCE_MATCH_ONLY"


def expected_service_status(verification_status: str) -> str:
    if verification_status == "PASS_CONTENT_EVIDENCE_MATCH_ONLY":
        return "ITEM_BODY_VERIFIED_CURRENTNESS_PENDING"
    if verification_status == "PARTIAL_WITH_GAPS":
        return "SOURCE_INVENTORY_VERIFIED_ITEM_BODY_GAPS_REMAIN"
    return "SOURCE_INVENTORY_VERIFIED_ITEM_BODY_FAILED"


def validate_service(service_id: str) -> list[str]:
    errors: list[str] = []
    expected_items = SERVICES[service_id]
    receipt_path = ROOT / "data/verification/standards-interpretation-item-body" / f"{service_id}.json"
    staging_path = ROOT / f"data/services/{service_id}/standards-interpretation-staging.json"
    service_path = ROOT / f"data/services/{service_id}.json"

    receipt = load(receipt_path)
    staging = load(staging_path)
    service = load(service_path)
    summary = receipt.get("integration_summary", {})

    if receipt.get("service_id") != service_id:
        errors.append("receipt service_id mismatch")
    if summary.get("schema_version") != 1:
        errors.append("missing common integration_summary schema v1")
    if summary.get("audit_receipt") != str(receipt_path.relative_to(ROOT)):
        errors.append("audit receipt path mismatch")
    verifier = summary.get("verifier")
    if not verifier or not (ROOT / verifier).exists():
        errors.append("verifier path missing")
    if not summary.get("worker_pr") or not summary.get("worker_head_sha"):
        errors.append("worker provenance incomplete")

    try:
        counts = observed_counts(receipt)
    except ValueError as exc:
        errors.append(str(exc))
        counts = {name: 0 for name in ALLOWED}

    if summary.get("counts") != counts:
        errors.append("common counts differ from receipt evidence")
    if sum(counts.values()) != expected_items:
        errors.append(f"receipt verdict total {sum(counts.values())} != expected {expected_items}")
    if summary.get("expected_staging_items_or_tasks") != expected_items:
        errors.append("common expected item count mismatch")
    if summary.get("non_pass_items") != counts["PARTIAL"] + counts["GAP"] + counts["FAIL"]:
        errors.append("non-pass count mismatch")

    verification_status = expected_status(counts)
    if summary.get("verification_status") != verification_status:
        errors.append("common verification status mismatch")

    layer = service.get("ingestion_layers", {}).get("standards_interpretation", {})
    if layer.get("source_inventory_verification") != "PASS_BOUNDED_SCOPE_ONLY":
        errors.append("source inventory state changed or missing")
    if layer.get("item_body_verification") != verification_status:
        errors.append("service item_body_verification mismatch")
    if layer.get("item_body_verification_counts") != counts:
        errors.append("service item_body_verification_counts mismatch")
    if layer.get("item_body_verification_receipt") != str(receipt_path.relative_to(ROOT)):
        errors.append("service receipt pointer mismatch")
    if layer.get("status") != expected_service_status(verification_status):
        errors.append("service integration status mismatch")

    declared = staging.get("item_count", staging.get("task_count"))
    if declared != expected_items or len(staging.get("items", [])) != expected_items:
        errors.append("staging count mismatch")
    if staging.get("currentness_state") != "NOT_ESTABLISHED":
        errors.append("currentness was promoted")
    if staging.get("human_review_state") != "NOT_REVIEWED":
        errors.append("human review was promoted")
    if staging.get("publication_state") != "NOT_PUBLIC":
        errors.append("staging publication state was promoted")

    if summary.get("source_inventory_state") != "PASS_BOUNDED_SCOPE_ONLY":
        errors.append("integration source inventory state mismatch")
    if summary.get("currentness_state") != "NOT_ESTABLISHED":
        errors.append("integration currentness state mismatch")
    if summary.get("human_review_state") != "NOT_REVIEWED":
        errors.append("integration human review state mismatch")
    for key in (
        "publication_allowed",
        "public_route_enabled",
        "staging_summary_treated_as_official_notice_text",
        "omitted_text_inferred",
        "service_scope_expanded",
    ):
        if summary.get(key) is not False:
            errors.append(f"integration_summary.{key} must remain false")

    gate = service.get("publication_gate", {})
    for key in (
        "public_routes_enabled",
        "content_ingested",
        "independent_verification_complete",
        "human_review_complete",
    ):
        if gate.get(key) is not False:
            errors.append(f"publication_gate.{key} was promoted")
    if service.get("routing", {}).get("future_service_base_enabled") is not False:
        errors.append("service route was enabled")

    if service_id == "preventive-support":
        if staging.get("service_package_state") != "SEPARATE_PRECHECK_BLOCKER_PRESERVED":
            errors.append("preventive-support PACKAGE blocker separation changed")
        if summary.get("package_blocker_state") != "BLOCKED_KR2-10-E006":
            errors.append("preventive-support PACKAGE blocker not preserved")
    elif summary.get("package_blocker_state") != "NOT_APPLICABLE":
        errors.append("unexpected package blocker state")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--all", action="store_true")
    group.add_argument("--service-id", choices=sorted(SERVICES))
    args = parser.parse_args()

    service_ids = list(SERVICES) if args.all else [args.service_id]
    failed = False
    for service_id in service_ids:
        errors = validate_service(service_id)
        if errors:
            failed = True
            for error in errors:
                print(f"FAIL {service_id}: {error}")
        else:
            receipt = load(ROOT / "data/verification/standards-interpretation-item-body" / f"{service_id}.json")
            summary = receipt["integration_summary"]
            counts = summary["counts"]
            print(
                f"PASS {service_id}: {summary['verification_status']} "
                f"(PASS={counts['PASS']} PARTIAL={counts['PARTIAL']} "
                f"GAP={counts['GAP']} FAIL={counts['FAIL']})"
            )
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
