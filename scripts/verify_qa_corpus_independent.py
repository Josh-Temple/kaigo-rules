#!/usr/bin/env python3
"""Independently verify the MHLW Q&A corpus by parsing XLSX OOXML directly.

The production importer uses openpyxl/xlrd. This verifier intentionally avoids
those libraries and reads the XLSX ZIP/XML package with the Python standard
library, then independently reproduces header detection, all classified service rows,
stable IDs, de-duplication, and row content for the committed corpus.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import unicodedata
import urllib.request
import zipfile
from collections import Counter
from datetime import datetime, timedelta
from io import BytesIO
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
META_PATH = DATA / "qa-corpus-meta.json"
CORPUS_PATH = DATA / "qa-corpus.json"

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
    "介護予防支援": "50",
}
CANONICAL_SCOPE_BY_CODE = {code: scope for scope, code in SERVICE_CODE_BY_SCOPE.items()}

NS_MAIN = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
NS_REL_DOC = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
NS_REL_PKG = "http://schemas.openxmlformats.org/package/2006/relationships"


def q(ns: str, tag: str) -> str:
    return f"{{{ns}}}{tag}"


def fetch(url: str) -> bytes:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "kaigo-rules-independent-qa-verifier/1.0 (+https://github.com/Josh-Temple/kaigo-rules)"
        },
    )
    with urllib.request.urlopen(req, timeout=90) as response:
        return response.read()


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
    match = re.match(r"\s*(\d{1,2})", text)
    return match.group(1).zfill(width) if match else ""

def source_service_code(value: str) -> str:
    text = unicodedata.normalize("NFKC", value)
    match = re.match(r"\\s*(\\d{1,2}|XX)", text, re.I)
    if not match:
        return ""
    return match.group(1).upper()

def scope_label(value: str) -> str:
    text = unicodedata.normalize("NFKC", clean(value))
    first_line = text.splitlines()[0] if text else ""
    return re.sub(r"^\\s*(?:\\d{1,2}|XX)\\s*[.．]?\\s*", "", first_line, flags=re.I).strip()

def canonical_service_code(value: str) -> str:
    scope = scope_label(value)
    if not scope:
        return ""
    known = SERVICE_CODE_BY_SCOPE.get(scope)
    if known:
        return known
    digest = hashlib.sha256(scope.encode("utf-8")).hexdigest()[:10]
    return "scope-" + digest

def find_header(rows: list[list], ncols: int):
    required = {"service", "criterion", "question", "answer"}
    for rowx in range(min(len(rows), 40)):
        values = [norm(rows[rowx][colx] if colx < len(rows[rowx]) else "") for colx in range(ncols)]
        mapping = {}
        for colx, value in enumerate(values):
            if "サービス種別" in value or "サービス種類" in value:
                mapping.setdefault("service", colx)
                if rowx + 1 < len(rows) and colx + 1 < ncols:
                    next_row = rows[rowx + 1]
                    next_value = next_row[colx + 1] if colx + 1 < len(next_row) else ""
                    if "qa以降" in norm(next_value):
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
            if rowx + 1 < len(rows) and service_col + 1 < ncols:
                next_header = norm(rows[rowx + 1][service_col + 1] if service_col + 1 < len(rows[rowx + 1]) else "")
                if "qa以降" in next_header or "q&a以降" in next_header:
                    mapping["service_new"] = service_col + 1
            return rowx, mapping
    return None, None


def parse_xlsx(payload: bytes):
    archive = zipfile.ZipFile(BytesIO(payload))
    shared = shared_strings(archive)
    date_styles = date_style_indexes(archive)
    date1904 = workbook_date1904(archive)
    sheet_defs = workbook_sheets(archive)

    sheet_names = [name for name, _ in sheet_defs]
    used_sheets = []
    header_probes = []
    scanned = 0
    items = []
    unclassified_rows = []

    for name, path in sheet_defs:
        rows, nrows, ncols = load_sheet_rows(archive, path, shared, date_styles, date1904)
        header_row, cols = find_header(rows, ncols)
        if cols is None:
            probe = []
            for row in rows[:40]:
                values = [clean(value) for value in row[:16]]
                if any(values):
                    probe.append(values)
                if len(probe) >= 10:
                    break
            header_probes.append({"sheet": name, "rows": probe})
            continue
        used_sheets.append(name)
        last_service_old = ""
        last_service_new = ""
        active_service_period = ""
        last_criterion = ""

        for rowx in range(header_row + 1, nrows):
            scanned += 1

            def get(key):
                col = cols.get(key)
                if col is None:
                    return ""
                row = rows[rowx] if rowx < len(rows) else []
                return clean(row[col] if col < len(row) else "")

            raw_service_old = get("service")
            raw_service_current = get("service_current")
            raw_criterion = get("criterion")

            if raw_service_current:
                last_service_current = raw_service_current
                active_service_period = "POST_2019_03_15"
            elif raw_service_old:
                last_service_old = raw_service_old
                active_service_period = "PRE_2019_03_15"

            if active_service_period == "POST_2019_03_15":
                service_raw = raw_service_current or last_service_current
            else:
                service_raw = raw_service_old or last_service_old

            criterion_raw = raw_criterion or last_criterion
            if raw_criterion:
                last_criterion = raw_criterion

            question = get("question")
            answer = get("answer")
            if not question or not answer:
                continue

            service_code = canonical_service_code(service_raw)
            if not service_code:
                unclassified_rows.append(rowx + 1)
                continue

            standard_code = leading_code(criterion_raw, 1)
            item = {
                "service_code": service_code,
                "source_service_code": source_service_code(service_raw),
                "service_classification_period": active_service_period,
                "service_label": service_raw,
                "scope": CANONICAL_SCOPE_BY_CODE.get(service_code, scope_label(service_raw)),
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
            item["id"] = stable_id(item)
            items.append(item)

    if unclassified_rows:
        preview = ", ".join(str(row) for row in unclassified_rows[:10])
        raise RuntimeError(f"Q&A rows with question/answer but no service code: {preview}")

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
    return sheet_names, used_sheets, header_probes, scanned, items


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", help="Optional JSON report path")
    args = parser.parse_args()

    meta = json.loads(META_PATH.read_text(encoding="utf-8"))
    expected = json.loads(CORPUS_PATH.read_text(encoding="utf-8"))
    payload = fetch(meta["source_workbook"])
    observed_sha = hashlib.sha256(payload).hexdigest()

    errors = []
    differences = []

    if payload[:2] != b"PK":
        errors.append("source workbook is not XLSX/ZIP")
        observed = []
        sheet_names = []
        used_sheets = []
        header_probes = []
        scanned = 0
    else:
        try:
            sheet_names, used_sheets, header_probes, scanned, observed = parse_xlsx(payload)
        except Exception as exc:
            errors.append(str(exc))
            observed = []
            sheet_names = []
            used_sheets = []
            header_probes = []
            scanned = 0

    if observed_sha != meta.get("source_sha256"):
        differences.append({
            "difference": "source_sha256_mismatch",
            "expected": meta.get("source_sha256"),
            "observed": observed_sha,
        })
    if sheet_names != meta.get("workbook_sheets"):
        differences.append({
            "difference": "workbook_sheets_mismatch",
            "expected": meta.get("workbook_sheets"),
            "observed": sheet_names,
        })
    if used_sheets != meta.get("parsed_sheets"):
        differences.append({
            "difference": "parsed_sheets_mismatch",
            "expected": meta.get("parsed_sheets"),
            "observed": used_sheets,
        })
    if scanned != meta.get("rows_scanned"):
        differences.append({
            "difference": "rows_scanned_mismatch",
            "expected": meta.get("rows_scanned"),
            "observed": scanned,
        })

    observed_counts = dict(sorted(Counter(row["service_code"] for row in observed).items()))
    observed_scope_by_code = {}
    for row in observed:
        previous = observed_scope_by_code.setdefault(row["service_code"], row["scope"])
        if previous != row["scope"]:
            differences.append({
                "difference": "inconsistent_service_scope_label",
                "service_code": row["service_code"],
                "expected": previous,
                "observed": row["scope"],
            })
    observed_scope_by_code = dict(sorted(observed_scope_by_code.items()))
    expected_classification = {
        "primary_column": "平成31年2月5日Q&A以前",
        "current_scope_column": "平成31年3月15日Q&A以降",
        "note": "Primary code/scope is retained for stable filtering; current_service_scope preserves the later applicability column verbatim when present.",
    }
    if meta.get("service_classification") != expected_classification:
        differences.append({
            "difference": "service_classification_contract_mismatch",
            "expected": expected_classification,
            "observed": meta.get("service_classification"),
        })
    if meta.get("scope_mode") != "ALL_CLASSIFIED_ROWS_IN_OFFICIAL_WORKBOOK":
        differences.append({
            "difference": "scope_mode_mismatch",
            "expected": "ALL_CLASSIFIED_ROWS_IN_OFFICIAL_WORKBOOK",
            "observed": meta.get("scope_mode"),
        })
    if meta.get("target_service_codes") != sorted(observed_scope_by_code):
        differences.append({
            "difference": "target_service_codes_mismatch",
            "expected": meta.get("target_service_codes"),
            "observed": sorted(observed_scope_by_code),
        })
    if meta.get("scope_by_code") != observed_scope_by_code:
        differences.append({
            "difference": "scope_by_code_mismatch",
            "expected": meta.get("scope_by_code"),
            "observed": observed_scope_by_code,
        })
    if len(observed) != meta.get("rows_included"):
        differences.append({
            "difference": "rows_included_mismatch",
            "expected": meta.get("rows_included"),
            "observed": len(observed),
        })
    if observed_counts != meta.get("counts_by_service"):
        differences.append({
            "difference": "service_counts_mismatch",
            "expected": meta.get("counts_by_service"),
            "observed": observed_counts,
        })

    expected_by_id = {row["id"]: row for row in expected}
    observed_by_id = {row["id"]: row for row in observed}
    for row_id in sorted(set(expected_by_id) - set(observed_by_id)):
        differences.append({"id": row_id, "difference": "missing_from_independent_parse"})
    for row_id in sorted(set(observed_by_id) - set(expected_by_id)):
        differences.append({"id": row_id, "difference": "unexpected_in_independent_parse"})

    fields = [
        "service_code", "service_label", "scope", "current_service_scope", "standard_code", "standard_label",
        "topic", "question", "answer", "issued_source", "number", "source_id",
        "ingestion_status",
    ]
    for row_id in sorted(set(expected_by_id) & set(observed_by_id)):
        expected_row = expected_by_id[row_id]
        observed_row = observed_by_id[row_id]
        for field in fields:
            if expected_row.get(field) != observed_row.get(field):
                differences.append({
                    "id": row_id,
                    "difference": f"{field}_mismatch",
                    "expected_sha256": hashlib.sha256(clean(expected_row.get(field)).encode("utf-8")).hexdigest(),
                    "observed_sha256": hashlib.sha256(clean(observed_row.get(field)).encode("utf-8")).hexdigest(),
                })

    result = "PASS" if not errors and not differences else "FAIL"
    report = {
        "format_version": 1,
        "verification_kind": "INDEPENDENT_QA_XLSX_OOXML_REPARSE",
        "parser": "python_stdlib_zipfile_elementtree",
        "result": result,
        "source_workbook": meta.get("source_workbook"),
        "observed_source_sha256": observed_sha,
        "observed": {
            "sheet_names": sheet_names,
            "parsed_sheets": used_sheets,
            "header_probes": header_probes,
            "rows_scanned": scanned,
            "rows_included": len(observed),
            "counts_by_service": observed_counts,
            "scope_by_code": observed_scope_by_code,
        },
        "expected": {
            "rows_included": len(expected),
            "counts_by_service": meta.get("counts_by_service"),
        },
        "differences": differences,
        "errors": errors,
        "safety": {
            "promotes_human_review": False,
            "promotes_verified_current": False,
            "note": "Independent workbook parse only; source freshness and human review remain separate.",
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
