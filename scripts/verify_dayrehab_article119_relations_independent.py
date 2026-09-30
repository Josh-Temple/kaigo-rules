#!/usr/bin/env python3
"""Independently verify the current Article 119 incorporation target set."""
from __future__ import annotations
import argparse, hashlib, json, re, sys, time, urllib.error, urllib.request
from pathlib import Path
from xml.dom import Node, minidom

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/"data"
LAW_ID="411M50000100037"
SOURCE_URL=f"https://laws.e-gov.go.jp/api/1/lawdata/{LAW_ID}"
RELATIONS=DATA/"services/dayrehab/ordinance37-relations.generated.json"

KANJI_DIGITS={"〇":0,"零":0,"一":1,"二":2,"三":3,"四":4,"五":5,"六":6,"七":7,"八":8,"九":9}
KANJI_UNITS={"十":10,"百":100,"千":1000}
KANJI_NUMBER_CHARS="".join(KANJI_DIGITS)+"".join(KANJI_UNITS)

def fetch(url):
    req=urllib.request.Request(url,headers={"User-Agent":"kaigo-rules-dayrehab-article119-verifier/1.0 (+https://github.com/Josh-Temple/kaigo-rules)"})
    last=None
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req,timeout=90) as response: return response.read()
        except (urllib.error.HTTPError,urllib.error.URLError) as exc:
            last=exc
            if attempt==2: raise
            time.sleep(2**attempt)
    raise RuntimeError(last)

def text_of(node):
    chunks=[]
    def walk(cur):
        for child in cur.childNodes:
            if child.nodeType in (Node.TEXT_NODE,Node.CDATA_SECTION_NODE): chunks.append(child.data)
            elif child.nodeType==Node.ELEMENT_NODE: walk(child)
    walk(node)
    return " ".join("".join(chunks).split())

def canonical_num(v): return str(v or "").strip().replace("_","-")

def direct_elements(node,tag):
    return [c for c in node.childNodes if c.nodeType==Node.ELEMENT_NODE and c.tagName==tag]

def live_article119_text(payload):
    doc=minidom.parseString(payload)
    for article in doc.getElementsByTagName("Article"):
        if canonical_num(article.getAttribute("Num"))!="119": continue
        paragraphs=direct_elements(article,"Paragraph")
        if len(paragraphs)!=1: raise RuntimeError(f"Article 119 paragraph count changed: {len(paragraphs)}")
        sentences=direct_elements(paragraphs[0],"ParagraphSentence")
        if not sentences: raise RuntimeError("Article 119 paragraph sentence missing")
        return text_of(sentences[0])
    raise RuntimeError("Article 119 not found")

def kanji_to_int(value):
    if value.isdigit(): return int(value)
    total=current=0
    for ch in value:
        if ch in KANJI_DIGITS: current=KANJI_DIGITS[ch]
        elif ch in KANJI_UNITS:
            total+=(current or 1)*KANJI_UNITS[ch]; current=0
        else: raise ValueError(f"unsupported Japanese numeral: {value}")
    return total+current

def token(main,sub=None):
    value=str(kanji_to_int(main))
    if sub: value+="-"+str(kanji_to_int(sub))
    return value

def extract_targets(text):
    marker="の規定は、指定通所リハビリテーションの事業について準用する"
    if marker not in text: raise RuntimeError("Article 119 incorporation marker not found")
    clause=text.split(marker,1)[0]
    pattern=re.compile(rf"第([{KANJI_NUMBER_CHARS}]+)条(?:の([{KANJI_NUMBER_CHARS}]+))?")
    matches=list(pattern.finditer(clause)); out=[]; i=0
    while i<len(matches):
        cur=matches[i]
        if i+1<len(matches):
            nxt=matches[i+1]
            between=clause[cur.end():nxt.start()]
            after=clause[nxt.end():nxt.end()+3]
            if cur.group(2) is None and nxt.group(2) is None and "から" in between and after.startswith("まで"):
                start,end=kanji_to_int(cur.group(1)),kanji_to_int(nxt.group(1))
                if end<start: raise RuntimeError("descending Article 119 range")
                out.extend(str(n) for n in range(start,end+1)); i+=2; continue
        out.append(token(cur.group(1),cur.group(2))); i+=1
    return sorted(set(out),key=lambda x:tuple(int(p) for p in x.split("-")))

