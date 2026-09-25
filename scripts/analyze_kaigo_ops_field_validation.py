#!/usr/bin/env python3
"""Validate and summarize measured Kaigo Ops Field Validation v0.1 data."""

from __future__ import annotations

import argparse
import csv
import json
import re
import statistics
from collections import defaultdict
from pathlib import Path
from typing import Any

SHA_RE = re.compile(r"(?:^|\s)production_sha=([0-9a-f]{40})(?:\s|$)")
BOOL_FIELDS = (
    "authoritative_source_reached",
    "answer_correct",
    "conditions_preserved",
    "source_correct",
)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def required_text(row: dict[str, str], field: str, attempt_id: str) -> str:
    value = (row.get(field) or "").strip()
    if not value:
        raise ValueError(f"{attempt_id}: missing {field}")
    return value


def parse_float(
    row: dict[str, str],
    field: str,
    attempt_id: str,
    *,
    allow_blank: bool = False,
    minimum: float = 0.0,
    maximum: float | None = None,
) -> float | None:
    raw = (row.get(field) or "").strip()
    if not raw and allow_blank:
        return None
    if not raw:
        raise ValueError(f"{attempt_id}: missing {field}")
    try:
        value = float(raw)
    except ValueError as exc:
        raise ValueError(f"{attempt_id}: {field} is not numeric: {raw!r}") from exc
    if value < minimum:
        raise ValueError(f"{attempt_id}: {field} must be >= {minimum}")
    if maximum is not None and value > maximum:
        raise ValueError(f"{attempt_id}: {field} must be <= {maximum}")
    return value


def parse_int(
    row: dict[str, str],
    field: str,
    attempt_id: str,
    *,
    minimum: int = 0,
    maximum: int | None = None,
) -> int:
    raw = required_text(row, field, attempt_id)
    try:
        value = int(raw)
    except ValueError as exc:
        raise ValueError(f"{attempt_id}: {field} is not an integer: {raw!r}") from exc
    if value < minimum:
        raise ValueError(f"{attempt_id}: {field} must be >= {minimum}")
    if maximum is not None and value > maximum:
        raise ValueError(f"{attempt_id}: {field} must be <= {maximum}")
    return value


def parse_bool(row: dict[str, str], field: str, attempt_id: str) -> bool:
    raw = required_text(row, field, attempt_id).upper()
    if raw == "TRUE":
        return True
    if raw == "FALSE":
        return False
    raise ValueError(f"{attempt_id}: {field} must be TRUE or FALSE")


def med(values: list[float]) -> float | None:
    return float(statistics.median(values)) if values else None


def rate(values: list[bool]) -> float | None:
    return sum(values) / len(values) if values else None


def fmt_num(value: float | None, digits: int = 1) -> str:
    return "NA" if value is None else f"{value:.{digits}f}"


def fmt_rate(value: float | None) -> str:
    return "NA" if value is None else f"{100 * value:.1f}%"


