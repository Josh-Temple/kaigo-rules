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
ASSIGNMENTS = DATA / "unit-price-region-assignments.json"
ASSIGNMENTS_META = DATA / "unit-price-region-assignments-meta.json"

REGIONS = ["一級地","二級地","三級地","四級地","五級地","六級地","七級地","その他"]
PREFECTURES = {
    "北海道","青森県","岩手県","宮城県","秋田県","山形県","福島県",
    "茨城県","栃木県","群馬県","埼玉県","千葉県","東京都","神奈川県",
    "新潟県","富山県","石川県","福井県","山梨県","長野県","岐阜県","静岡県","愛知県",
    "三重県","滋賀県","京都府","大阪府","兵庫県","奈良県","和歌山県",
    "鳥取県","島根県","岡山県","広島県","山口県","徳島県","香川県","愛媛県","高知県",
    "福岡県","佐賀県","長崎県","熊本県","大分県","宮崎県","鹿児島県","沖縄県",
}
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

def parse_assignments(htmls, rates):
    rate_id_by_region = {row["region_class"]: row["id"] for row in rates}
    assignments = []
    seen = set()
    current_region = None
    current_prefecture = None
    found_assignment_table = False
    default_rule = None

    for html in htmls:
        soup = BeautifulSoup(html, "html.parser")
        for table in soup.find_all("table"):
            header_text = clean(table.get_text(" ", strip=True))
            if "地域区分" not in header_text or "都道府県" not in header_text or "地域" not in header_text:
                continue
            found_assignment_table = True

            for row in table.find_all("tr"):
                cells = [clean(cell.get_text(" ", strip=True)) for cell in row.find_all(["th","td"])]
                cells = [cell for cell in cells if cell]
                if not cells or ("地域区分" in cells and "都道府県" in cells):
                    continue

                for cell in cells:
                    if cell in REGIONS:
                        current_region = cell
                    if cell in PREFECTURES:
                        current_prefecture = cell
                    if cell == "全ての都道府県":
                        current_prefecture = cell

                if current_region == "その他" and any("その他の地域" in cell for cell in cells):
                    default_rule = {
                        "id": "unitregion.default.other",
                        "assignment_type": "default_fallback",
                        "region_class": "その他",
                        "unit_price_id": rate_id_by_region["その他"],
                        "rule_text": "告示に明示された一級地から七級地以外の地域は「その他」とする。",
                        "source_id": SOURCE_ID,
                        "effective_reference_date": "2024-04-01",
                        "verification_status": "IMPORTED_CURRENT_SOURCE_NEEDS_HUMAN_CHECK",
                    }
                    continue

                if not current_region or current_region == "その他" or current_prefecture not in PREFECTURES:
                    continue

                locality_cell = None
                for cell in reversed(cells):
                    if cell in REGIONS or cell in PREFECTURES or cell in {"地域区分","都道府県","地域"}:
                        continue
                    locality_cell = cell
                    break
                if not locality_cell:
                    continue

                for locality in [clean(item) for item in locality_cell.split("、") if clean(item)]:
                    key = (current_prefecture, locality)
                    if key in seen:
                        continue
                    seen.add(key)
                    token = hashlib.sha1((current_prefecture + "|" + locality).encode("utf-8")).hexdigest()[:12]
                    assignments.append({
                        "id": "unitregion.explicit." + token,
                        "assignment_type": "explicit",
                        "prefecture": current_prefecture,
                        "locality": locality,
                        "region_class": current_region,
                        "unit_price_id": rate_id_by_region[current_region],
                        "source_id": SOURCE_ID,
                        "effective_reference_date": "2024-04-01",
                        "name_basis": "令和6年4月1日時点の名称・区域",
                        "verification_status": "IMPORTED_CURRENT_SOURCE_NEEDS_HUMAN_CHECK",
                    })

    if not found_assignment_table:
        raise RuntimeError("Region assignment table not found")
    if not assignments:
        raise RuntimeError("No explicit region assignments extracted")
    if default_rule is None:
        raise RuntimeError("Default 'その他' rule not found")

    explicit_regions = {row["region_class"] for row in assignments}
    missing = [region for region in REGIONS[:-1] if region not in explicit_regions]
    if missing:
        raise RuntimeError("Missing explicit assignment regions: " + ", ".join(missing))

    assignments.sort(key=lambda row: (
        REGIONS.index(row["region_class"]),
        row["prefecture"],
        row["locality"],
    ))
    return assignments, default_rule

def main():
    payloads=[]
    htmls=[]
    for page in [1,2]:
        payload,html=fetch(BASE_URL.format(page))
        payloads.append(payload)
        htmls.append(html)

    rates=parse_rates(htmls)
    assignments, default_rule = parse_assignments(htmls, rates)
    meta={
        "format_version":1,
        "source_id":SOURCE_ID,
        "source_urls":[BASE_URL.format(1),BASE_URL.format(2)],
        "source_sha256":[hashlib.sha256(p).hexdigest() for p in payloads],
        "service":"通所介護",
        "rate_count":len(rates),
        "region_assignment_status":"EXTRACTED_CURRENT_SOURCE_NEEDS_HUMAN_CHECK",
        "review_status":"IMPORTED_CURRENT_SOURCE_NEEDS_HUMAN_CHECK",
    }
    assignment_meta={
        "format_version":1,
        "source_id":SOURCE_ID,
        "source_urls":[BASE_URL.format(1),BASE_URL.format(2)],
        "source_sha256":[hashlib.sha256(p).hexdigest() for p in payloads],
        "effective_reference_date":"2024-04-01",
        "explicit_assignment_count":len(assignments),
        "default_rule_present":True,
        "default_rule":default_rule,
        "review_status":"IMPORTED_CURRENT_SOURCE_NEEDS_HUMAN_CHECK",
        "note":"告示本文は、表に明示した一級地〜七級地と、それ以外の「その他の地域」という構造。明示地域のみ個別レコード化する。",
    }
    OUT.write_text(json.dumps(rates,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    META.write_text(json.dumps(meta,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    ASSIGNMENTS.write_text(json.dumps(assignments,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    ASSIGNMENTS_META.write_text(json.dumps(assignment_meta,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({**meta, "explicit_assignment_count":len(assignments)},ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
