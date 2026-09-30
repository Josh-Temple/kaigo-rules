#!/usr/bin/env python3
"""Validate the pinned dayrehab Ordinance 37 independent audit record."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
RECORD = DATA / "dayrehab-ordinance37-independent-audit.json"
SHA_RE = re.compile(r"^[0-9a-f]{40}$")


def fail(message: str) -> None:
    raise SystemExit("dayrehab Ordinance 37 audit validation failed: " + message)


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
    if record.get("service_id") != "dayrehab" or record.get("layer") != "ordinance37":
        fail("unexpected service/layer")
    if record.get("audit_kind") != "INDEPENDENT_EGOV_CONTENT_REPARSE":
        fail("unexpected audit kind")
    if record.get("audit_result") != "PASS":
        fail("audit result is not PASS")

    run = record.get("audit_run", {})
    if run.get("parser") != "python_xml_dom_minidom":
        fail("unexpected parser")
    if not isinstance(run.get("run_id"), int) or run["run_id"] <= 0:
        fail("invalid run_id")
    if not SHA_RE.fullmatch(str(run.get("head_sha") or "")):
        fail("invalid head_sha")
    if not re.fullmatch(r"[0-9a-f]{64}", str(run.get("verification_report_sha256") or "")):
        fail("invalid verification report sha256")

    safety = record.get("safety", {})
    if safety.get("human_verified") is not False:
        fail("must not claim human verification")
    if safety.get("verified_current") is not False:
        fail("must not claim VERIFIED_CURRENT")
    if safety.get("automatic_promotion_allowed") is not False:
        fail("automatic promotion must remain disabled")

    scope = load(DATA / "services/dayrehab/ordinance37-scope.json")
    index = load(DATA / "services/dayrehab/ordinance37-index.generated.json")
    meta = load(DATA / "ordinance37-meta.json")
    nodes = load(DATA / "ordinance37-nodes.json")
    relations = load(DATA / "ordinance37-relations.json")

    expected_articles = scope["direct_scope"]["article_numbers"]
    if record.get("target_articles") != expected_articles:
        fail("target article list differs from service scope")
    if index.get("selectors", {}).get("resolved_direct_articles") != expected_articles:
        fail("generated index article list differs from service scope")
    if record.get("source", {}).get("observed_xml_sha256") != meta.get("xml_sha256"):
        fail("audited live XML hash differs from committed metadata")
    if record.get("source", {}).get("current_revision_id") != meta.get("current_revision", {}).get("law_revision_id"):
        fail("audited revision differs from committed current revision")

    node_ids = set(index.get("node_ids", []))
    selected = [row for row in nodes if row.get("id") in node_ids]
    contains = [
        row for row in relations
        if row.get("relation") == "contains"
        and row.get("from") in node_ids
        and row.get("to") in node_ids
    ]
    observed = record.get("observed", {})
    if len(selected) != observed.get("nodes"):
        fail("node count changed")
    if len(contains) != observed.get("contains_relations"):
        fail("contains relation count changed")
    counts = {}
    for row in selected:
        counts[row.get("node_type")] = counts.get(row.get("node_type"), 0) + 1
    for node_type, field in {
        "article": "articles",
        "paragraph": "paragraphs",
        "item": "items",
        "subitem": "subitems",
    }.items():
        if counts.get(node_type, 0) != observed.get(field):
            fail(f"{node_type} count changed")

    for relative, expected_blob in record.get("input_git_blob_shas_at_audit", {}).items():
        path = ROOT / relative
        if not path.exists():
            fail(f"pinned audit input missing: {relative}")
        if git_blob_sha1(path) != expected_blob:
            fail(f"pinned audit input changed: {relative}")

    print("dayrehab Ordinance 37 independent audit: valid")


if __name__ == "__main__":
    main()
