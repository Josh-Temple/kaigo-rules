#!/usr/bin/env python3
"""Fail closed on dayrehab fee-layer scope and state separation contracts."""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def load(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

def fail(message: str):
    raise SystemExit("dayrehab fee-layer validation failed: " + message)

def main():
    rem=load("data/services/dayrehab/remuneration-index.json")
    guide=load("data/services/dayrehab/fee-guidance-index.json")
    config=load("data/services/dayrehab.json")
    catalog=load("data/services/verification-layers.json")
    manifest=load("data/services/manifest.json")
    shortstay=load("data/services/shortstay-life.json")

    if rem.get("service_id")!="dayrehab" or guide.get("service_id")!="dayrehab": fail("service scope mismatch")
    if rem.get("service_scope",{}).get("excluded_next_section")!="8 短期入所生活介護費": fail("remuneration boundary changed")
    if guide.get("service_scope",{}).get("excluded_next_section")!="9 福祉用具貸与費": fail("guidance boundary changed")
    if len(rem.get("items",[]))!=42: fail("remuneration parent count must be 42")
    tariff=[x for x in rem["items"] if x.get("kind")=="BASE_TARIFF_ROW"]
    notes=[x for x in rem["items"] if x.get("kind")=="NUMBERED_NOTE"]
    addons=[x for x in rem["items"] if x.get("kind")=="LETTERED_ADD_ON"]
    if (len(tariff),sum(len(x.get("rates",[])) for x in tariff),len(notes),len(addons))!=(14,70,24,4):
        fail("remuneration granularity contract drifted")
    if len(guide.get("items",[]))!=33: fail("guidance parent count must be 33")
    children=[c for p in guide["items"] for c in p.get("children",[])]
    if len(children)!=88 or len({c["id"] for c in children})!=88: fail("guidance child IDs must remain 88 unique source-local slots")
    if [p["slot"] for p in guide["items"]]!=[f"8-({i})" for i in range(1,34)]: fail("guidance parent sequence changed")
    if sum(1 for p in guide["items"] if p["r6_source_state"]=="OMITTED_MARKER")!=8: fail("guidance literal omission count changed")
    if rem["states"]["currentness"]!="GAP" or guide["state"]["currentness"]!="GAP": fail("currentness must remain GAP")
    if rem["states"]["human_review"]!="NOT_REVIEWED" or guide["state"]["human_review"]!="NOT_REVIEWED": fail("human review state changed")
    if rem["states"]["verified_current"] or guide["state"]["verified_current"]: fail("currentness promotion is forbidden")
    if any(p["currentness"]!="GAP" for p in rem["items"]): fail("remuneration item currentness must remain GAP")
    if any(source["role"]=="CURRENT_INTEGRATED_TEXT" for source in rem["canonical_sources"]+guide["canonical_sources"]): fail("a synthetic current source was declared")
    if rem["amendment_patches"][0]["omitted_sections"]!=["イ","ロ","ハ","ニ","ホ"]: fail("R8 omission ledger changed")
    if rem["amendment_patches"][0]["status"]!="EXPLICIT_PATCH_ONLY": fail("R8 patch must remain a separate patch")
    if guide["policy"]["combine_source_versions"] is not False or guide["policy"]["fill_literal_omissions"] is not False: fail("guidance source version policy weakened")
    if guide["policy"]["interpret_r8_omission_as_no_change"] is not False: fail("R8 omission cannot mean no change")
    if not {"remuneration-dayrehab","fee-guidance-dayrehab"}.issubset(set(config["verification_layer_ids"])): fail("service config misses layer IDs")
    ids={x["id"]:x for x in catalog["layers"]}
    for layer_id in ("remuneration-dayrehab","fee-guidance-dayrehab"):
        definition=ids.get(layer_id,{})
        if definition.get("provider")!="normalized_report" or definition.get("scope_kind")!="SERVICE_SPECIFIC": fail(f"{layer_id} is not an isolated normalized layer")
        report=load(definition["report_file"])
        if report.get("content_verification",{}).get("status")!="PASS_BOUNDED_SCOPE_ONLY": fail(f"{layer_id} verification scope overclaim")
        if report.get("currentness",{}).get("status")!="GAP": fail(f"{layer_id} currentness must remain GAP")
        if report.get("human_review",{}).get("status")!="NOT_REVIEWED": fail(f"{layer_id} human review must remain NOT_REVIEWED")
    short=next(x for x in manifest["services"] if x["service_id"]=="shortstay-life")
    if short["status"]!="PARTIAL_INGESTION" or shortstay["routing"]["future_service_base_enabled"] or shortstay["publication_gate"]["public_routes_enabled"]:
        fail("shortstay-life publication gate was changed")
    print("dayrehab fee-layer structure: PASS (42/70, 33/88; currentness GAP; human review NOT_REVIEWED)")

if __name__=="__main__": main()
