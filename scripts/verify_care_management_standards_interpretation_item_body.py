#!/usr/bin/env python3
"""Validate the bounded care-management standards-interpretation item-body audit.

This verifier is intentionally service-specific. It binds the checked-in audit to
the exact staging/scope/source-inventory inputs and protects the boundary that this
audit does not establish currentness, human review, publication readiness, or a
synthetic integrated notice text.

With --live it also re-fetches the five pinned MHLW sources and verifies their
byte-level SHA-256 identities against the independently pinned source inventory.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SERVICE_ID = "care-management"
EXPECTED_TASKS = 32
EXPECTED_CHILD_ENTRIES = 41
ALLOWED_RESULTS = {"PASS", "PARTIAL", "GAP", "FAIL"}

SCOPE = ROOT / "data/services/care-management/standards-interpretation-scope.json"
STAGING = ROOT / "data/services/care-management/standards-interpretation-staging.json"
INVENTORY = ROOT / "data/verification/standards-interpretation-source-inventory/care-management.json"
AUDIT = ROOT / "data/verification/standards-interpretation-item-body/care-management.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def git_blob_sha(path: Path) -> str:
    body = path.read_bytes()
    return hashlib.sha1(f"blob {len(body)}\0".encode("ascii") + body).hexdigest()


def fail(message: str) -> None:
    raise SystemExit("care-management item-body audit invalid: " + message)


def parse_children(raw: str) -> list[dict[str, str | None]]:
    chunks = re.split(r"\n(?=\s*-\s+path:)", raw)
    rows = []
    for chunk in (c for c in chunks if c.strip()):
        row: dict[str, str | None] = {}
        for key in ("path", "number", "heading", "content_summary", "recovery_state"):
            match = re.search(
                rf"^\s*(?:-\s+)?{re.escape(key)}:\s*(.+)$",
                chunk,
                flags=re.MULTILINE,
            )
            value = match.group(1).strip() if match else None
            if value and len(value) >= 2 and value[0] == value[-1] and value[0] in {"\"", "'"}:
                value = value[1:-1]
            row[key] = value
        rows.append(row)
    return rows


def validate_offline() -> dict:
    scope = load(SCOPE)
    staging = load(STAGING)
    inventory = load(INVENTORY)
    audit = load(AUDIT)

    if audit.get("service_id") != SERVICE_ID:
        fail("service_id mismatch")
    if audit.get("audit_kind") != "INDEPENDENT_STANDARDS_INTERPRETATION_ITEM_BODY_VERIFICATION":
        fail("unexpected audit_kind")
    if audit.get("audit_result") != "PARTIAL_WITH_GAPS":
        fail("audit_result must preserve bounded gaps")

    audit_scope = audit.get("audit_scope", {})
    expected_blobs = {
        "scope_git_blob_sha": git_blob_sha(SCOPE),
        "staging_git_blob_sha": git_blob_sha(STAGING),
        "source_inventory_git_blob_sha": git_blob_sha(INVENTORY),
    }
    for key, value in expected_blobs.items():
        if audit_scope.get(key) != value:
            fail(f"stale input binding: {key}")

    items = staging.get("items", [])
    if len(items) != EXPECTED_TASKS or staging.get("task_count") != EXPECTED_TASKS:
        fail("staging task count changed")
    if audit_scope.get("task_count") != EXPECTED_TASKS:
        fail("audit task count mismatch")

    audit_tasks = audit.get("tasks", [])
    if len(audit_tasks) != EXPECTED_TASKS:
        fail("audit task list count mismatch")
    by_task = {row.get("task_id"): row for row in audit_tasks}
    if len(by_task) != EXPECTED_TASKS:
        fail("duplicate/missing audit task ids")

    observed_child_entries = 0
    task_counts = {key: 0 for key in ("PASS", "PARTIAL", "GAP", "FAIL")}
    child_counts = {key: 0 for key in ("PASS", "PARTIAL", "GAP", "FAIL")}

    for item in items:
        task_id = item.get("task_id")
        row = by_task.get(task_id)
        if row is None:
            fail(f"missing audit row for {task_id}")
        if row.get("item_id") != item.get("id"):
            fail(f"item_id mismatch for {task_id}")
        result = row.get("result")
        if result not in ALLOWED_RESULTS:
            fail(f"invalid result for {task_id}: {result}")
        task_counts[result] += 1

        identity = row.get("staging_identity", {})
        for key in ("path", "number", "heading", "parent", "source_locator", "source_urls", "content_state"):
            if identity.get(key) != item.get(key):
                fail(f"staging identity drift for {task_id}: {key}")

        expected_children = parse_children(item.get("structured_text_raw", ""))
        actual_children = row.get("children", [])
        if len(expected_children) != len(actual_children):
            fail(f"child count mismatch for {task_id}")
        observed_child_entries += len(expected_children)
        for expected, actual in zip(expected_children, actual_children):
            for key in ("path", "number", "heading", "content_summary", "recovery_state"):
                if actual.get(key) != expected.get(key):
                    fail(f"child drift for {task_id}: {key}")
            child_result = actual.get("verification_result")
            if child_result not in ALLOWED_RESULTS:
                fail(f"invalid child result for {task_id}: {child_result}")
            child_counts[child_result] += 1

        axes = row.get("axes", {})
        if axes.get("source_version_separation") != "PASS":
            fail(f"source-version separation not preserved for {task_id}")
        if axes.get("evidence_support") != result:
            fail(f"evidence result mismatch for {task_id}")
        if not row.get("official_evidence"):
            fail(f"missing official evidence metadata for {task_id}")
        if not row.get("finding"):
            fail(f"missing finding for {task_id}")

    if observed_child_entries != EXPECTED_CHILD_ENTRIES:
        fail(f"structured child entry count changed: {observed_child_entries}")
    if audit_scope.get("structured_text_child_entries") != EXPECTED_CHILD_ENTRIES:
        fail("audit child-entry count mismatch")

    summary = audit.get("summary", {})
    if summary.get("task_results") != task_counts:
        fail(f"task result summary mismatch: {task_counts}")
    if summary.get("child_entry_results") != child_counts:
        fail(f"child result summary mismatch: {child_counts}")

    expected_task_counts = {"PASS": 28, "PARTIAL": 2, "GAP": 2, "FAIL": 0}
    expected_child_counts = {"PASS": 37, "PARTIAL": 2, "GAP": 2, "FAIL": 0}
    if task_counts != expected_task_counts:
        fail(f"unexpected task outcomes: {task_counts}")
    if child_counts != expected_child_counts:
        fail(f"unexpected child outcomes: {child_counts}")

    boundaries = audit.get("verification_boundaries", {})
    for key in (
        "current_integrated_notice_text_established",
        "legal_currentness_promoted",
        "human_review_promoted",
        "publication_permitted",
        "omitted_text_inferred",
        "versions_silently_merged",
    ):
        if boundaries.get(key) is not False:
            fail(f"safety boundary weakened: {key}")

    scope_manifest = {row["url"]: row for row in scope.get("source_manifest", [])}
    inventory_sources = {row["url"]: row for row in inventory.get("sources", [])}
    audit_sources = {
        row["url"]: row for row in audit.get("source_version_policy", {}).get("source_roles", [])
    }
    if set(audit_sources) != set(scope_manifest):
        fail("source-role URL set differs from scope manifest")
    for url, source in scope_manifest.items():
        checked = audit_sources[url]
        if checked.get("id") != source.get("id") or checked.get("role") != source.get("role"):
            fail(f"source role drift: {url}")
        if inventory_sources.get(url, {}).get("fetch") != "PASS":
            fail(f"pinned source was not fetchable: {url}")
        if checked.get("pinned_sha256") != inventory_sources[url].get("sha256"):
            fail(f"pinned source hash drift: {url}")

    unresolved = {row.get("task_id"): row.get("result") for row in audit.get("unresolved_gaps", [])}
    if unresolved != {
        "KR2-09-B012": "PARTIAL",
        "KR2-09-B015": "GAP",
        "KR2-09-B017": "GAP",
        "KR2-09-B019": "PARTIAL",
    }:
        fail(f"unresolved gap set changed: {unresolved}")

    config = load(ROOT / "data/services/care-management.json")
    layer = config["ingestion_layers"]["standards_interpretation"]
    if layer.get("item_body_verification") != "PENDING":
        fail("service-level item_body_verification was promoted by this bounded audit")
    if config["publication_gate"].get("public_routes_enabled") is not False:
        fail("public route gate was promoted")
    if config["publication_gate"].get("content_ingested") is not False:
        fail("content publication gate was promoted")

    return {
        "task_counts": task_counts,
        "child_counts": child_counts,
        "audit": audit,
    }


def verify_live_sources(audit: dict) -> None:
    for source in audit["source_version_policy"]["source_roles"]:
        url = source["url"]
        request = urllib.request.Request(
            url,
            headers={
                "User-Agent": "kaigo-rules-care-management-item-body-verifier/2.0",
                "Cache-Control": "no-cache",
            },
        )
        with urllib.request.urlopen(request, timeout=60) as response:
            body = response.read()
        actual = hashlib.sha256(body).hexdigest()
        if actual != source["pinned_sha256"]:
            fail(f"live source bytes changed since pinned inventory: {url}")
    print("care-management item-body live source identities: PASS")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--live",
        action="store_true",
        help="re-fetch MHLW sources and compare byte hashes with the pinned source inventory",
    )
    args = parser.parse_args()
    result = validate_offline()
    if args.live:
        verify_live_sources(result["audit"])
    print(
        "care-management standards-interpretation item-body audit: "
        f"PASS_VALIDATION (tasks={EXPECTED_TASKS}; child_entries={EXPECTED_CHILD_ENTRIES}; "
        f"outcomes={result['task_counts']}; currentness not established)"
    )


if __name__ == "__main__":
    main()
