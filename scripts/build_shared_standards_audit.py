#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json
from datetime import date
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"data/shared/standards"
OUT=BASE/"independent-audit.json"

def blob(path):
    data=path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode()+data).hexdigest()

def main():
    p=argparse.ArgumentParser(); p.add_argument("--verification-report",type=Path,required=True); p.add_argument("--run-id",required=True); p.add_argument("--head-sha",required=True); a=p.parse_args()
    report=json.loads(a.verification_report.read_text(encoding="utf-8"))
    if report.get("result")!="PASS": raise SystemExit("cannot pin non-PASS shared standards verification")
    manifest=json.loads((BASE/"manifest.json").read_text(encoding="utf-8"))
    inputs=["data/shared/standards/manifest.json","scripts/verify_shared_standards_independent.py"]
    for entry in manifest["corpora"]:
        if entry["corpus_id"]=="ordinance37": continue
        for name in ("meta.json","nodes.json","relations.json"):
            inputs.append(f"data/shared/standards/{entry['corpus_id']}/{name}")
    payload={
      "format_version":1,"audit_kind":"INDEPENDENT_EGOV_SHARED_STANDARDS_REPARSE","audit_result":"PASS","audited_at":date.today().isoformat(),
      "audit_run":{"run_id":int(a.run_id),"head_sha":a.head_sha,"parser":report["parser"],"verification_report_sha256":hashlib.sha256(a.verification_report.read_bytes()).hexdigest()},
      "checks":[{"id":x["id"],"law_id":x["law_id"],"observed_xml_sha256":x["observed_xml_sha256"],"result":x["result"],"observed":x["observed"]} for x in report["checks"]],
      "input_git_blob_shas_at_audit":{rel:blob(ROOT/rel) for rel in inputs},
      "limitations":["Source text and XML containment only.","Service applicability, incorporation by reference, substitutions/read-as rules, currentness, human review and publication are not promoted."],
      "safety":{"service_verification":False,"verified_current":False,"human_verified":False,"automatic_promotion_allowed":False}
    }
    OUT.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+"\n",encoding="utf-8"); print(f"wrote {OUT.relative_to(ROOT)}")
if __name__=="__main__": main()
