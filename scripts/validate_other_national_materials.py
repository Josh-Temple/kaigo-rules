#!/usr/bin/env python3
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "data/shared/other-national-materials"
MANIFEST = BASE / "manifest.json"
REGISTRY = BASE / "source-registry.json"
AUDIT = BASE / "classification-audit.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def validate() -> list[str]:
    errors: list[str] = []
    manifest = load(MANIFEST)
    registry = load(REGISTRY)
    audit = load(AUDIT)

    if manifest.get("source_family") != "other_national_manuals_forms":
        errors.append("manifest source_family mismatch")
    if registry.get("source_family") != "other_national_manuals_forms":
        errors.append("registry source_family mismatch")
    if audit.get("source_family") != "other_national_manuals_forms":
        errors.append("audit source_family mismatch")

    policies = manifest.get("policies", {})
    required_false = (
        "service_body_duplication_allowed",
        "service_applicability_inference_allowed",
        "discovery_implies_corpus_available",
        "discovery_implies_scope_defined",
        "discovery_implies_ingested",
        "automatic_verification_promotion_allowed",
        "automatic_currentness_promotion_allowed",
        "automatic_human_review_promotion_allowed",
        "automatic_publication_promotion_allowed",
        "automatic_route_promotion_allowed",
        "global_coverage_matrix_regeneration_by_worker_d_allowed",
    )
    for key in required_false:
        if policies.get(key) is not False:
            errors.append(f"unsafe policy: {key} must be false")

    allowed_classifications = set(manifest.get("classification_values", []))
    existing_families = set(manifest.get("existing_source_families", []))
    allowed_hosts = set(registry.get("allowed_official_hosts", []))
    rows = registry.get("sources", [])
    ids = [row.get("candidate_id") for row in rows]

    if not rows:
        errors.append("source registry is empty")
    if len(ids) != len(set(ids)):
        errors.append("duplicate candidate_id")

    required_fields = (
        "candidate_id",
        "title",
        "issuing_authority",
        "official_url",
        "evidence_locator",
        "document_kind",
        "acquisition_state",
        "classification",
        "currentness_state",
        "applicability",
        "projection_ready",
    )
    accepted = 0
    duplicates = 0

    for row in rows:
        cid = row.get("candidate_id", "<missing>")
        for key in required_fields:
            if key not in row:
                errors.append(f"{cid}: missing {key}")

        classification = row.get("classification")
        if classification not in allowed_classifications:
            errors.append(f"{cid}: unknown classification {classification}")

        host = urlparse(row.get("official_url", "")).hostname
        if host not in allowed_hosts:
            errors.append(f"{cid}: non-official or unapproved host {host}")

        if row.get("acquisition_state") != "OFFICIAL_SOURCE_LOCATED_NOT_SNAPSHOTTED":
            errors.append(f"{cid}: acquisition state unexpectedly promoted")

        sha = row.get("snapshot_sha256")
        if sha is not None and (
            len(sha) != 64
            or any(ch not in "0123456789abcdef" for ch in sha.lower())
        ):
            errors.append(f"{cid}: invalid snapshot_sha256")

        if row.get("currentness_state") != "NOT_ESTABLISHED":
            errors.append(f"{cid}: currentness must remain NOT_ESTABLISHED in discovery wave")

        app = row.get("applicability", {})
        if app.get("state") != "NOT_ESTABLISHED" or app.get("service_ids") != []:
            errors.append(f"{cid}: service applicability must remain unestablished and unmapped")

        if row.get("projection_ready") is not False:
            errors.append(f"{cid}: discovery candidate must not be projection-ready")

        if classification == "ACCEPTED_OTHER_NATIONAL_MATERIAL":
            accepted += 1
            if row.get("overlap_source_family") is not None:
                errors.append(f"{cid}: accepted candidate cannot overlap an existing source family")
            if "厚生労働省" not in row.get("issuing_authority", ""):
                errors.append(f"{cid}: accepted candidate authority is not national/MHLW")

        if classification == "DUPLICATE_OF_EXISTING_SOURCE_FAMILY":
            duplicates += 1
            overlap = row.get("overlap_source_family")
            if overlap not in existing_families:
                errors.append(f"{cid}: duplicate classification lacks valid existing source family")

    if accepted == 0:
        errors.append("no accepted Other National candidate")
    if duplicates == 0:
        errors.append("no duplicate-source-family classification")

    checks = audit.get("checks", [])
    audit_by_id = {row.get("candidate_id"): row for row in checks}
    if set(audit_by_id) != set(ids):
        errors.append("classification audit candidate set mismatch")

    for row in rows:
        check = audit_by_id.get(row["candidate_id"], {})
        if check.get("classification") != row.get("classification"):
            errors.append(f"{row['candidate_id']}: audit classification mismatch")
        if check.get("overlap_source_family") != row.get("overlap_source_family"):
            errors.append(f"{row['candidate_id']}: audit overlap mismatch")
        if check.get("projection_ready") is not False:
            errors.append(f"{row['candidate_id']}: audit projection flag promoted")

    expected_counts = Counter(row["classification"] for row in rows)
    if audit.get("summary") != dict(sorted(expected_counts.items())):
        errors.append("audit classification counts mismatch")
    if audit.get("accepted_source_count") != accepted:
        errors.append("audit accepted_source_count mismatch")
    if audit.get("duplicate_or_rejected_count") != len(rows) - accepted:
        errors.append("audit duplicate_or_rejected_count mismatch")
    if audit.get("currentness_not_established_count") != len(rows):
        errors.append("audit currentness count mismatch")
    if audit.get("service_applicability_not_established_count") != len(rows):
        errors.append("audit applicability count mismatch")

    return errors


def main() -> int:
    errors = validate()
    if errors:
        for error in errors:
            print("FAIL other-national-materials:", error)
        return 1

    rows = load(REGISTRY)["sources"]
    counts = Counter(row["classification"] for row in rows)
    print(
        "PASS other-national-materials: "
        f"{len(rows)} candidates, "
        f"{counts.get('ACCEPTED_OTHER_NATIONAL_MATERIAL', 0)} accepted, "
        f"{counts.get('DUPLICATE_OF_EXISTING_SOURCE_FAMILY', 0)} existing-family duplicates; "
        "fail-closed"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
