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
    if coverage.get("required_sources_fetchable") != coverage.get("required_sources"):
        fail("required source coverage incomplete")

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
    if receipt.get("input_git_blob_shas_at_audit") != expected_blobs:
        fail("receipt inputs are stale")

    run = receipt.get("audit_run", {})
    if not run.get("run_id") or not run.get("head_sha") or not run.get("workflow"):
        fail("audit-run provenance incomplete")

    print(
        f"{service_id} standards-interpretation source inventory receipt: "
        f"PASS ({args.expected_items}; required sources "
        f"{coverage.get('required_sources_fetchable')}/{coverage.get('required_sources')})"
    )


if __name__ == "__main__":
    main()
