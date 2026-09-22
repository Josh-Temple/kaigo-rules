#!/usr/bin/env python3
"""Independently verify current day-service remuneration source text.

The production importers use BeautifulSoup and their own extraction logic.
This verifier intentionally uses Python's standard-library HTMLParser and
separate section discovery. It compares normalized official-source text
against the committed datasets without promoting any review status.
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

NOTICE19_URL = "https://www.mhlw.go.jp/web/t_doc?dataId=82aa0253&dataType=0"
NOTICE27_URL = "https://www.mhlw.go.jp/web/t_doc?dataId=82aa0261&dataType=0&pageNo=1"
NOTICE95_URL = "https://www.mhlw.go.jp/web/t_doc?dataId=82ab4584&dataType=0&pageNo=1"

CURRENT_ID_ORDER = [
    "fee.dayservice.standard",
    "fee.dayservice.large1",
    "fee.dayservice.large2",
    *[f"fee.dayservice.note.{i}" for i in range(1, 25)],
    "fee.dayservice.service-provision",
    "fee.dayservice.treatment-improvement",
]

NOTICE95_SCOPE = [
    ("十四の三", "criteria95.dayservice.14-3"),
    ("十四の四", "criteria95.dayservice.14-4"),
    ("十四の五", "criteria95.dayservice.14-5"),
    ("十四の六", "criteria95.dayservice.14-6"),
    ("十五", "criteria95.dayservice.15"),
    ("十六", "criteria95.dayservice.16"),
    ("十七", "criteria95.dayservice.17"),
    ("十八の二", "criteria95.dayservice.18-2"),
    ("十九", "criteria95.dayservice.19"),
    ("十九の二", "criteria95.dayservice.19-2"),
    ("二十", "criteria95.dayservice.20"),
    ("二十三", "criteria95.dayservice.23"),
    ("二十四", "criteria95.dayservice.24"),
]


def clean(value: str) -> str:
    return " ".join(unicodedata.normalize("NFKC", value).split())


def compact(value: str) -> str:
    return re.sub(r"\s+", "", unicodedata.normalize("NFKC", value))


def semantic_sha(value: str) -> str:
    return hashlib.sha256(compact(value).encode("utf-8")).hexdigest()


class VisibleTextParser(HTMLParser):
    """Collect non-empty visible data fragments in document order."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.fragments: list[str] = []
        self.suppressed_depth = 0

    def handle_starttag(self, tag: str, attrs) -> None:
        if tag.lower() in {"script", "style"}:
            self.suppressed_depth += 1

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() in {"script", "style"} and self.suppressed_depth:
            self.suppressed_depth -= 1

    def handle_data(self, data: str) -> None:
        if self.suppressed_depth:
            return
        value = clean(data)
        if value:
            self.fragments.append(value)


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


def visible_fragments(html: str) -> list[str]:
    parser = VisibleTextParser()
    parser.feed(html)
    parser.close()
    return parser.fragments


def locate_prefix(lines: list[str], prefix: str, start: int = 0) -> int:
    needle = compact(prefix)
    for index in range(start, len(lines)):
        if compact(lines[index]).startswith(needle):
            return index
    raise RuntimeError(f"Independent verifier could not locate prefix: {prefix}")


def locate_numbered(lines: list[str], number: int, start: int = 0) -> int:
    pattern = re.compile(rf"^{number}\s+")
    for index in range(start, len(lines)):
        if pattern.match(clean(lines[index])):
            return index
    raise RuntimeError(f"Independent verifier could not locate numbered note: {number}")


TOP_HEADING = re.compile(r"^([一二三四五六七八九十百]+(?:の[一二三四五六七八九十百]+)?)\s+(.+)$")


def next_top_heading(lines: list[str], start: int) -> int:
    for index in range(start + 1, len(lines)):
        if TOP_HEADING.match(clean(lines[index])):
            return index
    return len(lines)