def prepare_records(
    run_rows: list[dict[str, str]],
    adjudication_rows: list[dict[str, str]],
    pilot: dict[str, Any],
) -> tuple[list[dict[str, Any]], str]:
    questions = {row["id"]: row for row in pilot.get("questions", [])}
    if not questions:
        raise ValueError("pilot has no questions")

    run_by_id: dict[str, dict[str, str]] = {}
    for row in run_rows:
        attempt_id = required_text(row, "attempt_id", "<unknown>")
        if attempt_id in run_by_id:
            raise ValueError(f"duplicate run attempt_id: {attempt_id}")
        run_by_id[attempt_id] = row

    adj_by_id: dict[str, dict[str, str]] = {}
    for row in adjudication_rows:
        attempt_id = required_text(row, "attempt_id", "<unknown>")
        if attempt_id in adj_by_id:
            raise ValueError(f"duplicate adjudication attempt_id: {attempt_id}")
        adj_by_id[attempt_id] = row

    if set(run_by_id) != set(adj_by_id):
        missing_adj = sorted(set(run_by_id) - set(adj_by_id))
        missing_run = sorted(set(adj_by_id) - set(run_by_id))
        raise ValueError(
            f"attempt mismatch: missing_adjudication={missing_adj} missing_run={missing_run}"
        )

    records: list[dict[str, Any]] = []
    production_shas: set[str] = set()
    condition_counts = defaultdict(int)
    question_condition_counts: dict[str, dict[str, int]] = defaultdict(
        lambda: defaultdict(int)
    )

    for attempt_id in sorted(run_by_id):
        run = run_by_id[attempt_id]
        adj = adj_by_id[attempt_id]

        question_id = required_text(run, "question_id", attempt_id)
        slug = required_text(run, "question_slug", attempt_id)
        condition = required_text(run, "condition", attempt_id)
        if condition not in {"A", "B"}:
            raise ValueError(f"{attempt_id}: condition must be A or B")

        question = questions.get(question_id)
        if not question:
            raise ValueError(f"{attempt_id}: unknown question_id {question_id}")
        if slug != question.get("slug"):
            raise ValueError(f"{attempt_id}: question_slug does not match pilot")

        if required_text(adj, "question_id", attempt_id) != question_id:
            raise ValueError(f"{attempt_id}: adjudication question_id mismatch")
        if required_text(adj, "question_slug", attempt_id) != slug:
            raise ValueError(f"{attempt_id}: adjudication question_slug mismatch")

        answer_text = required_text(run, "answer_text", attempt_id)
        source_url = (run.get("source_url") or "").strip()
        source_locator = (run.get("source_locator") or "").strip()

        for copied_field, expected in (
            ("answer_text", answer_text),
            ("source_url", source_url),
            ("source_locator", source_locator),
        ):
            actual = (adj.get(copied_field) or "").strip()
            if actual != expected:
                raise ValueError(
                    f"{attempt_id}: adjudication {copied_field} does not match raw data"
                )

        first_source_sec = parse_float(
            run,
            "time_to_first_authoritative_source_sec",
            attempt_id,
            allow_blank=True,
            maximum=600.0,
        )
        submission_sec = parse_float(
            run,
            "time_to_answer_submission_sec",
            attempt_id,
            maximum=600.0,
        )
        assert submission_sec is not None
        if first_source_sec is not None and first_source_sec > submission_sec:
            raise ValueError(f"{attempt_id}: first source time exceeds submission time")

        clicks = parse_int(run, "clicks", attempt_id)
        reformulations = parse_int(run, "query_reformulations", attempt_id)
        confidence = parse_int(run, "confidence_1_5", attempt_id, minimum=1, maximum=5)

        notes = required_text(run, "observer_notes", attempt_id)
        sha_match = SHA_RE.search(notes)
        if not sha_match:
            raise ValueError(f"{attempt_id}: observer_notes missing production_sha=<40 sha>")
        production_shas.add(sha_match.group(1))

        judged = {field: parse_bool(adj, field, attempt_id) for field in BOOL_FIELDS}
        if judged["source_correct"] and not judged["authoritative_source_reached"]:
            raise ValueError(
                f"{attempt_id}: source_correct=TRUE requires authoritative_source_reached=TRUE"
            )
        if judged["authoritative_source_reached"]:
            if not source_url or not source_locator:
                raise ValueError(
                    f"{attempt_id}: authoritative source reached but source URL/locator is blank"
                )
            if first_source_sec is None:
                raise ValueError(
                    f"{attempt_id}: authoritative source reached but first-source time is blank"
                )

        correction_sec = parse_float(
            adj,
            "human_correction_sec",
            attempt_id,
            maximum=600.0,
        )
        assert correction_sec is not None
        adjudicator_id = required_text(adj, "adjudicator_id", attempt_id)

        condition_counts[condition] += 1
        question_condition_counts[question_id][condition] += 1

        records.append(
            {
                "attempt_id": attempt_id,
                "participant_id": required_text(run, "participant_id", attempt_id),
                "question_id": question_id,
                "question_slug": slug,
                "condition": condition,
                "complexity": question.get("complexity"),
                "first_source_sec": first_source_sec,
                "submission_sec": submission_sec,
                "clicks": clicks,
                "reformulations": reformulations,
                "confidence": confidence,
                "correction_sec": correction_sec,
                "adjudicator_id": adjudicator_id,
                **judged,
            }
        )

    if len(production_shas) != 1:
        raise ValueError(f"expected one production SHA across attempts, found {sorted(production_shas)}")
    if condition_counts["A"] != condition_counts["B"]:
        raise ValueError(f"unbalanced A/B attempts: {dict(condition_counts)}")
    for question_id, counts in question_condition_counts.items():
        if counts["A"] != counts["B"]:
            raise ValueError(
                f"{question_id}: expected equal A/B observations, found {dict(counts)}"
            )

    return records, next(iter(production_shas))


