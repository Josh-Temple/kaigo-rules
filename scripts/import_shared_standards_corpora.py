#!/usr/bin/env python3
"""Build reusable full-main-provision ministerial-standards corpora from live e-Gov XML.

Ordinance 37 is handled by the legacy-compatible importer so its existing node IDs stay stable.
All other current standards ordinances are written once under data/shared/standards/<corpus_id>/.
Service applicability is intentionally not encoded into source nodes.
"""
from __future__ import annotations

import hashlib
import json
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
BASE = DATA / "shared" / "standards"
MANIFEST = BASE / "manifest.json"

STRUCTURAL = {
    "Part": "PartTitle",
    "Chapter": "ChapterTitle",
    "Section": "SectionTitle",
    "Subsection": "SubsectionTitle",
    "Division": "DivisionTitle",
}
SKIP_TAGS = {"TOC", "SupplProvision", "AmendProvision", "NewProvision"}
REVISION_FIELDS = [
    "law_revision_id", "law_title", "amendment_law_id", "amendment_law_num",
    "amendment_promulgate_date", "amendment_enforcement_date",
    "amendment_scheduled_enforcement_date", "current_revision_status",
    "repeal_status", "mission", "updated",
]


def fetch(url: str) -> bytes:
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "kaigo-rules-shared-standards-importer/1.0 (+https://github.com/Josh-Temple/kaigo-rules)"},
    )
    with urllib.request.urlopen(req, timeout=90) as response:
        return response.read()


def text_of(el) -> str:
    if el is None:
        return ""
    return " ".join("".join(el.itertext()).split())


def direct_text(el, tag: str) -> str:
    return text_of(el.find(tag))


def canonical_num(value) -> str:
    return str(value or "").strip().replace("_", "-")


def current_revision_info(payload):
    revisions = payload.get("revisions") if isinstance(payload, dict) else None
    if revisions is None and isinstance(payload, dict):
        result = payload.get("result")
        if isinstance(result, dict):
            revisions = result.get("revisions")
    revisions = revisions or []
    current = next(
        (row for row in revisions if row.get("current_revision_status") == "CurrentEnforced"),
        revisions[0] if revisions else None,
    )
    kept = {key: current.get(key) for key in REVISION_FIELDS if current and key in current}
    return kept, len(revisions)


def node_id(prefix: str, article: str, paragraph: str | None = None, chain=()):
    value = f"{prefix}.article.{canonical_num(article)}"
    if paragraph is not None:
        value += f".p.{canonical_num(paragraph)}"
    for level, number in chain:
        value += f".{level}.{canonical_num(number)}"
    return value


def collect_items(entry, parent, prefix, article_num, paragraph_num, parent_id, path, nodes, relations, chain=()):
    tag_levels = {f"Subitem{i}": f"s{i}" for i in range(1, 11)}
    for child in list(parent):
        if child.tag == "Item":
            level, sentence_tag, node_type, title_tag = "i", "ItemSentence", "item", "ItemTitle"
        elif child.tag in tag_levels:
            level = tag_levels[child.tag]
            sentence_tag = child.tag + "Sentence"
            title_tag = child.tag + "Title"
            node_type = "subitem"
        else:
            continue
        number = canonical_num(child.attrib.get("Num"))
        child_chain = tuple(chain) + ((level, number),)
        nid = node_id(prefix, article_num, paragraph_num, child_chain)
        label = direct_text(child, title_tag) or number
        body = direct_text(child, sentence_tag) or text_of(child)
        node_path = path + [label]
        nodes.append({
            "id": nid,
            "node_type": node_type,
            "corpus_id": entry["corpus_id"],
            "law_id": entry["law_id"],
            "article_num": article_num,
            "paragraph_num": paragraph_num,
            "item_level": level,
            "item_num": number,
            "label": label,
            "path": node_path,
            "official_text": body,
            "text_sha256": hashlib.sha256(body.encode("utf-8")).hexdigest(),
            "source_url": f"https://laws.e-gov.go.jp/law/{entry['law_id']}",
            "source_locator": " ＞ ".join(node_path),
            "verification_status": "IMPORTED_NEEDS_INDEPENDENT_CHECK",
            "parent_id": parent_id,
        })
        relations.append({"from": parent_id, "relation": "contains", "to": nid})
        collect_items(entry, child, prefix, article_num, paragraph_num, nid, node_path, nodes, relations, child_chain)


