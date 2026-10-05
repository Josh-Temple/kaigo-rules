#!/usr/bin/env python3
"""Build the shared delegated-remuneration corpus metadata without duplicating source text.

The legacy data/remuneration-delegated-nodes.json file remains the single
text-bearing store for backward compatibility. This builder adds stable,
service-neutral identities plus separate service applicability and relation
metadata. It never promotes verification/currentness/review/publication/route.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
SHARED = DATA / "shared" / "remuneration-delegated"

MANIFEST = SHARED / "manifest.json"
IDENTITY = SHARED / "node-identity-map.json"
APPLICABILITY = SHARED / "service-applicability.json"
SERVICE_RELATIONS = SHARED / "service-relations.json"

CORPUS_ID = "delegated-remuneration-national"

# Canonical service-fee expressions used only to identify explicit applicability
# in the official node heading. A shorter expression does not match when the
# same character span is contained inside a longer service expression.
SERVICE_HEADING_TERMS: dict[str, tuple[str, ...]] = {
    "dayservice": ("通所介護費",),
    "homevisit": ("訪問介護費",),
    "homebath": ("訪問入浴介護費",),
    "homenursing": ("訪問看護費",),
    "homerehab": ("訪問リハビリテーション費",),
    "homecaremanagement": ("居宅療養管理指導費",),
    "dayrehab": ("通所リハビリテーション費",),
    "shortstay-life": ("短期入所生活介護費",),
    "community-dayservice": ("地域密着型通所介護費",),
    "regular-round": ("定期巡回・随時対応型訪問介護看護費",),
    "night-homevisit": ("夜間対応型訪問介護費",),
    "care-management": ("居宅介護支援費",),
    "preventive-support": ("介護予防支援費",),
    "shortstay-medical": ("短期入所療養介護費",),
    "specific-facility": ("特定施設入居者生活介護費",),
    "welfare-equipment-rental": ("福祉用具貸与費",),
    "specific-welfare-equipment-sale": ("特定福祉用具販売",),
    "dementia-dayservice": ("認知症対応型通所介護費",),
    "small-scale-multifunctional": ("小規模多機能型居宅介護費",),
    "dementia-group-home": ("認知症対応型共同生活介護費",),
    "community-specific-facility": ("地域密着型特定施設入居者生活介護費",),
    "community-elderly-facility": (
        "地域密着型介護老人福祉施設入所者生活介護費",
        "地域密着型介護福祉施設サービス",
    ),
    "nursing-small-scale-multifunctional": (
        "看護小規模多機能型居宅介護費",
        "複合型サービス費",
    ),
    "elderly-welfare-facility": ("介護福祉施設サービス費", "介護福祉施設サービス"),
    "elderly-health-facility": ("介護保健施設サービス費", "介護保健施設サービス"),
    "care-medical-institution": ("介護医療院サービス費", "介護医療院サービス"),
    "preventive-homebath": ("介護予防訪問入浴介護費",),
    "preventive-homenursing": ("介護予防訪問看護費",),
    "preventive-homerehab": ("介護予防訪問リハビリテーション費",),
    "preventive-homecaremanagement": ("介護予防居宅療養管理指導費",),
    "preventive-dayrehab": ("介護予防通所リハビリテーション費",),
    "preventive-shortstay-life": ("介護予防短期入所生活介護費",),
    "preventive-shortstay-medical": ("介護予防短期入所療養介護費",),
    "preventive-specific-facility": ("介護予防特定施設入居者生活介護費",),
    "preventive-welfare-equipment-rental": ("介護予防福祉用具貸与費",),
    "specific-preventive-welfare-equipment-sale": ("特定介護予防福祉用具販売",),
    "preventive-dementia-dayservice": ("介護予防認知症対応型通所介護費",),
    "preventive-small-scale-multifunctional": ("介護予防小規模多機能型居宅介護費",),
    "preventive-dementia-group-home": ("介護予防認知症対応型共同生活介護費",),
}

ADJUDICATION_PATH = SHARED / "service-applicability-adjudications.json"
ITEM_BODY_VERIFICATION_PATH = SHARED / "item-body-verification.json"
ITEM_BODY_VERIFICATION_REF = "data/shared/remuneration-delegated/item-body-verification.json"


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def canonical_node_id(legacy_id: str) -> str:
    if legacy_id == "calc27.dayservice.1":
        return "notice27.item.1"
    if legacy_id.startswith("calc27.dayservice.1."):
        return "notice27.item.1." + legacy_id.removeprefix("calc27.dayservice.1.")
    if legacy_id.startswith("criteria95.dayservice."):
        return "notice95.item." + legacy_id.removeprefix("criteria95.dayservice.")
    if legacy_id.startswith("criteria95.shared."):
        return "notice95.item." + legacy_id.removeprefix("criteria95.shared.")
    raise ValueError(f"unmapped legacy delegated node id: {legacy_id}")


def _term_is_explicit_in_heading(heading: str, term: str, all_terms: tuple[str, ...]) -> bool:
    start = 0
    while True:
        index = heading.find(term, start)
        if index < 0:
            return False
        end = index + len(term)
        covered_by_longer = False
        for longer in all_terms:
            if len(longer) <= len(term):
                continue
            longer_start = 0
            while True:
                longer_index = heading.find(longer, longer_start)
                if longer_index < 0:
                    break
                if longer_index <= index and longer_index + len(longer) >= end:
                    covered_by_longer = True
                    break
                longer_start = longer_index + 1
            if covered_by_longer:
                break
        if not covered_by_longer:
            return True
        start = index + 1


def _direct_node_ids(
    national_nodes: list[dict[str, Any]],
    service_id: str,
) -> list[str]:
    all_terms = tuple(
        sorted(
            {term for terms in SERVICE_HEADING_TERMS.values() for term in terms},
            key=len,
            reverse=True,
        )
    )
    terms = SERVICE_HEADING_TERMS[service_id]
    return sorted({
        node["canonical_node_id"]
        for node in national_nodes
        if any(
            _term_is_explicit_in_heading(str(node.get("heading", "")), term, all_terms)
            for term in terms
        )
    })


def _incorporated_reference_ids(
    text: str,
    label_to_canonical: dict[str, str],
) -> list[str]:
    # Covers forms such as 第四十八号の規定を準用する and
    # 第三十七号の三の規定を準用する. Verification remains separate.
    pattern = re.compile(
        r"第([一二三四五六七八九十百]+)号"
        r"(?:の([一二三四五六七八九十百]+))?"
        r"[^。]{0,60}?の規定を準用する"
    )
    references: set[str] = set()
    for match in pattern.finditer(text):
        label = match.group(1)
        if match.group(2):
            label += "の" + match.group(2)
        canonical_id = label_to_canonical.get(label)
        if canonical_id:
            references.add(canonical_id)
    return sorted(references)


def _fail_closed_assurance() -> dict[str, Any]:
    return {
        "item_body_verification": "NOT_ESTABLISHED",
        "currentness": "NOT_ESTABLISHED",
        "relation_verification": "NOT_ESTABLISHED",
        "human_review": "NOT_REVIEWED",
        "publication": "BLOCKED",
        "route_exposure": "BLOCKED",
        "automatic_promotion_allowed": False,
    }


def _passed_item_body_sources(item_body_doc: dict[str, Any]) -> set[str]:
    rejected = {
        str(value).lower()
        for value in item_body_doc.get("projection_policy", {}).get(
            "historical_or_superseded_source_statuses_rejected", []
        )
    }
    return {
        str(row["source_id"])
        for row in item_body_doc.get("source_verifications", [])
        if row.get("result") == "PASS"
        and row.get("coverage_kind") == "ALL_CANONICAL_TOP_LEVEL_NODES_IN_SOURCE"
        and row.get("currentness_claimed") is False
        and str(row.get("repository_source_status", "")).lower() not in rejected
        and row.get("page_snapshots")
    }


def item_body_assurance_for_service(
    *,
    applicability_state: str,
    mapped_node_ids: list[str],
    compatibility_subnode_ids: list[str],
    national_by_id: dict[str, dict[str, Any]],
    item_body_doc: dict[str, Any],
) -> dict[str, Any]:
    """Project source-level body assurance without changing any other axis."""
    assurance = _fail_closed_assurance()
    if applicability_state != "MAPPED":
        return assurance

    passed_sources = _passed_item_body_sources(item_body_doc)
    passed_compatibility = {
        str(row["canonical_node_id"])
        for row in item_body_doc.get("compatibility_node_verifications", [])
        if row.get("result") == "PASS"
    }
    unsupported: list[str] = []
    for canonical_id in mapped_node_ids:
        node = national_by_id.get(canonical_id)
        if not node or str(node.get("source_id")) not in passed_sources:
            unsupported.append(canonical_id)
    for canonical_id in compatibility_subnode_ids:
        if canonical_id not in passed_compatibility:
            unsupported.append(canonical_id)

    required_count = len(mapped_node_ids) + len(compatibility_subnode_ids)
    if required_count and not unsupported:
        assurance["item_body_verification"] = "PASS"
        assurance["item_body_verified_node_count"] = required_count
        assurance["item_body_projection_evidence"] = [ITEM_BODY_VERIFICATION_REF]
    elif unsupported:
        assurance["item_body_projection_blockers"] = sorted(set(unsupported))
    return assurance


def build() -> dict[str, Any]:
    nodes = load(DATA / "remuneration-delegated-nodes.json")
    delegated_meta = load(DATA / "remuneration-delegated-meta.json")
    sources = load(DATA / "sources.json")
    relation_audit = load(DATA / "remuneration-delegation-relation-independent-audit.json")
    independent_audit = load(DATA / "remuneration-independent-audit.json")
    national_corpus = load(SHARED / "national-corpus.json")
    national_nodes = national_corpus.get("nodes", [])
    national_ids = {row["canonical_node_id"] for row in national_nodes}
    adjudication_doc = load(ADJUDICATION_PATH)
    item_body_doc = load(ITEM_BODY_VERIFICATION_PATH)
    adjudications = {
        row["service_id"]: row for row in adjudication_doc.get("adjudications", [])
    }

    identity_rows = []
    for node in nodes:
        legacy_id = node["id"]
        canonical_id = canonical_node_id(legacy_id)
        parent = (
            "notice27.item.1"
            if legacy_id in {"calc27.dayservice.1.capacity", "calc27.dayservice.1.staffing"}
            else None
        )
        identity_rows.append({
            "canonical_node_id": canonical_id,
            "legacy_node_id": legacy_id,
            "source_id": node["source_id"],
            "source_url": node["source_url"],
            "heading": node["heading"],
            "parent_canonical_node_id": parent,
            "source_locator": {"kind": "HEADING", "value": node["heading"]},
            "text_sha256": node["text_sha256"],
        })

    identity_rows.sort(key=lambda row: row["canonical_node_id"])
    canonical_ids = [row["canonical_node_id"] for row in identity_rows]
    legacy_ids = [row["legacy_node_id"] for row in identity_rows]
    if len(canonical_ids) != len(set(canonical_ids)):
        raise ValueError("duplicate canonical delegated node id")
    if len(legacy_ids) != len(set(legacy_ids)):
        raise ValueError("duplicate legacy delegated node id")

    catalog = load(DATA / "services" / "catalog.generated.json")
    catalog_service_ids = [row["service_id"] for row in catalog.get("services", [])]
    configured_service_ids = set(SERVICE_HEADING_TERMS)
    if set(catalog_service_ids) != configured_service_ids:
        missing = sorted(set(catalog_service_ids) - configured_service_ids)
        extra = sorted(configured_service_ids - set(catalog_service_ids))
        raise ValueError(
            f"delegated applicability service-term map drift: missing={missing}, extra={extra}"
        )

    passed_checks_by_target: dict[str, list[str]] = {}
    for check in relation_audit.get("checks", []):
        if check.get("result") != "PASS":
            continue
        passed_checks_by_target.setdefault(check["to_id"], []).append(check["id"])

    node_by_legacy = {node["id"]: node for node in nodes}
    national_by_id = {row["canonical_node_id"]: row for row in national_nodes}
    label_to_canonical_by_source: dict[str, dict[str, str]] = {}
    for row in national_nodes:
        if not row.get("item_label"):
            continue
        label_to_canonical_by_source.setdefault(str(row["source_id"]), {})[
            str(row["item_label"])
        ] = row["canonical_node_id"]

    legacy_text_by_canonical = {
        canonical_node_id(node["id"]): str(node.get("official_text", ""))
        for node in nodes
    }

    def node_text(canonical_id: str) -> str:
        row = national_by_id[canonical_id]
        if row.get("official_text"):
            return str(row["official_text"])
        return legacy_text_by_canonical.get(canonical_id, "")

    legacy_dayservice_relations: dict[str, dict[str, Any]] = {}
    for row in identity_rows:
        legacy_id = row["legacy_node_id"]
        legacy = node_by_legacy[legacy_id]
        legacy_dayservice_relations[row["canonical_node_id"]] = {
            "canonical_node_id": row["canonical_node_id"],
            "relation": (
                "INCORPORATED_BY_REFERENCE"
                if legacy_id == "criteria95.shared.4"
                else "DIRECT_APPLICABILITY"
            ),
            "verification_state": "NOT_ESTABLISHED",
            "basis": {
                "legacy_node_id": legacy_id,
                "legacy_service_scope": legacy.get("service_scope"),
            },
            "independently_verified_delegation_edge_ids": sorted(
                passed_checks_by_target.get(legacy_id, [])
            ),
        }

    legacy_dayservice_top_level = {
        row["canonical_node_id"]
        for row in identity_rows
        if row["canonical_node_id"] in national_ids
    }
    compatibility_subnode_ids = sorted(
        row["canonical_node_id"]
        for row in identity_rows
        if row["canonical_node_id"] not in national_ids
    )

    direct_by_service: dict[str, list[str]] = {}
    incorporated_by_service: dict[str, dict[str, list[str]]] = {}
    applicability_services: list[dict[str, Any]] = []
    relation_services: list[dict[str, Any]] = []
    adjudications_used: set[str] = set()

    for service_id in catalog_service_ids:
        direct_ids = set(_direct_node_ids(national_nodes, service_id))
        if service_id == "dayservice":
            direct_ids.update(
                canonical_id
                for canonical_id in legacy_dayservice_top_level
                if canonical_id != "notice95.item.4"
            )
        if not direct_ids and service_id in adjudications:
            decision = adjudications[service_id]
            state = decision["applicability_state"]
            if state not in {"NOT_APPLICABLE", "UNKNOWN"}:
                raise ValueError(f"unsupported explicit applicability state for {service_id}: {state}")
            if decision.get("mapped_node_ids") != []:
                raise ValueError(f"unmapped adjudication must not claim node IDs: {service_id}")
            evidence = decision.get("official_primary_sources", [])
            if not evidence or not decision.get("rationale"):
                raise ValueError(f"adjudication evidence/rationale missing: {service_id}")
            for source in evidence:
                if not source.get("url") or not source.get("locator"):
                    raise ValueError(f"adjudication primary-source locator missing: {service_id}")
            for reference in decision.get("repository_evidence", []):
                if not (ROOT / reference.split("#", 1)[0]).is_file():
                    raise ValueError(f"adjudication repository evidence missing: {service_id}: {reference}")
            adjudications_used.add(service_id)
            applicability_services.append({
                "service_id": service_id,
                "scope_state": "SCOPE_DEFINED",
                "applicability_state": state,
                "ingestion_state": "NOT_APPLICABLE" if state == "NOT_APPLICABLE" else "NOT_INGESTED",
                "mapped_node_count": 0,
                "mapped_node_ids": [],
                "compatibility_subnode_ids": [],
                "mapping_evidence": sorted({
                    "data/shared/remuneration-delegated/national-corpus.json",
                    f"{ADJUDICATION_PATH.relative_to(ROOT)}#{service_id}",
                    *decision.get("repository_evidence", []),
                }),
                "adjudication": decision,
                "assurance": _fail_closed_assurance(),
            })
            relation_services.append({
                "service_id": service_id,
                "relation_verification_state": "NOT_APPLICABLE" if state == "NOT_APPLICABLE" else "NOT_ESTABLISHED",
                "applicability_state": state,
                "adjudication_ref": f"{ADJUDICATION_PATH.relative_to(ROOT)}#{service_id}",
                "relations": [],
            })
            continue
        if not direct_ids:
            raise ValueError(f"service lacks explicit delegated applicability adjudication: {service_id}")

        direct_ids_sorted = sorted(direct_ids)
        reference_to_referrers: dict[str, set[str]] = {}
        for direct_id in direct_ids_sorted:
            direct_source_id = str(national_by_id[direct_id]["source_id"])
            for reference_id in _incorporated_reference_ids(
                node_text(direct_id),
                label_to_canonical_by_source.get(direct_source_id, {}),
            ):
                if reference_id in direct_ids:
                    continue
                reference_to_referrers.setdefault(reference_id, set()).add(direct_id)

        # Preserve the pre-existing dayservice incorporation edge even though its
        # compatibility evidence predates this heading-derived expansion.
        if service_id == "dayservice":
            reference_to_referrers.setdefault("notice95.item.4", set()).add(
                "notice95.item.24"
            )

        incorporated_by_service[service_id] = {
            canonical_id: sorted(referrers)
            for canonical_id, referrers in sorted(reference_to_referrers.items())
        }
        direct_by_service[service_id] = direct_ids_sorted

        mapped_node_ids = sorted(
            set(direct_ids_sorted) | set(reference_to_referrers)
        )
        mapping_evidence = [
            "data/shared/remuneration-delegated/national-corpus.json",
        ]
        if service_id == "dayservice":
            mapping_evidence.extend([
                "data/remuneration-delegated-nodes.json",
                "data/shared/remuneration-delegated/node-identity-map.json",
                "data/remuneration-delegated-relations.json",
            ])

        service_compatibility_subnode_ids = (
            compatibility_subnode_ids if service_id == "dayservice" else []
        )
        applicability_services.append({
            "service_id": service_id,
            "scope_state": "SCOPE_DEFINED",
            "applicability_state": "MAPPED",
            "ingestion_state": "INGESTED",
            "mapped_node_count": len(mapped_node_ids),
            "mapped_node_ids": mapped_node_ids,
            "compatibility_subnode_ids": service_compatibility_subnode_ids,
            "mapping_evidence": mapping_evidence,
            "assurance": item_body_assurance_for_service(
                applicability_state="MAPPED",
                mapped_node_ids=mapped_node_ids,
                compatibility_subnode_ids=service_compatibility_subnode_ids,
                national_by_id=national_by_id,
                item_body_doc=item_body_doc,
            ),
        })

        relation_by_id: dict[str, dict[str, Any]] = {}
        if service_id == "dayservice":
            relation_by_id.update(legacy_dayservice_relations)

        for canonical_id in direct_ids_sorted:
            if canonical_id in relation_by_id:
                continue
            source_node = national_by_id[canonical_id]
            relation_by_id[canonical_id] = {
                "canonical_node_id": canonical_id,
                "relation": "DIRECT_APPLICABILITY",
                "verification_state": "NOT_ESTABLISHED",
                "basis": {
                    "source_id": source_node["source_id"],
                    "evidence_kind": "OFFICIAL_HEADING_EXPLICIT_SCOPE",
                },
                "independently_verified_delegation_edge_ids": [],
            }

        for canonical_id, referrers in incorporated_by_service[service_id].items():
            if canonical_id in relation_by_id:
                continue
            relation_by_id[canonical_id] = {
                "canonical_node_id": canonical_id,
                "relation": "INCORPORATED_BY_REFERENCE",
                "verification_state": "NOT_ESTABLISHED",
                "basis": {
                    "referenced_by_canonical_node_ids": referrers,
                    "evidence_kind": "EXPLICIT_INCORPORATION_BY_REFERENCE",
                },
                "independently_verified_delegation_edge_ids": [],
            }

        relation_services.append({
            "service_id": service_id,
            "relation_verification_state": "NOT_ESTABLISHED",
            "relations": [
                relation_by_id[canonical_id]
                for canonical_id in sorted(relation_by_id)
            ],
        })

    if adjudications_used != set(adjudications):
        raise ValueError(
            "delegated applicability adjudication service mismatch: "
            f"used={sorted(adjudications_used)}, declared={sorted(adjudications)}"
        )

    identity_doc = {
        "format_version": 1,
        "corpus_id": CORPUS_ID,
        "canonical_text_store": "data/shared/remuneration-delegated/national-corpus.json",
        "legacy_compatibility_text_store": "data/remuneration-delegated-nodes.json",
        "nodes": identity_rows,
    }

    applicability_doc = {
        "format_version": 1,
        "corpus_id": CORPUS_ID,
        "services": applicability_services,
        "mapping_policy": {
            "direct_applicability_basis": "OFFICIAL_NODE_HEADING_EXPLICIT_SERVICE_SCOPE",
            "incorporated_reference_basis": "EXPLICIT_INCORPORATION_BY_REFERENCE",
            "unmatched_services_require_explicit_adjudication": True,
            "allowed_applicability_states": ["MAPPED", "NOT_APPLICABLE", "UNKNOWN"],
            "service_applicability_auto_verification_allowed": False,
            "note": (
                "MAPPED means a service-to-node applicability relation is represented. "
                "It does not establish item-body verification, currentness, human review, "
                "publication, or route exposure."
            ),
        },
    }

    service_relations_doc = {
        "format_version": 1,
        "corpus_id": CORPUS_ID,
        "services": relation_services,
        "verification_policy": {
            "service_relation_auto_promotion_allowed": False,
            "note": (
                "Official-heading applicability and explicit incorporation relations "
                "are mapped independently from verification. Existing delegation-edge "
                "PASS evidence is retained where available and does not automatically "
                "verify service applicability or service-to-node relation semantics."
            ),
        },
    }

    mapped_top_level_ids = {
        canonical_id
        for row in applicability_services
        for canonical_id in row["mapped_node_ids"]
    }

    source_by_id = {row["id"]: row for row in sources}
    source_documents = []
    for document in national_corpus.get("documents", []):
        source_id = document["source_id"]
        source = source_by_id.get(source_id, {})
        source_documents.append({
            "source_id": source_id,
            "title": source.get("title") or document.get("title"),
            "publisher": source.get("publisher") or document.get("publisher"),
            "official_url": source.get("url") or document.get("official_url"),
            "repository_status": source.get("status"),
            "observed_pages": document.get("observed_pages"),
            "top_level_node_count": document.get("top_level_node_count"),
            "page_sha256": [
                {"page": row.get("page"), "sha256": row.get("sha256")}
                for row in document.get("pages", [])
            ],
            "last_independent_audit_at": independent_audit.get("audited_at"),
        })

    manifest_doc = {
        "format_version": 1,
        "corpus_id": CORPUS_ID,
        "source_family": "delegated_remuneration_criteria",
        "scope_kind": "SHARED_NATIONAL_CORPUS",
        "canonical_node_store": "data/shared/remuneration-delegated/national-corpus.json",
        "identity_map": "data/shared/remuneration-delegated/node-identity-map.json",
        "service_applicability": "data/shared/remuneration-delegated/service-applicability.json",
        "service_relations": "data/shared/remuneration-delegated/service-relations.json",
        "item_body_verification": ITEM_BODY_VERIFICATION_REF,
        "legacy_compatibility": {
            "legacy_text_store": "data/remuneration-delegated-nodes.json",
            "node_ids_preserved": True,
            "legacy_service_scope_field_authoritative": False,
            "shared_corpus_reuses_legacy_text_when_identical": True,
            "note": (
                "The national corpus is canonical for shared source structure. "
                "Existing dayservice text-bearing nodes remain as backward-compatible "
                "targets and are referenced instead of duplicated where possible."
            ),
        },
        "source_selection": national_corpus.get("source_selection", {}),
        "corpus_coverage": national_corpus.get("coverage", {}),
        "source_documents": source_documents,
        "inventory": {
            "national_top_level_nodes": len(national_nodes),
            "legacy_identity_aliases": len(identity_rows),
            "service_mapped_top_level_nodes": len(mapped_top_level_ids),
            "compatibility_subnodes": len(compatibility_subnode_ids),
            "sources": national_corpus.get("coverage", {}).get("source_documents", 0),
            "source_pages": national_corpus.get("coverage", {}).get("source_pages", 0),
            "services_mapped": sum(row["applicability_state"] == "MAPPED" for row in applicability_services),
            "services_not_applicable": sum(row["applicability_state"] == "NOT_APPLICABLE" for row in applicability_services),
            "services_unknown": sum(row["applicability_state"] == "UNKNOWN" for row in applicability_services),
            "item_body_verified_top_level_nodes": sum(
                1 for row in national_nodes
                if str(row.get("source_id")) in _passed_item_body_sources(item_body_doc)
            ),
            "services_item_body_pass": sum(
                (row.get("assurance") or {}).get("item_body_verification") == "PASS"
                for row in applicability_services
            ),
        },
        "assurance": {
            "item_body_verification": (
                "PASS"
                if national_nodes
                and all(
                    str(row.get("source_id")) in _passed_item_body_sources(item_body_doc)
                    for row in national_nodes
                )
                else "NOT_ESTABLISHED"
            ),
            "currentness": "NOT_ESTABLISHED",
            "service_applicability_verification": "NOT_ESTABLISHED",
            "service_relation_verification": "NOT_ESTABLISHED",
            "human_review": "NOT_REVIEWED",
            "publication": "BLOCKED",
            "route_exposure": "BLOCKED",
            "automatic_promotion_allowed": False,
        },
    }

    return {
        "manifest.json": manifest_doc,
        "node-identity-map.json": identity_doc,
        "service-applicability.json": applicability_doc,
        "service-relations.json": service_relations_doc,
    }


def render(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    outputs = build()
    SHARED.mkdir(parents=True, exist_ok=True)
    stale = []
    for name, value in outputs.items():
        path = SHARED / name
        content = render(value)
        if args.check:
            if not path.exists() or path.read_text(encoding="utf-8") != content:
                stale.append(str(path.relative_to(ROOT)))
        else:
            path.write_text(content, encoding="utf-8")
    if stale:
        raise SystemExit("delegated remuneration shared corpus is stale: " + ", ".join(stale))
    if args.check:
        print("delegated remuneration shared corpus: current")
    else:
        print("wrote delegated remuneration shared corpus projections")


if __name__ == "__main__":
    main()
