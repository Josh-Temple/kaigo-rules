#!/usr/bin/env python3
"""Fail-closed final gate for a *future* GitHub Pages release.

Only an independently reviewed, version-pinned, complete static candidate may
pass. A successful experimental CI job is not release approval.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REQUIRED_REVIEWS = (
    "legal_currentness_review",
    "publication_scope_review",
    "independent_functional_acceptance",
    "android_and_print_acceptance",
    "security_and_privacy_review",
    "hosting_and_link_acceptance",
    "fee_2026_revision_integrated",
)
SHA = re.compile(r"^[a-f0-9]{40}$")


def errors_for(report: dict, acceptance: dict, commit: str) -> list[str]:
    problems = []
    if not SHA.fullmatch(commit):
        return ["Expected exact 40-character source SHA"]
    if acceptance.get("source_sha") != commit:
        problems.append("Independent release approval does not match source SHA")
    if acceptance.get("decision") != "APPROVED_FOR_PUBLICATION":
        problems.append("Independent release decision is not approved")
    if not isinstance(acceptance.get("reviewer"), str) or not acceptance["reviewer"].strip():
        problems.append("Missing independent reviewer identity")
    for name in REQUIRED_REVIEWS:
        if acceptance.get(name) is not True:
            problems.append("Required review incomplete: " + name)
    size = report.get("total_bytes")
    budget = report.get("pages_budget_bytes")
    if not isinstance(size, int) or not isinstance(budget, int) or size <= 0 or budget != 1_000_000_000 or size > budget:
        problems.append("Pages total-byte budget is not verified")
    blockers = report.get("blockers")
    if not isinstance(blockers, dict) or not blockers:
        problems.append("Missing route/security blocker report")
    else:
        for key, value in blockers.items():
            if not isinstance(value, int) or value != 0:
                problems.append(f"Unresolved publication blocker: {key}={value}")
    if not isinstance(report.get("html_count"), int) or report["html_count"] < 585:
        problems.append("Incomplete static HTML output")
    return problems


def read_and_check(report_path: Path, approval_path: Path, source_sha: str) -> None:
    if not report_path.is_file() or not approval_path.is_file():
        raise RuntimeError("Missing audit or independent acceptance file; no release")
    report = json.loads(report_path.read_text(encoding="utf-8"))
    acceptance = json.loads(approval_path.read_text(encoding="utf-8"))
    failures = errors_for(report, acceptance, source_sha)
    if failures:
        raise RuntimeError("Pages release blocked:\n" + "\n".join("- " + item for item in failures))
    print("PAGES_RELEASE_GATE: PASS for source " + source_sha)


if __name__ == "__main__":
    if len(sys.argv) != 4:
        raise SystemExit("Usage: check_github_pages_release_gate.py AUDIT_JSON ACCEPTANCE_JSON SOURCE_SHA")
    read_and_check(Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3])
