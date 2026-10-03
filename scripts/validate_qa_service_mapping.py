#!/usr/bin/env python3
"""Validate the MHLW Q&A service taxonomy and Kaigo Rules mapping.

This validator is intentionally fail-closed:
- it does not infer new service IDs,
- it does not expand shared Q&A groups to individual services,
- it does not promote verification/currentness state.
"""

from __future__ import annotations

import json
import re
import unicodedata
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
MAPPING_PATH = DATA / "qa-service-mapping.json"
META_PATH = DATA / "qa-corpus-meta.json"
CORPUS_PATH = DATA / "qa-corpus.json"
MANIFEST_PATH = DATA / "services" / "manifest.json"
CATALOG_PATH = DATA / "services" / "catalog.generated.json"

ALLOWED_CLASSIFICATIONS = {
    "INDIVIDUAL_SERVICE",
    "SHARED_COMMON_CATEGORY",
    "HISTORICAL_ABOLISHED_SERVICE",
    "REMUNERATION_ONLY_THEME",
    "OTHER_SPECIAL",
}
EXPECTED_CLASSIFICATION_CODES = {
    "SHARED_COMMON_CATEGORY": {"01", "02", "03", "04", "05", "06"},
    "HISTORICAL_ABOLISHED_SERVICE": {"26"},
    "REMUNERATION_ONLY_THEME": {"50"},
    "OTHER_SPECIAL": {"27", "51"},
}
EXPECTED_EXISTING_MAPPINGS = {
    "11": "homevisit",
    "12": "homebath",
    "13": "homenursing",
    "14": "homerehab",
    "15": "homecaremanagement",
    "16": "dayservice",
    "17": "dayrehab",
    "18": "shortstay-life",
    "23": "care-management",
    "40": "regular-round",
    "41": "night-homevisit",
    "48": "community-dayservice",
    "XX": "preventive-support",
    "19": "shortstay-medical",
    "20": "specific-facility",
    "21": "welfare-equipment-rental",
    "22": "specific-welfare-equipment-sale",
    "24": "elderly-welfare-facility",
    "25": "elderly-health-facility",
    "42": "dementia-dayservice",
    "43": "small-scale-multifunctional",
    "44": "dementia-group-home",
    "45": "community-specific-facility",
    "46": "community-elderly-facility",
    "47": "nursing-small-scale-multifunctional",
    "49": "care-medical-institution",
}
EXPECTED_PENDING_CODES = set()


def fail(message: str) -> None:
    raise SystemExit("Q&A service mapping validation failed: " + message)


