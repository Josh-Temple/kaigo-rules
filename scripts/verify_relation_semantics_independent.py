#!/usr/bin/env python3
"""Independently verify explicit legal-reference relations.

This verifier intentionally audits only relations whose target article set can be
reconstructed from explicit wording in a primary source. It does not promote
hand-authored semantic mappings, human review, or currentness status.

The first covered lane is Ordinance 37 Article 105. The production importer
uses xml.etree.ElementTree plus a hand-authored scope file; this verifier uses
xml.dom.minidom and derives the incorporated article set directly from the live
Article 105 text.
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

LAW_ID = "411M50000100037"
SOURCE_URL = f"https://laws.e-gov.go.jp/api/1/lawdata/{LAW_ID}"

RELATION_FILES = [
    "care-insurance-act-relations.json",
    "fee-guidance-relations.json",
    "notice-ordinance-relations.json",
    "ordinance37-relations.json",
    "relationships.json",
    "remuneration-delegated-relations.json",
    "remuneration-relations.json",
]

KANJI_DIGITS = {
    "〇": 0,
    "零": 0,
    "一": 1,
    "二": 2,
    "三": 3,
    "四": 4,
    "五": 5,
    "六": 6,
    "七": 7,
    "八": 8,
    "九": 9,
}
KANJI_UNITS = {"十": 10, "百": 100, "千": 1000}
KANJI_NUMBER_CHARS = "".join(KANJI_DIGITS) + "".join(KANJI_UNITS)


def fetch(url: str) -> bytes:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "kaigo-rules-independent-relation-verifier/1.0 (+https://github.com/Josh-Temple/kaigo-rules)"
        },
    )
    with urllib.request.urlopen(request, timeout=90) as response:
        return response.read()


def load(name: str):
    return json.loads((DATA / name).read_text(encoding="utf-8"))


def direct_elements(node, tag_name: str):
    return [
        child
        for child in node.childNodes
        if child.nodeType == Node.ELEMENT_NODE and child.tagName == tag_name
    ]


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


def kanji_to_int(value: str) -> int:
    if value.isdigit():
        return int(value)
    total = 0
    current = 0
    for char in value:
        if char in KANJI_DIGITS:
            current = KANJI_DIGITS[char]
        elif char in KANJI_UNITS:
            total += (current or 1) * KANJI_UNITS[char]
            current = 0
        else:
            raise ValueError(f"unsupported Japanese numeral: {value}")
    return total + current


def article_token(main: str, sub: str | None = None) -> str:
    number = str(kanji_to_int(main))
    if sub:
        number += "-" + str(kanji_to_int(sub))
    return number


def extract_incorporated_articles(article_text: str) -> list[str]:
    marker = "の規定は、指定通所介護の事業について準用する"
    if marker not in article_text:
        raise RuntimeError("Article 105 incorporation clause marker not found")
    clause = article_text.split(marker, 1)[0]

    import re

    pattern = re.compile(
        rf"第([{KANJI_NUMBER_CHARS}]+)条(?:の([{KANJI_NUMBER_CHARS}]+))?"
    )
    matches = list(pattern.finditer(clause))
    result: list[str] = []
    index = 0
    while index < len(matches):
        current = matches[index]
        main = current.group(1)
        sub = current.group(2)

        if index + 1 < len(matches):
            following = matches[index + 1]
            between = clause[current.end() : following.start()]
            after_following = clause[following.end() : following.end() + 3]
            if (
                sub is None
                and following.group(2) is None
                and "から" in between
                and after_following.startswith("まで")
            ):
                start = kanji_to_int(main)
                end = kanji_to_int(following.group(1))
                if end < start:
                    raise RuntimeError(f"descending article range: {start}-{end}")
                result.extend(str(number) for number in range(start, end + 1))
                index += 2
                continue

        result.append(article_token(main, sub))
        index += 1

    return sorted(set(result), key=lambda value: tuple(int(x) for x in value.split("-")))


def live_article_105(payload: bytes) -> str:
    document = minidom.parseString(payload)
    for article in document.getElementsByTagName("Article"):
        if article.getAttribute("Num").replace("_", "-") != "105":
            continue
        paragraphs = direct_elements(article, "Paragraph")
        if not paragraphs:
            raise RuntimeError("Article 105 paragraph not found")
        sentences = direct_elements(paragraphs[0], "ParagraphSentence")
        if not sentences:
            raise RuntimeError("Article 105 paragraph sentence not found")
        return text_of(sentences[0])
    raise RuntimeError("Article 105 not found in live e-Gov XML")


def committed_article_105_text() -> str:
    nodes = load("ordinance37-nodes.json")
    node = next((row for row in nodes if row.get("id") == "ordinance37.article.105"), None)
    if node is None:
        raise RuntimeError("committed ordinance37.article.105 node missing")
    text = str(node.get("official_text", ""))
    marker = "第百五条"
    if marker in text:
        text = text.split(marker, 1)[1].strip()
    return " ".join(text.split())


def expected_article_105_targets() -> list[str]:
    relations = load("ordinance37-relations.json")
    targets = []
    for row in relations:
        if (
            row.get("from") == "ordinance37.article.105"
            and row.get("relation") == "incorporates_by_reference"
            and str(row.get("to", "")).startswith("ordinance37.article.")
        ):
            targets.append(str(row["to"]).removeprefix("ordinance37.article."))
    return sorted(set(targets), key=lambda value: tuple(int(x) for x in value.split("-")))


def relation_inventory() -> tuple[list[dict], int, int]:
    rows = []
    semantic_total = 0
    structural_total = 0
    for name in RELATION_FILES:
        relations = load(name)
        structural = sum(1 for row in relations if row.get("relation") == "contains")
        semantic = len(relations) - structural
        rows.append(
            {
                "file": f"data/{name}",
                "relations_total": len(relations),
                "source_derived_structural_contains": structural,
                "non_contains_semantic_or_cross_layer": semantic,
            }
        )
        structural_total += structural
        semantic_total += semantic
    return rows, structural_total, semantic_total


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", help="Optional JSON report path")
    args = parser.parse_args()

    errors: list[dict] = []
    checks: list[dict] = []
    try:
        payload = fetch(SOURCE_URL)
        source_sha = hashlib.sha256(payload).hexdigest()
        live_text = live_article_105(payload)
        committed_text = committed_article_105_text()
        observed = extract_incorporated_articles(live_text)
        expected = expected_article_105_targets()

        differences = []
        if live_text != committed_text:
            differences.append(
                {
                    "difference": "article_105_text_mismatch",
                    "live_sha256": hashlib.sha256(live_text.encode("utf-8")).hexdigest(),
                    "committed_sha256": hashlib.sha256(committed_text.encode("utf-8")).hexdigest(),
                }
            )
        if observed != expected:
            differences.append(
                {
                    "difference": "incorporated_article_set_mismatch",
                    "observed": observed,
                    "expected": expected,
                    "missing_from_relations": sorted(set(observed) - set(expected)),
                    "unexpected_relations": sorted(set(expected) - set(observed)),
                }
            )

        checks.append(
            {
                "id": "ordinance37-article105-incorporation",
                "source_url": SOURCE_URL,
                "source_xml_sha256": source_sha,
                "source_article_id": "ordinance37.article.105",
                "relation": "incorporates_by_reference",
                "result": "PASS" if not differences else "FAIL",
                "observed_article_targets": observed,
                "expected_relation_targets": expected,
                "relation_count": len(expected),
                "differences": differences,
            }
        )
    except Exception as exc:
        errors.append({"id": "ordinance37-article105-incorporation", "error": str(exc)})

    inventory, structural_total, semantic_total = relation_inventory()
    verified_explicit = (
        checks[0]["relation_count"]
        if checks and checks[0].get("result") == "PASS"
        else 0
    )
    remaining = semantic_total - verified_explicit

    result = (
        "PASS"
        if not errors and checks and all(row.get("result") == "PASS" for row in checks)
        else "FAIL"
    )
    report = {
        "format_version": 1,
        "verification_kind": "INDEPENDENT_EXPLICIT_LEGAL_REFERENCE_AUDIT",
        "parser": "python_xml_dom_minidom_plus_independent_japanese_article_reference_parser",
        "result": result,
        "checks": checks,
        "errors": errors,
        "relation_inventory": inventory,
        "coverage": {
            "source_derived_structural_contains_relations": structural_total,
            "non_contains_semantic_or_cross_layer_relations": semantic_total,
            "explicit_legal_reference_relations_independently_verified": verified_explicit,
            "semantic_or_cross_layer_relations_not_yet_independently_verified": remaining,
        },
        "safety": {
            "promotes_human_review": False,
            "promotes_verified_current": False,
            "promotes_unverified_semantic_mappings": False,
            "note": (
                "PASS applies only to the explicit Article 105 incorporation set. "
                "All remaining semantic/cross-layer mappings retain their existing review status."
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
