#!/usr/bin/env python3
"""Validate the explicit bounded-publication and route allowlists."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
READINESS_PATH = DATA / "publication-readiness.generated.json"
ALLOWLIST_PATH = DATA / "bounded-publication-allowlist.json"

SAFE_FIELDS = {
    "source_text",
    "item_body",
    "source_metadata",
    "source_locator",
    "currentness_statement",
    "service_applicability_statement",
}
FORBIDDEN_FIELDS = {
    "cross_layer_relation_assertion",
    "unverified_relation_assertion",
    "review_dependent_explanatory_text",
    "relation_rank_feature",
    "review_dependent_search_term",
}


class BoundedPublicationError(ValueError):
    pass


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def git_blob_sha(path: Path) -> str:
    body = path.read_bytes()
    header = f"blob {len(body)}\0".encode("utf-8")
    return hashlib.sha1(header + body).hexdigest()


def cell_key(row: dict) -> tuple[str, str]:
    return row.get("service_id"), row.get("source_family")


def validate(
    allowlist: dict | None = None,
    readiness: dict | None = None,
    readiness_blob_sha: str | None = None,
) -> dict:
    allowlist = allowlist if allowlist is not None else load_json(ALLOWLIST_PATH)
    readiness = readiness if readiness is not None else load_json(READINESS_PATH)
    readiness_blob_sha = (
        readiness_blob_sha
        if readiness_blob_sha is not None
        else git_blob_sha(READINESS_PATH)
    )

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
    )
    for key in required_true:
        if policy.get(key) is not True:
            raise BoundedPublicationError(f"unsafe bounded-publication policy: {key}")

    source = allowlist.get("source_readiness", {})
    if source.get("path") != "data/publication-readiness.generated.json":
        raise BoundedPublicationError("unexpected readiness source path")
    if source.get("git_blob_sha") != readiness_blob_sha:
        raise BoundedPublicationError(
            "readiness artifact changed after Worker D selection; rerun Worker D against the new canonical readiness"
        )

    rows = readiness.get("cells")
    if not isinstance(rows, list):
        raise BoundedPublicationError("readiness cells missing")

    by_key = {}
    for row in rows:
        key = cell_key(row)
        if key in by_key:
            raise BoundedPublicationError(f"duplicate readiness cell: {key}")
        by_key[key] = row

    ready = {
        key
        for key, row in by_key.items()
        if row.get("readiness") == "READY_FOR_PUBLICATION_REVIEW"
    }
    expected_ready = source.get("expected_ready_candidate_count")
    if expected_ready != len(ready):
        raise BoundedPublicationError(
            f"ready candidate count changed: expected {expected_ready}, current {len(ready)}"
        )

    publication = allowlist.get("publication_cell_allowlist")
    routes = allowlist.get("route_allowlist")
    fields = allowlist.get("field_allowlist_by_cell")
    if not isinstance(publication, list):
        raise BoundedPublicationError("publication_cell_allowlist must be a list")
    if not isinstance(routes, list):
        raise BoundedPublicationError("route_allowlist must be a list")
    if not isinstance(fields, dict):
        raise BoundedPublicationError("field_allowlist_by_cell must be an object")

    max_cells = policy.get("max_publication_cells")
    if not isinstance(max_cells, int) or max_cells < 0 or max_cells > 10:
        raise BoundedPublicationError("max_publication_cells must be between 0 and 10")
    if len(publication) > max_cells:
        raise BoundedPublicationError("bounded publication batch exceeds max_publication_cells")

    publication_keys = []
    for item in publication:
        key = cell_key(item)
        if key in publication_keys:
            raise BoundedPublicationError(f"duplicate publication cell: {key}")
        publication_keys.append(key)
        row = by_key.get(key)
        if row is None:
            raise BoundedPublicationError(f"unknown publication cell: {key}")
        if key not in ready:
            raise BoundedPublicationError(f"allowlist contains non-ready cell: {key}")
        if row.get("blocking_reasons"):
            raise BoundedPublicationError(f"allowlist contains blocked cell: {key}")

    publication_key_set = set(publication_keys)

    route_keys = []
    for item in routes:
        key = cell_key(item)
        if key in route_keys:
            raise BoundedPublicationError(f"duplicate route allowlist cell: {key}")
        route_keys.append(key)
        if key not in publication_key_set:
            raise BoundedPublicationError(
                f"route allowlist is not a subset of publication allowlist: {key}"
            )

    for encoded_key, cell_fields in fields.items():
        if not isinstance(cell_fields, list):
            raise BoundedPublicationError(f"field allowlist must be a list: {encoded_key}")
        selected = set(cell_fields)
        if selected - SAFE_FIELDS:
            raise BoundedPublicationError(
                f"field allowlist contains unsafe or unknown fields: {encoded_key}: {sorted(selected - SAFE_FIELDS)}"
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

    if not ready:
        if publication or routes or fields:
            raise BoundedPublicationError(
                "zero ready candidates must produce zero publication, routes, and field exposure"
            )
        summary = allowlist.get("summary", {})
        if summary.get("published_cells_added") != 0:
            raise BoundedPublicationError("zero-candidate run must add zero publication cells")
        if summary.get("routes_added") != 0:
            raise BoundedPublicationError("zero-candidate run must add zero routes")
        if summary.get("existing_public_surfaces_changed") is not False:
            raise BoundedPublicationError(
                "zero-candidate run must preserve existing public surfaces"
            )

    return {
        "ready_candidates": len(ready),
        "publication_allowlist_cells": len(publication_key_set),
        "route_allowlist_cells": len(set(route_keys)),
        "field_allowlist_cells": len(fields),
        "existing_public_surfaces_changed": allowlist.get("summary", {}).get(
            "existing_public_surfaces_changed"
        ),
    }


def main() -> None:
    result = validate()
    print(
        "bounded publication allowlist: PASS "
        f"({result['ready_candidates']} ready, "
        f"{result['publication_allowlist_cells']} published, "
        f"{result['route_allowlist_cells']} routes)"
    )


if __name__ == "__main__":
    main()
