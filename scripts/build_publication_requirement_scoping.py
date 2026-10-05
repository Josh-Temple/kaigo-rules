#!/usr/bin/env python3
"""Build publication-unit requirement scoping without changing canonical assurance state."""
from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MATRIX_PATH = ROOT / "data/database-coverage-matrix.generated.json"
OUTPUT_PATH = ROOT / "data/publication-requirement-scoping.json"

CURRENTNESS_PASS = {
    "PASS",
    "CURRENT",
    "CURRENT_OFFICIAL_CONSOLIDATED",
    "CURRENT_OFFICIAL_VERSIONED",
}
RELATION_PASS = {"PASS", "VERIFIED"}
HUMAN_REVIEW_PASS = {"REVIEWED", "PASS"}

REQUIREMENT_VALUES = {
    "REQUIRED",
    "NOT_REQUIRED",
    "UNRESOLVED_WHETHER_REQUIRED",
}

ALL_PUBLICATION_FIELDS = {
    "service_id",
    "service_label",
    "source_family",
    "source_family_label",
    "source_text",
    "item_body",
    "source_title",
    "source_url",
    "source_locator",
    "source_version",
    "source_fingerprint",
    "observed_at",
    "currentness_state",
    "effective_date",
    "currentness_evidence",
    "applicability_state",
    "applicability_evidence",
    "relation_identity",
    "relation_label",
    "target_url",
    "target_locator",
    "reviewed_explanatory_text",
    "review_decision_reference",
}

PUBLICATION_UNIT_DEFINITIONS = (
    {
        "unit_type": "SOURCE_TEXT_ITEM_BODY",
        "description": "Primary-source text or canonical item body with provenance only; no relation assertion or review-dependent explanation.",
        "requires_item_body_pass": True,
        "relation_requirement": "NOT_REQUIRED",
        "human_review_requirement": "NOT_REQUIRED",
        "field_allowlist": [
            "service_id",
            "service_label",
            "source_family",
            "source_family_label",
            "source_text",
            "item_body",
            "source_title",
            "source_url",
            "source_locator",
            "source_version",
            "source_fingerprint",
            "observed_at",
        ],
    },
    {
        "unit_type": "SOURCE_METADATA_LOCATOR",
        "description": "Source identity, provenance metadata, URL, locator, version, and fingerprint without a body or relation claim.",
        "requires_item_body_pass": False,
        "relation_requirement": "NOT_REQUIRED",
        "human_review_requirement": "NOT_REQUIRED",
        "field_allowlist": [
            "service_id",
            "service_label",
            "source_family",
            "source_family_label",
            "source_title",
            "source_url",
            "source_locator",
            "source_version",
            "source_fingerprint",
            "observed_at",
        ],
    },
    {
        "unit_type": "CURRENTNESS_STATEMENT",
        "description": "A source/service currentness statement backed by canonical currentness evidence; no relation assertion.",
        "requires_item_body_pass": False,
        "relation_requirement": "NOT_REQUIRED",
        "human_review_requirement": "NOT_REQUIRED",
        "field_allowlist": [
            "service_id",
            "service_label",
            "source_family",
            "source_family_label",
            "source_title",
            "source_url",
            "source_locator",
            "source_version",
            "source_fingerprint",
            "observed_at",
            "currentness_state",
            "effective_date",
            "currentness_evidence",
        ],
    },
    {
        "unit_type": "SERVICE_APPLICABILITY_STATEMENT",
        "description": "A source-family applicability statement scoped to one service, without cross-layer relation semantics.",
        "requires_item_body_pass": False,
        "relation_requirement": "NOT_REQUIRED",
        "human_review_requirement": "NOT_REQUIRED",
        "field_allowlist": [
            "service_id",
            "service_label",
            "source_family",
            "source_family_label",
            "source_title",
            "source_url",
            "source_locator",
            "source_version",
            "source_fingerprint",
            "observed_at",
            "applicability_state",
            "applicability_evidence",
        ],
    },
    {
        "unit_type": "CROSS_LAYER_RELATION_LINK",
        "description": "A bare cross-layer relation assertion without explanatory interpretation.",
        "requires_item_body_pass": True,
        "relation_requirement": "REQUIRED",
        "human_review_requirement": "NOT_REQUIRED",
        "field_allowlist": [
            "service_id",
            "service_label",
            "source_family",
            "source_family_label",
            "source_url",
            "source_locator",
            "target_url",
            "target_locator",
            "relation_identity",
            "relation_label",
        ],
    },
    {
        "unit_type": "INTERPRETIVE_RELATION_EXPLANATION",
        "description": "A cross-layer relation plus interpretation or explanatory semantics.",
        "requires_item_body_pass": True,
        "relation_requirement": "REQUIRED",
        "human_review_requirement": "REQUIRED",
        "field_allowlist": [
            "service_id",
            "service_label",
            "source_family",
            "source_family_label",
            "source_url",
            "source_locator",
            "target_url",
            "target_locator",
            "relation_identity",
            "relation_label",
            "reviewed_explanatory_text",
            "review_decision_reference",
        ],
    },
    {
        "unit_type": "REVIEW_DEPENDENT_EXPLANATORY_TEXT",
        "description": "Explanatory text whose publication depends on a recorded human review decision but does not itself assert a cross-layer relation.",
        "requires_item_body_pass": True,
        "relation_requirement": "NOT_REQUIRED",
        "human_review_requirement": "REQUIRED",
        "field_allowlist": [
            "service_id",
            "service_label",
            "source_family",
            "source_family_label",
            "source_url",
            "source_locator",
            "reviewed_explanatory_text",
            "review_decision_reference",
        ],
    },
)


