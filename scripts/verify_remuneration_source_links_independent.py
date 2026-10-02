#!/usr/bin/env python3
"""Independently verify two remuneration source-link relations from live MHLW HTML.

Intentionally excludes freshness-sensitive latest_interpretation_amendment_evidence.
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

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

UNIT_PRICE_PAGE1 = "https://www.mhlw.go.jp/web/t_doc?dataId=82ab4582&dataType=0&pageNo=1"
UNIT_PRICE_PAGE2 = "https://www.mhlw.go.jp/web/t_doc?dataId=82ab4582&dataType=0&pageNo=2"
HISTORICAL_GUIDANCE = "https://www.mhlw.go.jp/web/t_doc?dataId=00ta4378&dataType=1&pageNo=1"

SPECS = [
    {
        "from_fee_id": "fee.dayservice.root",
        "relation": "currency_conversion_uses",
        "to_source_id": "mhlw-unit-price-current",
        "evidence_kind": "unit_price",
    },
    {
        "from_fee_id": "fee.dayservice.root",
        "relation": "historically_interpreted_by",
        "to_source_id": "mhlw-fee-interpretation-historical",
        "evidence_kind": "historical_guidance",
    },
]


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
        value = " ".join(data.split())
        if value:
            self.fragments.append(value)


def fetch(url: str) -> bytes:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "kaigo-rules-remuneration-source-link-verifier/1.0 (+https://github.com/Josh-Temple/kaigo-rules)"
        },
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        return response.read()


def decode(payload: bytes) -> str:
    for encoding in ("utf-8", "cp932", "shift_jis"):
        try:
            return payload.decode(encoding)
        except UnicodeDecodeError:
            pass
    return payload.decode("utf-8", errors="replace")


def visible_text(payload: bytes) -> str:
    parser = VisibleTextParser()
    parser.feed(decode(payload))
    parser.close()
    return "\n".join(parser.fragments)


def compact(value: str) -> str:
    return re.sub(r"\s+", "", unicodedata.normalize("NFKC", value or ""))


def load(name: str):
    return json.loads((DATA / name).read_text(encoding="utf-8"))


def verify() -> dict:
    payloads = {
        "unit_price_page1": fetch(UNIT_PRICE_PAGE1),
        "unit_price_page2": fetch(UNIT_PRICE_PAGE2),
        "historical_guidance": fetch(HISTORICAL_GUIDANCE),
    }
    texts = {key: compact(visible_text(value)) for key, value in payloads.items()}

    relations = load("remuneration-relations.json")
    source_rows = {row["id"]: row for row in load("sources.json") if row.get("id")}
    checks = []

    for spec in SPECS:
        differences = []
        matches = [
            row
            for row in relations
            if row.get("from_fee_id") == spec["from_fee_id"]
            and row.get("relation") == spec["relation"]
            and row.get("to_source_id") == spec["to_source_id"]
        ]
        if len(matches) != 1:
            differences.append("committed source-link relation missing or duplicated")

        source = source_rows.get(spec["to_source_id"])
        if not source:
            differences.append("target source missing from source registry")
        elif source.get("publisher") != "厚生労働省":
            differences.append("target source publisher is not MHLW")

        evidence = []
        if spec["evidence_kind"] == "unit_price":
            page1 = texts["unit_price_page1"]
            page2 = texts["unit_price_page2"]
            required_page1 = [
                "厚生労働大臣が定める一単位の単価",
                "指定居宅サービスに要する費用の額の算定に関する基準",
                "一単位の単価",
                "十円",
            ]
            required_page2 = ["通所介護"]
            for phrase in required_page1:
                if compact(phrase) not in page1:
                    differences.append(f"unit-price page 1 evidence missing: {phrase}")
            for phrase in required_page2:
                if compact(phrase) not in page2:
                    differences.append(f"unit-price page 2 evidence missing: {phrase}")
            evidence = required_page1 + required_page2
        elif spec["evidence_kind"] == "historical_guidance":
            historical = texts["historical_guidance"]
            required = [
                "指定居宅サービスに要する費用の額の算定に関する基準",
                "実施上の留意事項",
                "通所介護",
            ]
            for phrase in required:
                if compact(phrase) not in historical:
                    differences.append(f"historical guidance evidence missing: {phrase}")
            evidence = required
        else:
            differences.append("unsupported evidence kind")

        checks.append(
            {
                "id": f"{spec['from_fee_id']}-to-{spec['to_source_id']}",
                "from_id": spec["from_fee_id"],
                "relation": spec["relation"],
                "to_source_id": spec["to_source_id"],
                "evidence_kind": spec["evidence_kind"],
                "required_primary_source_phrases": evidence,
                "result": "PASS" if not differences else "FAIL",
                "differences": differences,
            }
        )

    result = "PASS" if all(row["result"] == "PASS" for row in checks) else "FAIL"
    return {
        "format_version": 1,
        "verification_kind": "INDEPENDENT_MHLW_SOURCE_LINK_REPARSE",
        "result": result,
        "sources": {
            "unit_price_page1": {
                "url": UNIT_PRICE_PAGE1,
                "sha256": hashlib.sha256(payloads["unit_price_page1"]).hexdigest(),
            },
            "unit_price_page2": {
                "url": UNIT_PRICE_PAGE2,
                "sha256": hashlib.sha256(payloads["unit_price_page2"]).hexdigest(),
            },
            "historical_guidance": {
                "url": HISTORICAL_GUIDANCE,
                "sha256": hashlib.sha256(payloads["historical_guidance"]).hexdigest(),
            },
        },
        "checks": checks,
        "coverage": {
            "relations_in_this_lane": len(checks),
            "relations_passed": sum(row["result"] == "PASS" for row in checks),
        },
        "excluded_relation": {
            "identity": {
                "from": "fee.dayservice.root",
                "relation": "latest_interpretation_amendment_evidence",
                "to": "mhlw-r8-fee-guidance-may-amendment",
            },
            "reason": "Freshness-sensitive 'latest' semantics require separate exhaustive/currentness evidence and are intentionally not inferred here.",
        },
        "safety": {
            "human_verified": False,
            "verified_current": False,
            "automatic_promotion_allowed": False,
            "promotes_latest_claim": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report")
    args = parser.parse_args()
    report = verify()
    rendered = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    print(rendered, end="")
    if args.report:
        Path(args.report).write_text(rendered, encoding="utf-8")
    return 0 if report["result"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