def load(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        fail(f"cannot read valid JSON from {path.relative_to(ROOT)}: {exc}")


def normalize_raw_label(value: str) -> str:
    text = unicodedata.normalize("NFKC", str(value or ""))
    text = re.sub(r"[.．]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def main() -> None:
    mapping = load(MAPPING_PATH)
    meta = load(META_PATH)
    corpus = load(CORPUS_PATH)
    manifest = load(MANIFEST_PATH)
    catalog = load(CATALOG_PATH)

    if mapping.get("format_version") != 1:
        fail("unexpected mapping format_version")
    if mapping.get("purpose") != "MHLW_QA_SHARED_CORPUS_SERVICE_MAPPING":
        fail("unexpected mapping purpose")

    policy = mapping.get("policy", {})
    required_false_promotions = (
        policy.get("verification_state_is_not_promoted") is True
        and policy.get("currentness_state_is_not_promoted") is True
        and policy.get("unresolved_new_service_ids_remain_unresolved") is True
        and policy.get("noncanonical_row_labels_are_not_auto_expanded") is True
    )
    if not required_false_promotions:
        fail("fail-closed mapping policy is incomplete")

    entries = mapping.get("codes")
    if not isinstance(entries, list):
        fail("codes must be a list")
    codes = [entry.get("service_code") for entry in entries]
    if len(codes) != len(set(codes)):
        fail("duplicate service_code in mapping")
    if codes != meta.get("target_service_codes"):
        fail("mapping code inventory/order differs from qa-corpus-meta target_service_codes")
    if set(codes) != {row.get("service_code") for row in corpus}:
        fail("mapping code inventory differs from committed corpus")

    by_code = {entry["service_code"]: entry for entry in entries}
    actual_counts = Counter(row.get("service_code") for row in corpus)
    meta_counts = meta.get("counts_by_service", {})
    if dict(actual_counts) != meta_counts:
        fail("corpus counts differ from qa-corpus-meta")

    classification_counts = Counter()
    variant_total = 0
    for code, entry in by_code.items():
        classification = entry.get("classification")
        if classification not in ALLOWED_CLASSIFICATIONS:
            fail(f"unsupported classification for {code}: {classification}")
        classification_counts[classification] += 1

        if entry.get("official_label") != meta.get("scope_by_code", {}).get(code):
            fail(f"official label mismatch for {code}")
        if entry.get("corpus_rows") != actual_counts[code]:
            fail(f"corpus row count mismatch for {code}")

        rows = [row for row in corpus if row.get("service_code") == code]
        canonical_raw = normalize_raw_label(f"{code} {entry['official_label']}")
        variant_counter = Counter(
            row.get("service_label", "")
            for row in rows
            if normalize_raw_label(row.get("service_label", "")) != canonical_raw
        )
        canonical_rows = len(rows) - sum(variant_counter.values())
        row_scope = entry.get("row_scope", {})
        if row_scope.get("canonical_raw_label_rows") != canonical_rows:
            fail(f"canonical raw-label row count mismatch for {code}")
        if row_scope.get("qualified_or_variant_raw_label_rows") != sum(variant_counter.values()):
            fail(f"variant raw-label row count mismatch for {code}")
        recorded_variants = {
            item.get("raw_label"): item.get("count")
            for item in row_scope.get("raw_label_variants", [])
        }
        if recorded_variants != dict(variant_counter):
            fail(f"raw-label variants mismatch for {code}")
        variant_total += sum(variant_counter.values())

        catalog_mapping = entry.get("catalog_mapping", {})
        state = catalog_mapping.get("state")
        service_id = catalog_mapping.get("service_id")
        if classification == "SHARED_COMMON_CATEGORY":
            relation = entry.get("scope_relation", {})
            if relation.get("kind") != "GROUP" or not relation.get("group_id"):
                fail(f"shared category {code} lacks group relation")
            if relation.get("membership_state") != "EXPLICIT_RELATION_MODEL":
                fail(f"shared category {code} does not point to explicit membership relations")
            if relation.get("relation_model") != "data/qa-group-relations.json":
                fail(f"shared category {code} has wrong external relation model")
            if service_id is not None:
                fail(f"shared category {code} must not have service_id")
        elif classification == "INDIVIDUAL_SERVICE":
            if code in EXPECTED_EXISTING_MAPPINGS:
                if state != "MAPPED_CURRENT_CATALOG":
                    fail(f"existing individual service {code} is not mapped")
                if service_id != EXPECTED_EXISTING_MAPPINGS[code]:
                    fail(f"existing service ID mismatch for {code}")
            elif code in EXPECTED_PENDING_CODES:
                if state != "PENDING_PARALLEL_SERVICE_CATALOG" or service_id is not None:
                    fail(f"pending service {code} must remain unresolved")
                proposal = catalog_mapping.get("proposed_mapping", {})
                if proposal.get("mhlw_qa_service_code") != code:
                    fail(f"pending service {code} lacks code-based proposed mapping")
                if proposal.get("official_label") != entry.get("official_label"):
                    fail(f"pending service {code} lacks label-based proposed mapping")
                if "proposed_service_id" in proposal:
                    fail(f"pending service {code} must not guess a service_id")
            else:
                fail(f"individual service {code} is neither mapped nor explicitly pending")
        elif service_id is not None:
            fail(f"non-individual classification {code} must not have current service_id")

    for classification, expected_codes in EXPECTED_CLASSIFICATION_CODES.items():
        observed = {code for code, entry in by_code.items() if entry["classification"] == classification}
        if observed != expected_codes:
            fail(f"{classification} code set differs from audited taxonomy")

    observed_individual = {
        code for code, entry in by_code.items()
        if entry["classification"] == "INDIVIDUAL_SERVICE"
    }
    if observed_individual != set(EXPECTED_EXISTING_MAPPINGS) | EXPECTED_PENDING_CODES:
        fail("individual-service code set differs from audited taxonomy")

    manifest_ids = {service["service_id"] for service in manifest.get("services", [])}
    catalog_ids = {service["service_id"] for service in catalog.get("services", [])}
    if manifest_ids != catalog_ids:
        fail("manifest and generated catalog service IDs differ before Q&A mapping")
    mapped_ids = {
        entry["catalog_mapping"]["service_id"]
        for entry in entries
        if entry["catalog_mapping"].get("state") == "MAPPED_CURRENT_CATALOG"
    }
    expected_mapped_ids = set(EXPECTED_EXISTING_MAPPINGS.values())
    if mapped_ids != expected_mapped_ids:
        fail("mapped Q&A individual-service IDs differ from the audited mapping")
    if not mapped_ids.issubset(manifest_ids):
        fail("Q&A mapping references a service outside the current manifest")

    summary = mapping.get("summary", {})
    expected_summary_counts = dict(classification_counts)
    if summary.get("corpus_rows") != len(corpus):
        fail("summary corpus_rows mismatch")
    if summary.get("observed_service_codes") != len(entries):
        fail("summary observed_service_codes mismatch")
    if summary.get("classification_counts") != expected_summary_counts:
        fail("summary classification_counts mismatch")
    if summary.get("mapped_existing_service_ids") != len(mapped_ids):
        fail("summary mapped_existing_service_ids mismatch")
    if summary.get("pending_parallel_catalog_service_codes") != len(EXPECTED_PENDING_CODES):
        fail("summary pending catalog count mismatch")
    if summary.get("rows_with_qualified_or_variant_raw_service_label") != variant_total:
        fail("summary raw-label variant count mismatch")

    snapshot = mapping.get("current_catalog_snapshot", {})
    if set(snapshot.get("manifest_service_ids", [])) != manifest_ids:
        fail("manifest snapshot does not match current manifest")
    if set(snapshot.get("generated_catalog_service_ids", [])) != catalog_ids:
        fail("catalog snapshot does not match current generated catalog")

    print(
        "Q&A service mapping: OK "
        f"({len(corpus):,} rows / {len(entries)} codes / "
        f"{classification_counts['INDIVIDUAL_SERVICE']} individual / "
        f"{classification_counts['SHARED_COMMON_CATEGORY']} shared / "
        f"{len(mapped_ids)} mapped / {len(EXPECTED_PENDING_CODES)} pending / "
        f"{variant_total} qualified-or-variant raw-label rows)"
    )


if __name__ == "__main__":
    main()
