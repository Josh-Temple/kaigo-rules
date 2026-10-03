#!/usr/bin/env python3
"""Validate PREVENTIVE_SERVICE scope declarations without promoting state."""
from __future__ import annotations
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/"data"
FORBIDDEN_PROMOTED={"PASS","VERIFIED","HUMAN_VERIFIED","PUBLISHED","ENABLED","VERIFIED_CURRENT"}
TEXT_KEYS={"official_text","body","body_text","full_text"}
def load(path): return json.loads(path.read_text(encoding="utf-8"))
def iter_values(value):
    if isinstance(value,dict):
        for k,v in value.items():
            yield k,v
            yield from iter_values(v)
    elif isinstance(value,list):
        for child in value: yield from iter_values(child)
def validate():
    manifest=load(DATA/"services/manifest.json")
    targets=[r for r in manifest["services"] if r["service_class"]=="PREVENTIVE_SERVICE"]
    if not targets: raise AssertionError("PREVENTIVE_SERVICE set is empty")
    care_nodes={r["id"] for r in load(DATA/"care-insurance-act-nodes.json")}
    std_nodes={r["id"] for r in load(DATA/"shared/standards/preventive-services-standards/nodes.json")}
    sale_id="specific-preventive-welfare-equipment-sale"
    for row in targets:
        sid=row["service_id"]; cfg=load(ROOT/row["config"])
        expected={
          "care_insurance_act":f"data/services/{sid}/care-insurance-act-scope.json",
          "standards_index":f"data/services/{sid}/standards-scope.json",
          "remuneration":f"data/services/{sid}/remuneration-scope.json",
          "delegated_remuneration_criteria":f"data/services/{sid}/remuneration-scope.json",
          "unit_price_regional_classification":f"data/services/{sid}/remuneration-scope.json"}
        for key,path in expected.items():
            if cfg.get("scope_files",{}).get(key)!=path: raise AssertionError(f"{sid}: bad scope_files[{key}]")
        gate=cfg.get("publication_gate",{})
        if any(gate.get(k) is True for k in ("public_routes_enabled","content_ingested","independent_verification_complete","human_review_complete")):
            raise AssertionError(f"{sid}: scope wave promoted publication/readiness")
        care=load(ROOT/expected["care_insurance_act"]); std=load(ROOT/expected["standards_index"]); rem=load(ROOT/expected["remuneration"])
        for doc in (care,std,rem):
            if doc.get("service_id")!=sid: raise AssertionError(f"{sid}: service_id mismatch")
            if doc.get("automatic_verification_promotion_allowed") is not False: raise AssertionError(f"{sid}: auto promotion not false")
            for key,value in iter_values(doc):
                if key in TEXT_KEYS: raise AssertionError(f"{sid}: duplicated source text via {key}")
                if isinstance(value,str) and value in FORBIDDEN_PROMOTED: raise AssertionError(f"{sid}: promoted state {value}")
        care_refs=[care["service_definition"]["source_node_id"],care["benefit_basis"]["source_node_id"],*care["provider_governance"]["direct_node_ids"],care["provider_governance"]["coexistence_special_case"]["source_node_id"]]
        for inc in care["provider_governance"]["incorporation"]:
            care_refs.append(inc["via_node_id"]); care_refs.extend(inc["target_node_ids"])
        missing=sorted(set(care_refs)-care_nodes)
        if missing: raise AssertionError(f"{sid}: missing Care Act refs {missing}")
        std_refs=[*std["common_scope"]["source_node_ids"],std["primary_scope"]["from_node_id"],std["primary_scope"]["through_node_id"]]
        for v in std["service_variants"]: std_refs.extend([v["from_node_id"],v["through_node_id"]])
        for w in std["incorporation_wrappers"]:
            std_refs.append(w["node_id"])
            if w["target_resolution_state"]!="NOT_EXPANDED_FAIL_CLOSED": raise AssertionError(f"{sid}: wrapper not fail-closed")
            if "target_node_ids" in w: raise AssertionError(f"{sid}: unresolved wrapper invented targets")
        missing=sorted(set(std_refs)-std_nodes)
        if missing: raise AssertionError(f"{sid}: missing standards refs {missing}")
        if rem.get("source_text_duplicated") is not False: raise AssertionError(f"{sid}: remuneration text duplicated")
        if sid==sale_id:
            if rem["remuneration_notification"]["state"]!="NOT_APPLICABLE": raise AssertionError("sale remuneration must be N/A")
            if rem["unit_price_regional_classification"]["state"]!="NOT_APPLICABLE": raise AssertionError("sale unit price must be N/A")
        else:
            if rem["remuneration_notification"]["state"]!="SCOPE_DEFINED": raise AssertionError(f"{sid}: remuneration undefined")
            if rem["delegated_remuneration_criteria"]["state"]!="SCOPE_DEFINED_RELATION_NOT_NODE_RESOLVED": raise AssertionError(f"{sid}: delegated scope bad")
            if rem["unit_price_regional_classification"]["state"]!="SCOPE_DEFINED": raise AssertionError(f"{sid}: unit price undefined")
            if rem["unit_price_regional_classification"]["service_rate_nodes_state"]!="NOT_INGESTED_FOR_PREVENTIVE_SERVICE": raise AssertionError(f"{sid}: fabricated unit-price nodes")
    print(json.dumps({"service_class":"PREVENTIVE_SERVICE","services_validated":len(targets),"verification_promoted":False,"publication_promoted":False,"shared_text_duplicated":False},ensure_ascii=False))
if __name__=="__main__": validate()