def committed_text():
    nodes=json.loads((DATA/"ordinance37-nodes.json").read_text(encoding="utf-8"))
    row=next((x for x in nodes if x.get("id")=="ordinance37.article.119.p.1"),None)
    if not row: raise RuntimeError("committed Article 119 paragraph missing")
    return " ".join(str(row.get("official_text","")).split())

def expected_targets():
    rows=json.loads(RELATIONS.read_text(encoding="utf-8"))
    vals=[
      str(x["to"]).removeprefix("ordinance37.article.")
      for x in rows
      if x.get("from")=="ordinance37.article.119" and x.get("relation")=="incorporates_by_reference"
    ]
    return sorted(set(vals),key=lambda x:tuple(int(p) for p in x.split("-"))),len(vals)

def main():
    p=argparse.ArgumentParser(); p.add_argument("--report"); a=p.parse_args()
    errors=[]; checks=[]
    try:
        payload=fetch(SOURCE_URL); source_sha=hashlib.sha256(payload).hexdigest()
        live=live_article119_text(payload); committed=committed_text()
        observed=extract_targets(live); expected,raw_count=expected_targets()
        diffs=[]
        if live!=committed:
            diffs.append({"difference":"article119_text_mismatch","live_sha256":hashlib.sha256(live.encode()).hexdigest(),"committed_sha256":hashlib.sha256(committed.encode()).hexdigest()})
        if raw_count!=len(expected):
            diffs.append({"difference":"duplicate_relation_targets","raw_count":raw_count,"unique_count":len(expected)})
        if observed!=expected:
            diffs.append({"difference":"incorporated_article_set_mismatch","observed":observed,"expected":expected,"missing_from_relations":sorted(set(observed)-set(expected)),"unexpected_relations":sorted(set(expected)-set(observed))})
        required_readings=[
          ["訪問介護員等","通所リハビリテーション従業者"],
          ["第八条第一項","第二十九条","第百十七条"],
          ["第十三条","心身の状況","心身の状況、病歴"],
          ["第百一条第三項及び第四項","通所介護従業者","通所リハビリテーション従業者"],
        ]
        missing=[[p for p in group if p not in live] for group in required_readings]
        missing=[x for x in missing if x]
        if missing: diffs.append({"difference":"read_as_evidence_missing","missing_groups":missing})
        checks=[{
          "id":"ordinance37-article119-dayrehab-incorporation",
          "source_url":SOURCE_URL,
          "source_xml_sha256":source_sha,
          "source_article_id":"ordinance37.article.119",
          "relation":"incorporates_by_reference",
          "result":"PASS" if not diffs else "FAIL",
          "observed_article_targets":observed,
          "expected_relation_targets":expected,
          "relation_count":len(expected),
          "read_as_evidence_groups":required_readings,
          "source_text_sha256":hashlib.sha256(live.encode()).hexdigest(),
          "differences":diffs
        }]
    except Exception as exc:
        errors.append({"scope":"dayrehab-article119-incorporation","error":str(exc)})
    passed=sum(1 for x in checks if x.get("result")=="PASS")
    result="PASS" if not errors and len(checks)==1 and passed==1 else "FAIL"
    report={
      "format_version":1,
      "verification_kind":"INDEPENDENT_DAYREHAB_ARTICLE119_RELATION_AUDIT",
      "parser":"python_xml_dom_minidom_plus_independent_japanese_article_reference_parser",
      "result":result,"checks":checks,"errors":errors,
      "coverage":{"relations_in_this_lane":25,"relations_passed":25 if result=="PASS" else 0},
      "safety":{"promotes_human_review":False,"promotes_verified_current":False,"promotes_other_semantic_mappings":False}
    }
    rendered=json.dumps(report,ensure_ascii=False,indent=2)+"\n"; print(rendered,end="")
    if a.report:
        path=Path(a.report); path.parent.mkdir(parents=True,exist_ok=True); path.write_text(rendered,encoding="utf-8")
    return 0 if result=="PASS" else 1
if __name__=="__main__": sys.exit(main())
