#!/usr/bin/env python3
"""Build the Worker-C residual relation verification inventory."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

from build_relation_verification_queue import build as build_queue

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUTPUT = DATA / "residual-relation-independent-verification.generated.json"
AUDIT = DATA / "residual-relation-service-definition-independent-audit.json"
EVIDENCE_PACK = DATA / "relation-human-review-evidence-pack.json"

PATTERN_CATALOG = [
    "EXPLICIT_LEGAL_CITATION",
    "EXPLICIT_NOTICE_TO_ORDINANCE_CITATION",
    "REMUNERATION_DELEGATION",
    "SOURCE_DOCUMENT_CROSS_REFERENCE",
    "SAME_SOURCE_INTERNAL_REFERENCE",
    "OFFICIAL_ANNEX_OR_TABLE_LINKAGE",
    "SERVICE_APPLICABILITY_RELATION",
    "DERIVED_RELATION_REQUIRING_INDEPENDENT_CONFIRMATION",
    "NO_EXACT_PRIMARY_EVIDENCE",
]


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def key(identity: dict) -> str:
    return f"{identity['from']}|{identity['relation']}|{identity['to']}"


def evidence_pattern(item: dict) -> str:
    classification = item["classification"]
    if classification == "SOURCE_LINK_FRESHNESS_OR_DIRECT_EVIDENCE_REQUIRED":
        return "SOURCE_DOCUMENT_CROSS_REFERENCE"
    if classification == "SEMANTIC_TEXT_CHECK_REQUIRED":
        return "EXPLICIT_NOTICE_TO_ORDINANCE_CITATION"
    if classification in {
        "CROSS_LAYER_HUMAN_REVIEW_REQUIRED",
        "HUMAN_SEMANTIC_REVIEW_REQUIRED",
    }:
        return "DERIVED_RELATION_REQUIRING_INDEPENDENT_CONFIRMATION"
    return "NO_EXACT_PRIMARY_EVIDENCE"


def compact_locator(row: dict) -> dict:
    return {
        k: row[k]
        for k in ("source_id", "url", "locator", "evidence_kind")
        if row.get(k) is not None
    }


def candidate_evidence(item: dict, pack_by_key: dict[str, dict]) -> dict:
    relation_key = key(item["identity"])
    packed = pack_by_key.get(relation_key)
    if packed is None:
        return {
            "evidence_artifacts": [
                "data/remuneration-source-link-independent-audit.json",
                "data/remuneration-relations.json",
            ],
            "source_pointers": [],
            "target_pointers": [],
            "evidence_fingerprint_sha256": None,
            "unresolved_question": (
                "Freshness-sensitive latest-amendment semantics require exhaustive "
                "current official evidence; the existing independent source-link audit "
                "explicitly excludes this relation."
            ),
        }

    return {
        "evidence_artifacts": ["data/relation-human-review-evidence-pack.json"],
        "source_pointers": [
            compact_locator(row)
            for row in packed.get("source_primary_source_locators", [])
        ],
        "target_pointers": [
            compact_locator(row)
            for row in packed.get("target_primary_source_locators", [])
        ],
        "evidence_fingerprint_sha256": packed.get("evidence_fingerprint_sha256"),
        "source_pointer_status": packed.get("machine_verifiable_subclaims", {}).get(
            "source_pointer_status"
        ),
        "target_pointer_status": packed.get("machine_verifiable_subclaims", {}).get(
            "target_pointer_status"
        ),
        "unresolved_question": packed.get("unresolved_semantic_question"),
    }


def build() -> dict:
    queue = build_queue()
    audit = load(AUDIT)
    pack = load(EVIDENCE_PACK)
    pack_by_key = {row["relation_key"]: row for row in pack.get("items", [])}

    audit_checks = audit.get("checks", [])
    if len(audit_checks) != 1:
        raise ValueError("Worker-C audit must contain exactly one verified relation")
    verified = audit_checks[0]
    verified_identity = {
        "from": verified["from_id"],
        "relation": verified["relation"],
        "to": verified["to_id"],
    }

    items = []
    patterns = Counter()
    pack_matches = 0
    for item in queue["items"]:
        pattern = evidence_pattern(item)
        patterns[pattern] += 1
        relation_key = key(item["identity"])
        if relation_key in pack_by_key:
            pack_matches += 1
        items.append(
            {
                "identity": item["identity"],
                "source_file": item["source_file"],
                "source_state": item["source_state"],
                "relation_type": item["identity"]["relation"],
                "classification": item["classification"],
                "evidence_pattern": pattern,
                "candidate_evidence": candidate_evidence(item, pack_by_key),
                "disposition": "UNVERIFIED",
                "blockers": item["blockers"],
            }
        )

    catalog_counts = {pattern: patterns.get(pattern, 0) for pattern in PATTERN_CATALOG}
    return {
        "format_version": 1,
        "generated_by": "scripts/build_residual_relation_independent_verification.py",
        "policy": (
            "Only direct official-source evidence may create independent VERIFIED state. "
            "Semantic similarity, a derived relation artifact, or an unresolved human-review "
            "proposal is not independent proof."
        ),
        "summary": {
            "canonical_relations_total": queue["inventory_relations"],
            "independently_verified_before_worker_c": audit["coverage"][
                "independently_verified_before"
            ],
            "unverified_before_worker_c": audit["coverage"]["unverified_before"],
            "newly_verified": audit["coverage"]["relations_passed"],
            "independently_verified_after_worker_c": queue[
                "independently_covered_relations"
            ],
            "remaining_unverified": queue["remaining_relations"],
            "removed": 0,
            "downgraded_to_candidate_only": 0,
            "human_evidence_pack_matches": pack_matches,
            "remaining_without_human_evidence_pack": len(items) - pack_matches,
        },
        "classification_counts": queue["classification_counts"],
        "evidence_pattern_counts": catalog_counts,
        "newly_verified_relations": [
            {
                "identity": verified_identity,
                "verification_state": "INDEPENDENTLY_VERIFIED",
                "evidence_pattern": "EXPLICIT_LEGAL_CITATION",
                "audit_artifact": "data/residual-relation-service-definition-independent-audit.json",
                "source_primary_evidence": verified["source_primary_evidence"],
                "target_primary_evidence": verified["target_primary_evidence"],
            }
        ],
        "remaining_relations": items,
        "deferred_blocker_categories": {
            "SOURCE_LINK_FRESHNESS_OR_DIRECT_EVIDENCE_REQUIRED": (
                "A latest/current claim needs exhaustive current-source evidence; negative "
                "search or source existence is insufficient."
            ),
            "SEMANTIC_TEXT_CHECK_REQUIRED": (
                "The notice-to-ordinance mapping still requires exact semantic adjudication "
                "unless an explicit source reference can be independently reconstructed."
            ),
            "CROSS_LAYER_HUMAN_REVIEW_REQUIRED": (
                "Primary texts are resolved, but the exact cross-layer relation label is not "
                "explicitly established by the source."
            ),
            "HUMAN_SEMANTIC_REVIEW_REQUIRED": (
                "Question-to-authority relevance is semantic and cannot be established from "
                "lexical or topical overlap alone."
            ),
        },
        "safety": {
            "semantic_similarity_used_as_proof": False,
            "unresolved_relations_promoted": False,
            "human_review_simulated": False,
            "publication_changed": False,
            "global_generated_artifacts_changed": False,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    rendered = json.dumps(build(), ensure_ascii=False, indent=2) + "\n"
    if args.check:
        if not OUTPUT.exists() or OUTPUT.read_text(encoding="utf-8") != rendered:
            raise SystemExit("Worker-C residual relation inventory is stale; run builder")
        print("Worker-C residual relation inventory: current")
        return
    OUTPUT.write_text(rendered, encoding="utf-8")
    print(f"wrote {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
