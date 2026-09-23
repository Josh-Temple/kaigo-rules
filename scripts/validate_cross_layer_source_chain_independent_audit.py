#!/usr/bin/env python3
"""Validate pinned provenance for the cross-layer source-chain audit."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
RECORD = DATA / "cross-layer-source-chain-independent-audit.json"
PHASE1 = DATA / "relation-semantic-independent-audit.json"
PHASE2 = DATA / "careact-internal-relation-independent-audit.json"


def fail(message: str) -> None:
    raise SystemExit("cross-layer source-chain audit validation failed: " + message)


def load(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        fail(f"cannot read valid JSON from {path.relative_to(ROOT)}: {exc}")


def git_blob_sha1(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def sort_article(value: str):
    return tuple(int(part) for part in value.split("-"))


def equivalent_mhlw_doc_route(left: str, right: str) -> bool:
    a = urlparse(left)
    b = urlparse(right)
    if (a.scheme, a.netloc, a.path) != (b.scheme, b.netloc, b.path):
        return False
    qa = parse_qs(a.query)
    qb = parse_qs(b.query)
    return (
        qa.get("dataId") == qb.get("dataId")
        and qa.get("dataType") == qb.get("dataType")
    )


def main() -> None:
    record = load(RECORD)
    phase1 = load(PHASE1)
    phase2 = load(PHASE2)

    if record.get("scope") != "careact-to-remuneration-and-ordinance37-source-chains":
        fail("unexpected scope")
    if record.get("audit_kind") != "INDEPENDENT_CROSS_LAYER_SOURCE_CHAIN_AUDIT":
        fail("unexpected audit kind")
    if record.get("audit_result") != "PASS":
        fail("audit result is not PASS")

    run = record.get("audit_run", {})
    if run.get("run_id") != 35931363483:
        fail("unexpected audit run")
    if run.get("head_sha") != "9b3eb34fd5e8a665a424431d5a08907b355a50e1":
        fail("unexpected audited head SHA")
    if run.get("artifact_digest") != "sha256:2889e2b7a491a8a428538fbcd60b9edc97875a15544139fa2418f6151a4da875":
        fail("unexpected audit artifact digest")
    parsers = run.get("parsers", {})
    if parsers.get("egov_xml") != "python_xml_dom_minidom":
        fail("unexpected e-Gov parser")
    if parsers.get("mhlw_html") != "python_stdlib_html_parser":
        fail("unexpected MHLW parser")

    safety = record.get("safety", {})
    if safety.get("human_verified") is not False or safety.get("verified_current") is not False:
        fail("audit must not claim human/current verification")
    if safety.get("automatic_promotion_allowed") is not False:
        fail("automatic promotion must remain disabled")
    if safety.get("promotes_other_semantic_mappings") is not False:
        fail("other semantic mappings must remain unpromoted")

    checks = {row.get("id"): row for row in record.get("checks", [])}
    expected_ids = {
        "careact41-to-notice19-dayservice-fee",
        "careact74-to-ordinance37-dayservice-direct-standards",
    }
    if set(checks) != expected_ids:
        fail("unexpected check set")
    if any(row.get("result") != "PASS" or row.get("differences") != [] for row in checks.values()):
        fail("source-chain checks are not clean")

    care_meta = load(DATA / "care-insurance-act-meta.json")
    ord_meta = load(DATA / "ordinance37-meta.json")
    fee_meta = load(DATA / "remuneration-current-text-meta.json")
    sources = load(DATA / "sources.json")
    skeleton = load(DATA / "remuneration-current-skeleton.json")
    scope = load(DATA / "ordinance37-scope.json")
    relations = load(DATA / "care-insurance-act-relations.json")

    fee_check = checks["careact41-to-notice19-dayservice-fee"]
    if care_meta.get("xml_sha256") != fee_check.get("careact_source_sha256"):
        fail("Care Insurance Act source hash changed")
    if fee_meta.get("source_sha256") != fee_check.get("notice19_source_sha256"):
        fail("Notice 19 source hash changed")
    if fee_meta.get("source_id") != "mhlw-fee-notice19-base":
        fail("Notice 19 source ID changed")
    if fee_meta.get("section") != "6 通所介護費":
        fail("Notice 19 day-service section changed")

    source_row = next(
        (row for row in sources if row.get("id") == "mhlw-fee-notice19-base"),
        None,
    )
    if source_row is None:
        fail("Notice 19 source manifest row missing")
    if not equivalent_mhlw_doc_route(
        str(source_row.get("url", "")),
        str(fee_meta.get("source_url", "")),
    ):
        fail("Notice 19 source route changed")

    root = next((row for row in skeleton if row.get("id") == "fee.dayservice.root"), None)
    if root is None:
        fail("fee.dayservice.root missing")
    if root.get("source_id") != "mhlw-fee-notice19-base":
        fail("fee.dayservice.root source mapping changed")
    if root.get("title") != "通所介護費":
        fail("fee.dayservice.root title changed")

    fee_relations = [
        row for row in relations
        if row.get("from") == "careact.article.41.p.4.i.1"
        and row.get("relation") == "authorizes_fee_standard_for"
        and row.get("to") == "fee.dayservice.root"
    ]
    if len(fee_relations) != 1:
        fail("fee-authority relation cardinality changed")

    delegation_check = checks["careact74-to-ordinance37-dayservice-direct-standards"]
    if care_meta.get("xml_sha256") != delegation_check.get("careact_source_sha256"):
        fail("Care Insurance Act hash differs in delegation lane")
    if ord_meta.get("xml_sha256") != delegation_check.get("ordinance37_source_sha256"):
        fail("Ordinance 37 source hash changed")
    if ord_meta.get("law_title") != delegation_check.get("ordinance37_evidence", {}).get("law_title"):
        fail("Ordinance 37 title changed")

    expected_targets = delegation_check.get("committed_relation_targets", [])
    if scope.get("direct_articles") != expected_targets:
        fail("Ordinance 37 committed direct scope changed")

    current_targets = sorted(
        {
            str(row["to"]).removeprefix("ordinance37.article.")
            for row in relations
            if row.get("from") == "careact.article.74"
            and row.get("relation") == "delegates_standards_to"
            and str(row.get("to", "")).startswith("ordinance37.article.")
        },
        key=sort_article,
    )
    if current_targets != expected_targets:
        fail("Article 74 delegated target set changed")
    if delegation_check.get("relation_count") != 17 or len(current_targets) != 17:
        fail("Article 74 delegated relation count changed")

    if phase1.get("audit_result") != "PASS":
        fail("phase-1 relation audit is not PASS")
    if phase2.get("audit_result") != "PASS":
        fail("phase-2 relation audit is not PASS")
    if phase1.get("coverage", {}).get("explicit_legal_reference_relations_independently_verified") != 23:
        fail("phase-1 verified count changed")
    if phase2.get("coverage", {}).get("aggregate_explicit_relations_independently_verified") != 27:
        fail("phase-2 aggregate count changed")

    coverage = record.get("coverage", {})
    if coverage.get("relations_in_this_lane") != 18 or coverage.get("relations_passed") != 18:
        fail("phase-3 lane coverage changed")
    if coverage.get("previous_explicit_relations_independently_verified") != 27:
        fail("prior verified count changed")
    if coverage.get("aggregate_relations_independently_verified") != 45:
        fail("aggregate verified relation count changed")
    if coverage.get("non_contains_semantic_or_cross_layer_relations_current_inventory") != 163:
        fail("semantic relation inventory changed")
    if coverage.get("remaining_semantic_or_cross_layer_relations_not_independently_verified") != 118:
        fail("remaining unverified relation count changed")

    for relative, expected_blob in record.get("input_git_blob_shas_at_audit", {}).items():
        path = ROOT / relative
        if not path.exists():
            fail(f"pinned audit input missing: {relative}")
        if git_blob_sha1(path) != expected_blob:
            fail(f"pinned audit input changed: {relative}")

    print(
        "cross-layer source-chain audit: OK "
        "(18/18 PASS; aggregate independent semantic relation coverage 45/163)"
    )


if __name__ == "__main__":
    main()
