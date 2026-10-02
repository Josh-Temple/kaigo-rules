#!/usr/bin/env python3
import argparse
import hashlib
import json
import re
import unicodedata
import urllib.parse
import urllib.request
from collections import Counter
from html.parser import HTMLParser
from io import BytesIO
from pathlib import Path

import openpyxl
import xlrd

DEFAULT_PAGE = "https://www.mhlw.go.jp/stf/seisakunitsuite/bunya/hukushi_kaigo/kaigo_koureisha/qa/index.html"
SERVICE_CODE_BY_SCOPE = {
    "全サービス共通": "01",
    "居宅サービス共通": "02",
    "施設サービス共通": "03",
    "地域密着型サービス共通": "04",
    "訪問系サービス共通": "05",
    "通所系サービス共通": "06",
    "訪問介護事業": "11",
    "訪問入浴介護事業": "12",
    "訪問看護事業": "13",
    "訪問リハビリテーション事業": "14",
    "居宅療養管理指導事業": "15",
    "通所介護事業": "16",
    "通所リハビリテーション事業": "17",
    "短期入所生活介護事業": "18",
    "短期入所療養介護事業": "19",
    "特定施設入居者生活介護事業": "20",
    "福祉用具貸与事業": "21",
    "特定福祉用具販売事業": "22",
    "居宅介護支援事業": "23",
    "介護老人福祉施設": "24",
    "介護老人保健施設": "25",
    "介護療養型医療施設": "26",
    "住宅改修": "27",
    "定期巡回・随時対応型訪問介護看護事業": "40",
    "夜間対応型訪問介護事業": "41",
    "認知症対応型通所介護事業": "42",
    "小規模多機能型居宅介護事業": "43",
    "認知症対応型共同生活介護事業": "44",
    "地域密着型特定施設入居者生活介護事業": "45",
    "地域密着型介護老人福祉施設": "46",
    "看護小規模多機能型居宅介護": "47",
    "地域密着型通所介護事業": "48",
    "介護医療院": "49",
}
CANONICAL_SCOPE_BY_CODE = {code: scope for scope, code in SERVICE_CODE_BY_SCOPE.items()}

class XlsLinkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
    def handle_starttag(self, tag, attrs):
        if tag.lower() != "a":
            return
        href = dict(attrs).get("href")
        if href and re.search(r"\.xlsx?(?:$|\?)", href, re.I):
            self.links.append(href)

class SheetAdapter:
    def __init__(self, name, rows):
        self.name = name
        self.rows = rows
        self.nrows = len(rows)
        self.ncols = max((len(r) for r in rows), default=0)
    def cell_value(self, rowx, colx):
        if rowx >= len(self.rows) or colx >= len(self.rows[rowx]):
            return ""
        value = self.rows[rowx][colx]
        return "" if value is None else value

def fetch(url: str) -> bytes:
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "kaigo-rules/1.0 (+https://github.com/Josh-Temple/kaigo-rules)"},
    )
    with urllib.request.urlopen(req, timeout=60) as res:
        return res.read()

def discover_workbook(page_url: str) -> str:
    html = fetch(page_url).decode("utf-8", errors="replace")
    parser = XlsLinkParser()
    parser.feed(html)
    if not parser.links:
        raise RuntimeError("No Excel Q&A link found on the MHLW Q&A page")
    return urllib.parse.urljoin(page_url, parser.links[0])

def load_sheets(payload: bytes):
    if payload[:2] == b"PK":
        book = openpyxl.load_workbook(BytesIO(payload), read_only=True, data_only=True)
        sheets = []
        for ws in book.worksheets:
            rows = [tuple(row) for row in ws.iter_rows(values_only=True)]
            sheets.append(SheetAdapter(ws.title, rows))
        return book.sheetnames, sheets, "xlsx"

    book = xlrd.open_workbook(file_contents=payload)
    sheets = [SheetAdapter(s.name, [tuple(s.row_values(r)) for r in range(s.nrows)]) for s in book.sheets()]
    return book.sheet_names(), sheets, "xls"

def clean(value) -> str:
    if value is None:
        return ""
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value).replace("\r\n", "\n").replace("\r", "\n").strip()

