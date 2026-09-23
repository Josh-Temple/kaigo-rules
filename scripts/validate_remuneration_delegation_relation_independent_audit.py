#!/usr/bin/env python3
"""Validate pinned provenance for remuneration delegation relation audit."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
RECORD = DATA / "remuneration-delegation-relation-independent-audit.json"

EXPECTED = {
    ("fee.dayservice.note.1", "calculation_controlled_by", "calc27.dayservice.1.capacity"),
    ("fee.dayservice.note.1", "calculation_controlled_by", "calc27.dayservice.1.staffing"),
    ("fee.dayservice.note.10", "criteria_set_by", "criteria95.dayservice.14-6"),
    ("fee.dayservice.note.11", "criteria_set_by", "criteria95.dayservice.15"),
    ("fee.dayservice.note.13", "criteria_set_by", "criteria95.dayservice.16"),
    ("fee.dayservice.note.15", "criteria_set_by", "criteria95.dayservice.17"),
    ("fee.dayservice.note.17", "criteria_set_by", "criteria95.dayservice.18-2"),
    ("fee.dayservice.note.18", "criteria_set_by", "criteria95.dayservice.19"),
    ("fee.dayservice.service-provision", "criteria_set_by", "criteria95.dayservice.23"),
    ("fee.dayservice.treatment-improvement", "criteria_set_by", "criteria95.dayservice.24"),
    ("criteria95.dayservice.24", "incorporates_by_reference", "criteria95.shared.4"),
}

def fail(message: str) -> None:
    raise SystemExit("remuneration delegation relation audit validation failed: " + message)

def load(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        fail(f"cannot read valid JSON from {path.relative_to(ROOT)}: {exc}")

def git_blob_sha1(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()

def main() -> None:
    record = load(RECORD)
    if record.get("scope") != "remuneration-delegation-relations-explicit-primary-source":
        fail("unexpected scope")
    if record.get("audit_kind") != "INDEPENDENT_REMUNERATION_DELEGATION_RELATION_AUDIT":
        fail("unexpected audit kind")
    if record.get("audit_result") != "PASS":
        fail("audit result is not PASS")

    run = record.get("audit_run", {})
    if run.get("run_id") != 35931965818:
        fail("unexpected audit run")
    if run.get("head_sha") != "556b765ecc565511f8004ed98270ce4c03fcc284":
        fail("unexpected audited head SHA")
    if run.get("parser") != "python_stdlib_htmlparser_plus_explicit_title_and_reference_rules":
        fail("unexpected parser")
    if run.get("artifact_digest") != "sha256:3f57c1e55b1ea9eb1f01a1a2bac8f19185d05c0ed975c27e94db0ebffddcfa6f":
        fail("unexpected artifact digest")

    expected_hashes = {
        "notice19": "e189120c253f72d2d5dab24dfe7118bad7d602f0baba3d8cdf98a58c7ecc5bbd",
        "notice27": "222c91e52c7978377047104de2c374c26f5dd2aabfd6376cfe7a8caf1a8c1ff3",
        "notice95": "7f1006dd10ce1260b75dec5fe226972af1769ba1502803ba5d58b71d54ae5618",
    }
    for key, expected in expected_hashes.items():
        if record.get("sources", {}).get(key, {}).get("sha256") != expected:
            fail(f"{key} source hash changed in pinned record")

    checks = record.get("checks", [])
    observed = {
        (row.get("from_id"), row.get("relation"), row.get("to_id"))
        for row in checks
        if row.get("result") == "PASS" and row.get("differences") == []
    }
    if observed != EXPECTED or len(checks) != 11:
        fail("covered relation set changed")

    relations = load(DATA / "remuneration-delegated-relations.json")
    committed = {
        (row.get("from_id"), row.get("relation"), row.get("to_id"))
        for row in relations
    }
    if not EXPECTED.issubset(committed):
        fail("one or more audited committed relations changed or disappeared")

    previous = load(DATA / "cross-layer-source-chain-independent-audit.json")
    if previous.get("audit_result") != "PASS":
        fail("previous cross-layer audit is not PASS")
    prev_cov = previous.get("coverage", {})
    if prev_cov.get("aggregate_relations_independently_verified") != 45:
        fail("previous aggregate relation coverage changed")
    if prev_cov.get("non_contains_semantic_or_cross_layer_relations_current_inventory") != 163:
        fail("semantic relation inventory changed before this lane")

    cov = record.get("coverage", {})
    if cov.get("relations_in_this_lane") != 11 or cov.get("relations_passed") != 11:
        fail("lane coverage changed")
    if cov.get("aggregate_explicit_relations_independently_verified") != 56:
        fail("aggregate relation coverage changed")
    if cov.get("remaining_semantic_or_cross_layer_relations_not_independently_verified") != 107:
        fail("remaining relation count changed")

    safety = record.get("safety", {})
    if safety.get("human_verified") is not False or safety.get("verified_current") is not False:
        fail("audit must not claim human/current verification")
    if safety.get("automatic_promotion_allowed") is not False:
        fail("automatic promotion must remain disabled")
    if safety.get("promotes_other_semantic_mappings") is not False:
        fail("other mappings must remain unpromoted")

    for relative, expected_blob in record.get("input_git_blob_shas_at_audit", {}).items():
        path = ROOT / relative
        if not path.exists():
            fail(f"pinned input missing: {relative}")
        if git_blob_sha1(path) != expected_blob:
            fail(f"pinned input changed: {relative}")

    print("remuneration delegation relation audit: OK (11/11 PASS; aggregate explicit relation coverage 56/163)")

if __name__ == "__main__":
    main()
