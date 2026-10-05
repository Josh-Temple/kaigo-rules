#!/usr/bin/env python3
"""Validate fail-closed Remuneration Notification item-body assurance."""
from __future__ import annotations
import json, re, sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
FP=ROOT/"data/shared/remuneration-notification/body-fingerprints.json"
ASSURANCE=ROOT/"data/shared/remuneration-notification/service-item-body-assurance.json"
MANIFEST=ROOT/"data/services/manifest.json"
INVARIANTS=[
 "official_primary_source_identity_fixed","source_version_identified","snapshot_hash_locator_reproducible",
 "canonical_body_matches_official_body","service_scope_explicit","applicability_explicit",
 "all_referenced_nodes_verified","not_historical_or_superseded_pin",
 "omitted_text_not_treated_as_body_match","other_assurance_axes_not_promoted",
]
FORBIDDEN_BODY_KEYS={"official_text","raw_text","body_text","legal_text"}

def load(path): return json.loads(path.read_text(encoding="utf-8"))
def walk(obj):
    if isinstance(obj,dict):
        for k,v in obj.items():
            yield k,v
            yield from walk(v)
    elif isinstance(obj,list):
        for v in obj: yield from walk(v)

def fail(msg):
    print(f"remuneration notification assurance validation failed: {msg}",file=sys.stderr); raise SystemExit(1)

def main():
    fp,assurance,manifest=load(FP),load(ASSURANCE),load(MANIFEST)
    if fp.get("family")!="remuneration_notification" or assurance.get("family")!="remuneration_notification": fail("family mismatch")
    if fp.get("body_storage_policy")!="HASH_ONLY_NO_FULL_TEXT_DUPLICATION": fail("body storage policy changed")
    for k,_ in walk(fp):
        if k in FORBIDDEN_BODY_KEYS: fail(f"full legal text key present: {k}")
    service_ids=[x["service_id"] for x in manifest.get("services",[])]
    rows=assurance.get("services",[])
    if [x["service_id"] for x in rows] != sorted(service_ids): fail("assurance service set/order differs from manifest")
    if len({x["service_id"] for x in rows})!=len(service_ids): fail("duplicate service assurance row")
    sections=fp.get("service_sections",[])
    section_by_service={x["service_id"]:x for x in sections}
    if len(section_by_service)!=len(sections): fail("duplicate service fingerprint")
    docs=fp.get("source_documents",[])
    if len({x["document_key"] for x in docs})!=len(docs): fail("duplicate source document")
    for doc in docs:
        if doc.get("currentness_claimed") is not False: fail("source fingerprint claims currentness")
        if not doc.get("pages"): fail("source document has no pinned pages")
        for page in doc["pages"]:
            if not re.fullmatch(r"[0-9a-f]{64}",str(page.get("sha256",""))): fail("invalid page SHA-256")
    configs={x["service_id"]:load(ROOT/x["config"]) for x in manifest.get("services",[])}
    expected_na={sid for sid,cfg in configs.items() if "NOT_APPLICABLE" in str(((cfg.get("ingestion_layers") or {}).get("remuneration") or {}).get("status","")).upper()}
    for row in rows:
        sid=row["service_id"]; state=row.get("projection_state")
        safety=row.get("safety") or {}
        if any(safety.get(k) is not False for k in ("promotes_currentness","promotes_human_review","promotes_publication","promotes_route")):
            fail(f"{sid}: another assurance axis would be promoted")
        if sid in expected_na:
            if state!="NOT_APPLICABLE" or row.get("projection_applied_to_coverage_matrix") is not False:
                fail(f"{sid}: existing NOT_APPLICABLE not preserved")
            continue
        if row.get("projection_applied_to_coverage_matrix") is not True: fail(f"{sid}: applicable service projection missing")
        if state=="PASS":
            inv=row.get("invariants") or {}
            if any(inv.get(k) is not True for k in INVARIANTS): fail(f"{sid}: unsupported PASS projection")
            if not row.get("evidence"): fail(f"{sid}: PASS without evidence")
        elif state=="PARTIAL":
            if sid not in section_by_service: fail(f"{sid}: PARTIAL lacks primary-source body fingerprint")
            if not row.get("reason_codes"): fail(f"{sid}: PARTIAL lacks reason code")
            if all((row.get("invariants") or {}).get(k) is True for k in INVARIANTS):
                fail(f"{sid}: PARTIAL unexpectedly satisfies every PASS invariant")
        elif state!="NOT_ESTABLISHED":
            fail(f"{sid}: unsupported projection state {state}")
    for section in sections:
        if section.get("currentness_claimed") is not False: fail(f"{section['service_id']}: section fingerprint claims currentness")
        if section.get("body_storage_policy")!="HASH_ONLY_NO_FULL_TEXT_DUPLICATION": fail(f"{section['service_id']}: body duplication policy changed")
        if not re.fullmatch(r"[0-9a-f]{64}",str(section.get("section_semantic_sha256",""))): fail(f"{section['service_id']}: invalid section hash")
    print(json.dumps({"result":"PASS","services":len(rows),"fingerprinted_sections":len(sections),
                      "projection_counts":{s:sum(r.get("projection_state")==s for r in rows) for s in ("PASS","PARTIAL","NOT_ESTABLISHED","NOT_APPLICABLE")}},ensure_ascii=False))
    return 0
if __name__=="__main__": raise SystemExit(main())
