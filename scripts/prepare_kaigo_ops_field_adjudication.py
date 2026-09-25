#!/usr/bin/env python3
"""Create the blinded adjudication CSV for Kaigo Ops Field Validation v0.1."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TEMPLATE = (
    ROOT
    / "docs"
    / "kaigo-ops"
    / "research"
    / "issues"
    / "information-search"
    / "field-validation-adjudication-template-v0.1.csv"
)

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

BLINDED_COPY_FIELDS = (
    "attempt_id",
    "question_id",
    "question_slug",
    "answer_text",
    "source_url",
    "source_locator",
)


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def required(value: str | None, field: str, attempt_id: str) -> str:
    cleaned = (value or "").strip()
    if not cleaned:
        raise ValueError(f"{attempt_id}: missing {field}")
    return cleaned


def build_blinded_rows(
    run_headers: list[str],
    run_rows: list[dict[str, str]],
    template_headers: list[str],
    template_rows: list[dict[str, str]],
) -> list[dict[str, str]]:
    if run_headers != RUN_HEADERS:
        raise ValueError("run CSV headers do not match the frozen v0.1 schema")
    if template_headers != ADJUDICATION_HEADERS:
        raise ValueError("adjudication template headers do not match the frozen v0.1 schema")
    if len(run_rows) != len(template_rows):
        raise ValueError(
            f"row count mismatch: run={len(run_rows)} template={len(template_rows)}"
        )

    output: list[dict[str, str]] = []

    for run, template in zip(run_rows, template_rows, strict=True):
        attempt_id = required(run.get("attempt_id"), "attempt_id", "<unknown>")
        expected_attempt = required(
            template.get("attempt_id"), "attempt_id", "<template>"
        )
        if attempt_id != expected_attempt:
            raise ValueError(
                f"attempt order/id mismatch: run={attempt_id} template={expected_attempt}"
            )

        for field in ("question_id", "question_slug"):
            actual = required(run.get(field), field, attempt_id)
            expected = required(template.get(field), field, expected_attempt)
            if actual != expected:
                raise ValueError(
                    f"{attempt_id}: {field} mismatch ({actual!r} != {expected!r})"
                )

        required(run.get("answer_text"), "answer_text", attempt_id)

        row = {header: "" for header in ADJUDICATION_HEADERS}
        for field in BLINDED_COPY_FIELDS:
            row[field] = (run.get(field) or "").strip()

        output.append(row)

    return output


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=ADJUDICATION_HEADERS)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--template", type=Path, default=DEFAULT_TEMPLATE)
    args = parser.parse_args()

    run_headers, run_rows = read_csv(args.run)
    template_headers, template_rows = read_csv(args.template)
    blinded_rows = build_blinded_rows(
        run_headers,
        run_rows,
        template_headers,
        template_rows,
    )
    write_csv(args.output, blinded_rows)

    print(
        "Kaigo Ops Field Validation v0.1: blinded adjudication CSV created "
        f"({len(blinded_rows)} attempts; no condition/time/click/confidence columns)"
    )


if __name__ == "__main__":
    main()
