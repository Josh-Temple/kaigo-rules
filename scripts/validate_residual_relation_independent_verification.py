#!/usr/bin/env python3
"""Validate Worker-C residual relation independent-verification outputs."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
sys.path.insert(0, str(ROOT / "scripts"))

from build_residual_relation_independent_verification import build as build_inventory  # noqa: E402
from relation_verification_coverage import build_relation_coverage  # noqa: E402

OUTPUT = DATA / "residual-relation-independent-verification.generated.json"
AUDIT = DATA / "residual-relation-service-definition-independent-audit.json"
VERIFIED = ("fee.dayservice.root", "defined_service_by", "ordinance37.article.92")

EXPECTED_CLASSIFICATIONS = {
    "MACHINE_SOURCE_REPARSE_CANDIDATE": 0,
    "SOURCE_LINK_FRESHNESS_OR_DIRECT_EVIDENCE_REQUIRED": 1,
    "SEMANTIC_TEXT_CHECK_REQUIRED": 17,
    "CROSS_LAYER_HUMAN_REVIEW_REQUIRED": 4,
    "HUMAN_SEMANTIC_REVIEW_REQUIRED": 36,
}


def fail(message: str) -> None:
    raise SystemExit("Worker-C residual relation validation failed: " + message)


def main() -> None:
    committed = json.loads(OUTPUT.read_text(encoding="utf-8"))
    expected = build_inventory()
    if committed != expected:
        fail("generated residual inventory is stale")

    coverage = build_relation_coverage()
    if len(coverage["inventory"]) != 188:
        fail(f"canonical relation inventory changed: {len(coverage['inventory'])}")
    if len(coverage["verified"]) != 130:
        fail(f"independently verified count is not 130: {len(coverage['verified'])}")
    if len(coverage["remaining"]) != 58:
        fail(f"remaining count is not 58: {len(coverage['remaining'])}")
    if coverage["overlap_relations"] != 0:
        fail("independent verification lanes overlap")
    if VERIFIED not in coverage["verified"]:
        fail("new service-definition relation is not independently covered")

    prior_lane_count = sum(
        row["verified_relations"]
        for row in coverage["lanes"]
        if row["id"] != "residual-service-definition"
    )
    if prior_lane_count != 129:
        fail(f"pre-existing independently verified relations regressed: {prior_lane_count}")

    new_lane = [row for row in coverage["lanes"] if row["id"] == "residual-service-definition"]
    if len(new_lane) != 1 or new_lane[0]["verified_relations"] != 1:
        fail("residual service-definition lane must cover exactly one relation")

    if committed["classification_counts"] != EXPECTED_CLASSIFICATIONS:
        fail(f"unexpected remaining classification counts: {committed['classification_counts']}")

    summary = committed["summary"]
    expected_summary = {
        "canonical_relations_total": 188,
        "independently_verified_before_worker_c": 129,
        "unverified_before_worker_c": 59,
        "newly_verified": 1,
        "independently_verified_after_worker_c": 130,
        "remaining_unverified": 58,
        "removed": 0,
        "downgraded_to_candidate_only": 0,
        "human_evidence_pack_matches": 57,
        "remaining_without_human_evidence_pack": 1,
    }
    if summary != expected_summary:
        fail(f"summary is not deterministic: {summary}")

    identities = [
        (row["identity"]["from"], row["identity"]["relation"], row["identity"]["to"])
        for row in committed["remaining_relations"]
    ]
    if len(identities) != len(set(identities)):
        fail("remaining relation identities contain duplicates")
    if VERIFIED in identities:
        fail("newly verified relation remains in the residual inventory")
    if any(row["disposition"] != "UNVERIFIED" for row in committed["remaining_relations"]):
        fail("an unresolved relation was promoted")

    audit = json.loads(AUDIT.read_text(encoding="utf-8"))
    if audit.get("audit_result") != "PASS":
        fail("residual independent audit is not PASS")
    checks = audit.get("checks", [])
    if len(checks) != 1:
        fail("residual independent audit must have exactly one check")
    check = checks[0]
    identity = (check.get("from_id"), check.get("relation"), check.get("to_id"))
    if identity != VERIFIED or check.get("result") != "PASS" or check.get("differences") != []:
        fail("residual independent audit check is not the expected clean relation")

    fee_rows = json.loads((DATA / "remuneration-current-text.json").read_text(encoding="utf-8"))
    note1 = next((row for row in fee_rows if row.get("fee_id") == "fee.dayservice.note.1"), None)
    if note1 is None or "指定居宅サービス基準第92条に規定する指定通所介護" not in note1.get("official_text", ""):
        fail("canonical current remuneration text lacks the explicit Article 92 definition")

    ordinance_rows = json.loads((DATA / "ordinance37-nodes.json").read_text(encoding="utf-8"))
    article92 = next((row for row in ordinance_rows if row.get("id") == "ordinance37.article.92"), None)
    if article92 is None or "指定居宅サービスに該当する通所介護" not in article92.get("official_text", ""):
        fail("canonical Ordinance 37 Article 92 text no longer matches the verified target")

    print("Worker-C residual relation validation: PASS (188 total / 130 verified / 58 remaining)")


if __name__ == "__main__":
    main()