def group_summary(records: list[dict[str, Any]]) -> dict[str, Any]:
    reached_records = [r for r in records if r["authoritative_source_reached"]]
    return {
        "n": len(records),
        "authoritative_source_reach_rate": rate(
            [r["authoritative_source_reached"] for r in records]
        ),
        "answer_correct_rate": rate([r["answer_correct"] for r in records]),
        "conditions_preserved_rate": rate([r["conditions_preserved"] for r in records]),
        "source_correct_rate": rate([r["source_correct"] for r in records]),
        "median_first_source_sec_among_reached": med(
            [
                float(r["first_source_sec"])
                for r in reached_records
                if r["first_source_sec"] is not None
            ]
        ),
        "median_submission_sec": med([float(r["submission_sec"]) for r in records]),
        "median_clicks": med([float(r["clicks"]) for r in records]),
        "median_query_reformulations": med(
            [float(r["reformulations"]) for r in records]
        ),
        "median_confidence": med([float(r["confidence"]) for r in records]),
        "median_human_correction_sec": med(
            [float(r["correction_sec"]) for r in records]
        ),
    }


def build_report(
    run_rows: list[dict[str, str]],
    adjudication_rows: list[dict[str, str]],
    pilot: dict[str, Any],
) -> dict[str, Any]:
    records, production_sha = prepare_records(run_rows, adjudication_rows, pilot)

    by_condition = {
        condition: group_summary([r for r in records if r["condition"] == condition])
        for condition in ("A", "B")
    }

    complexities = sorted({r["complexity"] for r in records if r["complexity"]})
    by_complexity: dict[str, Any] = {}
    for complexity in complexities:
        by_complexity[complexity] = {
            condition: group_summary(
                [
                    r
                    for r in records
                    if r["complexity"] == complexity and r["condition"] == condition
                ]
            )
            for condition in ("A", "B")
        }

    question_rows = []
    for question in pilot.get("questions", []):
        question_records = [r for r in records if r["question_id"] == question["id"]]
        summaries = {
            condition: group_summary(
                [r for r in question_records if r["condition"] == condition]
            )
            for condition in ("A", "B")
        }
        a_time = summaries["A"]["median_first_source_sec_among_reached"]
        b_time = summaries["B"]["median_first_source_sec_among_reached"]
        question_rows.append(
            {
                "question_id": question["id"],
                "slug": question["slug"],
                "complexity": question.get("complexity"),
                "A": summaries["A"],
                "B": summaries["B"],
                "first_source_median_delta_B_minus_A_sec": (
                    None if a_time is None or b_time is None else b_time - a_time
                ),
            }
        )

    a_first = by_condition["A"]["median_first_source_sec_among_reached"]
    b_first = by_condition["B"]["median_first_source_sec_among_reached"]
    a_submit = by_condition["A"]["median_submission_sec"]
    b_submit = by_condition["B"]["median_submission_sec"]

    return {
        "pilot_id": pilot.get("pilot_id"),
        "production_sha": production_sha,
        "attempt_count": len(records),
        "result_interpretation": (
            "Descriptive statistics only. Do not treat median differences as a causal "
            "effect or an automated success verdict."
        ),
        "by_condition": by_condition,
        "descriptive_differences_B_minus_A": {
            "median_first_source_sec_among_reached": (
                None if a_first is None or b_first is None else b_first - a_first
            ),
            "median_submission_sec": (
                None if a_submit is None or b_submit is None else b_submit - a_submit
            ),
            "authoritative_source_reach_rate": (
                by_condition["B"]["authoritative_source_reach_rate"]
                - by_condition["A"]["authoritative_source_reach_rate"]
            ),
            "conditions_preserved_rate": (
                by_condition["B"]["conditions_preserved_rate"]
                - by_condition["A"]["conditions_preserved_rate"]
            ),
            "source_correct_rate": (
                by_condition["B"]["source_correct_rate"]
                - by_condition["A"]["source_correct_rate"]
            ),
            "median_human_correction_sec": (
                by_condition["B"]["median_human_correction_sec"]
                - by_condition["A"]["median_human_correction_sec"]
            ),
        },
        "by_complexity": by_complexity,
        "by_question": question_rows,
    }


