#!/usr/bin/env python3
"""Build a pinned remuneration delegation relation audit from a fresh report."""
from __future__ import annotations
import argparse, hashlib, json
from datetime import date
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/"data"
OUTPUT=DATA/"remuneration-delegation-relation-independent-audit.json"
PINNED_INPUTS=[
  "data/remuneration-delegated-relations.json",
  "data/cross-layer-source-chain-independent-audit.json",
  "scripts/verify_remuneration_delegation_relations.py",
]
def blob(path: Path)->str:
    data=path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii")+data).hexdigest()
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--verification-report",type=Path,required=True)
    p.add_argument("--run-id",required=True)
    p.add_argument("--head-sha",required=True)
    a=p.parse_args()
    report=json.loads(a.verification_report.read_text(encoding="utf-8"))
    if report.get("result")!="PASS" or len(report.get("checks",[]))!=11:
        raise SystemExit("cannot pin non-PASS remuneration delegation audit")
    payload={
      "format_version":1,
      "scope":"remuneration-delegation-relations-explicit-primary-source",
      "audit_kind":"INDEPENDENT_REMUNERATION_DELEGATION_RELATION_AUDIT",
      "audit_result":"PASS",
      "audited_at":date.today().isoformat(),
      "audit_run":{
        "workflow":"Verify remuneration delegation relations independently",
        "run_id":int(a.run_id),
        "head_sha":a.head_sha,
        "parser":report["parser"],
        "result":"PASS",
        "verification_report_sha256":hashlib.sha256(a.verification_report.read_bytes()).hexdigest(),
      },
      "sources":report["sources"],
      "checks":report["checks"],
      "coverage":report["coverage"],
      "input_git_blob_shas_at_audit":{x:blob(ROOT/x) for x in PINNED_INPUTS},
      "conclusion":"All 11 covered remuneration delegation/cross-reference relations matched explicit wording or named criteria in live MHLW primary-source HTML.",
      "limitations":[
        "PASS is limited to the 11 covered explicit remuneration relations.",
        "This audit does not promote HUMAN_VERIFIED or VERIFIED_CURRENT.",
        "Later pinned-input changes require a refreshed audit record."
      ],
      "safety":{"human_verified":False,"verified_current":False,"automatic_promotion_allowed":False,"promotes_other_semantic_mappings":False},
    }
    OUTPUT.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(f"wrote {OUTPUT.relative_to(ROOT)}")
if __name__=="__main__": main()
