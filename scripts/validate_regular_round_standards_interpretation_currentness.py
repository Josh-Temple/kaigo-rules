#!/usr/bin/env python3
"""Validate the fail-closed regular-round standards-interpretation currentness receipt.

This validator checks repository/source-role invariants only. A zero exit code
means the NOT_ESTABLISHED currentness decision is represented consistently; it
does not convert that decision into PASS and does not re-fetch MHLW sources.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SERVICE_ID = "regular-round"

SERVICE = ROOT / "data/services/regular-round.json"
SCOPE = ROOT / "data/services/regular-round/standards-interpretation-scope.json"
STAGING = ROOT / "data/services/regular-round/standards-interpretation-staging.json"
INVENTORY = ROOT / "data/verification/standards-interpretation-source-inventory/regular-round.json"
ITEM_BODY = ROOT / "data/verification/standards-interpretation-item-body/regular-round.json"
RECEIPT = ROOT / "data/verification/standards-interpretation-currentness/regular-round.json"

REQUIRED_SOURCE_IDS = {
    "original-2006-full-notice",
    "r24-regular-round-introduction-comparison",
    "historical-repository-comparison",
    "r30-comparison",
    "r3-comparison",
    "r6-earlier-comparison",
    "r6-final-comparison",
    "current-standards-ordinance-html",
    "r8-reform-index",
    "kaigo-latest-info-index",
    "mhlw-new-notification-index",
    "mhlw-law-database-update",
    "mhlw-law-database-coverage-notice",
}


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    differences: list[str] = []

    service = load(SERVICE)
    scope = load(SCOPE)
    staging = load(STAGING)
    inventory = load(INVENTORY)
    item_body = load(ITEM_BODY)
    receipt = load(RECEIPT)

    for label, doc in (
        ("service", service),
        ("scope", scope),
        ("staging", staging),
        ("inventory", inventory),
        ("item_body", item_body),
        ("receipt", receipt),
    ):
        if doc.get("service_id") != SERVICE_ID:
            differences.append(f"{label}: service_id mismatch")

    if receipt.get("audit_kind") != "INDEPENDENT_CURRENTNESS_VERIFICATION":
        differences.append("receipt audit_kind mismatch")
    if receipt.get("audit_result") != "NOT_ESTABLISHED":
        differences.append("receipt must remain NOT_ESTABLISHED")
    if receipt.get("verification_scope") != "CURRENTNESS_ONLY_NO_PUBLICATION_PROMOTION":
        differences.append("receipt currentness-only scope is missing")

    standards_layer = service.get("ingestion_layers", {}).get("standards_interpretation", {})
    if standards_layer.get("item_body_verification") != "PASS_CONTENT_EVIDENCE_MATCH_ONLY":
        differences.append("service item-body result changed; re-review currentness inputs")
    if standards_layer.get("status") != "ITEM_BODY_VERIFIED_CURRENTNESS_PENDING":
        differences.append("service currentness-pending status changed; re-review required")

    publication_gate = service.get("publication_gate", {})
    for key in (
        "public_routes_enabled",
        "content_ingested",
        "independent_verification_complete",
        "human_review_complete",
    ):
        if publication_gate.get(key) is not False:
            differences.append(f"service publication gate must remain false: {key}")

    if scope.get("currentness_state") != "NOT_ESTABLISHED":
        differences.append("scope currentness_state must remain NOT_ESTABLISHED")
    if scope.get("human_review_state") != "NOT_REVIEWED":
        differences.append("scope human_review_state must remain NOT_REVIEWED")
    if scope.get("publication", {}).get("allowed") is not False:
        differences.append("scope publication must remain disallowed")
    if scope.get("source_assurance", {}).get("integrated_current_text_established") is not False:
        differences.append("scope must not claim integrated current notice text")

    if staging.get("currentness_state") != "NOT_ESTABLISHED":
        differences.append("staging currentness_state must remain NOT_ESTABLISHED")
    if staging.get("human_review_state") != "NOT_REVIEWED":
        differences.append("staging human_review_state must remain NOT_REVIEWED")
    if staging.get("publication_state") != "NOT_PUBLIC":
        differences.append("staging publication_state must remain NOT_PUBLIC")
    if len(staging.get("items", [])) != 21:
        differences.append("regular-round staging item count changed from 21")
    for item in staging.get("items", []):
        if item.get("currentness_state") != "NOT_ESTABLISHED":
            differences.append(f"{item.get('id')}: item currentness must remain NOT_ESTABLISHED")
        if item.get("human_review_state") != "NOT_REVIEWED":
            differences.append(f"{item.get('id')}: human review must remain NOT_REVIEWED")

    if inventory.get("audit_result") != "PASS_BOUNDED_SCOPE_ONLY":
        differences.append("source inventory must remain bounded-scope PASS")
    if inventory.get("safety", {}).get("currentness_promoted") is not False:
        differences.append("source inventory must not promote currentness")
    if item_body.get("audit_result") != "PASS_CONTENT_EVIDENCE_MATCH_ONLY":
        differences.append("item-body receipt result changed")
    if item_body.get("verification_scope") != "CONTENT_EVIDENCE_MATCH_ONLY_NOT_CURRENTNESS":
        differences.append("item-body receipt must remain explicitly non-currentness")

    preconditions = receipt.get("preconditions", {})
    if preconditions.get("source_inventory_result") != "PASS_BOUNDED_SCOPE_ONLY":
        differences.append("receipt source-inventory precondition mismatch")
    if preconditions.get("item_body_result") != "PASS_CONTENT_EVIDENCE_MATCH_ONLY":
        differences.append("receipt item-body precondition mismatch")
    if preconditions.get("item_body_does_not_prove_currentness") is not True:
        differences.append("receipt must state item-body does not prove currentness")

    sources = {
        row.get("id"): row
        for row in receipt.get("official_sources", [])
        if isinstance(row, dict) and row.get("id")
    }
    missing = REQUIRED_SOURCE_IDS - set(sources)
    if missing:
        differences.append(f"missing required currentness sources: {sorted(missing)}")

    final_r6 = sources.get("r6-final-comparison", {})
    if final_r6.get("classification") != "AMENDMENT_COMPARISON_NOT_INTEGRATED":
        differences.append("R6 final source must remain amendment-comparison-only")
    if final_r6.get("counts_as_current_integrated_text") is not False:
        differences.append("R6 final comparison must not count as integrated text")

    ordinance = sources.get("current-standards-ordinance-html", {})
    if ordinance.get("classification") != "ORDINANCE_NOT_INTERPRETATION_NOTICE":
        differences.append("MHLW t_doc 82aa7858 must remain classified as ordinance")
    if ordinance.get("counts_as_current_integrated_text") is not False:
        differences.append("standards ordinance must not count as interpretation notice text")

    original = sources.get("original-2006-full-notice", {})
    if original.get("classification") != "FULL_NOTICE_AT_ORIGINAL_ISSUANCE_PRE_REGULAR_ROUND":
        differences.append("2006 original must remain historical pre-regular-round baseline")
    if original.get("counts_as_current_integrated_text") is not False:
        differences.append("2006 original must not count as current text")

    for source_id in ("r24-regular-round-introduction-comparison", "r30-comparison", "r3-comparison"):
        if sources.get(source_id, {}).get("classification") != "AMENDMENT_COMPARISON_NOT_INTEGRATED":
            differences.append(f"{source_id}: unsafe source classification")

    assessment = receipt.get("source_version_assessment", {})
    integrated = assessment.get("current_integrated_official_interpretation_notice", {})
    if integrated.get("found") is not False or integrated.get("status") != "NOT_ESTABLISHED":
        differences.append("current integrated official interpretation notice must remain not established")
    if assessment.get("amendment_chain_closed") is not False:
        differences.append("amendment chain must remain open")
    post_r6 = assessment.get("post_r6", {})
    if post_r6.get("status") != "NEGATIVE_DISCOVERY_ONLY_NOT_CLOSED":
        differences.append("post-R6 evidence must remain negative-discovery-only")
    if post_r6.get("absence_of_evidence_treated_as_proof") is not False:
        differences.append("absence of evidence must not be treated as proof")

    if not receipt.get("negative_search_limitations"):
        differences.append("negative-search limitations must be explicit")

    conclusion = receipt.get("conclusion", {})
    if conclusion.get("currentness") != "NOT_ESTABLISHED":
        differences.append("conclusion currentness must remain NOT_ESTABLISHED")
    if conclusion.get("currentness_pass") is not False:
        differences.append("currentness PASS must remain false")
    if conclusion.get("decision_effect") != "KEEP_FAIL_CLOSED":
        differences.append("decision effect must remain fail-closed")

    safety = receipt.get("safety", {})
    required_false = (
        "currentness_promoted",
        "human_review_promoted",
        "publication_permitted",
        "route_enabled",
        "current_integrated_notice_text_reconstructed",
        "historical_text_treated_as_current",
        "ordinance_treated_as_interpretation_notice",
        "negative_search_treated_as_no_amendment_proof",
    )
    for key in required_false:
        if safety.get(key) is not False:
            differences.append(f"safety invariant must be false: {key}")
    if safety.get("currentness_only") is not True:
        differences.append("receipt safety must remain currentness-only")

    report = {
        "service_id": SERVICE_ID,
        "validator": Path(__file__).name,
        "receipt_result": receipt.get("audit_result"),
        "amendment_chain_closed": assessment.get("amendment_chain_closed"),
        "current_integrated_text_found": integrated.get("found"),
        "validation_result": "PASS" if not differences else "FAIL",
        "differences": differences,
        "safety": {
            "currentness_promoted": False,
            "human_review_promoted": False,
            "publication_permitted": False,
            "route_enabled": False,
        },
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if not differences else 1


if __name__ == "__main__":
    sys.exit(main())
