#!/usr/bin/env python3
"""Independently verify day-service fee-guidance -> remuneration relations.

The verifier intentionally reconstructs the two sides from official sources:
- R6 fee-guidance redline PDF, current/new left column, for guidance headings.
- Live MHLW Notice 19 HTML for remuneration text.

It validates relation identities only. It does not promote guidance currentness,
human review, or legal correctness beyond the explicit source evidence checked.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
import unicodedata
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

GUIDANCE_URL = "https://www.mhlw.go.jp/content/12300000/001227887.pdf"
NOTICE19_URL = "https://www.mhlw.go.jp/web/t_doc?dataId=82aa0253&dataType=0"

# Each spec states the evidence that must independently appear on both official
# source sides before the committed relation identity can pass.
SPECS = [
    ("fee-guidance.dayservice.root", "通所介護費", "fee.dayservice.root", ["通所介護費"]),
    ("fee-guidance.dayservice.1", "所要時間による区分の取扱い", "fee.dayservice.standard", ["所要時間"]),
    ("fee-guidance.dayservice.1", "所要時間による区分の取扱い", "fee.dayservice.large1", ["所要時間"]),
    ("fee-guidance.dayservice.1", "所要時間による区分の取扱い", "fee.dayservice.large2", ["所要時間"]),
    ("fee-guidance.dayservice.1", "所要時間による区分の取扱い", "fee.dayservice.note.4", ["所要時間", "2時間以上3時間未満"]),
    ("fee-guidance.dayservice.2", "高齢者虐待防止措置未実施減算について", "fee.dayservice.note.2", ["高齢者虐待防止措置未実施減算"]),
    ("fee-guidance.dayservice.3", "業務継続計画未策定減算について", "fee.dayservice.note.3", ["業務継続計画未策定減算"]),
    ("fee-guidance.dayservice.8", "生活相談員配置等加算について", "fee.dayservice.note.8", ["生活相談員配置等加算"]),
    ("fee-guidance.dayservice.9", "注9の取扱い", "fee.dayservice.note.9", ["9", "通常の事業の実施地域"]),
    ("fee-guidance.dayservice.10", "入浴介助加算について", "fee.dayservice.note.10", ["入浴介助加算"]),
    ("fee-guidance.dayservice.11", "中重度者ケア体制加算について", "fee.dayservice.note.11", ["中重度者ケア体制加算"]),
    ("fee-guidance.dayservice.12", "生活機能向上連携加算について", "fee.dayservice.note.12", ["生活機能向上連携加算"]),
    ("fee-guidance.dayservice.13", "個別機能訓練加算について", "fee.dayservice.note.13", ["個別機能訓練"]),
    ("fee-guidance.dayservice.14", "ADL維持等加算について", "fee.dayservice.note.14", ["ADL", "維持等加算"]),
    ("fee-guidance.dayservice.15", "認知症加算について", "fee.dayservice.note.15", ["認知症加算"]),
    ("fee-guidance.dayservice.16", "若年性認知症利用者受入加算について", "fee.dayservice.note.16", ["若年性認知症利用者"]),
    ("fee-guidance.dayservice.17", "栄養アセスメント加算について", "fee.dayservice.note.17", ["栄養アセスメント"]),
    ("fee-guidance.dayservice.19", "口腔・栄養スクリーニング加算について", "fee.dayservice.note.19", ["栄養スクリーニング加算"]),
    ("fee-guidance.dayservice.20", "口腔機能向上加算について", "fee.dayservice.note.20", ["機能向上加算"]),
    ("fee-guidance.dayservice.21", "科学的介護推進体制加算について", "fee.dayservice.note.21", ["科学的介護推進体制加算"]),
    ("fee-guidance.dayservice.22", "事業所と同一の建物に居住する利用者又は同一建物から通う利用者に通所介護を行う場合の取扱い", "fee.dayservice.note.23", ["同一建物", "94単位"]),
    ("fee-guidance.dayservice.23", "送迎を行わない場合の減算について", "fee.dayservice.note.24", ["送迎を行わない場合", "47単位"]),
    ("fee-guidance.dayservice.26", "サービス提供体制強化加算について", "fee.dayservice.service-provision", ["サービス提供体制強化加算"]),
    ("fee-guidance.dayservice.27", "介護職員等処遇改善加算について", "fee.dayservice.treatment-improvement", ["介護職員等処遇改善加算"]),
]


def compact(value: str) -> str:
    return re.sub(r"\s+", "", unicodedata.normalize("NFKC", value or ""))


def fetch_bytes(url: str) -> bytes:
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "kaigo-rules-fee-guidance-relation-verifier/1.0 (+https://github.com/Josh-Temple/kaigo-rules)"},
    )
    with urllib.request.urlopen(req, timeout=60) as response:
        return response.read()


def decode_html(payload: bytes) -> str:
    for encoding in ("utf-8", "cp932", "shift_jis"):
        try:
            return payload.decode(encoding)
        except UnicodeDecodeError:
            pass
    return payload.decode("utf-8", errors="replace")


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
    raise RuntimeError(f"could not locate prefix: {prefix}")


def locate_numbered(lines: list[str], number: int, start: int = 0) -> int:
    pattern = re.compile(rf"^{number}\s+")
    for index in range(start, len(lines)):
        if pattern.match(" ".join(lines[index].split())):
            return index
    raise RuntimeError(f"could not locate numbered note: {number}")


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

    result = {"fee.dayservice.root": "\n".join(section).strip()}
    for pos, (node_id, index) in enumerate(found):
        next_index = found[pos + 1][1] if pos + 1 < len(found) else len(section)
        result[node_id] = "\n".join(section[index:next_index]).strip()
    return result


def require_poppler() -> None:
    for command in ("pdftotext", "pdfinfo"):
        if shutil.which(command) is None:
            raise RuntimeError(f"{command} is required")


def page_size(pdf: Path, page: int) -> tuple[float, float]:
    proc = subprocess.run(
        ["pdfinfo", "-f", str(page), "-l", str(page), str(pdf)],
        check=True,
        capture_output=True,
        text=True,
    )
    match = re.search(r"(?:Page\s+\d+\s+size|Page size):\s*([0-9.]+)\s+x\s+([0-9.]+)\s+pts", proc.stdout)
    if not match:
        raise RuntimeError("could not determine PDF page size")
    return float(match.group(1)), float(match.group(2))


def extract_guidance_current_column(pdf: Path) -> str:
    width, height = page_size(pdf, 42)
    half = width / 2.0
    crop_width = max(1, int(round(half - 4.0)))
    proc = subprocess.run(
        [
            "pdftotext",
            "-r", "72",
            "-f", "42",
            "-l", "53",
            "-layout",
            "-x", "0",
            "-y", "0",
            "-W", str(crop_width),
            "-H", str(int(round(height))),
            "-enc", "UTF-8",
            str(pdf),
            "-",
        ],
        check=True,
        capture_output=True,
    )
    return proc.stdout.decode("utf-8", errors="strict")


def relation_identity(row: dict) -> tuple[str, str, str]:
    return (
        str(row.get("from_guidance_id") or ""),
        str(row.get("relation") or ""),
        str(row.get("to_fee_id") or ""),
    )


def verify() -> dict:
    require_poppler()
    guidance_payload = fetch_bytes(GUIDANCE_URL)
    notice_payload = fetch_bytes(NOTICE19_URL)

    if not guidance_payload.startswith(b"%PDF"):
        raise RuntimeError("guidance source is not a PDF")

    with tempfile.TemporaryDirectory() as tmp:
        pdf = Path(tmp) / "guidance.pdf"
        pdf.write_bytes(guidance_payload)
        guidance_text = extract_guidance_current_column(pdf)

    notice_text = decode_html(notice_payload)
    notice_nodes = extract_notice19(visible_fragments(notice_text))
    guidance_compact = compact(guidance_text)

    committed = json.loads((DATA / "fee-guidance-relations.json").read_text(encoding="utf-8"))
    committed_identities = {relation_identity(row) for row in committed}
    expected_identities = {
        (guidance_id, "explains_calculation_of", fee_id)
        for guidance_id, _, fee_id, _ in SPECS
    }

    global_differences: list[str] = []
    if committed_identities != expected_identities:
        global_differences.append("committed relation identity set differs from verifier scope")

    checks = []
    for guidance_id, guidance_heading, fee_id, fee_phrases in SPECS:
        differences = []
        if compact(guidance_heading) not in guidance_compact:
            differences.append("guidance heading not found in R6 current/new column")
        fee_text = notice_nodes.get(fee_id, "")
        if not fee_text:
            differences.append("fee target missing from live Notice 19 extraction")
        fee_compact = compact(fee_text)
        for phrase in fee_phrases:
            if compact(phrase) not in fee_compact:
                differences.append(f"fee evidence phrase missing: {phrase}")

        identity_present = (
            guidance_id,
            "explains_calculation_of",
            fee_id,
        ) in committed_identities
        if not identity_present:
            differences.append("committed relation identity missing")

        checks.append(
            {
                "id": f"{guidance_id}-to-{fee_id}",
                "from_guidance_id": guidance_id,
                "relation": "explains_calculation_of",
                "to_fee_id": fee_id,
                "guidance_heading_evidence": guidance_heading,
                "fee_required_phrases": fee_phrases,
                "result": "PASS" if not differences else "FAIL",
                "differences": differences,
            }
        )

    result = "PASS" if not global_differences and all(row["result"] == "PASS" for row in checks) else "FAIL"
    return {
        "format_version": 1,
        "verification_kind": "INDEPENDENT_PRIMARY_SOURCE_RELATION_REPARSE",
        "parser": {
            "guidance_pdf": "pdftotext_current_left_column_pages_42_53",
            "notice19_html": "python_stdlib_html_parser",
        },
        "sources": {
            "guidance_r6_redline": {
                "url": GUIDANCE_URL,
                "sha256": hashlib.sha256(guidance_payload).hexdigest(),
            },
            "notice19": {
                "url": NOTICE19_URL,
                "sha256": hashlib.sha256(notice_payload).hexdigest(),
            },
        },
        "result": result,
        "checks": checks,
        "coverage": {
            "relations_in_scope": len(SPECS),
            "relations_passed": sum(row["result"] == "PASS" for row in checks),
        },
        "differences": global_differences,
        "safety": {
            "promotes_human_review": False,
            "promotes_verified_current": False,
            "promotes_guidance_text_currentness": False,
            "note": "PASS covers only the explicit relation identities evidenced by the current-side R6 guidance headings and live Notice 19 target text.",
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
