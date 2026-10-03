#!/usr/bin/env python3
"""Validate fail-closed standards-interpretation staging datasets."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

ALLOWED_CONTENT_STATES = {
    "SOURCE_CONTENT_STRUCTURED",
    "GAP_SCOPE_RESOLVED_FROM_PRIMARY_SOURCES",
    "GAP_SCOPE_PARTIALLY_RESOLVED_FROM_PRIMARY_SOURCES",
}


def fail(message: str) -> None:
    raise SystemExit("standards-interpretation staging validation failed: " + message)


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--service-id", required=True)
    parser.add_argument("--expected-items", type=int, required=True)
    args = parser.parse_args()

    service_id = args.service_id
    config = load(ROOT / f"data/services/{service_id}.json")
    scope = load(
        ROOT / f"data/services/{service_id}/standards-interpretation-scope.json"
    )
    dataset = load(
        ROOT / f"data/services/{service_id}/standards-interpretation-staging.json"
    )

    if config.get("service_id") != service_id:
        fail("config service mismatch")
    if scope.get("service_id") != service_id:
        fail("scope service mismatch")
    if dataset.get("service_id") != service_id:
        fail("dataset service mismatch")

    if dataset.get("dataset_role") != "WORK_CONTROL_ACCEPTED_STAGING_ADAPTER":
        fail("unexpected dataset role")
    if dataset.get("publication_state") != "NOT_PUBLIC":
        fail("staging dataset must remain non-public")
    if dataset.get("currentness_state") != "NOT_ESTABLISHED":
        fail("dataset currentness was promoted")
    if dataset.get("human_review_state") != "NOT_REVIEWED":
        fail("dataset human review was promoted")

    items = dataset.get("items", [])
    if dataset.get("item_count") != args.expected_items or len(items) != args.expected_items:
        fail("item count mismatch")

    manifest_urls = {
        row.get("url")
        for row in scope.get("source_manifest", [])
        if row.get("url")
    }
    manifest_urls.update(scope.get("source_urls", []))

    seen_ids = set()
    seen_tasks = set()
    for item in items:
        item_id = item.get("id")
        task_id = item.get("task_id")
        if not item_id or item_id in seen_ids:
            fail(f"duplicate or missing item id: {item_id}")
        if not task_id or task_id in seen_tasks:
            fail(f"duplicate or missing task id: {task_id}")
        seen_ids.add(item_id)
        seen_tasks.add(task_id)

        if "body_text" in item:
            fail(f"{task_id}: staging summary must not masquerade as official body_text")
        if not item.get("content_summary"):
            fail(f"{task_id}: content summary missing")
        if item.get("content_state") not in ALLOWED_CONTENT_STATES:
            fail(f"{task_id}: unexpected content state")
        if item.get("currentness_state") != "NOT_ESTABLISHED":
            fail(f"{task_id}: currentness promoted")
        if item.get("human_review_state") != "NOT_REVIEWED":
            fail(f"{task_id}: human review promoted")
        if not item.get("source_locator"):
            fail(f"{task_id}: source locator missing")
        urls = item.get("source_urls", [])
        if not urls:
            fail(f"{task_id}: source URLs missing")
        unknown = sorted(set(urls) - manifest_urls)
        if unknown:
            fail(f"{task_id}: source URLs are not pinned in scope manifest: {unknown}")

    publication = config.get("publication_gate", {})
    if publication.get("content_ingested") is not False:
        fail("content_ingested must remain false")
    if publication.get("public_routes_enabled") is not False:
        fail("public routes must remain false")
    if publication.get("independent_verification_complete") is not False:
        fail("independent verification must remain false")

    print(
        f"{service_id} standards-interpretation staging: OK "
        f"({args.expected_items} items; non-public; currentness NOT_ESTABLISHED)"
    )


if __name__ == "__main__":
    main()
