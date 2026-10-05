#!/usr/bin/env python3
"""Build fail-closed shared Remuneration Notification body assurance evidence."""
from __future__ import annotations
import argparse, hashlib, json, re, unicodedata, urllib.parse, urllib.request
from datetime import date
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

ROOT=Path(__file__).resolve().parents[1]
KNOWN_PAGE_COUNTS={"82aa0253":4,"82aa0254":1,"82aa0255":2,"82aa7862":3,"82aa7863":2,"82aa7864":1,"82aa7865":1}
PASS_EVIDENCE={"dayservice":"data/remuneration-independent-audit.json"}
BOUNDED_EVIDENCE={"dayrehab":"data/dayrehab-remuneration-independent-audit.json"}

def load(p:Path)->Any: return json.loads(p.read_text(encoding="utf-8"))
def compact(v:str)->str: return re.sub(r"\s+","",unicodedata.normalize("NFKC",v or ""))
def semsha(v:str)->str: return hashlib.sha256(compact(v).encode()).hexdigest()

class Parser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True); self.lines=[]; self.skip=0
    def handle_starttag(self,tag,attrs):
        if tag.lower() in {"script","style","rt","rp"}: self.skip+=1
    def handle_endtag(self,tag):
        if tag.lower() in {"script","style","rt","rp"} and self.skip: self.skip-=1
    def handle_data(self,data):
        if not self.skip:
            v=" ".join(unicodedata.normalize("NFKC",data).split())
            if v: self.lines.append(v)

def fetch(url:str):
    req=urllib.request.Request(url,headers={"User-Agent":"kaigo-rules-remuneration-assurance/1.0"})
    with urllib.request.urlopen(req,timeout=60) as r:
        raw=r.read(); charset=r.headers.get_content_charset()
    for enc in (charset,"utf-8","cp932","shift_jis"):
        if not enc: continue
        try: return raw,raw.decode(enc)
        except (UnicodeDecodeError,LookupError): pass
    return raw,raw.decode("utf-8",errors="replace")

def visible(html:str):
    p=Parser(); p.feed(html); p.close(); return p.lines

def doc_key(url:str)->str:
    p=urllib.parse.urlsplit(url)
    if p.netloc!="www.mhlw.go.jp" or p.path!="/web/t_doc": return url
    q=[(k,v) for k,v in urllib.parse.parse_qsl(p.query,keep_blank_values=True) if k!="pageNo"]
    return urllib.parse.urlunsplit((p.scheme,p.netloc,p.path,urllib.parse.urlencode(q),p.fragment))

def page_url(base:str,n:int)->str:
    p=urllib.parse.urlsplit(base)
    q=[(k,v) for k,v in urllib.parse.parse_qsl(p.query,keep_blank_values=True) if k!="pageNo"]+[("pageNo",str(n))]
    return urllib.parse.urlunsplit((p.scheme,p.netloc,p.path,urllib.parse.urlencode(q),p.fragment))

def fetch_doc(url:str,cache:dict)->dict:
    key=doc_key(url)
    if key in cache: return cache[key]
    p=urllib.parse.urlsplit(key); pages=[]
    if p.netloc=="www.mhlw.go.jp" and p.path=="/web/t_doc":
        u=page_url(key,1); raw,html=fetch(u); ls=visible(html)
        data_id=dict(urllib.parse.parse_qsl(p.query)).get("dataId")
        m=re.search(r"(\d+)\s*ページ中\s*\d+\s*ページ"," ".join(ls))
        total=KNOWN_PAGE_COUNTS.get(data_id,int(m.group(1)) if m else 1)
        pages.append((u,hashlib.sha256(raw).hexdigest(),ls))
        for n in range(2,total+1):
            u=page_url(key,n); raw,html=fetch(u); pages.append((u,hashlib.sha256(raw).hexdigest(),visible(html)))
    else:
        raw,html=fetch(url); pages.append((url,hashlib.sha256(raw).hexdigest(),visible(html)))
    lines=[line for _,_,ls in pages for line in ls]
    out={"document_key":key,"pages":[{"url":u,"sha256":h} for u,h,_ in pages],
         "document_semantic_sha256":semsha("\n".join(lines)),"lines":lines}
    cache[key]=out; return out

