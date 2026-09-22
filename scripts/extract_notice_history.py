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
SOURCE_URL = "https://www.mhlw.go.jp/web/t_doc?dataId=00ta4369&dataType=1"
SOURCE_ID = "mhlw-interpretation-html"
OUT = DATA / "notice-historical-backfill.json"
META = DATA / "notice-historical-backfill-meta.json"

MARKERS = [
    ("notice.dayservice.personnel.staffing", "(1) 従業者の員数"),
    ("notice.dayservice.personnel.life-counselor", "(2) 生活相談員"),
    ("notice.dayservice.personnel.function-training", "(3) 機能訓練指導員"),
    ("notice.dayservice.personnel.manager", "(4) 管理者"),
    ("notice.dayservice.equipment", "2 設備に関する基準"),
    ("notice.dayservice.equipment.office", "(1) 事業所"),
    ("notice.dayservice.equipment.dining-training-room", "(2) 食堂及び機能訓練室"),
    ("notice.dayservice.operation", "3 運営に関する基準"),
    ("notice.dayservice.operation.fees", "(1) 利用料等の受領"),
    ("notice.dayservice.operation.policy", "(2) 指定通所介護の基本取扱方針及び具体的取扱方針"),
    ("notice.dayservice.operation.plan", "(3) 通所介護計画の作成"),
    ("notice.dayservice.operation.rules", "(4) 運営規程"),
    ("notice.dayservice.operation.staffing", "(5) 勤務体制の確保等"),
    ("notice.dayservice.operation.disaster", "(6) 非常災害対策"),
    ("notice.dayservice.operation.hygiene", "(7) 衛生管理等"),
    ("notice.dayservice.operation.incorporation", "(8) 準用"),
]
SECTION_START = "第八 通所介護に関する基準"
SECTION_END = "4 基準該当通所介護に関する基準"

def compact(value: str) -> str:
    value = unicodedata.normalize("NFKC", value)
    return re.sub(r"\s+", "", value)

def fetch(url: str):
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "kaigo-rules/1.0 (+https://github.com/Josh-Temple/kaigo-rules)"},
    )
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

def locate(lines, marker, start=0):
    needle = compact(marker)
    for index in range(start, len(lines)):
        hay = compact(lines[index])
        if hay == needle or hay.startswith(needle):
            return index
    raise RuntimeError(f"Marker not found: {marker}")

def main():
    payload, html = fetch(SOURCE_URL)
    soup = BeautifulSoup(html, "html.parser")
    lines = [" ".join(text.split()) for text in soup.stripped_strings]
    lines = [line for line in lines if line]

    section_start = locate(lines, SECTION_START)
    section_end = locate(lines, SECTION_END, section_start + 1)
    section = lines[section_start:section_end]

    found = []
    cursor = 0
    for node_id, heading in MARKERS:
        index = locate(section, heading, cursor)
        found.append((node_id, heading, index))
        cursor = index + 1

    candidates = []
    for position, (node_id, heading, index) in enumerate(found):
        next_index = found[position + 1][2] if position + 1 < len(found) else len(section)
        body_lines = section[index + 1:next_index]
        body = "\n".join(body_lines).strip()
        if not body:
            raise RuntimeError(f"Empty historical candidate: {node_id}")

        candidates.append({
            "notice_id": node_id,
            "historical_heading": section[index],
            "historical_text": body,
            "historical_text_sha256": hashlib.sha256(body.encode("utf-8")).hexdigest(),
            "source_id": SOURCE_ID,
            "source_url": SOURCE_URL,
            "source_locator": f"第八 通所介護に関する基準 / {section[index]}",
            "candidate_status": "HISTORICAL_BACKFILL_CANDIDATE",
            "requires_forward_replay": True,
            "promotion_rule": "Do not copy into current official_text until later amendment events are replayed and current wording is verified.",
        })

    out_meta = {
        "format_version": 1,
        "source_id": SOURCE_ID,
        "source_url": SOURCE_URL,
        "source_sha256": hashlib.sha256(payload).hexdigest(),
        "source_class": "historical_reference",
        "section": SECTION_START,
        "candidate_count": len(candidates),
        "candidate_status": "HISTORICAL_BACKFILL_CANDIDATE",
        "currentness_warning": "This source is historical. Extracted text is never current by extraction alone.",
    }

    OUT.write_text(json.dumps(candidates, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    META.write_text(json.dumps(out_meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(out_meta, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
