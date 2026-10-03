#!/usr/bin/env python3
"""Validate a pinned service Rouki 25 historical-source audit receipt."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def fail(service_id: str, message: str) -> None:
    raise SystemExit(
        f"{service_id} Rouki 25 historical audit validation failed: {message}"
    )


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def blob(path: Path) -> str:
    body = path.read_bytes()
    return hashlib.sha1(f"blob {len(body)}\0".encode("ascii") + body).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--service-id", required=True)
    parser.add_argument("--expected-items", required=True, type=int)
    args = parser.parse_args()
    service_id = args.service_id
    receipt_path = ROOT / f"data/{service_id}-rouki25-historical-independent-audit.json"
    dataset_path = ROOT / f"data/services/{service_id}/rouki25-historical.generated.json"

    if not receipt_path.exists():
        fail(service_id, "receipt missing")
    receipt = load(receipt_path)
    if (
        receipt.get("service_id") != service_id
        or receipt.get("scope")
        != f"{service_id}-rouki25-official-historical-html-section"
        or receipt.get("audit_kind")
        != "INDEPENDENT_SERVICE_ROUKI25_HISTORICAL_SOURCE_AUDIT"
        or receipt.get("audit_result") != "PASS"
    ):
        fail(service_id, "unexpected identity/result")

    run = receipt.get("audit_run", {})
    if not isinstance(run.get("run_id"), int) or run["run_id"] <= 0:
        fail(service_id, "invalid run")
    if not re.fullmatch(r"[0-9a-f]{40}", str(run.get("head_sha") or "")):
        fail(service_id, "invalid head sha")
    if not re.fullmatch(
        r"[0-9a-f]{64}", str(run.get("verification_report_sha256") or "")
    ):
        fail(service_id, "invalid report sha")

    checks = receipt.get("checks", [])
    if (
        len(checks) != args.expected_items
        or any(
            item.get("result") != "PASS"
            or item.get("differences") != []
            for item in checks
        )
    ):
        fail(service_id, "item checks not clean")
    if receipt.get("coverage") != {
        "principal_items": args.expected_items,
        "items_passed": args.expected_items,
    }:
        fail(service_id, "coverage changed")

    safety = receipt.get("safety", {})
    if (
        safety.get("historical_source_only") is not True
        or safety.get("current_integrated_text") is not False
        or safety.get("human_verified") is not False
        or safety.get("verified_current") is not False
        or safety.get("automatic_promotion_allowed") is not False
    ):
        fail(service_id, "unsafe state")

    dataset = load(dataset_path)
    if dataset.get("service_id") != service_id:
        fail(service_id, "dataset service mismatch")
    if dataset.get("item_count") != args.expected_items:
        fail(service_id, "dataset item count changed")
    if dataset.get("source", {}).get("sha256") != receipt.get(
        "source", {}
    ).get("sha256"):
        fail(service_id, "source hash mismatch between dataset and audit")

    for relative_path, expected in receipt.get(
        "input_git_blob_shas_at_audit", {}
    ).items():
        path = ROOT / relative_path
        if not path.exists() or blob(path) != expected:
            fail(service_id, f"pinned input changed: {relative_path}")

    print(
        f"{service_id} Rouki 25 historical audit: OK "
        f"({args.expected_items}/{args.expected_items} PASS; currentness remains GAP)"
    )


if __name__ == "__main__":
    main()
