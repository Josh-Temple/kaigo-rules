#!/usr/bin/env python3
"""Fail-closed proof that a Kaigo Ops deploy hook reached the production alias.

A hook acknowledgement is not a deployment. The gate requires a new production
deployment for the exact Git SHA in the expected Vercel project, READY state,
the live alias pointing to that deployment, and successful public route checks.
No credential or raw API response is written to logs.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import time
import urllib.error
import urllib.parse
import urllib.request

TEAM_ID = "team_imvRFeaSa1LmNpMJkFiMwNmB"
PROJECT_ID = "prj_7kKmZkto1j9r9Z3otwccx05LAjTp"
ALIAS = "ops-site-pi.vercel.app"
EXPECTED_REPO = "kaigo-rules"
EXPECTED_ORG = "Josh-Temple"
ROUTES = (
    "/",
    "/issues/information-search",
    "/issues/documentation",
    "/issues/training-handover",
    "/issues/communication",
    "/issues/work-time",
    "/tools/information-inventory",
    "/tools/documentation-review",
    "/tools/training-handover-inventory",
    "/tools/communication-review",
    "/tools/work-time-review",
)
API_BASE = "https://api.vercel.com"


class VerificationError(Exception):
    """Safe-to-log verification failure, excluding secrets and response bodies."""


def api_json(path: str, token: str, *, timeout: float = 20) -> dict:
    url = API_BASE + path
    request = urllib.request.Request(
        url, headers={"Authorization": "Bearer " + token, "Accept": "application/json"}
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            payload = json.load(response)
    except urllib.error.HTTPError as exc:
        raise VerificationError(f"Vercel API returned HTTP {exc.code} for {path.split('?')[0]}") from None
    except (urllib.error.URLError, TimeoutError, ValueError, OSError) as exc:
        # Do not include exception detail: urllib errors may contain request URLs.
        raise VerificationError(f"Vercel API request failed for {path.split('?')[0]}") from None
    if not isinstance(payload, dict):
        raise VerificationError("Vercel API returned an invalid response shape")
    return payload


def route_ok(path: str, *, timeout: float = 20) -> None:
    url = "https://" + ALIAS + path
    request = urllib.request.Request(
        url, headers={"User-Agent": "kaigo-ops-production-verifier/1.0",
                      "Cache-Control": "no-cache"}
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            status = response.status
            content_type = response.headers.get("Content-Type", "")
            body = response.read(1_000_000).decode("utf-8", errors="replace")
    except urllib.error.HTTPError as exc:
        raise VerificationError(f"production route {path} returned HTTP {exc.code}") from None
    except (urllib.error.URLError, TimeoutError, OSError):
        raise VerificationError(f"production route {path} was unreachable") from None
    if status != 200 or "text/html" not in content_type.lower():
        raise VerificationError(f"production route {path} was not HTML HTTP 200")
    if "<html" not in body.lower() or "介護" not in body:
        raise VerificationError(f"production route {path} did not contain the expected site shell")


def matching_deployment(rows: list, expected_sha: str, started_at_ms: int) -> dict | None:
    matches = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        meta = row.get("meta") or {}
        if not isinstance(meta, dict):
            continue
        if (meta.get("githubCommitSha") != expected_sha
                or meta.get("githubRepo") != EXPECTED_REPO
                or meta.get("githubOrg") != EXPECTED_ORG
                or row.get("target") != "production"):
            continue
        created_at = row.get("createdAt", row.get("created"))
        if not isinstance(created_at, (int, float)) or created_at < started_at_ms - 1_000:
            # Old READY deployments must not satisfy a newly accepted hook.
            continue
        matches.append(row)
    if not matches:
        return None
    candidate = max(matches, key=lambda row: row.get("createdAt", row.get("created", 0)))
    state = candidate.get("readyState", candidate.get("state"))
    if state in ("ERROR", "CANCELED", "BLOCKED"):
        raise VerificationError(f"expected-SHA production deployment ended in {state}")
    if state == "READY":
        return candidate
    return None


def verify_once(expected_sha: str, started_at_ms: int, token: str) -> tuple[str | None, str]:
    params = urllib.parse.urlencode({
        "projectId": PROJECT_ID, "teamId": TEAM_ID, "target": "production", "limit": 100
    })
    response = api_json("/v7/deployments?" + params, token)
    rows = response.get("deployments")
    if not isinstance(rows, list):
        raise VerificationError("Vercel deployment list has an invalid shape")
    candidate = matching_deployment(rows, expected_sha, started_at_ms)
    if candidate is None:
        return None, "waiting for expected-SHA READY production deployment"

    deployment_id = candidate.get("id")
    if not isinstance(deployment_id, str) or not re.fullmatch(r"dpl_[A-Za-z0-9]+", deployment_id):
        raise VerificationError("expected-SHA deployment has an invalid ID")

    detail = api_json(
        "/v13/deployments/" + deployment_id + "?" + urllib.parse.urlencode({"teamId": TEAM_ID}),
        token,
    )
    project = detail.get("project") or {}
    meta = detail.get("meta") or {}
    if (detail.get("id") != deployment_id
            or (detail.get("projectId") or project.get("id")) != PROJECT_ID
            or detail.get("target") != "production"
            or meta.get("githubCommitSha") != expected_sha
            or meta.get("githubRepo") != EXPECTED_REPO
            or meta.get("githubOrg") != EXPECTED_ORG):
        raise VerificationError("deployment identity, project, environment or SHA mismatch")
    detail_state = detail.get("readyState", detail.get("state"))
    if detail_state != "READY":
        if detail_state in ("ERROR", "CANCELED", "BLOCKED"):
            raise VerificationError(f"expected-SHA deployment ended in {detail_state}")
        return None, "waiting for detailed deployment READY state"

    alias = api_json(
        "/v4/aliases/" + ALIAS + "?" + urllib.parse.urlencode(
            {"teamId": TEAM_ID, "projectId": PROJECT_ID}
        ),
        token,
    )
    if alias.get("projectId") != PROJECT_ID:
        raise VerificationError("production alias belongs to a different project")
    if alias.get("deploymentId") != deployment_id:
        return None, "waiting for production alias to point to expected deployment"

    for path in ROUTES:
        route_ok(path)
    return deployment_id, "verified"


def wait_for_verified(expected_sha: str, started_at_ms: int, token: str,
                      wait_seconds: int, interval_seconds: int) -> str:
    deadline = time.monotonic() + wait_seconds
    while True:
        deployment_id, message = verify_once(expected_sha, started_at_ms, token)
        if deployment_id is not None:
            return deployment_id
        if time.monotonic() >= deadline:
            raise VerificationError(f"production verification timed out: {message}")
        time.sleep(interval_seconds)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--expected-sha", required=True)
    parser.add_argument("--started-at-ms", type=int, required=True)
    parser.add_argument("--wait-seconds", type=int, default=900)
    parser.add_argument("--interval-seconds", type=int, default=15)
    args = parser.parse_args()
    if not re.fullmatch(r"[0-9a-f]{40}", args.expected_sha):
        parser.error("--expected-sha must be a lowercase full 40-character Git SHA")
    if args.started_at_ms <= 0:
        parser.error("--started-at-ms must be a positive Unix millisecond timestamp")
    if args.wait_seconds < 0 or args.interval_seconds < 1:
        parser.error("invalid polling interval / timeout")
    token = os.environ.get("VERCEL_TOKEN", "")
    if not token:
        parser.error("VERCEL_TOKEN is required for production verification")

    try:
        deployment_id = wait_for_verified(
            args.expected_sha, args.started_at_ms, token,
            args.wait_seconds, args.interval_seconds,
        )
    except VerificationError as exc:
        parser.exit(1, f"Kaigo Ops production verification FAILED: {exc}\n")
    print(f"Kaigo Ops production verification PASS: deployment={deployment_id} "
          f"state=READY commit={args.expected_sha} alias=https://{ALIAS} "
          f"routes={len(ROUTES)}/{len(ROUTES)}")


if __name__ == "__main__":
    main()
