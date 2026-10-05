#!/usr/bin/env python3
"""Validate Fee Guidance item-body evidence classification and fail-closed projection."""
from collections import Counter
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = "data/shared/fee-guidance/"


def load(root: Path, path: str):
    return json.loads((root / path).read_text(encoding="utf-8"))


def validate(root=ROOT):
    manifest = load(root, BASE + "manifest.json")
    assurance_path = manifest["item_body_assurance"]
    assurance = load(root, assurance_path)
    applicability = load(root, manifest["service_applicability"])["services"]
    corpus = load(root, manifest["canonical_node_store"])["nodes"]
    dayservice_audit = load(root, "data/fee-guidance-independent-verification.json")
    dayrehab_audit = load(root, "data/dayrehab-fee-guidance-independent-audit.json")

    apps = {row["service_id"]: row for row in applicability}
    projections = {row["service_id"]: row for row in assurance["service_projections"]}
    assert len(apps) == len(applicability) == 39
    assert len(projections) == len(assurance["service_projections"]) == 39
    assert set(projections) == set(apps)

    node_ids = {node["id"] for node in corpus}
    allowed_classes = {
        "DIRECT_CURRENT_BODY_AVAILABLE",
        "VERSIONED_BODY_AVAILABLE_NOT_CURRENTNESS_PROOF",
        "COMPARISON_BODY_ONLY",
        "LOCATOR_ONLY",
        "BODY_NOT_ESTABLISHED",
        "NOT_APPLICABLE",
    }
    allowed_states = {"PASS", "PARTIAL", "NOT_ESTABLISHED", "NOT_APPLICABLE"}

    for service_id, row in projections.items():
        app = apps[service_id]
        assert row["evidence_class"] in allowed_classes
        assert row["service_level_item_body"] in allowed_states
        assert row["scoped_node_ids"] == app.get("node_ids", [])
        assert row["scoped_node_count"] == len(row["scoped_node_ids"])
        assert set(row["scoped_node_ids"]) <= node_ids
        assert set(row["verified_node_ids"]) <= set(row["scoped_node_ids"])
        assert row["verified_node_count"] == len(row["verified_node_ids"])

        if app["state"] == "NOT_APPLICABLE":
            assert row["evidence_class"] == "NOT_APPLICABLE"
            assert row["service_level_item_body"] == "NOT_APPLICABLE"
            assert row["verified_node_count"] == 0
        else:
            assert row["applicability_state"] == "MAPPED"

        if row["evidence_class"] in {"COMPARISON_BODY_ONLY", "LOCATOR_ONLY", "BODY_NOT_ESTABLISHED"}:
            assert row["service_level_item_body"] != "PASS"

        if row["service_level_item_body"] == "PASS":
            assert row["verified_node_count"] == row["scoped_node_count"]
            assert row["projection_to_pass_permitted"] is True
        else:
            assert row["projection_to_pass_permitted"] is False

    expected_dayservice_verified = {
        "fee-guidance.shared.compat.dayservice." + item["guidance_id"]
        for item in dayservice_audit["items"]
        if item["result"] == "PASS"
    }
    dayservice = projections["dayservice"]
    assert dayservice["evidence_class"] == "VERSIONED_BODY_AVAILABLE_NOT_CURRENTNESS_PROOF"
    assert dayservice["service_level_item_body"] == "PARTIAL"
    assert set(dayservice["verified_node_ids"]) == expected_dayservice_verified
    assert dayservice["verified_node_count"] == 8
    assert dayservice["scoped_node_count"] == 29
    assert dayservice_audit["safety"]["verified_current"] is False
    assert dayservice_audit["safety"]["human_verified"] is False

    dayrehab = projections["dayrehab"]
    assert dayrehab["evidence_class"] == "COMPARISON_BODY_ONLY"
    assert dayrehab["service_level_item_body"] == "NOT_ESTABLISHED"
    assert dayrehab_audit["coverage"]["verified_current_items"] == 0
    assert "no full current text" in dayrehab_audit["method"].lower()

    evidence_counts = Counter(row["evidence_class"] for row in projections.values())
    state_counts = Counter(row["service_level_item_body"] for row in projections.values())
    assert dict(evidence_counts) == assurance["summary"]["evidence_class_counts"]
    assert dict(state_counts) == assurance["summary"]["service_level_item_body_counts"]
    assert assurance["summary"]["source_level_verified_canonical_nodes"] == 8
    assert assurance["summary"]["service_level_pass_count"] == 0

    safety = assurance["safety"]
    for key in (
        "comparison_only_promoted_to_current_integrated_body",
        "omitted_text_treated_as_body_equality",
        "currentness_promoted",
        "human_review_promoted",
        "publication_promoted",
        "route_exposure_promoted",
        "global_generated_artifacts_updated",
    ):
        assert safety[key] is False

    return {
        "services": len(projections),
        "evidence_classes": dict(evidence_counts),
        "item_body_states": dict(state_counts),
        "verified_nodes": 8,
    }


if __name__ == "__main__":
    print("Fee Guidance item-body assurance PASS:", validate())
