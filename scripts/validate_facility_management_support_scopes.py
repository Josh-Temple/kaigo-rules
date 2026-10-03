#!/usr/bin/env python3
"""Fail-closed validation for Chat E service-specific shared-source scopes."""
from __future__ import annotations
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
TARGETS = (
    "elderly-welfare-facility",
    "elderly-health-facility",
    "care-medical-institution",
    "care-management",
    "preventive-support",
)
SCOPE_KEYS = {
    "care_insurance_act": "care-insurance-act-scope.json",
    "governing_standards": "governing-standards-scope.json",
    "remuneration": "remuneration-scope.json",
    "delegated_remuneration_criteria": "delegated-remuneration-criteria-scope.json",
    "unit_price_regional_classification": "unit-price-scope.json",
}
FORBIDDEN_BODY_KEYS = {"official_text", "article_body", "body_text", "source_body", "full_text"}
PROMOTED_STATES = {"PASS", "VERIFIED", "HUMAN_VERIFIED", "REVIEWED", "PUBLISHED", "AVAILABLE", "CURRENT", "ESTABLISHED"}

def load(relative: str) -> Any:
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))

def walk(value: Any):
    if isinstance(value, dict):
        for key, child in value.items():
            yield key, child
            yield from walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk(child)

def article_sets(nodes: list[dict]) -> tuple[set[str], set[tuple[str, str]]]:
    articles = {str(row["article_num"]) for row in nodes if row.get("node_type") == "article" and row.get("article_num") is not None}
    paragraphs = {(str(row["article_num"]), str(row["paragraph_num"])) for row in nodes if row.get("node_type") == "paragraph" and row.get("article_num") is not None and row.get("paragraph_num") is not None}
    return articles, paragraphs

def selector_articles(selector: dict) -> list[str]:
    if selector.get("article") is not None:
        return [str(selector["article"])]
    return [str(x) for x in selector.get("articles", [])]

