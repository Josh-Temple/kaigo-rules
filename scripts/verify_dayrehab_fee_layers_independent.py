#!/usr/bin/env python3
"""Reparse official MHLW source files for dayrehab remuneration and guidance scope.

This is a bounded source-inventory check. A pass does not establish legal currentness,
visual column alignment, or human review.
"""
from __future__ import annotations

import hashlib
import html
import json
import re
import subprocess
import sys
import tempfile
import unicodedata
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REM_PATH = ROOT / "data/services/dayrehab/remuneration-index.json"
GUIDE_PATH = ROOT / "data/services/dayrehab/fee-guidance-index.json"
SOURCES = {
    "rem_base": "https://www.mhlw.go.jp/web/t_doc?dataId=82aa0253&dataType=0",
    "rem_patch": "https://www.mhlw.go.jp/content/12404000/001675895.pdf",
    "guide_r6": "https://www.mhlw.go.jp/content/12300000/001227887.pdf",
    "guide_r8": "https://www.mhlw.go.jp/content/12404000/001682729.pdf",
}
USER_AGENT = "kaigo-rules-dayrehab-independent-source-check/1.0"


class VisibleText(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []

    def handle_data(self, data: str) -> None:
        self.parts.append(data)


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", unicodedata.normalize("NFKC", html.unescape(text))).strip()


def fetch(url: str) -> bytes:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": USER_AGENT, "Cache-Control": "no-cache"},
    )
    with urllib.request.urlopen(request, timeout=45) as response:
        return response.read()


def pdf_text(payload: bytes) -> str:
    with tempfile.NamedTemporaryFile(suffix=".pdf") as source:
        source.write(payload)
        source.flush()
        result = subprocess.run(
            ["pdftotext", "-layout", "-enc", "UTF-8", source.name, "-"],
            check=True,
            capture_output=True,
            text=True,
            timeout=90,
        )
    return normalize(result.stdout)


def section(text: str, start: str, end: str, required_count: int | None = None) -> str:
    starts = list(re.finditer(start, text))
    for match in starts:
        end_match = re.search(end, text[match.end():])
        if not end_match:
            continue
        body = text[match.start():match.end() + end_match.start()]
        if required_count is None or len(body) > required_count:
            return body
    raise RuntimeError(f"could not locate bounded source section: {start} ... {end}")


def require(condition: bool, message: str, differences: list[str]) -> None:
    if not condition:
        differences.append(message)


def check_remuneration(rem: dict, observed: dict, differences: list[str]) -> dict:
    base_text = observed["rem_base_text"]
    base_section = section(
        base_text,
        r"7\s*通所リハビリテーション費",
        r"8\s*短期入所生活介護費\s*\(\s*1日",
        1000,
    )
    tariff_rows = [item for item in rem["items"] if item.get("kind") == "BASE_TARIFF_ROW"]
    expected_rates = [
        (rate["care_level"], int(rate["units"]))
        for item in tariff_rows
        for rate in item.get("rates", [])
    ]
    matrix_text = base_section.split("注1", 1)[0]
    found_rates = [
        (int(level), int(value.replace(",", "")))
        for level, value in re.findall(r"要介護\s*([1-5])\s*([0-9][0-9,]*)\s*単位", matrix_text)
    ]
    require(len(tariff_rows) == 14, "base source tariff row count is not 14", differences)
    require(len(expected_rates) == 70, "committed base rate value count is not 70", differences)
    require(found_rates == expected_rates, "MHLW base tariff sequence differs from the 70 committed source-version values", differences)
    expected_levels = [level for _ in tariff_rows for level in range(1, 6)]
    require([level for level, _ in found_rates] == expected_levels, "base tariff care-level ordering differs", differences)

    note_numbers = {
        int(value)
        for value in re.findall(r"注\s*(\d+)(?=\s|\()", base_section)
        if 1 <= int(value) <= 24
    }
    require(note_numbers == set(range(1, 25)), "source-visible note marker set is not 注1–注24", differences)
    for marker in ("ハ", "ニ", "ホ", "ヘ"):
        require(marker in base_section, f"source-visible additional item {marker} is missing", differences)
    require("短期入所生活介護費" not in base_section[:-40], "fee scope crosses into section 8", differences)

    patch_text = observed["rem_patch_text"]
    patch_start = re.search(r"7\s*通所リハビリテーション費", patch_text)
    if not patch_start:
        raise RuntimeError("R8告示の通所リハビリテーション費 section was not found")
    # The amendment PDF contains a patch excerpt and does not print the next section 8.
    patch_section = patch_text[patch_start.start():patch_start.start() + 6000]
    patch = rem["amendment_patches"][0]
    expected_fractions = {int(row["per_thousand"]) for row in patch["rates"]}
    observed_fractions = {
        int(value)
        for value in re.findall(r"1000\s*分\s*の\s*(\d+)", patch_section)
    }
    require(expected_fractions == {103, 111, 100, 108, 83, 70}, "committed R8 patch rate contract drifted", differences)
    require(expected_fractions.issubset(observed_fractions), "R8告示第87号 does not contain every recorded §7ヘ rate", differences)
    require(bool(re.search(r"イ\s*[~〜～-]\s*ホ\s*\(\s*略\s*\)", patch_section)), "R8告示 does not show イ〜ホ as an explicit omission", differences)
    return {
        "parent_items": len(rem["items"]),
        "base_tariff_rows_observed": len(tariff_rows),
        "base_tariff_values_observed": len(found_rates),
        "base_source_note_markers_observed": len(note_numbers),
        "r8_patch_rates_observed": len(expected_fractions),
        "r8_omitted_sections": patch["omitted_sections"],
        "currentness": "GAP",
    }


