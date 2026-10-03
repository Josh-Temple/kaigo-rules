#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
from typing import Any
ROOT=Path(__file__).resolve().parents[1]
TARGETS={
 "preventive-dementia-dayservice":{"paragraph":"13","chapter":"第二章 介護予防認知症対応型通所介護","via":None,"inc":[]},
 "preventive-small-scale-multifunctional":{"paragraph":"14","chapter":"第三章 介護予防小規模多機能型居宅介護","via":"64","inc":["11","12","13","14","15","21","23","24","26","28","28-2","31","32","33","34","35","36","37","37-2","38","39"]},
 "preventive-dementia-group-home":{"paragraph":"15","chapter":"第四章 介護予防認知症対応型共同生活介護","via":"85","inc":["11","12","14","15","23","24","26","28-2","31","32","33","34","36","37","37-2","38","39","56","58-2","60","62-2"]},
}
REQUIRED={"care_insurance_act","standards_index","remuneration","delegated_remuneration_criteria","unit_price"}
BODY_KEYS={"official_text","source_text","article_text","body","content"}
PROMOTED={"PASS","VERIFIED","ESTABLISHED","HUMAN_REVIEWED","PUBLISHED"}
def load(p:Path)->Any:return json.loads(p.read_text(encoding="utf-8"))
def walk(v):
 if isinstance(v,dict):
  yield v
  for x in v.values():yield from walk(x)
 elif isinstance(v,list):
  for x in v:yield from walk(x)
def refs(v,prefix):
 out=[]
 if isinstance(v,dict):
  for k,x in v.items():
   if k.endswith("_node_id") and isinstance(x,str) and x.startswith(prefix):out.append(x)
   elif k.endswith("_node_ids") and isinstance(x,list):out.extend(y for y in x if isinstance(y,str) and y.startswith(prefix))
   out.extend(refs(x,prefix))
 elif isinstance(v,list):
  for x in v:out.extend(refs(x,prefix))
 return out
def validation_errors(root:Path=ROOT):
 errors=[]
 sn=load(root/"data/shared/standards/preventive-community-based-standards/nodes.json"); sids={x["id"] for x in sn}
 cr=load(root/"data/care-insurance-act-relations.json"); cids={v for x in cr for v in (x.get("from"),x.get("to")) if v}
 for sid,e in TARGETS.items():
  cfg=load(root/f"data/services/{sid}.json"); scopes=cfg.get("scope_files") or {}
  if cfg.get("service_id")!=sid:errors.append(f"{sid}: service_id drift")
  if REQUIRED-set(scopes):errors.append(f"{sid}: missing scope keys {sorted(REQUIRED-set(scopes))}")
  for k in REQUIRED:
   if k in scopes and not (root/scopes[k]).exists():errors.append(f"{sid}: missing scope file {k}")
  if (cfg.get("routing") or {}).get("future_service_base_enabled") is not False:errors.append(f"{sid}: route enabled")
  gate=cfg.get("publication_gate") or {}
  for k in ("content_ingested","independent_verification","human_review","future_service_route_enabled"):
   if gate.get(k) is not False:errors.append(f"{sid}: publication gate promoted: {k}")
  ps=[root/f"data/services/{sid}/care-insurance-act-scope.json",root/f"data/services/{sid}/standards36-scope.json",root/f"data/services/{sid}/remuneration-scope.json",root/f"data/services/{sid}/unit-price-scope.json"]
  for p in ps:
   d=load(p)
   if d.get("service_id")!=sid:errors.append(f"{sid}: scope service mismatch {p.name}")
   if d.get("source_text_duplicated") is not False:errors.append(f"{sid}: body duplication flag {p.name}")
   if d.get("automatic_verification_promotion_allowed") is not False:errors.append(f"{sid}: auto promotion enabled {p.name}")
   if d.get("applicability_verification")!="NOT_SERVICE_VERIFIED":errors.append(f"{sid}: applicability promoted {p.name}")
   if (d.get("currentness") or {}).get("status")!="NOT_ESTABLISHED":errors.append(f"{sid}: currentness promoted {p.name}")
   for row in walk(d):
    if BODY_KEYS & set(row):errors.append(f"{sid}: shared body embedded in {p.name}")
    if any(isinstance(x,str) and x in PROMOTED for x in row.values()):errors.append(f"{sid}: unsafe promoted status in {p.name}")
  care=load(ps[0]); expected={"careact.article.8-2.p.12",f"careact.article.8-2.p.{e['paragraph']}"}
  if set(care["service_definition"]["source_node_ids"])!=expected:errors.append(f"{sid}: Care Act definition mismatch")
  for x in refs(care,"careact."):
   if x not in cids:errors.append(f"{sid}: missing Care Act node {x}")
  if care["conditional_special_provisions"][0]["scope_state"]!="APPLICABILITY_NOT_ESTABLISHED":errors.append(f"{sid}: special provision must fail closed")
  std=load(ps[1])
  chapter={x["id"] for x in sn if x.get("node_type")=="article" and (x.get("path") or [None])[0]==e["chapter"]}
  if set(std["service_chapter_direct_scope"]["source_node_ids"])!=chapter:errors.append(f"{sid}: direct standards chapter mismatch")
  if set(std["common_direct_scope"]["source_node_ids"])!={"standards36.article.1","standards36.article.2","standards36.article.3"}:errors.append(f"{sid}: common standards mismatch")
  inc=std["incorporated_scope"]
  if inc["article_numbers"]!=e["inc"]:errors.append(f"{sid}: incorporated standards mismatch")
  if e["via"] is None:
   if inc["state"]!="NONE_IDENTIFIED_IN_SERVICE_CHAPTER" or std["read_as_rules"]:errors.append(f"{sid}: unexpected incorporation")
  elif inc["via_node_id"]!=f"standards36.article.{e['via']}" or not std["read_as_rules"]:errors.append(f"{sid}: missing read-as relation")
  for x in refs(std,"standards36."):
   if x not in sids:errors.append(f"{sid}: missing standards node {x}")
  rem=load(ps[2])
  if rem["primary_notice"]["notice_number"]!="平成十八年厚生労働省告示第百二十八号":errors.append(f"{sid}: wrong remuneration notice")
  if rem["primary_notice"]["shared_corpus_relation"]["state"]!="TARGET_NOTICE_NOT_INGESTED_IN_CURRENT_SHARED_REMUNERATION_CORPUS":errors.append(f"{sid}: remuneration relation not fail-closed")
  if rem["delegated_criteria_scope"]["scope_status"]!="PARTIAL_SCOPE_DEFINED":errors.append(f"{sid}: delegated criteria incorrectly complete")
  unit=load(ps[3])
  if unit["source"]["notice_number"]!="平成二十七年厚生労働省告示第九十三号":errors.append(f"{sid}: wrong unit-price notice")
  if unit["repository_relation"]["state"]!="TARGET_SERVICE_ROWS_NOT_INGESTED":errors.append(f"{sid}: unit-price relation not fail-closed")
 return errors
def main():
 e=validation_errors()
 if e:raise SystemExit("\n".join(e))
 print(f"community preventive scope: OK ({len(TARGETS)} services; no verification promotion)")
if __name__=="__main__":main()