def validate_all() -> list[str]:
    errors: list[str] = []
    care_nodes = load("data/care-insurance-act-nodes.json")
    care_articles, care_paragraphs = article_sets(care_nodes)

    for sid in TARGETS:
        config_path = f"data/services/{sid}.json"
        config = load(config_path)
        refs = config.get("scope_files") or {}
        if config.get("service_id") != sid:
            errors.append(f"{config_path}: service_id mismatch")

        for key, filename in SCOPE_KEYS.items():
            expected = f"data/services/{sid}/{filename}"
            if refs.get(key) != expected:
                errors.append(f"{config_path}: {key} ref must be {expected}")
            if not (ROOT / expected).exists():
                errors.append(f"{expected}: referenced scope file missing")
                continue
            scope = load(expected)
            if scope.get("service_id") != sid:
                errors.append(f"{expected}: service_id mismatch")
            if scope.get("automatic_verification_promotion_allowed") is not False:
                errors.append(f"{expected}: automatic verification promotion must be false")
            if scope.get("source_text_duplicated") is not False:
                errors.append(f"{expected}: source_text_duplicated must be false")
            for found_key, found_value in walk(scope):
                if found_key in FORBIDDEN_BODY_KEYS:
                    errors.append(f"{expected}: source-body key is forbidden: {found_key}")
                if found_key in {"service_applicability","relation_verification","currentness","human_review","publication","verification_status","item_level_service_applicability"} and isinstance(found_value, str) and found_value.upper() in PROMOTED_STATES:
                    errors.append(f"{expected}: state promotion is forbidden: {found_key}={found_value}")

        care_path = refs.get("care_insurance_act")
        if care_path and (ROOT / care_path).exists():
            care = load(care_path)
            for row in care.get("service_definition_scope", []):
                article = str(row["article"])
                if article not in care_articles:
                    errors.append(f"{care_path}: Care Act article missing: {article}")
                for paragraph in row.get("paragraphs", []):
                    if (article, str(paragraph)) not in care_paragraphs:
                        errors.append(f"{care_path}: Care Act paragraph missing: {article}({paragraph})")
            for row in care.get("benefit_scope", []):
                article = str(row["article"])
                if article not in care_articles:
                    errors.append(f"{care_path}: Care Act benefit article missing: {article}")
                paragraph = row.get("paragraph")
                if paragraph is not None and (article, str(paragraph)) not in care_paragraphs:
                    errors.append(f"{care_path}: Care Act benefit paragraph missing: {article}({paragraph})")
            endpoints = care.get("provider_governance_scope", {}).get("article_range", {})
            for endpoint in ("from", "through"):
                article = str(endpoints.get(endpoint, ""))
                if article not in care_articles:
                    errors.append(f"{care_path}: Care Act governance endpoint missing: {article}")

        standards_path = refs.get("governing_standards")
        if standards_path and (ROOT / standards_path).exists():
            standards = load(standards_path)
            nodes_path = standards.get("shared_corpus", {}).get("nodes")
            if not nodes_path or not (ROOT / nodes_path).exists():
                errors.append(f"{standards_path}: shared nodes path missing")
                continue
            nodes = load(nodes_path)
            articles, paragraphs = article_sets(nodes)
            declared = [str(x) for x in standards.get("corpus_membership", {}).get("article_numbers", [])]
            if not declared:
                errors.append(f"{standards_path}: corpus membership must not be empty")
            missing = sorted(set(declared) - articles)
            if missing:
                errors.append(f"{standards_path}: corpus article refs missing: {missing}")
            for article in standards.get("common_direct_scope", {}).get("article_numbers", []):
                if str(article) not in articles:
                    errors.append(f"{standards_path}: common direct article missing: {article}")
            for variant in standards.get("service_variants", []):
                direct = variant.get("article_numbers")
                if direct is None:
                    direct = variant.get("direct_scope", {}).get("article_numbers", [])
                for article in direct or []:
                    if str(article) not in articles:
                        errors.append(f"{standards_path}: direct article missing: {article}")
                inc = variant.get("incorporated_scope") or {}
                via = inc.get("via_node_id")
                if via and not any(row.get("id") == via for row in nodes):
                    errors.append(f"{standards_path}: incorporation via node missing: {via}")
                for article in inc.get("source_article_numbers", []):
                    if str(article) not in articles:
                        errors.append(f"{standards_path}: incorporated article missing: {article}")
                for exclusion in inc.get("exclusions", []):
                    article = str(exclusion["article"])
                    if article not in articles:
                        errors.append(f"{standards_path}: exclusion article missing: {article}")
                    for paragraph in exclusion.get("paragraphs", []):
                        if (article, str(paragraph)) not in paragraphs:
                            errors.append(f"{standards_path}: exclusion paragraph missing: {article}({paragraph})")
                for rule in variant.get("read_as_rules", []):
                    via = rule.get("via_node_id")
                    if via and not any(row.get("id") == via for row in nodes):
                        errors.append(f"{standards_path}: read-as via node missing: {via}")
                    for article in selector_articles(rule.get("selector") or {}):
                        if article not in articles:
                            errors.append(f"{standards_path}: read-as selector article missing: {article}")
                    if not rule.get("from") or not rule.get("to"):
                        errors.append(f"{standards_path}: read-as rule requires from/to")

        delegated_path = refs.get("delegated_remuneration_criteria")
        if delegated_path and (ROOT / delegated_path).exists():
            delegated = load(delegated_path)
            if delegated.get("status") != "SCOPE_PARTIAL_ITEM_RELATIONS_NOT_ESTABLISHED":
                errors.append(f"{delegated_path}: delegated scope must remain partial")
            if delegated.get("unresolved", {}).get("state") != "ITEM_LEVEL_RELATION_MAPPING_REQUIRED":
                errors.append(f"{delegated_path}: unresolved item relation must remain explicit")

        unit_path = refs.get("unit_price_regional_classification")
        if unit_path and (ROOT / unit_path).exists():
            unit = load(unit_path)
            binding = unit.get("service_rate_binding", {})
            if binding.get("must_not_reuse") != "data/unit-price-dayservice.json":
                errors.append(f"{unit_path}: dayservice rate table reuse must be explicitly forbidden")
            if binding.get("state") != "TARGET_SERVICE_RATE_NOT_STRUCTURED_IN_EXISTING_SHARED_CORPUS":
                errors.append(f"{unit_path}: target service rate must remain not-ingested")
    return errors

def main() -> None:
    errors = validate_all()
    if errors:
        raise SystemExit("\n".join(errors))
    print(f"facility/management/support scopes: PASS ({len(TARGETS)} services, {len(TARGETS) * len(SCOPE_KEYS)} lanes)")

if __name__ == "__main__":
    main()
