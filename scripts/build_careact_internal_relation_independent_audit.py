#!/usr/bin/env python3
"""Build a pinned Care Insurance Act internal relation audit from a fresh report."""
from __future__ import annotations
import argparse, hashlib, json
from datetime import date
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/"data"
OUTPUT=DATA/"careact-internal-relation-independent-audit.json"
PINNED_INPUTS=[
  "data/care-insurance-act-nodes.json",
  "data/care-insurance-act-relations.json",
  "data/relation-semantic-independent-audit.json",
  "scripts/verify_careact_internal_relations_independent.py",
]

def blob(path: Path) -> str:
    data=path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii")+data).hexdigest()

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--verification-report",type=Path,required=True)
    p.add_argument("--run-id",required=True)
    p.add_argument("--head-sha",required=True)
    a=p.parse_args()
    report=json.loads(a.verification_report.read_text(encoding="utf-8"))
    if report.get("result")!="PASS" or len(report.get("checks",[]))!=4:
        raise SystemExit("cannot pin non-PASS Care Act internal audit")
    payload={
      "format_version":1,
      "scope":"care-insurance-act-internal-relations-to-article74",
      "audit_kind":"INDEPENDENT_CAREACT_INTERNAL_RELATION_AUDIT",
      "audit_result":"PASS",
      "audited_at":date.today().isoformat(),
      "audit_run":{
        "workflow":"Verify Care Insurance Act internal relations independently",
        "run_id":int(a.run_id),
        "head_sha":a.head_sha,
        "parser":report["parser"],
        "result":"PASS",
        "verification_report_sha256":hashlib.sha256(a.verification_report.read_bytes()).hexdigest(),
      },
      "source":report["source"],
      "checks":report["checks"],
      "coverage":report["coverage"],
      "input_git_blob_shas_at_audit":{x:blob(ROOT/x) for x in PINNED_INPUTS},
      "conclusion":"Four Care Insurance Act internal relations to Article 74 matched live e-Gov source evidence and committed relation rows.",
      "limitations":[
        "PASS applies only to the four listed Care Insurance Act internal relations.",
        "This audit does not promote HUMAN_VERIFIED or VERIFIED_CURRENT.",
        "Later pinned-input changes require a refreshed audit record."
      ],
      "safety":{"human_verified":False,"verified_current":False,"automatic_promotion_allowed":False,"promotes_other_semantic_mappings":False},
    }
    OUTPUT.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(f"wrote {OUTPUT.relative_to(ROOT)}")
if __name__=="__main__": main()