def parse_article(entry, article, structural_path, nodes, relations):
    prefix = entry["node_prefix"]
    article_num = canonical_num(article.attrib.get("Num"))
    title = direct_text(article, "ArticleTitle")
    caption = direct_text(article, "ArticleCaption")
    aid = node_id(prefix, article_num)
    path = structural_path + ([caption] if caption else []) + [title]
    body = text_of(article)
    nodes.append({
        "id": aid,
        "node_type": "article",
        "corpus_id": entry["corpus_id"],
        "law_id": entry["law_id"],
        "article_num": article_num,
        "paragraph_num": None,
        "article_title": title,
        "caption": caption,
        "path": path,
        "official_text": body,
        "text_sha256": hashlib.sha256(body.encode("utf-8")).hexdigest(),
        "source_url": f"https://laws.e-gov.go.jp/law/{entry['law_id']}",
        "source_locator": " ＞ ".join(path),
        "verification_status": "IMPORTED_NEEDS_INDEPENDENT_CHECK",
        "parent_id": None,
    })
    for paragraph in article.findall("Paragraph"):
        pnum = canonical_num(paragraph.attrib.get("Num"))
        pid = node_id(prefix, article_num, pnum)
        ppath = path + [f"第{pnum}項"]
        pbody = direct_text(paragraph, "ParagraphSentence")
        nodes.append({
            "id": pid,
            "node_type": "paragraph",
            "corpus_id": entry["corpus_id"],
            "law_id": entry["law_id"],
            "article_num": article_num,
            "paragraph_num": pnum,
            "label": direct_text(paragraph, "ParagraphNum") or pnum,
            "path": ppath,
            "official_text": pbody,
            "text_sha256": hashlib.sha256(pbody.encode("utf-8")).hexdigest(),
            "source_url": f"https://laws.e-gov.go.jp/law/{entry['law_id']}",
            "source_locator": " ＞ ".join(ppath),
            "verification_status": "IMPORTED_NEEDS_INDEPENDENT_CHECK",
            "parent_id": aid,
        })
        relations.append({"from": aid, "relation": "contains", "to": pid})
        collect_items(entry, paragraph, prefix, article_num, pnum, pid, ppath, nodes, relations)


def walk(entry, element, path, nodes, relations):
    current = list(path)
    if element.tag in STRUCTURAL:
        title = direct_text(element, STRUCTURAL[element.tag])
        if title:
            current.append(title)
    if element.tag == "Article":
        parse_article(entry, element, current, nodes, relations)
        return
    if element.tag in SKIP_TAGS:
        return
    for child in list(element):
        if child.tag in SKIP_TAGS:
            continue
        walk(entry, child, current, nodes, relations)


def build(entry):
    law_id = entry["law_id"]
    api_v1 = f"https://laws.e-gov.go.jp/api/1/lawdata/{law_id}"
    revisions_v2 = f"https://laws.e-gov.go.jp/api/2/law_revisions/{law_id}"
    xml_bytes = fetch(api_v1)
    revisions_bytes = fetch(revisions_v2)
    root = ET.fromstring(xml_bytes)
    law = root.find(".//LawFullText/Law")
    if law is None:
        raise RuntimeError(f"{entry['corpus_id']}: Law element not found")
    body = law.find("LawBody")
    main = body.find("MainProvision") if body is not None else None
    if main is None:
        raise RuntimeError(f"{entry['corpus_id']}: MainProvision not found")

    nodes, relations = [], []
    walk(entry, main, [], nodes, relations)
    article_count = sum(1 for row in nodes if row["node_type"] == "article")
    if article_count == 0:
        raise RuntimeError(f"{entry['corpus_id']}: no articles parsed")

    revisions_payload = json.loads(revisions_bytes.decode("utf-8"))
    current_revision, revision_count = current_revision_info(revisions_payload)
    if current_revision.get("repeal_status") not in (None, "None"):
        raise RuntimeError(f"{entry['corpus_id']}: current corpus unexpectedly reports repeal status")

    meta = {
        "format_version": 1,
        "corpus_id": entry["corpus_id"],
        "node_prefix": entry["node_prefix"],
        "law_id": law_id,
        "law_num": text_of(law.find("LawNum")),
        "law_title": text_of(body.find("LawTitle")) if body is not None else "",
        "source_api_v1": api_v1,
        "source_revisions_v2": revisions_v2,
        "source_page": f"https://laws.e-gov.go.jp/law/{law_id}",
        "xml_sha256": hashlib.sha256(xml_bytes).hexdigest(),
        "revision_response_sha256": hashlib.sha256(revisions_bytes).hexdigest(),
        "current_revision": current_revision,
        "revision_count": revision_count,
        "scope": "FULL_MAIN_PROVISION",
        "counts": {
            "nodes_total": len(nodes),
            "articles_total": article_count,
            "paragraphs_total": sum(1 for row in nodes if row["node_type"] == "paragraph"),
            "items_total": sum(1 for row in nodes if row["node_type"] == "item"),
            "subitems_total": sum(1 for row in nodes if row["node_type"] == "subitem"),
            "contains_relations": len(relations),
        },
        "text_normalization": "XML text with whitespace runs collapsed to one space; Unicode content otherwise unchanged",
        "corpus_verification_status": "IMPORTED_NEEDS_INDEPENDENT_CHECK",
        "service_applicability_status": "SEPARATE_NOT_IMPLIED",
        "human_review_status": "NOT_REVIEWED",
        "automatic_verification_promotion_allowed": False,
    }
    nodes.sort(key=lambda row: row["id"])
    relations.sort(key=lambda row: (row["from"], row["relation"], row["to"]))
    out = BASE / entry["corpus_id"]
    out.mkdir(parents=True, exist_ok=True)
    (out / "nodes.json").write_text(json.dumps(nodes, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (out / "relations.json").write_text(json.dumps(relations, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (out / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(meta, ensure_ascii=False))


def main():
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    for entry in manifest["corpora"]:
        if entry["corpus_id"] == "ordinance37":
            continue
        build(entry)


if __name__ == "__main__":
    main()
