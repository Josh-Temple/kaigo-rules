#!/usr/bin/env python3
"""Independently verify day-service unit-price data against the current MHLW HTML.

This verifier intentionally does not import or reuse scripts/import_unit_price.py.
It reparses the official HTML with Python's standard-library HTMLParser and compares
only normalized factual keys against the committed generated datasets.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import unicodedata
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
BASE_URL = "https://www.mhlw.go.jp/web/t_doc?dataId=82ab4582&dataType=0&pageNo={}"
REGIONS = ["一級地", "二級地", "三級地", "四級地", "五級地", "六級地", "七級地", "その他"]
EXPLICIT_REGIONS = set(REGIONS[:-1])
PREFECTURES = {
    "北海道","青森県","岩手県","宮城県","秋田県","山形県","福島県",
    "茨城県","栃木県","群馬県","埼玉県","千葉県","東京都","神奈川県",
    "新潟県","富山県","石川県","福井県","山梨県","長野県","岐阜県","静岡県","愛知県",
    "三重県","滋賀県","京都府","大阪府","兵庫県","奈良県","和歌山県",
    "鳥取県","島根県","岡山県","広島県","山口県","徳島県","香川県","愛媛県","高知県",
    "福岡県","佐賀県","長崎県","熊本県","大分県","宮崎県","鹿児島県","沖縄県",
}
JP_DIGITS = {"〇": 0, "零": 0, "一": 1, "二": 2, "三": 3, "四": 4, "五": 5, "六": 6, "七": 7, "八": 8, "九": 9}
JP_UNITS = {"十": 10, "百": 100, "千": 1000}


def clean(value: str) -> str:
    return " ".join(unicodedata.normalize("NFKC", value).split())


class TableCollector(HTMLParser):
    """Collect table rows/cells without BeautifulSoup or the production importer."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.tables: list[list[list[str]]] = []
        self.table_depth = 0
        self.current_table: list[list[str]] | None = None
        self.current_row: list[str] | None = None
        self.current_cell: list[str] | None = None

    def handle_starttag(self, tag: str, attrs) -> None:
        tag = tag.lower()
        if tag == "table":
            if self.table_depth == 0:
                self.current_table = []
            self.table_depth += 1
            return
        if not self.table_depth:
            return
        if tag == "tr":
            self.current_row = []
        elif tag in {"td", "th"}:
            self.current_cell = []
        elif tag == "br" and self.current_cell is not None:
            self.current_cell.append(" ")

    def handle_data(self, data: str) -> None:
        if self.table_depth and self.current_cell is not None:
            self.current_cell.append(data)

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if not self.table_depth:
            return
        if tag in {"td", "th"} and self.current_cell is not None:
            if self.current_row is not None:
                self.current_row.append(clean("".join(self.current_cell)))
            self.current_cell = None
        elif tag == "tr" and self.current_row is not None:
            if self.current_table is not None and any(self.current_row):
                self.current_table.append(self.current_row)
            self.current_row = None
        elif tag == "table":
            self.table_depth -= 1
            if self.table_depth == 0 and self.current_table is not None:
                self.tables.append(self.current_table)
                self.current_table = None


def decode_payload(payload: bytes, charset: str | None) -> str:
    for encoding in [charset, "utf-8", "cp932", "shift_jis"]:
        if not encoding:
            continue
        try:
            return payload.decode(encoding)
        except (UnicodeDecodeError, LookupError):
            continue
    return payload.decode("utf-8", errors="replace")


def fetch(url: str) -> tuple[bytes, str]:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "kaigo-rules-independent-verifier/1.0 (+https://github.com/Josh-Temple/kaigo-rules)"},
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        payload = response.read()
        charset = response.headers.get_content_charset()
    return payload, decode_payload(payload, charset)


def parse_tables(html: str) -> list[list[list[str]]]:
    parser = TableCollector()
    parser.feed(html)
    parser.close()
    return parser.tables


