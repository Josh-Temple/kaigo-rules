#!/usr/bin/env python3
"""Independently verify the MHLW Q&A corpus by parsing XLSX OOXML directly.

The production importer uses openpyxl/xlrd. This verifier intentionally avoids
those libraries and reads the XLSX ZIP/XML package with the Python standard
library, then independently reproduces header detection, service-code filtering,
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

TARGET_SERVICE_CODES = {"01", "02", "06", "16"}
SCOPE_BY_CODE = {
    "01": "全サービス共通",
    "02": "居宅サービス共通",
    "06": "通所系サービス共通",
    "16": "通所介護事業",
}

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


def stable_id(row: dict) -> str:
    basis = "\u241f".join(
        [
            row.get("service_code", ""),
            row.get("standard_code", ""),
            row.get("topic", ""),
            row.get("issued_source", ""),
            row.get("number", ""),
            row.get("question", ""),
        ]
    )
    return "qa.mhlw." + hashlib.sha256(basis.encode("utf-8")).hexdigest()[:20]


def col_index(cell_ref: str) -> int:
    match = re.match(r"([A-Z]+)", cell_ref or "")
    if not match:
        return 0
    result = 0
    for char in match.group(1):
        result = result * 26 + (ord(char) - ord("A") + 1)
    return result - 1


def shared_strings(archive: zipfile.ZipFile) -> list[str]:
    try:
        root = ET.fromstring(archive.read("xl/sharedStrings.xml"))
    except KeyError:
        return []
    values = []
    for si in root.findall(q(NS_MAIN, "si")):
        chunks = [node.text or "" for node in si.iter(q(NS_MAIN, "t"))]
        values.append("".join(chunks))
    return values


def date_style_indexes(archive: zipfile.ZipFile) -> set[int]:
    try:
        root = ET.fromstring(archive.read("xl/styles.xml"))
    except KeyError:
        return set()

    custom = {}
    numfmts = root.find(q(NS_MAIN, "numFmts"))
    if numfmts is not None:
        for fmt in numfmts.findall(q(NS_MAIN, "numFmt")):
            try:
                custom[int(fmt.attrib.get("numFmtId", "0"))] = fmt.attrib.get("formatCode", "")
            except ValueError:
                pass

    builtin_date_ids = set(range(14, 23)) | set(range(27, 37)) | set(range(45, 48)) | set(range(50, 59))
    result = set()
    cell_xfs = root.find(q(NS_MAIN, "cellXfs"))
    if cell_xfs is None:
        return result

    for index, xf in enumerate(cell_xfs.findall(q(NS_MAIN, "xf"))):
        try:
            fmt_id = int(xf.attrib.get("numFmtId", "0"))
        except ValueError:
            continue
        if fmt_id in builtin_date_ids:
            result.add(index)
            continue
        code = custom.get(fmt_id, "").lower()
        stripped = re.sub(r'"[^"]*"|\\.|\[[^\]]*\]', "", code)
        if any(token in stripped for token in ("yy", "dd", "hh", "ss")):
            result.add(index)
    return result


def workbook_date1904(archive: zipfile.ZipFile) -> bool:
    root = ET.fromstring(archive.read("xl/workbook.xml"))
    props = root.find(q(NS_MAIN, "workbookPr"))
    return props is not None and props.attrib.get("date1904") in {"1", "true", "True"}


def excel_datetime(serial: float, date1904: bool):
    epoch = datetime(1904, 1, 1) if date1904 else datetime(1899, 12, 30)
    value = epoch + timedelta(days=serial)
    if value.time().hour == 0 and value.time().minute == 0 and value.time().second == 0 and value.microsecond == 0:
        return value.date()
    return value


def workbook_sheets(archive: zipfile.ZipFile) -> list[tuple[str, str]]:
    workbook = ET.fromstring(archive.read("xl/workbook.xml"))
    rels = ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
    targets = {}
    for rel in rels.findall(q(NS_REL_PKG, "Relationship")):
        targets[rel.attrib.get("Id", "")] = rel.attrib.get("Target", "")

    result = []
    sheets = workbook.find(q(NS_MAIN, "sheets"))
    if sheets is None:
        return result
    for sheet in sheets.findall(q(NS_MAIN, "sheet")):
        rid = sheet.attrib.get(q(NS_REL_DOC, "id"), "")
        target = targets.get(rid, "")
        if target.startswith("/"):
            path = target.lstrip("/")
        elif target.startswith("xl/"):
            path = target
        else:
            path = "xl/" + target.lstrip("/")
        result.append((sheet.attrib.get("name", ""), path))
    return result


def cell_value(cell, shared: list[str], date_styles: set[int], date1904: bool):
    cell_type = cell.attrib.get("t")
    style_raw = cell.attrib.get("s")
    try:
        style = int(style_raw) if style_raw is not None else -1
    except ValueError:
        style = -1

    if cell_type == "inlineStr":
        inline = cell.find(q(NS_MAIN, "is"))
        if inline is None:
            return ""
        return "".join(node.text or "" for node in inline.iter(q(NS_MAIN, "t")))

    value_node = cell.find(q(NS_MAIN, "v"))
    raw = value_node.text if value_node is not None and value_node.text is not None else ""

    if cell_type == "s":
        try:
            return shared[int(raw)]
        except (ValueError, IndexError):
            return ""
    if cell_type == "str":
        return raw
    if cell_type == "b":
        return raw == "1"
    if raw == "":
        return ""

    try:
        number = float(raw)
    except ValueError:
        return raw
    if style in date_styles:
        return excel_datetime(number, date1904)
    return int(number) if number.is_integer() else number


def load_sheet_rows(
    archive: zipfile.ZipFile,
    path: str,
    shared: list[str],
    date_styles: set[int],
    date1904: bool,
) -> tuple[list[list], int, int]:
    root = ET.fromstring(archive.read(path))
    sheet_data = root.find(q(NS_MAIN, "sheetData"))
    if sheet_data is None:
        return [], 0, 0

    rows_by_index: dict[int, dict[int, object]] = {}
    max_row = 0
    max_col = 0
    next_row = 1

    for row in sheet_data.findall(q(NS_MAIN, "row")):
        try:
            row_index = int(row.attrib.get("r", str(next_row)))
        except ValueError:
            row_index = next_row
        next_row = row_index + 1
        max_row = max(max_row, row_index)
        cells = {}
        for cell in row.findall(q(NS_MAIN, "c")):
            index = col_index(cell.attrib.get("r", ""))
            max_col = max(max_col, index + 1)
            cells[index] = cell_value(cell, shared, date_styles, date1904)
        rows_by_index[row_index] = cells

    rows = []
    for row_index in range(1, max_row + 1):
        cell_map = rows_by_index.get(row_index, {})
        rows.append([cell_map.get(col, "") for col in range(max_col)])
    return rows, max_row, max_col


def find_header(rows: list[list], ncols: int):
    required = {"service", "criterion", "question", "answer"}
    for rowx in range(min(len(rows), 40)):
        values = [norm(rows[rowx][colx] if colx < len(rows[rowx]) else "") for colx in range(ncols)]
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
        last_service = ""
        last_criterion = ""

        for rowx in range(header_row + 1, nrows):
            scanned += 1

            def get(key):
                col = cols.get(key)
                if col is None:
                    return ""
                row = rows[rowx] if rowx < len(rows) else []
                return clean(row[col] if col < len(row) else "")

            raw_service = get("service")
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

            service_code = leading_code(service_raw, 2)
            if service_code not in TARGET_SERVICE_CODES:
                continue

            standard_code = leading_code(criterion_raw, 1)
            item = {
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
            item["id"] = stable_id(item)
            items.append(item)

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
        "service_code", "service_label", "scope", "standard_code", "standard_label",
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
