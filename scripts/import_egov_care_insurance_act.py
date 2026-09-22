#!/usr/bin/env python3
import hashlib
import json
import re
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

LAW_ID = "409AC0000000123"
API_V1 = f"https://laws.e-gov.go.jp/api/1/lawdata/{LAW_ID}"
REVISIONS_V2 = f"https://laws.e-gov.go.jp/api/2/law_revisions/{LAW_ID}"
SOURCE_PAGE = f"https://laws.e-gov.go.jp/law/{LAW_ID}"

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
SCOPE_PATH = DATA / "care-insurance-act-scope.json"
NODES_PATH = DATA / "care-insurance-act-nodes.json"
RELATIONS_PATH = DATA / "care-insurance-act-relations.json"
META_PATH = DATA / "care-insurance-act-meta.json"

STRUCTURAL = {
    "Part": "PartTitle",
    "Chapter": "ChapterTitle",
    "Section": "SectionTitle",
    "Subsection": "SubsectionTitle",
    "Division": "DivisionTitle",
}

def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent":"kaigo-rules/1.0 (+https://github.com/Josh-Temple/kaigo-rules)"})
    with urllib.request.urlopen(req, timeout=60) as response:
        return response.read()

def text_of(el):
    if el is None:
        return ""
    return " ".join("".join(el.itertext()).split())

def canonical_num(value):
    return str(value or "").strip().replace("_","-")

def direct_child_text(el, child_name):
    return text_of(el.find(child_name))

def node_id(article, paragraph=None, item_chain=None):
    base=f"careact.article.{canonical_num(article)}"
    if paragraph is not None:
        base += f".p.{canonical_num(paragraph)}"
    for level, number in item_chain or []:
        base += f".{level}.{canonical_num(number)}"
    return base

def sentence_text(container, sentence_tag):
    return text_of(container.find(sentence_tag))

def collect_items(parent, article_num, paragraph_num, parent_id, path, nodes, relations, locator):
    tag_levels={f"Subitem{i}":f"s{i}" for i in range(1,11)}
    for child in list(parent):
        if child.tag=="Item":
            level="i"
        elif child.tag in tag_levels:
            level=tag_levels[child.tag]
        else:
            continue
        num=canonical_num(child.attrib.get("Num"))
        title_tag="ItemTitle" if child.tag=="Item" else child.tag+"Title"
        sentence_tag="ItemSentence" if child.tag=="Item" else child.tag+"Sentence"
        label=direct_child_text(child,title_tag) or num

        chain=[]
        cursor=parent_id.split(f".p.{canonical_num(paragraph_num)}",1)[-1]
        if cursor:
            parts=[p for p in cursor.split(".") if p]
            for i in range(0,len(parts),2):
                if i+1<len(parts): chain.append((parts[i],parts[i+1]))
        chain.append((level,num))

        nid=node_id(article_num,paragraph_num,chain)
        node_path=path+[label]
        body=sentence_text(child,sentence_tag) or text_of(child)
        nodes.append({
            "id":nid,
            "node_type":"item" if level=="i" else "subitem",
            "law_id":LAW_ID,
            "article_num":canonical_num(article_num),
            "paragraph_num":canonical_num(paragraph_num),
            "item_level":level,
            "item_num":num,
            "label":label,
            "path":node_path,
            "official_text":body,
            "text_sha256":hashlib.sha256(body.encode("utf-8")).hexdigest(),
            "service_scope":"通所介護・上位法",
            "source_url":SOURCE_PAGE,
            "source_locator":locator+" "+" ".join(node_path[-2:]),
            "verification_status":"IMPORTED_NEEDS_HUMAN_CHECK",
            "parent_id":parent_id
        })
        relations.append({"from":parent_id,"relation":"contains","to":nid,"target_layer":"care_insurance_act"})
        collect_items(child,article_num,paragraph_num,nid,node_path,nodes,relations,locator)

def parse_article(article, structural_path, nodes, relations):
    article_num=canonical_num(article.attrib.get("Num"))
    article_title=direct_child_text(article,"ArticleTitle")
    caption=direct_child_text(article,"ArticleCaption")
    aid=node_id(article_num)
    article_path=structural_path+([caption] if caption else [])+[article_title]
    article_text=text_of(article)
    locator=" ＞ ".join(article_path)

    nodes.append({
        "id":aid,
        "node_type":"article",
        "law_id":LAW_ID,
        "article_num":article_num,
        "article_title":article_title,
        "caption":caption,
        "path":article_path,
        "official_text":article_text,
        "text_sha256":hashlib.sha256(article_text.encode("utf-8")).hexdigest(),
        "service_scope":"通所介護・上位法",
        "source_url":SOURCE_PAGE,
        "source_locator":locator,
        "verification_status":"IMPORTED_NEEDS_HUMAN_CHECK",
        "parent_id":None
    })

    for paragraph in article.findall("Paragraph"):
        pnum=canonical_num(paragraph.attrib.get("Num"))
        pid=node_id(article_num,pnum)
        pnum_text=direct_child_text(paragraph,"ParagraphNum") or pnum
        body=sentence_text(paragraph,"ParagraphSentence")
        ppath=article_path+[f"第{pnum}項"]
        nodes.append({
            "id":pid,
            "node_type":"paragraph",
            "law_id":LAW_ID,
            "article_num":article_num,
            "paragraph_num":pnum,
            "label":pnum_text,
            "path":ppath,
            "official_text":body,
            "text_sha256":hashlib.sha256(body.encode("utf-8")).hexdigest(),
            "service_scope":"通所介護・上位法",
            "source_url":SOURCE_PAGE,
            "source_locator":locator+f" 第{pnum}項",
            "verification_status":"IMPORTED_NEEDS_HUMAN_CHECK",
            "parent_id":aid
        })
        relations.append({"from":aid,"relation":"contains","to":pid,"target_layer":"care_insurance_act"})
        collect_items(paragraph,article_num,pnum,pid,ppath,nodes,relations,locator)

def walk(element,path,targets,nodes,relations,found):
    current_path=list(path)
    if element.tag in STRUCTURAL:
        title=direct_child_text(element,STRUCTURAL[element.tag])
        if title: current_path.append(title)
    if element.tag=="Article":
        num=canonical_num(element.attrib.get("Num"))
        if num in targets:
            parse_article(element,current_path,nodes,relations)
            found.add(num)
        return
    if element.tag in {"AmendProvision","NewProvision","SupplProvision"}:
        return
    for child in list(element):
        if child.tag in {"TOC","SupplProvision"}: continue
        walk(child,current_path,targets,nodes,relations,found)

def current_revision_info(payload):
    revisions=payload.get("revisions") if isinstance(payload,dict) else None
    if revisions is None and isinstance(payload,dict):
        result=payload.get("result")
        if isinstance(result,dict): revisions=result.get("revisions")
    revisions=revisions or []
    current=next((r for r in revisions if r.get("current_revision_status")=="CurrentEnforced"),None)
    if current is None and revisions: current=revisions[0]
    keep=["law_revision_id","law_title","amendment_law_id","amendment_law_num","amendment_promulgate_date","amendment_enforcement_date","amendment_scheduled_enforcement_date","current_revision_status","repeal_status","mission","updated"]
    return {k:current.get(k) for k in keep if current and k in current},len(revisions)

def add_cross_relations(relations, article_ids, node_ids):
    def add(frm, relation, to, layer):
        if frm not in node_ids:
            raise RuntimeError(f"Cross relation source missing: {frm}")
        relations.append({"from":frm,"relation":relation,"to":to,"target_layer":layer,"verification_status":"STRUCTURAL_MAPPING_NEEDS_HUMAN_CHECK"})

    add("careact.article.8.p.7","defines_service_for","ordinance37.article.92","ordinance37")
    add("careact.article.8.p.7","defines_service_for","fee.dayservice.root","remuneration")
    add("careact.article.41.p.4.i.1","authorizes_fee_standard_for","fee.dayservice.root","remuneration")
    add("careact.article.70","designation_requires_standards","careact.article.74","care_insurance_act")
    add("careact.article.73","requires_compliance_with","careact.article.74","care_insurance_act")
    for num in ["92","93","94","95","96","97","98","99","100","101","102","103","104","104-2","104-3","104-4","105"]:
        add("careact.article.74","delegates_standards_to",f"ordinance37.article.{num}","ordinance37")
    add("careact.article.76-2","enforces","careact.article.74","care_insurance_act")
    add("careact.article.77","sanctions_noncompliance_with","careact.article.74","care_insurance_act")

def main():
    scope=json.loads(SCOPE_PATH.read_text(encoding="utf-8"))
    targets=set(scope["articles"])

    xml_bytes=fetch(API_V1)
    revisions_bytes=fetch(REVISIONS_V2)
    root=ET.fromstring(xml_bytes)
    law=root.find(".//LawFullText/Law")
    if law is None: raise RuntimeError("Law element not found in e-Gov API response")
    law_body=law.find("LawBody")
    main_provision=law_body.find("MainProvision") if law_body is not None else None
    if main_provision is None: raise RuntimeError("MainProvision not found")

    nodes=[]
    relations=[]
    found=set()
    walk(main_provision,[],targets,nodes,relations,found)
    missing=sorted(targets-found)
    if missing: raise RuntimeError("Target articles missing from e-Gov XML: "+", ".join(missing))

    node_ids={n["id"] for n in nodes}
    article_ids={n["id"] for n in nodes if n["node_type"]=="article"}
    add_cross_relations(relations,article_ids,node_ids)

    revision_payload=json.loads(revisions_bytes.decode("utf-8"))
    current_revision,revision_count=current_revision_info(revision_payload)

    focus=scope.get("focus_paragraphs",{})
    for article, paragraphs in focus.items():
        for paragraph in paragraphs:
            pid=f"careact.article.{article}.p.{paragraph}"
            if pid not in node_ids:
                raise RuntimeError(f"Focus paragraph missing: {pid}")

    meta={
        "format_version":1,
        "law_id":LAW_ID,
        "law_num":text_of(law.find("LawNum")),
        "law_title":text_of(law_body.find("LawTitle")) if law_body is not None else "",
        "source_api_v1":API_V1,
        "source_revisions_v2":REVISIONS_V2,
        "source_page":SOURCE_PAGE,
        "xml_sha256":hashlib.sha256(xml_bytes).hexdigest(),
        "revision_response_sha256":hashlib.sha256(revisions_bytes).hexdigest(),
        "current_revision":current_revision,
        "revision_count":revision_count,
        "scope":{"articles":scope["articles"],"focus_paragraphs":focus,"excluded_initial_scope":scope["excluded_initial_scope"]},
        "counts":{
            "nodes_total":len(nodes),
            "articles_total":len(article_ids),
            "relations_total":len(relations),
            "cross_layer_relations":len([r for r in relations if r.get("target_layer")!="care_insurance_act"])
        },
        "text_normalization":"XML text with whitespace runs collapsed to one space; Unicode content otherwise unchanged",
        "review_status":"IMPORTED_NEEDS_HUMAN_CHECK"
    }

    nodes.sort(key=lambda n:n["id"])
    relations.sort(key=lambda r:(r["from"],r["relation"],r["to"]))
    NODES_PATH.write_text(json.dumps(nodes,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    RELATIONS_PATH.write_text(json.dumps(relations,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    META_PATH.write_text(json.dumps(meta,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(meta,ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
