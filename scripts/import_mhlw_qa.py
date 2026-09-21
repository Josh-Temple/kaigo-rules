#!/usr/bin/env python3
import argparse
import hashlib
import json
import re
import unicodedata
import urllib.parse
import urllib.request
from collections import Counter
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path

import xlrd

DEFAULT_PAGE = "https://www.mhlw.go.jp/stf/seisakunitsuite/bunya/hukushi_kaigo/kaigo_koureisha/qa/index.html"
TARGET_SERVICE_CODES = {"01", "02", "06", "16"}
SCOPE_BY_CODE = {
    "01": "全サービス共通",
    "02": "居宅サービス共通",
    "06": "通所系サービス共通",
    "16": "通所介護事業",
}

class XlsLinkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
    def handle_starttag(self, tag, attrs):
        if tag.lower() != "a":
            return
        href = dict(attrs).get("href")
        if href and ".xls" in href.lower():
            self.links.append(href)

def fetch(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "kaigo-rules/1.0 (+https://github.com/Josh-Temple/kaigo-rules)"})
    with urllib.request.urlopen(req, timeout=60) as res:
        return res.read()

def discover_xls(page_url: str) -> str:
    html = fetch(page_url).decode("utf-8", errors="replace")
    parser = XlsLinkParser()
    parser.feed(html)
    if not parser.links:
        raise RuntimeError("No .xls link found on the MHLW Q&A page")
    # The official page lists the Q&A corpus XLS before the document-index XLS.
    return urllib.parse.urljoin(page_url, parser.links[0])

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

def find_header(sheet):
    required = {"service", "criterion", "question", "answer"}
    for rowx in range(min(sheet.nrows, 30)):
        values = [norm(sheet.cell_value(rowx, colx)) for colx in range(sheet.ncols)]
        mapping = {}
        for colx, value in enumerate(values):
            if "サービス種別" in value or "サービス種類" in value:
                mapping.setdefault("service", colx)
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
    book = xlrd.open_workbook(file_contents=payload)
    items = []
    scanned = 0
    used_sheets = []

    for sheet in book.sheets():
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

            service_raw = get("service") or last_service
            criterion_raw = get("criterion") or last_criterion
            if get("service"):
                last_service = get("service")
            if get("criterion"):
                last_criterion = get("criterion")

            question = get("question")
            answer = get("answer")
            if not question or not answer:
                continue

            service_code = leading_code(service_raw, 2)
            if service_code not in TARGET_SERVICE_CODES:
                continue

            standard_code = leading_code(criterion_raw, 1)
            row = {
                "service_code": service_code,
                "service_label": service_raw,
                "scope": SCOPE_BY_CODE[service_code],
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
    if len(items) < 10:
        raise RuntimeError(f"Only {len(items)} target rows were parsed; refusing to overwrite corpus")

    dedup = {}
    for item in items:
        dedup[item["id"]] = item
    items = sorted(dedup.values(), key=lambda x: (
        x["service_code"], x["standard_code"], x["topic"], x["issued_source"], x["number"], x["id"]
    ))
    return book.sheet_names(), used_sheets, scanned, items

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--page-url", default=DEFAULT_PAGE)
    ap.add_argument("--xls-url", default="")
    ap.add_argument("--out", default="data/qa-corpus.json")
    ap.add_argument("--meta-out", default="data/qa-corpus-meta.json")
    args = ap.parse_args()

    xls_url = args.xls_url or discover_xls(args.page_url)
    payload = fetch(xls_url)
    sha = hashlib.sha256(payload).hexdigest()
    sheet_names, used_sheets, scanned, items = parse_workbook(payload)
    counts = Counter(item["service_code"] for item in items)

    out = Path(args.out)
    meta_out = Path(args.meta_out)
    out.parent.mkdir(parents=True, exist_ok=True)
    generated = datetime.now(timezone.utc).isoformat()

    out.write_text(json.dumps(items, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    meta = {
        "format_version": 1,
        "generated_at": generated,
        "source_page": args.page_url,
        "source_xls": xls_url,
        "source_sha256": sha,
        "target_service_codes": sorted(TARGET_SERVICE_CODES),
        "scope_by_code": SCOPE_BY_CODE,
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
