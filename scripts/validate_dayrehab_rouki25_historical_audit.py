#!/usr/bin/env python3
"""Validate pinned dayrehab Rouki 25 historical-source audit provenance."""
from __future__ import annotations
import hashlib,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; REC=ROOT/"data/dayrehab-rouki25-historical-independent-audit.json"
def fail(m): raise SystemExit("dayrehab Rouki 25 historical audit validation failed: "+m)
def load(p): return json.loads(p.read_text(encoding="utf-8"))
def blob(p):
    b=p.read_bytes(); return hashlib.sha1(f"blob {len(b)}\0".encode("ascii")+b).hexdigest()
def main():
    r=load(REC)
    if r.get("scope")!="dayrehab-rouki25-official-historical-html-section" or r.get("audit_kind")!="INDEPENDENT_DAYREHAB_ROUKI25_HISTORICAL_SOURCE_AUDIT" or r.get("audit_result")!="PASS": fail("unexpected identity/result")
    run=r.get("audit_run",{})
    if not isinstance(run.get("run_id"),int) or run["run_id"]<=0: fail("invalid run")
    if not re.fullmatch(r"[0-9a-f]{40}",str(run.get("head_sha") or "")): fail("invalid head sha")
    if not re.fullmatch(r"[0-9a-f]{64}",str(run.get("verification_report_sha256") or "")): fail("invalid report sha")
    checks=r.get("checks",[])
    if len(checks)!=9 or any(x.get("result")!="PASS" or x.get("differences")!=[] for x in checks): fail("item checks not clean")
    if r.get("coverage",{}).get("items_passed")!=9: fail("coverage changed")
    s=r.get("safety",{})
    if s.get("historical_source_only") is not True or s.get("current_integrated_text") is not False or s.get("human_verified") is not False or s.get("verified_current") is not False: fail("unsafe state")
    for rel,expected in r.get("input_git_blob_shas_at_audit",{}).items():
        p=ROOT/rel
        if not p.exists() or blob(p)!=expected: fail(f"pinned input changed: {rel}")
    print("dayrehab Rouki 25 historical audit: OK (9/9 PASS; currentness remains GAP)")
if __name__=="__main__": main()
