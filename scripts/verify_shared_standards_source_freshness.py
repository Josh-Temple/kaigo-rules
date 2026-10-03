#!/usr/bin/env python3
"""Read-only freshness check for shared ministerial-standards corpora."""
from __future__ import annotations
import argparse, hashlib, json, sys, urllib.request
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"data/shared/standards"
FIELDS=["law_revision_id","law_title","amendment_law_id","amendment_law_num","amendment_promulgate_date","amendment_enforcement_date","amendment_scheduled_enforcement_date","current_revision_status","repeal_status","mission","updated"]

def fetch(url):
    req=urllib.request.Request(url,headers={"User-Agent":"kaigo-rules-shared-standards-freshness/1.0 (+https://github.com/Josh-Temple/kaigo-rules)"})
    with urllib.request.urlopen(req,timeout=90) as response:return response.read()
def revisions(payload):
    rows=payload.get("revisions") if isinstance(payload,dict) else None
    if rows is None and isinstance(payload,dict) and isinstance(payload.get("result"),dict): rows=payload["result"].get("revisions")
    return rows or []
def current(rows):
    row=next((x for x in rows if x.get("current_revision_status")=="CurrentEnforced"),rows[0] if rows else {})
    return {k:row.get(k) for k in FIELDS if k in row}
def check(entry):
    meta=json.loads((BASE/entry["corpus_id"]/"meta.json").read_text(encoding="utf-8"))
    xb=fetch(meta["source_api_v1"]); rb=fetch(meta["source_revisions_v2"])
    rows=revisions(json.loads(rb.decode("utf-8"))); diffs=[]
    observed_xml=hashlib.sha256(xb).hexdigest(); observed_rev=hashlib.sha256(rb).hexdigest(); observed_current=current(rows)
    for field,expected,observed in [
      ("xml_sha256",meta.get("xml_sha256"),observed_xml),
      ("revision_response_sha256",meta.get("revision_response_sha256"),observed_rev),
      ("revision_count",meta.get("revision_count"),len(rows)),
      ("current_revision",meta.get("current_revision"),observed_current),
    ]:
        if expected!=observed: diffs.append({"field":field,"expected":expected,"observed":observed})
    return {"id":entry["corpus_id"],"law_id":entry["law_id"],"result":"PASS" if not diffs else "SOURCE_DRIFT_DETECTED","differences":diffs}
def main():
    p=argparse.ArgumentParser();p.add_argument("--report");a=p.parse_args()
    manifest=json.loads((BASE/"manifest.json").read_text(encoding="utf-8"))
    checks=[];errors=[]
    for entry in manifest["corpora"]:
        if entry["corpus_id"]=="ordinance37":continue
        try:checks.append(check(entry))
        except Exception as exc:errors.append({"id":entry["corpus_id"],"error":str(exc)})
    result="PASS" if not errors and checks and all(x["result"]=="PASS" for x in checks) else "FAIL"
    report={"format_version":1,"verification_kind":"EGOV_SHARED_STANDARDS_SOURCE_FRESHNESS","result":result,"checks":checks,"errors":errors,
      "safety":{"read_only":True,"updates_generated_data":False,"promotes_service_verification":False,"promotes_currentness":False,"promotes_human_review":False}}
    rendered=json.dumps(report,ensure_ascii=False,indent=2)+"\n";print(rendered,end="")
    if a.report:Path(a.report).write_text(rendered,encoding="utf-8")
    return 0 if result=="PASS" else 1
if __name__=="__main__":sys.exit(main())
