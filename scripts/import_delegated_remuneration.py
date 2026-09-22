#!/usr/bin/env python3
import hashlib
import json
import re
import unicodedata
import urllib.request
from pathlib import Path

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
NOTICE27_URL = "https://www.mhlw.go.jp/web/t_doc?dataId=82aa0261&dataType=0&pageNo=1"
NOTICE95_URL = "https://www.mhlw.go.jp/web/t_doc?dataId=82ab4584&dataType=0&pageNo=1"
OUT = DATA / "remuneration-delegated-nodes.json"
REL = DATA / "remuneration-delegated-relations.json"
META = DATA / "remuneration-delegated-meta.json"

CRITERIA95 = [
    ("criteria95.14-3", "十四の三", "高齢者虐待防止措置未実施減算", ["fee.dayservice.note.2"]),
    ("criteria95.14-4", "十四の四", "業務継続計画未策定減算", ["fee.dayservice.note.3"]),
    ("criteria95.14-5", "十四の五", "生活相談員配置等加算", ["fee.dayservice.note.8"]),
    ("criteria95.14-6", "十四の六", "入浴介助加算", ["fee.dayservice.note.10"]),
    ("criteria95.15", "十五", "中重度者ケア体制加算", ["fee.dayservice.note.11"]),
    ("criteria95.15-2", "十五の二", "生活機能向上連携加算", ["fee.dayservice.note.12"]),
    ("criteria95.16", "十六", "個別機能訓練加算", ["fee.dayservice.note.13"]),
    ("criteria95.16-2", "十六の二", "ADL維持等加算", ["fee.dayservice.note.14"]),
    ("criteria95.17", "十七", "認知症加算", ["fee.dayservice.note.15"]),
    ("criteria95.18", "十八", "若年性認知症利用者受入加算", ["fee.dayservice.note.16"]),
    ("criteria95.18-2", "十八の二", "栄養アセスメント加算", ["fee.dayservice.note.17"]),
    ("criteria95.19", "十九", "栄養改善加算", ["fee.dayservice.note.18"]),
    ("criteria95.19-2", "十九の二", "口腔・栄養スクリーニング加算", ["fee.dayservice.note.19"]),
    ("criteria95.20", "二十", "口腔機能向上加算", ["fee.dayservice.note.20"]),
    ("criteria95.23", "二十三", "サービス提供体制強化加算", ["fee.dayservice.service-provision"]),
    ("criteria95.24", "二十四", "介護職員等処遇改善加算", ["fee.dayservice.treatment-improvement"]),
]

TOP_HEADING = re.compile(r"^(?:[一二三四五六七八九十百]+(?:の[一二三四五六七八九十百]+)?|[一二三四五六七八九十百]+・[一二三四五六七八九十百]+)[　 ]")

def fetch(url):
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "kaigo-rules/1.0 (+https://github.com/Josh-Temple/kaigo-rules)"},
    )
    with urllib.request.urlopen(req, timeout=60) as response:
        payload = response.read()
        charset = response.headers.get_content_charset()
    for enc in [charset, "utf-8", "cp932", "shift_jis"]:
        if not enc:
            continue
        try:
            return payload, payload.decode(enc)
        except (UnicodeDecodeError, LookupError):
            pass
    return payload, payload.decode("utf-8", errors="replace")

def lines_from_html(html):
    soup = BeautifulSoup(html, "html.parser")
    return [" ".join(x.split()) for x in soup.stripped_strings if " ".join(x.split())]

def norm(value):
    return re.sub(r"\s+", "", unicodedata.normalize("NFKC", value)).replace("くう", "")

def locate_contains(lines, *parts, start=0):
    needles = [norm(p) for p in parts]
    for index in range(start, len(lines)):
        hay = norm(lines[index])
        if all(needle in hay for needle in needles):
            return index
    raise RuntimeError("Marker not found: " + " / ".join(parts))

def next_top(lines, start):
    for index in range(start + 1, len(lines)):
        if TOP_HEADING.match(lines[index]):
            return index
    return len(lines)

def make_record(node_id, source_id, source_url, heading, text, service_scope, related_fee_ids):
    return {
        "id": node_id,
        "source_id": source_id,
        "source_url": source_url,
        "heading": heading,
        "official_text": text,
        "text_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
        "service_scope": service_scope,
        "related_fee_ids": related_fee_ids,
        "verification_status": "IMPORTED_CURRENT_SOURCE_NEEDS_HUMAN_CHECK",
    }

