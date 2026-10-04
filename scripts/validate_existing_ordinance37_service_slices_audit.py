#!/usr/bin/env python3
"""Validate pinned audit evidence for existing Ordinance 37 service slices."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "data/verification/existing-ordinance37-service-slices-independent-audit.json"
LAYER = ROOT / "data/verification/layers/ordinance37-existing-services.json"
LAW_ID = "411M50000100037"
TARGETS = {
    "homevisit",
    "homebath",
    "homenursing",
    "homerehab",
    "homecaremanagement",
    "shortstay-life",
    "shortstay-medical",
    "specific-facility",
    "welfare-equipment-rental",
    "specific-welfare-equipment-sale",
}


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def git_blob_sha(path: Path) -> str:
    data = path.read_bytes()
    header = f"blob {len(data)}\0".encode()
    return hashlib.sha1(header + data).hexdigest()


def article_from_id(value: str) -> str:
    prefix = "ordinance37.article."
    if not value.startswith(prefix):
        raise ValueError(f"unexpected article id: {value}")
    return value[len(prefix):]


def main() -> None:
    audit = load(AUDIT)
    layer = load(LAYER)
    meta = load(ROOT / "data/ordinance37-meta.json")
    service_map = load(ROOT / "data/shared/standards/service-ordinance-map.json")

    errors: list[str] = []
    if audit.get("audit_result") != "PASS":
        errors.append("audit_result is not PASS")
    if audit.get("audit_kind") != "INDEPENDENT_EGOV_SERVICE_SLICE_REPARSE":
        errors.append("unexpected audit_kind")
    if audit.get("coverage") != {
        "services_total": 10,
        "services_pass": 10,
        "services_fail": 0,
        "articles_total": 177,
        "nodes_total": 1010,
        "discrepancies": 0,
    }:
        errors.append("audit coverage summary changed")

    source = audit.get("source", {})
    if source.get("law_id") != LAW_ID or meta.get("law_id") != LAW_ID:
        errors.append("Ordinance 37 law identity mismatch")
    if source.get("observed_xml_sha256") != source.get("committed_xml_sha256"):
        errors.append("live/committed XML hash mismatch in pinned audit")
    if source.get("committed_xml_sha256") != meta.get("xml_sha256"):
        errors.append("pinned XML hash no longer matches committed meta")
    if source.get("current_revision_id") != meta.get("current_revision", {}).get("law_revision_id"):
        errors.append("pinned revision id no longer matches committed meta")
    if not isinstance(audit.get("workflow_run_id"), int):
        errors.append("workflow_run_id missing")
    if not re.fullmatch(r"[0-9a-f]{40}", str(audit.get("verified_head_sha", ""))):
        errors.append("verified_head_sha invalid")

    for relative, expected_sha in audit.get("inputs", {}).items():
        path = ROOT / relative
        if not path.exists():
            errors.append(f"pinned input missing: {relative}")
            continue
        observed_sha = git_blob_sha(path)
        if observed_sha != expected_sha:
            errors.append(
                f"pinned input changed: {relative}: {observed_sha} != {expected_sha}"
            )

    rows = audit.get("services", [])
    row_ids = {row.get("service_id") for row in rows}
    if row_ids != TARGETS or len(rows) != len(TARGETS):
        errors.append("audited service set changed")

    mapped = {
        row.get("service_id"): row.get("corpus_id")
        for row in service_map.get("relations", [])
        if row.get("service_id") in TARGETS
    }
    if any(mapped.get(service_id) != "ordinance37" for service_id in TARGETS):
        errors.append("one or more audited services no longer map to ordinance37")

    home_index = load(ROOT / "data/services/homevisit/ordinance37-index.generated.json")
    for row in rows:
        service_id = row["service_id"]
        if row.get("result") != "PASS":
            errors.append(f"{service_id}: pinned result is not PASS")
        target = row.get("target_articles", [])
        if service_id == "homevisit":
            declared = home_index.get("selectors", {}).get("resolved_direct_articles", [])
        else:
            scope = load(ROOT / f"data/services/{service_id}/ordinance37-scope.json")
            declared = [
                article_from_id(value)
                for value in scope.get("direct_scope", {}).get("article_ids", [])
            ]
        if target != declared:
            errors.append(f"{service_id}: pinned article scope no longer matches canonical scope")
        if row.get("observed", {}).get("articles") != len(target):
            errors.append(f"{service_id}: pinned article count mismatch")

    safety = audit.get("safety", {})
    if safety.get("currentness_status") != "NOT_ESTABLISHED":
        errors.append("currentness must remain NOT_ESTABLISHED")
    if safety.get("human_review_status") != "NOT_REVIEWED":
        errors.append("human review must remain NOT_REVIEWED")
    for flag in (
        "publication_promoted",
        "route_exposure_promoted",
        "semantic_or_cross_layer_relations_audited",
        "automatic_promotion_allowed",
    ):
        if safety.get(flag) is not False:
            errors.append(f"safety flag must remain false: {flag}")

    if layer.get("id") != "ordinance37-existing-services":
        errors.append("normalized layer id mismatch")
    if layer.get("content_verification", {}).get("status") != "PASS":
        errors.append("normalized layer content verification is not PASS")
    if layer.get("currentness", {}).get("status") != "NOT_ESTABLISHED":
        errors.append("normalized layer currentness must remain NOT_ESTABLISHED")
    if layer.get("human_review", {}).get("status") != "NOT_REVIEWED":
        errors.append("normalized layer human review must remain NOT_REVIEWED")
    if layer.get("content_verification", {}).get("evidence") != str(AUDIT.relative_to(ROOT)):
        errors.append("normalized layer evidence path mismatch")

    if errors:
        raise SystemExit("\n".join(errors))
    print("existing Ordinance 37 service-slice audit: valid")


if __name__ == "__main__":
    main()
