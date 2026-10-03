#!/usr/bin/env python3
"""Pin a successful service Rouki 25 historical verification as an audit receipt."""
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERIFIER = ROOT / "scripts/verify_rouki25_historical_service_independent.py"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def blob(path: Path) -> str:
    body = path.read_bytes()
    return hashlib.sha1(f"blob {len(body)}\0".encode("ascii") + body).hexdigest()


def fail(message: str) -> None:
    raise SystemExit("cannot pin Rouki 25 historical audit: " + message)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--service-id", required=True)
    parser.add_argument("--expected-items", type=int, required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--run-id", type=int, required=True)
    parser.add_argument("--head-sha", required=True)
    parser.add_argument("--workflow", required=True)
    args = parser.parse_args()

    service_id = args.service_id
    scope_path = ROOT / f"data/services/{service_id}/rouki25-scope.json"
    dataset_path = ROOT / f"data/services/{service_id}/rouki25-historical.generated.json"
    receipt_path = ROOT / f"data/{service_id}-rouki25-historical-independent-audit.json"

    scope = load(scope_path)
    dataset = load(dataset_path)
    report = load(args.report)

    if scope.get("service_id") != service_id:
        fail("scope service mismatch")
    if dataset.get("service_id") != service_id:
        fail("dataset service mismatch")
    if report.get("service_id") != service_id:
        fail("report service mismatch")
    if report.get("verification_kind") != "INDEPENDENT_SERVICE_ROUKI25_HISTORICAL_SOURCE_AUDIT":
        fail("unexpected verification kind")
    if report.get("result") != "PASS" or report.get("errors") != []:
        fail("independent verification did not pass cleanly")
    if dataset.get("item_count") != args.expected_items:
        fail("dataset item count mismatch")
    if report.get("coverage") != {
        "principal_items": args.expected_items,
        "items_passed": args.expected_items,
    }:
        fail("report coverage mismatch")
    checks = report.get("checks", [])
    if len(checks) != args.expected_items or any(
        item.get("result") != "PASS" or item.get("differences") != []
        for item in checks
    ):
        fail("item checks are not all clean")
    if dataset.get("source", {}).get("sha256") != report.get("source", {}).get("sha256"):
        fail("dataset/report source hash mismatch")

    report_sha256 = hashlib.sha256(args.report.read_bytes()).hexdigest()
    receipt = {
        "format_version": 1,
        "service_id": service_id,
        "scope": f"{service_id}-rouki25-official-historical-html-section",
        "audit_kind": "INDEPENDENT_SERVICE_ROUKI25_HISTORICAL_SOURCE_AUDIT",
        "audit_result": "PASS",
        "audited_at": date.today().isoformat(),
        "audit_run": {
            "workflow": args.workflow,
            "run_id": args.run_id,
            "head_sha": args.head_sha,
            "parser": report.get("parser"),
            "verification_report_sha256": report_sha256,
        },
        "source": report.get("source"),
        "checks": checks,
        "coverage": report.get("coverage"),
        "input_git_blob_shas_at_audit": {
            str(scope_path.relative_to(ROOT)): blob(scope_path),
            str(dataset_path.relative_to(ROOT)): blob(dataset_path),
            str(VERIFIER.relative_to(ROOT)): blob(VERIFIER),
        },
        "conclusion": (
            f"All {args.expected_items} principal items in the bounded {service_id} "
            "Rouki 25 historical HTML section matched the official MHLW source "
            "under an independent text-extraction path."
        ),
        "limitations": [
            "This proves historical-source transcription, not current integrated notice text.",
            "The R6 old/new comparison remains separate amendment evidence and omitted text is not reconstructed.",
            "Human review and exhaustive currentness review are not complete.",
        ],
        "safety": {
            "historical_source_only": True,
            "current_integrated_text": False,
            "human_verified": False,
            "verified_current": False,
            "automatic_promotion_allowed": False,
        },
    }
    receipt_path.write_text(
        json.dumps(receipt, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"wrote {receipt_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
