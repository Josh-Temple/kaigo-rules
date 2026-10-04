#!/usr/bin/env python3
"""Validate Worker D currentness evidence without promoting downstream gates."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
RECEIPT = ROOT / "data/verification/currentness-evidence-expansion-wave.json"
MATRIX = ROOT / "data/database-coverage-matrix.generated.json"
STANDARDS_MANIFEST = ROOT / "data/shared/standards/manifest.json"
QA_META = ROOT / "data/qa-corpus-meta.json"
SOURCES = ROOT / "data/sources.json"
FEE_EVENTS = ROOT / "data/fee-guidance-amendment-events.json"
RELATION_QUEUE = ROOT / "data/relation-verification-queue.json"

EXPECTED_BASE_SHA = "e0d814b1b22d449fd13784bbb051fba5c27df64e"
EXPECTED_CURRENTNESS = {
    "PARTIAL": 45,
    "BLOCKED": 1,
    "NOT_ESTABLISHED": 303,
    "NOT_APPLICABLE": 2,
}
EXPECTED_QA_PAGE = (
    "https://www.mhlw.go.jp/stf/seisakunitsuite/bunya/"
    "hukushi_kaigo/kaigo_koureisha/qa/index.html"
)
EXPECTED_FEE_SOURCE = "mhlw-r8-fee-guidance-may-amendment"
EXPECTED_FEE_URL = "https://www.mhlw.go.jp/content/001698614.pdf"
EXPECTED_QUEUE_IDENTITY = {
    "from": "fee.dayservice.root",
    "relation": "latest_interpretation_amendment_evidence",
    "to": EXPECTED_FEE_SOURCE,
}

SAFETY_FALSE = (
    "global_generated_artifacts_updated",
    "service_scope_changed",
    "service_applicability_promoted",
    "item_body_promoted",
    "currentness_auto_promoted_to_services",
    "human_review_promoted",
    "publication_promoted",
    "route_enabled",
    "negative_search_used_as_conclusive_proof",
)


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def find_by_id(value: Any, target: str) -> dict[str, Any] | None:
    if isinstance(value, dict):
        if value.get("id") == target:
            return value
        for child in value.values():
            found = find_by_id(child, target)
            if found is not None:
                return found
    elif isinstance(value, list):
        for child in value:
            found = find_by_id(child, target)
            if found is not None:
                return found
    return None


def is_sha256(value: Any) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(
        char in "0123456789abcdef" for char in value
    )


def currentness_counts(matrix: dict[str, Any]) -> tuple[int, dict[str, int]]:
    cells = 0
    counts: dict[str, int] = {}
    for service in matrix.get("services", []):
        for family in service.get("source_families", []):
            cells += 1
            state = family.get("currentness", {}).get("state", "MISSING")
            counts[state] = counts.get(state, 0) + 1
    return cells, counts


def validate_egov_meta(
    errors: list[str],
    label: str,
    path: Path,
) -> None:
    if not path.exists():
        errors.append(f"{label}: missing metadata {path.relative_to(ROOT)}")
        return
    meta = load(path)
    if not str(meta.get("source_api_v1", "")).startswith(
        "https://laws.e-gov.go.jp/api/1/lawdata/"
    ):
        errors.append(f"{label}: source_api_v1 is not the official e-Gov lawdata API")
    if not str(meta.get("source_revisions_v2", "")).startswith(
        "https://laws.e-gov.go.jp/api/2/law_revisions/"
    ):
        errors.append(f"{label}: source_revisions_v2 is not the official e-Gov revisions API")
    if not is_sha256(meta.get("xml_sha256")):
        errors.append(f"{label}: xml_sha256 missing or invalid")
    if not is_sha256(meta.get("revision_response_sha256")):
        errors.append(f"{label}: revision_response_sha256 missing or invalid")
    if not isinstance(meta.get("revision_count"), int) or meta["revision_count"] < 1:
        errors.append(f"{label}: revision_count missing or invalid")

    current = meta.get("current_revision") or {}
    if current.get("current_revision_status") != "CurrentEnforced":
        errors.append(f"{label}: current revision is not CurrentEnforced")
    if current.get("repeal_status") not in (None, "None"):
        errors.append(f"{label}: current revision is marked repealed")
    if not current.get("law_revision_id"):
        errors.append(f"{label}: law_revision_id missing")
    if not current.get("amendment_enforcement_date"):
        errors.append(f"{label}: amendment_enforcement_date missing")


def main() -> int:
    errors: list[str] = []

    receipt = load(RECEIPT)
    if receipt.get("audit_kind") != "CURRENTNESS_EVIDENCE_EXPANSION_WAVE":
        errors.append("unexpected receipt audit_kind")
    if receipt.get("base_main_sha") != EXPECTED_BASE_SHA:
        errors.append("receipt base_main_sha drifted")

    snapshot = receipt.get("coverage_snapshot", {})
    matrix = load(MATRIX)
    cells, counts = currentness_counts(matrix)
    if cells != snapshot.get("cells") or cells != 351:
        errors.append(f"coverage cell count drifted: {cells}")
    if counts != EXPECTED_CURRENTNESS:
        errors.append(f"coverage currentness counts drifted: {counts!r}")
    if snapshot.get("currentness") != EXPECTED_CURRENTNESS:
        errors.append("receipt currentness snapshot differs from expected base snapshot")

    # Shared e-Gov evidence: one Act plus all current standards corpora.
    validate_egov_meta(errors, "care_insurance_act", ROOT / "data/care-insurance-act-meta.json")
    validate_egov_meta(errors, "ordinance37", ROOT / "data/ordinance37-meta.json")

    manifest = load(STANDARDS_MANIFEST)
    corpora = manifest.get("corpora", [])
    if len(corpora) != 9:
        errors.append(f"expected 9 current standards corpora, found {len(corpora)}")
    for entry in corpora:
        corpus_id = entry.get("corpus_id")
        if not corpus_id:
            errors.append("standards manifest entry without corpus_id")
            continue
        if corpus_id == "ordinance37":
            continue
        validate_egov_meta(
            errors,
            corpus_id,
            ROOT / "data/shared/standards" / corpus_id / "meta.json",
        )

    historical = manifest.get("historical_or_special", [])
    if not any(
        row.get("status") == "HISTORICAL_REPEALED_NOT_CURRENT_BASELINE"
        for row in historical
    ):
        errors.append("historical/repealed standards boundary is missing")

    # National Q&A: compilation freshness is distinct from individual-Q&A currentness.
    qa = load(QA_META)
    if qa.get("source_page") != EXPECTED_QA_PAGE:
        errors.append("Q&A official source page drifted")
    if not str(qa.get("source_workbook", "")).startswith("https://www.mhlw.go.jp/"):
        errors.append("Q&A workbook is not an official MHLW URL")
    if not is_sha256(qa.get("source_sha256")):
        errors.append("Q&A source_sha256 missing or invalid")
    if "介護サービスQ＆A集（令和8年9月掲載）" not in qa.get("workbook_sheets", []):
        errors.append("Q&A repository metadata no longer identifies the R8 September workbook")

    # Fee-guidance direct evidence is confirmed, but the freshness-sensitive word
    # "latest" must remain unresolved until direct supersession evidence exists.
    source = find_by_id(load(SOURCES), EXPECTED_FEE_SOURCE)
    if source is None:
        errors.append("R8 May fee-guidance amendment source missing")
    else:
        if source.get("url") != EXPECTED_FEE_URL:
            errors.append("R8 May fee-guidance amendment URL drifted")
        if source.get("status") != "current_amendment":
            errors.append("R8 May fee-guidance source status drifted")

    event = find_by_id(load(FEE_EVENTS), "fee-guidance.r8-may.dayservice.staffing-shortage-exception")
    if event is None:
        errors.append("R8 May fee-guidance amendment event missing")
    else:
        if event.get("source_id") != EXPECTED_FEE_SOURCE:
            errors.append("R8 May amendment event source identity drifted")
        if event.get("effective_from") != "2026-06-01":
            errors.append("R8 May amendment effective date drifted")

    queue = load(RELATION_QUEUE)
    if queue.get("classification_counts", {}).get(
        "SOURCE_LINK_FRESHNESS_OR_DIRECT_EVIDENCE_REQUIRED"
    ) != 1:
        errors.append("source-link freshness queue count changed; Integrator must re-evaluate")

    queue_item = None
    for item in queue.get("items", []):
        if item.get("identity") == EXPECTED_QUEUE_IDENTITY:
            queue_item = item
            break
    if queue_item is None:
        errors.append("expected freshness-sensitive relation queue item missing")
    elif queue_item.get("classification") != "SOURCE_LINK_FRESHNESS_OR_DIRECT_EVIDENCE_REQUIRED":
        errors.append("freshness-sensitive relation was promoted outside this Worker boundary")

    relation = receipt.get("relation_queue", {})
    if relation.get("closed_by_this_worker") is not False:
        errors.append("receipt must keep the freshness-sensitive relation open")

    lanes = {lane.get("source_family"): lane for lane in receipt.get("evidence_lanes", [])}
    for family in ("care_insurance_act", "governing_standards_ordinance", "national_qa", "fee_calculation_guidance"):
        if family not in lanes:
            errors.append(f"missing evidence lane: {family}")
    if lanes.get("fee_calculation_guidance", {}).get("latestness_of_amendment") != "NOT_ESTABLISHED":
        errors.append("fee-guidance latestness must remain NOT_ESTABLISHED")
    if lanes.get("national_qa", {}).get("individual_qa_currentness_inferred") is not False:
        errors.append("individual Q&A currentness must not be inferred from compilation freshness")

    safety = receipt.get("safety", {})
    for key in SAFETY_FALSE:
        if safety.get(key) is not False:
            errors.append(f"safety boundary broken: {key}")

    report = {
        "format_version": 1,
        "validation_kind": "CURRENTNESS_EVIDENCE_EXPANSION_WAVE",
        "result": "PASS" if not errors else "FAIL",
        "errors": errors,
        "observed": {
            "coverage_cells": cells,
            "coverage_currentness": counts,
            "standards_current_corpora": len(corpora),
            "source_freshness_queue_items": queue.get("classification_counts", {}).get(
                "SOURCE_LINK_FRESHNESS_OR_DIRECT_EVIDENCE_REQUIRED"
            ),
        },
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
