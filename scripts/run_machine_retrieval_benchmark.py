#!/usr/bin/env python3
"""Run Kaigo Ops Machine Retrieval Benchmark v0.1 against a deployed site."""

from __future__ import annotations

import argparse
import html
import json
import urllib.error
import urllib.parse
import urllib.request
from collections import defaultdict
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BENCHMARK = ROOT / "docs" / "kaigo-ops" / "research" / "issues" / "information-search" / "machine-retrieval-benchmark-v0.1.json"


class LinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.hrefs: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag != "a":
            return
        for key, value in attrs:
            if key == "href" and value:
                self.hrefs.append(html.unescape(value))


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def fetch(url: str, timeout: float) -> tuple[int, str]:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "kaigo-rules-machine-retrieval-benchmark/0.1",
            "Cache-Control": "no-cache",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.status, response.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read().decode("utf-8", errors="replace")


def question_link_order(body: str) -> list[str]:
    parser = LinkParser()
    parser.feed(body)
    seen: set[str] = set()
    slugs: list[str] = []
    for href in parser.hrefs:
        parsed = urllib.parse.urlparse(href)
        path = parsed.path
        if not path.startswith("/questions/"):
            continue
        slug = path.removeprefix("/questions/").strip("/")
        if slug and slug not in seen:
            seen.add(slug)
            slugs.append(slug)
    return slugs


def check_context(
    base_url: str,
    service_id: str,
    slug: str,
    expected_sources: list[str],
    timeout: float,
) -> dict[str, Any]:
    url = f"{base_url}/api/context/services/{urllib.parse.quote(service_id)}/questions/{urllib.parse.quote(slug)}"
    status, body = fetch(url, timeout)
    result: dict[str, Any] = {
        "status": status,
        "slug_match": False,
        "short_answer_present": False,
        "verified_question": False,
        "expected_sources_present": False,
        "actual_source_ids": [],
        "errors": [],
    }
    if status != 200:
        result["errors"].append(f"context HTTP {status}")
        result["integrity_ok"] = False
        return result

    try:
        payload = json.loads(body)
    except json.JSONDecodeError as exc:
        result["errors"].append(f"context invalid JSON: {exc}")
        result["integrity_ok"] = False
        return result

    package = payload.get("package") or {}
    question = package.get("question") or {}
    answer = package.get("answer") or {}
    assurance = package.get("assurance") or {}
    sources = ((package.get("evidence") or {}).get("sources") or [])

    actual_sources = sorted(
        {
            row.get("source_id")
            for row in sources
            if isinstance(row, dict) and row.get("source_id")
        }
    )
    result["actual_source_ids"] = actual_sources
    result["slug_match"] = question.get("slug") == slug
    result["short_answer_present"] = bool(str(answer.get("short_answer") or "").strip())
    result["verified_question"] = assurance.get("question_content_status") == "verified"
    result["expected_sources_present"] = set(expected_sources).issubset(actual_sources)

    if not result["slug_match"]:
        result["errors"].append("context slug mismatch")
    if not result["short_answer_present"]:
        result["errors"].append("context short_answer missing")
    if not result["verified_question"]:
        result["errors"].append("context question status is not verified")
    if not result["expected_sources_present"]:
        missing = sorted(set(expected_sources) - set(actual_sources))
        result["errors"].append(f"context expected sources missing: {missing}")

    result["integrity_ok"] = not result["errors"]
    return result


def run(benchmark: dict[str, Any], base_url: str, timeout: float) -> dict[str, Any]:
    base_url = base_url.rstrip("/")
    context_cache: dict[str, dict[str, Any]] = {}
    case_results: list[dict[str, Any]] = []

    for case in benchmark["cases"]:
        slug = case["expected_question_slug"]
        query = case["query"]
        search_url = f"{base_url}/search?{urllib.parse.urlencode({'q': query})}"
        status, body = fetch(search_url, timeout)
        links = question_link_order(body) if status == 200 else []
        rank = links.index(slug) + 1 if slug in links else None

        if slug not in context_cache:
            context_cache[slug] = check_context(
                base_url,
                benchmark["service_id"],
                slug,
                case["expected_source_ids"],
                timeout,
            )

        context = context_cache[slug]
        search_hit = rank is not None
        case_results.append(
            {
                "id": case["id"],
                "field_validation_id": case["field_validation_id"],
                "query": query,
                "expected_question_slug": slug,
                "search_http_status": status,
                "search_hit": search_hit,
                "search_rank": rank,
                "top3_hit": bool(rank is not None and rank <= 3),
                "context_integrity_ok": bool(context["integrity_ok"]),
                "full_pass": bool(search_hit and context["integrity_ok"]),
            }
        )

    total = len(case_results)
    by_question: dict[str, dict[str, Any]] = {}
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in case_results:
        grouped[row["field_validation_id"]].append(row)
    for field_id, rows in grouped.items():
        by_question[field_id] = {
            "cases": len(rows),
            "search_hits": sum(1 for row in rows if row["search_hit"]),
            "top3_hits": sum(1 for row in rows if row["top3_hit"]),
            "full_passes": sum(1 for row in rows if row["full_pass"]),
        }

    context_ok_questions = sum(
        1 for value in context_cache.values() if value["integrity_ok"]
    )

    return {
        "benchmark_id": benchmark["benchmark_id"],
        "base_url": base_url,
        "case_count": total,
        "question_count": len(context_cache),
        "interpretation": benchmark["evaluation"]["interpretation"],
        "metrics": {
            "search_hit_rate": sum(1 for row in case_results if row["search_hit"]) / total,
            "top3_hit_rate": sum(1 for row in case_results if row["top3_hit"]) / total,
            "context_integrity_rate": context_ok_questions / len(context_cache),
            "full_pass_rate": sum(1 for row in case_results if row["full_pass"]) / total,
        },
        "by_question": by_question,
        "context_results": context_cache,
        "cases": case_results,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--benchmark", type=Path, default=DEFAULT_BENCHMARK)
    parser.add_argument("--base-url", default="https://kaigo-rules.vercel.app")
    parser.add_argument("--timeout-seconds", type=float, default=20.0)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    report = run(load_json(args.benchmark), args.base_url, args.timeout_seconds)
    rendered = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")


if __name__ == "__main__":
    main()
