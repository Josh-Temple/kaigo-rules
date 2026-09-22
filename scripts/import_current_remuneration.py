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
SOURCE_URL = "https://www.mhlw.go.jp/web/t_doc?dataId=82aa0253&dataType=0"
SOURCE_ID = "mhlw-fee-notice19-base"
OUT = DATA / "remuneration-current-text.json"
META = DATA / "remuneration-current-text-meta.json"

SECTION_START = "6 通所介護費"
SECTION_END = "7 通所リハビリテーション費"

MARKERS = [
    ("fee.dayservice.standard", "イ 通常規模型通所介護費"),
    ("fee.dayservice.large1", "ロ 大規模型通所介護費(Ⅰ)"),
    ("fee.dayservice.large2", "ハ 大規模型通所介護費(Ⅱ)"),
    ("fee.dayservice.note.1", "1 イからハまでについて"),
    ("fee.dayservice.note.2", "2 別に厚生労働大臣が定める基準を満たさない場合は、高齢者虐待防止措置未実施減算"),
    ("fee.dayservice.note.3", "3 別に厚生労働大臣が定める基準を満たさない場合は、業務継続計画未策定減算"),
    ("fee.dayservice.note.4", "4 別に厚生労働大臣が定める基準に適合する利用者に対して、所要時間2時間以上3時間未満"),
    ("fee.dayservice.note.5", "5 イからハまでについて、感染症又は災害"),
    ("fee.dayservice.note.6", "6 電子情報処理組織を使用する方法により"),
    ("fee.dayservice.note.7", "7 共生型居宅サービスの事業を行い"),
    ("fee.dayservice.note.8", "8 別に厚生労働大臣が定める基準に適合しているものとして"),
    ("fee.dayservice.note.9", "9 指定通所介護事業所の従業者"),
    ("fee.dayservice.note.10", "10 別に厚生労働大臣が定める基準に適合しているものとして"),
    ("fee.dayservice.note.11", "11 別に厚生労働大臣が定める基準に適合しているものとして"),
    ("fee.dayservice.note.12", "12 別に厚生労働大臣が定める基準に適合しているものとして"),
    ("fee.dayservice.note.13", "13 別に厚生労働大臣が定める基準に適合しているものとして"),
    ("fee.dayservice.note.14", "14 別に厚生労働大臣が定める基準に適合しているものとして"),
    ("fee.dayservice.note.15", "15 別に厚生労働大臣が定める基準に適合しているものとして"),
    ("fee.dayservice.note.16", "16 別に厚生労働大臣が定める基準に適合しているものとして"),
    ("fee.dayservice.note.17", "17 次に掲げるいずれの基準にも適合しているものとして"),
    ("fee.dayservice.note.18", "18 次に掲げるいずれの基準にも適合しているものとして"),
    ("fee.dayservice.note.19", "19 別に厚生労働大臣が定める基準に適合する指定通所介護事業所"),
    ("fee.dayservice.note.20", "20 別に厚生労働大臣が定める基準に適合しているものとして"),
    ("fee.dayservice.note.21", "21 次に掲げるいずれの基準にも適合しているものとして"),
    ("fee.dayservice.note.22", "22 利用者が短期入所生活介護"),
    ("fee.dayservice.note.23", "23 指定通所介護事業所と同一建物に居住する者"),
    ("fee.dayservice.note.24", "24 利用者に対して、その居宅と指定通所介護事業所との間の送迎を行わない場合"),
    ("fee.dayservice.service-provision", "ニ サービス提供体制強化加算"),
    ("fee.dayservice.treatment-improvement", "ホ 介護職員等処遇改善加算"),
]

def compact(value):
    return re.sub(r"\s+", "", unicodedata.normalize("NFKC", value))

def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent":"kaigo-rules/1.0 (+https://github.com/Josh-Temple/kaigo-rules)"})
    with urllib.request.urlopen(req, timeout=60) as res:
        payload=res.read()
        charset=res.headers.get_content_charset()
    for enc in [charset,"utf-8","cp932","shift_jis"]:
        if not enc: continue
        try: return payload,payload.decode(enc)
        except (UnicodeDecodeError,LookupError): pass
    return payload,payload.decode("utf-8",errors="replace")

def locate(lines, marker, start=0):
    needle=compact(marker)
    for i in range(start,len(lines)):
        if compact(lines[i]).startswith(needle):
            return i
    raise RuntimeError(f"Marker not found: {marker}")

def main():
    payload,html=fetch(SOURCE_URL)
    soup=BeautifulSoup(html,"html.parser")
    lines=[" ".join(t.split()) for t in soup.stripped_strings]
    lines=[x for x in lines if x]
    start=locate(lines,SECTION_START)
    end=locate(lines,SECTION_END,start+1)
    section=lines[start:end]

    found=[]
    cursor=0
    for node_id,marker in MARKERS:
        idx=locate(section,marker,cursor)
        found.append((node_id,idx,section[idx]))
        cursor=idx+1

    records=[]
    for pos,(node_id,idx,heading) in enumerate(found):
        next_idx=found[pos+1][1] if pos+1<len(found) else len(section)
        text="\n".join(section[idx:next_idx]).strip()
        if not text:
            raise RuntimeError(f"Empty current fee text: {node_id}")
        records.append({
            "fee_id":node_id,
            "official_text":text,
            "text_sha256":hashlib.sha256(text.encode("utf-8")).hexdigest(),
            "source_id":SOURCE_ID,
            "source_url":SOURCE_URL,
            "source_locator":f"6 通所介護費 / {heading}",
            "import_status":"IMPORTED_CURRENT_SOURCE_NEEDS_HUMAN_CHECK"
        })

    meta={
        "format_version":1,
        "source_id":SOURCE_ID,
        "source_url":SOURCE_URL,
        "source_sha256":hashlib.sha256(payload).hexdigest(),
        "section":SECTION_START,
        "current_amendment":"令和8年厚生労働省告示第87号",
        "current_amendment_effective_from":"2026-06-01",
        "record_count":len(records),
        "import_status":"IMPORTED_CURRENT_SOURCE_NEEDS_HUMAN_CHECK"
    }
    OUT.write_text(json.dumps(records,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    META.write_text(json.dumps(meta,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(meta,ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
