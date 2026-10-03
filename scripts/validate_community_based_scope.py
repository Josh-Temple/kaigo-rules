#!/usr/bin/env python3
from __future__ import annotations
import json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def load(p): return json.loads(Path(p).read_text(encoding="utf-8"))
REQUIRED={"care_insurance_act","standards_index","remuneration","delegated_remuneration_criteria","unit_price"}
FORBIDDEN={"official_text","source_text","body_text","full_text"}
JP={"〇":0,"零":0,"一":1,"二":2,"三":3,"四":4,"五":5,"六":6,"七":7,"八":8,"九":9}
def jpint(s):
    total=0; digit=0
    for ch in s:
        if ch in JP: digit=JP[ch]
        elif ch=="十": total+=(digit or 1)*10; digit=0
        elif ch=="百": total+=(digit or 1)*100; digit=0
        elif ch=="千": total+=(digit or 1)*1000; digit=0
    return str(total+digit)
def refs(text):
    out=set()
    for m in re.finditer(r"第([一二三四五六七八九十百千]+)条((?:の[一二三四五六七八九十百千]+)*)",text or ""):
        n=jpint(m.group(1))
        if m.group(2): n+="-"+"-".join(jpint(x) for x in m.group(2).split("の") if x)
        out.add(n)
    return out
def walk(v):
    if isinstance(v,dict):
        for k,x in v.items():
            if k in FORBIDDEN: raise AssertionError(f"source body key forbidden: {k}")
            if k=="automatic_verification_promotion_allowed" and x is not False: raise AssertionError("auto promotion enabled")
            if k=="verification_status" and x!="NOT_SERVICE_VERIFIED": raise AssertionError(f"unexpected verification: {x}")
            if k=="currentness_status" and x=="PASS": raise AssertionError("currentness promoted")
            walk(x)
    elif isinstance(v,list):
        for x in v: walk(x)
manifest=load(ROOT/"data/services/manifest.json")
targets=[x for x in manifest["services"] if x.get("service_class")=="COMMUNITY_BASED_SERVICE"]
assert targets
act=load(ROOT/"data/care-insurance-act-nodes.json"); actids={x["id"] for x in act}
std=load(ROOT/"data/shared/standards/community-based-standards/nodes.json")
stdids={x["id"] for x in std}; byid={x["id"]:x for x in std}
order=[x["article_num"] for x in std if x.get("node_type")=="article"]; pos={n:i for i,n in enumerate(order)}
counts={"services":0,"care_act_scopes":0,"standards_scopes":0,"remuneration_scopes":0,"delegated_scopes":0,"unit_price_scopes":0,"unresolved_scopes":0,"applicability_verification_unfinished":0}
for svc in targets:
    sid=svc["service_id"]; cfg=load(ROOT/svc["config"]); rel=f"data/services/{sid}/shared-corpus-scope.json"
    assert (ROOT/rel).exists(), f"{sid}: scope missing"
    s=load(ROOT/rel); walk(s)
    assert s["service_id"]==sid and s["policy"]["shared_source_body_duplicated"] is False
    for k in REQUIRED: assert cfg.get("scope_files",{}).get(k)==rel, f"{sid}: config link missing {k}"
    if sid in {"community-dayservice","regular-round","night-homevisit"}:
        assert "standards_interpretation" in cfg["scope_files"] and "standards_interpretation_staging" in cfg["scope_files"]
    ca=s["care_insurance_act"]
    for nid in [ca["service_definition"]["source_node_id"],ca["service_definition"]["paragraph_node_id"],ca["service_definition"]["regional_service_class_paragraph_node_id"]]:
        assert nid in actids, f"{sid}: Care Act node missing {nid}"
    for row in ca["common_scope"]:
        for f in ("source_node_id","via_node_id"):
            if row.get(f): assert row[f] in actids, f"{sid}: Care Act node missing {row[f]}"
        for nid in row.get("target_node_ids",[]): assert nid in actids, f"{sid}: Care Act target missing {nid}"
        if row.get("article_range"):
            for n in (row["article_range"]["from"],row["article_range"]["through"]): assert f"careact.article.{n}" in actids
    st=s["governing_standards_ordinance"]
    for rg in st["direct_article_ranges"]:
        a,b=rg["from"],rg["through"]; assert a in pos and b in pos and pos[a]<=pos[b], f"{sid}: invalid direct range {a}..{b}"
    for sp in st.get("conditional_or_special",[]):
        a,b=sp["range"]; assert a in pos and b in pos and pos[a]<=pos[b], f"{sid}: invalid special range {a}..{b}"
    for r in st["incorporation_relations"]:
        via=r["via_node_id"]; assert via in byid, f"{sid}: missing via {via}"
        text=byid[via].get("official_text",""); assert "準用" in text, f"{sid}: via is not 準用 {via}"
        rr=refs(text); assert rr, f"{sid}: no refs parsed {via}"
        for n in rr: assert f"standards34.article.{n}" in stdids, f"{sid}: referenced standards article missing {n}"
        if "読み替" in text: assert r["read_as_relation"]["resolution"]=="SUBSTITUTIONS_IN_VIA_NODE_OFFICIAL_TEXT_WHEN_PRESENT"
    assert s["remuneration_notification"]["scope_status"]=="SCOPE_DEFINED"
    assert s["delegated_remuneration_criteria"]["scope_status"]=="PARTIAL_SCOPE_DEFINED"
    assert s["delegated_remuneration_criteria"]["clause_level_scope_status"]=="NOT_ESTABLISHED"
    assert s["unit_price_regional_classification"]["scope_status"]=="SCOPE_DEFINED"
    assert cfg.get("publication_gate",{}).get("public_routes_enabled") is False
    counts["services"]+=1; counts["care_act_scopes"]+=1; counts["standards_scopes"]+=1; counts["remuneration_scopes"]+=1; counts["delegated_scopes"]+=1; counts["unit_price_scopes"]+=1; counts["unresolved_scopes"]+=1; counts["applicability_verification_unfinished"]+=5
print(json.dumps(counts,ensure_ascii=False,sort_keys=True))