def main():
    payload27, html27 = fetch(NOTICE27_URL)
    payload95, html95 = fetch(NOTICE95_URL)
    lines27 = lines_from_html(html27)
    lines95 = lines_from_html(html95)

    nodes = []
    relations = []

    section_start = locate_contains(lines27, "一", "利用者の数の基準", "通所介護費の算定方法")
    section_end = locate_contains(lines27, "二", "通所リハビリテーション費の算定方法", start=section_start + 1)
    section = lines27[section_start:section_end]
    capacity_start = locate_contains(section, "イ", "指定通所介護", "月平均", "利用者")
    staffing_start = locate_contains(section, "ロ", "指定通所介護事業所", "看護職員", "介護職員", start=capacity_start + 1)

    nodes.extend([
        make_record(
            "calc27.dayservice",
            "mhlw-fee-notice27-base",
            NOTICE27_URL,
            section[0],
            "\n".join(section).strip(),
            "通所介護",
            ["fee.dayservice.note.1"],
        ),
        make_record(
            "calc27.dayservice.capacity",
            "mhlw-fee-notice27-base",
            NOTICE27_URL,
            section[capacity_start],
            "\n".join(section[capacity_start:staffing_start]).strip(),
            "通所介護",
            ["fee.dayservice.note.1"],
        ),
        make_record(
            "calc27.dayservice.staffing",
            "mhlw-fee-notice27-base",
            NOTICE27_URL,
            section[staffing_start],
            "\n".join(section[staffing_start:]).strip(),
            "通所介護",
            ["fee.dayservice.note.1"],
        ),
    ])

    relations.extend([
        {
            "from_id": "fee.dayservice.note.1",
            "relation": "delegated_calculation_to",
            "to_id": "calc27.dayservice.capacity",
            "verification_status": "STRUCTURAL_MAPPING_NEEDS_HUMAN_CHECK",
        },
        {
            "from_id": "fee.dayservice.note.1",
            "relation": "delegated_calculation_to",
            "to_id": "calc27.dayservice.staffing",
            "verification_status": "STRUCTURAL_MAPPING_NEEDS_HUMAN_CHECK",
        },
    ])

    for node_id, number, title_fragment, fee_ids in CRITERIA95:
        pos = locate_contains(lines95, number, "通所介護費", title_fragment)
        end = next_top(lines95, pos)
        chunk = lines95[pos:end]
        text = "\n".join(chunk).strip()
        if len(text) < 20:
            raise RuntimeError("Suspiciously short criteria section: " + node_id)
        service_scope = "共生型通所介護・コア範囲外" if node_id == "criteria95.14-5" else "通所介護"
        nodes.append(
            make_record(
                node_id,
                "mhlw-fee-criteria95-current",
                NOTICE95_URL,
                chunk[0],
                text,
                service_scope,
                fee_ids,
            )
        )
        for fee_id in fee_ids:
            relations.append({
                "from_id": fee_id,
                "relation": "delegated_criteria_to",
                "to_id": node_id,
                "verification_status": "STRUCTURAL_MAPPING_NEEDS_HUMAN_CHECK",
            })

    ids = [node["id"] for node in nodes]
    if len(ids) != len(set(ids)):
        raise RuntimeError("Duplicate delegated node id")
    if len(nodes) != 19:
        raise RuntimeError("Expected 19 delegated nodes, got " + str(len(nodes)))

    meta = {
        "format_version": 1,
        "status": "GENERATED",
        "review_status": "IMPORTED_CURRENT_SOURCE_NEEDS_HUMAN_CHECK",
        "sources": {
            "notice27": {"url": NOTICE27_URL, "sha256": hashlib.sha256(payload27).hexdigest()},
            "criteria95": {"url": NOTICE95_URL, "sha256": hashlib.sha256(payload95).hexdigest()},
        },
        "counts": {
            "nodes": len(nodes),
            "notice27_nodes": 3,
            "notice95_nodes": 16,
            "relations": len(relations),
        },
        "safeguards": [
            "機械抽出だけでVERIFIED_CURRENTに昇格しない",
            "科学的介護推進体制加算など委任先告示を必要としない項目を告示95号へ誤接続しない",
            "共生型通所介護固有の生活相談員配置等加算はコア範囲外として分離する",
        ],
    }

    OUT.write_text(json.dumps(nodes, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    REL.write_text(json.dumps(relations, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    META.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(meta, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
