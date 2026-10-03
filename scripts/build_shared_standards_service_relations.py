#!/usr/bin/env python3
"""Generate service-to-shared-standards relations without copying legal text."""
from __future__ import annotations
import argparse, json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/"data"
BASE=DATA/"shared/standards"
OUTPUT=BASE/"service-relations.generated.json"

def load(path): return json.loads(path.read_text(encoding="utf-8"))
def article_id(num): return f"ordinance37.article.{str(num)}"\nSTANDARDS_SCOPE_KEYS=("ordinance37","standards_index","governing_standards")

def build():
    manifest=load(DATA/"services/manifest.json")
    corpus_map=load(BASE/"service-ordinance-map.json")
    ord_scope=load(DATA/"ordinance37-scope.json")
    home_scope=load(DATA/"services/homevisit/ordinance37-scope.json")
    home_index=load(DATA/"services/homevisit/ordinance37-index.generated.json")
    rehab_scope=load(DATA/"services/dayrehab/ordinance37-scope.json")
    nodes=load(DATA/"ordinance37-nodes.json")
    node_ids={row["id"] for row in nodes}
    mapped={row["service_id"]:row["corpus_id"] for row in corpus_map["relations"]}

    relations=[]
    states=[]

    def add_direct(service_id, articles, scope_source):
        for num in articles:
            nid=article_id(num)
            if nid not in node_ids: raise ValueError(f"{service_id}: direct source node missing: {nid}")
            relations.append({
              "service_id":service_id,"corpus_id":"ordinance37",
              "relation":"direct_applicability","source_node_id":nid,
              "scope_source":scope_source,"verification_status":"NOT_SERVICE_VERIFIED"
            })

    def add_incorporated(service_id, articles, via, scope_source):
        via_id=article_id(via)
        if via_id not in node_ids: raise ValueError(f"{service_id}: via node missing: {via_id}")
        for num in articles:
            nid=article_id(num)
            if nid not in node_ids: raise ValueError(f"{service_id}: incorporated source node missing: {nid}")
            relations.append({
              "service_id":service_id,"corpus_id":"ordinance37",
              "relation":"incorporates_by_reference","source_node_id":nid,
              "via_node_id":via_id,"scope_source":scope_source,
              "verification_status":"NOT_SERVICE_VERIFIED"
            })

    add_direct("dayservice",ord_scope["direct_articles"],"data/ordinance37-scope.json")
    add_incorporated("dayservice",ord_scope["incorporated_articles"],ord_scope["incorporation_via"],"data/ordinance37-scope.json")
    for rule in ord_scope.get("read_as_rules",[]):
        relations.append({
          "service_id":"dayservice","corpus_id":"ordinance37",
          "relation":"applies_with_substitution","via_node_id":article_id(ord_scope["incorporation_via"]),
          "selector":{k:v for k,v in rule.items() if k!="substitutions"},
          "substitutions":rule["substitutions"],"scope_source":"data/ordinance37-scope.json",
          "verification_status":"NOT_SERVICE_VERIFIED"
        })

    home_articles=home_index.get("selectors",{}).get("resolved_direct_articles",[])
    if not home_articles: raise ValueError("homevisit resolved direct scope is empty")
    add_direct("homevisit",home_articles,"data/services/homevisit/ordinance37-scope.json")

    rehab_direct=rehab_scope["direct_scope"]["article_numbers"]
    add_direct("dayrehab",rehab_direct,"data/services/dayrehab/ordinance37-scope.json")
    inc=rehab_scope["incorporated_scope"]
    add_incorporated("dayrehab",inc["article_numbers"],inc["via_article"],"data/services/dayrehab/ordinance37-scope.json")
    for rule in inc.get("read_as_rules",[]):
        relations.append({
          "service_id":"dayrehab","corpus_id":"ordinance37",
          "relation":"applies_with_substitution","via_node_id":article_id(inc["via_article"]),
          "selector":{k:v for k,v in rule.items() if k!="substitutions"},
          "substitutions":rule["substitutions"],"scope_source":"data/services/dayrehab/ordinance37-scope.json",
          "verification_status":"NOT_SERVICE_VERIFIED"
        })

    for svc in manifest["services"]:
        sid=svc["service_id"]
        config=load(ROOT/svc["config"])
        scope_files=config.get("scope_files") or {}
        scope_source=next((scope_files[key] for key in STANDARDS_SCOPE_KEYS if scope_files.get(key)),None)
        if scope_source and not (ROOT/scope_source).exists():
            raise ValueError(f"{sid}: standards scope source missing: {scope_source}")
        states.append({
          "service_id":sid,
          "corpus_id":mapped.get(sid),
          "scope_status":"SCOPE_DEFINED" if mapped.get(sid) and scope_source else "SCOPE_NOT_DEFINED",
          "scope_source":scope_source,
          "relation_verification":"NOT_SERVICE_VERIFIED",
          "automatic_verification_promotion_allowed":False
        })
    relations.sort(key=lambda x:(x["service_id"],x["relation"],x.get("source_node_id",""),json.dumps(x.get("selector",{}),ensure_ascii=False,sort_keys=True)))
    states.sort(key=lambda x:x["service_id"])
    return {
      "format_version":1,
      "generated_by":"scripts/build_shared_standards_service_relations.py",
      "source_text_duplicated":False,
      "service_scope_states":states,
      "relations":relations,
      "safety":{
        "service_applicability_verified":False,
        "currentness_established":False,
        "human_reviewed":False,
        "automatic_verification_promotion_allowed":False
      }
    }

def render(value): return json.dumps(value,ensure_ascii=False,indent=2)+"\n"
def main():
    p=argparse.ArgumentParser(); p.add_argument("--check",action="store_true"); a=p.parse_args()
    rendered=render(build())
    if a.check:
        if not OUTPUT.exists() or OUTPUT.read_text(encoding="utf-8")!=rendered:
            raise SystemExit("shared standards service relations are stale; run builder")
        print("shared standards service relations: current"); return
    OUTPUT.parent.mkdir(parents=True,exist_ok=True); OUTPUT.write_text(rendered,encoding="utf-8")
    print(f"wrote {OUTPUT.relative_to(ROOT)}")
if __name__=="__main__": main()
