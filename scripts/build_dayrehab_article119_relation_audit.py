#!/usr/bin/env python3
"""Pin a fresh Article 119 relation verification report."""
from __future__ import annotations
import argparse, hashlib, json
from datetime import date
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"data/dayrehab-article119-relation-independent-audit.json"
INPUTS=[
 "data/services/dayrehab/ordinance37-scope.json",
 "data/services/dayrehab/ordinance37-relations.generated.json",
 "data/ordinance37-nodes.json",
 "scripts/verify_dayrehab_article119_relations_independent.py",
]
def blob(p):
    b=p.read_bytes(); return hashlib.sha1(f"blob {len(b)}\0".encode("ascii")+b).hexdigest()
def main():
    p=argparse.ArgumentParser(); p.add_argument("--verification-report",type=Path,required=True); p.add_argument("--run-id",required=True); p.add_argument("--head-sha",required=True); a=p.parse_args()
    report=json.loads(a.verification_report.read_text(encoding="utf-8"))
    if report.get("result")!="PASS" or len(report.get("checks",[]))!=1 or report["coverage"].get("relations_passed")!=25:
        raise SystemExit("cannot pin non-PASS Article 119 relation audit")
    payload={
      "format_version":1,"scope":"dayrehab-current-article119-incorporation",
      "audit_kind":"INDEPENDENT_DAYREHAB_ARTICLE119_RELATION_AUDIT","audit_result":"PASS","audited_at":date.today().isoformat(),
      "audit_run":{"workflow":"Verify dayrehab Article 119 relations independently","run_id":int(a.run_id),"head_sha":a.head_sha,"parser":report["parser"],"verification_report_sha256":hashlib.sha256(a.verification_report.read_bytes()).hexdigest()},
      "checks":report["checks"],"coverage":report["coverage"],
      "input_git_blob_shas_at_audit":{x:blob(ROOT/x) for x in INPUTS},
      "conclusion":"The 25 current Article 119 incorporation targets and four read-as evidence groups matched a fresh independent parse of live e-Gov XML.",
      "limitations":["PASS covers the explicit current Article 119 target set and read-as wording only.","It does not establish human legal review or exhaustive future amendment review.","Historical Rouki 25 HTML is not used to define the current Article 119 target set."],
      "safety":{"human_verified":False,"verified_current":False,"automatic_promotion_allowed":False,"promotes_other_semantic_mappings":False}
    }
    OUT.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+"\n",encoding="utf-8"); print(f"wrote {OUT.relative_to(ROOT)}")
if __name__=="__main__": main()
