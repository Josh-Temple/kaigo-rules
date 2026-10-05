#!/usr/bin/env python3
"""Validate Worker B Standards Interpretation residual classification.

The contract is deliberately fail-closed:
- the residual set must match the generated Coverage Matrix;
- historical/version-bounded body evidence and amendment material are not
  sufficient to establish a current integrated body;
- item-body and currentness remain independent axes;
- incomplete amendment chains cannot be reconstructed or promoted;
- pinned source fingerprints must remain reproducible.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "data/verification/standards-interpretation-item-body/currentness-human-review-activation-worker-b.json"
MATRIX = ROOT / "data/database-coverage-matrix.generated.json"

ALLOWED_EVIDENCE_CLASSES = {
    "official current integrated text available",
    "official historical text + amendment materials available",
    "official comparison table only",
    "locator/fingerprint only",
    "source identity unresolved",
    "source body unavailable",
}

REQUIRED_BLOCKERS = {
    "CANONICAL_ITEM_BODY_NOT_AVAILABLE_FOR_COMPARISON",
    "NO_ITEM_LEVEL_STAGING",
    "SERVICE_LEVEL_BODY_COMPARISON_NOT_POSSIBLE",
    "SOURCE_VERSION_ALIGNMENT_NOT_ESTABLISHED",
}


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def git_blob_sha(path: Path) -> str:
    data = path.read_bytes()
    header = f"blob {len(data)}\0".encode("ascii")
    return hashlib.sha1(header + data).hexdigest()


def standards_rows(matrix: dict) -> list[dict]:
    rows: list[dict] = []
    for service in matrix.get("services", []):
        family = next(
            (
                row
                for row in service.get("source_families", [])
                if row.get("source_family") == "standards_interpretation_notice"
            ),
            None,
        )
        if family:
            rows.append({"service_id": service["service_id"], "family": family})
    return rows


def residual_ids(matrix: dict) -> set[str]:
    return {
        row["service_id"]
        for row in standards_rows(matrix)
        if row["family"].get("item_body_verification", {}).get("state") == "NOT_ESTABLISHED"
    }


def axis_counts(matrix: dict, axis: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in standards_rows(matrix):
        value = row["family"].get(axis, {}).get("state")
        if value is not None:
            counts[value] = counts.get(value, 0) + 1
    return counts


def validate_payload(artifact: dict, matrix: dict, root: Path = ROOT) -> list[str]:
    errors: list[str] = []

    if artifact.get("worker") != "B":
        errors.append("worker identity mismatch")
    if artifact.get("source_family") != "standards_interpretation_notice":
        errors.append("source family mismatch")

    expected = residual_ids(matrix)
    rows = artifact.get("inventory", [])
    by_id = {row.get("service_id"): row for row in rows}

    if len(rows) != 26:
        errors.append(f"expected 26 residual rows, got {len(rows)}")
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
        errors.append("fresh residual service ids mismatch")

    expected_item_counts = axis_counts(matrix, "item_body_verification")
    expected_current_counts = axis_counts(matrix, "currentness")
    if fresh.get("item_body_before") != expected_item_counts:
        errors.append(
            f"item-body before counts mismatch: recorded={fresh.get('item_body_before')} "
            f"actual={expected_item_counts}"
        )
    if fresh.get("currentness_before") != expected_current_counts:
        errors.append(
            f"currentness before counts mismatch: recorded={fresh.get('currentness_before')} "
            f"actual={expected_current_counts}"
        )

    summary = artifact.get("evidence_classification_summary", {})
    if set(summary) != ALLOWED_EVIDENCE_CLASSES:
        errors.append("evidence classification keys differ from Worker B contract")
    if sum(int(summary.get(key, 0)) for key in ALLOWED_EVIDENCE_CLASSES) != len(rows):
        errors.append("evidence classification counts do not sum to residual inventory")

    actual_classes: dict[str, int] = {key: 0 for key in ALLOWED_EVIDENCE_CLASSES}
    snapshot_checks = 0
    groups = artifact.get("source_document_groups", [])
    group_by_doc = {group.get("document_id"): group for group in groups}

    for service_id, row in by_id.items():
        evidence_class = row.get("evidence_class")
        if evidence_class not in ALLOWED_EVIDENCE_CLASSES:
            errors.append(f"{service_id}: unsupported evidence class {evidence_class!r}")
        else:
            actual_classes[evidence_class] += 1

        if row.get("prior_item_body_state") != "NOT_ESTABLISHED":
            errors.append(f"{service_id}: prior item-body state mismatch")
        if row.get("item_body_state_after_worker_b") != "NOT_ESTABLISHED":
            errors.append(f"{service_id}: item-body was promoted without verified integrated body")
        if row.get("prior_currentness_state") != "NOT_ESTABLISHED":
            errors.append(f"{service_id}: prior currentness state mismatch")
        if row.get("currentness_state_after_worker_b") != "NOT_ESTABLISHED":
            errors.append(f"{service_id}: historical/amendment evidence was used to promote currentness")

        if row.get("pass_eligibility", {}).get("item_body") is not False:
            errors.append(f"{service_id}: item-body PASS eligibility overclaimed")
        if row.get("pass_eligibility", {}).get("currentness") is not False:
            errors.append(f"{service_id}: currentness PASS eligibility overclaimed")

        reconstruction = row.get("integrated_body_reconstruction", {})
        if reconstruction.get("attempted") is not False:
            errors.append(f"{service_id}: reconstruction attempted despite incomplete evidence chain")
        if reconstruction.get("reconstructed_text_committed") is not False:
            errors.append(f"{service_id}: reconstructed text committed despite incomplete evidence chain")
        reason = str(reconstruction.get("reason", "")).lower()
        if "amendment chain" not in reason or "canonical item-level body/staging" not in reason:
            errors.append(f"{service_id}: reconstruction blocker explanation incomplete")

        amendment = row.get("amendment_material", {})
        if not str(amendment.get("url", "")).startswith("https://www.mhlw.go.jp/"):
            errors.append(f"{service_id}: amendment material is not an official MHLW URL")
        if amendment.get("current_integrated_text") is not False:
            errors.append(f"{service_id}: amendment material treated as integrated current text")
        if amendment.get("proves_currentness") is not False:
            errors.append(f"{service_id}: amendment material treated as currentness proof")
        if not amendment.get("locator"):
            errors.append(f"{service_id}: amendment locator missing")

        if not row.get("historical_or_versioned_body_urls"):
            errors.append(f"{service_id}: historical/versioned body URL missing")
        if not row.get("service_scope_locators"):
            errors.append(f"{service_id}: service scope locator missing")

        missing_blockers = REQUIRED_BLOCKERS - set(row.get("blockers", []))
        if missing_blockers:
            errors.append(f"{service_id}: missing blockers {sorted(missing_blockers)}")

        safety = row.get("safety", {})
        if safety.get("historical_match_does_not_prove_currentness") is not True:
            errors.append(f"{service_id}: historical/currentness separation weakened")
        if safety.get("amendment_comparison_does_not_prove_integrated_current_text") is not True:
            errors.append(f"{service_id}: comparison/integrated-body separation weakened")
        if safety.get("item_body_and_currentness_evaluated_separately") is not True:
            errors.append(f"{service_id}: item-body/currentness separation weakened")
        if safety.get("publication_promoted") is not False:
            errors.append(f"{service_id}: publication promoted")
        if safety.get("route_promoted") is not False:
            errors.append(f"{service_id}: route promoted")

        fps = row.get("pinned_versioned_source_body_evidence", [])
        document_id = row.get("canonical_notice_identity", {}).get("document_id")
        group_fps = group_by_doc.get(document_id, {}).get("pinned_snapshot_evidence", [])
        if not fps and not group_fps:
            errors.append(
                f"{service_id}: neither service-linked nor source-document pinned fingerprint is available"
            )
        for fp in fps:
            snapshot_checks += 1
            relative = fp.get("snapshot_path")
            recorded = fp.get("git_blob_sha")
            if not relative or not recorded:
                errors.append(f"{service_id}: incomplete snapshot fingerprint")
                continue
            path = root / relative
            if not path.exists():
                errors.append(f"{service_id}: snapshot missing: {relative}")
                continue
            actual = git_blob_sha(path)
            if actual != recorded:
                errors.append(
                    f"{service_id}: source fingerprint mismatch for {relative}: "
                    f"recorded={recorded} actual={actual}"
                )
            if fp.get("proves_currentness") is not False:
                errors.append(f"{service_id}: pinned historical/versioned body overclaims currentness")

    if actual_classes != {key: int(summary.get(key, 0)) for key in ALLOWED_EVIDENCE_CLASSES}:
        errors.append(
            f"evidence classification summary mismatch: recorded={summary} actual={actual_classes}"
        )
    if snapshot_checks == 0:
        errors.append("no source fingerprints were checked")

    group_services: list[str] = []
    for group in groups:
        group_services.extend(group.get("service_ids", []))
        if not group.get("document_id") or not group.get("document_title"):
            errors.append("source document group identity incomplete")
        amendment = group.get("amendment_material", {})
        if amendment.get("current_integrated_text") is not False:
            errors.append(f"{group.get('document_id')}: source group overclaims integrated current text")
        if amendment.get("proves_currentness") is not False:
            errors.append(f"{group.get('document_id')}: source group overclaims currentness")
        for fp in group.get("pinned_snapshot_evidence", []):
            snapshot_checks += 1
            relative = fp.get("snapshot_path")
            recorded = fp.get("git_blob_sha")
            if not relative or not recorded:
                errors.append(f"{group.get('document_id')}: incomplete source-document fingerprint")
                continue
            path = root / relative
            if not path.exists():
                errors.append(f"{group.get('document_id')}: source-document snapshot missing: {relative}")
                continue
            actual = git_blob_sha(path)
            if actual != recorded:
                errors.append(
                    f"{group.get('document_id')}: source-document fingerprint mismatch for {relative}: "
                    f"recorded={recorded} actual={actual}"
                )
            if fp.get("proves_currentness") is not False:
                errors.append(f"{group.get('document_id')}: source-document fingerprint overclaims currentness")
    if set(group_services) != expected or len(group_services) != len(expected):
        errors.append("source document groups do not cover each residual service exactly once")

    result = artifact.get("result", {})
    if result.get("item_body_after") != expected_item_counts:
        errors.append("item-body result counts differ from Coverage Matrix")
    if result.get("currentness_after") != expected_current_counts:
        errors.append("currentness result counts differ from Coverage Matrix")
    for key in (
        "promoted_item_body_to_pass",
        "promoted_currentness_to_pass",
        "reconstructed_integrated_bodies",
    ):
        if result.get(key) != 0:
            errors.append(f"unsafe nonzero result count: {key}")
    if result.get("kept_not_established") != len(expected):
        errors.append("kept_not_established count mismatch")

    safety = artifact.get("safety", {})
    if safety.get("generated_coverage_artifacts_modified") is not False:
        errors.append("generated coverage artifacts were marked modified")
    for key in (
        "item_body_promotions",
        "currentness_promotions",
        "human_review_promotions",
        "publication_promotions",
        "route_promotions",
    ):
        if safety.get(key) != 0:
            errors.append(f"unsafe nonzero promotion count: {key}")
    for key in (
        "amendment_only_never_treated_as_integrated_current_text",
        "historical_body_never_treated_as_currentness_proof",
        "source_fingerprint_mismatch_fails_closed",
    ):
        if safety.get(key) is not True:
            errors.append(f"safety invariant weakened: {key}")

    return errors


def validate() -> list[str]:
    return validate_payload(load(ARTIFACT), load(MATRIX), ROOT)


def main() -> int:
    errors = validate()
    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        return 1
    print(
        "PASS: Worker B classified all 26 Standards Interpretation residuals; "
        "no incomplete amendment chain, historical match, or comparison-only evidence "
        "was promoted to item-body/currentness PASS."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
