#!/usr/bin/env python3
"""Validate fail-closed unit-price item-body assurance projections."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
ARTIFACT = DATA / "unit-price-item-body-assurance.json"
INDEX = DATA / "unit-price-service-multipliers.json"
MANIFEST = DATA / "services" / "manifest.json"
DAY_META = DATA / "unit-price-dayservice-meta.json"
REGION_META = DATA / "unit-price-region-assignments-meta.json"
EXPECTED_NA = {
    "specific-welfare-equipment-sale": "第44条",
    "specific-preventive-welfare-equipment-sale": "第56条",
}
ALLOWED_ITEM_STATES = {"PASS", "PARTIAL", "NOT_ESTABLISHED", "NOT_APPLICABLE"}


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def validate_payload(artifact: dict, index: dict, manifest: dict, day_meta: dict, region_meta: dict) -> None:
    if artifact.get("source_family") != "unit_price_regional_classification":
        raise ValueError("unexpected source family")
    if artifact.get("source_identity", {}).get("source_id") != index.get("source_id"):
        raise ValueError("source identity mismatch")
    if artifact.get("source_identity", {}).get("currentness_claim") is not False:
        raise ValueError("item-body assurance must not claim currentness")

    documents = artifact.get("source_identity", {}).get("documents", [])
    urls = [row.get("url") for row in documents]
    hashes = [row.get("sha256") for row in documents]
    if urls != day_meta.get("source_urls") or hashes != day_meta.get("source_sha256"):
        raise ValueError("assurance source identity does not match pinned unit-price source")
    if urls != region_meta.get("source_urls") or hashes != region_meta.get("source_sha256"):
        raise ValueError("assurance source identity does not match regional assignment source")

    index_profiles = {row["profile_id"]: row for row in index.get("multiplier_profiles", [])}
    assurance_profiles = {row["profile_id"]: row for row in artifact.get("profile_verification", [])}
    if set(index_profiles) != set(assurance_profiles):
        raise ValueError("profile set mismatch")

    for profile_id, expected in index_profiles.items():
        actual = assurance_profiles[profile_id]
        if actual.get("verification_state") != "PASS":
            raise ValueError(f"{profile_id}: profile is not directly verified PASS")
        if actual.get("verification_method") != "DIRECT_OFFICIAL_TABLE_REPARSE":
            raise ValueError(f"{profile_id}: unsupported verification method")
        if actual.get("official_service_names") != expected.get("official_service_names"):
            raise ValueError(f"{profile_id}: official service names differ")
        expected_rows = [
            (row.get("region_class"), row.get("ratio_per_thousand"), row.get("unit_price_yen"))
            for row in expected.get("rows", [])
        ]
        actual_rows = [
            (row.get("region_class"), row.get("ratio_per_thousand"), row.get("unit_price_yen"))
            for row in actual.get("rows", [])
        ]
        if actual_rows != expected_rows:
            raise ValueError(f"{profile_id}: verified item rows differ from canonical profile")
        if actual.get("mapped_item_count") != len(expected_rows) or len(expected_rows) != 8:
            raise ValueError(f"{profile_id}: incomplete regional item set")

    manifest_ids = [row["service_id"] for row in manifest.get("services", [])]
    index_map = {row["service_id"]: row for row in index.get("service_mappings", [])}
    projections = artifact.get("service_projections", [])
    projection_ids = [row.get("service_id") for row in projections]
    if projection_ids != manifest_ids:
        raise ValueError("service projections must exactly follow service manifest")
    if set(index_map) != set(manifest_ids):
        raise ValueError("unit-price mappings must cover the service manifest exactly")

    pass_count = 0
    na_count = 0
    for projection in projections:
        service_id = projection["service_id"]
        mapping = index_map[service_id]
        state = projection.get("service_level_item_body")
        if state not in ALLOWED_ITEM_STATES:
            raise ValueError(f"{service_id}: invalid item-body state {state}")

        assurance = projection.get("assurance") or {}
        if assurance.get("automatic_promotion_allowed") is not False:
            raise ValueError(f"{service_id}: automatic promotion must remain disabled")

        if mapping.get("applicability") == "NOT_APPLICABLE":
            na_count += 1
            if service_id not in EXPECTED_NA or state != "NOT_APPLICABLE":
                raise ValueError(f"{service_id}: unsupported NOT_APPLICABLE projection")
            evidence = projection.get("evidence", [])
            locators = [
                str(row.get("locator"))
                for row in evidence
                if isinstance(row, dict)
            ]
            if not any(EXPECTED_NA[service_id] in locator for locator in locators):
                raise ValueError(f"{service_id}: missing explicit statutory purchase-benefit basis")
            continue

        if mapping.get("applicability") != "APPLIES":
            raise ValueError(f"{service_id}: unknown applicability")
        if state != "PASS":
            raise ValueError(f"{service_id}: applicable service lacks complete item-body PASS")
        pass_count += 1

        profile_id = projection.get("multiplier_profile_id")
        profile = assurance_profiles.get(profile_id)
        if not profile or profile.get("verification_state") != "PASS":
            raise ValueError(f"{service_id}: PASS is not backed by a PASS source profile")
        if projection.get("official_service_name") != mapping.get("official_service_name"):
            raise ValueError(f"{service_id}: official service identity differs")
        if projection.get("official_service_name") not in profile.get("official_service_names", []):
            raise ValueError(f"{service_id}: official service is absent from verified profile")
        if projection.get("mapped_item_count") != 8:
            raise ValueError(f"{service_id}: incomplete mapped node set")
        if assurance.get("currentness") != "NOT_ESTABLISHED":
            raise ValueError(f"{service_id}: item-body PASS must not promote currentness")
        if assurance.get("human_review") != "NOT_REVIEWED":
            raise ValueError(f"{service_id}: item-body PASS must not promote human review")
        if assurance.get("publication") != "UNCHANGED" or assurance.get("route_exposure") != "UNCHANGED":
            raise ValueError(f"{service_id}: item-body PASS must not promote publication or route")

    if pass_count != 37 or na_count != 2:
        raise ValueError(f"unexpected service result counts PASS={pass_count} NOT_APPLICABLE={na_count}")

    summary = artifact.get("summary") or {}
    expected_summary = {
        "applicable_services": 37,
        "pass": 37,
        "partial": 0,
        "not_established": 0,
        "not_applicable": 2,
    }
    if summary != expected_summary:
        raise ValueError(f"summary mismatch: {summary}")

    safety = artifact.get("safety") or {}
    for key in (
        "human_review_promoted",
        "currentness_promoted",
        "publication_promoted",
        "route_exposure_promoted",
        "automatic_promotion_allowed",
    ):
        if safety.get(key) is not False:
            raise ValueError(f"unsafe assurance flag: {key}")


def main() -> None:
    validate_payload(load(ARTIFACT), load(INDEX), load(MANIFEST), load(DAY_META), load(REGION_META))
    print("unit-price item-body assurance: PASS (37 applicable PASS, 2 explicit NOT_APPLICABLE; currentness unchanged)")


if __name__ == "__main__":
    main()
