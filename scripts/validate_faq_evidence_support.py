#!/usr/bin/env python3
"""Validate the contract between curated FAQ evidence and canonical制度 datasets."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

SUPPORT_FILES = {
    "data/rule-nodes.json",
    "data/notice-nodes.json",
    "data/qa-items.json",
}
CONTEXT_PATH = DATA / "context-packages" / "dayservice-questions.generated.json"
QUESTION_PAGE = ROOT / "app" / "questions" / "[slug]" / "page.tsx"


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def legacy_rule_article_num(node_id: str) -> str | None:
    match = re.match(r"^ordinance37\.article([0-9]+(?:-[0-9]+)?)(?:\.|$)", node_id)
    return match.group(1) if match else None


def validate() -> list[str]:
    errors: list[str] = []

    manifest_path = DATA / "faq-evidence-support-manifest.json"
    if not manifest_path.exists():
        return ["FAQ evidence support manifest is missing"]

    manifest = load_json(manifest_path)
    if manifest.get("contract") != "FAQ_PRESENTATION_SUPPORT":
        errors.append("manifest: unexpected contract")
    if manifest.get("canonical_authority") is not False:
        errors.append("manifest: canonical_authority must be false")

    policy = manifest.get("policy") or {}
    for key, expected in {
        "may_assert_layer_currentness": False,
        "may_assert_layer_human_review_completion": False,
        "must_keep_layer_assurance_separate": True,
        "must_link_back_to_canonical_layer_when_available": True,
    }.items():
        if policy.get(key) is not expected:
            errors.append(f"manifest policy: {key} must be {expected}")

    file_rows = manifest.get("files") or []
    declared = {row.get("path") for row in file_rows}
    if declared != SUPPORT_FILES:
        errors.append(
            "manifest files: expected exactly "
            + ", ".join(sorted(SUPPORT_FILES))
            + f"; got {sorted(x for x in declared if x)}"
        )

    rows_by_path = {row.get("path"): row for row in file_rows}
    for path in SUPPORT_FILES:
        row = rows_by_path.get(path)
        if not row:
            continue
        if row.get("status_semantics") != "FAQ_EVIDENCE_LOCAL_ONLY":
            errors.append(f"{path}: status_semantics must be FAQ_EVIDENCE_LOCAL_ONLY")
        canonical = row.get("canonical_dataset")
        if not canonical or not (ROOT / canonical).exists():
            errors.append(f"{path}: canonical_dataset missing: {canonical}")

    questions = load_json(DATA / "questions.json")
    rules = load_json(DATA / "rule-nodes.json")
    notices = load_json(DATA / "notice-nodes.json")
    qa_items = load_json(DATA / "qa-items.json")
    sources = load_json(DATA / "sources.json")
    ordinance = load_json(DATA / "ordinance37-nodes.json")

    rule_by_id = {row["id"]: row for row in rules}
    notice_by_id = {row["id"]: row for row in notices}
    qa_by_id = {row["id"]: row for row in qa_items}
    source_ids = {row["id"] for row in sources}
    canonical_articles = {
        row["article_num"]
        for row in ordinance
        if row.get("node_type") == "article" and row.get("article_num")
    }

    referenced_rules: set[str] = set()

    for question in questions:
        slug = question.get("slug", "(missing slug)")
        rule_ids = question.get("rule_node_ids") or []
        notice_ids = question.get("notice_node_ids") or []
        qa_ids = question.get("qa_item_ids") or []
        source_refs = question.get("source_refs") or []

        referenced_rules.update(rule_ids)

        if question.get("status") == "verified":
            if not question.get("last_verified"):
                errors.append(f"question {slug}: verified without last_verified")
            evidence_count = len(rule_ids) + len(notice_ids) + len(qa_ids) + len(source_refs)
            if evidence_count == 0:
                errors.append(f"question {slug}: verified without evidence")

        for node_id in rule_ids:
            if node_id not in rule_by_id:
                errors.append(f"question {slug}: missing FAQ support rule {node_id}")
        for node_id in notice_ids:
            if node_id not in notice_by_id:
                errors.append(f"question {slug}: missing FAQ support notice {node_id}")
        for node_id in qa_ids:
            if node_id not in qa_by_id:
                errors.append(f"question {slug}: missing FAQ support Q&A {node_id}")
        for ref in source_refs:
            source_id = ref.get("source_id")
            if source_id not in source_ids:
                errors.append(f"question {slug}: missing official source {source_id}")

    for row in rules:
        source_id = row.get("source_id")
        if source_id not in source_ids:
            errors.append(f"rule support {row.get('id')}: missing source {source_id}")

    for row in notices:
        for source_id in row.get("source_ids") or []:
            if source_id not in source_ids:
                errors.append(f"notice support {row.get('id')}: missing source {source_id}")

    for row in qa_items:
        source_id = row.get("source_id")
        if source_id not in source_ids:
            errors.append(f"Q&A support {row.get('id')}: missing source {source_id}")

    rule_manifest = rows_by_path.get("data/rule-nodes.json") or {}
    exceptions = {
        row.get("id"): row.get("reason")
        for row in rule_manifest.get("canonical_scope_exceptions") or []
        if row.get("id")
    }

    for node_id in sorted(referenced_rules):
        article = legacy_rule_article_num(node_id)
        if not article:
            errors.append(f"rule support {node_id}: cannot derive canonical article route")
            continue
        if article in canonical_articles:
            if node_id in exceptions:
                errors.append(
                    f"rule support {node_id}: stale canonical-scope exception; "
                    f"/rules/{article} now exists"
                )
        elif node_id not in exceptions:
            errors.append(
                f"rule support {node_id}: canonical article /rules/{article} is absent "
                "and no explicit exception is declared"
            )

    for node_id, reason in exceptions.items():
        if node_id not in referenced_rules:
            errors.append(f"rule support exception {node_id}: no longer referenced by a FAQ")
        if not reason:
            errors.append(f"rule support exception {node_id}: missing reason")

    if not QUESTION_PAGE.exists():
        errors.append("FAQ detail page is missing")
    else:
        page = QUESTION_PAGE.read_text(encoding="utf-8")
        for token in (
            "FAQ根拠対応を確認済み",
            "根拠資料全体の確認状態は別です",
            "基準省令DBで現在の条文と確認状態を見る",
            "解釈通知DBの再構成・現行性を見る",
            "国Q&A DBで収載状態を見る",
        ):
            if token not in page:
                errors.append(f"FAQ detail page: missing contract text/link: {token}")

    if not CONTEXT_PATH.exists():
        errors.append("question context package is missing")
    else:
        context = load_json(CONTEXT_PATH)
        context_policy = context.get("policy") or {}
        if context_policy.get("faq_evidence_role") != "FAQ_PRESENTATION_SUPPORT":
            errors.append("question context policy: faq_evidence_role is missing")
        if context_policy.get("support_evidence_is_canonical_layer_status") is not False:
            errors.append(
                "question context policy: support_evidence_is_canonical_layer_status must be false"
            )

        for package in context.get("packages") or []:
            package_id = package.get("package_id", "(missing package_id)")
            assurance = package.get("assurance") or {}
            if assurance.get("evidence_status_scope") != "FAQ_PRESENTATION_SUPPORT_ONLY":
                errors.append(f"{package_id}: missing evidence_status_scope")
            evidence = package.get("evidence") or {}
            for group in ("rules", "notices", "qa_items"):
                for item in evidence.get(group) or []:
                    if item.get("evidence_role") != "FAQ_PRESENTATION_SUPPORT":
                        errors.append(
                            f"{package_id}: {group} {item.get('id')} missing evidence_role"
                        )
                    if item.get("canonical_authority") is not False:
                        errors.append(
                            f"{package_id}: {group} {item.get('id')} canonical_authority must be false"
                        )

    return errors


def main() -> None:
    errors = validate()
    if errors:
        raise SystemExit("\n".join(errors))
    print("FAQ evidence support contract: PASS")


if __name__ == "__main__":
    main()