def find(obj:Any,key:str):
    if isinstance(obj,dict):
        if obj.get(key): return obj[key]
        for v in obj.values():
            x=find(v,key)
            if x: return x
    elif isinstance(obj,list):
        for v in obj:
            x=find(v,key)
            if x: return x
    return None

def index_path(service_id:str,config:dict,scope:dict):
    explicit=(config.get("scope_files") or {}).get("remuneration_index")
    if explicit and (ROOT/explicit).exists(): return ROOT/explicit
    nested=find(scope,"structured_index_path")
    if nested and (ROOT/str(nested)).exists(): return ROOT/str(nested)
    p=ROOT/f"data/services/{service_id}/remuneration-index.json"
    return p if p.exists() else None

def primary_url(index:dict,scope:dict):
    official=index.get("official_source") or {}
    if official.get("url"): return official["url"]
    for row in index.get("canonical_sources") or []:
        if row.get("role")!="AMENDMENT_COMPARISON_ONLY" and str(row.get("url","")).startswith("https://www.mhlw.go.jp/"): return row["url"]
    for key in ("official_current_text_url","official_url"):
        u=find(scope,key)
        if isinstance(u,str) and u.startswith("https://www.mhlw.go.jp/"): return u
    return None

def identity(index:dict,scope:dict):
    official=index.get("official_source") or ((index.get("canonical_sources") or [{}])[0])
    return {"source_id":official.get("source_id") or official.get("id") or find(scope,"source_id"),
            "notice_number":official.get("notice_number") or find(scope,"notice_number") or find(scope,"notification_number"),
            "title":official.get("title") or find(scope,"title")}

def boundary(v):
    if not v or str(v).startswith("END_OF_") or "末尾" in str(v): return None
    return re.sub(r"\s*(?:の直前|直前)$","",str(v)).strip()

def locate(lines,start_marker,end_marker):
    key=compact(start_marker); starts=[i for i,x in enumerate(lines) if compact(x).startswith(key)]
    if not starts: raise RuntimeError(f"start marker not found: {start_marker}")
    start=starts[-1]; end=len(lines)
    if end_marker:
        ek=compact(end_marker)
        for i in range(start+1,len(lines)):
            if compact(lines[i]).startswith(ek): end=i; break
        else: raise RuntimeError(f"end marker not found: {end_marker}")
    if end<=start+1: raise RuntimeError("degenerate section")
    return start,end

def safety():
    return {"promotes_currentness":False,"promotes_human_review":False,"promotes_publication":False,"promotes_route":False}