def norm(value) -> str:
    return re.sub(r"\s+", "", unicodedata.normalize("NFKC", clean(value))).lower()

def leading_code(value: str, width: int) -> str:
    text = unicodedata.normalize("NFKC", value)
    m = re.match(r"\s*(\d{1,2})", text)
    return m.group(1).zfill(width) if m else ""

def source_service_code(value: str) -> str:
    text = unicodedata.normalize("NFKC", value)
    m = re.match(r"\s*(\d{1,2}|XX)", text, re.I)
    if not m:
        return ""
    return m.group(1).upper()

def scope_label(value: str) -> str:
    text = unicodedata.normalize("NFKC", clean(value))
    first_line = text.splitlines()[0] if text else ""
    return re.sub(r"^\s*(?:\d{1,2}|XX)\s*[.．]?\s*", "", first_line, flags=re.I).strip()

LEGACY_COMPATIBLE_CODES = {
    "全サービス共通": "01",
    "居宅サービス共通": "02",
    "通所系サービス共通": "06",
    "通所介護事業": "16",
}

def canonical_service_code(scope: str) -> str:
    if scope in LEGACY_COMPATIBLE_CODES:
        return LEGACY_COMPATIBLE_CODES[scope]
    digest = hashlib.sha256(scope.encode("utf-8")).hexdigest()[:10]
    return "scope-" + digest

def canonical_service_code(value: str) -> str:
    scope = scope_label(value)
    return SERVICE_CODE_BY_SCOPE.get(scope) or leading_service_code(value)

def find_header(sheet):
    required = {"service", "criterion", "question", "answer"}
    for rowx in range(min(sheet.nrows, 40)):
        values = [norm(sheet.cell_value(rowx, colx)) for colx in range(sheet.ncols)]
        mapping = {}
        for colx, value in enumerate(values):
            if "サービス種別" in value or "サービス種類" in value:
                mapping.setdefault("service", colx)
                if rowx + 1 < sheet.nrows and colx + 1 < sheet.ncols:
                    next_label = norm(sheet.cell_value(rowx + 1, colx + 1))
                    if "qa以降" in next_label:
                        mapping.setdefault("service_current", colx + 1)
            elif "基準種別" in value or "基準種類" in value:
                mapping.setdefault("criterion", colx)
            elif value == "項目" or "項目" in value:
                mapping.setdefault("topic", colx)
            elif value == "質問" or value.endswith("質問"):
                mapping.setdefault("question", colx)
            elif value == "回答" or value.endswith("回答"):
                mapping.setdefault("answer", colx)
            elif ("発出時期" in value and "文書番号" in value) or "qa発出時期" in value:
                mapping.setdefault("issued_source", colx)
            elif value == "番号" or value.endswith("番号"):
                mapping.setdefault("number", colx)
        if required.issubset(mapping):
            service_col = mapping["service"]
            if rowx + 1 < sheet.nrows and service_col + 1 < sheet.ncols:
                next_header = norm(sheet.cell_value(rowx + 1, service_col + 1))
                if "qa以降" in next_header or "q&a以降" in next_header:
                    mapping["service_new"] = service_col + 1
            return rowx, mapping
    return None, None

def stable_id(row: dict) -> str:
    basis = "\u241f".join([
        row.get("service_code", ""),
        row.get("standard_code", ""),
        row.get("topic", ""),
        row.get("issued_source", ""),
        row.get("number", ""),
        row.get("question", ""),
    ])
    return "qa.mhlw." + hashlib.sha256(basis.encode("utf-8")).hexdigest()[:20]