def jp_integer(text: str) -> int:
    value = 0
    pending_digit: int | None = None
    for char in clean(text):
        if char in JP_DIGITS:
            pending_digit = JP_DIGITS[char]
        elif char in JP_UNITS:
            value += (1 if pending_digit is None else pending_digit) * JP_UNITS[char]
            pending_digit = None
        elif char.isdigit():
            pending_digit = (0 if pending_digit is None else pending_digit * 10) + int(char)
    return value + (pending_digit or 0)


def find_rate_table(tables: list[list[list[str]]]) -> list[list[str]]:
    for table in tables:
        for row in table:
            values = set(row)
            if {"地域区分", "サービス種類", "割合"}.issubset(values):
                return table
    raise RuntimeError("Independent verifier could not find the unit-price table")


def find_assignment_table(tables: list[list[list[str]]]) -> list[list[str]]:
    for table in tables:
        for row in table:
            values = set(row)
            if {"地域区分", "都道府県", "地域"}.issubset(values):
                return table
    raise RuntimeError("Independent verifier could not find the municipality assignment table")


def extract_rates(table: list[list[str]]) -> dict[str, dict]:
    observed: dict[str, dict] = {}
    current_region: str | None = None

    for row in table:
        for cell in row:
            if cell in REGIONS:
                current_region = cell

        ratio_cells = [cell for cell in row if cell.startswith("千分の")]
        if not current_region or not ratio_cells:
            continue

        ratio_text = ratio_cells[-1]
        service_cells = [
            cell for cell in row
            if cell and cell != current_region and cell != ratio_text
            and cell not in {"地域区分", "サービス種類", "割合"}
        ]
        service_text = " ".join(service_cells)

        is_target = (
            current_region == "その他" and "全てのサービス" in service_text
        ) or service_text.startswith("通所介護")

        if not is_target:
            continue

        ratio = jp_integer(ratio_text.split("千分の", 1)[1])
        if not 900 <= ratio <= 1200:
            raise RuntimeError(f"Independent verifier found implausible ratio: {ratio_text}")

        fact = {
            "region_class": current_region,
            "ratio_text": ratio_text,
            "ratio_per_thousand": ratio,
            "unit_price_yen": round(10 * ratio / 1000, 3),
        }
        previous = observed.get(current_region)
        if previous and previous != fact:
            raise RuntimeError(f"Independent verifier found conflicting rates for {current_region}")
        observed[current_region] = fact

    missing = [region for region in REGIONS if region not in observed]
    if missing:
        raise RuntimeError("Independent verifier missed region classes: " + ", ".join(missing))
    return observed


def extract_assignments(table: list[list[str]]) -> tuple[set[tuple[str, str, str]], bool]:
    observed: set[tuple[str, str, str]] = set()
    current_region: str | None = None
    current_prefecture: str | None = None
    default_rule_present = False

    for row in table:
        if {"地域区分", "都道府県", "地域"}.issubset(set(row)):
            continue

        for cell in row:
            if cell in REGIONS:
                current_region = cell
            if cell in PREFECTURES:
                current_prefecture = cell

        if current_region == "その他" and "全ての都道府県" in row and "その他の地域" in row:
            default_rule_present = True
            continue

        if current_region not in EXPLICIT_REGIONS or current_prefecture not in PREFECTURES:
            continue

        locality_cells = [
            cell for cell in row
            if cell and cell not in REGIONS and cell not in PREFECTURES
            and cell not in {"地域区分", "都道府県", "地域"}
        ]
        if not locality_cells:
            continue

        locality_text = locality_cells[-1]
        for locality in [clean(item) for item in locality_text.split("、")]:
            if locality:
                observed.add((current_prefecture, locality, current_region))

    if not observed:
        raise RuntimeError("Independent verifier extracted no municipality assignments")
    if not default_rule_present:
        raise RuntimeError("Independent verifier did not find the その他 default rule")
    return observed, default_rule_present


def load_json(name: str):
    return json.loads((DATA / name).read_text(encoding="utf-8"))


