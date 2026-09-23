#!/usr/bin/env python3
"""Validate pinned provenance for the Care Insurance Act internal relation audit."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
RECORD = DATA / "careact-internal-relation-independent-audit.json"
PHASE1 = DATA / "relation-semantic-independent-audit.json"


def fail(message: str) -> None:
    raise SystemExit("Care Act internal relation audit validation failed: " + message)


def load(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        fail(f"cannot read valid JSON from {path.relative_to(ROOT)}: {exc}")


def git_blob_sha1(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def normalized_text(value: str) -> str:
    return " ".join(str(value).split())


def main() -> None:
    record = load(RECORD)
    phase1 = load(PHASE1)

    if record.get("scope") != "care-insurance-act-internal-relations-to-article74":
        fail("unexpected scope")
    if record.get("audit_kind") != "INDEPENDENT_CAREACT_INTERNAL_RELATION_AUDIT":
        fail("unexpected audit kind")
    if record.get("audit_result") != "PASS":
        fail("audit result is not PASS")

    run = record.get("audit_run", {})
    if run.get("run_id") != 35930443080:
        fail("unexpected audit run")
    if run.get("head_sha") != "54c49e94f46b4e46bf1d23f9a016f61ab699ff96":
        fail("unexpected audited head SHA")
    if run.get("parser") != "python_xml_dom_minidom_plus_explicit_reference_evidence_rules":
        fail("unexpected independent parser")
    if run.get("artifact_digest") != "sha256:6d5c4ea0402d62e866a0bc008ed37e2ac2c90ef324b079dfecee7f646d9da424":
        fail("unexpected audit artifact digest")

    source = record.get("source", {})
    if source.get("law_id") != "409AC0000000123":
        fail("unexpected Care Insurance Act law ID")
    if source.get("xml_sha256") != "e323026237027e02f02cb883548c36c725126915afc36cd9f8a46fccc28dc6dc":
        fail("unexpected live e-Gov source hash")

    safety = record.get("safety", {})
    if safety.get("human_verified") is not False or safety.get("verified_current") is not False:
        fail("independent audit must not claim human/current verification")
    if safety.get("automatic_promotion_allowed") is not False:
        fail("automatic promotion must remain disabled")
    if safety.get("promotes_other_semantic_mappings") is not False:
        fail("other semantic mappings must remain unpromoted")

    expected_checks = {
        "careact-article70-designation-requires-standards": (
            "careact.article.70",
            "designation_requires_standards",
            "careact.article.74",
        ),
        "careact-article73-requires-compliance-with": (
            "careact.article.73",
            "requires_compliance_with",
            "careact.article.74",
        ),
        "careact-article76-2-enforces": (
            "careact.article.76-2",
            "enforces",
            "careact.article.74",
        ),
        "careact-article77-sanctions-noncompliance": (
            "careact.article.77",
            "sanctions_noncompliance_with",
            "careact.article.74",
        ),
    }

    checks = {row.get("id"): row for row in record.get("checks", [])}
    if set(checks) != set(expected_checks):
        fail("unexpected audit check set")

    relations = load(DATA / "care-insurance-act-relations.json")
    nodes = {row.get("id"): row for row in load(DATA / "care-insurance-act-nodes.json")}

    for check_id, expected in expected_checks.items():
        check = checks[check_id]
        source_id, relation, target_id = expected
        if check.get("result") != "PASS" or check.get("differences") != []:
            fail(f"{check_id}: audit check not clean")
        if (
            check.get("source_article_id"),
            check.get("relation"),
            check.get("target_id"),
        ) != expected:
            fail(f"{check_id}: relation identity changed")

        matching = [
            row
            for row in relations
            if row.get("from") == source_id
            and row.get("relation") == relation
            and row.get("to") == target_id
        ]
        if len(matching) != 1:
            fail(f"{check_id}: committed relation cardinality changed")

        node = nodes.get(source_id)
        if node is None:
            fail(f"{check_id}: committed source node missing")
        text = normalized_text(node.get("official_text", ""))
        if hashlib.sha256(text.encode("utf-8")).hexdigest() != check.get("source_text_sha256"):
            fail(f"{check_id}: committed source text changed")

        missing = [
            pattern for pattern in check.get("required_all_patterns", [])
            if pattern not in text
        ]
        if missing:
            fail(f"{check_id}: required source evidence missing")

        required_any = check.get("required_any_patterns", [])
        if required_any and not any(pattern in text for pattern in required_any):
            fail(f"{check_id}: operative source evidence missing")

    if checks["careact-article73-requires-compliance-with"].get("relative_next_article_target") != "74":
        fail("Article 73 relative-reference resolution changed")

    if phase1.get("audit_result") != "PASS":
        fail("phase-1 explicit relation audit is not PASS")
    phase1_coverage = phase1.get("coverage", {})
    if phase1_coverage.get("explicit_legal_reference_relations_independently_verified") != 23:
        fail("phase-1 verified relation count changed")

    coverage = record.get("coverage", {})
    if coverage.get("relations_in_this_lane") != 4 or coverage.get("relations_passed") != 4:
        fail("phase-2 lane coverage changed")
    if coverage.get("phase1_explicit_relations_independently_verified") != 23:
        fail("phase-1 count mismatch in phase-2 record")
    if coverage.get("aggregate_explicit_relations_independently_verified") != 27:
        fail("aggregate explicit relation coverage changed")
    if coverage.get("non_contains_semantic_or_cross_layer_relations_current_inventory") != 163:
        fail("semantic relation inventory changed")
    if coverage.get("remaining_semantic_or_cross_layer_relations_not_independently_verified") != 136:
        fail("remaining unverified relation count changed")

    for relative, expected_blob in record.get("input_git_blob_shas_at_audit", {}).items():
        path = ROOT / relative
        if not path.exists():
            fail(f"pinned audit input missing: {relative}")
        if git_blob_sha1(path) != expected_blob:
            fail(f"pinned audit input changed: {relative}")

    print(
        "Care Act internal relation audit: OK "
        "(4/4 Article 74 dependency relations PASS; aggregate explicit coverage 27/163)"
    )


if __name__ == "__main__":
    main()
