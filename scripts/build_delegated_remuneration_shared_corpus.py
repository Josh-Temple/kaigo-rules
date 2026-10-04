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


def build() -> dict[str, Any]:
    nodes = load(DATA / "remuneration-delegated-nodes.json")
    delegated_meta = load(DATA / "remuneration-delegated-meta.json")
    sources = load(DATA / "sources.json")
    relation_audit = load(DATA / "remuneration-delegation-relation-independent-audit.json")
    independent_audit = load(DATA / "remuneration-independent-audit.json")

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

    passed_checks_by_target: dict[str, list[str]] = {}
    for check in relation_audit.get("checks", []):
        if check.get("result") != "PASS":
            continue
        passed_checks_by_target.setdefault(check["to_id"], []).append(check["id"])

    node_by_legacy = {node["id"]: node for node in nodes}
    service_relations = []
    for row in identity_rows:
        legacy_id = row["legacy_node_id"]
        legacy = node_by_legacy[legacy_id]
        service_relations.append({
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
        })

    identity_doc = {
        "format_version": 1,
        "corpus_id": CORPUS_ID,
        "canonical_text_store": "data/remuneration-delegated-nodes.json",
        "nodes": identity_rows,
    }

    applicability_doc = {
        "format_version": 1,
        "corpus_id": CORPUS_ID,
        "services": [{
            "service_id": "dayservice",
            "scope_state": "SCOPE_DEFINED",
            "applicability_state": "MAPPED",
            "ingestion_state": "INGESTED",
            "mapped_node_count": len(identity_rows),
            "mapped_node_ids": canonical_ids,
            "mapping_evidence": [
                "data/remuneration-delegated-nodes.json",
                "data/shared/remuneration-delegated/node-identity-map.json",
                "data/remuneration-delegated-relations.json",
            ],
            "assurance": {
                "item_body_verification": "NOT_ESTABLISHED",
                "currentness": "NOT_ESTABLISHED",
                "relation_verification": "NOT_ESTABLISHED",
                "human_review": "NOT_REVIEWED",
                "publication": "BLOCKED",
                "route_exposure": "BLOCKED",
                "automatic_promotion_allowed": False,
            },
        }],
    }

    service_relations_doc = {
        "format_version": 1,
        "corpus_id": CORPUS_ID,
        "services": [{
            "service_id": "dayservice",
            "relation_verification_state": "NOT_ESTABLISHED",
            "relations": service_relations,
        }],
        "verification_policy": {
            "service_relation_auto_promotion_allowed": False,
            "note": (
                "Independent delegation-edge PASS evidence is retained separately "
                "and does not automatically verify service applicability or "
                "service-to-node relation semantics."
            ),
        },
    }

    source_ids = sorted({node["source_id"] for node in nodes})
    source_by_id = {row["id"]: row for row in sources}
    meta_by_source_id = {
        "mhlw-fee-notice27-base": delegated_meta.get("sources", {}).get("notice27", {}),
        "mhlw-fee-criteria95-current": delegated_meta.get("sources", {}).get("notice95", {}),
    }
    source_documents = []
    for source_id in source_ids:
        source = source_by_id.get(source_id, {})
        meta = meta_by_source_id.get(source_id, {})
        source_documents.append({
            "source_id": source_id,
            "title": source.get("title"),
            "publisher": source.get("publisher"),
            "official_url": source.get("url") or meta.get("url"),
            "repository_status": source.get("status"),
            "source_sha256": meta.get("sha256"),
            "last_independent_audit_at": independent_audit.get("audited_at"),
            "node_count": sum(1 for node in nodes if node["source_id"] == source_id),
        })

    manifest_doc = {
        "format_version": 1,
        "corpus_id": CORPUS_ID,
        "source_family": "delegated_remuneration_criteria",
        "scope_kind": "SHARED_NATIONAL_CORPUS",
        "canonical_node_store": "data/remuneration-delegated-nodes.json",
        "identity_map": "data/shared/remuneration-delegated/node-identity-map.json",
        "service_applicability": "data/shared/remuneration-delegated/service-applicability.json",
        "service_relations": "data/shared/remuneration-delegated/service-relations.json",
        "legacy_compatibility": {
            "node_ids_preserved": True,
            "legacy_service_scope_field_authoritative": False,
            "note": (
                "The existing delegated-node file remains the single text-bearing "
                "store for backward compatibility. Service applicability is canonical "
                "only in the shared applicability file."
            ),
        },
        "source_documents": source_documents,
        "inventory": {
            "nodes": len(identity_rows),
            "sources": len(source_ids),
            "services_mapped": 1,
        },
        "assurance": {
            "item_body_verification": "NOT_ESTABLISHED",
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
