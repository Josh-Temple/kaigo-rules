#!/usr/bin/env python3
"""Validate Worker C final Governing Standards and residual relation assurance."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
sys.path.insert(0, str(ROOT / "scripts"))

from build_database_coverage_matrix import build as build_matrix  # noqa: E402

ARTIFACT = DATA / "verification/final-standards-residual-relation-worker-c.json"
PRIOR = DATA / "verification/governing-standards-residual-currentness-worker-a.json"
META = DATA / "shared/standards/community-based-standards/meta.json"
NODES = DATA / "shared/standards/community-based-standards/nodes.json"
AUDIT = DATA / "shared/standards/independent-audit.json"
RELATIONS = DATA / "residual-relation-independent-verification.generated.json"
FRESHNESS = DATA / "relation-freshness-direct-evidence-assessment.json"

TARGETS = {
    "night-homevisit": ("夜間対応型訪問介護", "4", "18"),
    "dementia-group-home": ("認知症対応型共同生活介護", "89", "108"),
}
EXPECTED_RELATION_CLASSIFICATIONS = {
    "SOURCE_LINK_FRESHNESS_OR_DIRECT_EVIDENCE_REQUIRED": 1,
    "SEMANTIC_TEXT_CHECK_REQUIRED": 17,
    "CROSS_LAYER_HUMAN_REVIEW_REQUIRED": 4,
    "HUMAN_SEMANTIC_REVIEW_REQUIRED": 36,
}


def load(path: Path) -> dict | list:
    return json.loads(path.read_text(encoding="utf-8"))


def fail(message: str) -> None:
    raise SystemExit("Worker-C final assurance validation failed: " + message)


def main() -> None:
    artifact = load(ARTIFACT)
    prior = load(PRIOR)
    meta = load(META)
    nodes = load(NODES)
    audit = load(AUDIT)
    relations = load(RELATIONS)
    freshness = load(FRESHNESS)

    if artifact.get("worker") != "C":
        fail("worker identity mismatch")
    if artifact.get("base_main_sha") != "29c5529be51a1211e060acd5911a1122aa0eaf0e":
        fail("base main SHA mismatch")

    source = artifact["governing_standards"]["source_identity"]
    if source.get("law_id") != "418M60000100034":
        fail("canonical law identity changed")
    revision = meta.get("current_revision") or {}
    if revision.get("current_revision_status") != "CurrentEnforced":
        fail("canonical source is not CurrentEnforced")
    if revision.get("repeal_status") != "None":
        fail("canonical source has a repeal state")
    if source.get("version_id") != revision.get("law_revision_id"):
        fail("artifact current version does not match corpus metadata")
    if source.get("xml_sha256") != meta.get("xml_sha256"):
        fail("artifact source fingerprint does not match corpus metadata")

    audit_row = next((x for x in audit.get("checks", []) if x.get("id") == "community-based-standards"), None)
    if not audit_row or audit_row.get("result") != "PASS":
        fail("independent community-based standards audit is not PASS")
    if audit_row.get("observed_xml_sha256") != meta.get("xml_sha256"):
        fail("independent audit fingerprint does not match current corpus")

    articles = {
        str(x.get("article_num")): x
        for x in nodes
        if x.get("node_type") == "article"
    }
    prior_decisions = {x["service_id"]: x for x in prior.get("decisions", [])}
    decisions = {x["service_id"]: x for x in artifact["governing_standards"]["decisions"]}
    if set(decisions) != set(TARGETS):
        fail("final-two decision identity set changed")

    for service_id, (label, start, end) in TARGETS.items():
        decision = decisions[service_id]
        if prior_decisions[service_id].get("item_body_state") != "PASS":
            fail(f"{service_id}: prior item-body state is not PASS")
        if decision.get("decision") != "PROMOTE_PASS_BOUNDED":
            fail(f"{service_id}: decision is not bounded PASS")
        if decision.get("projected_currentness_state") != "PASS" or decision.get("promotion_applied") is not True:
            fail(f"{service_id}: promotion fields are not PASS/applied")
        if decision.get("canonical_source_id") != "community-based-standards":
            fail(f"{service_id}: canonical source mismatch")
        if decision.get("source_family") != "governing_standards_ordinance":
            fail(f"{service_id}: source family mismatch")

        # Resolve legal ranges by article number, never by storage-array position.
        expected_numbers = [str(n) for n in range(int(start), int(end) + 1)]
        missing = [n for n in expected_numbers if n not in articles]
        if missing:
            fail(f"{service_id}: current corpus range has missing articles: {missing}")
        scoped = [articles[n] for n in expected_numbers]
        if any(label not in " ".join(map(str, row.get("path", []))) for row in scoped):
            fail(f"{service_id}: a direct-range article left the service chapter")
        if label not in str(articles[start].get("official_text", "")):
            fail(f"{service_id}: first direct article does not identify service")
        if label not in str(articles[end].get("official_text", "")):
            fail(f"{service_id}: terminal direct article does not identify service")

    before = artifact["governing_standards"]["before"]
    after = artifact["governing_standards"]["after"]
    if (before.get("ready"), before.get("total"), before.get("blocked_currentness")) != (37, 39, 2):
        fail("Governing Standards before counts changed")
    if (after.get("ready"), after.get("total"), after.get("blocked_currentness")) != (39, 39, 0):
        fail("Governing Standards after counts are not 39/39")

    rel_summary = relations.get("summary", {})
    if rel_summary.get("canonical_relations_total") != 188:
        fail("canonical relation total changed")
    if rel_summary.get("independently_verified_after_worker_c") != 130:
        fail("pre-wave verified relation count is not 130")
    if rel_summary.get("remaining_unverified") != 58:
        fail("pre-wave residual relation count is not 58")
    if relations.get("classification_counts") != EXPECTED_RELATION_CLASSIFICATIONS:
        fail("residual relation classification counts changed")

    rel_after = artifact["residual_relations"]["after"]
    if (rel_after.get("verified"), rel_after.get("total"), rel_after.get("remaining")) != (130, 188, 58):
        fail("Worker C relation result must remain 130/188 with 58 unresolved")
    if rel_after.get("classifications") != EXPECTED_RELATION_CLASSIFICATIONS:
        fail("Worker C relation classifications changed")
    lanes = artifact["residual_relations"]["audited_priority_lanes"]
    if lanes["human_semantic_review"].get("promoted") != 0 or lanes["human_semantic_review"].get("candidates") != 36:
        fail("human-semantic relations were promoted")
    if lanes["cross_layer_human_review"].get("promoted") != 0:
        fail("cross-layer human-review relations were promoted")
    if freshness.get("items", [{}])[0].get("closure_assessment") != "KEEP_OPEN":
        fail("latest-amendment freshness relation unexpectedly closed")

    matrix = build_matrix()
    for service_id in TARGETS:
        service = next(x for x in matrix["services"] if x["service_id"] == service_id)
        family = next(x for x in service["source_families"] if x["source_family"] == "governing_standards_ordinance")
        if family["currentness"]["state"] != "PASS":
            fail(f"{service_id}: matrix projection did not reach currentness PASS")
        evidence = family["currentness"].get("evidence", [])
        if not any("final-standards-residual-relation-worker-c.json" in item for item in evidence):
            fail(f"{service_id}: matrix lacks Worker C evidence pointer")

    print("Worker-C final assurance validation: PASS (Governing Standards 39/39; relations 130/188, 58 unresolved)")


if __name__ == "__main__":
    main()