def marker_tokens(marker: str) -> list[str]:
    value = marker.replace("-current-side", "").replace("（略）", "").replace("(略)", "")
    value = unicodedata.normalize("NFKC", value)
    return [part.strip() for part in re.split(r"[-–—]", value) if part.strip()]


def check_guidance(guide: dict, observed: dict, differences: list[str]) -> dict:
    r6_text = observed["guide_r6_text"]
    r6_section = section(
        r6_text,
        r"8\s*通所リハビリテーション費",
        r"9\s*福祉用具貸与費",
        1000,
    )
    parents = guide["items"]
    parent_numbers = [int(item["slot"].split("(")[1].split(")")[0]) for item in parents]
    require(parent_numbers == list(range(1, 34)), "R6 parent-slot inventory is not 8-(1) through 8-(33)", differences)
    for number in range(1, 34):
        require(bool(re.search(rf"\({number}\)(?!\d)", r6_section)), f"R6 comparison marker 8-({number}) not found in bounded section", differences)

    children = [child for item in parents for child in item.get("children", [])]
    require(len(children) == 88, "committed visible child inventory is not 88", differences)
    found = 0
    for child in children:
        tokens = marker_tokens(child["marker"])
        if tokens and all(token in r6_section for token in tokens):
            found += 1
        else:
            differences.append(f"R6 visible child marker not found in section: {child['id']} {child['marker']}")
    require(found == 88, f"only {found}/88 R6 visible child markers were observed", differences)
    require("福祉用具貸与費" not in r6_section[:-40], "guidance scope crosses into section 9", differences)

    r8_patch = observed["guide_r8_text"]
    omitted = re.search(r"6\s*[~〜～]\s*9\s*\(\s*略\s*\)", r8_patch)
    require(omitted is not None, "R8 guidance patch no longer shows sections 6–9 omitted in its extracted text", differences)
    require(guide["state"]["currentness"] == "GAP", "guidance currentness must remain GAP", differences)
    return {
        "parent_items": len(parents),
        "parent_slots_observed": len(parent_numbers),
        "visible_child_items": len(children),
        "visible_child_markers_observed": found,
        "r8_section_omission_observed": bool(omitted),
        "visual_column_alignment": "NOT_VERIFIED",
        "currentness": "GAP",
    }


def main() -> int:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()

    rem = json.loads(REM_PATH.read_text(encoding="utf-8"))
    guide = json.loads(GUIDE_PATH.read_text(encoding="utf-8"))
    payloads = {key: fetch(url) for key, url in SOURCES.items()}
    observed = {}
    observed["rem_base_text"] = normalize(VisibleTextText(payloads["rem_base"]))
    observed["rem_patch_text"] = pdf_text(payloads["rem_patch"])
    observed["guide_r6_text"] = pdf_text(payloads["guide_r6"])
    observed["guide_r8_text"] = pdf_text(payloads["guide_r8"])

    differences: list[str] = []
    try:
        remuneration_coverage = check_remuneration(rem, observed, differences)
    except Exception as exc:
        differences.append(f"remuneration parse error: {exc}")
        remuneration_coverage = {}
    try:
        guidance_coverage = check_guidance(guide, observed, differences)
    except Exception as exc:
        differences.append(f"guidance parse error: {exc}")
        guidance_coverage = {}

    result = "PASS_BOUNDED_SCOPE_ONLY" if not differences else "FAIL"
    report = {
        "audit_kind": "INDEPENDENT_MHLW_SOURCE_INVENTORY_REPARSE",
        "audit_result": result,
        "sources": {
            key: {"url": url, "bytes": len(payloads[key]), "sha256": hashlib.sha256(payloads[key]).hexdigest()}
            for key, url in SOURCES.items()
        },
        "coverage": {"remuneration": remuneration_coverage, "fee_guidance": guidance_coverage},
        "safety": {
            "currentness_promoted": False,
            "human_review_promoted": False,
            "versions_merged": False,
            "visual_pdf_layout_claimed": False,
        },
        "differences": differences,
    }
    rendered = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    print(rendered, end="")
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(rendered, encoding="utf-8")
    return 0 if result == "PASS_BOUNDED_SCOPE_ONLY" else 1


def VisibleTextText(payload: bytes) -> str:
    parser = VisibleText()
    parser.feed(payload.decode("utf-8", errors="replace"))
    return " ".join(parser.parts)


if __name__ == "__main__":
    sys.exit(main())
