#!/usr/bin/env python3
"""Build the bounded publication decision from current readiness.

The current application does not yet enforce this allowlist across every public
runtime surface. Until that binding is established, READY candidates remain
review candidates and publication/route deltas stay empty.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
READINESS_PATH = ROOT / "data/publication-readiness.generated.json"
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

def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))

def git_blob_sha(path: Path) -> str:
    body = path.read_bytes()
    header = f"blob {len(body)}\0".encode("utf-8")
    return hashlib.sha1(header + body).hexdigest()

def build() -> dict:
    readiness = load_json(READINESS_PATH)
    ready = [
        row for row in readiness.get("cells", [])
        if row.get("readiness") == "READY_FOR_PUBLICATION_REVIEW"
    ]
    ready_count = len(ready)
    reason = (
        "No READY_FOR_PUBLICATION_REVIEW cells exist after integrated readiness regeneration."
        if ready_count == 0
        else
        "READY candidates exist, but repository-wide runtime enforcement of the bounded publication allowlist across UI, search, API, and machine retrieval is not established. Publication therefore remains fail-closed."
    )
    decision = "NO_PUBLICATION_CHANGE" if ready_count == 0 else "DEFER_PUBLICATION_FAIL_CLOSED"
    return {
        "format_version": 2,
        "generated_by": "scripts/build_bounded_publication_allowlist.py",
        "role": "Semantic Integrator / Bounded Publication Release Worker",
        "source_readiness": {
            "path": "data/publication-readiness.generated.json",
            "git_blob_sha": git_blob_sha(READINESS_PATH),
            "expected_ready_candidate_count": ready_count,
        },
        "runtime_binding": {
            "required_for_nonempty_publication": True,
            "established": False,
            "required_surfaces": [
                "UI",
                "SEARCH",
                "API",
                "MACHINE_RETRIEVAL",
            ],
            "blocker": "RUNTIME_PUBLICATION_ALLOWLIST_BINDING_NOT_ESTABLISHED",
        },
        "policy": {
            "explicit_publication_allowlist_required": True,
            "explicit_route_allowlist_required": True,
            "max_publication_cells": 10,
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
            "ready_candidates_at_selection": ready_count,
            "ready_candidate_cells": [
                {
                    "service_id": row["service_id"],
                    "source_family": row["source_family"],
                    "ready_publication_units": row.get("ready_publication_units", []),
                }
                for row in ready
            ],
            "published_cells_added": 0,
            "routes_added": 0,
            "existing_public_surfaces_changed": False,
            "decision": decision,
            "reason": reason,
            "blocker_counts_at_selection": readiness.get("summary", {}).get("blocking_axis_counts", {}),
        },
        "publication_cell_allowlist": [],
        "route_allowlist": [],
        "field_allowlist_by_cell": {},
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
