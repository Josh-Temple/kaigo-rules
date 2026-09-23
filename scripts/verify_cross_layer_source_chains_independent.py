#!/usr/bin/env python3
"""Independently verify selected cross-layer legal source chains.

This audit covers:
1. Care Insurance Act Article 41(4)(i) -> Notice 19 day-service fee root.
2. Care Insurance Act Article 74 -> Ordinance 37 direct day-service standards.

The verifier intentionally uses live primary sources and independent parsers:
- e-Gov XML via xml.dom.minidom
- MHLW Notice 19 HTML via html.parser.HTMLParser

It does not promote HUMAN_VERIFIED, VERIFIED_CURRENT, or unrelated mappings.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import unicodedata
import urllib.request
from html.parser import HTMLParser
from pathlib import Path
from xml.dom import Node, minidom

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

CAREACT_ID = "409AC0000000123"
ORDINANCE37_ID = "411M50000100037"
CAREACT_URL = f"https://laws.e-gov.go.jp/api/1/lawdata/{CAREACT_ID}"
ORDINANCE37_URL = f"https://laws.e-gov.go.jp/api/1/lawdata/{ORDINANCE37_ID}"
NOTICE19_URL = "https://www.mhlw.go.jp/web/t_doc?dataId=82aa0253&dataType=0"

EXPECTED_DIRECT_SECTION_TITLES = {
    "基本方針",
    "人員に関する基準",
    "設備に関する基準",
    "運営に関する基準",
}


def load(name: str):
    return json.loads((DATA / name).read_text(encoding="utf-8"))


def fetch(url: str) -> tuple[bytes, str | None]:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "kaigo-rules-cross-layer-source-chain-verifier/1.0 (+https://github.com/Josh-Temple/kaigo-rules)"
        },
    )
    with urllib.request.urlopen(req, timeout=90) as response:
        payload = response.read()
        charset = response.headers.get_content_charset()
    return payload, charset


def normalize(value: str) -> str:
    return " ".join(unicodedata.normalize("NFKC", value).split())


def compact(value: str) -> str:
    return re.sub(r"\s+", "", unicodedata.normalize("NFKC", value))


def text_of(node) -> str:
    chunks: list[str] = []

    def walk(current):
        for child in current.childNodes:
            if child.nodeType in (Node.TEXT_NODE, Node.CDATA_SECTION_NODE):
                chunks.append(child.data)
            elif child.nodeType == Node.ELEMENT_NODE:
                walk(child)

    walk(node)
    return normalize("".join(chunks))


def first_descendant(node, tag: str):
    found = node.getElementsByTagName(tag)
    return found[0] if found else None


def direct_elements(node, tag: str | None = None):
    return [
        child
        for child in node.childNodes
        if child.nodeType == Node.ELEMENT_NODE and (tag is None or child.tagName == tag)
    ]


def canonical_num(value: str | None) -> str:
    return str(value or "").strip().replace("_", "-")


def find_article(document, num: str):
    for article in document.getElementsByTagName("Article"):
        if canonical_num(article.getAttribute("Num")) == num:
            return article
    raise RuntimeError(f"Article {num} not found")


def find_item(article, paragraph_num: str, item_num: str):
    for paragraph in direct_elements(article, "Paragraph"):
        if canonical_num(paragraph.getAttribute("Num")) != paragraph_num:
            continue
        for item in direct_elements(paragraph, "Item"):
            if canonical_num(item.getAttribute("Num")) == item_num:
                return item
    raise RuntimeError(
        f"Article {article.getAttribute('Num')} paragraph {paragraph_num} item {item_num} not found"
    )


def law_title(document) -> str:
    law = first_descendant(document, "Law")
    if law is None:
        raise RuntimeError("Law element not found")
    body = first_descendant(law, "LawBody")
    if body is None:
        raise RuntimeError("LawBody not found")
    title = first_descendant(body, "LawTitle")
    if title is None:
        raise RuntimeError("LawTitle not found")
    return text_of(title)


def element_title(node, tag: str) -> str:
    direct = [child for child in direct_elements(node) if child.tagName == tag]
    return text_of(direct[0]) if direct else ""


def find_dayservice_direct_articles(document) -> tuple[list[str], dict]:
    chapters = document.getElementsByTagName("Chapter")
    target_chapter = None
    for chapter in chapters:
        title = element_title(chapter, "ChapterTitle")
        if "通所介護" in title:
            target_chapter = chapter
            break
    if target_chapter is None:
        raise RuntimeError("Ordinance 37 day-service chapter not found")

    selected_sections = []
    article_nums: list[str] = []

    for section in direct_elements(target_chapter, "Section"):
        section_title = element_title(section, "SectionTitle")
        normalized_title = re.sub(r"^第.+節\s*", "", section_title).strip()
        if normalized_title not in EXPECTED_DIRECT_SECTION_TITLES:
            continue
        selected_sections.append({"title": section_title, "normalized_title": normalized_title})
        for article in section.getElementsByTagName("Article"):
            article_nums.append(canonical_num(article.getAttribute("Num")))

    if {row["normalized_title"] for row in selected_sections} != EXPECTED_DIRECT_SECTION_TITLES:
        raise RuntimeError("Expected four direct day-service sections not all found")

    article_nums = sorted(
        set(article_nums),
        key=lambda value: tuple(int(part) for part in value.split("-")),
    )
    return article_nums, {
        "chapter_title": element_title(target_chapter, "ChapterTitle"),
        "selected_sections": selected_sections,
    }


class VisibleTextParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.fragments: list[str] = []
        self.suppressed = 0

    def handle_starttag(self, tag: str, attrs) -> None:
        if tag.lower() in {"script", "style", "rt", "rp"}:
            self.suppressed += 1

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() in {"script", "style", "rt", "rp"} and self.suppressed:
            self.suppressed -= 1

    def handle_data(self, data: str) -> None:
        if self.suppressed:
            return
        value = normalize(data)
        if value:
            self.fragments.append(value)


def decode_html(payload: bytes, charset: str | None) -> str:
    for encoding in [charset, "utf-8", "cp932", "shift_jis"]:
        if not encoding:
            continue
        try:
            return payload.decode(encoding)
        except (UnicodeDecodeError, LookupError):
            continue
    return payload.decode("utf-8", errors="replace")


def notice19_evidence(payload: bytes, charset: str | None) -> dict:
    parser = VisibleTextParser()
    parser.feed(decode_html(payload, charset))
    parser.close()
    lines = parser.fragments

    title_match = next(
        (
            line
            for line in lines
            if compact("指定居宅サービスに要する費用の額の算定に関する基準")
            in compact(line)
        ),
        None,
    )
    section_match = next(
        (line for line in lines if compact(line).startswith(compact("6 通所介護費"))),
        None,
    )
    if title_match is None:
        raise RuntimeError("Notice 19 title evidence not found")
    if section_match is None:
        raise RuntimeError("Notice 19 day-service section evidence not found")

    return {
        "title_evidence": title_match,
        "dayservice_section_evidence": section_match,
    }


def relation_rows():
    rows = load("care-insurance-act-relations.json")
    fee = [
        row
        for row in rows
        if row.get("from") == "careact.article.41.p.4.i.1"
        and row.get("relation") == "authorizes_fee_standard_for"
        and row.get("to") == "fee.dayservice.root"
    ]
    delegated = [
        row
        for row in rows
        if row.get("from") == "careact.article.74"
        and row.get("relation") == "delegates_standards_to"
        and str(row.get("to", "")).startswith("ordinance37.article.")
    ]
    return fee, delegated


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report")
    args = parser.parse_args()

    checks: list[dict] = []
    errors: list[dict] = []

    try:
        care_payload, _ = fetch(CAREACT_URL)
        ordinance_payload, _ = fetch(ORDINANCE37_URL)
        notice_payload, notice_charset = fetch(NOTICE19_URL)

        care_doc = minidom.parseString(care_payload)
        ordinance_doc = minidom.parseString(ordinance_payload)

        fee_item = find_item(find_article(care_doc, "41"), "4", "1")
        fee_item_text = text_of(fee_item)
        article74_text = text_of(find_article(care_doc, "74"))

        direct_articles, ordinance_structure = find_dayservice_direct_articles(ordinance_doc)
        notice_evidence = notice19_evidence(notice_payload, notice_charset)

        fee_relations, delegated_relations = relation_rows()

        fee_differences = []
        for phrase in ["通所介護", "厚生労働大臣が定める基準"]:
            if phrase not in fee_item_text:
                fee_differences.append(
                    {"difference": "careact_fee_authority_phrase_missing", "phrase": phrase}
                )
        if len(fee_relations) != 1:
            fee_differences.append(
                {
                    "difference": "committed_fee_relation_cardinality_mismatch",
                    "expected": 1,
                    "observed": len(fee_relations),
                }
            )

        checks.append(
            {
                "id": "careact41-to-notice19-dayservice-fee",
                "relation": "authorizes_fee_standard_for",
                "source_id": "careact.article.41.p.4.i.1",
                "target_id": "fee.dayservice.root",
                "result": "PASS" if not fee_differences else "FAIL",
                "careact_source_sha256": hashlib.sha256(care_payload).hexdigest(),
                "notice19_source_sha256": hashlib.sha256(notice_payload).hexdigest(),
                "careact_evidence": {
                    "required_phrases": ["通所介護", "厚生労働大臣が定める基準"],
                    "source_text_sha256": hashlib.sha256(
                        fee_item_text.encode("utf-8")
                    ).hexdigest(),
                },
                "notice19_evidence": notice_evidence,
                "differences": fee_differences,
            }
        )

        delegation_differences = []
        if "厚生労働省令で定める基準" not in article74_text:
            delegation_differences.append(
                {
                    "difference": "careact_delegation_phrase_missing",
                    "phrase": "厚生労働省令で定める基準",
                }
            )

        ordinance_title = law_title(ordinance_doc)
        expected_title = "指定居宅サービス等の事業の人員、設備及び運営に関する基準"
        if ordinance_title != expected_title:
            delegation_differences.append(
                {
                    "difference": "ordinance37_title_mismatch",
                    "expected": expected_title,
                    "observed": ordinance_title,
                }
            )

        committed_targets = sorted(
            {
                str(row["to"]).removeprefix("ordinance37.article.")
                for row in delegated_relations
            },
            key=lambda value: tuple(int(part) for part in value.split("-")),
        )
        if committed_targets != direct_articles:
            delegation_differences.append(
                {
                    "difference": "delegated_direct_article_set_mismatch",
                    "independently_observed": direct_articles,
                    "committed_targets": committed_targets,
                    "missing_from_relations": sorted(set(direct_articles) - set(committed_targets)),
                    "unexpected_relations": sorted(set(committed_targets) - set(direct_articles)),
                }
            )

        checks.append(
            {
                "id": "careact74-to-ordinance37-dayservice-direct-standards",
                "relation": "delegates_standards_to",
                "source_id": "careact.article.74",
                "target_layer": "ordinance37",
                "result": "PASS" if not delegation_differences else "FAIL",
                "careact_source_sha256": hashlib.sha256(care_payload).hexdigest(),
                "ordinance37_source_sha256": hashlib.sha256(ordinance_payload).hexdigest(),
                "careact_evidence": {
                    "required_phrase": "厚生労働省令で定める基準",
                    "source_text_sha256": hashlib.sha256(
                        article74_text.encode("utf-8")
                    ).hexdigest(),
                },
                "ordinance37_evidence": {
                    "law_title": ordinance_title,
                    "chapter_title": ordinance_structure["chapter_title"],
                    "selected_sections": ordinance_structure["selected_sections"],
                    "independently_observed_direct_articles": direct_articles,
                },
                "committed_relation_targets": committed_targets,
                "relation_count": len(committed_targets),
                "differences": delegation_differences,
            }
        )

    except Exception as exc:
        errors.append({"scope": "cross-layer-source-chain", "error": str(exc)})

    passed_relations = 0
    for check in checks:
        if check.get("result") != "PASS":
            continue
        if check["id"] == "careact41-to-notice19-dayservice-fee":
            passed_relations += 1
        elif check["id"] == "careact74-to-ordinance37-dayservice-direct-standards":
            passed_relations += check.get("relation_count", 0)

    result = (
        "PASS"
        if not errors and len(checks) == 2 and all(row.get("result") == "PASS" for row in checks)
        else "FAIL"
    )

    report = {
        "format_version": 1,
        "verification_kind": "INDEPENDENT_CROSS_LAYER_SOURCE_CHAIN_AUDIT",
        "result": result,
        "parsers": {
            "egov_xml": "python_xml_dom_minidom",
            "mhlw_html": "python_stdlib_html_parser",
        },
        "checks": checks,
        "errors": errors,
        "coverage": {
            "relations_in_this_lane": 18,
            "relations_passed": passed_relations,
            "previous_explicit_relations_independently_verified": 27,
            "aggregate_relations_independently_verified": 27 + passed_relations,
            "non_contains_semantic_or_cross_layer_relations_current_inventory": 163,
            "remaining_semantic_or_cross_layer_relations_not_independently_verified": 163 - 27 - passed_relations,
        },
        "safety": {
            "promotes_human_review": False,
            "promotes_verified_current": False,
            "promotes_other_semantic_mappings": False,
            "note": (
                "PASS is limited to source-chain consistency for one fee-authority relation "
                "and 17 Article 74 -> Ordinance 37 direct day-service standard relations."
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
