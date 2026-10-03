#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"data/shared/standards"
MANIFEST=BASE/"manifest.json"
SERVICE_MAP=BASE/"service-ordinance-map.json"
AUDIT=BASE/"independent-audit.json"

def fail(msg): raise SystemExit("shared standards validation failed: "+msg)
def load(path): return json.loads(path.read_text(encoding="utf-8"))
def blob(path):
    data=path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode()+data).hexdigest()

def main():
    manifest=load(MANIFEST); corpora=manifest.get("corpora",[])
    ids=[x.get("corpus_id") for x in corpora]; law_ids=[x.get("law_id") for x in corpora]; prefixes=[x.get("node_prefix") for x in corpora]
    if len(ids)!=len(set(ids)): fail("duplicate corpus_id")
    if len(law_ids)!=len(set(law_ids)): fail("duplicate law_id")
    if len(prefixes)!=len(set(prefixes)): fail("duplicate node_prefix")
    by_id={x["corpus_id"]:x for x in corpora}
    if "ordinance37" not in by_id: fail("ordinance37 missing")
    if by_id["ordinance37"].get("law_id")!="411M50000100037": fail("ordinance37 law_id changed")
    if manifest.get("policies",{}).get("automatic_verification_promotion_allowed") is not False: fail("automatic promotion must remain disabled")

    for entry in corpora:
        if entry["corpus_id"]=="ordinance37":
            files=[ROOT/entry["storage"][key] for key in ("meta","nodes","relations")]
        else:
            base=BASE/entry["corpus_id"]; files=[base/"meta.json",base/"nodes.json",base/"relations.json"]
        if not all(path.exists() for path in files): fail(f"{entry['corpus_id']}: generated corpus files missing")
        meta,nodes,relations=map(load,files)
        if meta.get("law_id")!=entry["law_id"]: fail(f"{entry['corpus_id']}: meta law_id mismatch")
        if meta.get("scope") not in ("FULL_MAIN_PROVISION",None) and entry["corpus_id"]!="ordinance37": fail(f"{entry['corpus_id']}: unexpected scope")
        node_ids=[row.get("id") for row in nodes]
        if len(node_ids)!=len(set(node_ids)): fail(f"{entry['corpus_id']}: duplicate node ids")
        if not nodes: fail(f"{entry['corpus_id']}: empty corpus")
        if entry["corpus_id"]!="ordinance37" and any(not str(nid).startswith(entry["node_prefix"]+".article.") for nid in node_ids): fail(f"{entry['corpus_id']}: node prefix drift")
        node_set=set(node_ids)
        for rel in relations:
            if rel.get("relation")!="contains" and entry["corpus_id"]!="ordinance37": fail(f"{entry['corpus_id']}: source relation must be contains only")
            if rel.get("relation")=="contains" and (rel.get("from") not in node_set or rel.get("to") not in node_set): fail(f"{entry['corpus_id']}: dangling containment")
        if entry["corpus_id"]!="ordinance37":
            if any("service_scope" in row or "applicable_via" in row for row in nodes): fail(f"{entry['corpus_id']}: service applicability leaked into source corpus")
            if meta.get("automatic_verification_promotion_allowed") is not False: fail(f"{entry['corpus_id']}: unsafe promotion flag")

    service_map=load(SERVICE_MAP)
    if service_map.get("automatic_verification_promotion_allowed") is not False: fail("service map promotion must remain disabled")
    seen=set()
    for rel in service_map.get("relations",[]):
        key=rel.get("service_id")
        if key in seen: fail("duplicate service mapping: "+str(key))
        seen.add(key)
        if rel.get("corpus_id") not in by_id: fail(f"unknown corpus in service map: {rel.get('corpus_id')}")
        if rel.get("verification_status")!="NOT_SERVICE_VERIFIED": fail(f"{key}: service mapping must not claim verification")

    service_manifest=load(ROOT/"data/services/manifest.json")
    expected_services={row["service_id"] for row in service_manifest.get("services",[])}
    if seen!=expected_services:
        fail(f"service mapping coverage mismatch: missing={sorted(expected_services-seen)} extra={sorted(seen-expected_services)}")

    audit=load(AUDIT)
    if audit.get("audit_result")!="PASS": fail("independent audit not PASS")
    safety=audit.get("safety",{})
    if safety.get("service_verification") is not False or safety.get("verified_current") is not False or safety.get("human_verified") is not False or safety.get("automatic_promotion_allowed") is not False:
        fail("independent audit safety boundary changed")
    audited={x.get("id") for x in audit.get("checks",[])}
    expected=set(ids)-{"ordinance37"}
    if audited!=expected: fail(f"independent audit coverage mismatch: expected {sorted(expected)} got {sorted(audited)}")
    for rel,expected_blob in audit.get("input_git_blob_shas_at_audit",{}).items():
        path=ROOT/rel
        if not path.exists() or blob(path)!=expected_blob: fail("pinned audit input changed: "+rel)
    print(f"shared standards: OK ({len(corpora)} current corpora + {len(manifest.get('historical_or_special',[]))} historical/special inventory)")
if __name__=="__main__": main()
