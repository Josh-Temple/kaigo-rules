#!/usr/bin/env python3
"""Validate explicit bounded-publication and route allowlists."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
READINESS_PATH = DATA / "publication-readiness.generated.json"
GOVERNING_CURRENTNESS_PATH = DATA / "verification/bounded-currentness-closure-worker-b.json"
HIGH_VALUE_CURRENTNESS_PATH = DATA / "verification/high-value-currentness-closure-worker-b.json"
ALLOWLIST_PATH = DATA / "bounded-publication-allowlist.json"

SAFE_FIELDS = {
    "source_text",
    "item_body",
    "source_metadata",
    "source_locator",
    "currentness_statement",
    "service_applicability_statement",
}
RUNTIME_SOURCE_IDENTITIES = {
    "ordinance37",
    "preventive-services-standards",
    "mhlw-unit-price-current",
}
RUNTIME_SOURCE_FAMILIES = {
    "governing_standards_ordinance",
    "unit_price_regional_classification",
}
FORBIDDEN_FIELDS = {
    "cross_layer_relation_assertion",
    "unverified_relation_assertion",
    "review_dependent_explanatory_text",
    "relation_rank_feature",
    "review_dependent_search_term",
}
MAX_ALLOWED_CELLS = 32


class BoundedPublicationError(ValueError):
    pass


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

    if canonical_source_id not in RUNTIME_SOURCE_IDENTITIES:
        return False
    if source_family not in RUNTIME_SOURCE_FAMILIES:
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


def load_promotions() -> dict[tuple[str | None, str | None], dict[str, Any]]:
    promotions: dict[tuple[str | None, str | None], dict[str, Any]] = {}
    for path in (GOVERNING_CURRENTNESS_PATH, HIGH_VALUE_CURRENTNESS_PATH):
        payload = load_json(path)
        for row in payload.get("promotions", []):
            key = cell_key(row)
            if key in promotions:
                raise BoundedPublicationError(
                    f"duplicate currentness promotion: {key}"
                )
            promotions[key] = row
    return promotions


def validate(
    allowlist: dict[str, Any] | None = None,
    readiness: dict[str, Any] | None = None,
    readiness_blob_sha: str | None = None,
    governing_blob_sha: str | None = None,
    high_value_blob_sha: str | None = None,
) -> dict[str, Any]:
    allowlist = allowlist if allowlist is not None else load_json(ALLOWLIST_PATH)
    readiness = readiness if readiness is not None else load_json(READINESS_PATH)
    readiness_blob_sha = readiness_blob_sha or git_blob_sha(READINESS_PATH)
    governing_blob_sha = governing_blob_sha or git_blob_sha(GOVERNING_CURRENTNESS_PATH)
    high_value_blob_sha = high_value_blob_sha or git_blob_sha(HIGH_VALUE_CURRENTNESS_PATH)

    policy = allowlist.get("policy", {})
    required_true = (
        "explicit_publication_allowlist_required",
        "explicit_route_allowlist_required",
        "publication_does_not_enable_route",
        "blocked_cells_cannot_be_published",
        "allowlist_must_be_subset_of_ready_candidates",
        "unverified_relation_assertions_forbidden",
        "unreviewed_explanatory_text_forbidden",
        "search_and_machine_retrieval_must_respect_publication_allowlist",
        "preventive_services_group_with_non_preventive_counterpart",
        "preventive_support_is_standalone",
        "existing_public_surfaces_must_not_be_removed_by_zero_candidate_run",
        "runtime_binding_required_for_nonempty_publication",
    )
    for key in required_true:
        if policy.get(key) is not True:
            raise BoundedPublicationError(f"unsafe bounded-publication policy: {key}")

    source = allowlist.get("source_readiness", {})
    if source.get("path") != "data/publication-readiness.generated.json":
        raise BoundedPublicationError("unexpected readiness source path")
    if source.get("git_blob_sha") != readiness_blob_sha:
        raise BoundedPublicationError(
            "readiness artifact changed after bounded-publication selection; regenerate allowlist"
        )

    currentness_source = allowlist.get("source_currentness", {})
    if currentness_source.get("path") != "data/verification/bounded-currentness-closure-worker-b.json":
        raise BoundedPublicationError("unexpected primary currentness source path")
    if currentness_source.get("git_blob_sha") != governing_blob_sha:
        raise BoundedPublicationError(
            "primary currentness artifact changed after selection; regenerate allowlist"
        )
    additions = currentness_source.get("additional_sources") or []
    expected_additions = [
        {
            "path": "data/verification/high-value-currentness-closure-worker-b.json",
            "git_blob_sha": high_value_blob_sha,
        }
    ]
    if additions != expected_additions:
        raise BoundedPublicationError(
            "additional currentness sources do not match the runtime contract"
        )

    rows = readiness.get("cells")
    if not isinstance(rows, list):
        raise BoundedPublicationError("readiness cells missing")
    by_key: dict[tuple[str | None, str | None], dict[str, Any]] = {}
    for row in rows:
        key = cell_key(row)
        if key in by_key:
            raise BoundedPublicationError(f"duplicate readiness cell: {key}")
        by_key[key] = row

    ready = {
        key
        for key, row in by_key.items()
        if row.get("readiness") == "READY_FOR_PUBLICATION_REVIEW"
        and not row.get("blocking_reasons")
    }
    if source.get("expected_ready_candidate_count") != len(ready):
        raise BoundedPublicationError(
            "ready candidate count changed; regenerate allowlist"
        )

    publication = allowlist.get("publication_cell_allowlist")
    routes = allowlist.get("route_allowlist")
    fields = allowlist.get("field_allowlist_by_cell")
    if (
        not isinstance(publication, list)
        or not isinstance(routes, list)
        or not isinstance(fields, dict)
    ):
        raise BoundedPublicationError(
            "publication, route, and field allowlists must have canonical container types"
        )

    max_cells = policy.get("max_publication_cells")
    if (
        not isinstance(max_cells, int)
        or max_cells < 0
        or max_cells > MAX_ALLOWED_CELLS
    ):
        raise BoundedPublicationError(
            f"max_publication_cells must be between 0 and {MAX_ALLOWED_CELLS}"
        )
    if len(publication) > max_cells:
        raise BoundedPublicationError(
            "bounded publication batch exceeds max_publication_cells"
        )

    runtime = allowlist.get("runtime_binding") or {}
    if runtime.get("policy_module") != "lib/publication-policy.ts":
        raise BoundedPublicationError("unexpected runtime policy module")
    if runtime.get("adapter_registry_module") != "lib/publication-runtime-adapters.ts":
        raise BoundedPublicationError("multi-source adapter registry is not bound")
    if set(runtime.get("supported_source_identities") or []) != RUNTIME_SOURCE_IDENTITIES:
        raise BoundedPublicationError(
            "runtime supported source identities do not match validator contracts"
        )
    if set(runtime.get("supported_source_families") or []) != RUNTIME_SOURCE_FAMILIES:
        raise BoundedPublicationError(
            "runtime supported source families do not match validator contracts"
        )

    promotions = load_promotions()
    publication_keys: list[tuple[str | None, str | None]] = []
    for item in publication:
        key = cell_key(item)
        if key in publication_keys:
            raise BoundedPublicationError(
                f"duplicate publication cell: {key}"
            )
        publication_keys.append(key)
        row = by_key.get(key)
        if row is None or key not in ready:
            raise BoundedPublicationError(
                f"allowlist contains non-ready cell: {key}"
            )
        promotion = promotions.get(key)
        if not promotion or not source_contract_supported(promotion):
            raise BoundedPublicationError(
                f"published cell lacks a supported runtime source contract: {key}"
            )
    publication_key_set = set(publication_keys)

    if publication and runtime.get("established") is not True:
        raise BoundedPublicationError(
            "nonempty publication requires established runtime allowlist enforcement"
        )
    if publication and runtime.get("required_for_nonempty_publication") is not True:
        raise BoundedPublicationError(
            "runtime binding requirement cannot be disabled"
        )

    route_keys: list[tuple[str | None, str | None]] = []
    for item in routes:
        key = cell_key(item)
        if key in route_keys:
            raise BoundedPublicationError(
                f"duplicate route allowlist cell: {key}"
            )
        route_keys.append(key)
        if key not in publication_key_set:
            raise BoundedPublicationError(
                f"route allowlist is not a subset of publication allowlist: {key}"
            )

    for key in publication_key_set:
        encoded_key = f"{key[0]}|{key[1]}"
        if encoded_key not in fields:
            raise BoundedPublicationError(
                f"published cell lacks an explicit field allowlist: {encoded_key}"
            )

    for encoded_key, cell_fields in fields.items():
        if not isinstance(cell_fields, list):
            raise BoundedPublicationError(
                f"field allowlist must be a list: {encoded_key}"
            )
        selected = set(cell_fields)
        if selected != SAFE_FIELDS:
            raise BoundedPublicationError(
                f"published cell must expose exactly the bounded safe fields: {encoded_key}"
            )
        if selected & FORBIDDEN_FIELDS:
            raise BoundedPublicationError(
                f"forbidden relation/review field exposed: {encoded_key}"
            )
        try:
            service_id, source_family = encoded_key.split("|", 1)
        except ValueError as exc:
            raise BoundedPublicationError(
                f"invalid field allowlist cell key: {encoded_key}"
            ) from exc
        if (service_id, source_family) not in publication_key_set:
            raise BoundedPublicationError(
                f"field allowlist exists for non-published cell: {encoded_key}"
            )

    summary = allowlist.get("summary", {})
    if summary.get("published_cells_added") != len(publication):
        raise BoundedPublicationError(
            "published cell summary does not match allowlist"
        )
    if summary.get("routes_added") != len(routes):
        raise BoundedPublicationError(
            "route summary does not match allowlist"
        )
    if summary.get("existing_public_surfaces_changed") is not False:
        raise BoundedPublicationError(
            "this wave must not silently rewrite existing public surfaces"
        )

    if not ready:
        if publication or routes or fields:
            raise BoundedPublicationError(
                "zero ready candidates must produce zero publication, routes, and field exposure"
            )
        if summary.get("decision") != "NO_PUBLICATION_CHANGE":
            raise BoundedPublicationError(
                "zero-candidate decision must remain NO_PUBLICATION_CHANGE"
            )
    elif not publication:
        if summary.get("decision") != "DEFER_PUBLICATION_FAIL_CLOSED":
            raise BoundedPublicationError(
                "ready-but-unpublished candidates must be explicitly deferred"
            )
    else:
        if summary.get("decision") != "PUBLISH_BOUNDED_READY_UNITS":
            raise BoundedPublicationError(
                "nonempty publication must record the bounded publication decision"
            )
        if set(route_keys) != publication_key_set:
            raise BoundedPublicationError(
                "this progressive release requires explicit route binding for every published cell"
            )

    unit_price_key = ("dayservice", "unit_price_regional_classification")
    if unit_price_key in ready and unit_price_key not in publication_key_set:
        raise BoundedPublicationError(
            "READY dayservice Unit Price cell must be published once the adapter contract is supported"
        )

    return {
        "ready_candidates": len(ready),
        "publication_allowlist_cells": len(publication_key_set),
        "route_allowlist_cells": len(set(route_keys)),
        "field_allowlist_cells": len(fields),
        "runtime_binding_established": runtime.get("established") is True,
        "source_families": sorted(
            {source_family for _, source_family in publication_key_set if source_family}
        ),
    }


def main() -> None:
    result = validate()
    print(
        "bounded publication allowlist: PASS "
        f"({result['ready_candidates']} ready, "
        f"{result['publication_allowlist_cells']} published, "
        f"{result['route_allowlist_cells']} routes, "
        f"families={','.join(result['source_families'])}, "
        f"runtime_binding={result['runtime_binding_established']})"
    )


if __name__ == "__main__":
    main()
