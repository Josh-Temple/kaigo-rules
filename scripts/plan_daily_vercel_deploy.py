#!/usr/bin/env python3
"""Fail-closed change planning for the two daily Vercel deployment targets.

Compare complete trees of the last *recorded* deployment and current HEAD.
Do not use a merge-base (...), which can miss changes on diverged histories.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import subprocess


def _git(repo: str, *args: str) -> str:
    return subprocess.run(
        ["git", *args],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def changed_paths(repo: str, baseline: str, head: str) -> set[str] | None:
    """Return changed tracked paths, or None if a baseline is unavailable.

    A missing/unresolvable marker requires deployment; it must never mean
    "no changes". Real git-diff errors raise and fail the workflow.
    """
    if not baseline:
        return None
    try:
        _git(repo, "cat-file", "-e", f"{baseline}^{{commit}}")
    except subprocess.CalledProcessError:
        return None
    names = _git(repo, "diff", "--name-only", "--no-renames", baseline, head, "--")
    return set(names.splitlines()) if names else set()


def is_ops_path(path: str) -> bool:
    return path == "ops-site" or path.startswith("ops-site/")


def needs_deploy(
    rules_paths: set[str] | None,
    ops_paths: set[str] | None,
    *,
    force_rules: bool = False,
    force_ops: bool = False,
) -> tuple[bool, bool]:
    # Conservative by design: any tracked non-ops change might affect rules,
    # including lib/, new directories, build configuration or CI/deploy code.
    # This may cause safe extra deploys for docs-only changes.
    rules = force_rules or rules_paths is None or any(
        not is_ops_path(path) for path in rules_paths
    )
    ops = force_ops or ops_paths is None or any(is_ops_path(path) for path in ops_paths)
    return bool(rules), bool(ops)


def parse_bool(value: str) -> bool:
    if value.lower() not in ("true", "false"):
        raise argparse.ArgumentTypeError("expected true or false")
    return value.lower() == "true"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--head", required=True)
    parser.add_argument("--rules-base", default="")
    parser.add_argument("--ops-base", default="")
    parser.add_argument("--force-rules", type=parse_bool, default=False)
    parser.add_argument("--force-ops", type=parse_bool, default=False)
    parser.add_argument("--repo", default=".")
    parser.add_argument("--github-output", required=True)
    parser.add_argument("--github-step-summary", required=True)
    args = parser.parse_args()

    rules_paths = changed_paths(args.repo, args.rules_base, args.head)
    ops_paths = changed_paths(args.repo, args.ops_base, args.head)
    rules, ops = needs_deploy(
        rules_paths, ops_paths,
        force_rules=args.force_rules, force_ops=args.force_ops,
    )

    output = (
        f"head_sha={args.head}\n"
        f"rules_changed={str(rules).lower()}\n"
        f"ops_changed={str(ops).lower()}\n"
    )
    with Path(args.github_output).open("a", encoding="utf-8") as handle:
        handle.write(output)

    def status(paths: set[str] | None) -> str:
        if paths is None:
            return "marker unavailable (deploy required)"
        return f"{len(paths)} changed paths"

    summary = (
        "## Daily Vercel deployment plan\n\n"
        f"- HEAD: {args.head}\n"
        f"- kaigo-rules baseline: {args.rules_base or '(missing)'}; "
        f"{status(rules_paths)}\n"
        f"- kaigo-rules deploy needed: {str(rules).lower()}\n"
        f"- kaigo-ops baseline: {args.ops_base or '(missing)'}; "
        f"{status(ops_paths)}\n"
        f"- kaigo-ops deploy needed: {str(ops).lower()}\n"
        "- A successful plan is not evidence of production deployment. "
        "For kaigo-rules, production SHA is checked by the deploy job.\n"
    )
    with Path(args.github_step_summary).open("a", encoding="utf-8") as handle:
        handle.write(summary)
    print(output, end="")
    print(summary)


if __name__ == "__main__":
    main()
