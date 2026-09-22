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
REL_OUT = DATA / "remuneration-delegated-relations.json"
META_OUT = DATA / "remuneration-delegated-meta.json"

JP_DIGITS = {"一": 1, "二": 2, "三": 3, "四": 4, "五": 5, "六": 6, "七": 7, "八": 8, "九": 9}

FEE_TITLE_MAP = [
    ("入浴介助加算", "fee.dayservice.note.10"),
    ("中重度者ケア体制加算", "fee.dayservice.note.11"),
    ("生活機能向上連携加算", "fee.dayservice.note.12"),
    ("個別機能訓練加算", "fee.dayservice.note.13"),
    ("ADL維持等加算", "fee.dayservice.note.14"),
    ("認知症加算", "fee.dayservice.note.15"),
    ("若年性認知症利用者受入加算", "fee.dayservice.note.16"),
    ("栄養アセスメント加算", "fee.dayservice.note.17"),
    ("栄養改善加算", "fee.dayservice.note.18"),
    ("口腔・栄養スクリーニング加算", "fee.dayservice.note.19"),
    ("口腔機能向上加算", "fee.dayservice.note.20"),
    ("科学的介護推進体制加算", "fee.dayservice.note.21"),
    ("サービス提供体制強化加算", "fee.dayservice.service-provision"),
    ("介護職員等処遇改善加算", "fee.dayservice.treatment-improvement"),
]

def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "kaigo-rules/1.0 (+https://github.com/Josh-Temple/kaigo-rules)"})
    with urllib.request.urlopen(req, timeout=60) as response:
        payload = response.read()
        charset = response.headers.get_content_charset()
    for encoding in [charset, "utf-8", "cp932", "shift_jis"]:
        if not encoding:
            continue
        try:
            return payload, payload.decode(encoding)
        except (UnicodeDecodeError, LookupError):
            pass
    return payload, payload.decode("utf-8", errors="replace")

def clean(value):
    return " ".join(unicodedata.normalize("NFKC", str(value)).split())

def strings_from_html(html):
    soup = BeautifulSoup(html, "html.parser")
    return [clean(x) for x in soup.stripped_strings if clean(x)]

def jp_int(value):
    if value.isdigit():
        return int(value)
    total = 0
    if "百" in value:
        left, value = value.split("百", 1)
        total += (JP_DIGITS.get(left, 1) if left else 1) * 100
    if "十" in value:
        left, right = value.split("十", 1)
        total += (JP_DIGITS.get(left, 1) if left else 1) * 10
        if right:
            total += JP_DIGITS.get(right, 0)
    elif value:
        total += JP_DIGITS.get(value, 0)
    return total

def numeric_key(raw):
    parts = raw.split("の")
    nums = [str(jp_int(p)) for p in parts]
    return "-".join(nums)

def top_heading(line):
    m = re.match(r"^([一二三四五六七八九十百]+(?:の[一二三四五六七八九十百]+)?)\s+(.+)$", line)
    return m

def extract_section(lines, start_index):
    end = len(lines)
    for idx in range(start_index + 1, len(lines)):
        if top_heading(lines[idx]):
            end = idx
            break
    return lines[start_index:end]