def extract_notice19(lines: list[str]) -> dict[str, str]:
    start = locate_prefix(lines, "6 通所介護費")
    end = locate_prefix(lines, "7 通所リハビリテーション費", start + 1)
    section = lines[start:end]

    found: list[tuple[str, int]] = []
    cursor = 0
    for node_id, marker in [
        ("fee.dayservice.standard", "イ 通常規模型通所介護費"),
        ("fee.dayservice.large1", "ロ 大規模型通所介護費"),
        ("fee.dayservice.large2", "ハ 大規模型通所介護費"),
    ]:
        index = locate_prefix(section, marker, cursor)
        found.append((node_id, index))
        cursor = index + 1

    for number in range(1, 25):
        index = locate_numbered(section, number, cursor)
        found.append((f"fee.dayservice.note.{number}", index))
        cursor = index + 1

    for node_id, marker in [
        ("fee.dayservice.service-provision", "ニ サービス提供体制強化加算"),
        ("fee.dayservice.treatment-improvement", "ホ 介護職員等処遇改善加算"),
    ]:
        index = locate_prefix(section, marker, cursor)
        found.append((node_id, index))
        cursor = index + 1

    ids = [node_id for node_id, _ in found]
    if ids != CURRENT_ID_ORDER:
        raise RuntimeError("Independent Notice 19 boundary order differs from expected scope")

    result: dict[str, str] = {}
    for pos, (node_id, index) in enumerate(found):
        next_index = found[pos + 1][1] if pos + 1 < len(found) else len(section)
        text = "\n".join(section[index:next_index]).strip()
        if not text:
            raise RuntimeError(f"Independent Notice 19 extraction is empty: {node_id}")
        result[node_id] = text
    return result


def extract_notice27(lines: list[str]) -> dict[str, str]:
    start = locate_prefix(lines, "一 厚生労働大臣が定める利用者の数の基準")
    end = next_top_heading(lines, start)
    section = lines[start:end]

    index_i = locate_prefix(section, "イ 指定通所介護")
    index_ro = locate_prefix(section, "ロ 指定通所介護事業所", index_i + 1)
    if index_ro <= index_i:
        raise RuntimeError("Independent Notice 27 subsection order is invalid")

    return {
        "calc27.dayservice.1": "\n".join(section).strip(),
        "calc27.dayservice.1.capacity": "\n".join(section[index_i:index_ro]).strip(),
        "calc27.dayservice.1.staffing": "\n".join(section[index_ro:]).strip(),
    }


def find_top_heading(lines: list[str], label: str, required_text: str) -> int:
    for index, line in enumerate(lines):
        match = TOP_HEADING.match(clean(line))
        if not match:
            continue
        if match.group(1) == label and required_text in match.group(2):
            return index
    raise RuntimeError(f"Independent Notice 95 heading not found: {label} / {required_text}")


def extract_notice95(lines: list[str]) -> dict[str, str]:
    result: dict[str, str] = {}

    for label, node_id in NOTICE95_SCOPE:
        start = find_top_heading(lines, label, "通所介護費")
        end = next_top_heading(lines, start)
        text = "\n".join(lines[start:end]).strip()
        if not text:
            raise RuntimeError(f"Independent Notice 95 extraction is empty: {node_id}")
        result[node_id] = text

    shared_start = find_top_heading(lines, "四", "訪問介護費における介護職員等処遇改善加算")
    shared_end = next_top_heading(lines, shared_start)
    result["criteria95.shared.4"] = "\n".join(lines[shared_start:shared_end]).strip()

    return result


def load_json(name: str):
    return json.loads((DATA / name).read_text(encoding="utf-8"))


def compare_text_map(observed: dict[str, str], expected: dict[str, str], family: str) -> list[dict]:
    differences = []
    observed_ids = set(observed)
    expected_ids = set(expected)

    for node_id in sorted(expected_ids - observed_ids):
        differences.append({"family": family, "id": node_id, "difference": "missing_from_independent_extraction"})
    for node_id in sorted(observed_ids - expected_ids):
        differences.append({"family": family, "id": node_id, "difference": "unexpected_independent_extraction"})

    for node_id in sorted(observed_ids & expected_ids):
        observed_text = observed[node_id]
        expected_text = expected[node_id]
        if compact(observed_text) != compact(expected_text):
            differences.append({
                "family": family,
                "id": node_id,
                "difference": "semantic_text_mismatch",
                "expected_semantic_sha256": semantic_sha(expected_text),
                "observed_semantic_sha256": semantic_sha(observed_text),
                "expected_compact_chars": len(compact(expected_text)),
                "observed_compact_chars": len(compact(observed_text)),
            })
    return differences


