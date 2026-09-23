#!/usr/bin/env python3
"""Independently verify explicit internal relations in the Care Insurance Act.

The production Care Insurance Act importer uses xml.etree.ElementTree and adds
hand-authored semantic relations. This verifier instead uses xml.dom.minidom,
reads live e-Gov XML, and checks only four relations whose target Article 74 is
explicitly referenced (or, for Article 73, referenced as the immediately next
article) in operative source text.

Passing this audit does not constitute HUMAN_VERIFIED or VERIFIED_CURRENT and
does not promote any other semantic/cross-layer relation.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import urllib.request
from pathlib import Path
from xml.dom import Node, minidom

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

LAW_ID = "409AC0000000123"
SOURCE_URL = f"https://laws.e-gov.go.jp/api/1/lawdata/{LAW_ID}"

CHECKS = [
    {
        "id": "careact-article70-designation-requires-standards",
        "source_article_num": "70",
        "source_id": "careact.article.70",
        "relation": "designation_requires_standards",
        "target_id": "careact.article.74",
        "required_all": ["第七十四条第一項", "第七十四条第二項"],
        "required_any": ["指定をしてはならない"],
    },
    {
        "id": "careact-article73-requires-compliance-with",
        "source_article_num": "73",
        "source_id": "careact.article.73",
        "relation": "requires_compliance_with",
        "target_id": "careact.article.74",
        "required_all": [
            "次条第二項に規定する指定居宅サービスの事業の設備及び運営に関する基準に従い"
        ],
        "required_any": [],
        "relative_next_article_target": "74",
    },
    {
        "id": "careact-article76-2-enforces",
        "source_article_num": "76-2",
        "source_id": "careact.article.76-2",
        "relation": "enforces",
        "target_id": "careact.article.74",
        "required_all": ["第七十四条第一項", "第七十四条第二項"],
        "required_any": ["勧告することができる", "命ずることができる"],
    },
    {
        "id": "careact-article77-sanctions-noncompliance",
        "source_article_num": "77",
        "source_id": "careact.article.77",
        "relation": "sanctions_noncompliance_with",
        "target_id": "careact.article.74",
        "required_all": ["第七十四条第一項", "第七十四条第二項"],
        "required_any": ["指定を取り消し", "効力を停止"],
    },
]


def fetch(url: str) -> bytes:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "kaigo-rules-careact-relation-verifier/1.0 (+https://github.com/Josh-Temple/kaigo-rules)"
        },
    )
    with urllib.request.urlopen(request, timeout=90) as response:
        return response.read()


def load(name: str):
    return json.loads((DATA / name).read_text(encoding="utf-8"))


def canonical_num(value: str | None) -> str:
    return str(value or "").strip().replace("_", "-")


def text_of(node) -> str:
    chunks: list[str] = []

    def walk(current):
        for child in current.childNodes:
            if child.nodeType in (Node.TEXT_NODE, Node.CDATA_SECTION_NODE):
                chunks.append(child.data)
            elif child.nodeType == Node.ELEMENT_NODE:
                walk(child)

    walk(node)
    return " ".join("".join(chunks).split())


def main_provision(document):
    found = document.getElementsByTagName("MainProvision")
    if not found:
        raise RuntimeError("MainProvision not found in live e-Gov XML")
    return found[0]


def direct_articles(main):
    return [
        child
        for child in main.childNodes
        if child.nodeType == Node.ELEMENT_NODE and child.tagName == "Article"
    ]


def collect_live_articles(payload: bytes):
    document = minidom.parseString(payload)
    main = main_provision(document)
    ordered: list[str] = []
    by_num: dict[str, str] = {}

    def walk(node):
        for child in node.childNodes:
            if child.nodeType != Node.ELEMENT_NODE:
                continue
            if child.tagName in {"TOC", "SupplProvision", "AmendProvision", "NewProvision"}:
                continue
            if child.tagName == "Article":
                num = canonical_num(child.getAttribute("Num"))
                if num and num not in by_num:
                    ordered.append(num)
                    by_num[num] = text_of(child)
                continue
            walk(child)

    walk(main)
    return ordered, by_num


def next_article_num(ordered: list[str], current: str) -> str | None:
    try:
        index = ordered.index(current)
    except ValueError:
        return None
    if index + 1 >= len(ordered):
        return None
    return ordered[index + 1]


def committed_texts() -> dict[str, str]:
    nodes = load("care-insurance-act-nodes.json")
    wanted = {check["source_id"] for check in CHECKS}
    result = {
        row["id"]: " ".join(str(row.get("official_text", "")).split())
        for row in nodes
        if row.get("id") in wanted
    }
    missing = sorted(wanted - set(result))
    if missing:
        raise RuntimeError("committed Care Insurance Act nodes missing: " + ", ".join(missing))
    return result


def relation_matches(check: dict) -> list[dict]:
    relations = load("care-insurance-act-relations.json")
    return [
        row
        for row in relations
        if row.get("from") == check["source_id"]
        and row.get("relation") == check["relation"]
        and row.get("to") == check["target_id"]
    ]


def evidence_differences(
    check: dict,
    live_text: str,
    committed_text: str,
    ordered_articles: list[str],
) -> list[dict]:
    differences: list[dict] = []

    if live_text != committed_text:
        differences.append(
            {
                "difference": "source_article_text_mismatch",
                "live_sha256": hashlib.sha256(live_text.encode("utf-8")).hexdigest(),
                "committed_sha256": hashlib.sha256(committed_text.encode("utf-8")).hexdigest(),
            }
        )

    missing_required = [
        phrase for phrase in check.get("required_all", []) if phrase not in live_text
    ]
    if missing_required:
        differences.append(
            {
                "difference": "required_source_evidence_missing",
                "missing_patterns": missing_required,
            }
        )

    required_any = check.get("required_any", [])
    if required_any and not any(phrase in live_text for phrase in required_any):
        differences.append(
            {
                "difference": "operative_source_evidence_missing",
                "expected_any_patterns": required_any,
            }
        )

    expected_relative = check.get("relative_next_article_target")
    if expected_relative:
        observed_next = next_article_num(ordered_articles, check["source_article_num"])
        if observed_next != expected_relative:
            differences.append(
                {
                    "difference": "relative_next_article_resolution_mismatch",
                    "expected": expected_relative,
                    "observed": observed_next,
                }
            )

    matches = relation_matches(check)
    if len(matches) != 1:
        differences.append(
            {
                "difference": "committed_relation_cardinality_mismatch",
                "expected": 1,
                "observed": len(matches),
            }
        )

    return differences


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", help="Optional JSON report path")
    args = parser.parse_args()

    checks: list[dict] = []
    errors: list[dict] = []

    try:
        payload = fetch(SOURCE_URL)
        source_sha = hashlib.sha256(payload).hexdigest()
        ordered_articles, live_articles = collect_live_articles(payload)
        committed = committed_texts()

        if "74" not in live_articles:
            raise RuntimeError("target Article 74 missing from live e-Gov XML")

        for config in CHECKS:
            source_num = config["source_article_num"]
            live_text = live_articles.get(source_num)
            if live_text is None:
                checks.append(
                    {
                        "id": config["id"],
                        "source_article_id": config["source_id"],
                        "relation": config["relation"],
                        "target_id": config["target_id"],
                        "result": "FAIL",
                        "differences": [
                            {
                                "difference": "source_article_missing_from_live_xml",
                                "article_num": source_num,
                            }
                        ],
                    }
                )
                continue

            differences = evidence_differences(
                config,
                live_text,
                committed[config["source_id"]],
                ordered_articles,
            )
            checks.append(
                {
                    "id": config["id"],
                    "source_url": SOURCE_URL,
                    "source_xml_sha256": source_sha,
                    "source_article_id": config["source_id"],
                    "relation": config["relation"],
                    "target_id": config["target_id"],
                    "target_article_num": "74",
                    "source_text_sha256": hashlib.sha256(live_text.encode("utf-8")).hexdigest(),
                    "required_all_patterns": config.get("required_all", []),
                    "required_any_patterns": config.get("required_any", []),
                    "relative_next_article_target": config.get("relative_next_article_target"),
                    "result": "PASS" if not differences else "FAIL",
                    "differences": differences,
                }
            )
    except Exception as exc:
        errors.append({"scope": "care-insurance-act-internal-relations", "error": str(exc)})

    passed = sum(1 for row in checks if row.get("result") == "PASS")
    result = (
        "PASS"
        if not errors and len(checks) == len(CHECKS) and passed == len(CHECKS)
        else "FAIL"
    )

    report = {
        "format_version": 1,
        "verification_kind": "INDEPENDENT_CAREACT_INTERNAL_RELATION_AUDIT",
        "parser": "python_xml_dom_minidom_plus_explicit_reference_evidence_rules",
        "result": result,
        "source": {
            "law_id": LAW_ID,
            "url": SOURCE_URL,
            "xml_sha256": checks[0].get("source_xml_sha256") if checks else None,
        },
        "checks": checks,
        "errors": errors,
        "coverage": {
            "relations_in_this_lane": len(CHECKS),
            "relations_passed": passed,
            "previous_explicit_relations_independently_verified": 23,
            "aggregate_explicit_relations_independently_verified": 23 + passed,
            "non_contains_semantic_or_cross_layer_relations_current_inventory": 163,
            "remaining_semantic_or_cross_layer_relations_not_independently_verified": 163 - 23 - passed,
        },
        "safety": {
            "promotes_human_review": False,
            "promotes_verified_current": False,
            "promotes_other_semantic_mappings": False,
            "note": (
                "PASS is limited to four Care Insurance Act internal relations whose "
                "Article 74 dependency is evidenced by the live source text."
            ),
        },
    }

    rendered = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    print(rendered, end="")
    if args.report:
        path = Path(args.report)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(rendered, encoding="utf-8")
    return 0 if result == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
