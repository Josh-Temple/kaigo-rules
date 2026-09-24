#!/usr/bin/env python3
"""Identity-level coverage for independently audited semantic/cross-layer relations."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

RELATION_FILES = (
    "care-insurance-act-relations.json",
    "fee-guidance-relations.json",
    "notice-ordinance-relations.json",
    "ordinance37-relations.json",
    "relationships.json",
    "remuneration-delegated-relations.json",
    "remuneration-relations.json",
)
FROM_KEYS = ("from", "from_id", "from_guidance_id", "from_notice_id", "from_fee_id")
TO_KEYS = ("to", "to_id", "to_fee_id", "to_ordinance_id", "to_source_id")


def load(name: str):
    return json.loads((DATA / name).read_text(encoding="utf-8"))


def first_value(row: dict, keys: tuple[str, ...]) -> str | None:
    for key in keys:
        value = row.get(key)
        if value:
            return str(value)
    return None


def make_identity(source, relation, target) -> tuple[str, str, str]:
    if not source or not relation or not target:
        raise ValueError(
            f"incomplete relation identity: source={source!r}, relation={relation!r}, target={target!r}"
        )
    return str(source), str(relation), str(target)


def relation_identity(row: dict) -> tuple[str, str, str]:
    return make_identity(
        first_value(row, FROM_KEYS),
        row.get("relation"),
        first_value(row, TO_KEYS),
    )


def canonical_inventory() -> set[tuple[str, str, str]]:
    identities: set[tuple[str, str, str]] = set()
    duplicates: list[tuple[str, str, str]] = []
    for name in RELATION_FILES:
        for row in load(name):
            if row.get("relation") == "contains":
                continue
            identity = relation_identity(row)
            if identity in identities:
                duplicates.append(identity)
            identities.add(identity)
    if duplicates:
        rendered = ", ".join("|".join(item) for item in sorted(set(duplicates)))
        raise ValueError(f"duplicate canonical relation identities: {rendered}")
    return identities


def require_clean_check(check: dict, lane: str) -> None:
    if check.get("result") != "PASS" or check.get("differences") != []:
        raise ValueError(f"{lane}: audit check is not clean: {check.get('id') or check!r}")


def explicit_reference_identities(audit: dict) -> set[tuple[str, str, str]]:
    if audit.get("audit_result") != "PASS":
        raise ValueError("explicit-legal-reference audit is not PASS")
    checks = audit.get("checks", [])
    if len(checks) != 1:
        raise ValueError("explicit-legal-reference audit check set changed")
    check = checks[0]
    require_clean_check(check, "explicit-legal-reference")
    identities = {
        make_identity(
            check.get("source_article_id"),
            check.get("relation"),
            f"ordinance37.article.{target}",
        )
        for target in check.get("expected_relation_targets", [])
    }
    expected = audit.get("coverage", {}).get(
        "explicit_legal_reference_relations_independently_verified"
    )
    if len(identities) != expected:
        raise ValueError("explicit-legal-reference identity count changed")
    return identities


def careact_internal_identities(audit: dict) -> set[tuple[str, str, str]]:
    if audit.get("audit_result") != "PASS":
        raise ValueError("careact-internal audit is not PASS")
    identities = set()
    for check in audit.get("checks", []):
        require_clean_check(check, "careact-internal")
        identities.add(
            make_identity(
                check.get("source_article_id"),
                check.get("relation"),
                check.get("target_id"),
            )
        )
    if len(identities) != audit.get("coverage", {}).get("relations_passed"):
        raise ValueError("careact-internal identity count changed")
    return identities


def cross_layer_identities(audit: dict) -> set[tuple[str, str, str]]:
    if audit.get("audit_result") != "PASS":
        raise ValueError("cross-layer-source-chain audit is not PASS")
    identities = set()
    for check in audit.get("checks", []):
        require_clean_check(check, "cross-layer-source-chain")
        if check.get("target_id"):
            identities.add(
                make_identity(
                    check.get("source_id"),
                    check.get("relation"),
                    check.get("target_id"),
                )
            )
            continue

        if check.get("target_layer") != "ordinance37":
            raise ValueError(
                f"cross-layer-source-chain: unsupported target layer: {check.get('target_layer')!r}"
            )
        targets = check.get("committed_relation_targets", [])
        if not targets:
            raise ValueError("cross-layer-source-chain: grouped target list is empty")
        for target in targets:
            identities.add(
                make_identity(
                    check.get("source_id"),
                    check.get("relation"),
                    f"ordinance37.article.{target}",
                )
            )
    if len(identities) != audit.get("coverage", {}).get("relations_passed"):
        raise ValueError("cross-layer-source-chain identity count changed")
    return identities


def remuneration_delegation_identities(audit: dict) -> set[tuple[str, str, str]]:
    if audit.get("audit_result") != "PASS":
        raise ValueError("remuneration-delegation audit is not PASS")
    identities = set()
    for check in audit.get("checks", []):
        require_clean_check(check, "remuneration-delegation")
        identities.add(
            make_identity(
                check.get("from_id"),
                check.get("relation"),
                check.get("to_id"),
            )
        )
    if len(identities) != audit.get("coverage", {}).get("relations_passed"):
        raise ValueError("remuneration-delegation identity count changed")
    return identities


def build_relation_coverage() -> dict:
    inventory = canonical_inventory()
    lane_specs = (
        (
            "explicit-legal-reference",
            "data/relation-semantic-independent-audit.json",
            explicit_reference_identities(load("relation-semantic-independent-audit.json")),
        ),
        (
            "careact-internal",
            "data/careact-internal-relation-independent-audit.json",
            careact_internal_identities(load("careact-internal-relation-independent-audit.json")),
        ),
        (
            "cross-layer-source-chain",
            "data/cross-layer-source-chain-independent-audit.json",
            cross_layer_identities(load("cross-layer-source-chain-independent-audit.json")),
        ),
        (
            "remuneration-delegation",
            "data/remuneration-delegation-relation-independent-audit.json",
            remuneration_delegation_identities(load("remuneration-delegation-relation-independent-audit.json")),
        ),
    )

    lane_rows = []
    verified: set[tuple[str, str, str]] = set()
    owner: dict[tuple[str, str, str], str] = {}
    overlaps = []

    for lane_id, evidence, identities in lane_specs:
        missing = identities - inventory
        if missing:
            rendered = ", ".join("|".join(item) for item in sorted(missing))
            raise ValueError(
                f"{lane_id}: audited relation is missing from canonical inventory: {rendered}"
            )

        for identity in identities:
            previous = owner.get(identity)
            if previous is not None:
                overlaps.append((identity, previous, lane_id))
            owner[identity] = lane_id
        verified.update(identities)
        lane_rows.append(
            {
                "id": lane_id,
                "status": "PASS",
                "verified_relations": len(identities),
                "evidence": evidence,
            }
        )

    if overlaps:
        rendered = "; ".join(
            f"{'|'.join(identity)} ({previous}, {lane})"
            for identity, previous, lane in sorted(overlaps)
        )
        raise ValueError(f"independent audit lanes overlap: {rendered}")

    return {
        "inventory": inventory,
        "verified": verified,
        "remaining": inventory - verified,
        "lanes": lane_rows,
        "overlap_relations": 0,
        "identity_validation": "PASS",
    }