def compare() -> dict:
    payloads: list[bytes] = []
    htmls: list[str] = []
    urls = [BASE_URL.format(1), BASE_URL.format(2)]
    for url in urls:
        payload, html = fetch(url)
        payloads.append(payload)
        htmls.append(html)

    tables = []
    for html in htmls:
        tables.extend(parse_tables(html))

    observed_rates = extract_rates(find_rate_table(tables))
    observed_assignments, observed_default = extract_assignments(find_assignment_table(tables))

    canonical_rates = load_json("unit-price-dayservice.json")
    canonical_assignments = load_json("unit-price-region-assignments.json")
    rate_meta = load_json("unit-price-dayservice-meta.json")
    assignment_meta = load_json("unit-price-region-assignments-meta.json")

    expected_rates = {
        row["region_class"]: {
            "region_class": row["region_class"],
            "ratio_text": clean(row["ratio_text"]),
            "ratio_per_thousand": row["ratio_per_thousand"],
            "unit_price_yen": row["unit_price_yen"],
        }
        for row in canonical_rates
    }
    expected_assignments = {
        (row["prefecture"], clean(row["locality"]), row["region_class"])
        for row in canonical_assignments
    }

    rate_differences = []
    for region in REGIONS:
        expected = expected_rates.get(region)
        actual = observed_rates.get(region)
        if expected != actual:
            rate_differences.append({"region_class": region, "expected": expected, "observed": actual})

    missing_assignments = sorted(expected_assignments - observed_assignments)
    unexpected_assignments = sorted(observed_assignments - expected_assignments)
    source_sha256 = [hashlib.sha256(payload).hexdigest() for payload in payloads]

    metadata_differences = []
    if rate_meta.get("source_urls") != urls:
        metadata_differences.append("unit-price-dayservice-meta source_urls differ from verifier URLs")
    if assignment_meta.get("source_urls") != urls:
        metadata_differences.append("unit-price-region-assignments-meta source_urls differ from verifier URLs")
    if rate_meta.get("source_sha256") != source_sha256:
        metadata_differences.append("unit-price-dayservice-meta source_sha256 differs from current live source")
    if assignment_meta.get("source_sha256") != source_sha256:
        metadata_differences.append("unit-price-region-assignments-meta source_sha256 differs from current live source")
    if rate_meta.get("rate_count") != len(observed_rates):
        metadata_differences.append("unit-price-dayservice-meta rate_count differs from independent extraction")
    if assignment_meta.get("explicit_assignment_count") != len(observed_assignments):
        metadata_differences.append("unit-price-region-assignments-meta explicit_assignment_count differs from independent extraction")
    if bool(assignment_meta.get("default_rule_present")) != observed_default:
        metadata_differences.append("unit-price-region-assignments-meta default_rule_present differs from independent extraction")

    result = "PASS"
    if rate_differences or missing_assignments or unexpected_assignments or metadata_differences:
        result = "FAIL"

    return {
        "format_version": 1,
        "verification_kind": "INDEPENDENT_MACHINE_REPARSE",
        "parser": "python_stdlib_html_parser",
        "source_urls": urls,
        "source_sha256": source_sha256,
        "result": result,
        "observed": {
            "rate_count": len(observed_rates),
            "explicit_assignment_count": len(observed_assignments),
            "default_rule_present": observed_default,
            "assignment_counts_by_region": {
                region: sum(1 for _, _, value in observed_assignments if value == region)
                for region in REGIONS[:-1]
            },
        },
        "differences": {
            "rates": rate_differences,
            "missing_assignments": [
                {"prefecture": p, "locality": l, "region_class": r}
                for p, l, r in missing_assignments
            ],
            "unexpected_assignments": [
                {"prefecture": p, "locality": l, "region_class": r}
                for p, l, r in unexpected_assignments
            ],
            "metadata": metadata_differences,
        },
        "safety": {
            "promotes_human_review": False,
            "promotes_verified_current": False,
            "note": "This verifier is an independent machine cross-check only.",
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", help="Optional path for the JSON verification report")
    args = parser.parse_args()

    report = compare()
    rendered = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    print(rendered, end="")

    if args.report:
        path = Path(args.report)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(rendered, encoding="utf-8")

    return 0 if report["result"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
