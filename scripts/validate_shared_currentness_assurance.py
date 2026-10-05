#!/usr/bin/env python3
"""Validate shared currentness evidence and fail-closed service projection rules."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from shared_currentness_projection import (
    ASSURANCE_PATH,
    ROOT,
    TARGET_FAMILIES,
    build_projection_report,
    load,
)

EXPECTED_BASE_SHA = "8094361e28c25c134b7195abf12977e904c19162"
EXPECTED_FAMILIES = set(TARGET_FAMILIES)


def is_sha256(value: Any) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(ch in "0123456789abcdef" for ch in value)
    )


def require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def validate_current_meta(
    label: str,
    meta: dict[str, Any],
    snapshot: dict[str, Any],
    errors: list[str],
) -> None:
    current = meta.get("current_revision") or {}
    require(
        current.get("current_revision_status") == "CurrentEnforced",
        f"{label}: source is not CurrentEnforced",
        errors,
    )
    require(
        current.get("repeal_status") in (None, "None"),
        f"{label}: current revision is marked repealed",
        errors,
    )
    require(
        snapshot.get("current_revision_id") == current.get("law_revision_id"),
        f"{label}: current revision identity drifted",
        errors,
    )
    require(
        snapshot.get("amendment_enforcement_date")
        == current.get("amendment_enforcement_date"),
        f"{label}: amendment enforcement date drifted",
        errors,
    )
    require(
        snapshot.get("xml_sha256") == meta.get("xml_sha256")
        and is_sha256(meta.get("xml_sha256")),
        f"{label}: XML hash missing or drifted",
        errors,
    )
    require(
        snapshot.get("revision_response_sha256")
        == meta.get("revision_response_sha256")
        and is_sha256(meta.get("revision_response_sha256")),
        f"{label}: revisions hash missing or drifted",
        errors,
    )
    require(
        snapshot.get("revision_count") == meta.get("revision_count")
        and isinstance(meta.get("revision_count"), int)
        and meta.get("revision_count") > 0,
        f"{label}: revision count missing or drifted",
        errors,
    )


def main() -> int:
    errors: list[str] = []
    assurance = load(ASSURANCE_PATH)

    require(
        assurance.get("assurance_kind")
        == "SHARED_CURRENTNESS_EVIDENCE_AND_SAFE_PROJECTION",
        "unexpected assurance_kind",
        errors,
    )
    require(
        assurance.get("base_main_sha") == EXPECTED_BASE_SHA,
        "base_main_sha drifted",
        errors,
    )
    require(
        set((assurance.get("source_families") or {}).keys()) == EXPECTED_FAMILIES,
        "top-three source family evidence set drifted",
        errors,
    )

    invariant = assurance.get("projection_invariant") or {}
    required_conditions = invariant.get("required_conditions") or []
    require(
        required_conditions
        == [
            "source_identity_currentness_established",
            "service_scope_established",
            "service_applicability_explicitly_established",
            "service_reference_aligned_with_current_source_identity",
            "no_historical_or_old_version_pin",
        ],
        "projection invariant no longer contains the five required conditions",
        errors,
    )

    act_source = assurance["source_families"]["care_insurance_act"]
    act_meta = load(act_source["meta_path"])
    require(
        act_source.get("source_level_verdict") == "CURRENT",
        "care_insurance_act source verdict must be CURRENT",
        errors,
    )
    require(
        act_source.get("law_id") == act_meta.get("law_id"),
        "care_insurance_act law identity drifted",
        errors,
    )
    validate_current_meta(
        "care_insurance_act",
        act_meta,
        act_source.get("source_snapshot") or {},
        errors,
    )

    standards = assurance["source_families"]["governing_standards_ordinance"]
    manifest = load(standards["manifest"])
    manifest_ids = [row.get("corpus_id") for row in manifest.get("corpora", [])]
    snapshots = {
        row.get("corpus_id"): row for row in standards.get("corpora", [])
    }
    require(
        len(manifest_ids) == standards.get("current_corpus_count") == 9,
        "governing standards current corpus count drifted",
        errors,
    )
    require(
        set(manifest_ids) == set(snapshots),
        "governing standards snapshot set differs from manifest",
        errors,
    )
    for corpus_id in manifest_ids:
        snap = snapshots.get(corpus_id) or {}
        meta_path = snap.get("meta_path")
        if not meta_path:
            errors.append(f"{corpus_id}: missing meta_path")
            continue
        meta = load(meta_path)
        require(
            snap.get("law_id") == meta.get("law_id"),
            f"{corpus_id}: law identity drifted",
            errors,
        )
        validate_current_meta(corpus_id, meta, snap, errors)

    historical = manifest.get("historical_or_special", [])
    require(
        any(
            row.get("status") == "HISTORICAL_REPEALED_NOT_CURRENT_BASELINE"
            for row in historical
        ),
        "historical/repealed standards exclusion boundary missing",
        errors,
    )

    qa = assurance["source_families"]["national_qa"]
    qa_meta = load("data/qa-corpus-meta.json")
    require(
        qa.get("source_level_verdict") == "CURRENT_COMPILATION_ONLY",
        "national_qa must remain compilation-level only",
        errors,
    )
    require(
        qa.get("official_page") == qa_meta.get("source_page"),
        "national_qa official page drifted",
        errors,
    )
    require(
        qa.get("workbook") == qa_meta.get("source_workbook"),
        "national_qa workbook identity drifted",
        errors,
    )
    require(
        qa.get("workbook_sha256") == qa_meta.get("source_sha256")
        and is_sha256(qa_meta.get("source_sha256")),
        "national_qa workbook hash drifted",
        errors,
    )
    require(
        qa.get("individual_qa_currentness")
        == "NOT_ESTABLISHED_BY_COMPILATION_FRESHNESS",
        "national_qa individual currentness boundary was weakened",
        errors,
    )

    freshness = assurance.get("source_link_freshness_relation") or {}
    require(
        freshness.get("latestness_verdict") == "NOT_ESTABLISHED",
        "freshness-sensitive fee relation must remain unproven",
        errors,
    )
    require(
        freshness.get("queue_disposition") == "KEEP_OPEN",
        "freshness-sensitive fee relation was closed without conclusive evidence",
        errors,
    )

    queue = load("data/relation-verification-queue.json")
    queue_item = next(
        (
            row
            for row in queue.get("items", [])
            if row.get("identity") == freshness.get("identity")
        ),
        None,
    )
    require(queue_item is not None, "freshness-sensitive relation queue item missing", errors)
    if queue_item is not None:
        require(
            queue_item.get("classification")
            == "SOURCE_LINK_FRESHNESS_OR_DIRECT_EVIDENCE_REQUIRED",
            "freshness-sensitive relation classification changed unexpectedly",
            errors,
        )

    report = build_projection_report()
    expected_services = len(load("data/services/manifest.json").get("services", []))
    require(
        report["summary"]["cells_evaluated"] == expected_services * 3,
        "projection evaluator did not cover every service x top-three family cell",
        errors,
    )

    for row in report.get("rows", []):
        conditions = row.get("conditions") or {}
        missing = [name for name in required_conditions if name not in conditions]
        require(
            not missing,
            f"{row.get('service_id')}/{row.get('source_family')}: missing conditions {missing}",
            errors,
        )
        if row.get("promotion_applied"):
            require(
                all(bool(conditions.get(name)) for name in required_conditions),
                f"{row['service_id']}/{row['source_family']}: promotion without all five conditions",
                errors,
            )
            require(
                row.get("automatic_projection_allowed") is True,
                f"{row['service_id']}/{row['source_family']}: promotion without explicit gate",
                errors,
            )
            require(
                row.get("source_family") != "national_qa",
                f"{row['service_id']}/national_qa: compilation freshness promoted to PASS",
                errors,
            )
        else:
            require(
                row.get("projected_currentness") == row.get("existing_currentness"),
                f"{row['service_id']}/{row['source_family']}: unsupported state change",
                errors,
            )

    for row in report.get("rows", []):
        if row.get("source_family") == "national_qa":
            require(
                row.get("promotion_applied") is False,
                f"{row['service_id']}/national_qa: individual currentness inferred from compilation",
                errors,
            )

    safety = assurance.get("safety") or {}
    for key in (
        "global_generated_artifacts_updated",
        "source_currentness_broadcast_to_all_services",
        "item_body_promoted",
        "relation_verification_promoted",
        "human_review_promoted",
        "publication_promoted",
        "route_enabled",
        "negative_search_used_as_conclusive_proof",
    ):
        require(safety.get(key) is False, f"safety boundary broken: {key}", errors)

    output = {
        "format_version": 1,
        "validation_kind": "SHARED_CURRENTNESS_ASSURANCE",
        "result": "PASS" if not errors else "FAIL",
        "errors": errors,
        "observed": {
            "services": expected_services,
            "cells_evaluated": report["summary"]["cells_evaluated"],
            "promotions_recommended": report["summary"]["promotions_recommended"],
            "family_summary": report["summary"]["source_family"],
            "freshness_relation": freshness.get("queue_disposition"),
        },
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