def node(node_id, source_id, source_url, heading, body_lines, service_scope, related_fee_ids):
    text = "\n".join(body_lines).strip()
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
    lines27 = strings_from_html(html27)
    lines95 = strings_from_html(html95)

    nodes = []
    relations = []

    start27 = next((i for i, line in enumerate(lines27) if line.startswith("一 厚生労働大臣が定める利用者の数の基準")), None)
    if start27 is None:
        raise RuntimeError("Notice 27 day-service section not found")
    section27 = extract_section(lines27, start27)
    if not any(line.startswith("イ 指定通所介護") for line in section27) or not any(line.startswith("ロ 指定通所介護事業所") for line in section27):
        raise RuntimeError("Notice 27 expected イ/ロ subsections not found")

    root27 = node(
        "calc27.dayservice.1",
        "mhlw-fee-notice27-base",
        NOTICE27_URL,
        section27[0],
        section27,
        "通所介護",
        ["fee.dayservice.note.1"],
    )
    nodes.append(root27)

    idx_i = next(i for i, line in enumerate(section27) if line.startswith("イ 指定通所介護"))
    idx_ro = next(i for i, line in enumerate(section27) if line.startswith("ロ 指定通所介護事業所"))
    cap = node(
        "calc27.dayservice.1.capacity",
        "mhlw-fee-notice27-base",
        NOTICE27_URL,
        "利用定員超過時の算定",
        section27[idx_i:idx_ro],
        "通所介護",
        ["fee.dayservice.note.1"],
    )
    staff = node(
        "calc27.dayservice.1.staffing",
        "mhlw-fee-notice27-base",
        NOTICE27_URL,
        "看護職員・介護職員の人員欠如時の算定",
        section27[idx_ro:],
        "通所介護",
        ["fee.dayservice.note.1"],
    )
    nodes.extend([cap, staff])
    relations.extend([
        {"from_id": "fee.dayservice.note.1", "relation": "calculation_controlled_by", "to_id": cap["id"], "status": "IMPORTED_MAPPING_NEEDS_HUMAN_CHECK"},
        {"from_id": "fee.dayservice.note.1", "relation": "calculation_controlled_by", "to_id": staff["id"], "status": "IMPORTED_MAPPING_NEEDS_HUMAN_CHECK"},
    ])

    heading_indices = []
    for idx, line in enumerate(lines95):
        m = top_heading(line)
        if m and "通所介護費における" in m.group(2):
            heading_indices.append((idx, m.group(1), line))

    if len(heading_indices) < 3:
        raise RuntimeError(f"Only {len(heading_indices)} day-service criteria headings found in Notice 95")

    for idx, raw_num, heading in heading_indices:
        sec = extract_section(lines95, idx)
        key = numeric_key(raw_num)
        related = []
        for phrase, fee_id in FEE_TITLE_MAP:
            if phrase in heading:
                related.append(fee_id)
        record = node(
            f"criteria95.dayservice.{key}",
            "mhlw-fee-criteria95-current",
            NOTICE95_URL,
            heading,
            sec,
            "通所介護",
            related,
        )
        nodes.append(record)
        for fee_id in related:
            relations.append({
                "from_id": fee_id,
                "relation": "criteria_set_by",
                "to_id": record["id"],
                "status": "IMPORTED_MAPPING_NEEDS_HUMAN_CHECK",
            })

    start4 = next((i for i, line in enumerate(lines95) if line.startswith("四 訪問介護費における介護職員等処遇改善加算の基準")), None)
    if start4 is None:
        raise RuntimeError("Notice 95 shared treatment-improvement section 4 not found")
    sec4 = extract_section(lines95, start4)
    shared4 = node(
        "criteria95.shared.4",
        "mhlw-fee-criteria95-current",
        NOTICE95_URL,
        sec4[0],
        sec4,
        "通所介護第24号から準用される共通参照",
        ["fee.dayservice.treatment-improvement"],
    )
    nodes.append(shared4)
    criteria24 = next((n for n in nodes if n["id"] == "criteria95.dayservice.24"), None)
    if criteria24:
        relations.append({
            "from_id": criteria24["id"],
            "relation": "incorporates_by_reference",
            "to_id": shared4["id"],
            "status": "IMPORTED_MAPPING_NEEDS_HUMAN_CHECK",
        })

    ids = [n["id"] for n in nodes]
    if len(ids) != len(set(ids)):
        raise RuntimeError("Duplicate delegated criteria node IDs")

    nodes.sort(key=lambda x: x["id"])
    relations.sort(key=lambda x: (x["from_id"], x["relation"], x["to_id"]))

    meta = {
        "format_version": 1,
        "sources": {
            "notice27": {"url": NOTICE27_URL, "sha256": hashlib.sha256(payload27).hexdigest()},
            "notice95": {"url": NOTICE95_URL, "sha256": hashlib.sha256(payload95).hexdigest()},
        },
        "counts": {
            "nodes": len(nodes),
            "relations": len(relations),
            "notice27_nodes": len([n for n in nodes if n["id"].startswith("calc27.")]),
            "notice95_nodes": len([n for n in nodes if n["id"].startswith("criteria95.")]),
        },
        "review_status": "IMPORTED_CURRENT_SOURCE_NEEDS_HUMAN_CHECK",
    }

    OUT.write_text(json.dumps(nodes, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    REL_OUT.write_text(json.dumps(relations, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    META_OUT.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(meta, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
