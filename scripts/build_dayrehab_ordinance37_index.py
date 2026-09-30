#!/usr/bin/env python3
"""Build the non-duplicating dayrehab Ordinance 37 index from the shared corpus."""
from __future__ import annotations
import argparse, json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/"data"
SERVICE_DIR=DATA/"services/dayrehab"
SHARED_SCOPE=DATA/"ordinance37-scope.json"
SERVICE_SCOPE=SERVICE_DIR/"ordinance37-scope.json"
OUTPUT=SERVICE_DIR/"ordinance37-index.generated.json"

def load(path): return json.loads(path.read_text(encoding="utf-8"))
def article_key(value): return tuple(int(x) for x in str(value).split("-"))

def build():
    shared_scope=load(SHARED_SCOPE)
    service_scope=load(SERVICE_SCOPE)
    nodes=load(DATA/"ordinance37-nodes.json")
    meta=load(DATA/"ordinance37-meta.json")

    entries=[x for x in shared_scope.get("additional_service_direct_scopes",[]) if x.get("service_id")=="dayrehab"]
    if len(entries)!=1: raise ValueError("shared Ordinance 37 scope must contain exactly one dayrehab direct scope")
    direct=[str(x) for x in service_scope["direct_scope"]["article_numbers"]]
    if entries[0].get("articles")!=direct: raise ValueError("shared and service-specific dayrehab direct article lists differ")

    inc=service_scope.get("incorporated_scope",{})
    if inc.get("via_article")!="119": raise ValueError("dayrehab incorporated scope must be via Article 119")
    incorporated=[str(x) for x in inc.get("article_numbers",[])]
    if len(incorporated)!=25 or len(set(incorporated))!=25: raise ValueError("dayrehab Article 119 scope must contain 25 unique articles")

    direct_set=set(direct); incorporated_set=set(incorporated)
    direct_nodes=[x for x in nodes if str(x.get("article_num")) in direct_set]
    incorporated_nodes=[x for x in nodes if str(x.get("article_num")) in incorporated_set]
    direct_articles=[x for x in direct_nodes if x.get("node_type")=="article"]
    incorporated_articles=[x for x in incorporated_nodes if x.get("node_type")=="article"]

    observed_direct={str(x.get("article_num")) for x in direct_articles}
    if observed_direct!=direct_set:
        raise ValueError(f"dayrehab direct coverage mismatch: missing={sorted(direct_set-observed_direct,key=article_key)}")
    wrong_chapter=[x["id"] for x in direct_articles if not x.get("path") or x["path"][0]!="第八章 通所リハビリテーション"]
    if wrong_chapter: raise ValueError("dayrehab direct article outside Chapter 8: "+", ".join(wrong_chapter))

    observed_inc={str(x.get("article_num")) for x in incorporated_articles}
    missing_inc=sorted(incorporated_set-observed_inc,key=article_key)
    unexpected=sorted(observed_inc-incorporated_set,key=article_key)
    if unexpected: raise ValueError("unexpected incorporated articles: "+", ".join(unexpected))
    # Fail closed on the known corpus gap. Do not fabricate Article 64 text.
    if missing_inc not in ([],["64"]):
        raise ValueError("unexpected dayrehab incorporated corpus gaps: "+", ".join(missing_inc))

    direct_ids=[x["id"] for x in direct_nodes]
    incorporated_ids=[x["id"] for x in incorporated_nodes]
    all_ids=list(dict.fromkeys(direct_ids+incorporated_ids))
    all_selected=[x for x in nodes if x["id"] in set(all_ids)]
    by_type={}
    for row in all_selected: by_type[row["node_type"]]=by_type.get(row["node_type"],0)+1

    return {
      "format_version":2,
      "generated_by":"scripts/build_dayrehab_ordinance37_index.py",
      "service_id":"dayrehab","layer":"ordinance37",
      "status":"DIRECT_TEXT_PLUS_VERIFIED_INCORPORATION_SCOPE",
      "source_corpus":{
        "nodes_file":"data/ordinance37-nodes.json","meta_file":"data/ordinance37-meta.json",
        "law_id":meta["law_id"],"current_revision_id":meta["current_revision"]["law_revision_id"],
        "xml_sha256":meta["xml_sha256"],"corpus_review_status":meta.get("review_status")
      },
      "scope_sources":{"service_scope":"data/services/dayrehab/ordinance37-scope.json","shared_corpus_scope":"data/ordinance37-scope.json"},
      "selectors":{
        "chapter":service_scope["chapter"],"resolved_direct_articles":direct,
        "article119_incorporated_articles":incorporated,
        "locally_resolved_incorporated_articles":sorted(observed_inc,key=article_key),
        "missing_shared_corpus_articles":missing_inc
      },
      "counts":{
        "selected_nodes_total":len(all_selected),
        "selected_articles":len(direct_articles)+len(incorporated_articles),
        "direct_articles":len(direct_articles),"incorporated_articles_local":len(incorporated_articles),
        "incorporated_articles_total":len(incorporated),"incorporated_articles_missing_local":len(missing_inc),
        "by_type":by_type
      },
      "node_ids":all_ids,
      "node_ids_by_basis":{"direct":direct_ids,"incorporated":incorporated_ids},
      "assurance":{
        "legal_text_duplicated":False,
        "direct_text_independent_verification":"data/dayrehab-ordinance37-independent-audit.json",
        "article119_relation_independent_verification":"data/dayrehab-article119-relation-independent-audit.json",
        "missing_text_is_not_fabricated":True,"human_review":"NOT_REVIEWED",
        "automatic_verification_promotion_allowed":False
      }
    }

def render(payload): return json.dumps(payload,ensure_ascii=False,indent=2)+"\n"
def main():
    p=argparse.ArgumentParser(); p.add_argument("--check",action="store_true"); a=p.parse_args()
    rendered=render(build())
    if a.check:
        if not OUTPUT.exists() or OUTPUT.read_text(encoding="utf-8")!=rendered:
            raise SystemExit("dayrehab Ordinance 37 index is stale; run builder")
        print("dayrehab Ordinance 37 index: current"); return
    OUTPUT.write_text(rendered,encoding="utf-8"); print(f"wrote {OUTPUT.relative_to(ROOT)}")
if __name__=="__main__": main()
