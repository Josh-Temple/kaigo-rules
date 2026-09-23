#!/usr/bin/env python3
"""Independently verify explicit remuneration delegation relations.

Production importers use BeautifulSoup and hand-authored mapping tables.
This verifier uses only Python standard-library HTMLParser, fetches the live
MHLW consolidated HTML for Notices 19, 27 and 95, and audits only relations
whose target can be tied to explicit source wording/title correspondence.

PASS does not promote HUMAN_VERIFIED or VERIFIED_CURRENT.
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

TITLE_CHECKS = [
    ("fee.dayservice.note.10", "criteria_set_by", "criteria95.dayservice.14-6", "入浴介助加算"),
    ("fee.dayservice.note.11", "criteria_set_by", "criteria95.dayservice.15", "中重度者ケア体制加算"),
    ("fee.dayservice.note.13", "criteria_set_by", "criteria95.dayservice.16", "個別機能訓練加算"),
    ("fee.dayservice.note.15", "criteria_set_by", "criteria95.dayservice.17", "認知症加算"),
    ("fee.dayservice.note.17", "criteria_set_by", "criteria95.dayservice.18-2", "栄養アセスメント加算"),
    ("fee.dayservice.note.18", "criteria_set_by", "criteria95.dayservice.19", "栄養改善加算"),
    ("fee.dayservice.service-provision", "criteria_set_by", "criteria95.dayservice.23", "サービス提供体制強化加算"),
    ("fee.dayservice.treatment-improvement", "criteria_set_by", "criteria95.dayservice.24", "介護職員等処遇改善加算"),
]

NOTICE95_LABELS = {
    "criteria95.dayservice.14-6": ("十四の六", "通所介護費"),
    "criteria95.dayservice.15": ("十五", "通所介護費"),
    "criteria95.dayservice.16": ("十六", "通所介護費"),
    "criteria95.dayservice.17": ("十七", "通所介護費"),
    "criteria95.dayservice.18-2": ("十八の二", "通所介護費"),
    "criteria95.dayservice.19": ("十九", "通所介護費"),
    "criteria95.dayservice.23": ("二十三", "通所介護費"),
    "criteria95.dayservice.24": ("二十四", "通所介護費"),
    "criteria95.shared.4": ("四", "訪問介護費における介護職員等処遇改善加算"),
}

def clean(value: str) -> str:
    return " ".join(unicodedata.normalize("NFKC", value).split())

def compact(value: str) -> str:
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
        value = clean(data)
        if value:
            self.fragments.append(value)

def decode(payload: bytes, charset: str | None) -> str:
    for encoding in [charset, "utf-8", "cp932", "shift_jis"]:
        if not encoding:
            continue
        try:
            return payload.decode(encoding)
        except (UnicodeDecodeError, LookupError):
            pass
    return payload.decode("utf-8", errors="replace")

def fetch(url: str) -> tuple[bytes, list[str]]:
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "kaigo-rules-independent-remuneration-relation-verifier/1.0 (+https://github.com/Josh-Temple/kaigo-rules)"},
    )
    with urllib.request.urlopen(req, timeout=90) as response:
        payload = response.read()
        charset = response.headers.get_content_charset()
    parser = VisibleTextParser()
    parser.feed(decode(payload, charset))
    parser.close()
    return payload, parser.fragments

def load(name: str):
    return json.loads((DATA / name).read_text(encoding="utf-8"))

def locate(lines: list[str], prefix: str, start: int = 0) -> int:
    needle = compact(prefix)
    for i in range(start, len(lines)):
        if compact(lines[i]).startswith(needle):
            return i
    raise RuntimeError(f"prefix not found: {prefix}")

TOP = re.compile(r"^([一二三四五六七八九十百]+(?:の[一二三四五六七八九十百]+)?)\s+(.+)$")

def next_top(lines: list[str], start: int) -> int:
    for i in range(start + 1, len(lines)):
        if TOP.match(clean(lines[i])):
            return i
    return len(lines)

def extract_notice19(lines: list[str]) -> dict[str, str]:
    start = locate(lines, "6 通所介護費")
    end = locate(lines, "7 通所リハビリテーション費", start + 1)
    section = lines[start:end]

    boundaries: list[tuple[str, int]] = []
    # Notes 1-24.
    cursor = 0
    for n in range(1, 25):
        pat = re.compile(rf"^{n}\s+")
        found = None
        for i in range(cursor, len(section)):
            if pat.match(clean(section[i])):
                found = i
                break
        if found is None:
            raise RuntimeError(f"Notice 19 note {n} not found")
        boundaries.append((f"fee.dayservice.note.{n}", found))
        cursor = found + 1

    for node_id, marker in [
        ("fee.dayservice.service-provision", "ニ サービス提供体制強化加算"),
        ("fee.dayservice.treatment-improvement", "ホ 介護職員等処遇改善加算"),
    ]:
        idx = locate(section, marker)
        boundaries.append((node_id, idx))

    boundaries.sort(key=lambda x: x[1])
    result: dict[str, str] = {}
    for pos, (node_id, idx) in enumerate(boundaries):
        nxt = boundaries[pos + 1][1] if pos + 1 < len(boundaries) else len(section)
        result[node_id] = "\n".join(section[idx:nxt]).strip()
    return result

def extract_notice27(lines: list[str]) -> dict[str, str]:
    start = locate(lines, "一 厚生労働大臣が定める利用者の数の基準")
    end = next_top(lines, start)
    section = lines[start:end]
    i_idx = locate(section, "イ 指定通所介護")
    ro_idx = locate(section, "ロ 指定通所介護事業所", i_idx + 1)
    return {
        "calc27.dayservice.1.capacity": "\n".join(section[i_idx:ro_idx]).strip(),
        "calc27.dayservice.1.staffing": "\n".join(section[ro_idx:]).strip(),
    }

def extract_notice95(lines: list[str]) -> dict[str, str]:
    out: dict[str, str] = {}
    for node_id, (label, required) in NOTICE95_LABELS.items():
        found = None
        for i, line in enumerate(lines):
            m = TOP.match(clean(line))
            if m and m.group(1) == label and required in m.group(2):
                found = i
                break
        if found is None:
            raise RuntimeError(f"Notice 95 heading not found: {node_id}")
        out[node_id] = "\n".join(lines[found:next_top(lines, found)]).strip()
    return out

def relation_exists(rows: list[dict], from_id: str, relation: str, to_id: str) -> bool:
    return sum(
        1 for row in rows
        if row.get("from_id") == from_id
        and row.get("relation") == relation
        and row.get("to_id") == to_id
    ) == 1

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report")
    args = parser.parse_args()

    checks: list[dict] = []
    errors: list[dict] = []
    try:
        p19, lines19 = fetch(NOTICE19_URL)
        p27, lines27 = fetch(NOTICE27_URL)
        p95, lines95 = fetch(NOTICE95_URL)
        n19 = extract_notice19(lines19)
        n27 = extract_notice27(lines27)
        n95 = extract_notice95(lines95)
        relations = load("remuneration-delegated-relations.json")

        # Notice 19 note 1 -> Notice 27 capacity/staffing lanes.
        note1 = n19["fee.dayservice.note.1"]
        note1_required = [
            "利用者の数又は看護職員若しくは介護職員の員数",
            "別に厚生労働大臣が定めるところにより算定する",
        ]
        for target_id, target_required in [
            ("calc27.dayservice.1.capacity", ["利用者の数", "通所介護費については"]),
            ("calc27.dayservice.1.staffing", ["看護職員", "介護職員", "通所介護費については"]),
        ]:
            diffs = []
            if not all(x in compact(note1) for x in map(compact, note1_required)):
                diffs.append("notice19_delegation_phrase_missing")
            target_text = n27[target_id]
            if not all(compact(x) in compact(target_text) for x in target_required):
                diffs.append("notice27_target_evidence_missing")
            if not relation_exists(relations, "fee.dayservice.note.1", "calculation_controlled_by", target_id):
                diffs.append("committed_relation_missing_or_duplicate")
            checks.append({
                "id": f"note1-to-{target_id}",
                "from_id": "fee.dayservice.note.1",
                "relation": "calculation_controlled_by",
                "to_id": target_id,
                "result": "PASS" if not diffs else "FAIL",
                "differences": diffs,
                "source_evidence": {
                    "notice19_phrase": note1_required,
                    "notice27_required": target_required,
                },
            })

        # Notice 19 named add-on -> matching Notice 95 named criteria.
        for from_id, relation, to_id, title in TITLE_CHECKS:
            source_text = n19[from_id]
            target_text = n95[to_id]
            diffs = []
            if compact(title) not in compact(source_text):
                diffs.append("notice19_named_addon_missing")
            if compact(title) not in compact(target_text.split("\n", 1)[0]):
                diffs.append("notice95_named_criteria_heading_missing")
            if "別に厚生労働大臣" not in source_text:
                diffs.append("notice19_delegation_wording_missing")
            if not relation_exists(relations, from_id, relation, to_id):
                diffs.append("committed_relation_missing_or_duplicate")
            checks.append({
                "id": f"{from_id}-to-{to_id}",
                "from_id": from_id,
                "relation": relation,
                "to_id": to_id,
                "title_key": title,
                "result": "PASS" if not diffs else "FAIL",
                "differences": diffs,
            })

        # Notice 95 no.24 explicitly incorporates no.4.
        text24 = n95["criteria95.dayservice.24"]
        shared4 = n95["criteria95.shared.4"]
        diffs = []
        if "第四号の規定を準用する" not in compact(text24):
            diffs.append("explicit_incorporation_phrase_missing")
        if "訪問介護費における介護職員等処遇改善加算の基準" not in shared4:
            diffs.append("shared_no4_heading_missing")
        if not relation_exists(relations, "criteria95.dayservice.24", "incorporates_by_reference", "criteria95.shared.4"):
            diffs.append("committed_relation_missing_or_duplicate")
        checks.append({
            "id": "criteria95-dayservice24-incorporates-shared4",
            "from_id": "criteria95.dayservice.24",
            "relation": "incorporates_by_reference",
            "to_id": "criteria95.shared.4",
            "result": "PASS" if not diffs else "FAIL",
            "differences": diffs,
        })

        source_hashes = {
            "notice19": hashlib.sha256(p19).hexdigest(),
            "notice27": hashlib.sha256(p27).hexdigest(),
            "notice95": hashlib.sha256(p95).hexdigest(),
        }
    except Exception as exc:
        errors.append({"scope": "remuneration-delegated-relations", "error": str(exc)})
        source_hashes = {}

    passed = sum(1 for row in checks if row.get("result") == "PASS")
    result = "PASS" if not errors and len(checks) == 11 and passed == 11 else "FAIL"
    report = {
        "format_version": 1,
        "verification_kind": "INDEPENDENT_REMUNERATION_DELEGATION_RELATION_AUDIT",
        "parser": "python_stdlib_htmlparser_plus_explicit_title_and_reference_rules",
        "result": result,
        "sources": {
            "notice19": {"url": NOTICE19_URL, "sha256": source_hashes.get("notice19")},
            "notice27": {"url": NOTICE27_URL, "sha256": source_hashes.get("notice27")},
            "notice95": {"url": NOTICE95_URL, "sha256": source_hashes.get("notice95")},
        },
        "checks": checks,
        "errors": errors,
        "coverage": {
            "relations_in_this_lane": 11,
            "relations_passed": passed,
            "previous_explicit_relations_independently_verified": 45,
            "aggregate_explicit_relations_independently_verified": 45 + passed,
            "non_contains_semantic_or_cross_layer_relations_current_inventory": 163,
            "remaining_semantic_or_cross_layer_relations_not_independently_verified": 163 - 45 - passed,
        },
        "safety": {
            "promotes_human_review": False,
            "promotes_verified_current": False,
            "promotes_other_semantic_mappings": False,
        },
    }
    rendered = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    print(rendered, end="")
    if args.report:
        Path(args.report).write_text(rendered, encoding="utf-8")
    return 0 if result == "PASS" else 1

if __name__ == "__main__":
    sys.exit(main())
