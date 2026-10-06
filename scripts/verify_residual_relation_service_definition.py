#!/usr/bin/env python3
"""Independently verify the residual day-service service-definition relation."""

from __future__ import annotations

import argparse
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

MHLW_URL = "https://www.mhlw.go.jp/web/t_doc?dataId=82aa0253&dataType=0&pageNo=1"
EGOV_API_URL = "https://laws.e-gov.go.jp/api/1/lawdata/411M50000100037"
AUDIT = DATA / "residual-relation-service-definition-independent-audit.json"
RELATION_IDENTITY = ("fee.dayservice.root", "defined_service_by", "ordinance37.article.92")
REQUIRED_FEE_REFERENCE = "指定通所介護(指定居宅サービス基準第92条に規定する指定通所介護をいう。以下同じ。)"
REQUIRED_ORDINANCE_PHRASE = "指定居宅サービスに該当する通所介護"


def clean(value: str) -> str:
    return re.sub(r"\s+", "", unicodedata.normalize("NFKC", value))


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
        value = " ".join(unicodedata.normalize("NFKC", data).split())
        if value:
            self.fragments.append(value)


def fetch(url: str) -> bytes:
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "kaigo-rules-residual-relation-verifier/1.0 (+https://github.com/Josh-Temple/kaigo-rules)"},
    )
    with urllib.request.urlopen(req, timeout=90) as response:
        return response.read()


def decode_html(payload: bytes) -> str:
    for encoding in ("utf-8", "cp932", "shift_jis"):
        try:
            return payload.decode(encoding)
        except UnicodeDecodeError:
            pass
    return payload.decode("utf-8", errors="replace")


def text_of(node) -> str:
    chunks: list[str] = []

    def walk(current) -> None:
        for child in current.childNodes:
            if child.nodeType in (Node.TEXT_NODE, Node.CDATA_SECTION_NODE):
                chunks.append(child.data)
            elif child.nodeType == Node.ELEMENT_NODE:
                walk(child)

    walk(node)
    return " ".join("".join(chunks).split())


def live_mhlw_definition(payload: bytes) -> dict:
    parser = VisibleTextParser()
    parser.feed(decode_html(payload))
    parser.close()
    lines = parser.fragments
    section_index = next(
        (i for i, line in enumerate(lines) if clean(line).startswith(clean("6 通所介護費"))),
        None,
    )
    if section_index is None:
        raise RuntimeError("6 通所介護費 section not found in current MHLW HTML")
    note = next(
        (
            line
            for line in lines[section_index:]
            if clean(line).startswith("1") and clean(REQUIRED_FEE_REFERENCE) in clean(line)
        ),
        None,
    )
    if note is None:
        raise RuntimeError("explicit Article 92 service-definition reference not found in day-service note 1")
    return {"locator": "6 通所介護費 / 注1", "matched_reference": REQUIRED_FEE_REFERENCE}


def live_ordinance_article92(payload: bytes) -> dict:
    document = minidom.parseString(payload)
    article = next(
        (
            node
            for node in document.getElementsByTagName("Article")
            if node.getAttribute("Num").replace("_", "-") == "92"
        ),
        None,
    )
    if article is None:
        raise RuntimeError("Ordinance 37 Article 92 not found in current e-Gov XML")
    text = text_of(article)
    if clean(REQUIRED_ORDINANCE_PHRASE) not in clean(text):
        raise RuntimeError("Article 92 no longer contains the expected designated day-service definition")
    return {"locator": "第七章 通所介護 ＞ 第一節 基本方針 ＞ 第九十二条"}


def canonical_checks() -> list[str]:
    errors: list[str] = []
    relations = json.loads((DATA / "remuneration-relations.json").read_text(encoding="utf-8"))
    matches = [
        row
        for row in relations
        if (
            row.get("from_fee_id"),
            row.get("relation"),
            row.get("to_id") or row.get("to_source_id"),
        )
        == RELATION_IDENTITY
    ]
    if len(matches) != 1:
        errors.append(f"canonical relation count is {len(matches)}, expected 1")

    skeleton = json.loads((DATA / "remuneration-current-skeleton.json").read_text(encoding="utf-8"))
    source = next((row for row in skeleton if row.get("id") == RELATION_IDENTITY[0]), None)
    if source is None or source.get("title") != "通所介護費":
        errors.append("canonical source node fee.dayservice.root is missing or changed")

    ordinance = json.loads((DATA / "ordinance37-nodes.json").read_text(encoding="utf-8"))
    target = next((row for row in ordinance if row.get("id") == RELATION_IDENTITY[2]), None)
    if target is None:
        errors.append("canonical target ordinance37.article.92 is missing")
    return errors


def verify_committed_audit() -> list[str]:
    errors: list[str] = []
    audit = json.loads(AUDIT.read_text(encoding="utf-8"))
    if audit.get("audit_result") != "PASS":
        errors.append("committed audit is not PASS")
    checks = audit.get("checks", [])
    if len(checks) != 1:
        errors.append("committed audit must contain exactly one check")
        return errors
    check = checks[0]
    identity = (check.get("from_id"), check.get("relation"), check.get("to_id"))
    if identity != RELATION_IDENTITY:
        errors.append(f"committed audit identity changed: {identity!r}")
    if check.get("result") != "PASS" or check.get("differences") != []:
        errors.append("committed audit check is not clean")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report")
    args = parser.parse_args()

    errors = canonical_checks() + verify_committed_audit()
    evidence = {}
    try:
        evidence["mhlw"] = live_mhlw_definition(fetch(MHLW_URL))
    except Exception as exc:
        errors.append(f"MHLW verification failed: {exc}")
    try:
        evidence["egov"] = live_ordinance_article92(fetch(EGOV_API_URL))
    except Exception as exc:
        errors.append(f"e-Gov verification failed: {exc}")

    report = {
        "format_version": 1,
        "verification_kind": "INDEPENDENT_EXPLICIT_SERVICE_DEFINITION_RELATION_AUDIT",
        "identity": {
            "from": RELATION_IDENTITY[0],
            "relation": RELATION_IDENTITY[1],
            "to": RELATION_IDENTITY[2],
        },
        "sources": {"mhlw": MHLW_URL, "egov": EGOV_API_URL},
        "evidence": evidence,
        "result": "PASS" if not errors else "FAIL",
        "errors": errors,
        "safety": {
            "semantic_similarity_used_as_proof": False,
            "promotes_other_relations": False,
            "promotes_human_review": False,
        },
    }
    rendered = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    print(rendered, end="")
    if args.report:
        path = Path(args.report)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(rendered, encoding="utf-8")
    return 0 if report["result"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
