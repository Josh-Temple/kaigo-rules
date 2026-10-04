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
CORPUS = BASE / "national-corpus.json"
IDENTITY_MAP = BASE / "source-identity-map.json"
APPLICABILITY = BASE / "service-applicability.json"
RECEIPTS = BASE / "source-observation-receipts.json"
SERVICES = ROOT / "data/services/manifest.json"
SOURCES = ROOT / "data/sources.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _source_rows(doc):
    return doc if isinstance(doc, list) else doc.get("sources", [])


def validate() -> list[str]:
    errors: list[str] = []
    manifest = load(MANIFEST)
    registry = load(REGISTRY)
    audit = load(AUDIT)
    corpus = load(CORPUS)
    identity_map = load(IDENTITY_MAP)
    applicability = load(APPLICABILITY)
    receipts = load(RECEIPTS)
    service_manifest = load(SERVICES)
    source_registry = load(SOURCES)

    family = "other_national_manuals_forms"
    for name, doc in (
        ("manifest", manifest),
        ("registry", registry),
        ("audit", audit),
        ("corpus", corpus),
        ("applicability", applicability),
        ("receipts", receipts),
    ):
        if doc.get("source_family") != family:
            errors.append(f"{name} source_family mismatch")

    if manifest.get("corpus_id") != "other-national-materials-national":
        errors.append("manifest corpus_id mismatch")
    if corpus.get("corpus_id") != manifest.get("corpus_id"):
        errors.append("corpus_id mismatch between manifest and corpus")
    if manifest.get("foundation_state") != "CANONICAL_SHARED_CORPUS_ESTABLISHED_NOT_PROJECTED":
        errors.append("manifest foundation_state is not canonical/not-projected")
    if manifest.get("canonical_node_store") != "data/shared/other-national-materials/national-corpus.json":
        errors.append("manifest canonical_node_store mismatch")

    policies = manifest.get("policies", {})
    for key in (
        "service_body_duplication_allowed",
        "service_applicability_inference_allowed",
        "automatic_verification_promotion_allowed",
        "automatic_currentness_promotion_allowed",
        "automatic_human_review_promotion_allowed",
        "automatic_publication_promotion_allowed",
        "automatic_route_promotion_allowed",
        "global_coverage_matrix_regeneration_by_worker_b_allowed",
    ):
        if policies.get(key) is not False:
            errors.append(f"unsafe policy: {key} must be false")

    allowed_hosts = set(registry.get("allowed_official_hosts", []))
    registry_rows = registry.get("sources", [])
    registry_ids = [row.get("candidate_id") for row in registry_rows]
    if len(registry_ids) != len(set(registry_ids)):
        errors.append("duplicate candidate_id in discovery/canonical registry")

    accepted = {
        row["candidate_id"]
        for row in registry_rows
        if row.get("classification") == "ACCEPTED_OTHER_NATIONAL_MATERIAL"
    }
    if not accepted:
        errors.append("no accepted source remains in registry")

    corpus_rows = corpus.get("sources", [])
    corpus_candidates = {row.get("candidate_id") for row in corpus_rows}
    identity_rows = identity_map.get("identities", [])
    identity_candidates = {row.get("candidate_id") for row in identity_rows}
    receipt_rows = receipts.get("receipts", [])
    receipt_candidates = {row.get("candidate_id") for row in receipt_rows}

    if corpus_candidates != accepted:
        errors.append("canonical corpus candidate set must equal accepted candidate set")
    if identity_candidates != accepted:
        errors.append("identity-map candidate set must equal accepted candidate set")
    if receipt_candidates != accepted:
        errors.append("observation-receipt candidate set must equal accepted candidate set")

    nonaccepted = {
        row["candidate_id"]
        for row in registry_rows
        if row.get("classification") != "ACCEPTED_OTHER_NATIONAL_MATERIAL"
    }
    if nonaccepted & corpus_candidates:
        errors.append("duplicate/out-of-scope/discovery-only source was canonically promoted")

    canonical_source_ids = [row.get("source_id") for row in corpus_rows]
    canonical_node_ids = [row.get("id") for row in corpus_rows]
    if len(canonical_source_ids) != len(set(canonical_source_ids)):
        errors.append("duplicate canonical source_id")
    if len(canonical_node_ids) != len(set(canonical_node_ids)):
        errors.append("duplicate canonical node id")

    source_rows = _source_rows(source_registry)
    source_ids = [row.get("id") for row in source_rows]
    if len(source_ids) != len(set(source_ids)):
        errors.append("duplicate id in data/sources.json")
    missing_source_ids = sorted(set(canonical_source_ids) - set(source_ids))
    if missing_source_ids:
        errors.append(f"canonical source IDs missing from data/sources.json: {missing_source_ids}")

    receipt_by_id = {row.get("id"): row for row in receipt_rows}
    for row in registry_rows:
        cid = row.get("candidate_id", "<missing>")
        host = urlparse(row.get("official_url", "")).hostname
        if host not in allowed_hosts:
            errors.append(f"{cid}: non-official or unapproved host {host}")

        if cid in accepted:
            if row.get("acquisition_state") != "CANONICAL_LOCATOR_EVIDENCE_PINNED":
                errors.append(f"{cid}: accepted source not promoted to canonical locator evidence")
            if not row.get("canonical_source_id") or not row.get("canonical_node_id"):
                errors.append(f"{cid}: accepted source missing canonical identity")
            if row.get("projection_ready") is not True:
                errors.append(f"{cid}: accepted canonical source should be ready for Worker E projection")
            evidence = row.get("durable_evidence") or {}
            receipt_id = evidence.get("receipt_id")
            if receipt_id not in receipt_by_id:
                errors.append(f"{cid}: durable-evidence receipt missing")
            if evidence.get("source_bytes_sha256") is not None:
                errors.append(f"{cid}: source bytes hash must not be invented")
            if evidence.get("source_bytes_state") != "NOT_CAPTURED_IN_THIS_WORKER":
                errors.append(f"{cid}: source byte capture state must stay explicit")
        else:
            if row.get("projection_ready") is not False:
                errors.append(f"{cid}: nonaccepted source must not be projection-ready")
            if row.get("canonical_source_id") is not None or row.get("canonical_node_id") is not None:
                errors.append(f"{cid}: nonaccepted source has canonical identity")

    for row in corpus_rows:
        cid = row.get("candidate_id", "<missing>")
        if row.get("body_duplicated") is not False:
            errors.append(f"{cid}: service/source body duplication is forbidden")
        if row.get("content_mode") != "REFERENCE_ONLY":
            errors.append(f"{cid}: canonical corpus must stay reference-only in this worker")
        assurance = row.get("assurance") or {}
        if assurance.get("item_body_verification") != "NOT_ESTABLISHED":
            errors.append(f"{cid}: item-body verification was overpromoted")
        if assurance.get("human_review") != "NOT_REVIEWED":
            errors.append(f"{cid}: human review was overpromoted")
        if assurance.get("publication") != "BLOCKED" or assurance.get("route_exposure") != "BLOCKED":
            errors.append(f"{cid}: publication/route was overpromoted")

    evidence_policy = receipts.get("evidence_policy") or {}
    if evidence_policy.get("locator_receipt_does_not_establish_item_body_verification") is not True:
        errors.append("receipt policy must keep locator evidence separate from item-body verification")
    if evidence_policy.get("locator_receipt_does_not_establish_global_currentness_pass") is not True:
        errors.append("receipt policy must keep locator evidence separate from global currentness PASS")

    for row in receipt_rows:
        rid = row.get("id", "<missing>")
        host = urlparse(row.get("official_landing_url", "")).hostname
        if host not in allowed_hosts:
            errors.append(f"{rid}: unapproved landing host {host}")
        if not row.get("native_locator"):
            errors.append(f"{rid}: missing native locator")
        if not row.get("durable_evidence_mode"):
            errors.append(f"{rid}: missing durable evidence mode")
        if row.get("source_bytes_sha256") is not None:
            errors.append(f"{rid}: source bytes hash is present without captured bytes")
        if row.get("source_bytes_state") != "NOT_CAPTURED_IN_THIS_WORKER":
            errors.append(f"{rid}: source bytes state is not explicit")
        currentness = row.get("currentness") or {}
        if currentness.get("state") not in {"PARTIAL", "NOT_ESTABLISHED"}:
            errors.append(f"{rid}: currentness is overclaimed")
        for artifact in row.get("artifacts", []):
            artifact_host = urlparse(artifact.get("url", "")).hostname
            if artifact_host not in allowed_hosts:
                errors.append(f"{rid}: unapproved artifact host {artifact_host}")
            if not artifact.get("locator"):
                errors.append(f"{rid}: artifact missing source-native locator")

    service_ids = [row["service_id"] for row in service_manifest.get("services", [])]
    service_set = set(service_ids)
    app_rows = {row["canonical_source_id"]: row for row in applicability.get("sources", [])}
    if set(app_rows) != set(canonical_source_ids):
        errors.append("service-applicability source set must equal canonical source set")

    for source_id, row in app_rows.items():
        mapped = set(row.get("mapped_service_ids", []))
        conditional_raw = row.get("conditional_service_ids", [])
        conditional = {
            item if isinstance(item, str) else item.get("service_id")
            for item in conditional_raw
        }
        na_raw = row.get("not_applicable_service_ids", [])
        not_applicable = {
            item if isinstance(item, str) else item.get("service_id")
            for item in na_raw
        }
        referenced = mapped | conditional | not_applicable
        unknown = sorted(referenced - service_set)
        if unknown:
            errors.append(f"{source_id}: unknown service IDs {unknown}")
        if mapped & conditional or mapped & not_applicable or conditional & not_applicable:
            errors.append(f"{source_id}: mapped/conditional/not-applicable sets overlap")

    forms = app_rows.get("mhlw-application-forms", {})
    if forms.get("state") != "MAPPED_PRIMARY_SOURCE":
        errors.append("application forms must retain explicit primary-source mapping state")
    if set(forms.get("mapped_service_ids", [])) != service_set:
        errors.append("application forms mapping must match the 39 service types explicitly listed in official forms")

    operator = app_rows.get("mhlw-electronic-application-operator-manual-v2-50", {})
    if operator.get("state") != "NOT_ESTABLISHED" or operator.get("mapped_service_ids") != []:
        errors.append("electronic-application operator manual applicability must remain unestablished")

    accident = app_rows.get("mhlw-accident-report-vol1332", {})
    if accident.get("state") != "PARTIAL_EXPLICIT_TARGET":
        errors.append("accident-report scope must stay partial/explicit-target")
    required_accident = {
        "elderly-welfare-facility",
        "elderly-health-facility",
        "care-medical-institution",
        "dementia-group-home",
        "preventive-dementia-group-home",
        "specific-facility",
        "community-specific-facility",
        "preventive-specific-facility",
    }
    if set(accident.get("mapped_service_ids", [])) != required_accident:
        errors.append("accident-report target mapping does not match explicit primary-source target categories")

    financial = app_rows.get("mhlw-care-business-financial-db-manual-v1-20", {})
    financial_mapped = set(financial.get("mapped_service_ids", []))
    financial_conditional = {x.get("service_id") for x in financial.get("conditional_service_ids", [])}
    financial_na = {x.get("service_id") for x in financial.get("not_applicable_service_ids", [])}
    if financial_mapped | financial_conditional | financial_na != service_set:
        errors.append("financial DB service table must partition all repository service IDs without inference gaps")
    if financial_na != {"homecaremanagement", "preventive-homecaremanagement", "preventive-support"}:
        errors.append("financial DB explicit not-applicable service set mismatch")

    expected_counts = Counter(row["classification"] for row in registry_rows)
    if audit.get("summary") != dict(sorted(expected_counts.items())):
        errors.append("audit classification counts mismatch")
    if audit.get("accepted_source_count") != len(accepted):
        errors.append("audit accepted_source_count mismatch")
    if audit.get("canonical_promotion", {}).get("canonical_source_count") != len(corpus_rows):
        errors.append("audit canonical_source_count mismatch")
    if audit.get("canonical_promotion", {}).get("duplicate_or_out_of_scope_promoted") != 0:
        errors.append("audit indicates a duplicate/out-of-scope promotion")
    if audit.get("canonical_promotion", {}).get("global_generated_artifacts_regenerated") is not False:
        errors.append("Worker B must not claim global generated artifact regeneration")

    currentness_counts = Counter(row.get("currentness_state") for row in registry_rows)
    if audit.get("currentness_not_established_count") != currentness_counts.get("NOT_ESTABLISHED", 0):
        errors.append("audit currentness NOT_ESTABLISHED count mismatch")
    if audit.get("currentness_partial_count") != currentness_counts.get("PARTIAL", 0):
        errors.append("audit currentness PARTIAL count mismatch")

    app_counts = Counter(row.get("applicability", {}).get("state") for row in registry_rows)
    if audit.get("service_applicability_not_established_count") != app_counts.get("NOT_ESTABLISHED", 0):
        errors.append("audit applicability NOT_ESTABLISHED count mismatch")
    if audit.get("service_applicability_promoted_count") != len(registry_rows) - app_counts.get("NOT_ESTABLISHED", 0):
        errors.append("audit promoted applicability count mismatch")

    return errors


def main() -> int:
    errors = validate()
    if errors:
        for error in errors:
            print("FAIL other-national-materials:", error)
        return 1

    registry = load(REGISTRY)
    accepted = sum(
        row.get("classification") == "ACCEPTED_OTHER_NATIONAL_MATERIAL"
        for row in registry.get("sources", [])
    )
    print(
        "PASS other-national-materials: "
        f"{accepted} accepted sources canonically promoted; "
        "service applicability remains evidence-scoped; "
        "item-body/currentness/human-review/publication/route gates remain fail-closed"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