def parse_workbook(payload: bytes):
    sheet_names, sheets, workbook_format = load_sheets(payload)
    items = []
    scanned = 0
    used_sheets = []
    unclassified_rows = []

    for sheet in sheets:
        header_row, cols = find_header(sheet)
        if cols is None:
            continue
        used_sheets.append(sheet.name)
        last_service = ""
        last_criterion = ""

        for rowx in range(header_row + 1, sheet.nrows):
            scanned += 1

            def get(name):
                col = cols.get(name)
                return clean(sheet.cell_value(rowx, col)) if col is not None else ""

            raw_service = get("service")
            current_service_scope = get("service_current")
            raw_criterion = get("criterion")
            service_raw = raw_service or last_service
            criterion_raw = raw_criterion or last_criterion
            if raw_service:
                last_service = raw_service
            if raw_criterion:
                last_criterion = raw_criterion

            question = get("question")
            answer = get("answer")
            if not question or not answer:
                continue

            service_code = canonical_service_code(service_raw)
            if not service_code:
                unclassified_rows.append({
                    "row": rowx + 1,
                    "service": service_raw,
                    "criterion": criterion_raw,
                    "topic": get("topic"),
                    "question": question[:120],
                })
                continue

            standard_code = leading_code(criterion_raw, 1)
            row = {
                "service_code": service_code,
                "service_label": service_raw,
                "scope": CANONICAL_SCOPE_BY_CODE.get(service_code, scope_label(service_raw)),
                "current_service_scope": current_service_scope,
                "standard_code": standard_code,
                "standard_label": criterion_raw,
                "topic": get("topic"),
                "question": question,
                "answer": answer,
                "issued_source": get("issued_source"),
                "number": get("number"),
                "source_id": "mhlw-qa",
                "ingestion_status": "INGESTED_UNREVIEWED",
            }
            row["id"] = stable_id(row)
            items.append(row)

    if not used_sheets:
        raise RuntimeError("Could not find a Q&A table header in any worksheet")
    if unclassified_rows:
        raise RuntimeError(
            "Q&A rows with question/answer but no service code: "
            + json.dumps(unclassified_rows[:10], ensure_ascii=False)
        )
    if len(items) < 10:
        raise RuntimeError(f"Only {len(items)} classified rows were parsed; refusing to overwrite corpus")

    dedup = {item["id"]: item for item in items}
    items = sorted(
        dedup.values(),
        key=lambda x: (
            x["service_code"],
            x["standard_code"],
            x["topic"],
            x["issued_source"],
            x["number"],
            x["id"],
        ),
    )
    return sheet_names, used_sheets, scanned, items, workbook_format

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--page-url", default=DEFAULT_PAGE)
    ap.add_argument("--xls-url", default="")
    ap.add_argument("--out", default="data/qa-corpus.json")
    ap.add_argument("--meta-out", default="data/qa-corpus-meta.json")
    args = ap.parse_args()

    workbook_url = args.xls_url or discover_workbook(args.page_url)
    payload = fetch(workbook_url)
    sha = hashlib.sha256(payload).hexdigest()
    sheet_names, used_sheets, scanned, items, workbook_format = parse_workbook(payload)
    counts = Counter(item["service_code"] for item in items)
    scope_by_code = {}
    for item in items:
        previous = scope_by_code.setdefault(item["service_code"], item["scope"])
        if previous != item["scope"]:
            raise RuntimeError(
                f"Canonical service-code collision for {item['service_code']}: {previous!r} vs {item['scope']!r}"
            )

    out = Path(args.out)
    meta_out = Path(args.meta_out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(items, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    meta = {
        "format_version": 1,
        "source_page": args.page_url,
        "source_workbook": workbook_url,
        "source_format": workbook_format,
        "source_sha256": sha,
        "scope_mode": "ALL_CLASSIFIED_ROWS_IN_OFFICIAL_WORKBOOK",
        "service_classification": {
            "primary_column": "平成31年2月5日Q&A以前",
            "current_scope_column": "平成31年3月15日Q&A以降",
            "note": "Primary code/scope is retained for stable filtering; current_service_scope preserves the later applicability column verbatim when present.",
        },
        "target_service_codes": sorted(scope_by_code),
        "scope_by_code": dict(sorted(scope_by_code.items())),
        "workbook_sheets": sheet_names,
        "parsed_sheets": used_sheets,
        "rows_scanned": scanned,
        "rows_included": len(items),
        "counts_by_service": dict(sorted(counts.items())),
        "review_status": "INGESTED_UNREVIEWED",
    }
    meta_out.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(meta, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
