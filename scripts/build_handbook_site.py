#!/usr/bin/env python3
"""Build a read-only working handbook from committed content and source indexes.

This projection never writes verification, currentness or acceptance decisions.
All service references are taken from existing scopes; text is kept verbatim.
"""
import argparse
import json
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(path, default=None):
    file = ROOT / path
    return json.loads(file.read_text()) if file.exists() else default


def article_key(value):
    return tuple(int(n) for n in re.findall(r"\d+", str(value).split(".article.")[-1]))


def article_id(value):
    match = re.match(r"(.+?\.article\.[\d-]+)(?:\.|$)", value)
    return match[1] if match else value


def official_url(value):
    from urllib.parse import urlsplit
    try:
        url = urlsplit(value or "")
        return value if url.scheme == "https" and url.hostname in {
            "www.mhlw.go.jp", "laws.e-gov.go.jp"
        } and not url.username and not url.password and not url.port else ""
    except ValueError:
        return ""


CHAPTERS = [
    ("applicability", "適用対象・基本事項", "サービスの対象、目的、提供形態を整理します。通常の指定、基準該当、共生型などの範囲は、資料に記された区分ごとに確認します。", ["対象者・サービス種別・提供形態を確認する", "定義と基本方針を原典で確認する"], r"基本方針|目的|定義|趣旨|適用|総則"),
    ("designation", "指定・開設", "開設から指定までの準備を整理します。申請先、事前相談、指定の要件、事業開始日をまとめ、自治体の案内を追記できる章です。", ["指定権者と申請・事前相談の窓口を確認する", "法人・事業所・提供形態と開設予定日を整理する"], r"指定|開設|許可|申請|更新"),
    ("staffing", "人員基準", "職種別の配置、資格、勤務時間、兼務を整理します。人数だけで判断せず、常勤・常勤換算・提供単位などの条件を資料と照合します。", ["職種ごとの配置・資格・常勤換算を確認する", "提供日・時間帯・単位ごとの勤務体制を整理する"], r"従業者|員数|職員|人員|管理者|勤務体制"),
    ("equipment", "設備基準", "事業所の区画、面積、設備、備品を整理します。平面図と設備一覧をもとに、対象となる提供形態の基準と対応付けます。", ["平面図・面積・専用区画を確認する", "必要設備・備品と共用の条件を照合する"], r"設備|施設の基準|構造|面積|居室"),
    ("operations", "運営基準", "利用開始からサービス提供、計画、評価までの日常運営を整理します。各条文と実際の業務手順・担当者・様式を結び付けます。", ["契約・説明・計画・提供・評価の手順を整理する", "運営規程と日常の業務手順を照合する"], r"運営|取扱|計画|提供|利用料|勤務|研修"),
    ("records", "記録・情報管理", "サービス提供記録、計画、同意、個人情報の管理を整理します。保存期間、保管場所、閲覧権限は該当する条文と自治体の規定を確認して追記します。", ["必要な記録・様式・保存期間を照合する", "個人情報の取扱い・同意・保管方法を整理する"], r"記録|保存|秘密|個人情報|電磁"),
    ("safeguarding", "利用者保護", "説明と同意、意思の尊重、苦情対応、権利擁護を整理します。事業所の対応手順と窓口を記載し、関係する条文・通知へたどれるようにします。", ["説明・同意と意思確認の手順を整理する", "苦情相談・権利擁護の窓口と対応記録を確認する"], r"説明|同意|苦情|身体的拘束|権利|秘密|掲示|差別"),
    ("incident_and_infection", "事故・感染症・虐待防止", "事故、感染症、虐待が疑われる場合の対応と予防策を整理します。連絡先、報告手順、研修、会議、記録を項目ごとに追記できます。", ["事故・感染症・虐待の対応手順と連絡先を整理する", "委員会・研修・訓練・記録の条件を原典で確認する"], r"事故|感染|衛生|虐待|緊急|非常災害"),
    ("business_continuity", "業務継続計画", "感染症や災害時の業務継続を整理します。優先業務、代替体制、連絡網、備蓄、研修・訓練を、計画と現場の手順に対応付けます。", ["感染症・災害それぞれの継続計画を確認する", "連絡網・備蓄・代替体制・研修訓練を整理する"], r"業務継続|非常災害|感染症"),
    ("remuneration", "基本報酬", "基本報酬の区分と算定の前提を整理します。サービス類型、時間、利用者の区分、規模などを、収載済みの報酬項目から確認します。", ["該当する基本報酬・時間・規模等の区分を確認する", "算定単位と適用日、留意事項を照合する"], r"費|基本|通常|規模|所要時間"),
    ("deductions", "減算", "減算の対象となる条件と確認記録を整理します。対象期間、判定方法、届出、改善後の取扱いを、項目ごとの根拠に沿って追記します。", ["減算条件と対象期間を確認する", "判定・改善・届出の記録を整理する"], r"減算|減じ|未実施|定員|欠如|超過"),
    ("additions", "加算", "加算の名称、算定要件、届出、記録を整理します。対象者、実施内容、職員体制、併算定の条件を項目ごとに確認できます。", ["対象者・体制・実施内容の条件を照合する", "届出・併算定・記録・評価の条件を確認する"], r"加算|加える|処遇改善"),
    ("notifications", "届出・手続", "指定、変更、休止・廃止、報酬体制などの手続を整理します。窓口、様式、提出期限、添付資料を自治体の案内と照合して追記します。", ["手続別の窓口・様式・提出期限を確認する", "変更内容と添付資料・提出記録を整理する"], r"届出|変更|休止|廃止|報告|公表|申請"),
    ("national_qa", "国Q&A", "該当サービスの国Q&Aと、全サービス共通・サービス群共通のQ&Aをまとめます。発出日、問番号、質問の前提、後続の取扱いを分けて確認します。", ["質問の前提と対象サービスを確認する", "発出日・改定・削除情報を確認する"], r".*"),
    ("sources_and_history", "原典・改正履歴", "法令、通知、報酬、Q&Aの出典と版をまとめます。収載済みの資料と未収載の本文を区別し、改正資料は元の本文とは別に確認します。", ["原典URL・取得した版・施行日を確認する", "改正資料と本文の対応・未確認事項を記録する"], r".*"),
]


