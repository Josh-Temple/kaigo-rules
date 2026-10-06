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
RUNTIME_SUPPORTED_SOURCE_FAMILIES = {"governing_standards_ordinance"}
MAX_PUBLICATION_CELLS = 10


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
        and not row.get("blocking_reasons")
    ]
    publishable = [
        row for row in ready
        if row.get("source_family") in RUNTIME_SUPPORTED_SOURCE_FAMILIES
    ][:MAX_PUBLICATION_CELLS]

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
            "READY publication units supported by the shared runtime policy are "
            "bound across UI, search, API, and machine retrieval."
        )
    else:
        decision = "DEFER_PUBLICATION_FAIL_CLOSED"
        reason = (
            "READY candidates exist, but none are supported by the currently "
            "implemented runtime publication policy."
        )

    return {
        "format_version": 3,
        "generated_by": "scripts/build_bounded_publication_allowlist.py",
        "role": "Publication Runtime Binding / Progressive Release Worker",
        "source_readiness": {
            "path": "data/publication-readiness.generated.json",
            "git_blob_sha": git_blob_sha(READINESS_PATH),
            "expected_ready_candidate_count": len(ready),
        },
        "runtime_binding": {
            "required_for_nonempty_publication": True,
            "established": True,
            "policy_module": "lib/publication-policy.ts",
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
            "blocker_counts_at_selection": readiness.get("summary", {}).get("blocking_axis_counts", {}),
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
