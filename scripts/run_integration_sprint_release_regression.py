#!/usr/bin/env python3
"""Run the Integration Sprint black-box release regression gate."""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_FIXTURE = ROOT / "data" / "integration-sprint-release-regression-v0.1.json"
SHA_RE = re.compile(r"^[0-9a-f]{40}$")


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.text_parts: list[str] = []
        self.hrefs: list[str] = []

    def handle_data(self, data: str) -> None:
        if data.strip():
            self.text_parts.append(data)

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag != "a":
            return
        for key, value in attrs:
            if key == "href" and value:
                self.hrefs.append(html.unescape(value))


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def normalize_text(value: str) -> str:
    return re.sub(
        r"\s+",
        " ",
        unicodedata.normalize("NFKC", html.unescape(value)),
    ).strip()


def page_snapshot(body: str) -> tuple[str, list[str]]:
    parser = PageParser()
    parser.feed(body)
    return normalize_text(" ".join(parser.text_parts)), parser.hrefs


def resolve_url(base_url: str, path: str) -> str:
    parsed = urllib.parse.urlsplit(path)
    encoded_path = urllib.parse.quote(parsed.path, safe="/:@")
    query = urllib.parse.urlencode(
        urllib.parse.parse_qsl(parsed.query, keep_blank_values=True),
        doseq=True,
    )
    relative = urllib.parse.urlunsplit(("", "", encoded_path, query, ""))
    return urllib.parse.urljoin(base_url.rstrip("/") + "/", relative.lstrip("/"))


def fetch(url: str, timeout: float) -> tuple[int, str]:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "kaigo-rules-integration-release-regression/0.1",
            "Cache-Control": "no-cache",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.status, response.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read().decode("utf-8", errors="replace")


def get_deployment_version(base_url: str, timeout: float) -> dict[str, Any]:
    status, body = fetch(resolve_url(base_url, "/api/version"), timeout)
    if status != 200:
        raise RuntimeError(f"/api/version returned HTTP {status}")
    try:
        payload = json.loads(body)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"/api/version returned invalid JSON: {exc}") from exc
    commit_sha = str(payload.get("commit_sha") or "").strip()
    if not SHA_RE.fullmatch(commit_sha):
        raise RuntimeError(f"/api/version returned invalid commit_sha: {commit_sha!r}")
    return payload


def require_expected_sha(actual_sha: str, expected_sha: str) -> None:
    if not SHA_RE.fullmatch(expected_sha):
        raise ValueError("--expected-sha must be a full 40-character lowercase Git SHA")
    if actual_sha != expected_sha:
        raise RuntimeError(
            f"deployment SHA mismatch: expected {expected_sha}, got {actual_sha}"
        )


def validate_fixture(fixture: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if fixture.get("format_version") != 1:
        errors.append("unsupported format_version")

    required_coverage = set(fixture.get("required_coverage") or [])
    expected_coverage = {
        "service_isolation",
        "verification_wording",
        "scoped_counts",
        "faq_to_authority_expansion",
        "notice_retrieval",
    }
    if required_coverage != expected_coverage:
        errors.append("required_coverage does not match Integration Sprint D4 contract")

    contract = fixture.get("run_contract") or {}
    if contract.get("exact_deployment_sha_required") is not True:
        errors.append("exact deployment SHA gate must remain enabled")
    if contract.get("human_effectiveness_claims_supported") is not False:
        errors.append("release regression must not claim human effectiveness")

    cases = fixture.get("cases") or []
    ids = [case.get("id") for case in cases]
    if not cases:
        errors.append("no regression cases")
    if len(set(ids)) != len(ids):
        errors.append("duplicate regression case id")

    covered = {case.get("coverage") for case in cases}
    if not expected_coverage.issubset(covered):
        errors.append("one or more required coverage areas have no case")

    for case in cases:
        case_id = case.get("id") or "<missing-id>"
        if not str(case.get("path") or "").startswith("/"):
            errors.append(f"{case_id}: path must start with /")
        status = case.get("expect_status")
        if not isinstance(status, int) or status < 100 or status > 599:
            errors.append(f"{case_id}: invalid expect_status")
        for field in ("contains_text", "regex_text", "href_contains", "not_contains_text"):
            values = case.get(field, [])
            if not isinstance(values, list) or any(
                not isinstance(value, str) or not value for value in values
            ):
                errors.append(f"{case_id}: invalid {field}")

    return errors


def evaluate_case(case: dict[str, Any], status: int, body: str) -> dict[str, Any]:
    text, hrefs = page_snapshot(body)
    errors: list[str] = []

    if status != case["expect_status"]:
        errors.append(
            f"HTTP status mismatch: expected {case['expect_status']}, got {status}"
        )

    for expected in case.get("contains_text", []):
        if normalize_text(expected) not in text:
            errors.append(f"missing text: {expected}")

    for forbidden in case.get("not_contains_text", []):
        if normalize_text(forbidden) in text:
            errors.append(f"forbidden text present: {forbidden}")

    for pattern in case.get("regex_text", []):
        if not re.search(pattern, text):
            errors.append(f"text regex did not match: {pattern}")

    for expected in case.get("href_contains", []):
        if not any(expected in href for href in hrefs):
            errors.append(f"missing href containing: {expected}")

    return {
        "id": case["id"],
        "coverage": case["coverage"],
        "title": case["title"],
        "path": case["path"],
        "expected_status": case["expect_status"],
        "actual_status": status,
        "passed": not errors,
        "errors": errors,
    }


def run(
    fixture: dict[str, Any],
    base_url: str,
    expected_sha: str,
    timeout: float,
) -> dict[str, Any]:
    fixture_errors = validate_fixture(fixture)
    if fixture_errors:
        raise RuntimeError("invalid release-regression fixture: " + "; ".join(fixture_errors))

    deployment = get_deployment_version(base_url, timeout)
    require_expected_sha(deployment["commit_sha"], expected_sha)

    results = []
    for case in fixture["cases"]:
        url = resolve_url(base_url, case["path"])
        status, body = fetch(url, timeout)
        results.append(evaluate_case(case, status, body))

    failed = [row["id"] for row in results if not row["passed"]]
    return {
        "gate_id": fixture["gate_id"],
        "service_id": fixture["service_id"],
        "base_url": base_url.rstrip("/"),
        "deployment_version": deployment,
        "case_count": len(results),
        "passed_count": len(results) - len(failed),
        "failed_count": len(failed),
        "gate_result": "PASS" if not failed else "FAIL",
        "failed_case_ids": failed,
        "coverage": sorted({row["coverage"] for row in results}),
        "human_effectiveness": {
            "status": "NOT_EVALUATED",
            "claims_supported": [],
        },
        "cases": results,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixture", type=Path, default=DEFAULT_FIXTURE)
    parser.add_argument("--base-url", default="https://kaigo-rules.vercel.app")
    parser.add_argument("--expected-sha", required=True)
    parser.add_argument("--timeout-seconds", type=float, default=20.0)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    report = run(
        load_json(args.fixture),
        args.base_url,
        args.expected_sha,
        args.timeout_seconds,
    )
    rendered = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")

    if report["gate_result"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
