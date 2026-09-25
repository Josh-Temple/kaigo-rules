#!/usr/bin/env python3
"""Fail-closed production gate for Kaigo Ops Field Validation v0.1."""

from __future__ import annotations

import argparse
import html
import json
import time
import urllib.error
import urllib.parse
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PILOT = ROOT / "docs" / "kaigo-ops" / "research" / "issues" / "information-search" / "field-validation-v0.1.json"

OFFICIAL_HOST_SUFFIXES = (
    "mhlw.go.jp",
    "e-gov.go.jp",
)


class LinkCollector(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.hrefs: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag != "a":
            return
        for key, value in attrs:
            if key == "href" and value:
                self.hrefs.append(value)


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def fetch_text(url: str, timeout_sec: float) -> tuple[int, str]:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "kaigo-rules-field-validation-gate/0.1",
            "Cache-Control": "no-cache",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout_sec) as response:
            status = response.status
            body = response.read().decode("utf-8", errors="replace")
            return status, body
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        return exc.code, body


def is_official_href(href: str) -> bool:
    parsed = urllib.parse.urlparse(html.unescape(href))
    host = (parsed.hostname or "").lower()
    return any(host == suffix or host.endswith("." + suffix) for suffix in OFFICIAL_HOST_SUFFIXES)


def wait_for_expected_version(
    base_url: str,
    expected_sha: str,
    wait_seconds: int,
    interval_seconds: int,
    timeout_sec: float,
) -> dict[str, object]:
    deadline = time.monotonic() + wait_seconds
    last_problem = "version endpoint was not checked"

    while True:
        status, body = fetch_text(f"{base_url}/api/version", timeout_sec)
        if status == 200:
            try:
                payload = json.loads(body)
            except json.JSONDecodeError as exc:
                last_problem = f"/api/version returned invalid JSON: {exc}"
            else:
                actual_sha = payload.get("commit_sha")
                if payload.get("service") != "kaigo-rules":
                    last_problem = f"unexpected service marker: {payload.get('service')!r}"
                elif actual_sha == expected_sha:
                    return payload
                else:
                    last_problem = f"production SHA is {actual_sha!r}, expected {expected_sha!r}"
        else:
            last_problem = f"/api/version returned HTTP {status}"

        if time.monotonic() >= deadline:
            raise SystemExit(f"production gate failed: {last_problem}")
        time.sleep(interval_seconds)


def verify_routes(base_url: str, timeout_sec: float) -> tuple[int, int]:
    pilot = load_json(PILOT)
    errors: list[str] = []

    status, search_body = fetch_text(f"{base_url}/search", timeout_sec)
    if status != 200:
        errors.append(f"/search returned HTTP {status}")
    elif "検索" not in search_body:
        errors.append("/search did not contain the expected search UI marker")

    checked = 0
    for row in pilot.get("questions", []):
        slug = row["slug"]
        title = row["snapshot_title"]
        route = f"/questions/{slug}"
        status, body = fetch_text(f"{base_url}{route}", timeout_sec)
        if status != 200:
            errors.append(f"{route} returned HTTP {status}")
            continue

        checked += 1
        if title not in body:
            errors.append(f"{route} is missing frozen title {title!r}")
        if "FAQ根拠対応を確認済み" not in body:
            errors.append(f"{route} is missing the verified FAQ evidence label")

        parser = LinkCollector()
        parser.feed(body)
        if not any(is_official_href(href) for href in parser.hrefs):
            errors.append(f"{route} has no MHLW/e-Gov outgoing evidence link")

    if errors:
        raise SystemExit("production route verification failed:\n" + "\n".join(errors))

    return checked, len(pilot.get("questions", []))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="https://kaigo-rules.vercel.app")
    parser.add_argument("--expected-sha", required=True)
    parser.add_argument("--wait-seconds", type=int, default=0)
    parser.add_argument("--interval-seconds", type=int, default=15)
    parser.add_argument("--timeout-seconds", type=float, default=20.0)
    args = parser.parse_args()

    base_url = args.base_url.rstrip("/")
    expected_sha = args.expected_sha.strip()
    if len(expected_sha) != 40:
        raise SystemExit("--expected-sha must be a full 40-character Git SHA")

    version = wait_for_expected_version(
        base_url,
        expected_sha,
        max(args.wait_seconds, 0),
        max(args.interval_seconds, 1),
        args.timeout_seconds,
    )
    checked, total = verify_routes(base_url, args.timeout_seconds)

    print(
        "Kaigo Ops production gate: PASS "
        f"(sha={version.get('commit_sha')} / routes={checked}/{total} / base={base_url})"
    )


if __name__ == "__main__":
    main()
