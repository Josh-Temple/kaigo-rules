#!/usr/bin/env python3
"""Validate Worker A residual Standards Interpretation assurance evidence.

This validator is fail-closed. It checks that the residual set is derived from
the current generated Coverage Matrix, that official evidence remains
version-separated, that repository snapshot fingerprints are reproducible,
and that no item-body/currentness/human-review/publication/routing promotion
is inferred without canonical item-level comparison.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "data/verification/standards-interpretation-item-body/residual-assurance-human-review-readiness-worker-a.json"
MATRIX = ROOT / "data/database-coverage-matrix.generated.json"

REQUIRED_BLOCKERS = {
    "CANONICAL_ITEM_BODY_NOT_AVAILABLE_FOR_COMPARISON",
    "NO_ITEM_LEVEL_STAGING",
    "SERVICE_LEVEL_BODY_COMPARISON_NOT_POSSIBLE",
    "SOURCE_VERSION_ALIGNMENT_NOT_ESTABLISHED",
}


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def current_residual_ids(matrix: dict) -> set[str]:
    result: set[str] = set()
    for service in matrix.get("services", []):
        family = next(
            (
                row
                for row in service.get("source_families", [])
                if row.get("source_family") == "standards_interpretation_notice"
            ),
            None,
        )
        if family and family.get("item_body_verification", {}).get("state") == "NOT_ESTABLISHED":
            result.add(service["service_id"])
    return result


def git_blob_sha(path: Path) -> str:
    data = path.read_bytes()
    header = f"blob {len(data)}\0".encode("ascii")
    return hashlib.sha1(header + data).hexdigest()


def validate() -> list[str]:
    errors: list[str] = []
    artifact = load(ARTIFACT)
    matrix = load(MATRIX)

    if artifact.get("source_family") != "standards_interpretation_notice":
        errors.append("source family mismatch")

    expected = current_residual_ids(matrix)
    rows = artifact.get("inventory", [])
    by_id = {row.get("service_id"): row for row in rows}
    if len(rows) != 26:
        errors.append(f"expected 26 rows, got {len(rows)}")
    if len(by_id) != len(rows) or None in by_id:
        errors.append("duplicate or missing service_id")
    if set(by_id) != expected:
        errors.append(
            "artifact residual set differs from Coverage Matrix: "
            f"missing={sorted(expected - set(by_id))} extra={sorted(set(by_id) - expected)}"
        )

    fresh = artifact.get("fresh_inventory", {})
    if fresh.get("residual_count") != len(expected):
        errors.append("fresh residual count mismatch")
    if set(fresh.get("residual_service_ids", [])) != expected:
        errors.append("fresh residual ids mismatch")

    result = artifact.get("result", {})
    if result.get("promoted_to_pass") != 0:
        errors.append("unsafe PASS promotion recorded")
    if result.get("kept_not_established") != 26:
        errors.append("all 26 residuals must remain fail-closed in this Worker A result")
    if result.get("service_level_item_body_after") != {"PASS": 13, "NOT_ESTABLISHED": 26}:
        errors.append("unexpected post-worker service-level item-body inventory")

    for service_id, row in by_id.items():
        if row.get("prior_item_body_state") != "NOT_ESTABLISHED":
            errors.append(f"{service_id}: prior item-body state mismatch")
        if row.get("item_body_state_after_worker_a") != "NOT_ESTABLISHED":
            errors.append(f"{service_id}: item-body was promoted")
        if row.get("canonical_item_body_exists") is not False:
            errors.append(f"{service_id}: canonical item body overclaimed")
        if row.get("item_level_staging_exists") is not False:
            errors.append(f"{service_id}: item-level staging overclaimed")
        if row.get("direct_canonical_vs_official_comparison_performed") is not False:
            errors.append(f"{service_id}: direct comparison overclaimed")
        if row.get("service_level_pass_eligible") is not False:
            errors.append(f"{service_id}: PASS eligibility overclaimed")
        if not row.get("service_scope_locators"):
            errors.append(f"{service_id}: service scope locator missing")

        blockers = set(row.get("blockers", []))
        missing_blockers = REQUIRED_BLOCKERS - blockers
        if missing_blockers:
            errors.append(f"{service_id}: missing blockers {sorted(missing_blockers)}")

        comparison = row.get("r6_comparison_evidence", {})
        url = str(comparison.get("url", ""))
        if not url.startswith("https://www.mhlw.go.jp/"):
            errors.append(f"{service_id}: comparison source is not official MHLW")
        if comparison.get("current_integrated_text") is not False:
            errors.append(f"{service_id}: comparison treated as integrated current text")
        if comparison.get("proves_currentness") is not False:
            errors.append(f"{service_id}: comparison improperly proves currentness")
        if not comparison.get("locator"):
            errors.append(f"{service_id}: comparison/body locator note missing")

        identity = row.get("canonical_notice_identity", {})
        if not identity.get("document_id") or not identity.get("notice_number"):
            errors.append(f"{service_id}: canonical notice identity incomplete")
        if row.get("official_index_url") != "https://www.mhlw.go.jp/stf/newpage_38790.html":
            errors.append(f"{service_id}: official index URL mismatch")

        for fp in row.get("pinned_versioned_source_body_evidence", []):
            relative = fp.get("snapshot_path")
            recorded = fp.get("git_blob_sha")
            if not relative or not recorded:
                errors.append(f"{service_id}: incomplete snapshot fingerprint")
                continue
            path = ROOT / relative
            if not path.exists():
                errors.append(f"{service_id}: snapshot missing: {relative}")
                continue
            actual = git_blob_sha(path)
            if actual != recorded:
                errors.append(
                    f"{service_id}: snapshot fingerprint mismatch for {relative}: "
                    f"recorded={recorded} actual={actual}"
                )
            if fp.get("proves_currentness") is not False:
                errors.append(f"{service_id}: snapshot improperly proves currentness")

        axes = row.get("axis_preservation", {})
        if axes.get("currentness") != "NOT_ESTABLISHED":
            errors.append(f"{service_id}: currentness promoted")
        if axes.get("human_review") != "NOT_REVIEWED":
            errors.append(f"{service_id}: human review promoted")
        if axes.get("publication_promoted") is not False:
            errors.append(f"{service_id}: publication promoted")
        if axes.get("route_promoted") is not False:
            errors.append(f"{service_id}: route promoted")

    source_progress = artifact.get("source_level_progress", {})
    for doc in source_progress.get("observed_primary_documents", []):
        url = str(doc.get("comparison_url", ""))
        if not url.startswith("https://www.mhlw.go.jp/"):
            errors.append(f"{doc.get('document_id')}: non-MHLW source")
        if doc.get("current_integrated_text") is not False:
            errors.append(f"{doc.get('document_id')}: source-level currentness overclaim")

    safety = artifact.get("safety", {})
    if safety.get("generated_coverage_artifacts_modified") is not False:
        errors.append("generated Coverage Matrix mutation claimed")
    for key in (
        "item_body_promotions",
        "currentness_promotions",
        "human_review_promotions",
        "publication_promotions",
        "route_promotions",
    ):
        if safety.get(key) != 0:
            errors.append(f"nonzero unsafe promotion count: {key}")
    for key in (
        "heading_only_never_promoted",
        "url_presence_never_promoted",
        "historical_body_never_treated_as_current_integrated_text",
        "comparison_only_never_treated_as_current_integrated_text",
    ):
        if safety.get(key) is not True:
            errors.append(f"safety invariant weakened: {key}")

    return errors


def main() -> int:
    errors = validate()
    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        return 1
    print(
        "PASS: residual Standards Interpretation assurance evidence is reproducible; "
        "26 services remain fail-closed and no downstream axis was promoted."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