def compare() -> dict:
    payload19, html19 = fetch(NOTICE19_URL)
    payload27, html27 = fetch(NOTICE27_URL)
    payload95, html95 = fetch(NOTICE95_URL)

    observed19 = extract_notice19(visible_fragments(html19))
    observed27 = extract_notice27(visible_fragments(html27))
    observed95 = extract_notice95(visible_fragments(html95))

    current_rows = load_json("remuneration-current-text.json")
    current_meta = load_json("remuneration-current-text-meta.json")
    delegated_rows = load_json("remuneration-delegated-nodes.json")
    delegated_meta = load_json("remuneration-delegated-meta.json")

    expected19 = {row["fee_id"]: row["official_text"] for row in current_rows}
    expected27 = {
        row["id"]: row["official_text"]
        for row in delegated_rows
        if row["source_id"] == "mhlw-fee-notice27-base"
    }
    expected95 = {
        row["id"]: row["official_text"]
        for row in delegated_rows
        if row["source_id"] == "mhlw-fee-criteria95-current"
    }

    text_differences = []
    text_differences.extend(compare_text_map(observed19, expected19, "notice19"))
    text_differences.extend(compare_text_map(observed27, expected27, "notice27"))
    text_differences.extend(compare_text_map(observed95, expected95, "notice95"))

    sha19 = hashlib.sha256(payload19).hexdigest()
    sha27 = hashlib.sha256(payload27).hexdigest()
    sha95 = hashlib.sha256(payload95).hexdigest()

    metadata_differences = []
    if current_meta.get("source_url") != NOTICE19_URL:
        metadata_differences.append("remuneration-current-text-meta source_url differs from verifier URL")
    if current_meta.get("source_sha256") != sha19:
        metadata_differences.append("remuneration-current-text-meta source_sha256 differs from current live source")
    if current_meta.get("record_count") != len(observed19):
        metadata_differences.append("remuneration-current-text-meta record_count differs from independent extraction")

    source27 = delegated_meta.get("sources", {}).get("notice27", {})
    source95 = delegated_meta.get("sources", {}).get("notice95", {})
    if source27.get("url") != NOTICE27_URL:
        metadata_differences.append("remuneration-delegated-meta notice27 URL differs from verifier URL")
    if source27.get("sha256") != sha27:
        metadata_differences.append("remuneration-delegated-meta notice27 SHA-256 differs from current live source")
    if source95.get("url") != NOTICE95_URL:
        metadata_differences.append("remuneration-delegated-meta notice95 URL differs from verifier URL")
    if source95.get("sha256") != sha95:
        metadata_differences.append("remuneration-delegated-meta notice95 SHA-256 differs from current live source")

    observed_counts = {
        "notice19_records": len(observed19),
        "notice27_nodes": len(observed27),
        "notice95_nodes": len(observed95),
        "delegated_nodes": len(observed27) + len(observed95),
    }
    expected_counts = delegated_meta.get("counts", {})
    if expected_counts.get("notice27_nodes") != observed_counts["notice27_nodes"]:
        metadata_differences.append("remuneration-delegated-meta notice27_nodes differs from independent extraction")
    if expected_counts.get("notice95_nodes") != observed_counts["notice95_nodes"]:
        metadata_differences.append("remuneration-delegated-meta notice95_nodes differs from independent extraction")
    if expected_counts.get("nodes") != observed_counts["delegated_nodes"]:
        metadata_differences.append("remuneration-delegated-meta nodes differs from independent extraction")

    result = "PASS" if not text_differences and not metadata_differences else "FAIL"
    return {
        "format_version": 1,
        "verification_kind": "INDEPENDENT_MACHINE_REPARSE",
        "parser": "python_stdlib_html_parser",
        "sources": {
            "notice19": {"url": NOTICE19_URL, "sha256": sha19},
            "notice27": {"url": NOTICE27_URL, "sha256": sha27},
            "notice95": {"url": NOTICE95_URL, "sha256": sha95},
        },
        "result": result,
        "observed": observed_counts,
        "differences": {
            "text": text_differences,
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
