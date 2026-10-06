#!/usr/bin/env python3
"""Build the bounded publication allowlist used by every public runtime surface.

Only publication units that are READY, supported by the runtime policy, and
explicitly selected here can be exposed. Route exposure is selected separately,
even when it currently matches the publication selection.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
READINESS_PATH = ROOT / "data/publication-readiness.generated.json"
GOVERNING_CURRENTNESS_PATH = ROOT / "data/verification/bounded-currentness-closure-worker-b.json"
HIGH_VALUE_CURRENTNESS_PATH = ROOT / "data/verification/high-value-currentness-closure-worker-b.json"
OUTPUT_PATH = ROOT / "data/bounded-publication-allowlist.json"

SAFE_FIELDS = [
    "source_text",
    "item_body",
    "source_metadata",
    "source_locator",
    "currentness_statement",
    "service_applicability_statement",
]
FORBIDDEN_FIELDS = [
    "cross_layer_relation_assertion",
    "unverified_relation_assertion",
    "review_dependent_explanatory_text",
    "relation_rank_feature",
    "review_dependent_search_term",
]
RUNTIME_SUPPORTED_SOURCE_FAMILIES = {
    "governing_standards_ordinance",
    "unit_price_regional_classification",
}
RUNTIME_SUPPORTED_SOURCE_IDENTITIES = {
    "ordinance37",
    "preventive-services-standards",
    "mhlw-unit-price-current",
}
MAX_PUBLICATION_CELLS = 32


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def git_blob_sha(path: Path) -> str:
    body = path.read_bytes()
    header = f"blob {len(body)}\0".encode("utf-8")
    return hashlib.sha1(header + body).hexdigest()


def cell_key(row: dict[str, Any]) -> tuple[str | None, str | None]:
    return row.get("service_id"), row.get("source_family")


def source_contract_supported(row: dict[str, Any]) -> bool:
    source_family = row.get("source_family")
    source = row.get("source_identity") or {}
    proof = row.get("applicability_proof") or {}
    canonical_source_id = source.get("canonical_source_id")

    if canonical_source_id not in RUNTIME_SUPPORTED_SOURCE_IDENTITIES:
        return False
    if source_family not in RUNTIME_SUPPORTED_SOURCE_FAMILIES:
        return False
    if row.get("promotion_applied") is not True:
        return False
    if row.get("projected_currentness_state") != "PASS":
        return False
    if row.get("ingestion_state") != "INGESTED":
        return False
    if row.get("item_body_state") != "PASS":
        return False
    if row.get("source_version_contains_scope") is not True:
        return False

    if canonical_source_id == "ordinance37":
        return (
            source_family == "governing_standards_ordinance"
            and proof.get("state") == "PASS_DIRECT_SERVICE_CHAPTER"
            and proof.get("direct_service_chapter_verified") is True
            and proof.get("discrepancies") == 0
            and bool(proof.get("target_articles"))
        )

    if canonical_source_id == "preventive-services-standards":
        return (
            source_family == "governing_standards_ordinance"
            and proof.get("state") == "PASS_DIRECT_SERVICE_SCOPE"
            and proof.get("direct_service_scope_verified") is True
            and proof.get("discrepancies") == 0
            and (
                bool(proof.get("common_source_node_ids"))
                or bool((proof.get("primary_range") or {}).get("from_node_id"))
                or bool(proof.get("variant_ranges"))
            )
        )

    if canonical_source_id == "mhlw-unit-price-current":
        return (
            row.get("service_id") == "dayservice"
            and source_family == "unit_price_regional_classification"
            and source.get("currentness_class") == "CURRENT_OFFICIAL_CONSOLIDATED"
            and bool(source.get("version_id"))
            and source.get("effective_date") == "2024-04-01"
            and proof.get("state") == "PASS_DIRECT_SERVICE_SCOPE"
            and proof.get("official_service_name") == "通所介護"
            and proof.get("multiplier_profile_id") == "group-1090"
            and proof.get("mapped_item_count") == 8
            and proof.get("source_locator") == "第一号 表 / 通所介護 / 地域区分別割合"
        )

    return False


def load_promotions() -> tuple[dict[tuple[str | None, str | None], dict[str, Any]], list[dict[str, str]]]:
    sources = []
    promotions: dict[tuple[str | None, str | None], dict[str, Any]] = {}
    for path in (GOVERNING_CURRENTNESS_PATH, HIGH_VALUE_CURRENTNESS_PATH):
        payload = load_json(path)
        sources.append(
            {
                "path": str(path.relative_to(ROOT)).replace("\\", "/"),
                "git_blob_sha": git_blob_sha(path),
            }
        )
        for row in payload.get("promotions", []):
            key = cell_key(row)
            if key in promotions:
                raise ValueError(f"duplicate currentness promotion: {key}")
            promotions[key] = row
    return promotions, sources


def build() -> dict[str, Any]:
    readiness = load_json(READINESS_PATH)
    promotions, currentness_sources = load_promotions()

    ready = [
        row
        for row in readiness.get("cells", [])
        if row.get("readiness") == "READY_FOR_PUBLICATION_REVIEW"
        and not row.get("blocking_reasons")
    ]

    publishable = []
    for row in ready:
        if row.get("source_family") not in RUNTIME_SUPPORTED_SOURCE_FAMILIES:
            continue
        promotion = promotions.get(cell_key(row))
        if not promotion or not source_contract_supported(promotion):
            continue
        publishable.append(row)

    publishable.sort(
        key=lambda row: (
            0 if row.get("source_family") == "governing_standards_ordinance" else 1,
            str(row.get("service_id") or ""),
            str(row.get("source_family") or ""),
        )
    )
    publishable = publishable[:MAX_PUBLICATION_CELLS]

    publication = [
        {
            "service_id": row["service_id"],
            "source_family": row["source_family"],
        }
        for row in publishable
    ]
    routes = list(publication)
    fields = {
        f"{row['service_id']}|{row['source_family']}": SAFE_FIELDS
        for row in publishable
    }

    if not ready:
        decision = "NO_PUBLICATION_CHANGE"
        reason = "No READY_FOR_PUBLICATION_REVIEW cells exist after integrated readiness regeneration."
    elif publication:
        decision = "PUBLISH_BOUNDED_READY_UNITS"
        reason = (
            "READY publication units supported by the shared multi-source runtime policy are "
            "bound across UI, search, API, and machine retrieval."
        )
    else:
        decision = "DEFER_PUBLICATION_FAIL_CLOSED"
        reason = (
            "READY candidates exist, but none are supported by the currently "
            "implemented runtime publication policy."
        )

    return {
        "format_version": 5,
        "generated_by": "scripts/build_bounded_publication_allowlist.py",
        "role": "Publication Runtime Binding / Progressive Release Worker",
        "source_readiness": {
            "path": "data/publication-readiness.generated.json",
            "git_blob_sha": git_blob_sha(READINESS_PATH),
            "expected_ready_candidate_count": len(ready),
        },
        "source_currentness": {
            "path": currentness_sources[0]["path"],
            "git_blob_sha": currentness_sources[0]["git_blob_sha"],
            "additional_sources": currentness_sources[1:],
        },
        "runtime_binding": {
            "required_for_nonempty_publication": True,
            "established": True,
            "policy_module": "lib/publication-policy.ts",
            "adapter_registry_module": "lib/publication-runtime-adapters.ts",
            "supported_source_families": sorted(RUNTIME_SUPPORTED_SOURCE_FAMILIES),
            "supported_source_identities": sorted(RUNTIME_SUPPORTED_SOURCE_IDENTITIES),
            "required_surfaces": [
                "UI",
                "SEARCH",
                "API",
                "MACHINE_RETRIEVAL",
            ],
        },
        "policy": {
            "explicit_publication_allowlist_required": True,
            "explicit_route_allowlist_required": True,
            "max_publication_cells": MAX_PUBLICATION_CELLS,
            "publication_does_not_enable_route": True,
            "blocked_cells_cannot_be_published": True,
            "allowlist_must_be_subset_of_ready_candidates": True,
            "unverified_relation_assertions_forbidden": True,
            "unreviewed_explanatory_text_forbidden": True,
            "search_and_machine_retrieval_must_respect_publication_allowlist": True,
            "preventive_services_group_with_non_preventive_counterpart": True,
            "preventive_support_is_standalone": True,
            "existing_public_surfaces_must_not_be_removed_by_zero_candidate_run": True,
            "runtime_binding_required_for_nonempty_publication": True,
        },
        "safe_publication_fields": SAFE_FIELDS,
        "forbidden_publication_fields": FORBIDDEN_FIELDS,
        "summary": {
            "ready_candidates_at_selection": len(ready),
            "ready_candidate_cells": [
                {
                    "service_id": row["service_id"],
                    "source_family": row["source_family"],
                    "ready_publication_units": row.get("ready_publication_units", []),
                }
                for row in ready
            ],
            "published_cells_added": len(publication),
            "routes_added": len(routes),
            "existing_public_surfaces_changed": False,
            "decision": decision,
            "reason": reason,
            "blocker_counts_at_selection": readiness.get("summary", {}).get(
                "blocking_axis_counts", {}
            ),
        },
        "publication_cell_allowlist": publication,
        "route_allowlist": routes,
        "field_allowlist_by_cell": fields,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    artifact = build()
    rendered = json.dumps(artifact, ensure_ascii=False, indent=2) + "\n"
    if args.check:
        if not OUTPUT_PATH.exists() or OUTPUT_PATH.read_text(encoding="utf-8") != rendered:
            raise SystemExit("bounded publication allowlist is stale; run builder")
        print("bounded publication allowlist: current")
        return
    OUTPUT_PATH.write_text(rendered, encoding="utf-8")
    print(f"wrote {OUTPUT_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
