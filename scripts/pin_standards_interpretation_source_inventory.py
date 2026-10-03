#!/usr/bin/env python3
"""Pin a successful standards-interpretation source inventory as a durable receipt."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERIFIER = ROOT / "scripts/verify_standards_interpretation_sources_independent.py"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def blob(path: Path) -> str:
    body = path.read_bytes()
    return hashlib.sha1(f"blob {len(body)}\0".encode("ascii") + body).hexdigest()


def fail(message: str) -> None:
    raise SystemExit("cannot pin standards-interpretation source inventory: " + message)


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
    scope_path = ROOT / f"data/services/{service_id}/standards-interpretation-scope.json"
    staging_path = ROOT / f"data/services/{service_id}/standards-interpretation-staging.json"
    receipt_path = (
        ROOT
        / "data/verification/standards-interpretation-source-inventory"
        / f"{service_id}.json"
    )

    scope = load(scope_path)
    report = load(args.report)
    if report.get("service_id") != service_id:
        fail("report service mismatch")
    if report.get("audit_kind") != "INDEPENDENT_STANDARDS_INTERPRETATION_SOURCE_INVENTORY":
        fail("unexpected audit kind")
    if report.get("audit_result") != "PASS_BOUNDED_SCOPE_ONLY":
        fail("report did not pass bounded source inventory")
    if report.get("differences") != []:
        fail("report contains differences")

    coverage = report.get("coverage", {})
    if coverage.get("expected_staging_items_or_tasks") != args.expected_items:
        fail("expected item/task count mismatch")
    if coverage.get("observed_staging_items_or_tasks") != args.expected_items:
        fail("observed item/task count mismatch")

    manifest_required_urls = sorted(
        row["url"]
        for row in scope.get("source_manifest", [])
        if isinstance(row, dict)
        and row.get("url")
        and row.get("required_for_source_inventory") is True
    )
    if coverage.get("manifest_required_sources") != len(manifest_required_urls):
        fail("manifest required-source count mismatch")
    if coverage.get("required_sources") != len(manifest_required_urls):
        fail("report does not cover every manifest-required source")
    if coverage.get("required_sources_fetchable") != coverage.get("required_sources"):
        fail("not all required sources were fetchable")

    source_rows = {
        row.get("url"): row
        for row in report.get("sources", [])
        if isinstance(row, dict) and row.get("url")
    }
    missing_required = sorted(set(manifest_required_urls) - set(source_rows))
    if missing_required:
        fail(f"manifest-required source rows missing: {missing_required}")
    for url in manifest_required_urls:
        row = source_rows[url]
        if row.get("required_for_source_inventory") is not True:
            fail(f"manifest-required source lost required flag: {url}")
        if row.get("fetch") != "PASS":
            fail(f"manifest-required source not fetchable: {url}")

    safety = report.get("safety", {})
    forbidden_true = [
        "item_body_match_proven",
        "currentness_promoted",
        "human_review_promoted",
        "omitted_text_reconstructed",
        "publication_permitted",
    ]
    if any(safety.get(key) is not False for key in forbidden_true):
        fail("report safety boundary was weakened")

    receipt = {
        "format_version": 1,
        "service_id": service_id,
        "audit_kind": report["audit_kind"],
        "audit_result": report["audit_result"],
        "check_level": report.get("check_level"),
        "source_family": report.get("source_family"),
        "audit_run": {
            "workflow": args.workflow,
            "run_id": args.run_id,
            "head_sha": args.head_sha,
            "verifier": str(VERIFIER.relative_to(ROOT)),
            "report_sha256": hashlib.sha256(args.report.read_bytes()).hexdigest(),
        },
        "coverage": coverage,
        "sources": report.get("sources", []),
        "safety": safety,
        "differences": report.get("differences", []),
        "input_git_blob_shas_at_audit": {
            str(scope_path.relative_to(ROOT)): blob(scope_path),
            str(staging_path.relative_to(ROOT)): blob(staging_path),
            str(VERIFIER.relative_to(ROOT)): blob(VERIFIER),
        },
        "conclusion": (
            "All manifest-required official sources, plus referenced supplemental sources, "
            "were independently re-fetched and text-extracted, and the configured "
            "service anchor was observed in the "
            "bounded source family. This receipt does not prove item-body equality, "
            "currentness, human review, omitted-text completeness, or publication readiness."
        ),
    }

    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    receipt_path.write_text(
        json.dumps(receipt, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"wrote {receipt_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
