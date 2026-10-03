#!/usr/bin/env python3
"""Validate the fail-closed currentness receipt for night-homevisit standards interpretation."""
from __future__ import annotations

import re
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECEIPT = (
    ROOT
    / "data/verification/standards-interpretation-currentness/night-homevisit.json"
)
SERVICE = ROOT / "data/services/night-homevisit.json"
SCOPE = ROOT / "data/services/night-homevisit/standards-interpretation-scope.json"
ITEM_BODY = (
    ROOT
    / "data/verification/standards-interpretation-item-body/night-homevisit.json"
)


def fail(message: str) -> None:
    raise SystemExit(
        "night-homevisit standards-interpretation currentness validation failed: "
        + message
    )


def load(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        fail(f"cannot read valid JSON from {path.relative_to(ROOT)}: {exc}")


def git_blob_sha(path: Path) -> str:
    payload = path.read_bytes()
    header = f"blob {len(payload)}\0".encode("ascii")
    return hashlib.sha1(header + payload).hexdigest()


def main() -> None:
    receipt = load(RECEIPT)
    service = load(SERVICE)
    scope = load(SCOPE)
    item_body = load(ITEM_BODY)

    if receipt.get("service_id") != "night-homevisit":
        fail("unexpected service_id")
    if receipt.get("layer") != "standards_interpretation":
        fail("unexpected layer")
    if receipt.get("audit_kind") != "INDEPENDENT_CURRENTNESS_VERIFICATION":
        fail("unexpected audit_kind")
    if receipt.get("audit_result") != "NOT_ESTABLISHED":
        fail("currentness must remain NOT_ESTABLISHED")
    if receipt.get("effect") != "KEEP_HOLD":
        fail("receipt must keep HOLD")

    repository_inputs = receipt.get("repository_inputs", {})
    path_map = {
        "service_config": SERVICE,
        "scope": SCOPE,
        "staging": ROOT / "data/services/night-homevisit/standards-interpretation-staging.json",
        "source_inventory": (
            ROOT
            / "data/verification/standards-interpretation-source-inventory/night-homevisit.json"
        ),
        "item_body": ITEM_BODY,
    }
    for key, path in path_map.items():
        row = repository_inputs.get(key, {})
        if row.get("path") != str(path.relative_to(ROOT)):
            fail(f"{key}: provenance path mismatch")
        blob_sha = str(row.get("blob_sha") or "")
        if not re.fullmatch(r"[0-9a-f]{40}", blob_sha):
            fail(f"{key}: provenance blob SHA is missing or malformed")

    coverage = item_body.get("coverage", {})
    if item_body.get("audit_result") != "PASS_CONTENT_EVIDENCE_MATCH_ONLY":
        fail("item-body baseline no longer has the expected bounded PASS")
    if coverage.get("expected_items") != 25 or coverage.get("observed_items") != 25:
        fail("item-body expected/observed item count changed")
    if coverage.get("counts") != {
        "PASS": 25,
        "PARTIAL": 0,
        "GAP": 0,
        "FAIL": 0,
    }:
        fail("item-body 25/25 PASS baseline changed")

    standards = service.get("ingestion_layers", {}).get("standards_interpretation", {})
    if standards.get("status") != "ITEM_BODY_VERIFIED_CURRENTNESS_PENDING":
        fail("service currentness gate was unexpectedly promoted or changed")
    if standards.get("item_body_verification") != "PASS_CONTENT_EVIDENCE_MATCH_ONLY":
        fail("service item-body status changed")
    if service.get("publication_gate", {}).get("public_routes_enabled") is not False:
        fail("public route must remain disabled")
    if service.get("publication_gate", {}).get("human_review_complete") is not False:
        fail("human review must remain incomplete")

    if scope.get("currentness_state") != "NOT_ESTABLISHED":
        fail("scope currentness must remain NOT_ESTABLISHED")
    if scope.get("human_review_state") != "NOT_REVIEWED":
        fail("scope human review must remain NOT_REVIEWED")
    if scope.get("publication", {}).get("allowed") is not False:
        fail("scope publication must remain disabled")
    if scope.get("source_assurance", {}).get("integrated_current_text_established") is not False:
        fail("scope must not claim integrated current text")

    protocol = receipt.get("protocol", {})
    if set(protocol.get("pass_requires_one_of", [])) != {
        "CURRENT_INTEGRATED_OFFICIAL_NOTICE_TEXT",
        "SUFFICIENTLY_CLOSED_OFFICIAL_AMENDMENT_CHAIN",
    }:
        fail("PASS protocol requirements changed")
    for key in (
        "negative_search_can_prove_no_change",
        "amendment_comparison_alone_is_integrated_text",
        "underlying_ordinance_can_substitute_for_notice",
    ):
        if protocol.get(key) is not False:
            fail(f"fail-closed protocol flag must remain false: {key}")

    versions = {
        row.get("id"): row
        for row in receipt.get("versions_checked", [])
        if isinstance(row, dict) and row.get("id")
    }
    required_versions = {
        "h18-original-full-notice",
        "older-amendment-reference",
        "h27-full-notice-comparison",
        "r3-amendment-comparison",
        "r6-final-comparison",
        "underlying-current-ordinance",
    }
    if not required_versions.issubset(versions):
        fail("required historical/R3/R6/ordinance version classes are missing")
    if (
        versions["r3-amendment-comparison"].get("classification")
        != "R3_AMENDMENT_COMPARISON_NOT_INTEGRATED"
    ):
        fail("R3 evidence must remain a non-integrated amendment comparison")
    if (
        versions["r6-final-comparison"].get("classification")
        != "R6_FINAL_AMENDMENT_COMPARISON_NOT_INTEGRATED"
    ):
        fail("R6 evidence must remain a non-integrated amendment comparison")
    if (
        versions["underlying-current-ordinance"].get("classification")
        != "UNDERLYING_STANDARD_ORDINANCE_NOT_NOTICE"
    ):
        fail("underlying ordinance must not be classified as notice text")

    discovery = {
        row.get("id"): row
        for row in receipt.get("official_discovery_and_post_r6_checks", [])
        if isinstance(row, dict) and row.get("id")
    }
    for required in (
        "mhlw-r6-reform-index",
        "mhlw-r8-reform-index",
        "mhlw-kaigo-latest-info",
        "mhlw-law-database",
    ):
        if required not in discovery:
            fail(f"official discovery/post-R6 route missing: {required}")
        if not discovery[required].get("limitation"):
            fail(f"official route limitation missing: {required}")

    amendment = receipt.get("amendment_coverage", {})
    for key in (
        "current_integrated_official_notice_text_found",
        "complete_pre_r3_amendment_chain_established",
        "complete_r3_to_r6_amendment_chain_established",
        "complete_post_r6_amendment_chain_established",
        "sufficiently_closed_chain",
    ):
        if amendment.get(key) is not False:
            fail(f"unproven amendment/current-text flag must remain false: {key}")

    current_text = receipt.get("current_integrated_official_text", {})
    if current_text.get("available") is not False:
        fail("integrated current official notice text must remain unavailable")

    limitations = receipt.get("negative_search_limitations", [])
    if len(limitations) < 4:
        fail("negative-search limitations are incomplete")
    if not any("証明" in str(row) for row in limitations):
        fail("negative search must explicitly be non-probative")

    conclusion = receipt.get("conclusion", {})
    if conclusion.get("state") != "NOT_ESTABLISHED":
        fail("conclusion must remain NOT_ESTABLISHED")
    if conclusion.get("publication_effect") != "HOLD":
        fail("publication effect must remain HOLD")

    safety = receipt.get("safety_boundary", {})
    if safety.get("currentness_only") is not True:
        fail("receipt must remain currentness-only")
    for key in (
        "item_body_status_changed",
        "human_review_promoted",
        "publication_promoted",
        "public_route_promoted",
        "automatic_promotion_allowed",
    ):
        if safety.get(key) is not False:
            fail(f"safety boundary must remain false: {key}")

    print(
        "night-homevisit standards-interpretation currentness: "
        "OK (NOT_ESTABLISHED; HOLD preserved; item-body 25/25 unchanged)"
    )


if __name__ == "__main__":
    main()
