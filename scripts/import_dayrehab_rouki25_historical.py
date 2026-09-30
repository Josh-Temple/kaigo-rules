#!/usr/bin/env python3
"""Import the bounded historical Rouki 25 dayrehab section from official MHLW HTML."""
from __future__ import annotations
import argparse, hashlib, json, unicodedata, urllib.request
from html.parser import HTMLParser
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SCOPE_PATH=ROOT/"data/services/dayrehab/rouki25-scope.json"
OUTPUT=ROOT/"data/services/dayrehab/rouki25-historical.generated.json"

def norm(v): return " ".join(unicodedata.normalize("NFKC",v).split())
class Visible(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True); self.fragments=[]; self.suppressed=0
    def handle_starttag(self,tag,attrs):
        if tag.lower() in {"script","style","rt","rp"}: self.suppressed+=1
    def handle_endtag(self,tag):
        if tag.lower() in {"script","style","rt","rp"} and self.suppressed: self.suppressed-=1
    def handle_data(self,data):
        if not self.suppressed:
            v=norm(data)
            if v: self.fragments.append(v)

def fetch(url):
    req=urllib.request.Request(url,headers={"User-Agent":"kaigo-rules-dayrehab-rouki25-importer/1.0 (+https://github.com/Josh-Temple/kaigo-rules)"})
    with urllib.request.urlopen(req,timeout=90) as r:
        b=r.read(); charset=r.headers.get_content_charset()
    for enc in [charset,"utf-8","cp932","shift_jis"]:
        if not enc: continue
        try: return b,b.decode(enc)
        except (UnicodeDecodeError,LookupError): pass
    return b,b.decode("utf-8",errors="replace")

def locate(lines,needle,start=0,end=None):
    n=norm(needle); end=len(lines) if end is None else end
    for i in range(start,end):
        if norm(lines[i])==n or norm(lines[i]).startswith(n): return i
    raise ValueError(f"marker not found: {needle}")

def build():
    scope=json.loads(SCOPE_PATH.read_text(encoding="utf-8"))
    raw,html=fetch(scope["source_url"])
    p=Visible(); p.feed(html); p.close(); lines=p.fragments
    start=locate(lines,scope["boundary"]["start_heading"])
    end=locate(lines,scope["boundary"]["end_before_heading"],start+1)
    section=lines[start:end]
    items=[]
    group_positions=[]
    cursor=0
    for group in scope["groups"]:
        marker=f'{group["number"]} {group["heading"]}'
        pos=locate(section,marker,cursor)
        group_positions.append((group,pos)); cursor=pos+1
    for gi,(group,gstart) in enumerate(group_positions):
        gend=group_positions[gi+1][1] if gi+1<len(group_positions) else len(section)
        marker_positions=[]; cursor=gstart+1
        for item in group["items"]:
            pos=locate(section,item["marker"],cursor,gend)
            marker_positions.append((item,pos)); cursor=pos+1
        for ii,(item,istart) in enumerate(marker_positions):
            iend=marker_positions[ii+1][1] if ii+1<len(marker_positions) else gend
            body="\n".join(section[istart:iend]).strip()
            if not body: raise ValueError(f"empty body for {item['id']}")
            items.append({
              "id":item["id"],"group_number":group["number"],"group_heading":group["heading"],
              "marker":item["marker"],"title":item["title"],"body_text":body,
              "body_sha256":hashlib.sha256(body.encode("utf-8")).hexdigest(),
              "source_locator":f'{scope["source_section"]} / {group["number"]} {group["heading"]} / {item["marker"]}',
              "source_url":scope["source_url"],"source_state":"OFFICIAL_HISTORICAL_HTML",
              "currentness_state":scope["currentness_state"],"human_review_state":scope["human_review_state"]
            })
    if len(items)!=9: raise ValueError(f"expected 9 principal items, got {len(items)}")
    return {
      "format_version":1,"generated_by":"scripts/import_dayrehab_rouki25_historical.py",
      "service_id":"dayrehab","layer":"standards_interpretation",
      "document_id":"rouki25","source_section":scope["source_section"],
      "source":{"url":scope["source_url"],"sha256":hashlib.sha256(raw).hexdigest(),"state":"OFFICIAL_HISTORICAL_HTML"},
      "boundary":scope["boundary"],"items":items,"item_count":len(items),
      "amendment_evidence":scope["amendment_evidence"],"work_control":scope["work_control"],
      "assurance":{"historical_source_text":True,"current_integrated_text":False,"human_verified":False,"verified_current":False,"automatic_promotion_allowed":False}
    }

def render(): return json.dumps(build(),ensure_ascii=False,indent=2)+"\n"
def main():
    p=argparse.ArgumentParser(); p.add_argument("--check",action="store_true"); a=p.parse_args()
    rendered=render()
    if a.check:
        if not OUTPUT.exists() or OUTPUT.read_text(encoding="utf-8")!=rendered:
            raise SystemExit("dayrehab Rouki 25 historical dataset is stale; run importer")
        print("dayrehab Rouki 25 historical dataset: current"); return
    OUTPUT.write_text(rendered,encoding="utf-8"); print(f"wrote {OUTPUT.relative_to(ROOT)}")
if __name__=="__main__": main()
