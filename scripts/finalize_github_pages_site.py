#!/usr/bin/env python3
"""Audit, rewrite, brand, and finalize the generated GitHub Pages site artifact.

Extracted from the inline YAML step in .github/workflows/kaigo-pages-public-beta-main.yml
so the publication checks and branding transformation are directly testable and maintainable.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.audit_github_pages_migration_readiness import inspect

PREVIOUS_LABEL = "Kaigo Rules 試験公開版"
PREVIOUS_NOTICE = "試験公開版です。未確認の法令情報や旧サイトへのリンクが含まれます。"
CURRENT_NOTICE = "制度情報の確認状況は項目ごとに異なり、未確認の情報を含みます。"
REQUIRED_CAUTION = "制度の現行性・適用条件は必ず国の原典と指定権者に確認してください。"
OBSOLETE_BANNER = (
    '<div class="pilot-banner"><strong>Kaigo Rules</strong>'
    "<p>現在の本番とは別の試作品です。法令の現行性・適用条件・自治体の基準を必ず原典で確認してください。"
    "この試作品では印刷・対話操作やサイト内リンクの一部が本番と異なる場合があります。</p></div>"
)

EXPECTED_SINGLE_STAFFING_OVERVIEWS = (
    "community_staffing_overview",
    "health_facility_staffing_overview",
    "welfare_facility_staffing_overview",
    "group_home_staffing_overview",
    "preventive_group_home_staffing_overview",
    "night_homevisit_manager",
    "care_medical_staffing_overview",
    "nursing_small_scale_roles",
    "care_management_staffing_overview",
    "dementia_dayservice_staffing_overview",
    "preventive_dementia_dayservice_staffing_overview",
    "community_facility_equipment_overview",
)

EXPECTED_DOUBLE_STAFFING_OVERVIEWS = (
    ("homebath_staffing_overview", "Missing or duplicate home-bathing staffing or operations source"),
    (
        "preventive_homebath_staffing_overview",
        "Missing or duplicate preventive home-bathing staffing or operations source",
    ),
)

EXPECTED_FEE_VERSION_LABELS = (
    ("fee_root_version_labels", 1),
    ("fee_detail_version_labels", 29),
)


def apply_public_site_branding(root: Path, expected_html_count: int) -> dict[str, int | bool]:
    """Remove public-beta wording while preserving unverified-source warnings and noindex."""
    updated = 0
    removed_obsolete_banners = 0

    for page in root.rglob("*.html"):
        if page.is_symlink():
            raise RuntimeError("Unsafe symbolic link in published site")
        old = page.read_text(encoding="utf-8")
        if PREVIOUS_LABEL not in old or PREVIOUS_NOTICE not in old or REQUIRED_CAUTION not in old:
            raise RuntimeError("Missing safety banner or expected published page: " + str(page))
        new = old.replace(PREVIOUS_LABEL, "Kaigo Rules").replace(PREVIOUS_NOTICE, CURRENT_NOTICE)
        removed_obsolete_banners += new.count(OBSOLETE_BANNER)
        new = new.replace(OBSOLETE_BANNER, "")
        new = new.replace(" — 静的移行検証</title>", " — Kaigo Rules</title>")
        relative = page.relative_to(root).as_posix()
        if relative == "index.html":
            new = new.replace("制度DB横断検索を試す", "制度DBを横断検索する")
        elif relative == "databases/search/index.html":
            if (
                "<title>制度DB検索・非公開の移行検証</title>" not in new
                or "<strong>検索の移行検証用・公開不可</strong>" not in new
            ):
                raise RuntimeError("Unexpected database search copy")
            new = new.replace(
                "<title>制度DB検索・非公開の移行検証</title>",
                "<title>制度DB検索 — Kaigo Rules</title>",
            )
            new = new.replace(
                "<strong>検索の移行検証用・公開不可</strong>",
                "<strong>検索結果の確認について</strong>",
            )
            new = new.replace("リンク先は現行サイトです。", "")
        elif relative == "databases/search/qa.html":
            if (
                "<title>国Q&A検索・非公開の移行検証</title>" not in new
                or "<strong>国Q&A検索の移行検証用・公開不可</strong>" not in new
            ):
                raise RuntimeError("Unexpected Q&A search copy")
            new = new.replace(
                "<title>国Q&A検索・非公開の移行検証</title>",
                "<title>国Q&A検索 — Kaigo Rules</title>",
            )
            new = new.replace(
                "<strong>国Q&A検索の移行検証用・公開不可</strong>",
                "<strong>国Q&Aの確認について</strong>",
            )
        if (
            "試験公開版" in new
            or "一般公開していません" in new
            or "現在の本番とは別の試作品です。" in new
            or "この試作品では印刷・対話操作" in new
            or REQUIRED_CAUTION not in new
        ):
            raise RuntimeError("Inconsistent public site branding or caution: " + str(page))
        if new != old:
            page.write_text(new, encoding="utf-8")
            updated += 1

    if updated != expected_html_count:
        raise RuntimeError("Incomplete production-label update")
    if removed_obsolete_banners == 0:
        raise RuntimeError("Expected obsolete pilot banner was not found")

    result: dict[str, int | bool] = {
        "updated_html_pages": updated,
        "obsolete_banners_removed": removed_obsolete_banners,
        "noindex_retained": True,
    }
    print("PUBLIC_SITE_BRANDING:", json.dumps(result, ensure_ascii=False))
    return result


def finalize_site(build_log: Path, source_sha: str, github_output: Path | None = None) -> Path:
    summary = json.loads(build_log.read_text(encoding="utf-8").splitlines()[-1])
    root = Path(summary["directory"]).resolve(strict=True)
    if root.is_symlink() or not (root / "index.html").is_file():
        raise RuntimeError("Unsafe output path")
    if summary.get("handbook_services") != 39 or summary.get("handbook_chapters") != 585:
        raise RuntimeError("Missing service handbook chapters")
    if summary.get("qa_details", {}).get("detail_pages") != 7392:
        raise RuntimeError("Missing QA details")
    if summary.get("legal_details", {}).get("detail_pages") != 1552:
        raise RuntimeError("Missing legal source details")

    pre = inspect(root)
    problems = pre["blockers"]
    for item in ("missing_local_links", "root_relative_links", "unsafe_or_invalid_links"):
        if problems[item] != 0:
            raise RuntimeError("Unsafe static route blocker: " + item)
    if not 0 <= problems["production_fallback_links"] <= 2500:
        raise RuntimeError("Unexpected legacy link regression")
    if problems["javascript_references_to_production"] > 2:
        raise RuntimeError("Unexpected production URL usage in JS")
    if pre["total_bytes"] >= 1_000_000_000 or pre["html_count"] < 13000:
        raise RuntimeError("Unexpected Pages size/content")

    outcome = subprocess.run(
        [sys.executable, str(ROOT / "scripts/prepare_github_pages_beta.py"), str(root)],
        capture_output=True,
        text=True,
        check=True,
    )
    print("SOURCE_SAFETY_PREPARATION:", outcome.stdout.strip())

    link_fix = subprocess.run(
        [sys.executable, str(ROOT / "scripts/rewrite_public_navigation.py"), str(root)],
        capture_output=True,
        text=True,
        check=True,
    )
    print("FEE_NAVIGATION:", link_fix.stdout.strip())
    navigation_counts = json.loads(link_fix.stdout).get("additional_changes", {})

    for overview in EXPECTED_SINGLE_STAFFING_OVERVIEWS:
        if navigation_counts.get(overview) != 1:
            raise RuntimeError("Missing or duplicate staffing overview: " + overview)
    for key, error_message in EXPECTED_DOUBLE_STAFFING_OVERVIEWS:
        if navigation_counts.get(key) != 2:
            raise RuntimeError(error_message)
    for label, count in EXPECTED_FEE_VERSION_LABELS:
        if navigation_counts.get(label) != count:
            raise RuntimeError("Unexpected fee page version labels: " + label)

    apply_public_site_branding(root, pre["html_count"])

    post = inspect(root)
    for item in (
        "missing_local_links",
        "root_relative_links",
        "unsafe_or_invalid_links",
        "private_preview_pages",
    ):
        if post["blockers"][item] != 0:
            raise RuntimeError("Final beta safety check failed: " + item)
    if post["blockers"]["noindex_pages"] != post["html_count"]:
        raise RuntimeError("Beta pages not consistently noindex")

    boundary = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts/prepare_handbook_publication_boundary.py"),
            "audit",
            str(ROOT),
            str(root),
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    print("PUBLICATION_BOUNDARY:", boundary.stdout.strip())

    (root / ".nojekyll").touch()
    if github_output is not None:
        with github_output.open("a", encoding="utf-8") as out:
            out.write(f"path={root}\n")

    print(
        "PUBLIC_SITE_PRECHECK:",
        json.dumps(
            {
                "sha": source_sha,
                "html_count": post["html_count"],
                "total_bytes": post["total_bytes"],
                "remaining_legacy_links": post["blockers"]["production_fallback_links"],
                "noindex_pages": post["blockers"]["noindex_pages"],
                "local_links": post["local_links_resolved"],
            },
            ensure_ascii=False,
        ),
    )
    return root


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build-log", type=Path, required=True)
    parser.add_argument("--source-sha", default=os.environ.get("SOURCE_SHA", ""))
    parser.add_argument(
        "--github-output",
        type=Path,
        default=Path(os.environ["GITHUB_OUTPUT"]) if os.environ.get("GITHUB_OUTPUT") else None,
    )
    args = parser.parse_args()
    finalize_site(args.build_log, args.source_sha, args.github_output)


if __name__ == "__main__":
    main()
