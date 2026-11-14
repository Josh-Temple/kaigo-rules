#!/usr/bin/env python3
"""Validate a pinned standards-interpretation source-inventory receipt."""
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
    raise SystemExit("standards-interpretation source-inventory receipt invalid: " + message)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--service-id", required=True)
    parser.add_argument("--expected-items", type=int, required=True)
    args = parser.parse_args()

    service_id = args.service_id
    scope_path = ROOT / f"data/services/{service_id}/standards-interpretation-scope.json"
    staging_path = ROOT / f"data/services/{service_id}/standards-interpretation-staging.json"
    receipt_path = (
        ROOT
        / "data/verification/standards-interpretation-source-inventory"
        / f"{service_id}.json"
    )
    if not receipt_path.exists():
        fail(f"receipt missing for {service_id}")

    scope = load(scope_path)
    receipt = load(receipt_path)
    if receipt.get("service_id") != service_id:
        fail("service mismatch")
    if receipt.get("audit_kind") != "INDEPENDENT_STANDARDS_INTERPRETATION_SOURCE_INVENTORY":
        fail("unexpected audit kind")
    if receipt.get("audit_result") != "PASS_BOUNDED_SCOPE_ONLY":
        fail("receipt result is not bounded PASS")
    if receipt.get("differences") != []:
        fail("receipt contains differences")

    coverage = receipt.get("coverage", {})
    if coverage.get("expected_staging_items_or_tasks") != args.expected_items:
        fail("expected count mismatch")
    if coverage.get("observed_staging_items_or_tasks") != args.expected_items:
        fail("observed count mismatch")

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
        fail("receipt does not cover every manifest-required source")
    if coverage.get("required_sources_fetchable") != coverage.get("required_sources"):
        fail("required source coverage incomplete")

    source_rows = {
        row.get("url"): row
        for row in receipt.get("sources", [])
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

    if coverage.get("inspected_sources") != len(source_rows):
        fail("inspected source count mismatch")
    if coverage.get("referenced_sources", 0) > coverage.get("inspected_sources", 0):
        fail("referenced source count exceeds inspected source count")

    safety = receipt.get("safety", {})
    for key in (
        "item_body_match_proven",
        "currentness_promoted",
        "human_review_promoted",
        "omitted_text_reconstructed",
        "publication_permitted",
    ):
        if safety.get(key) is not False:
            fail(f"safety boundary weakened: {key}")

    expected_blobs = {
        str(scope_path.relative_to(ROOT)): blob(scope_path),
        str(staging_path.relative_to(ROOT)): blob(staging_path),
        str(VERIFIER.relative_to(ROOT)): blob(VERIFIER),
    }
    reassessment = receipt.get("reassessment")
    if service_id == "community-dayservice":
        # The old retrieval is preserved as history.  Only a subset of those
        # observations is carried forward; no new fetch is being asserted.
        history_path = ROOT / "data/verification/history/community-dayservice-20261003/source-inventory.json"
        if not isinstance(reassessment, dict) or reassessment.get("kind") != "HISTORICAL_SOURCE_INVENTORY_SUBSET_NOT_NEW_FETCH":
            fail("historical inventory reassessment missing")
        if reassessment.get("historical_receipt") != str(history_path.relative_to(ROOT)) or reassessment.get("historical_receipt_git_blob_sha") != blob(history_path):
            fail("historical inventory receipt changed")
        if reassessment.get("current_input_git_blob_shas") != expected_blobs:
            fail("reassessed inventory inputs are stale")
        original = load(history_path)
        removed = "https://www.mhlw.go.jp/content/12300000/001225905.pdf"
        if reassessment.get("removed_url") != removed:
            fail("incorrect source removal is not recorded")
        if receipt.get("sources") != [row for row in original.get("sources", []) if row.get("url") != removed]:
            fail("derived source observations differ from historical subset")
        if receipt.get("audit_run") != original.get("audit_run") or receipt.get("input_git_blob_shas_at_audit") != original.get("input_git_blob_shas_at_audit"):
            fail("historical retrieval provenance was rewritten")
    elif receipt.get("input_git_blob_shas_at_audit") != expected_blobs:
        fail("receipt inputs are stale")

    run = receipt.get("audit_run", {})
    if not run.get("run_id") or not run.get("head_sha") or not run.get("workflow"):
        fail("audit-run provenance incomplete")

    print(
        f"{service_id} standards-interpretation source inventory receipt: "
        f"PASS (historical retrieval for {args.expected_items}; required sources "
        f"{coverage.get('required_sources_fetchable')}/{coverage.get('required_sources')})"
    )


if __name__ == "__main__":
    main()
