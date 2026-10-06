#!/usr/bin/env python3
"""Validate Worker B residual currentness impact before or after Worker E writeback."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MATRIX = ROOT / "data/database-coverage-matrix.generated.json"
READINESS = ROOT / "data/publication-readiness.generated.json"
CANONICAL = ROOT / "data/verification/bounded-currentness-closure-worker-b.json"
HIGH_VALUE_EXPANSION = (
    ROOT / "data/verification/high-value-currentness-expansion-worker-c.json"
)
GOVERNING_RESIDUAL = (
    ROOT / "data/verification/governing-standards-residual-currentness-worker-a.json"
)
FINAL_GOVERNING = (
    ROOT / "data/verification/final-standards-residual-relation-worker-c.json"
)
DELEGATED_CURRENTNESS = (
    ROOT / "data/verification/delegated-remuneration-currentness-worker-b.json"
)
TARGETS = {"dayservice", "dayrehab"}
FAMILY = "governing_standards_ordinance"
EXPECTED_UNITS = {
    "SOURCE_TEXT_ITEM_BODY",
    "SOURCE_METADATA_LOCATOR",
    "CURRENTNESS_STATEMENT",
    "SERVICE_APPLICABILITY_STATEMENT",
}


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    matrix, readiness, canonical = load(MATRIX), load(READINESS), load(CANONICAL)
    failures: list[str] = []
    cells = {
        (service["service_id"], cell["source_family"]): cell
        for service in matrix["services"]
        for cell in service["source_families"]
    }
    ready = {
        (row["service_id"], row["source_family"]): row
        for row in readiness["cells"]
    }

    standards = canonical["priority_1"][FAMILY]
    before = standards["before"]
    after = standards["after"]
    coverage = matrix["summary"]["source_family_coverage"][FAMILY]["currentness"]
    preintegration = coverage == before

    subsequent_governing_promotions = []
    if GOVERNING_RESIDUAL.exists():
        residual = load(GOVERNING_RESIDUAL)
        if residual.get("artifact_kind") != "GOVERNING_STANDARDS_RESIDUAL_CURRENTNESS_CLOSURE":
            failures.append("unexpected Worker A residual governing-currentness artifact kind")
        subsequent_governing_promotions = [
            row
            for row in residual.get("decisions", [])
            if row.get("promotion_applied") is True
        ]

    final_governing_promotions = []
    if FINAL_GOVERNING.exists():
        final_artifact = load(FINAL_GOVERNING)
        if (
            final_artifact.get("artifact_kind")
            != "FINAL_STANDARDS_AND_RESIDUAL_RELATION_ASSURANCE"
        ):
            failures.append("unexpected Worker C final governing-currentness artifact kind")
        final_governing_promotions = [
            row
            for row in (final_artifact.get("governing_standards") or {}).get(
                "decisions", []
            )
            if row.get("promotion_applied") is True
        ]

    expected_governing_after = dict(after)
    all_subsequent_governing = (
        subsequent_governing_promotions + final_governing_promotions
    )
    if all_subsequent_governing:
        expected_governing_after["PASS"] = expected_governing_after.get("PASS", 0) + len(
            all_subsequent_governing
        )
        expected_governing_after["NOT_ESTABLISHED"] = (
            expected_governing_after.get("NOT_ESTABLISHED", 0)
            - len(all_subsequent_governing)
        )
        expected_governing_after = {
            key: value for key, value in expected_governing_after.items() if value
        }

    integrated = coverage in (after, expected_governing_after)
    if not preintegration and not integrated:
        failures.append(
            "governing-standards currentness matches neither canonical before nor "
            f"bounded/subsequent integrated state: {coverage}"
        )

    new_ids = set(standards["newly_promoted_service_ids"])
    if new_ids != TARGETS:
        failures.append(f"canonical promoted target mismatch: {sorted(new_ids)}")
    if standards.get("projected_ready_increase") != len(TARGETS):
        failures.append("projected READY increase mismatch")

    for sid in sorted(TARGETS):
        promotion = next(
            (
                row
                for row in canonical["promotions"]
                if row.get("service_id") == sid
                and row.get("source_family") == FAMILY
            ),
            None,
        )
        if promotion is None:
            failures.append(f"{sid}: canonical promotion missing")
            continue
        cell = cells[(sid, FAMILY)]
        row = ready[(sid, FAMILY)]
        if (cell.get("item_body_verification") or {}).get("state") != "PASS":
            failures.append(f"{sid}: item-body prerequisite is not PASS")
        if (cell.get("service_scope") or {}).get("state") != "SCOPE_DEFINED":
            failures.append(f"{sid}: service scope prerequisite is not SCOPE_DEFINED")

        if preintegration:
            prior = promotion.get("prior_currentness_state")
            if (cell.get("currentness") or {}).get("state") != prior:
                failures.append(f"{sid}: preintegration currentness differs from canonical prior state")
            if row.get("readiness") != "BLOCKED_CURRENTNESS":
                failures.append(f"{sid}: preintegration readiness is {row.get('readiness')}")
        else:
            if (cell.get("currentness") or {}).get("state") != "PASS":
                failures.append(f"{sid}: integrated currentness is not PASS")
            if row.get("readiness") != "READY_FOR_PUBLICATION_REVIEW":
                failures.append(f"{sid}: integrated readiness is {row.get('readiness')}")
            if set(row.get("ready_publication_units") or []) != EXPECTED_UNITS:
                failures.append(f"{sid}: ready units mismatch")

    current_gaps = len(matrix["summary"]["currentness_gaps"])

    downstream_promotions = []
    if HIGH_VALUE_EXPANSION.exists():
        expansion = load(HIGH_VALUE_EXPANSION)
        if expansion.get("artifact_kind") != "CANONICAL_HIGH_VALUE_CURRENTNESS_EXPANSION_DECISION":
            failures.append("unexpected Worker C currentness expansion artifact kind")
        downstream_promotions.extend(
            row
            for row in expansion.get("promotions", [])
            if row.get("promotion_applied") is True
        )
    downstream_promotions.extend(subsequent_governing_promotions)
    downstream_promotions.extend(final_governing_promotions)
    if DELEGATED_CURRENTNESS.exists():
        delegated = load(DELEGATED_CURRENTNESS)
        if delegated.get("artifact_kind") not in {
            "DELEGATED_REMUNERATION_BOUNDED_CURRENTNESS_DECISIONS",
            "DELEGATED_REMUNERATION_RESIDUAL_CURRENTNESS_DECISIONS",
        }:
            failures.append("unexpected Worker B delegated-currentness artifact kind")
        downstream_promotions.extend(
            row
            for row in delegated.get("promotions", [])
            if row.get("promotion_applied") is True
        )

    downstream_pass = sum(
        1
        for row in downstream_promotions
        if (cells.get((row["service_id"], row["source_family"])) or {})
        .get("currentness", {})
        .get("state") == "PASS"
    )
    if downstream_pass not in {0, len(downstream_promotions)}:
        failures.append(
            "Worker C currentness expansion must be either wholly unapplied or wholly integrated"
        )

    projected_gaps = current_gaps - len(TARGETS) if preintegration else current_gaps
    expected_after_b = 320
    expected_integrated_gaps = expected_after_b - downstream_pass

    if preintegration and projected_gaps != expected_after_b:
        failures.append(
            f"expected {expected_after_b} projected currentness gaps, got {projected_gaps}"
        )
    if integrated and current_gaps != expected_integrated_gaps:
        failures.append(
            f"expected {expected_integrated_gaps} integrated currentness gaps, got {current_gaps}"
        )

    print(
        json.dumps(
            {
                "result": "PASS" if not failures else "FAIL",
                "integrated": integrated,
                "preintegration": preintegration,
                "new_currentness_pass_cells": len(TARGETS),
                "expected_ready_units": len(TARGETS) * len(EXPECTED_UNITS),
                "projected_currentness_gaps": projected_gaps,
                "failures": failures,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