def markdown_report(report: dict[str, Any]) -> str:
    lines = [
        "# Kaigo Ops Field Validation v0.1 — descriptive summary",
        "",
        f"- production SHA: \`{report['production_sha']}\`",
        f"- attempts: {report['attempt_count']}",
        "- interpretation: descriptive only; no automated success verdict",
        "",
        "## Condition summary",
        "",
        "| Metric | A | B |",
        "| --- | ---: | ---: |",
    ]

    a = report["by_condition"]["A"]
    b = report["by_condition"]["B"]
    metrics = [
        ("n", str(a["n"]), str(b["n"])),
        (
            "authoritative source reach rate",
            fmt_rate(a["authoritative_source_reach_rate"]),
            fmt_rate(b["authoritative_source_reach_rate"]),
        ),
        (
            "median first source sec among reached",
            fmt_num(a["median_first_source_sec_among_reached"]),
            fmt_num(b["median_first_source_sec_among_reached"]),
        ),
        (
            "median answer submission sec",
            fmt_num(a["median_submission_sec"]),
            fmt_num(b["median_submission_sec"]),
        ),
        ("answer correct rate", fmt_rate(a["answer_correct_rate"]), fmt_rate(b["answer_correct_rate"])),
        (
            "conditions preserved rate",
            fmt_rate(a["conditions_preserved_rate"]),
            fmt_rate(b["conditions_preserved_rate"]),
        ),
        ("source correct rate", fmt_rate(a["source_correct_rate"]), fmt_rate(b["source_correct_rate"])),
        (
            "median human correction sec",
            fmt_num(a["median_human_correction_sec"]),
            fmt_num(b["median_human_correction_sec"]),
        ),
        ("median clicks", fmt_num(a["median_clicks"]), fmt_num(b["median_clicks"])),
        (
            "median query reformulations",
            fmt_num(a["median_query_reformulations"]),
            fmt_num(b["median_query_reformulations"]),
        ),
        ("median confidence", fmt_num(a["median_confidence"]), fmt_num(b["median_confidence"])),
    ]
    for label, av, bv in metrics:
        lines.append(f"| {label} | {av} | {bv} |")

    lines.extend(
        [
            "",
            "## Descriptive differences (B - A)",
            "",
            "Negative time differences mean B was faster in this sample. "
            "Percentage-point differences are descriptive only.",
            "",
        ]
    )
    for key, value in report["descriptive_differences_B_minus_A"].items():
        if key.endswith("_rate"):
            rendered = "NA" if value is None else f"{100 * value:+.1f} pp"
        else:
            rendered = "NA" if value is None else f"{value:+.1f}"
        lines.append(f"- {key}: {rendered}")

    lines.extend(["", "## By question", "", "| ID | Complexity | A reach | B reach | B-A first-source median sec |", "| --- | --- | ---: | ---: | ---: |"])
    for row in report["by_question"]:
        lines.append(
            "| {id} | {complexity} | {ar} | {br} | {delta} |".format(
                id=row["question_id"],
                complexity=row["complexity"],
                ar=fmt_rate(row["A"]["authoritative_source_reach_rate"]),
                br=fmt_rate(row["B"]["authoritative_source_reach_rate"]),
                delta=fmt_num(row["first_source_median_delta_B_minus_A_sec"]),
            )
        )
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", type=Path, required=True)
    parser.add_argument("--adjudication", type=Path, required=True)
    parser.add_argument(
        "--pilot",
        type=Path,
        default=Path(
            "docs/kaigo-ops/research/issues/information-search/field-validation-v0.1.json"
        ),
    )
    parser.add_argument("--format", choices=("json", "markdown"), default="markdown")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    report = build_report(read_csv(args.run), read_csv(args.adjudication), read_json(args.pilot))
    rendered = (
        json.dumps(report, ensure_ascii=False, indent=2) + "\n"
        if args.format == "json"
        else markdown_report(report)
    )

    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")


if __name__ == "__main__":
    main()
