#!/usr/bin/env python3
"""Validate the fail-closed preventive-support standards-interpretation currentness receipt."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SERVICE_ID = "preventive-support"
RECEIPT = ROOT / "data/verification/standards-interpretation-currentness/preventive-support.json"
SERVICE = ROOT / f"data/services/{SERVICE_ID}.json"
SCOPE = ROOT / f"data/services/{SERVICE_ID}/standards-interpretation-scope.json"
STAGING = ROOT / f"data/services/{SERVICE_ID}/standards-interpretation-staging.json"
ITEM_BODY = ROOT / f"data/verification/standards-interpretation-item-body/{SERVICE_ID}.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def fail(message: str) -> None:
    raise SystemExit(f"{SERVICE_ID} currentness validation failed: {message}")


def main() -> None:
    receipt = load(RECEIPT)
    service = load(SERVICE)
    scope = load(SCOPE)
    staging = load(STAGING)
    item_body = load(ITEM_BODY)

    if receipt.get("service_id") != SERVICE_ID:
        fail("service mismatch")
    if receipt.get("audit_kind") != "INDEPENDENT_CURRENTNESS_VERIFICATION":
        fail("unexpected audit kind")
    if receipt.get("audit_result") != "NOT_ESTABLISHED":
        fail("audit result must remain NOT_ESTABLISHED")
    conclusion = receipt.get("conclusion", {})
    if conclusion.get("currentness") != "NOT_ESTABLISHED":
        fail("conclusion must remain NOT_ESTABLISHED")
    if conclusion.get("currentness_pass") is not False:
        fail("currentness PASS must remain false")
    if conclusion.get("decision_effect") != "KEEP_FAIL_CLOSED":
        fail("decision effect must remain fail-closed")

    summary = item_body.get("integration_summary", {})
    if summary.get("verification_status") != "PARTIAL_WITH_GAPS":
        fail("item-body baseline changed")
    if conclusion.get("item_body_result_unchanged") != "PARTIAL_WITH_GAPS":
        fail("receipt changed item-body result")

    if scope.get("currentness_state") != "NOT_ESTABLISHED":
        fail("scope currentness promoted")
    if staging.get("currentness_state") != "NOT_ESTABLISHED":
        fail("staging currentness promoted")
    if staging.get("human_review_state") != "NOT_REVIEWED":
        fail("human review promoted")
    if staging.get("publication_state") != "NOT_PUBLIC":
        fail("publication state promoted")

    gate = service.get("publication_gate", {})
    for key in ("public_routes_enabled", "content_ingested", "independent_verification_complete", "human_review_complete"):
        if gate.get(key) is not False:
            fail(f"publication gate promoted: {key}")
    if service.get("routing", {}).get("future_service_base_enabled") is not False:
        fail("route enabled")

    assessment = receipt.get("source_version_assessment", {})
    integrated = assessment.get("current_integrated_official_interpretation_notice", {})
    if integrated.get("found") is not False or integrated.get("status") != "NOT_ESTABLISHED":
        fail("integrated current notice must remain not established")
    if assessment.get("amendment_chain_closed") is not False:
        fail("amendment chain must remain open")
    post_r6 = assessment.get("post_r6", {})
    if post_r6.get("status") != "NEGATIVE_DISCOVERY_ONLY_NOT_CLOSED":
        fail("post-R6 assessment must remain negative-discovery-only")
    if post_r6.get("absence_of_evidence_treated_as_proof") is not False:
        fail("negative discovery was treated as proof")

    sources = receipt.get("official_sources", [])
    if not any(row.get("classification") == "AMENDMENT_COMPARISON_NOT_INTEGRATED" for row in sources):
        fail("R6 amendment-comparison classification missing")
    if any(row.get("counts_as_current_integrated_text") is True for row in sources):
        fail("a non-integrated source was promoted to integrated current text")

    safety = receipt.get("safety", {})
    required_false = (
        "currentness_promoted",
        "human_review_promoted",
        "publication_permitted",
        "route_enabled",
        "current_integrated_notice_text_reconstructed",
        "negative_search_treated_as_no_amendment_proof",
    )
    for key in required_false:
        if safety.get(key) is not False:
            fail(f"safety invariant weakened: {key}")
    if safety.get("currentness_only") is not True:
        fail("receipt must remain currentness-only")
    if safety.get("item_body_promoted") is not False:
        fail("item-body was promoted")
    if safety.get("package_blocker_cleared") is not False:
        fail("PACKAGE blocker was cleared")

    print(f"{SERVICE_ID} standards-interpretation currentness: PASS_VALIDATION (NOT_ESTABLISHED; fail-closed)")


if __name__ == "__main__":
    main()
