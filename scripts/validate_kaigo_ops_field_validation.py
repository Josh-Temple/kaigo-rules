#!/usr/bin/env python3
"""Validate the frozen Kaigo Ops information-search field pilot against canonical questions."""

from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PILOT = ROOT / "docs" / "kaigo-ops" / "research" / "issues" / "information-search" / "field-validation-v0.1.json"
QUESTIONS = ROOT / "data" / "questions.json"
RUN_TEMPLATE = ROOT / "docs" / "kaigo-ops" / "research" / "issues" / "information-search" / "field-validation-run-template-v0.1.csv"
ADJUDICATION_TEMPLATE = ROOT / "docs" / "kaigo-ops" / "research" / "issues" / "information-search" / "field-validation-adjudication-template-v0.1.csv"

RUN_HEADERS = [
    "attempt_id",
    "participant_id",
    "assignment_pattern",
    "question_id",
    "question_slug",
    "condition",
    "time_to_first_authoritative_source_sec",
    "time_to_answer_submission_sec",
    "answer_text",
    "source_url",
    "source_locator",
    "clicks",
    "query_reformulations",
    "confidence_1_5",
    "observer_notes",
]

ADJUDICATION_HEADERS = [
    "attempt_id",
    "question_id",
    "question_slug",
    "answer_text",
    "source_url",
    "source_locator",
    "authoritative_source_reached",
    "answer_correct",
    "conditions_preserved",
    "source_correct",
    "human_correction_sec",
    "adjudicator_id",
    "adjudication_notes",
]


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def load_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def main() -> None:
    pilot = load_json(PILOT)
    questions = load_json(QUESTIONS)
    canonical = {row["slug"]: row for row in questions}

    errors: list[str] = []

    if pilot.get("format_version") != 1:
        errors.append("field validation: unsupported format_version")

    rows = pilot.get("questions", [])
    if len(rows) != 10:
        errors.append(f"field validation: expected 10 questions, found {len(rows)}")

    ids = [row.get("id") for row in rows]
    slugs = [row.get("slug") for row in rows]
    if len(set(ids)) != len(ids):
        errors.append("field validation: duplicate question id")
    if len(set(slugs)) != len(slugs):
        errors.append("field validation: duplicate canonical slug")

    categories = set()
    multi_source = 0

    for row in rows:
        slug = row.get("slug")
        source = canonical.get(slug)
        if source is None:
            errors.append(f"{slug}: canonical question missing")
            continue

        if source.get("status") != "verified":
            errors.append(f"{slug}: canonical status is not verified")

        checks = {
            "snapshot_title": "title",
            "category": "category",
            "snapshot_last_verified": "last_verified",
        }
        for snapshot_field, canonical_field in checks.items():
            if row.get(snapshot_field) != source.get(canonical_field):
                errors.append(
                    f"{slug}: {snapshot_field} drifted "
                    f"({row.get(snapshot_field)!r} != {source.get(canonical_field)!r})"
                )

        if not source.get("source_refs"):
            errors.append(f"{slug}: verified canonical question has no source_refs")

        categories.add(source.get("category"))
        source_ref_ids = {
            ref.get("source_id")
            for ref in source.get("source_refs", [])
            if ref.get("source_id")
        }
        is_multi_source = (
            len(source_ref_ids) > 1
            or bool(source.get("notice_node_ids"))
            or bool(source.get("qa_item_ids"))
        )
        if is_multi_source:
            multi_source += 1
            if row.get("complexity") != "multi-source":
                errors.append(f"{slug}: expected complexity=multi-source")
        elif row.get("complexity") != "single-source":
            errors.append(f"{slug}: expected complexity=single-source")

    if len(categories) < 5:
        errors.append(f"field validation: expected >=5 categories, found {len(categories)}")
    if multi_source < 3:
        errors.append(f"field validation: expected >=3 multi-source questions, found {multi_source}")

    if pilot.get("result_state") != "NOT_RUN":
        errors.append(
            "field validation: result_state must remain NOT_RUN until measured results are separately reviewed"
        )

    run_headers, run_rows = load_csv(RUN_TEMPLATE)
    if run_headers != RUN_HEADERS:
        errors.append("field validation: run template headers drifted")
    if len(run_rows) != 20:
        errors.append(f"field validation: expected 20 raw attempts, found {len(run_rows)}")

    attempt_ids = [row.get("attempt_id") for row in run_rows]
    if len(set(attempt_ids)) != len(attempt_ids):
        errors.append("field validation: duplicate attempt_id in run template")

    conditions = [row.get("condition") for row in run_rows]
    if conditions.count("A") != 10 or conditions.count("B") != 10:
        errors.append(
            f"field validation: expected balanced A/B attempts (10/10), found "
            f"{conditions.count('A')}/{conditions.count('B')}"
        )

    adjudication_headers, adjudication_rows = load_csv(ADJUDICATION_TEMPLATE)
    if adjudication_headers != ADJUDICATION_HEADERS:
        errors.append("field validation: adjudication template headers drifted")
    if len(adjudication_rows) != 20:
        errors.append(
            f"field validation: expected 20 adjudication attempts, found {len(adjudication_rows)}"
        )

    adjudication_attempts = [row.get("attempt_id") for row in adjudication_rows]
    if adjudication_attempts != attempt_ids:
        errors.append("field validation: adjudication attempts do not match raw attempts")

    forbidden_blind_fields = {"condition", "participant_id", "confidence_1_5"}
    if forbidden_blind_fields.intersection(adjudication_headers):
        errors.append("field validation: adjudication template exposes blinded fields")

    if errors:
        raise SystemExit("\n".join(errors))

    print(
        "Kaigo Ops field validation v0.1: valid "
        f"({len(rows)} questions / {len(categories)} categories / {multi_source} multi-source / "
        f"{len(run_rows)} balanced attempts / blinded adjudication)"
    )


if __name__ == "__main__":
    main()