def _load(path: Path):
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def _state(cell: dict, axis: str) -> str:
    value = cell.get(axis) or {}
    return str(value.get("state", "MISSING"))


def axis_observations(cell: dict) -> dict:
    return {
        "corpus_availability": _state(cell, "corpus_availability"),
        "service_scope": _state(cell, "service_scope"),
        "ingestion": _state(cell, "ingestion"),
        "item_body_verification": _state(cell, "item_body_verification"),
        "currentness": _state(cell, "currentness"),
        "relation_verification": _state(cell, "relation_verification"),
        "human_review": _state(cell, "human_review"),
        "publication": _state(cell, "publication"),
        "route_exposure": _state(cell, "route_exposure"),
    }


def _is_not_applicable(axis_states: dict) -> bool:
    return any(
        axis_states[key] == "NOT_APPLICABLE"
        for key in ("ingestion", "item_body_verification", "currentness")
    )


def evaluate_publication_unit(axis_states: dict, definition: dict) -> dict:
    relation_requirement = definition["relation_requirement"]
    human_requirement = definition["human_review_requirement"]
    if relation_requirement not in REQUIREMENT_VALUES:
        raise ValueError(f"unsupported relation requirement: {relation_requirement}")
    if human_requirement not in REQUIREMENT_VALUES:
        raise ValueError(f"unsupported human review requirement: {human_requirement}")

    fields = list(definition["field_allowlist"])
    unknown_fields = sorted(set(fields) - ALL_PUBLICATION_FIELDS)
    if unknown_fields:
        raise ValueError(f"unknown publication fields: {unknown_fields}")

    if _is_not_applicable(axis_states):
        return {
            "unit_type": definition["unit_type"],
            "readiness": "NOT_APPLICABLE",
            "blocking_reasons": [],
            "requirements": {
                "corpus_available": True,
                "scope_defined": True,
                "ingestion_complete": True,
                "item_body_pass": bool(definition["requires_item_body_pass"]),
                "currentness_pass": True,
                "relation_verification": relation_requirement,
                "human_review": human_requirement,
            },
            "field_allowlist": fields,
            "excluded_sensitive_fields": sorted(ALL_PUBLICATION_FIELDS - set(fields)),
            "canonical_relation_state_observed": axis_states["relation_verification"],
            "canonical_human_review_state_observed": axis_states["human_review"],
        }

    blockers = []
    if axis_states["corpus_availability"] != "AVAILABLE":
        blockers.append("BLOCKED_CORPUS")
    if axis_states["service_scope"] != "SCOPE_DEFINED":
        blockers.append("BLOCKED_SCOPE")
    if axis_states["ingestion"] != "INGESTED":
        blockers.append("BLOCKED_INGESTION")
    if definition["requires_item_body_pass"] and axis_states["item_body_verification"] != "PASS":
        blockers.append("BLOCKED_ITEM_BODY")

    # The wave contract requires unresolved currentness to block every publication unit,
    # including metadata-only publication.
    if axis_states["currentness"] not in CURRENTNESS_PASS:
        blockers.append("BLOCKED_CURRENTNESS")

    if relation_requirement == "REQUIRED":
        if axis_states["relation_verification"] not in RELATION_PASS:
            blockers.append("BLOCKED_RELATION")
    elif relation_requirement == "UNRESOLVED_WHETHER_REQUIRED":
        blockers.append("BLOCKED_RELATION_REQUIREMENT_UNRESOLVED")

    if human_requirement == "REQUIRED":
        if axis_states["human_review"] not in HUMAN_REVIEW_PASS:
            blockers.append("BLOCKED_HUMAN_REVIEW")
    elif human_requirement == "UNRESOLVED_WHETHER_REQUIRED":
        blockers.append("BLOCKED_HUMAN_REVIEW_REQUIREMENT_UNRESOLVED")

    return {
        "unit_type": definition["unit_type"],
        "readiness": "READY_FOR_PUBLICATION_REVIEW" if not blockers else blockers[0],
        "blocking_reasons": blockers,
        "requirements": {
            "corpus_available": True,
            "scope_defined": True,
            "ingestion_complete": True,
            "item_body_pass": bool(definition["requires_item_body_pass"]),
            "currentness_pass": True,
            "relation_verification": relation_requirement,
            "human_review": human_requirement,
        },
        "field_allowlist": fields,
        "excluded_sensitive_fields": sorted(ALL_PUBLICATION_FIELDS - set(fields)),
        "canonical_relation_state_observed": axis_states["relation_verification"],
        "canonical_human_review_state_observed": axis_states["human_review"],
    }


