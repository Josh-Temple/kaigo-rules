#!/usr/bin/env python3
"""Pin a dayrehab Rouki 25 historical-source audit receipt."""
from __future__ import annotations
import argparse,hashlib,json
from datetime import date
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"data/dayrehab-rouki25-historical-independent-audit.json"
INPUTS=["data/services/dayrehab/rouki25-scope.json","data/services/dayrehab/rouki25-historical.generated.json","scripts/verify_dayrehab_rouki25_historical_independent.py"]
def blob(p):
    b=p.read_bytes(); return hashlib.sha1(f"blob {len(b)}\0".encode("ascii")+b).hexdigest()
def main():
    p=argparse.ArgumentParser(); p.add_argument("--verification-report",type=Path,required=True); p.add_argument("--run-id",required=True); p.add_argument("--head-sha",required=True); a=p.parse_args()
    report=json.loads(a.verification_report.read_text(encoding="utf-8"))
    if report.get("result")!="PASS" or report.get("coverage",{}).get("items_passed")!=9: raise SystemExit("cannot pin non-PASS historical notice audit")
    payload={
      "format_version":1,"scope":"dayrehab-rouki25-official-historical-html-section",
      "audit_kind":"INDEPENDENT_DAYREHAB_ROUKI25_HISTORICAL_SOURCE_AUDIT","audit_result":"PASS","audited_at":date.today().isoformat(),
      "audit_run":{"workflow":"Verify dayrehab Rouki 25 historical source independently","run_id":int(a.run_id),"head_sha":a.head_sha,"parser":report["parser"],"verification_report_sha256":hashlib.sha256(a.verification_report.read_bytes()).hexdigest()},
      "source":report["source"],"checks":report["checks"],"coverage":report["coverage"],
      "input_git_blob_shas_at_audit":{x:blob(ROOT/x) for x in INPUTS},
      "conclusion":"All nine principal items in the bounded dayrehab Rouki 25 historical HTML section matched the official MHLW source under an independent text-extraction path.",
      "limitations":["This proves historical-source transcription, not current integrated notice text.","The R6 old/new comparison remains separate amendment evidence and omitted text is not reconstructed.","Human review and exhaustive currentness review are not complete."],
      "safety":{"historical_source_only":True,"current_integrated_text":False,"human_verified":False,"verified_current":False,"automatic_promotion_allowed":False}
    }
    OUT.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+"\n",encoding="utf-8"); print(f"wrote {OUT.relative_to(ROOT)}")
if __name__=="__main__": main()
