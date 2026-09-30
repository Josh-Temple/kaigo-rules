#!/usr/bin/env python3
"""Validate pinned provenance for remuneration delegation relation audit."""
from __future__ import annotations
import hashlib
import json
import re
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
    if not isinstance(run.get("run_id"), int) or run["run_id"] <= 0:
        fail("invalid audit run")
    if not re.fullmatch(r"[0-9a-f]{40}", str(run.get("head_sha") or "")):
        fail("invalid audited head SHA")
    if run.get("parser") != "python_stdlib_htmlparser_plus_explicit_title_and_reference_rules":
        fail("unexpected parser")
    if not re.fullmatch(r"[0-9a-f]{64}", str(run.get("verification_report_sha256") or "")):
        fail("invalid verification report sha256")

    expected_urls = {
        "notice19": "https://www.mhlw.go.jp/web/t_doc?dataId=82aa0253&dataType=0",
        "notice27": "https://www.mhlw.go.jp/web/t_doc?dataId=82aa0261&dataType=0&pageNo=1",
        "notice95": "https://www.mhlw.go.jp/web/t_doc?dataId=82ab4584&dataType=0&pageNo=1",
    }
    for key, expected_url in expected_urls.items():
        row = record.get("sources", {}).get(key, {})
        if row.get("url") != expected_url:
            fail(f"{key} source URL changed")
        if not re.fullmatch(r"[0-9a-f]{64}", str(row.get("sha256") or "")):
            fail(f"{key} source hash invalid")

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


    cov = record.get("coverage", {})
    if cov.get("relations_in_this_lane") != 11 or cov.get("relations_passed") != 11:
        fail("lane coverage changed")

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

    print("remuneration delegation relation audit: OK (11/11 PASS; lane provenance valid)")

if __name__ == "__main__":
    main()