def build_artifact() -> dict:
    matrix = _load(MATRIX_PATH)
    rows = []
    primary = Counter()
    blockers = Counter()
    candidates = Counter()
    by_family = defaultdict(Counter)

    for service in matrix["services"]:
        for cell in service["source_families"]:
            axes = axis_observations(cell)
            units = []
            for definition in PUBLICATION_UNIT_DEFINITIONS:
                result = evaluate_publication_unit(axes, definition)
                units.append(result)
                primary[result["readiness"]] += 1
                by_family[cell["source_family"]][result["readiness"]] += 1
                blockers.update(result["blocking_reasons"])
                if result["readiness"] == "READY_FOR_PUBLICATION_REVIEW":
                    candidates[result["unit_type"]] += 1

            rows.append(
                {
                    "service_id": service["service_id"],
                    "service_label": service.get("label"),
                    "source_family": cell["source_family"],
                    "source_family_label": cell.get("label"),
                    "canonical_axis_observations": axes,
                    "publication_units": units,
                }
            )

    candidate_total = sum(candidates.values())
    return {
        "format_version": 1,
        "generated_by": "scripts/build_publication_requirement_scoping.py",
        "projection_only": True,
        "purpose": "Scope publication requirements by unit so relation and human review are required only where the published assertion actually depends on them.",
        "policy": {
            "canonical_relation_writeback_allowed": False,
            "canonical_human_review_writeback_allowed": False,
            "publication_writeback_allowed": False,
            "route_auto_enable_allowed": False,
            "readiness_implies_publication": False,
            "not_required_means_pass": False,
            "unverified_relations_may_influence_safe_units": False,
            "unreviewed_explanations_may_influence_safe_units": False,
            "currentness_required_for_every_publication_unit": True,
            "field_allowlist_is_exhaustive": True,
        },
        "canonical_inputs": [
            "data/database-coverage-matrix.generated.json"
        ],
        "publication_unit_definitions": list(PUBLICATION_UNIT_DEFINITIONS),
        "summary": {
            "service_source_family_cells": len(rows),
            "publication_units_total": sum(len(row["publication_units"]) for row in rows),
            "ready_for_publication_review_candidates": candidate_total,
            "ready_candidates_by_unit_type": dict(sorted(candidates.items())),
            "primary_readiness": dict(sorted(primary.items())),
            "blocking_reason_counts": dict(sorted(blockers.items())),
            "by_source_family": {
                family: dict(sorted(counts.items()))
                for family, counts in sorted(by_family.items())
            },
        },
        "cells": rows,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    artifact = build_artifact()

    if args.check:
        if not OUTPUT_PATH.exists():
            raise SystemExit("publication requirement scoping artifact missing; run builder")
        if _load(OUTPUT_PATH) != artifact:
            raise SystemExit("publication requirement scoping artifact is stale; run builder")
        print("publication requirement scoping artifact: PASS")
        return

    OUTPUT_PATH.write_text(
        json.dumps(artifact, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"wrote {OUTPUT_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
