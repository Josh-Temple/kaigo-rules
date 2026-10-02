#!/usr/bin/env python3
"""Build a conservative work queue for relations not yet independently covered."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

from relation_verification_coverage import (
    RELATION_FILES,
    build_relation_coverage,
    load,
    relation_identity,
)

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "data" / "relation-verification-queue.json"

DETAILS = {
    "MACHINE_SOURCE_REPARSE_CANDIDATE": {
        "verification_strategy": "Independently reparse the relevant official source and prove the guidance-to-fee alignment from explicit numbering, headings, or cross-references.",
        "blockers": ["Existing committed relation is structural; current independent audit does not yet cover this exact relation identity."],
    },
    "SEMANTIC_TEXT_CHECK_REQUIRED": {
        "verification_strategy": "Compare notice text and ordinance text with explicit evidence for why the notice interprets the target provision; use machine assistance but require semantic adjudication.",
        "blockers": ["The relation expresses interpretation, not mere document structure.", "rouki25-dayservice currentness remains HOLD and must stay separate from relation verification."],
    },
    "HUMAN_SEMANTIC_REVIEW_REQUIRED": {
        "verification_strategy": "Review whether the cited authority actually answers, qualifies, clarifies, or otherwise supports the practical question; preserve evidence links independently of currentness.",
        "blockers": ["Question-to-authority relevance is semantic and should not be inferred from lexical overlap alone."],
    },
    "CROSS_LAYER_HUMAN_REVIEW_REQUIRED": {
        "verification_strategy": "Review the cross-layer legal meaning and record explicit primary-source evidence before adding an independent audit lane.",
        "blockers": ["The mapping is not a direct contains/reference edge and needs a legal-semantic judgment."],
    },
    "SOURCE_LINK_FRESHNESS_OR_DIRECT_EVIDENCE_REQUIRED": {
        "verification_strategy": "Verify the source-level provenance claim against direct official evidence and, where the relation says latest/current, separately prove freshness.",
        "blockers": ["Source existence alone does not prove the relation semantics.", "Freshness-sensitive labels must not be inferred from historical provenance."],
    },
}


def classify(path: str, row: dict) -> str:
    if path == "data/fee-guidance-relations.json":
        return "MACHINE_SOURCE_REPARSE_CANDIDATE"
    if path == "data/notice-ordinance-relations.json":
        return "SEMANTIC_TEXT_CHECK_REQUIRED"
    if path == "data/relationships.json":
        return "HUMAN_SEMANTIC_REVIEW_REQUIRED"
    if path == "data/care-insurance-act-relations.json":
        return "CROSS_LAYER_HUMAN_REVIEW_REQUIRED"
    if path == "data/remuneration-relations.json":
        if row.get("to_source_id"):
            return "SOURCE_LINK_FRESHNESS_OR_DIRECT_EVIDENCE_REQUIRED"
        return "CROSS_LAYER_HUMAN_REVIEW_REQUIRED"
    raise ValueError(f"unclassified remaining relation source: {path}")


def build() -> dict:
    coverage = build_relation_coverage()
    remaining = coverage["remaining"]

    located = {}
    for relative in RELATION_FILES:
        path = f"data/{relative}"
        for row in load(relative):
            if row.get("relation") == "contains":
                continue
            identity = relation_identity(row)
            if identity in remaining:
                if identity in located:
                    raise ValueError(f"remaining relation appears in multiple files: {identity}")
                located[identity] = (path, row)

    if set(located) != remaining:
        missing = sorted(remaining - set(located))
        raise ValueError(f"remaining relation identities could not be located: {missing}")

    items = []
    for identity in sorted(remaining):
        path, row = located[identity]
        classification = classify(path, row)
        detail = DETAILS[classification]
        items.append(
            {
                "identity": {
                    "from": identity[0],
                    "relation": identity[1],
                    "to": identity[2],
                },
                "source_file": path,
                "source_state": row.get("verification_status") or row.get("status"),
                "classification": classification,
                "verification_strategy": detail["verification_strategy"],
                "blockers": detail["blockers"],
            }
        )

    counts = Counter(item["classification"] for item in items)
    priority = [
        "MACHINE_SOURCE_REPARSE_CANDIDATE",
        "SOURCE_LINK_FRESHNESS_OR_DIRECT_EVIDENCE_REQUIRED",
        "SEMANTIC_TEXT_CHECK_REQUIRED",
        "CROSS_LAYER_HUMAN_REVIEW_REQUIRED",
        "HUMAN_SEMANTIC_REVIEW_REQUIRED",
    ]

    return {
        "format_version": 1,
        "generated_by": "scripts/build_relation_verification_queue.py",
        "policy": "Classification selects a verification method only; it never promotes relation, currentness, or human-review state.",
        "inventory_relations": len(coverage["inventory"]),
        "independently_covered_relations": len(coverage["verified"]),
        "remaining_relations": len(remaining),
        "classification_counts": {key: counts.get(key, 0) for key in priority},
        "priority_order": priority,
        "items": items,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    rendered = json.dumps(build(), ensure_ascii=False, indent=2) + "\n"
    if args.check:
        if not OUTPUT.exists() or OUTPUT.read_text(encoding="utf-8") != rendered:
            raise SystemExit("relation verification queue is stale; run builder")
        print("relation verification queue: current")
        return
    OUTPUT.write_text(rendered, encoding="utf-8")
    print(f"wrote {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
