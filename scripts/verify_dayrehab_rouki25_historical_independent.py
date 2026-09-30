#!/usr/bin/env python3
"""Independently verify committed dayrehab Rouki 25 historical text against MHLW HTML."""
from __future__ import annotations
import argparse, hashlib, html as htmlmod, json, re, sys, unicodedata, urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DATASET=ROOT/"data/services/dayrehab/rouki25-historical.generated.json"
SCOPE=ROOT/"data/services/dayrehab/rouki25-scope.json"
def norm(v): return " ".join(unicodedata.normalize("NFKC",v).split())
def compact(v): return re.sub(r"\s+","",unicodedata.normalize("NFKC",v))
def fetch(url):
    req=urllib.request.Request(url,headers={"User-Agent":"kaigo-rules-dayrehab-rouki25-independent/1.0 (+https://github.com/Josh-Temple/kaigo-rules)"})
    with urllib.request.urlopen(req,timeout=90) as r:
        raw=r.read(); charset=r.headers.get_content_charset()
    for enc in [charset,"utf-8","cp932","shift_jis"]:
        if not enc: continue
        try: return raw,raw.decode(enc)
        except (UnicodeDecodeError,LookupError): pass
    return raw,raw.decode("utf-8",errors="replace")
def independent_visible_text(raw_html):
    text=re.sub(r"(?is)<(script|style|rt|rp)\b.*?</\1>"," ",raw_html)
    text=re.sub(r"(?i)<br\s*/?>|</p\s*>|</tr\s*>|</td\s*>|</div\s*>","\n",text)
    text=re.sub(r"(?s)<[^>]+>"," ",text)
    return norm(htmlmod.unescape(text))
def main():
    p=argparse.ArgumentParser(); p.add_argument("--report"); a=p.parse_args()
    scope=json.loads(SCOPE.read_text(encoding="utf-8")); data=json.loads(DATASET.read_text(encoding="utf-8"))
    errors=[]; checks=[]
    try:
        raw,decoded=fetch(scope["source_url"]); visible=independent_visible_text(decoded)
        live_hash=hashlib.sha256(raw).hexdigest()
        if data.get("source",{}).get("sha256")!=live_hash:
            errors.append({"difference":"source_hash_mismatch","committed":data.get("source",{}).get("sha256"),"live":live_hash})
        if compact(scope["boundary"]["start_heading"]) not in compact(visible) or compact(scope["boundary"]["end_before_heading"]) not in compact(visible):
            errors.append({"difference":"section_boundary_missing"})
        for item in data.get("items",[]):
            body=compact(item.get("body_text",""))
            diffs=[]
            if not body or body not in compact(visible): diffs.append("committed_item_text_not_found_in_live_html")
            if hashlib.sha256(item.get("body_text","").encode("utf-8")).hexdigest()!=item.get("body_sha256"): diffs.append("committed_body_hash_mismatch")
            checks.append({"id":item.get("id"),"result":"PASS" if not diffs else "FAIL","differences":diffs,"body_sha256":item.get("body_sha256"),"source_locator":item.get("source_locator")})
    except Exception as exc:
        errors.append({"difference":"verification_exception","error":str(exc)})
    passed=sum(1 for x in checks if x["result"]=="PASS")
    result="PASS" if not errors and len(checks)==9 and passed==9 else "FAIL"
    report={
      "format_version":1,"verification_kind":"INDEPENDENT_DAYREHAB_ROUKI25_HISTORICAL_SOURCE_AUDIT",
      "parser":"regex_html_text_extractor_independent_of_htmlparser_importer","result":result,
      "source":{"url":scope["source_url"],"sha256":data.get("source",{}).get("sha256")},
      "checks":checks,"errors":errors,"coverage":{"principal_items":9,"items_passed":passed},
      "safety":{"historical_source_only":True,"promotes_current_integrated_text":False,"promotes_human_review":False,"promotes_verified_current":False}
    }
    rendered=json.dumps(report,ensure_ascii=False,indent=2)+"\n"; print(rendered,end="")
    if a.report:
        out=Path(a.report); out.parent.mkdir(parents=True,exist_ok=True); out.write_text(rendered,encoding="utf-8")
    return 0 if result=="PASS" else 1
if __name__=="__main__": sys.exit(main())
