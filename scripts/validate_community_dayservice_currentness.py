#!/usr/bin/env python3
"""Validate the community-dayservice standards-interpretation currentness receipt.

This validator is intentionally service-specific. It enforces the fail-closed
currentness decision and source-role separation without changing item-body,
human-review, publication, or routing state.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SERVICE_ID = "community-dayservice"
EXPECTED_ITEMS = 21

SERVICE = ROOT / "data/services/community-dayservice.json"
SCOPE = ROOT / "data/services/community-dayservice/standards-interpretation-scope.json"
STAGING = ROOT / "data/services/community-dayservice/standards-interpretation-staging.json"
SOURCE_INVENTORY = (
    ROOT / "data/verification/standards-interpretation-source-inventory/community-dayservice.json"
)
ITEM_BODY = (
    ROOT / "data/verification/standards-interpretation-item-body/community-dayservice.json"
)
CURRENTNESS = (
    ROOT / "data/verification/standards-interpretation-currentness/community-dayservice.json"
)

REQUIRED_CATEGORIES = {
    "HISTORICAL_FULL_NOTICE",
    "AMENDMENT_COMPARISON",
    "FINAL_R6_COMPARISON",
    "OFFICIAL_DISCOVERY_INDEX",
    "POST_R6_OFFICIAL_INDEX",
    "CURRENT_ORDINANCE_NOT_INTERPRETATION_NOTICE",
}


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def git_blob_sha(path: Path) -> str:
    body = path.read_bytes()
    header = f"blob {len(body)}\0".encode("ascii")
    return hashlib.sha1(header + body).hexdigest()


def validate() -> list[str]:
    errors: list[str] = []
    service = load(SERVICE)
    scope = load(SCOPE)
    staging = load(STAGING)
    inventory = load(SOURCE_INVENTORY)
    item_body = load(ITEM_BODY)
    receipt = load(CURRENTNESS)

    if receipt.get("service_id") != SERVICE_ID:
        errors.append("currentness receipt service_id mismatch")
    if receipt.get("audit_kind") != "INDEPENDENT_STANDARDS_INTERPRETATION_CURRENTNESS_VERIFICATION":
        errors.append("unexpected currentness audit_kind")
    if receipt.get("source_family") != scope.get("source_family"):
        errors.append("currentness/source scope family mismatch")
    if scope.get("currentness_state") != "NOT_ESTABLISHED":
        errors.append("scope currentness was promoted")
    if staging.get("currentness_state") != "NOT_ESTABLISHED":
        errors.append("staging currentness was promoted")
    if staging.get("human_review_state") != "NOT_REVIEWED":
        errors.append("staging human review was promoted")
    if staging.get("publication_state") != "NOT_PUBLIC":
        errors.append("staging publication was promoted")

    layer = service.get("ingestion_layers", {}).get("standards_interpretation", {})
    if layer.get("item_body_verification") != "PASS_CONTENT_EVIDENCE_MATCH_ONLY":
        errors.append("item-body verification state drifted")
    if layer.get("item_body_verification_counts") != {
        "PASS": EXPECTED_ITEMS,
        "PARTIAL": 0,
        "GAP": 0,
        "FAIL": 0,
    }:
        errors.append("item-body verification counts drifted")
    if layer.get("currentness_verification") != "HOLD_NOT_ESTABLISHED":
        errors.append("service currentness_verification pointer state mismatch")
    if layer.get("currentness_verification_receipt") != str(CURRENTNESS.relative_to(ROOT)):
        errors.append("service currentness receipt pointer mismatch")

    if inventory.get("audit_result") != "PASS_BOUNDED_SCOPE_ONLY":
        errors.append("source inventory result changed")
    if inventory.get("safety", {}).get("currentness_promoted") is not False:
        errors.append("source inventory unexpectedly promotes currentness")

    if item_body.get("audit_result") != "PASS_WITH_ITEM_LEVEL_EVIDENCE":
        errors.append("item-body receipt is not PASS_WITH_ITEM_LEVEL_EVIDENCE")
    if item_body.get("counts") != {"PASS": 21, "PARTIAL": 0, "GAP": 0, "FAIL": 0}:
        errors.append("item-body receipt counts changed")
    if "currentness" not in item_body.get("scope", {}).get("does_not_verify", []):
        errors.append("item-body receipt no longer excludes currentness")
    if item_body.get("safety", {}).get("currentness_promoted") is not False:
        errors.append("item-body receipt unexpectedly promotes currentness")

    precondition = receipt.get("item_body_precondition", {})
    if precondition.get("result") != "PASS_WITH_ITEM_LEVEL_EVIDENCE":
        errors.append("currentness receipt item-body precondition mismatch")
    if precondition.get("proves_currentness") is not False:
        errors.append("item-body precondition must not prove currentness")

    sources = receipt.get("official_sources", [])
    source_ids = [row.get("id") for row in sources]
    if len(source_ids) != len(set(source_ids)):
        errors.append("duplicate currentness source id")
    categories = {row.get("category") for row in sources}
    if not REQUIRED_CATEGORIES.issubset(categories):
        errors.append("required source categories are missing")
    for row in sources:
        if not str(row.get("url", "")).startswith("https://www.mhlw.go.jp/"):
            errors.append(f"{row.get('id')}: non-MHLW source in currentness receipt")
        if row.get("current_integrated_text") is not False:
            errors.append(f"{row.get('id')}: source must not be classified as integrated current text")
        if not row.get("limitation"):
            errors.append(f"{row.get('id')}: source limitation missing")

    by_id = {row["id"]: row for row in sources if row.get("id")}
    r6 = by_id.get("mhlw-r6-final-comparison", {})
    if r6.get("url") != "https://www.mhlw.go.jp/content/12300000/001227939.pdf":
        errors.append("final R6 source URL changed")
    observations = " ".join(r6.get("observations", []))
    for marker in ("（抄）", "新・旧", "（略）"):
        if marker not in observations:
            errors.append(f"final R6 comparison marker missing: {marker}")

    ordinance = by_id.get("mhlw-current-standard-ordinance", {})
    if ordinance.get("category") != "CURRENT_ORDINANCE_NOT_INTERPRETATION_NOTICE":
        errors.append("current ordinance must remain separated from interpretation notice")
    if "82aa7858" not in ordinance.get("url", ""):
        errors.append("current ordinance source URL changed")

    discovery = receipt.get("post_r6_discovery", {})
    if discovery.get("checked") is not True:
        errors.append("post-R6 discovery was not recorded")
    if discovery.get("target_amendment_identified") is not False:
        errors.append("unexpected post-R6 target amendment state")
    if discovery.get("negative_search_is_proof_of_no_change") is not False:
        errors.append("negative search must not prove no change")
    if not discovery.get("limitation"):
        errors.append("post-R6 negative-search limitation missing")

    coverage = receipt.get("amendment_coverage", {})
    for key in (
        "all_intervening_amendments_closed",
        "post_r6_amendment_chain_closed",
        "sufficiently_closed_amendment_chain",
    ):
        if coverage.get(key) is not False:
            errors.append(f"amendment coverage must remain open: {key}")

    integrated = receipt.get("integrated_current_text", {})
    if integrated.get("official_current_integrated_text_identified") is not False:
        errors.append("integrated current notice text must remain unidentified")
    if integrated.get("r6_final_comparison_is_integrated_text") is not False:
        errors.append("R6 final comparison must not be treated as integrated text")
    if integrated.get("current_standard_ordinance_is_interpretation_notice") is not False:
        errors.append("ordinance must not be treated as interpretation notice")
    if integrated.get("availability") != "NOT_IDENTIFIED":
        errors.append("unexpected integrated current text availability")

    conclusion = receipt.get("conclusion", {})
    if conclusion.get("currentness_state") != "NOT_ESTABLISHED":
        errors.append("currentness conclusion must remain NOT_ESTABLISHED")
    if conclusion.get("decision") != "HOLD":
        errors.append("currentness decision must remain HOLD")
    if conclusion.get("pass") is not False:
        errors.append("currentness must not PASS")

    provenance = receipt.get("verification_provenance", {})
    pinned = provenance.get("repository_inputs", {})
    current_paths = {
        str(SCOPE.relative_to(ROOT)): SCOPE,
        str(STAGING.relative_to(ROOT)): STAGING,
        str(SOURCE_INVENTORY.relative_to(ROOT)): SOURCE_INVENTORY,
        str(ITEM_BODY.relative_to(ROOT)): ITEM_BODY,
    }
    for name, path in current_paths.items():
        if pinned.get(name) != git_blob_sha(path):
            errors.append(f"pinned repository input drifted: {name}")

    safety = receipt.get("safety", {})
    if safety.get("verification_scope") != "CURRENTNESS_ONLY":
        errors.append("currentness-only safety scope missing")
    for key in (
        "item_body_result_changed",
        "human_review_promoted",
        "publication_promoted",
        "public_route_enabled",
        "integrated_current_text_synthesized",
        "omitted_text_reconstructed",
        "negative_search_used_as_proof",
    ):
        if safety.get(key) is not False:
            errors.append(f"safety flag must remain false: {key}")

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

    return errors


def main() -> int:
    errors = validate()
    if errors:
        for error in errors:
            print("FAIL community-dayservice currentness:", error)
        return 1
    print("PASS community-dayservice currentness: NOT_ESTABLISHED / HOLD (no promotion)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
