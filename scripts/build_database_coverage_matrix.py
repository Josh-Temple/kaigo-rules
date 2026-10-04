#!/usr/bin/env python3
"""Generate the service x national-source database coverage matrix.

This file is a projection only. It reads canonical repository state and never
promotes verification, currentness, review, publication, or route state.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "data" / "database-coverage-matrix.generated.json"
SUMMARY_OUTPUT = ROOT / "docs" / "database-coverage-summary.generated.md"

SOURCE_FAMILIES = (
    {
        "id": "care_insurance_act",
        "label": "Long-Term Care Insurance Act",
        "shared_layer_ids": ("care-insurance-act",),
        "scope_keys": ("care_insurance_act", "care_insurance_act_core"),
        "ingestion_keys": ("care_insurance_act",),
        "verification_layer_ids": ("care-insurance-act",),
    },
    {
        "id": "governing_standards_ordinance",
        "label": "Governing standards ordinance",
        "shared_layer_ids": ("ordinance37",),
        "scope_keys": ("ordinance37", "standards_index", "governing_standards"),
        "ingestion_keys": ("ordinance37",),
        "verification_layer_ids": (
            "ordinance37",
            "ordinance37-dayrehab",
            "ordinance37-existing-services",
        ),
    },
    {
        "id": "standards_interpretation_notice",
        "label": "Standards interpretation notice",
        "shared_layer_ids": (),
        "scope_keys": ("rouki25", "standards_interpretation", "notice_review_packet"),
        "ingestion_keys": ("rouki25", "standards_interpretation"),
        "verification_layer_prefixes": ("rouki25-",),
    },
    {
        "id": "remuneration_notification",
        "label": "Remuneration notification",
        "shared_layer_ids": ("remuneration-notices",),
        "scope_keys": ("remuneration_skeleton", "remuneration", "remuneration_index"),
        "ingestion_keys": ("remuneration",),
        "verification_layer_ids": ("remuneration-notices", "remuneration-dayrehab"),
    },
    {
        "id": "delegated_remuneration_criteria",
        "label": "Delegated remuneration criteria",
        "shared_layer_ids": ("remuneration-notices",),
        "scope_keys": ("delegated_remuneration_criteria", "remuneration_skeleton", "remuneration", "remuneration_index"),
        "ingestion_keys": ("delegated_remuneration_criteria",),
        "verification_layer_ids": (),
    },
    {
        "id": "fee_calculation_guidance",
        "label": "Fee-calculation guidance",
        "shared_layer_ids": (),
        "scope_keys": ("fee_guidance", "fee_guidance_index"),
        "ingestion_keys": ("fee_guidance",),
        "verification_layer_ids": ("rouki36-dayservice", "fee-guidance-dayrehab"),
    },
    {
        "id": "unit_price_regional_classification",
        "label": "Unit price / regional classification",
        "shared_layer_ids": ("unit-price",),
        "scope_keys": ("unit_price", "unit_price_regional_classification"),
        "ingestion_keys": ("unit_price",),
        "verification_layer_ids": ("unit-price",),
    },
    {
        "id": "national_qa",
        "label": "National Q&A",
        "shared_layer_ids": ("qa-corpus",),
        "scope_keys": ("qa_corpus", "questions"),
        "ingestion_keys": (),
        "verification_layer_ids": ("qa-corpus",),
    },
    {
        "id": "other_national_manuals_forms",
        "label": "Other material national manuals/forms",
        "shared_layer_ids": (),
        "scope_keys": ("other_national_manuals", "national_manuals", "forms"),
        "ingestion_keys": ("other_national_manuals", "national_manuals", "forms"),
        "verification_layer_ids": (),
    },
)

AXES = (
    "corpus_availability",
    "service_scope",
    "ingestion",
    "item_body_verification",
    "currentness",
    "relation_verification",
    "human_review",
    "publication",
    "route_exposure",
)

def load(path: str) -> Any:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

def normalize_ingestion(raw: str | None, scope_defined: bool, layer_present: bool) -> str:
    if raw:
        upper = raw.upper()
        if "NOT_APPLICABLE" in upper:
            return "NOT_APPLICABLE"
        if "NOT_INGESTED" in upper:
            return "NOT_INGESTED"
        if "PARTIAL" in upper and "ITEM_BODY" not in upper:
            return "PARTIAL"
        if any(token in upper for token in (
            "PUBLISHED", "INDEXED", "DIRECT_TEXT", "ITEM_BODY_VERIFIED",
            "SOURCE_INVENTORY_VERIFIED", "SOURCE_VERSIONED", "COMPARISON_SLOT",
            "RECONSTRUCTED",
        )):
            return "INGESTED"
    if layer_present:
        return "INGESTED"
    if scope_defined:
        return "NOT_INGESTED"
    return "NOT_INGESTED"

def normalize_verification(raw: str | None) -> str:
    if not raw:
        return "NOT_ESTABLISHED"
    upper = raw.upper()
    if upper.startswith("PASS"):
        return "PASS"
    if "PARTIAL" in upper or "GAP" in upper:
        return "PARTIAL"
    if "FAIL" in upper:
        return "BLOCKED"
    return "NOT_ESTABLISHED"

def normalize_currentness(raw: str | None) -> str:
    if not raw:
        return "NOT_ESTABLISHED"
    upper = raw.upper()
    if upper.startswith("PASS") or upper in {"CURRENT", "ESTABLISHED"}:
        return "PASS"
    if "HOLD" in upper or "BLOCK" in upper:
        return "BLOCKED"
    if "GAP" in upper or "NOT_ESTABLISHED" in upper:
        return "NOT_ESTABLISHED"
    if "MONITORED" in upper or "LIVE_SOURCE_REPARSE" in upper:
        return "PARTIAL"
    return "NOT_ESTABLISHED"

def normalize_human_review(raw: str | None) -> str:
    if not raw:
        return "NOT_REVIEWED"
    upper = raw.upper()
    if upper in {"PASS", "HUMAN_VERIFIED", "REVIEWED"}:
        return "PASS"
    if "BLOCK" in upper:
        return "BLOCKED"
    return "NOT_REVIEWED"

def matching_layers(registry: dict, family: dict, service_id: str) -> list[dict]:
    exact = set(family.get("verification_layer_ids", ()))
    prefixes = tuple(family.get("verification_layer_prefixes", ()))
    rows = []
    for layer in registry.get("layers", []):
        layer_id = str(layer.get("id", ""))
        if layer_id not in exact and not any(layer_id.startswith(prefix) for prefix in prefixes):
            continue
        service_ids = layer.get("service_ids") or []
        scope_kind = layer.get("scope_kind")
        if service_id in service_ids or scope_kind == "GLOBAL":
            rows.append(layer)
    return rows

def raw_values(rows: list[dict], path: tuple[str, ...]) -> list[str]:
    values = []
    for row in rows:
        value: Any = row
        for key in path:
            if not isinstance(value, dict):
                value = None
                break
            value = value.get(key)
        if value is not None:
            values.append(str(value))
    return sorted(set(values))

def build_cell(
    service: dict,
    config: dict,
    family: dict,
    registry: dict,
    standards_gate: dict | None,
    relation_queue: dict,
    shared_context: dict,
) -> dict:
    service_id = service["service_id"]
    scope_files = config.get("scope_files") or {}
    ingestion_layers = config.get("ingestion_layers") or {}
    layers = matching_layers(registry, family, service_id)

    shared_layers = [
        layer for layer in registry.get("layers", [])
        if layer.get("id") in family.get("shared_layer_ids", ())
    ]
    declared_scope = [key for key in family.get("scope_keys", ()) if scope_files.get(key)]
    layer_scoped = any(
        service_id in (layer.get("service_ids") or []) and layer.get("scope_kind") != "GLOBAL"
        for layer in layers
    )
    scope_defined = bool(declared_scope or layer_scoped)
    mapped_standards_corpus = shared_context["standards_map"].get(service_id)
    if family["id"] == "governing_standards_ordinance":
        scope_state_row = shared_context["standards_scope_states"].get(service_id, {})
        scope_defined = scope_state_row.get("scope_status") == "SCOPE_DEFINED"
    if family["id"] == "national_qa":
        if service_id in shared_context["qa_direct_service_ids"]:
            scope_defined = True
            if "qa_service_mapping" not in declared_scope:
                declared_scope.append("qa_service_mapping")
        if service_id in shared_context["qa_scoped_service_ids"]:
            scope_defined = True
            if "qa_service_relations" not in declared_scope:
                declared_scope.append("qa_service_relations")

    ingestion_rows = [
        ingestion_layers[key]
        for key in family.get("ingestion_keys", ())
        if isinstance(ingestion_layers.get(key), dict)
    ]
    raw_ingestion = sorted({
        str(row.get("status")) for row in ingestion_rows if row.get("status") is not None
    })

    unit_price_mapping = None
    if family["id"] == "unit_price_regional_classification":
        unit_price_mapping = shared_context["unit_price_service_map"].get(service_id)
        if unit_price_mapping and unit_price_mapping.get("ingestion_status"):
            raw_ingestion = sorted(set(raw_ingestion + [str(unit_price_mapping["ingestion_status"])]))

    delegated_applicability = None
    if family["id"] == "delegated_remuneration_criteria":
        delegated_applicability = shared_context["delegated_applicability"].get(service_id)
        if delegated_applicability and delegated_applicability.get("ingestion_state"):
            raw_ingestion = [str(delegated_applicability["ingestion_state"])]

    corpus_id = None
    delegated_manifest = shared_context.get("delegated_manifest") or {}
    if family["id"] == "delegated_remuneration_criteria" and delegated_manifest:
        corpus_state = "AVAILABLE"
        corpus_kind = "SHARED"
        corpus_id = delegated_manifest.get("corpus_id")
        corpus_evidence = [
            "data/shared/remuneration-delegated/manifest.json",
            str(delegated_manifest.get("canonical_node_store")),
        ]
    elif family["id"] == "governing_standards_ordinance" and mapped_standards_corpus:
        corpus_state = "AVAILABLE"
        corpus_kind = "SHARED"
        corpus_id = mapped_standards_corpus
        corpus_evidence = [
            "data/shared/standards/manifest.json",
            f"data/shared/standards/service-ordinance-map.json#{service_id}",
        ]
    elif shared_layers:
        corpus_state = "AVAILABLE"
        corpus_kind = "SHARED"
        corpus_evidence = [f"data/verification-registry.json#{layer['id']}" for layer in shared_layers]
    elif scope_defined or ingestion_rows or layers:
        corpus_state = "AVAILABLE"
        corpus_kind = "SERVICE_SPECIFIC"
        corpus_evidence = sorted({
            *[str(scope_files[key]) for key in declared_scope],
            *[
                str(layer.get("content_verification", {}).get("evidence"))
                for layer in layers
                if layer.get("content_verification", {}).get("evidence")
            ],
        })
    else:
        corpus_state = "NOT_AVAILABLE"
        corpus_kind = "UNKNOWN"
        corpus_evidence = []

    scope_state = "SCOPE_DEFINED" if scope_defined else "SCOPE_NOT_DEFINED"
    scope_evidence = sorted(
        "data/qa-service-mapping.json" if key == "qa_service_mapping"
        else "data/qa-service-relations.generated.json" if key == "qa_service_relations"
        else str(scope_files[key])
        for key in declared_scope
    )
    if layer_scoped:
        scope_evidence.extend(
            f"data/verification-registry.json#{layer['id']}"
            for layer in layers
            if service_id in (layer.get("service_ids") or []) and layer.get("scope_kind") != "GLOBAL"
        )
        scope_evidence = sorted(set(scope_evidence))

    layer_present = bool(layers)
    if family["id"] == "governing_standards_ordinance" and mapped_standards_corpus:
        layer_present = True
    ingestion_state = normalize_ingestion(
        raw_ingestion[0] if len(raw_ingestion) == 1 else (" | ".join(raw_ingestion) if raw_ingestion else None),
        scope_defined,
        layer_present,
    )
    if family["id"] == "delegated_remuneration_criteria":
        ingestion_state = (
            str(delegated_applicability.get("ingestion_state"))
            if delegated_applicability
            else "NOT_INGESTED"
        )

    content_raw = raw_values(layers, ("content_verification", "status"))
    currentness_raw = raw_values(layers, ("currentness", "status"))
    human_raw = raw_values(layers, ("human_review", "status"))
    if family["id"] == "delegated_remuneration_criteria" and delegated_applicability:
        delegated_assurance = delegated_applicability.get("assurance") or {}
        content_value = delegated_assurance.get("item_body_verification")
        currentness_value = delegated_assurance.get("currentness")
        human_value = delegated_assurance.get("human_review")
        content_raw = [str(content_value)] if content_value else []
        currentness_raw = [str(currentness_value)] if currentness_value else []
        human_raw = [str(human_value)] if human_value else []
    if family["id"] == "governing_standards_ordinance" and mapped_standards_corpus and mapped_standards_corpus != "ordinance37":
        audit_row = shared_context["standards_audit"].get(mapped_standards_corpus)
        content_raw = [audit_row.get("result")] if audit_row else []
        currentness_raw = []
        human_raw = []

    item_body_evidence = [
        str(layer.get("content_verification", {}).get("evidence"))
        for layer in layers
        if layer.get("content_verification", {}).get("evidence")
    ]
    if family["id"] == "governing_standards_ordinance" and mapped_standards_corpus and mapped_standards_corpus != "ordinance37":
        item_body_evidence = ["data/shared/standards/independent-audit.json"]
    currentness_evidence = [
        str(layer.get("currentness", {}).get("evidence"))
        for layer in layers
        if layer.get("currentness", {}).get("evidence")
    ]

    if family["id"] == "standards_interpretation_notice" and standards_gate:
        item_raw = standards_gate.get("item_body", {}).get("state")
        current_raw = standards_gate.get("currentness", {}).get("state")
        content_raw = [str(item_raw)] if item_raw else content_raw
        currentness_raw = [str(current_raw)] if current_raw else currentness_raw
        receipt = standards_gate.get("item_body", {}).get("receipt")
        if receipt:
            item_body_evidence.append(str(receipt))
        current_receipt = standards_gate.get("currentness", {}).get("receipt")
        if current_receipt:
            currentness_evidence.append(str(current_receipt))

    item_state = normalize_verification(content_raw[0] if len(content_raw) == 1 else (" | ".join(content_raw) if content_raw else None))
    current_state = normalize_currentness(currentness_raw[0] if len(currentness_raw) == 1 else (" | ".join(currentness_raw) if currentness_raw else None))

    ingestion_human = [
        str(row.get("human_review"))
        for row in ingestion_rows
        if row.get("human_review") is not None
    ]
    human_values = sorted(set(human_raw + ingestion_human))
    human_state = normalize_human_review(
        human_values[0] if len(human_values) == 1 else (" | ".join(human_values) if human_values else None)
    )

    publication_gate = config.get("publication_gate") or {}
    routing = config.get("routing") or {}
    route_enabled = bool(
        routing.get("future_service_base_enabled")
        or routing.get("current_mode") == "LEGACY_ROOT"
    )
    explicit_public = publication_gate.get("public_routes_enabled")
    if family["id"] == "delegated_remuneration_criteria" and delegated_applicability:
        delegated_assurance = delegated_applicability.get("assurance") or {}
        publication_state = str(delegated_assurance.get("publication") or "NOT_ESTABLISHED")
        route_state = str(delegated_assurance.get("route_exposure") or "NOT_ESTABLISHED")
    else:
        if explicit_public is False:
            publication_state = "BLOCKED"
        elif explicit_public is True and scope_defined and ingestion_state in {"INGESTED", "PARTIAL"}:
            publication_state = "AVAILABLE"
        elif route_enabled and scope_defined and ingestion_state in {"INGESTED", "PARTIAL"}:
            publication_state = "AVAILABLE"
        else:
            publication_state = "NOT_ESTABLISHED"

        if route_enabled and scope_defined and ingestion_state in {"INGESTED", "PARTIAL"}:
            route_state = "AVAILABLE"
        elif route_enabled:
            route_state = "NOT_ESTABLISHED"
        else:
            route_state = "BLOCKED"

    if (
        family["id"] == "unit_price_regional_classification"
        and unit_price_mapping
        and unit_price_mapping.get("applicability") == "APPLIES"
        and not ingestion_rows
        and not layers
    ):
        publication_state = "BLOCKED"
        route_state = "BLOCKED"

    relation_raw = str(registry.get("relation_verification", {}).get("status") or "NOT_ESTABLISHED")
    relation_state = "PASS" if relation_raw == "PASS" else "NOT_ESTABLISHED"

    if (
        family["id"] == "delegated_remuneration_criteria"
        and delegated_applicability
        and delegated_applicability.get("applicability_state") == "NOT_APPLICABLE"
    ):
        relation_state = "NOT_APPLICABLE"

    if (
        family["id"] == "unit_price_regional_classification"
        and unit_price_mapping
        and unit_price_mapping.get("applicability") == "NOT_APPLICABLE"
    ):
        item_state = "NOT_APPLICABLE"
        current_state = "NOT_APPLICABLE"
        relation_state = "NOT_APPLICABLE"
        human_state = "NOT_APPLICABLE"
        publication_state = "NOT_APPLICABLE"
        route_state = "NOT_APPLICABLE"

    result = {
        "source_family": family["id"],
        "label": family["label"],
        "corpus_availability": {
            "state": corpus_state,
            "kind": corpus_kind,
            "corpus_id": corpus_id,
            "evidence": sorted(set(corpus_evidence)),
        },
        "service_scope": {
            "state": scope_state,
            "declared_keys": sorted(declared_scope),
            "evidence": scope_evidence,
        },
        "ingestion": {
            "state": ingestion_state,
            "raw_status": raw_ingestion,
        },
        "item_body_verification": {
            "state": item_state,
            "raw_status": content_raw,
            "evidence": sorted(set(item_body_evidence)),
        },
        "currentness": {
            "state": current_state,
            "raw_status": currentness_raw,
            "evidence": sorted(set(currentness_evidence)),
        },
        "relation_verification": {
            "state": relation_state,
            "raw_status": relation_raw,
            "remaining_global_relations": relation_queue.get("remaining_relations"),
            "note": "Global relation coverage is retained as raw context; no service x source-family PASS is inferred without canonical attribution.",
        },
        "human_review": {
            "state": human_state,
            "raw_status": human_values,
        },
        "publication": {
            "state": publication_state,
            "raw_service_public_routes_enabled": explicit_public,
        },
        "route_exposure": {
            "state": route_state,
            "raw_current_mode": routing.get("current_mode"),
            "raw_future_service_base_enabled": routing.get("future_service_base_enabled"),
        },
    }
    if family["id"] == "delegated_remuneration_criteria":
        result["service_applicability"] = {
            "state": (
                str(delegated_applicability.get("applicability_state"))
                if delegated_applicability
                else "NOT_MAPPED"
            ),
            "mapped_node_count": (
                int(delegated_applicability.get("mapped_node_count", 0))
                if delegated_applicability
                else 0
            ),
            "evidence": (
                [f"data/shared/remuneration-delegated/service-applicability.json#{service_id}"]
                if delegated_applicability
                else []
            ),
            "relation_model": (
                f"data/shared/remuneration-delegated/service-relations.json#{service_id}"
                if delegated_applicability
                else None
            ),
        }
    return result

def count_axis(rows: list[dict], family_id: str, axis: str) -> dict[str, int]:
    counts = Counter(
        cell[axis]["state"]
        for row in rows
        for cell in row["source_families"]
        if cell["source_family"] == family_id
    )
    return dict(sorted(counts.items()))

def build() -> dict:
    manifest = load("data/services/manifest.json")
    catalog = load("data/services/catalog.generated.json")
    registry = load("data/verification-registry.json")
    relation_queue = load("data/relation-verification-queue.json")
    gate_path = ROOT / "data/verification/standards-interpretation-gates.json"
    gates = load("data/verification/standards-interpretation-gates.json") if gate_path.exists() else {"services": []}
    gates_by_service = {row["service_id"]: row for row in gates.get("services", [])}
    standards_map_data = load("data/shared/standards/service-ordinance-map.json")
    standards_relations = load("data/shared/standards/service-relations.generated.json")
    standards_audit_data = load("data/shared/standards/independent-audit.json")
    qa_mapping = load("data/qa-service-mapping.json")
    qa_service_relations = load("data/qa-service-relations.generated.json")
    unit_price_index = load("data/unit-price-service-multipliers.json")
    delegated_manifest = load("data/shared/remuneration-delegated/manifest.json")
    delegated_applicability_data = load("data/shared/remuneration-delegated/service-applicability.json")
    delegated_relations_data = load("data/shared/remuneration-delegated/service-relations.json")
    shared_context = {
        "standards_map": {row["service_id"]: row["corpus_id"] for row in standards_map_data.get("relations", [])},
        "standards_scope_states": {row["service_id"]: row for row in standards_relations.get("service_scope_states", [])},
        "standards_audit": {row["id"]: row for row in standards_audit_data.get("checks", [])},
        "qa_direct_service_ids": {
            row["catalog_mapping"]["service_id"]
            for row in qa_mapping.get("codes", [])
            if row.get("classification") == "INDIVIDUAL_SERVICE"
            and row.get("catalog_mapping", {}).get("state") == "MAPPED_CURRENT_CATALOG"
        },
        "qa_scoped_service_ids": {
            row["service_id"]
            for row in qa_service_relations.get("services", [])
            if str(row.get("scope_state", "")).startswith("DEFINED")
        },
        "unit_price_service_map": {
            row["service_id"]: row
            for row in unit_price_index.get("service_mappings", [])
        },
        "delegated_manifest": delegated_manifest,
        "delegated_applicability": {
            row["service_id"]: row
            for row in delegated_applicability_data.get("services", [])
        },
        "delegated_relations": {
            row["service_id"]: row
            for row in delegated_relations_data.get("services", [])
        },
    }

    manifest_ids = [row["service_id"] for row in manifest.get("services", [])]
    catalog_ids = [row["service_id"] for row in catalog.get("services", [])]
    if manifest_ids != catalog_ids:
        raise ValueError("service manifest and generated catalog are not aligned")

    rows = []
    for service in manifest.get("services", []):
        config = load(service["config"])
        cells = [
            build_cell(
                service,
                config,
                family,
                registry,
                gates_by_service.get(service["service_id"]),
                relation_queue,
                shared_context,
            )
            for family in SOURCE_FAMILIES
        ]
        rows.append({
            "service_id": service["service_id"],
            "label": service["label"],
            "service_status": service["status"],
            "config": service["config"],
            "publication_gate": config.get("publication_gate") or {},
            "routing": config.get("routing") or {},
            "source_families": cells,
        })

    shared_scope_missing = []
    missing_corpus = []
    currentness_gaps = []
    verification_gaps = []
    publication_gaps = []

    for row in rows:
        for cell in row["source_families"]:
            identity = {"service_id": row["service_id"], "source_family": cell["source_family"]}
            if (
                cell["corpus_availability"]["state"] == "AVAILABLE"
                and cell["corpus_availability"]["kind"] == "SHARED"
                and cell["service_scope"]["state"] == "SCOPE_NOT_DEFINED"
            ):
                shared_scope_missing.append(identity)
            if cell["corpus_availability"]["state"] == "NOT_AVAILABLE":
                missing_corpus.append(identity)
            if (
                cell["ingestion"]["state"] in {"INGESTED", "PARTIAL"}
                and cell["currentness"]["state"] != "PASS"
            ):
                currentness_gaps.append({**identity, "state": cell["currentness"]["state"]})
            if (
                cell["ingestion"]["state"] in {"INGESTED", "PARTIAL"}
                and cell["item_body_verification"]["state"] != "PASS"
            ):
                verification_gaps.append({**identity, "state": cell["item_body_verification"]["state"]})
            if (
                cell["ingestion"]["state"] in {"INGESTED", "PARTIAL"}
                and cell["publication"]["state"] != "AVAILABLE"
            ):
                publication_gaps.append({**identity, "state": cell["publication"]["state"]})

    family_summary = {}
    for family in SOURCE_FAMILIES:
        family_summary[family["id"]] = {
            axis: count_axis(rows, family["id"], axis)
            for axis in AXES
        }

    delegated_applicability_counts = Counter(
        cell.get("service_applicability", {}).get("state", "NOT_MAPPED")
        for row in rows
        for cell in row["source_families"]
        if cell["source_family"] == "delegated_remuneration_criteria"
    )
    delegated_mapped_services = [
        row["service_id"]
        for row in rows
        for cell in row["source_families"]
        if cell["source_family"] == "delegated_remuneration_criteria"
        and cell.get("service_applicability", {}).get("state") == "MAPPED"
    ]

    return {
        "format_version": 1,
        "generated_by": "scripts/build_database_coverage_matrix.py",
        "projection_only": True,
        "policy": {
            "canonical_status_writeback_allowed": False,
            "verification_auto_promotion_allowed": False,
            "currentness_auto_promotion_allowed": False,
            "human_review_auto_promotion_allowed": False,
            "route_auto_enable_allowed": False,
            "single_completion_percentage_allowed": False,
        },
        "canonical_inputs": [
            "data/services/manifest.json",
            "data/services/catalog.generated.json",
            "data/services/*.json",
            "data/verification-registry.json",
            "data/verification/standards-interpretation-gates.json",
            "data/relation-verification-queue.json",
            "data/shared/standards/manifest.json",
            "data/shared/standards/service-ordinance-map.json",
            "data/shared/standards/service-relations.generated.json",
            "data/shared/standards/independent-audit.json",
            "data/qa-service-mapping.json",
            "data/shared/remuneration-delegated/manifest.json",
            "data/shared/remuneration-delegated/national-corpus.json",
            "data/shared/remuneration-delegated/node-identity-map.json",
            "data/shared/remuneration-delegated/service-applicability.json",
            "data/shared/remuneration-delegated/service-relations.json",
            "data/shared/remuneration-delegated/service-applicability-adjudications.json",
        ],
        "source_families": [
            {"id": family["id"], "label": family["label"]}
            for family in SOURCE_FAMILIES
        ],
        "services": rows,
        "summary": {
            "services_total": len(rows),
            "source_families_total": len(SOURCE_FAMILIES),
            "source_family_coverage": family_summary,
            "shared_corpus_available_but_service_scope_missing": shared_scope_missing,
            "genuinely_missing_corpus": missing_corpus,
            "currentness_gaps": currentness_gaps,
            "verification_gaps": verification_gaps,
            "relation_verification": {
                "inventory_relations": relation_queue.get("inventory_relations"),
                "independently_covered_relations": relation_queue.get("independently_covered_relations"),
                "remaining_relations": relation_queue.get("remaining_relations"),
                "classification_counts": relation_queue.get("classification_counts", {}),
            },
            "publication_gaps": publication_gaps,
            "delegated_remuneration_criteria": {
                "corpus_id": delegated_manifest.get("corpus_id"),
                "service_applicability": dict(sorted(delegated_applicability_counts.items())),
                "mapped_services": delegated_mapped_services,
            },
        },
    }

def render_summary(matrix: dict) -> str:
    summary = matrix["summary"]
    lines = [
        "# Database coverage matrix summary",
        "",
        "> Generated projection. Do not edit this file to change canonical status.",
        "",
        f"- Services total: {summary['services_total']}",
        f"- Source families: {summary['source_families_total']}",
        f"- Shared corpus available but service scope missing: {len(summary['shared_corpus_available_but_service_scope_missing'])}",
        f"- Genuinely missing corpus cells: {len(summary['genuinely_missing_corpus'])}",
        f"- Currentness gaps on ingested cells: {len(summary['currentness_gaps'])}",
        f"- Item-body verification gaps on ingested cells: {len(summary['verification_gaps'])}",
        f"- Relation verification remaining: {summary['relation_verification']['remaining_relations']}",
        f"- Publication gaps on ingested cells: {len(summary['publication_gaps'])}",
        f"- Delegated remuneration applicability mapped: {summary['delegated_remuneration_criteria']['service_applicability'].get('MAPPED', 0)}",
        "",
        "## Source-family coverage",
        "",
        "| Source family | Corpus | Scope | Ingestion | Item-body | Currentness | Human review | Publication | Route |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for family in matrix["source_families"]:
        coverage = summary["source_family_coverage"][family["id"]]
        def fmt(axis: str) -> str:
            return ", ".join(f"{key}={value}" for key, value in coverage[axis].items()) or "-"
        lines.append(
            "| " + family["label"] + " | "
            + fmt("corpus_availability") + " | "
            + fmt("service_scope") + " | "
            + fmt("ingestion") + " | "
            + fmt("item_body_verification") + " | "
            + fmt("currentness") + " | "
            + fmt("human_review") + " | "
            + fmt("publication") + " | "
            + fmt("route_exposure") + " |"
        )
    delegated = summary["delegated_remuneration_criteria"]
    delegated_counts = ", ".join(
        f"{key}={value}" for key, value in delegated["service_applicability"].items()
    ) or "-"
    lines.extend([
        "",
        "## Delegated remuneration criteria detail",
        "",
        f"- Shared corpus: AVAILABLE ({delegated['corpus_id']})",
        f"- Service applicability: {delegated_counts}",
        "- Applicability mapping does not establish item-body verification, currentness, human review, publication, or route exposure.",
        "",
        "## Interpretation",
        "",
        "- Corpus availability and service scope are separate dimensions. A shared corpus being present does not establish service applicability.",
        "- Item-body verification does not establish currentness, human review, publication, or route exposure.",
        "- Relation verification is retained as global raw context until canonical service × source-family attribution exists.",
        "- Missing and unestablished states remain visible rather than being inferred as PASS.",
        "",
    ])
    return "\n".join(lines)

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    matrix = build()
    rendered_json = json.dumps(matrix, ensure_ascii=False, indent=2) + "\n"
    rendered_summary = render_summary(matrix)

    if args.check:
        if not OUTPUT.exists() or OUTPUT.read_text(encoding="utf-8") != rendered_json:
            raise SystemExit("database coverage matrix is stale; run builder")
        if not SUMMARY_OUTPUT.exists() or SUMMARY_OUTPUT.read_text(encoding="utf-8") != rendered_summary:
            raise SystemExit("database coverage summary is stale; run builder")
        print("database coverage matrix: current")
        return

    OUTPUT.write_text(rendered_json, encoding="utf-8")
    SUMMARY_OUTPUT.write_text(rendered_summary, encoding="utf-8")
    print(f"wrote {OUTPUT.relative_to(ROOT)}")
    print(f"wrote {SUMMARY_OUTPUT.relative_to(ROOT)}")

if __name__ == "__main__":
    main()
