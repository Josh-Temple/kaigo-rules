#!/usr/bin/env python3
"""Validate pinned provenance for the independent scoped e-Gov content audit."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
RECORD = DATA / "egov-content-independent-audit.json"


def fail(message: str) -> None:
    raise SystemExit("e-Gov content independent audit validation failed: " + message)


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
    if record.get("scope") != "egov-scoped-content-ordinance37-care-insurance-act":
        fail("unexpected scope")
    if record.get("audit_result") != "PASS":
        fail("audit result is not PASS")
    if record.get("audit_run", {}).get("run_id") != 36210164036:
        fail("unexpected audit run")
    if record.get("audit_run", {}).get("parser") != "python_xml_dom_minidom":
        fail("unexpected independent parser")

    safety = record.get("safety", {})
    if safety.get("human_verified") is not False or safety.get("verified_current") is not False:
        fail("independent audit must not claim human/current verification")
    if safety.get("automatic_promotion_allowed") is not False:
        fail("automatic promotion must remain disabled")

    checks = {row.get("id"): row for row in record.get("checks", [])}
    if set(checks) != {"ordinance37", "care-insurance-act"}:
        fail("expected exactly two audited e-Gov layers")

    expected = {
        "ordinance37": {
            "meta": "ordinance37-meta.json",
            "nodes": "ordinance37-nodes.json",
            "relations": "ordinance37-relations.json",
        },
        "care-insurance-act": {
            "meta": "care-insurance-act-meta.json",
            "nodes": "care-insurance-act-nodes.json",
            "relations": "care-insurance-act-relations.json",
        },
    }

    for layer_id, files in expected.items():
        check = checks[layer_id]
        if check.get("result") != "PASS":
            fail(f"{layer_id}: audit check not PASS")
        meta = load(DATA / files["meta"])
        nodes = load(DATA / files["nodes"])
        relations = load(DATA / files["relations"])
        contains = [row for row in relations if row.get("relation") == "contains"]
        if meta.get("xml_sha256") != check.get("observed_xml_sha256"):
            fail(f"{layer_id}: committed XML hash differs from audited live source")
        observed = check.get("observed", {})
        if len(nodes) != observed.get("nodes"):
            fail(f"{layer_id}: node count changed")
        if len(contains) != observed.get("contains_relations"):
            fail(f"{layer_id}: containment count changed")
        counts = {}
        for row in nodes:
            counts[row.get("node_type")] = counts.get(row.get("node_type"), 0) + 1
        mapping = {
            "article": "articles",
            "paragraph": "paragraphs",
            "item": "items",
            "subitem": "subitems",
        }
        for node_type, key in mapping.items():
            if counts.get(node_type, 0) != observed.get(key):
                fail(f"{layer_id}: {node_type} count changed")

    for relative, expected_blob in record.get("input_git_blob_shas_at_audit", {}).items():
        path = ROOT / relative
        if not path.exists():
            fail(f"pinned audit input missing: {relative}")
        if git_blob_sha1(path) != expected_blob:
            fail(f"pinned audit input changed: {relative}")

    print("e-Gov content independent audit: OK (ordinance37 + care-insurance-act PASS; semantic relations excluded)")


if __name__ == "__main__":
    main()
