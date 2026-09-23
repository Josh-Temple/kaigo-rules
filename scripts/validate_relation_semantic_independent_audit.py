#!/usr/bin/env python3
"""Validate pinned provenance for the independent relation-semantic audit."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
RECORD = DATA / "relation-semantic-independent-audit.json"

RELATION_FILES = [
    "care-insurance-act-relations.json",
    "fee-guidance-relations.json",
    "notice-ordinance-relations.json",
    "ordinance37-relations.json",
    "relationships.json",
    "remuneration-delegated-relations.json",
    "remuneration-relations.json",
]


def fail(message: str) -> None:
    raise SystemExit("relation semantic independent audit validation failed: " + message)


def load(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        fail(f"cannot read valid JSON from {path.relative_to(ROOT)}: {exc}")


def git_blob_sha1(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def target_sort_key(value: str):
    return tuple(int(part) for part in value.split("-"))


def main() -> None:
    record = load(RECORD)

    if record.get("scope") != "explicit-legal-reference-relations-ordinance37-article105":
        fail("unexpected scope")
    if record.get("audit_kind") != "INDEPENDENT_EXPLICIT_LEGAL_REFERENCE_AUDIT":
        fail("unexpected audit kind")
    if record.get("audit_result") != "PASS":
        fail("audit result is not PASS")

    run = record.get("audit_run", {})
    if run.get("run_id") != 35929830286:
        fail("unexpected audit run")
    if run.get("head_sha") != "dd8e10b7fc6d186f33537cb79fa7252fdfbde5a4":
        fail("unexpected audited head SHA")
    if run.get("parser") != "python_xml_dom_minidom_plus_independent_japanese_article_reference_parser":
        fail("unexpected independent parser")
    if run.get("artifact_digest") != "sha256:c79f4415ea3c7014fe4f5982578230ee05d78ca801940c8aea6a4439101a92f5":
        fail("unexpected audit artifact digest")

    safety = record.get("safety", {})
    if safety.get("human_verified") is not False or safety.get("verified_current") is not False:
        fail("independent audit must not claim human/current verification")
    if safety.get("automatic_promotion_allowed") is not False:
        fail("automatic promotion must remain disabled")
    if safety.get("promotes_unverified_semantic_mappings") is not False:
        fail("unverified semantic mappings must not be promoted")

    checks = record.get("checks", [])
    if len(checks) != 1:
        fail("expected exactly one explicit-reference audit lane")
    check = checks[0]
    if check.get("id") != "ordinance37-article105-incorporation":
        fail("unexpected audit check")
    if check.get("result") != "PASS" or check.get("differences") != []:
        fail("explicit Article 105 relation audit is not clean")
    if check.get("relation") != "incorporates_by_reference":
        fail("unexpected audited relation type")

    ordinance_relations = load(DATA / "ordinance37-relations.json")
    current_targets = sorted(
        {
            str(row["to"]).removeprefix("ordinance37.article.")
            for row in ordinance_relations
            if row.get("from") == "ordinance37.article.105"
            and row.get("relation") == "incorporates_by_reference"
            and str(row.get("to", "")).startswith("ordinance37.article.")
        },
        key=target_sort_key,
    )
    expected_targets = check.get("expected_relation_targets", [])
    observed_targets = check.get("observed_article_targets", [])
    if current_targets != expected_targets or current_targets != observed_targets:
        fail("Article 105 incorporation target set changed")
    if len(current_targets) != 23 or check.get("relation_count") != 23:
        fail("Article 105 incorporation relation count is not 23")

    structural_total = 0
    semantic_total = 0
    for name in RELATION_FILES:
        relations = load(DATA / name)
        structural = sum(1 for row in relations if row.get("relation") == "contains")
        structural_total += structural
        semantic_total += len(relations) - structural

    coverage = record.get("coverage", {})
    if structural_total != coverage.get("source_derived_structural_contains_relations"):
        fail("structural relation inventory changed")
    if semantic_total != coverage.get("non_contains_semantic_or_cross_layer_relations"):
        fail("semantic/cross-layer relation inventory changed")
    verified = coverage.get("explicit_legal_reference_relations_independently_verified")
    remaining = coverage.get("semantic_or_cross_layer_relations_not_yet_independently_verified")
    if verified != 23 or remaining != semantic_total - verified:
        fail("relation audit coverage arithmetic changed")

    for relative, expected_blob in record.get("input_git_blob_shas_at_audit", {}).items():
        path = ROOT / relative
        if not path.exists():
            fail(f"pinned audit input missing: {relative}")
        if git_blob_sha1(path) != expected_blob:
            fail(f"pinned audit input changed: {relative}")

    print(
        "relation semantic independent audit: OK "
        "(Article 105 explicit incorporation 23/23 PASS; remaining semantic mappings unpromoted)"
    )


if __name__ == "__main__":
    main()
