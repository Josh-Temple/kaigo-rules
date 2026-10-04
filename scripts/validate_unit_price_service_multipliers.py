#!/usr/bin/env python3
"""Validate the shared national unit-price service multiplier index.

This validation proves repository structure and deterministic mappings only.
It does not promote item-body verification, currentness, human review,
publication, or route exposure.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "data" / "unit-price-service-multipliers.json"
MANIFEST = ROOT / "data" / "services" / "manifest.json"

REGIONS = ["一級地", "二級地", "三級地", "四級地", "五級地", "六級地", "七級地", "その他"]
EXPECTED_PROFILES = {
    "flat-1000": [1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000],
    "group-1090": [1090, 1072, 1068, 1054, 1045, 1027, 1014, 1000],
    "group-1110": [1110, 1088, 1083, 1066, 1055, 1033, 1017, 1000],
    "group-1140": [1140, 1112, 1105, 1084, 1070, 1042, 1021, 1000],
}
NOT_APPLICABLE_IDS = {
    "specific-welfare-equipment-sale",
    "specific-preventive-welfare-equipment-sale",
}

def fail(message: str) -> None:
    raise SystemExit("unit-price service multipliers invalid: " + message)

def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))

def main() -> None:
    data = load(INDEX)
    manifest = load(MANIFEST)

    if data.get("source_id") != "mhlw-unit-price-current":
        fail("unexpected source_id")
    if data.get("shared_region_assignments") != "data/unit-price-region-assignments.json":
        fail("shared region assignment path changed")

    profiles = {row["profile_id"]: row for row in data.get("multiplier_profiles", [])}
    if set(profiles) != set(EXPECTED_PROFILES):
        fail(f"profile set mismatch: {sorted(profiles)}")

    for profile_id, expected_rates in EXPECTED_PROFILES.items():
        rows = profiles[profile_id].get("rows", [])
        if [row.get("region_class") for row in rows] != REGIONS:
            fail(f"{profile_id}: region order/set mismatch")
        observed_rates = [row.get("ratio_per_thousand") for row in rows]
        if observed_rates != expected_rates:
            fail(f"{profile_id}: multiplier mismatch")
        for row in rows:
            rate = row["ratio_per_thousand"]
            if row.get("unit_price_yen") != rate / 100:
                fail(f"{profile_id}/{row.get('region_class')}: yen conversion mismatch")

    manifest_ids = [row["service_id"] for row in manifest.get("services", [])]
    mappings = data.get("service_mappings", [])
    mapping_ids = [row.get("service_id") for row in mappings]
    if mapping_ids != manifest_ids:
        fail("service mappings must exactly follow the current service manifest")

    observed_na = {
        row["service_id"]
        for row in mappings
        if row.get("applicability") == "NOT_APPLICABLE"
    }
    if observed_na != NOT_APPLICABLE_IDS:
        fail(f"NOT_APPLICABLE service set mismatch: {sorted(observed_na)}")

    applies = 0
    for row in mappings:
        applicability = row.get("applicability")
        if applicability == "NOT_APPLICABLE":
            if row.get("ingestion_status") != "NOT_APPLICABLE":
                fail(f"{row['service_id']}: non-applicable row must remain explicit")
            continue
        if applicability != "APPLIES":
            fail(f"{row['service_id']}: invalid applicability={applicability}")
        applies += 1
        if row.get("ingestion_status") != "INDEXED_CURRENT_MHLW_DISPLAY_NOT_SERVICE_VERIFIED":
            fail(f"{row['service_id']}: ingestion status must not imply verification")
        profile_id = row.get("multiplier_profile_id")
        profile = profiles.get(profile_id)
        if not profile:
            fail(f"{row['service_id']}: missing multiplier profile")
        if row.get("official_service_name") not in profile.get("official_service_names", []):
            fail(f"{row['service_id']}: official service name not present in profile group")

    if applies != 37:
        fail(f"expected 37 applicable services, got {applies}")

    day = load(ROOT / "data" / "unit-price-dayservice.json")
    homevisit = load(ROOT / "data" / "unit-price-homevisit.json")
    if [row["ratio_per_thousand"] for row in day] != EXPECTED_PROFILES["group-1090"]:
        fail("existing dayservice rates drifted from shared profile")
    if [row["ratio_per_thousand"] for row in homevisit] != EXPECTED_PROFILES["group-1140"]:
        fail("existing homevisit rates drifted from shared profile")

    if data.get("assurance", {}).get("automatic_promotion_allowed") is not False:
        fail("automatic promotion must remain disabled")

    print("unit-price service multipliers: PASS (37 applicable, 2 explicit NOT_APPLICABLE)")

if __name__ == "__main__":
    main()
