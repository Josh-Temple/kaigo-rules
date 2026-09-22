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
BASE_URL = "https://www.mhlw.go.jp/web/t_doc?dataId=82ab4582&dataType=0&pageNo={}"
SOURCE_ID = "mhlw-unit-price-current"
OUT = DATA / "unit-price-dayservice.json"
META = DATA / "unit-price-dayservice-meta.json"

REGIONS = ["一級地","二級地","三級地","四級地","五級地","六級地","七級地","その他"]
KANJI = {"〇":0,"零":0,"一":1,"二":2,"三":3,"四":4,"五":5,"六":6,"七":7,"八":8,"九":9}

def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent":"kaigo-rules/1.0 (+https://github.com/Josh-Temple/kaigo-rules)"})
    with urllib.request.urlopen(req, timeout=60) as response:
        payload=response.read()
        charset=response.headers.get_content_charset()
    for encoding in [charset,"utf-8","cp932","shift_jis"]:
        if not encoding: continue
        try:
            return payload,payload.decode(encoding)
        except (UnicodeDecodeError,LookupError):
            pass
    return payload,payload.decode("utf-8",errors="replace")

def clean(value):
    return " ".join(unicodedata.normalize("NFKC",str(value)).split())

def kanji_number(value):
    value=clean(value)
    total=0
    section=0
    digit=0
    for ch in value:
        if ch in KANJI:
            digit=KANJI[ch]
        elif ch=="十":
            section += (digit or 1)*10
            digit=0
        elif ch=="百":
            section += (digit or 1)*100
            digit=0
        elif ch=="千":
            section += (digit or 1)*1000
            digit=0
        elif ch.isdigit():
            digit = digit*10 + int(ch)
    return total+section+digit

def is_dayservice_group(text):
    reduced=text
    for phrase in ["地域密着型通所介護","認知症対応型通所介護","介護予防認知症対応型通所介護"]:
        reduced=reduced.replace(phrase,"")
    return "通所介護" in reduced

def parse_rates(htmls):
    result={}
    for html in htmls:
        soup=BeautifulSoup(html,"html.parser")
        current_region=None
        for row in soup.find_all("tr"):
            cells=[clean(cell.get_text(" ",strip=True)) for cell in row.find_all(["th","td"])]
            if not cells: continue
            for region in REGIONS:
                if region in cells:
                    current_region=region
                    break
            if not current_region: continue

            service_text=" ".join(cells[:-1]) if len(cells)>1 else ""
            ratio_text=cells[-1]
            if current_region=="その他" and "全てのサービス" in service_text and "千分の" in ratio_text:
                pass
            elif not is_dayservice_group(service_text):
                continue
            if "千分の" not in ratio_text:
                continue

            raw=ratio_text.split("千分の",1)[1]
            ratio=kanji_number(raw)
            if ratio < 900 or ratio > 1200:
                raise RuntimeError(f"Unexpected ratio {ratio_text} -> {ratio}")
            price=round(10*ratio/1000,3)
            record={
                "id":f"unitprice.dayservice.{REGIONS.index(current_region)+1 if current_region!='その他' else 'other'}",
                "region_class":current_region,
                "service":"通所介護",
                "ratio_text":ratio_text,
                "ratio_per_thousand":ratio,
                "unit_price_yen":price,
                "source_id":SOURCE_ID,
                "verification_status":"IMPORTED_CURRENT_SOURCE_NEEDS_HUMAN_CHECK",
            }
            existing=result.get(current_region)
            if existing and existing["ratio_per_thousand"]!=ratio:
                raise RuntimeError(f"Conflicting rate for {current_region}")
            result[current_region]=record

    missing=[r for r in REGIONS if r not in result]
    if missing:
        raise RuntimeError("Missing region classes: "+", ".join(missing))
    return [result[r] for r in REGIONS]

def main():
    payloads=[]
    htmls=[]
    for page in [1,2]:
        payload,html=fetch(BASE_URL.format(page))
        payloads.append(payload)
        htmls.append(html)

    rates=parse_rates(htmls)
    meta={
        "format_version":1,
        "source_id":SOURCE_ID,
        "source_urls":[BASE_URL.format(1),BASE_URL.format(2)],
        "source_sha256":[hashlib.sha256(p).hexdigest() for p in payloads],
        "service":"通所介護",
        "rate_count":len(rates),
        "region_assignment_status":"PENDING_SEPARATE_EXTRACTION",
        "review_status":"IMPORTED_CURRENT_SOURCE_NEEDS_HUMAN_CHECK",
    }
    OUT.write_text(json.dumps(rates,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    META.write_text(json.dumps(meta,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(meta,ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