def build():
    services = load("data/services/catalog.generated.json")["services"]
    service_ids = {s["service_id"] for s in services}
    records, documents = [], []
    record_by_id, corpus_articles, node_labels = {}, {}, {}

    def add_document(id_, category, title, url="", version="", number=""):
        if not any(d["id"] == id_ for d in documents):
            documents.append(dict(id=id_, category=category, title=title,
                                  url=official_url(url), version=version, number=number))

    def add_record(id_, doc, label, title, text="", locator="", state="収載済み・未確認", source_file="", url="", order=None):
        if id_ in record_by_id:
            return record_by_id[id_]
        r = dict(id=id_, document_id=doc, label=str(label), title=str(title),
                 text=text or "", locator=str(locator), state=state,
                 source_file=source_file, url=official_url(url),
                 service_ids=[], service_references={}, order=order or [len(records)])
        records.append(r)
        record_by_id[id_] = r
        return r

    def reference(node_id, sid, basis):
        r = record_by_id.get(article_id(node_id))
        if not r or sid not in service_ids:
            return
        if sid not in r["service_ids"]:
            r["service_ids"].append(sid)
        detail = r["service_references"].setdefault(sid, [])
        info = {"basis": basis, "node_id": node_id, "label": node_labels.get(node_id, r["label"])}
        if info not in detail:
            detail.append(info)

    corpora = [{"corpus_id": "care-insurance-act", "node_prefix": "careact",
                "title": "介護保険法", "law_id": "409AC0000000123",
                "storage": {"nodes": "data/care-insurance-act-nodes.json", "meta": "data/care-insurance-act-meta.json"}}]
    corpora += load("data/shared/standards/manifest.json")["corpora"]
    for corpus in corpora:
        cid = corpus["corpus_id"]
        folder = f"data/shared/standards/{cid}"
        storage = corpus.get("storage", {})
        path = storage.get("nodes", folder + "/nodes.json")
        meta = load(storage.get("meta", folder + "/meta.json"), {})
        add_document(cid, "law" if cid == "care-insurance-act" else "standards",
                     corpus["title"], f'https://laws.e-gov.go.jp/law/{corpus["law_id"]}',
                     meta.get("current_revision", {}).get("amendment_enforcement_date", ""),
                     meta.get("law_num", corpus.get("law_num", "")))
        nodes = load(path, [])
        for node in nodes:
            node_labels[node["id"]] = node.get("source_locator") or " ＞ ".join(node.get("path", [])) or node.get("article_title", "関連箇所")
        articles = [n for n in nodes if n.get("node_type") == "article"]
        corpus_articles[cid] = articles
        for n in sorted(articles, key=lambda n: article_key(n["article_num"])):
            add_record(n["id"], cid, n.get("article_title", n["article_num"]),
                       n.get("caption") or "条文", n.get("official_text", ""),
                       n.get("source_locator") or " ＞ ".join(n.get("path", [])),
                       source_file=path, order=list(article_key(n["article_num"])))

    # Materialized care-act scopes include paragraph-level references for all services.
    for service in services:
        sid = service["service_id"]
        folder = ROOT / "data/services" / sid
        for path in [folder / "care-insurance-act-index.json", folder / "care-insurance-act-index.generated.json"]:
            if path.exists():
                idx = json.loads(path.read_text())
                nodes = idx.get("node_ids", [])
                if isinstance(nodes, dict):
                    nodes = nodes.get("all", [])
                for node_id in nodes:
                    reference(node_id, sid, "登録された関連箇所（適用未確認）")
                break
        if sid == "dayservice":
            for num in load("data/care-insurance-act-scope.json")["articles"]:
                reference(f"careact.article.{num}", sid, "登録された関連条文")

        # Explicit scope selectors are read as references, never as legal acceptance.
        for path in sorted(folder.glob("*scope.json")):
            d = json.loads(path.read_text())
            if "governing_standards_ordinance" in d:
                d = d["governing_standards_ordinance"]
            source = d.get("source_corpus", d.get("shared_corpus", d))
            if not isinstance(source, dict):
                continue
            cid = source.get("corpus_id")
            if not cid or cid not in corpus_articles or cid == "care-insurance-act":
                continue
            prefix = next(c["node_prefix"] for c in corpora if c["corpus_id"] == cid)

            def select(value, basis):
                if isinstance(value, list):
                    for v in value:
                        select(v, basis)
                elif isinstance(value, dict):
                    for key in ("article_ids", "source_node_ids", "target_article_ids", "node_ids"):
                        for node_id in value.get(key, []):
                            reference(node_id, sid, basis)
                    for key in ("article_numbers", "source_article_numbers"):
                        for num in value.get(key, []):
                            reference(f"{prefix}.article.{num}", sid, basis)
                    start = value.get("from_node_id")
                    end = value.get("through_node_id")
                    if start and end:
                        lo, hi = article_key(start), article_key(end)
                        for n in corpus_articles[cid]:
                            if lo <= article_key(n["article_num"]) <= hi:
                                reference(n["id"], sid, basis)
                    for span in value.get("direct_article_ranges", []):
                        lo, hi = article_key(span["from"]), article_key(span["through"])
                        for n in corpus_articles[cid]:
                            if lo <= article_key(n["article_num"]) <= hi:
                                reference(n["id"], sid, basis)
                    for key in ("direct_scope", "incorporated_scope"):
                        if key in value:
                            select(value[key], "準用の参照候補" if key == "incorporated_scope" else basis)

            for key in ("common_scope", "common_direct_scope", "direct_scope", "primary_scope", "service_chapter_direct_scope"):
                select(d.get(key, {}), "直接規定の参照候補")
            if "direct_article_ranges" in d:
                select(d, "直接規定の参照候補")
            select(d.get("incorporation_relations", []), "準用の参照候補")
            select(d.get("incorporated_scope", {}), "準用の参照候補")
            select(d.get("service_variants", []), "提供形態別の参照候補")

    # Legacy ordinary-home-service scopes.
    legacy = load("data/ordinance37-scope.json")
    for key, basis in [("direct_articles", "直接規定の参照候補"), ("incorporated_articles", "準用の参照候補")]:
        for num in legacy[key]:
            reference(f"ordinance37.article.{num}", "dayservice", basis)
    for scope in legacy["additional_service_direct_scopes"]:
        for num in scope["articles"]:
            reference(f"ordinance37.article.{num}", scope["service_id"], "直接規定の参照候補")
    for rel in load("data/shared/standards/service-relations.generated.json")["relations"]:
        if rel.get("source_node_id"):
            reference(rel["source_node_id"], rel["service_id"],
                      "準用の参照候補" if rel["relation"] == "incorporates_by_reference" else "直接規定の参照候補")

    sources = {s["id"]: s for s in load("data/sources.json")}
    # The source order is retained for notice items and fee schedules.
    notice_doc = "interpretation-rouki25"
    add_document(notice_doc, "notices", "基準解釈通知（老企第25号）", "https://www.mhlw.go.jp/web/t_doc?dataId=00ta4369&dataType=1", "旧版・改正資料を含む")
    for sid in service_ids:
        path = f"data/services/{sid}/rouki25-historical.generated.json"
        dataset = load(path, {})
        for index, item in enumerate(dataset.get("items", [])):
            r = add_record(item["id"], notice_doc, " / ".join(filter(None, [str(item.get("group_number", "")), item.get("marker", "")])),
                           item["title"], item.get("body_text", ""), item.get("source_locator", ""),
                           "旧版資料・現行性未確認", path,
                           item.get("source_url", dataset.get("source", {}).get("url", "")),
                           [list(s["service_id"] for s in services).index(sid), index])
            reference(r["id"], sid, "サービス別収載資料")
    packet = load("data/notice-review-packet.json", {})
    for index, item in enumerate(packet.get("items", [])):
        evidence = item.get("source_evidence", [])
        r = add_record(item["notice_id"], notice_doc, " / ".join(item.get("number_path", [])),
                       item["title"], item.get("candidate_text", ""), item.get("section", ""),
                       "再構成本文・現行性未確認", "data/notice-review-packet.json",
                       evidence[0].get("source_url", "") if evidence else "", [0, index])
        reference(r["id"], "dayservice", "サービス別収載資料")

    for service in services:
        sid = service["service_id"]
        path = f"data/services/{sid}/standards-interpretation-staging.json"
        staging = load(path, {})
        if not staging:
            continue
        scope = load(f"data/services/{sid}/standards-interpretation-scope.json", {})
        doc = "notice-summary-" + sid
        add_document(doc, "notices", scope.get("document_title") or service["label"] + "の基準解釈通知", "", "既存の整理メモ・未確認")
        for index, item in enumerate(staging.get("items", [])):
            r = add_record(item["id"], doc, item.get("path", ""), item.get("heading") or item.get("title", "通知項目"),
                           item.get("content_summary", ""), item.get("source_locator", ""),
                           "通知の整理メモ（未確認の要約・原文ではありません）", path,
                           next((u for u in item.get("source_urls", []) if official_url(u)), ""), [index])
            reference(r["id"], sid, "既存のサービス別整理メモ")

    # All-service remuneration indexes. Unstored note bodies remain explicitly empty.
    for service in services:
        sid = service["service_id"]
        path = f"data/services/{sid}/remuneration-index.json"
        d = load(path, {})
        src = d.get("official_source") or next(iter(d.get("canonical_sources", [])), {})
        doc = "remuneration-" + (src.get("source_id") or src.get("id") or sid)
        if not d:
            continue
        add_document(doc, "remuneration", src.get("title") or src.get("notice_number") or "報酬基準", src.get("url", ""), src.get("observed_on_jst", "取得時の掲載表示"))
        items = d.get("items") or d.get("top_level_items", []) + d.get("numeric_child_items", [])
        if "top_level_items" in d:
            def line_number(item):
                match = re.search(r"section-line-(\d+)", item.get("source_locator", ""))
                return int(match[1]) if match else 10**9
            items = sorted(items, key=line_number)
        for index, item in enumerate(items):
            texts = item.get("official_text") or item.get("body_text") or ""
            if not texts and item.get("rates"):
                texts = "\n".join(f'要介護{r["care_level"]}：{r["units"]} {r.get("unit", "単位")}' for r in item["rates"])
                texts = item.get("duration", "") + "\n" + texts
            if not texts:
                texts = " / ".join(item.get("numeric_expressions", []))
            r = add_record(item["id"], doc, item.get("marker", ""), item.get("title", "報酬項目"),
                           texts, item.get("source_locator", ""), "構造・数値の収載／要件本文は原典確認", path,
                           src.get("url", ""), [list(s["service_id"] for s in services).index(sid), index])
            reference(r["id"], sid, "サービス別報酬索引")
        for index, patch in enumerate(d.get("amendment_patches", [])):
            patch_source = next((s for s in d.get("canonical_sources", []) if s["id"] == patch["source_id"]), {})
            patch_doc = "remuneration-amendment-" + patch["source_id"]
            add_document(patch_doc, "remuneration", patch_source.get("title", "報酬改正資料"), patch_source.get("url", ""), "改正差分のみ・本文と分離")
            patch_text = "\n".join(f'{rate["label"]}：千分の{rate["per_thousand"]}' for rate in patch.get("rates", []))
            r = add_record(patch["id"], patch_doc, patch.get("scope", ""), "報酬改正の差分", patch_text,
                           patch.get("scope", ""), "改正資料・掲載本文への自動合成なし", path, patch_source.get("url", ""), [index])
            reference(r["id"], sid, "サービス別改正差分")
    texts = {r["fee_id"]: r for r in load("data/remuneration-current-text.json", [])}
    doc = "remuneration-dayservice"
    add_document(doc, "remuneration", "通所介護の報酬基準", sources.get("mhlw-fee-notice19-base", {}).get("url", ""), "取得した掲載本文")
    for index, item in enumerate(load("data/remuneration-current-skeleton.json", [])):
        text = texts.get(item["id"], {})
        r = add_record(item["id"], doc, " / ".join(item.get("number_path", [])), item["title"],
                       text.get("official_text", ""), item.get("source_locator", ""),
                       "収載済み・算定要件確認中", "data/remuneration-current-skeleton.json",
                       text.get("source_url", ""), [0, index])
        reference(r["id"], "dayservice", "サービス別報酬索引")

    # The separately registered ministerial criteria keep their original notice order.
    delegated = load("data/shared/remuneration-delegated/national-corpus.json")
    legacy_delegated = {r["id"]: r for r in load("data/remuneration-delegated-nodes.json", [])}
    delegated_sids = defaultdict(list)
    for row in load("data/shared/remuneration-delegated/service-applicability.json")["services"]:
        for node_id in row.get("mapped_node_ids", []):
            delegated_sids[node_id].append(row["service_id"])
    for doc in delegated["documents"]:
        add_document("criteria-" + doc["source_id"], "criteria", doc["title"], doc["official_url"], "取得した掲載本文・現行性確認中")
    for index, n in enumerate(delegated["nodes"]):
        storage = n.get("text_storage", {})
        old = legacy_delegated.get(storage.get("legacy_node_id"), {})
        locator = n.get("source_locator", {})
        r = add_record(n["canonical_node_id"], "criteria-" + n["source_id"], n.get("item_label", ""),
                       n.get("heading", "算定基準"), n.get("official_text") or old.get("official_text", ""),
                       locator.get("heading", "") if isinstance(locator, dict) else locator,
                       "収載本文・適用と現行性は確認中", "data/shared/remuneration-delegated/national-corpus.json", order=[index])
        for sid in delegated_sids[r["id"]]:
            reference(r["id"], sid, "登録された別告示の参照候補")

    # Shared fee-guidance nodes may be comparison tables, not consolidated law.
    registry = {s["id"]: s for s in load("data/shared/fee-guidance/source-registry.json", {}).get("sources", [])}
    guidance_scopes = load("data/shared/fee-guidance/service-applicability.json", {}).get("services", [])
    guidance_sids = defaultdict(list)
    for row in guidance_scopes:
        for node_id in row.get("node_ids", []):
            guidance_sids[node_id].append(row["service_id"])
    for index, n in enumerate(load("data/shared/fee-guidance/national-corpus.json", {}).get("nodes", [])):
        src = registry.get(n.get("source_id"), sources.get(n.get("source_id"), {}))
        doc = "guidance-" + n.get("source_id", "unknown")
        add_document(doc, "guidance", src.get("title") or "算定上の留意事項・改正資料", src.get("url", ""), "新旧対照表・所在案内を含む")
        r = add_record(n["id"], doc, " / ".join(n.get("number_path", [])), n.get("title", "留意事項"),
                       n.get("official_text", ""), " / ".join(n.get("number_path", [])),
                       "改正資料・見出し／現行統合本文未確立", "data/shared/fee-guidance/national-corpus.json", order=[index])
        for sid in guidance_sids[n["id"]]:
            reference(r["id"], sid, "登録された留意事項の参照候補")

    # Retain the useful existing dayservice candidate paragraphs as separate records.
    for stage, path in [("baseline", "data/fee-guidance-text-candidates.json"), ("reconstructed", "data/fee-guidance-current-text-candidates.json")]:
        content = load(path, [])
        candidates = content if isinstance(content, list) else content.get("items", [])
        for index, n in enumerate(candidates):
            nid = n.get("guidance_id") or n.get("id")
            if not nid:
                continue
            doc = "guidance-dayservice-" + stage
            add_document(doc, "guidance", "通所介護の算定留意事項（" + ("収載本文" if stage == "baseline" else "再構成候補") + "）", "https://www.mhlw.go.jp/content/12300000/001227887.pdf", "版・再構成段階を分離")
            r = add_record("working." + stage + "." + nid, doc, " / ".join(n.get("number_path", [])), n.get("title", "留意事項"),
                           n.get("candidate_text", ""), " / ".join(n.get("number_path", [])),
                           "収載本文候補・確認中", path, order=[index])
            reference(r["id"], "dayservice", "サービス別収載資料")

    path = "data/services/dayrehab/fee-guidance-index.json"
    guidance = load(path, {})
    for source in guidance.get("canonical_sources", []):
        add_document("guidance-" + source["id"], "guidance", source["title"], source.get("url", ""), source.get("version_note", ""))
    def add_guidance_item(item, order, parent=None):
        source_id = item.get("source_id") or (parent or {}).get("source_id")
        if not source_id:
            return
        source = next((s for s in guidance["canonical_sources"] if s["id"] == source_id), {})
        nid = "guidance.dayrehab." + item.get("id", "-".join(str(n) for n in order))
        r = add_record(nid, "guidance-" + source_id, item.get("slot") or item.get("marker", ""),
                       item.get("title") or item.get("heading", "留意事項の細目"), item.get("official_text") or item.get("body_text", ""),
                       item.get("source_locator") or (parent or {}).get("source_locator", ""),
                       "改正対照表の構造索引・省略を補完しない", path, source.get("url", ""), order)
        reference(r["id"], "dayrehab", "サービス別留意事項の収載構造")
        for index, child in enumerate(item.get("children", [])):
            add_guidance_item(child, order + [index], item)
    for index, item in enumerate(guidance.get("items", [])):
        add_guidance_item(item, [index])

    # Existing notice locator registries fill the remaining service notice sections.
    notice_sources = {}
    for src in load("data/shared/standards-interpretation/manifest.json")["sources"]:
        notice_sources[src["source_id"]] = src
    for src in load("data/shared/standards-interpretation/remaining-source-register.json")["sources"]:
        notice_sources[src["source_id"]] = src
    for filename in ["service-scopes.json", "remaining-service-scopes.json"]:
        for row in load("data/shared/standards-interpretation/" + filename)["services"]:
            for index, source_id in enumerate(row.get("source_ids", [])):
                src = notice_sources.get(source_id, {})
                doc = "notice-locator-" + source_id
                url = src.get("url") or next(iter(src.get("urls", [])), "")
                add_document(doc, "notices", src.get("document_title") or "基準解釈通知の原典案内", url, "旧版・改正資料を含む")
                r = add_record(doc + "." + row["service_id"], doc, "資料案内", row["label"], "",
                               " / ".join(row.get("source_locators", [])), "原典の所在を収載・本文整理待ち",
                               "data/shared/standards-interpretation/" + filename, url, [index])
                reference(r["id"], row["service_id"], "サービス見出しの参照候補")

    # Deterministic source ordering: documents stay in registry order, articles sort numerically.
    doc_order = {d["id"]: i for i, d in enumerate(documents)}
    records.sort(key=lambda r: (doc_order[r["document_id"]], r["order"], r["id"]))
    for r in records:
        r["service_ids"].sort()
    qa_relations = {r["service_id"]: r for r in load("data/qa-service-relations.generated.json")["services"]}
    qa = load("data/qa-corpus.json", [])
    qa_counts = defaultdict(int)
    for q in qa:
        qa_counts[q["service_code"]] += 1
    old_draft = {s["section_id"]: s for s in load("docs/prototypes/data/dayservice-handbook-drafts.v1.json")["sections"]}
    bridges = {sid: load(f"docs/prototypes/evidence-bridges/{sid}.json", {}) for sid in ["dayservice", "dayrehab"]}
    overrides = load("data/handbook-content.json", {}).get("services", {})
    for sid, content in overrides.items():
        if sid not in service_ids:
            raise ValueError("Unknown handbook service: " + sid)
        for section, values in content.get("chapters", {}).items():
            if section not in {c[0] for c in CHAPTERS}:
                raise ValueError("Unknown chapter: " + section)
            if set(values) - {"summary", "paragraphs", "checkpoints"}:
                raise ValueError("Only summary, paragraphs and checkpoints may be edited")
            for key, value in values.items():
                valid = isinstance(value, str) if key == "summary" else isinstance(value, list) and all(isinstance(v, str) for v in value)
                if not valid:
                    raise ValueError("Invalid handbook content: " + key)
    result = []
    by_service = {sid: [r for r in records if sid in r["service_ids"]] for sid in service_ids}
    category = {d["id"]: d["category"] for d in documents}
    for s in services:
        sid = s["service_id"]
        chapters = []
        bridge = {c["section_id"]: c for c in bridges.get(sid, {}).get("chapters", [])}
        service_qa = qa_relations.get(sid, {})
        for index, (section, title, summary, checks, pattern) in enumerate(CHAPTERS, 1):
            source_records = by_service[sid]
            if section in {"remuneration", "deductions", "additions"}:
                source_records = [r for r in source_records if category[r["document_id"]] in {"remuneration", "guidance", "criteria"}]
            elif section == "national_qa":
                source_records = []
            elif section != "sources_and_history":
                source_records = [r for r in source_records if category[r["document_id"]] in {"law", "standards", "notices"}]
            matched = [r["id"] for r in source_records if re.search(pattern, r["title"] + " " + r["locator"])]
            paragraphs = [p["text"] for p in bridge.get(section, {}).get("candidate_paragraphs", [])]
            draft_checks = checks
            if sid == "dayservice":
                draft_checks = [p["text"] for p in old_draft[section]["draft_statements"] if p["kind"] == "CHECKPOINT"] or checks
            chapter = dict(section_id=section, number=index, title=title, summary=summary,
                           paragraphs=paragraphs, checkpoints=draft_checks,
                           reference_ids=matched, editorial_state="作成中・未確認")
            chapter.update(overrides.get(sid, {}).get("chapters", {}).get(section, {}))
            chapters.append(chapter)
        codes = service_qa.get("candidate_query_service_codes", [])
        result.append(dict(service_id=sid, label=s["label"], chapters=chapters,
                           source_record_count=len(by_service[sid]),
                           qa_codes=codes, qa_count=sum(qa_counts[c] for c in codes),
                           qa_direct_codes=service_qa.get("direct_individual_service_codes", [])))
    return {
        "data/handbook.generated.json": dict(schema_version=1, generated_by="scripts/build_handbook_site.py", services=result),
        "data/legal-browser.generated.json": dict(schema_version=1, generated_by="scripts/build_handbook_site.py", documents=documents, records=records),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    for path, data in build().items():
        text = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
        file = ROOT / path
        if args.check:
            if not file.exists() or file.read_text() != text:
                raise SystemExit("Generated content is stale: " + path)
        else:
            file.write_text(text)
        print(path, "OK", len(text.encode()), "bytes")


if __name__ == "__main__":
    main()
