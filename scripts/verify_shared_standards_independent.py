#!/usr/bin/env python3
"""Independently reparse shared ministerial-standards corpora with minidom."""
from __future__ import annotations
import argparse, hashlib, json, sys, urllib.request
from pathlib import Path
from xml.dom import Node, minidom

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"data/shared/standards"
MANIFEST=BASE/"manifest.json"
SKIP={"TOC","SupplProvision","AmendProvision","NewProvision"}

def fetch(url):
    req=urllib.request.Request(url,headers={"User-Agent":"kaigo-rules-shared-standards-independent/1.0 (+https://github.com/Josh-Temple/kaigo-rules)"})
    with urllib.request.urlopen(req,timeout=90) as response: return response.read()
def elements(node,name=None):
    return [c for c in node.childNodes if c.nodeType==Node.ELEMENT_NODE and (name is None or c.tagName==name)]
def first_desc(node,name):
    xs=node.getElementsByTagName(name); return xs[0] if xs else None
def first_direct(node,name):
    for c in elements(node):
        if c.tagName==name:return c
    return None
def text_of(node):
    if node is None:return ""
    chunks=[]
    def walk(n):
        for c in n.childNodes:
            if c.nodeType in (Node.TEXT_NODE,Node.CDATA_SECTION_NODE): chunks.append(c.data)
            elif c.nodeType==Node.ELEMENT_NODE: walk(c)
    walk(node); return " ".join("".join(chunks).split())
def canon(v): return str(v or "").strip().replace("_","-")

def collect_items(parent,parent_id,prefix,article,paragraph,nodes,contains,chain=()):
    levels={f"Subitem{i}":f"s{i}" for i in range(1,11)}
    for child in elements(parent):
        if child.tagName=="Item": level,tag,kind="i","ItemSentence","item"
        elif child.tagName in levels: level,tag,kind=levels[child.tagName],child.tagName+"Sentence","subitem"
        else: continue
        num=canon(child.getAttribute("Num")); child_chain=tuple(chain)+((level,num),)
        nid=f"{prefix}.article.{article}.p.{paragraph}"+"".join(f".{a}.{b}" for a,b in child_chain)
        body=text_of(first_direct(child,tag)) or text_of(child)
        nodes[nid]={"id":nid,"node_type":kind,"article_num":article,"paragraph_num":paragraph,"official_text":body,"parent_id":parent_id}
        contains.add((parent_id,nid))
        collect_items(child,nid,prefix,article,paragraph,nodes,contains,child_chain)

def parse_article(article,prefix,nodes,contains):
    anum=canon(article.getAttribute("Num")); aid=f"{prefix}.article.{anum}"
    nodes[aid]={"id":aid,"node_type":"article","article_num":anum,"paragraph_num":None,"official_text":text_of(article),"parent_id":None}
    for p in elements(article,"Paragraph"):
        pnum=canon(p.getAttribute("Num")); pid=f"{aid}.p.{pnum}"
        body=text_of(first_direct(p,"ParagraphSentence"))
        nodes[pid]={"id":pid,"node_type":"paragraph","article_num":anum,"paragraph_num":pnum,"official_text":body,"parent_id":aid}
        contains.add((aid,pid)); collect_items(p,pid,prefix,anum,pnum,nodes,contains)

def reparse(payload,prefix):
    doc=minidom.parseString(payload); law=first_desc(doc,"Law"); main=first_desc(law,"MainProvision") if law else None
    if main is None: raise RuntimeError("MainProvision not found")
    nodes={}; contains=set()
    def walk(node):
        for child in elements(node):
            if child.tagName in SKIP: continue
            if child.tagName=="Article": parse_article(child,prefix,nodes,contains); continue
            walk(child)
    walk(main); return nodes,contains

def check(entry):
    base=BASE/entry["corpus_id"]; meta=json.loads((base/"meta.json").read_text(encoding="utf-8"))
    expected=json.loads((base/"nodes.json").read_text(encoding="utf-8"))
    relations=json.loads((base/"relations.json").read_text(encoding="utf-8"))
    payload=fetch(f"https://laws.e-gov.go.jp/api/1/lawdata/{entry['law_id']}")
    observed_sha=hashlib.sha256(payload).hexdigest()
    observed,contains=reparse(payload,entry["node_prefix"])
    exp={x["id"]:x for x in expected}; exp_contains={(r["from"],r["to"]) for r in relations if r.get("relation")=="contains"}
    diffs=[]
    for nid in sorted(set(exp)-set(observed)): diffs.append({"id":nid,"difference":"missing_from_reparse"})
    for nid in sorted(set(observed)-set(exp)): diffs.append({"id":nid,"difference":"unexpected_in_reparse"})
    for nid in sorted(set(exp)&set(observed)):
        a,b=exp[nid],observed[nid]
        for field in ("node_type","article_num","paragraph_num","parent_id"):
            if a.get(field)!=b.get(field): diffs.append({"id":nid,"difference":field+"_mismatch"})
        if " ".join(str(a.get("official_text","")).split())!=b["official_text"]:
            diffs.append({"id":nid,"difference":"official_text_mismatch"})
    for pair in sorted(exp_contains-contains): diffs.append({"from":pair[0],"to":pair[1],"difference":"missing_contains_relation"})
    for pair in sorted(contains-exp_contains): diffs.append({"from":pair[0],"to":pair[1],"difference":"unexpected_contains_relation"})
    if observed_sha!=meta.get("xml_sha256"): diffs.append({"difference":"live_xml_sha256_differs_from_meta","expected":meta.get("xml_sha256"),"observed":observed_sha})
    return {"id":entry["corpus_id"],"law_id":entry["law_id"],"observed_xml_sha256":observed_sha,"result":"PASS" if not diffs else "FAIL",
            "observed":{"nodes":len(observed),"articles":sum(x["node_type"]=="article" for x in observed.values()),"paragraphs":sum(x["node_type"]=="paragraph" for x in observed.values()),"items":sum(x["node_type"]=="item" for x in observed.values()),"subitems":sum(x["node_type"]=="subitem" for x in observed.values()),"contains_relations":len(contains)},
            "differences":diffs}

def main():
    p=argparse.ArgumentParser(); p.add_argument("--report"); a=p.parse_args()
    manifest=json.loads(MANIFEST.read_text(encoding="utf-8"))
    checks=[]; errors=[]
    for entry in manifest["corpora"]:
        if entry["corpus_id"]=="ordinance37": continue
        try: checks.append(check(entry))
        except Exception as exc: errors.append({"id":entry["corpus_id"],"error":str(exc)})
    result="PASS" if not errors and checks and all(x["result"]=="PASS" for x in checks) else "FAIL"
    report={"format_version":1,"verification_kind":"INDEPENDENT_EGOV_SHARED_STANDARDS_REPARSE","parser":"python_xml_dom_minidom","result":result,"checks":checks,"errors":errors,
            "safety":{"promotes_service_verification":False,"promotes_currentness":False,"promotes_human_review":False,"semantic_applicability_relations_audited":False}}
    rendered=json.dumps(report,ensure_ascii=False,indent=2)+"\n"; print(rendered,end="")
    if a.report: Path(a.report).write_text(rendered,encoding="utf-8")
    return 0 if result=="PASS" else 1
if __name__=="__main__": sys.exit(main())
