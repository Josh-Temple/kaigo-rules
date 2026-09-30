#!/usr/bin/env python3
"""Validate pinned provenance for the dayrehab Article 119 relation audit."""
from __future__ import annotations
import hashlib,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
REC=ROOT/"data/dayrehab-article119-relation-independent-audit.json"
REL=ROOT/"data/services/dayrehab/ordinance37-relations.generated.json"
def fail(m): raise SystemExit("dayrehab Article 119 audit validation failed: "+m)
def load(p): return json.loads(p.read_text(encoding="utf-8"))
def blob(p):
    b=p.read_bytes(); return hashlib.sha1(f"blob {len(b)}\0".encode("ascii")+b).hexdigest()
def key(v): return tuple(int(x) for x in v.split("-"))
def main():
    r=load(REC)
    if r.get("scope")!="dayrehab-current-article119-incorporation" or r.get("audit_kind")!="INDEPENDENT_DAYREHAB_ARTICLE119_RELATION_AUDIT" or r.get("audit_result")!="PASS": fail("unexpected audit identity/result")
    run=r.get("audit_run",{})
    if not isinstance(run.get("run_id"),int) or run["run_id"]<=0: fail("invalid run id")
    if not re.fullmatch(r"[0-9a-f]{40}",str(run.get("head_sha") or "")): fail("invalid head sha")
    if not re.fullmatch(r"[0-9a-f]{64}",str(run.get("verification_report_sha256") or "")): fail("invalid report sha")
    checks=r.get("checks",[])
    if len(checks)!=1: fail("expected one check")
    c=checks[0]
    if c.get("result")!="PASS" or c.get("differences")!=[] or c.get("relation_count")!=25: fail("check not clean")
    rows=load(REL)
    targets=sorted([str(x["to"]).removeprefix("ordinance37.article.") for x in rows if x.get("from")=="ordinance37.article.119" and x.get("relation")=="incorporates_by_reference"],key=key)
    if len(targets)!=25 or len(set(targets))!=25: fail("canonical relation count changed")
    if targets!=c.get("expected_relation_targets") or targets!=c.get("observed_article_targets"): fail("target set changed")
    if r.get("coverage",{}).get("relations_passed")!=25: fail("coverage changed")
    safety=r.get("safety",{})
    if safety.get("human_verified") is not False or safety.get("verified_current") is not False or safety.get("automatic_promotion_allowed") is not False: fail("unsafe promotion")
    for rel,expected in r.get("input_git_blob_shas_at_audit",{}).items():
        p=ROOT/rel
        if not p.exists() or blob(p)!=expected: fail(f"pinned input changed: {rel}")
    print("dayrehab Article 119 relation audit: OK (25/25 PASS)")
if __name__=="__main__": main()
