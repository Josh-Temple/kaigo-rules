#!/usr/bin/env python3
"""Validate the frozen Kaigo Ops Machine Retrieval Benchmark v0.1 fixture."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BENCHMARK = ROOT / "docs" / "kaigo-ops" / "research" / "issues" / "information-search" / "machine-retrieval-benchmark-v0.1.json"
FIELD_PILOT = ROOT / "docs" / "kaigo-ops" / "research" / "issues" / "information-search" / "field-validation-v0.1.json"
QUESTIONS = ROOT / "data" / "questions.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    benchmark = load(BENCHMARK)
    pilot = load(FIELD_PILOT)
    questions = {row["slug"]: row for row in load(QUESTIONS)}
    errors: list[str] = []

    if benchmark.get("format_version") != 1:
        errors.append("machine retrieval: unsupported format_version")
    if benchmark.get("result_state") != "NOT_RUN":
        errors.append("machine retrieval: result_state must remain NOT_RUN until a production run is reviewed")
    if benchmark.get("relation_to_human_validation") != "COMPLEMENTARY_NOT_SUBSTITUTE":
        errors.append("machine retrieval: human-validation relationship drifted")

    pilot_rows = pilot.get("questions", [])
    pilot_by_id = {row["id"]: row for row in pilot_rows}
    if len(pilot_by_id) != 10:
        errors.append(f"machine retrieval: expected 10 fixed field questions, found {len(pilot_by_id)}")

    cases = benchmark.get("cases", [])
    if len(cases) != 30:
        errors.append(f"machine retrieval: expected 30 cases, found {len(cases)}")

    ids = [row.get("id") for row in cases]
    if len(set(ids)) != len(ids):
        errors.append("machine retrieval: duplicate case id")

    queries = [str(row.get("query") or "").strip() for row in cases]
    if any(not q for q in queries):
        errors.append("machine retrieval: blank query")
    if len(set(queries)) != len(queries):
        errors.append("machine retrieval: duplicate query")

    counts = Counter(row.get("field_validation_id") for row in cases)
    for field_id, pilot_row in pilot_by_id.items():
        if counts[field_id] != 3:
            errors.append(
                f"{field_id}: expected 3 machine-retrieval variants, found {counts[field_id]}"
            )
        slug = pilot_row["slug"]
        canonical = questions.get(slug)
        if not canonical:
            errors.append(f"{field_id}: canonical question missing for {slug}")
            continue
        if canonical.get("status") != "verified":
            errors.append(f"{field_id}: canonical question is not verified")

        expected_sources = sorted(
            ref["source_id"]
            for ref in canonical.get("source_refs", [])
            if ref.get("source_id")
        )
        if not expected_sources:
            errors.append(f"{field_id}: canonical question has no source_refs")

        for case in [c for c in cases if c.get("field_validation_id") == field_id]:
            if case.get("expected_question_slug") != slug:
                errors.append(f"{case.get('id')}: expected question slug drifted")
            if sorted(case.get("expected_source_ids", [])) != expected_sources:
                errors.append(f"{case.get('id')}: expected source ids drifted")

    unknown = sorted(set(counts) - set(pilot_by_id))
    if unknown:
        errors.append(f"machine retrieval: unknown field_validation_id values: {unknown}")

    if errors:
        raise SystemExit("\n".join(errors))

    print(
        "Kaigo Ops machine retrieval v0.1: valid "
        f"({len(cases)} cases / {len(pilot_by_id)} questions / 3 variants each)"
    )


if __name__ == "__main__":
    main()