def build(observed_date:str):
    manifest=load(ROOT/"data/services/manifest.json"); cache={}; docs={}; sections=[]; projections=[]
    for service in manifest.get("services",[]):
        sid=service["service_id"]; config=load(ROOT/service["config"])
        ingestion=(config.get("ingestion_layers") or {}).get("remuneration") or {}
        if "NOT_APPLICABLE" in str(ingestion.get("status","")).upper():
            projections.append({"service_id":sid,"projection_state":"NOT_APPLICABLE","applicability_state":"NOT_APPLICABLE_EXISTING_CANONICAL_STATE",
                                "reason_codes":["EXISTING_NOT_APPLICABLE_PRESERVED"],"projection_applied_to_coverage_matrix":False,"safety":safety()}); continue
        if sid=="dayservice":
            audit=load(ROOT/PASS_EVIDENCE[sid]); meta=load(ROOT/"data/remuneration-current-text-meta.json")
            ok=audit.get("audit_result")=="PASS" and meta.get("record_count")==29
            inv={k:ok for k in ["official_primary_source_identity_fixed","source_version_identified","snapshot_hash_locator_reproducible",
                                "canonical_body_matches_official_body","service_scope_explicit","applicability_explicit",
                                "all_referenced_nodes_verified","not_historical_or_superseded_pin","omitted_text_not_treated_as_body_match"]}
            inv["other_assurance_axes_not_promoted"]=True
            projections.append({"service_id":sid,"projection_state":"PASS" if ok else "NOT_ESTABLISHED",
                "applicability_state":"APPLIES_PRIMARY_SOURCE_SECTION","verified_node_count":meta.get("record_count",0),
                "evidence":[PASS_EVIDENCE[sid],"data/remuneration-current-text.json","data/remuneration-current-text-meta.json"],
                "invariants":inv,"projection_applied_to_coverage_matrix":True,"safety":safety()}); continue
        sf=config.get("scope_files") or {}; sp=sf.get("remuneration") or sf.get("remuneration_index")
        scope=load(ROOT/sp) if sp and (ROOT/sp).exists() else {}; ip=index_path(sid,config,scope)
        if not ip:
            projections.append({"service_id":sid,"projection_state":"NOT_ESTABLISHED","applicability_state":"NOT_ESTABLISHED",
                                "reason_codes":["REMUNERATION_INDEX_NOT_FOUND"],"projection_applied_to_coverage_matrix":True,"safety":safety()}); continue
        idx=load(ip); ss=idx.get("service_scope") or {}; start=ss.get("start_marker"); end=ss.get("excluded_next_section") or boundary(ss.get("end_marker")); url=primary_url(idx,scope)
        if not start or not url:
            projections.append({"service_id":sid,"projection_state":"NOT_ESTABLISHED","applicability_state":"NOT_ESTABLISHED",
                "index_path":str(ip.relative_to(ROOT)),"reason_codes":["SOURCE_BOUNDARY_OR_URL_NOT_ESTABLISHED"],
                "projection_applied_to_coverage_matrix":True,"safety":safety()}); continue
        ident=identity(idx,scope); doc=fetch_doc(url,cache); did=ident.get("source_id") or doc["document_key"]
        docs.setdefault(doc["document_key"],{"source_id":ident.get("source_id"),"notice_number":ident.get("notice_number"),"title":ident.get("title"),
                   "document_key":doc["document_key"],"pages":doc["pages"],"document_semantic_sha256":doc["document_semantic_sha256"],
                   "snapshot_version":f"MHLW_CONSOLIDATED_DISPLAY_OBSERVED_{observed_date}","currentness_claimed":False})
        try:
            a,b=locate(doc["lines"],start,end); body="\n".join(doc["lines"][a:b]).strip()
            if len(compact(body))<20: raise RuntimeError("section body too short")
            ids=[r["id"] for key in ("top_level_items","child_items","items") for r in (idx.get(key) or []) if isinstance(r,dict) and r.get("id")]
            secid=f"remuneration-notification.{sid}"
            sections.append({"section_id":secid,"service_id":sid,"source_id":ident.get("source_id"),"notice_number":ident.get("notice_number"),
                "source_document_key":doc["document_key"],"source_snapshot_version":f"MHLW_CONSOLIDATED_DISPLAY_OBSERVED_{observed_date}",
                "source_locator":ss.get("source_section") or start,"start_marker":start,"end_marker":end,
                "section_semantic_sha256":semsha(body),"section_compact_chars":len(compact(body)),"indexed_node_count":len(ids),
                "index_path":str(ip.relative_to(ROOT)),"body_storage_policy":"HASH_ONLY_NO_FULL_TEXT_DUPLICATION",
                "source_level_result":"PRIMARY_SOURCE_SECTION_BODY_FINGERPRINT_PINNED","currentness_claimed":False})
            reasons=["CANONICAL_FULL_ITEM_BODY_NOT_PRESENT_FOR_DIRECT_COMPARISON"]
            if sid in BOUNDED_EVIDENCE: reasons.append("EXISTING_AUDIT_IS_BOUNDED_STRUCTURE_AND_VALUES_ONLY")
            projections.append({"service_id":sid,"projection_state":"PARTIAL","applicability_state":"APPLIES_PRIMARY_SOURCE_SECTION_LOCATED",
                "source_fingerprint_section_id":secid,"index_path":str(ip.relative_to(ROOT)),"indexed_node_count":len(ids),
                "evidence":["data/shared/remuneration-notification/body-fingerprints.json",str(ip.relative_to(ROOT))]+([BOUNDED_EVIDENCE[sid]] if sid in BOUNDED_EVIDENCE else []),
                "reason_codes":reasons,"invariants":{"official_primary_source_identity_fixed":bool(ident.get("notice_number") or ident.get("source_id")),
                    "source_version_identified":True,"snapshot_hash_locator_reproducible":True,"canonical_body_matches_official_body":False,
                    "service_scope_explicit":True,"applicability_explicit":True,"all_referenced_nodes_verified":False,
                    "not_historical_or_superseded_pin":True,"omitted_text_not_treated_as_body_match":True,"other_assurance_axes_not_promoted":True},
                "projection_applied_to_coverage_matrix":True,"safety":safety()})
        except Exception as exc:
            projections.append({"service_id":sid,"projection_state":"NOT_ESTABLISHED","applicability_state":"NOT_ESTABLISHED",
                "index_path":str(ip.relative_to(ROOT)),"reason_codes":["PRIMARY_SOURCE_SECTION_FINGERPRINT_FAILED"],"failure_detail":str(exc),
                "projection_applied_to_coverage_matrix":True,"safety":safety()})
    fingerprints={"format_version":1,"family":"remuneration_notification","generated_by":"scripts/build_remuneration_notification_assurance.py",
        "observed_date":observed_date,"body_storage_policy":"HASH_ONLY_NO_FULL_TEXT_DUPLICATION",
        "policy":{"section_fingerprint_is_not_service_pass":True,"fingerprint_does_not_establish_currentness":True,
                  "fingerprint_does_not_establish_human_review":True,"fingerprint_does_not_establish_publication_or_route":True},
        "source_documents":sorted(docs.values(),key=lambda x:str(x.get("document_key"))),"service_sections":sorted(sections,key=lambda x:x["service_id"])}
    projection={"format_version":1,"family":"remuneration_notification","generated_by":"scripts/build_remuneration_notification_assurance.py",
        "observed_date":observed_date,"projection_invariant":["official_primary_source_identity_fixed","source_version_identified",
        "snapshot_hash_locator_reproducible","canonical_body_matches_official_body","service_scope_explicit","applicability_explicit",
        "all_referenced_nodes_verified","not_historical_or_superseded_pin","omitted_text_not_treated_as_body_match","other_assurance_axes_not_promoted"],
        "services":sorted(projections,key=lambda x:x["service_id"])}
    return fingerprints,projection

def main():
    p=argparse.ArgumentParser(); p.add_argument("--observed-date",default=date.today().isoformat()); p.add_argument("--output-dir",default="data/shared/remuneration-notification"); a=p.parse_args()
    fp,pr=build(a.observed_date); out=Path(a.output_dir); out=out if out.is_absolute() else ROOT/out; out.mkdir(parents=True,exist_ok=True)
    (out/"body-fingerprints.json").write_text(json.dumps(fp,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    (out/"service-item-body-assurance.json").write_text(json.dumps(pr,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    counts={}
    for row in pr["services"]: counts[row["projection_state"]]=counts.get(row["projection_state"],0)+1
    print(json.dumps({"result":"OK","projection_counts":counts,"section_fingerprints":len(fp["service_sections"])},ensure_ascii=False))
    return 0
if __name__=="__main__": raise SystemExit(main())
