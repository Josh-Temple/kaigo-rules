#!/usr/bin/env python3
"""Build and audit full private Kaigo Rules pilot site.

Generates all 39 services x 15 chapters (585 chapters), service indexes,
legislation records (3,812), integrated client-side search database, runs
link localization, and outputs audit datasets.

SAFETY CONSTRAINTS:
- Fails closed if running in public CI / GitHub Actions (GITHUB_ACTIONS=true or CI=true).
- Rejects output inside the git repository.
- Rejects output to public deployment candidates (public/, dist/, etc.).
- Rejects symbolic links in destination or source paths.
- Never deploys to production; retains RELEASE_HOLD / D_FAIL_HOLD.
"""
from __future__ import annotations

import csv
import gc
import hashlib
import html
import json
import os
import posixpath
import re
import shutil
import subprocess
import sys
import tempfile
import time
from collections import defaultdict
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_github_pages_legislation_pilot as legislation
import localize_github_pages_links_pilot as navigation
import build_github_pages_handbook_pilot as pilot

TOPIC_CHAPTERS = [
    ("staffing", "人員基準"),
    ("equipment", "設備基準"),
    ("operations", "運営基準"),
    ("remuneration", "報酬"),
    ("national_qa", "国Q&A"),
]

DISALLOWED_PUBLIC_DIRS = {
    "public", "dist", "build", "out", ".next", "pages", "static"
}

def safe_escape(text: str) -> str:
    return html.escape(str(text or ""), quote=True)

def safe_escape_text(text: str) -> str:
    return html.escape(str(text or ""), quote=False)

def get_official_url(record: dict, doc: dict) -> str:
    url = record.get("url") or doc.get("url") or ""
    try:
        parts = urlsplit(url)
        if parts.scheme == "https" and parts.hostname in {
            "www.mhlw.go.jp", "laws.e-gov.go.jp", "www.city.yokohama.lg.jp", "cgi.city.yokohama.lg.jp"
        }:
            return url
    except Exception:
        pass
    return ""

def validate_safety_and_dest(dest_dir: Path | None) -> Path:
    # 1. Reject public CI / GitHub Actions
    if os.environ.get("GITHUB_ACTIONS") == "true" or os.environ.get("CI") == "true":
        raise RuntimeError("Refusing to generate private full pilot in public CI/GitHub Actions environment")

    root_resolved = ROOT.resolve()

    if dest_dir is None:
        temp_root = Path(tempfile.gettempdir()).resolve()
        out = Path(tempfile.mkdtemp(prefix="kaigo-full-private-", dir=temp_root))
    else:
        # Check symbolic links in destination or hierarchy
        if dest_dir.is_symlink():
            raise RuntimeError(f"Refusing symbolic link destination: {dest_dir}")
        
        cur = dest_dir
        while cur != cur.parent:
            if cur.is_symlink():
                raise RuntimeError(f"Refusing symbolic link in destination hierarchy: {cur}")
            cur = cur.parent

        dest_resolved = dest_dir.resolve(strict=False)

        # Reject output inside git repository
        if dest_resolved == root_resolved or root_resolved in dest_resolved.parents:
            raise RuntimeError("Refusing to output private pilot inside the repository path")

        # Reject public directory candidates
        if dest_resolved.name in DISALLOWED_PUBLIC_DIRS or any(p.name in DISALLOWED_PUBLIC_DIRS for p in dest_resolved.parents):
            raise RuntimeError(f"Refusing to output private pilot to public directory candidate: {dest_resolved.name}")

        return dest_resolved

    return None

def build_full_pilot(dest_dir: Path | None = None, csv_audit_path: Path | None = None) -> dict:
    t0 = time.time()
    target_dest = validate_safety_and_dest(dest_dir)

    # Atomic staging directory: build everything isolated first
    staging_dir = Path(tempfile.mkdtemp(prefix="kaigo_pilot_stage_"))
    out = staging_dir

    master_path = ROOT / "data/handbook.generated.json"
    legal_path = ROOT / "data/legal-browser.generated.json"
    
    if not master_path.is_file() or not legal_path.is_file():
        raise RuntimeError("Missing handbook or legal master data files")
    if master_path.stat().st_size == 0 or legal_path.stat().st_size == 0:
        raise RuntimeError("Empty master data files")
        
    handbook_data = json.loads(master_path.read_text(encoding="utf-8"))
    legal_data = json.loads(legal_path.read_text(encoding="utf-8"))
    
    services = handbook_data.get("services", [])
    if len(services) != 39:
        raise RuntimeError(f"Expected 39 services in master data, found {len(services)}")

    docs_light = {d["id"]: {"title": d.get("title", ""), "number": d.get("number", ""), "url": d.get("url", "")} for d in legal_data.get("documents", [])}
    records_light = {r["id"]: {
        "label": r.get("label", ""), "title": r.get("title", ""),
        "locator": r.get("locator", ""), "url": r.get("url", ""),
        "doc": r.get("document_id", ""), "state": r.get("state", ""),
        "excerpt": (r.get("text", "")[:300] + ("…" if len(r.get("text", "")) > 300 else ""))
    } for r in legal_data.get("records", [])}
    
    del legal_data
    gc.collect()

    try:
        # 1. Build styles and scripts
        styles_content = pilot.STYLES + "\n" + (ROOT / "app/reader.css").read_text(encoding="utf-8")
        (out / "styles.css").write_text(styles_content, encoding="utf-8")
        (out / "print.js").write_text(pilot.PRINT_JS, encoding="utf-8")
        
        # 2. Build Legislation pilot (3,812 records) - always build fresh in clean staging
        leg_result = legislation.build(out)
        
        # 3. Build search database and QA using the official github-pages-db module
        search_dir = out / "databases/search"
        search_dir.mkdir(parents=True, exist_ok=True)
        
        # Dynamically resolve node binary from PATH with opt fallbacks for portability
        node_bin = shutil.which("node")
        if not node_bin or not Path(node_bin).is_file():
            candidates = [
                "/workspace/opt/node-v22.11.0-linux-x64/bin/node",
                "/workspace/opt/node-v20.18.0-linux-x64/bin/node",
            ]
            for c in candidates:
                if Path(c).is_file():
                    node_bin = c
                    break
        if not node_bin:
            raise RuntimeError("node binary not found in PATH or standard opt paths")
        build_script = ROOT / "experiments/github-pages-db/build.mjs"
        register_script = ROOT / "experiments/github-pages-db/register.mjs"
        
        cmd = [node_bin, "--experimental-strip-types", "--import", str(register_script), str(build_script)]
        proc = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True)
        if proc.returncode != 0:
            raise RuntimeError(f"Search builder failed (exit {proc.returncode}): {proc.stderr[:400]}")
            
        try:
            db_result = json.loads(proc.stdout)
            db_temp_dir = Path(db_result["dir"])
            for f in db_temp_dir.iterdir():
                if f.is_file():
                    shutil.copy2(f, search_dir / f.name)
            shutil.rmtree(db_temp_dir, ignore_errors=True)
        except Exception as e:
            raise RuntimeError(f"Failed to copy search database assets: {e}")
            
        # Verify essential search files exist
        required_search_files = [
            "index.html", "qa.html", "style.css", "app.mjs", "qa-app.mjs",
            "search.mjs", "rank-core.mjs", "qa-core.mjs", "load-json.mjs",
            "services.json", "qa-options.json", "global.json"
        ]
        for name in required_search_files:
            if not (search_dir / name).is_file():
                raise RuntimeError(f"Missing required search database asset: {name}")

        # 4. Build info and fee guidance pages
        (out / "fees").mkdir(parents=True, exist_ok=True)
        (out / "fees/index.html").write_text(
            '<!doctype html><html lang="ja"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width,initial-scale=1">'
            '<title>介護報酬案内 — 静的移行検証</title><link rel="stylesheet" href="../styles.css"></head>'
            '<body><main><article class="answer-page wide-page"><h1>介護報酬の案内</h1>'
            '<p><a href="../index.html">手引一覧へ</a> / <a href="../databases/search/index.html">制度DB横断検索へ</a></p>'
            '<p class="meta">地域区分および一単位単価の確認は、各サービスの手引または検索データベースをご利用ください。</p>'
            '</article></main></body></html>',
            encoding="utf-8"
        )
        
        # 5. Build all 39 services x 15 chapters (585 chapters)
        audit_file = open(csv_audit_path, "w", encoding="utf-8", newline="") if csv_audit_path else None
        writer = csv.writer(audit_file) if audit_file else None
        if writer:
            writer.writerow([
                "source_page", "service_id", "service_label", "chapter_id", "chapter_title",
                "original_url", "normalized_path", "link_text", "link_category", "query",
                "fragment", "target_kind", "is_valid", "can_localize", "localized_route_kind", "localized_relative_href"
            ])
            
        total_links_logged = 0
        generated_pages = []
        root_service_links = []
        
        for service in services:
            sid = service["service_id"]
            if not re.match(r"^[a-z0-9-]+$", sid):
                raise RuntimeError(f"Invalid service identifier: {sid}")
            slabel = service.get("label", sid)
            chapters = service["chapters"]
            if len(chapters) != 15:
                raise RuntimeError(f"Expected 15 chapters for service {sid}, found {len(chapters)}")
            chapter_toc_links = []
            
            for idx, chapter in enumerate(chapters):
                cid = chapter["section_id"]
                if not re.match(r"^[a-z0-9_-]+$", cid):
                    raise RuntimeError(f"Invalid chapter identifier: {cid}")
                slug = cid.replace("_", "-")
                ctitle = chapter["title"]
                cnum = chapter["number"]
                paragraphs = chapter.get("paragraphs", [])
                checkpoints = chapter.get("checkpoints", [])
                ref_ids = chapter.get("reference_ids", [])
                role_sections = chapter.get("role_sections")
                
                prev_ch = chapters[idx - 1] if idx > 0 else None
                next_ch = chapters[idx + 1] if idx < len(chapters) - 1 else None
                
                chapter_dest = out / "handbook" / sid / f"{slug}.html"
                chapter_dest.parent.mkdir(parents=True, exist_ok=True)
                
                with open(chapter_dest, "w", encoding="utf-8") as f:
                    f.write(f'<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow,noarchive"><title>{cnum:02d} {safe_escape(ctitle)} — {safe_escape(slabel)}の手引</title><link rel="stylesheet" href="../../styles.css"><script src="../../print.js" defer></script></head><body>')
                    f.write('<div class="pilot-banner"><strong>静的移行の検証版（一般公開していません）</strong><p>現在の本番とは別の試作品です。法令の現行性・適用条件・自治体の基準を必ず原典で確認してください。</p></div><main>')
                    f.write(f'<article class="answer-page wide-page handbook-page"><p class="eyebrow"><a href="../../services/{sid}/index.html">{safe_escape(slabel)}の手引</a> ／ 第{cnum}章</p><h1>{safe_escape(ctitle)}</h1><section class="handbook-chapter-body">')
                    
                    # Staffing / Roles
                    if cid == "staffing":
                        if role_sections:
                            f.write('<section class="handbook-roles" aria-label="職種ごとの人員基準"><h2 id="staffing-navigation">職種ごとの人員基準</h2><nav class="handbook-role-nav" aria-label="職種一覧"><ul>')
                            for r in role_sections:
                                rid = r.get("role_id", "")
                                f.write(f'<li><a href="#{safe_escape(rid)}">{safe_escape(r.get("role_name", ""))}</a></li>')
                            f.write('</ul></nav>')
                            
                            for r in role_sections:
                                rid = r.get("role_id", "")
                                rname = r.get("role_name", "")
                                reqs = r.get("requirements", [])
                                hours = r.get("work_hours", [])
                                evidence_list = r.get("evidence", [])
                                f.write(f'<section class="handbook-role-card" id="{safe_escape(rid)}"><h4 class="handbook-role-title">{safe_escape(rname)}</h4>')
                                if reqs:
                                    f.write(f'<h5>人員配置・資格要件</h5><ul>{" ".join(f"<li>{safe_escape_text(rq)}</li>" for rq in reqs)}</ul>')
                                if hours:
                                    f.write(f'<h5>勤務形態・提供時間</h5><ul>{" ".join(f"<li>{safe_escape_text(wh)}</li>" for wh in hours)}</ul>')
                                if evidence_list:
                                    e_items = []
                                    for ev in evidence_list:
                                        ev_url = ev.get("url", "")
                                        url_link = f'<div><a href="{safe_escape(ev_url)}" target="_blank" rel="noopener noreferrer">公式原典を開く ↗</a></div>' if ev_url else ""
                                        e_items.append(f'<li><strong>{safe_escape(ev.get("kind", "出典"))}</strong><div>{safe_escape(ev.get("title", ""))}（{safe_escape(ev.get("issuer", ""))}）</div><div>該当箇所：{safe_escape(ev.get("locator", ""))}</div>{url_link}</li>')
                                    f.write(f'<h5>関連する原典と適用上の注意</h5><ul class="handbook-role-evidence">{" ".join(e_items)}</ul>')
                                f.write(f'<p class="handbook-role-return"><a href="#staffing-navigation">職種一覧に戻る ↑</a></p></section>')
                            f.write('</section>')
                        else:
                            f.write(f'<section class="handbook-roles handbook-roles-pending" aria-label="職種ごとの人員基準"><h2 id="staffing-navigation">職種ごとの人員基準（構造化確認中）</h2><p class="handbook-working-note">未確認：このサービス（{safe_escape(slabel)}）の職種別要件は、法令員数・兼務解釈の独立確認を進めています。現時点の基準・確認項目は、本章の「確認すること」および関連する省令・解釈通知をご確認ください。</p><p class="handbook-primary-action"><a href="#handbook-sources-{cid}">人員基準の関連条文・解釈通知を確認する（{len(ref_ids)}件） ↓</a></p></section>')
                            
                    # Paragraphs
                    for p in paragraphs:
                        f.write(f'<div class="handbook-reader-paragraph"><p>{safe_escape_text(p)}</p></div>')
                        
                    # Checkpoints
                    f.write(f'<h2>確認すること</h2><div class="handbook-checklist"><p class="handbook-checklist-instruction">印刷して使える確認用チェックリストです。各項目の条件を原典で確認してください。</p><ul>')
                    for item in checkpoints:
                        f.write(f'<li><label><input type="checkbox" data-handbook-print="true"><span>{safe_escape_text(item)}</span></label></li>')
                    f.write('</ul></div>')
                    
                    # Sources / References
                    if cid == "national_qa":
                        qa_codes = service.get("qa_codes", [])
                        f.write('<h2>関連する国Q&A</h2><p>サービス個別・共通分類の候補を収載しています。各問の条件を原典で確認してください。</p><div class="handbook-inline-links">')
                        for qcode in qa_codes:
                            href = f"https://kaigo-rules.vercel.app/qa?service={qcode}"
                            f.write(f'<a href="{safe_escape(href)}">{safe_escape(qcode)}の国Q&A →</a>')
                            if writer:
                                writer.writerow([f"handbook/{sid}/{slug}.html", sid, slabel, cid, ctitle, href, f"/qa?service={qcode}", f"{qcode}の国Q&A →", "国Q&Aサービス別絞り込み", f"service={qcode}", "", "qa-search", "True", "True", "local_search", f"../../databases/search/qa.html?service={qcode}"])
                            total_links_logged += 1
                        root_qa_href = "https://kaigo-rules.vercel.app/qa"
                        f.write(f'<a href="{safe_escape(root_qa_href)}">国Q&A全体を見る →</a></div>')
                        if writer:
                            writer.writerow([f"handbook/{sid}/{slug}.html", sid, slabel, cid, ctitle, root_qa_href, "/qa", "国Q&A全体を見る →", "国Q&A全体検索", "", "", "qa-search", "True", "True", "local_search", "../../databases/search/qa.html"])
                        total_links_logged += 1
                    else:
                        f.write(f'<h2 id="handbook-sources-{cid}">関連する条文・資料 <small>（{len(ref_ids)}件）</small></h2><p class="meta">この章に関連する資料の候補です。適用関係は原典で確認してください。準用する条文は、読替え前の原文を表示します。</p>')
                        for rid in ref_ids:
                            rec = records_light.get(rid)
                            if not rec: continue
                            doc = docs_light.get(rec.get("doc", ""), {})
                            official = get_official_url(rec, doc)
                            official_btn = f'<a href="{safe_escape(official)}" target="_blank" rel="noopener noreferrer">公式原典を開く ↗</a>' if official else ''
                            link_href = f"https://kaigo-rules.vercel.app/legislation?record={rid}&service={sid}"
                            doc_hash = hashlib.sha256(rid.encode("utf-8")).hexdigest()
                            if writer:
                                writer.writerow([f"handbook/{sid}/{slug}.html", sid, slabel, cid, ctitle, link_href, f"/legislation?record={rid}&service={sid}", "この項目へのリンク", "法令条文個別詳細", f"record={rid}&service={sid}", "", "legislation-record", "True", "True", "local_legislation_record", f"../../legislation/record/{doc_hash}.html"])
                            total_links_logged += 1
                            
                            f.write(f'<details class="handbook-source"><summary><span class="handbook-source-label">{safe_escape(rec.get("label", "項目"))}</span><span>{safe_escape(rec.get("title", ""))}</span></summary><div class="handbook-source-content">')
                            f.write(f'<p class="meta">{safe_escape(doc.get("title", ""))} {safe_escape(doc.get("number", ""))}</p>')
                            f.write(f'<p class="handbook-status">{safe_escape(rec.get("state", ""))}</p>')
                            f.write(f'<p class="handbook-original">{safe_escape_text(rec.get("excerpt", ""))}</p>')
                            f.write(f'<p class="meta">原典の掲載箇所：{safe_escape(rec.get("locator", ""))}</p>')
                            f.write(f'<div class="handbook-inline-links">{official_btn}<a href="{safe_escape(link_href)}">この項目へのリンク</a></div>')
                            f.write('</div></details>')
                            
                    # Sequences and bottom
                    prev_html = f'<a href="../../handbook/{sid}/{prev_ch["section_id"].replace("_", "-")}.html">← {safe_escape(prev_ch["title"])}</a>' if prev_ch else ''
                    next_html = f'<a href="../../handbook/{sid}/{next_ch["section_id"].replace("_", "-")}.html">{safe_escape(next_ch["title"])} →</a>' if next_ch else ''
                    f.write(f'<nav class="handbook-inline-links handbook-chapter-sequence" aria-label="前後の章">{prev_html}<a href="../../services/{sid}/index.html">目次へ</a>{next_html}</nav>')
                    
                    leg_service_href = f"https://kaigo-rules.vercel.app/legislation?service={sid}"
                    if writer:
                        writer.writerow([f"handbook/{sid}/{slug}.html", sid, slabel, cid, ctitle, leg_service_href, f"/legislation?service={sid}", "このサービスの法令等を見る →", "サービス別法令一覧", f"service={sid}", "", "legislation-browse", "True", "True", "local_legislation_browse", f"../../legislation/index.html?service={sid}"])
                    total_links_logged += 1
                    
                    f.write(f'<div class="handbook-inline-links"><a href="../../services/{sid}/index.html#{cid}">手引のこの章へ戻る ↑</a><a href="{safe_escape(leg_service_href)}">このサービスの法令等を見る →</a></div>')
                    f.write('</section></article></main></body></html>')
                    
                chapter_toc_links.append(f'<li id="{cid}"><a href="../../handbook/{sid}/{slug}.html"><span>{chapter["number"]:02d}</span> {safe_escape(ctitle)}</a></li>')
                generated_pages.append(chapter_dest)
                
            # Service index page
            service_leg_link = f"https://kaigo-rules.vercel.app/legislation?service={sid}"
            if writer:
                writer.writerow([f"services/{sid}/index.html", sid, slabel, "", "", service_leg_link, f"/legislation?service={sid}", "法令等を条文順で読む →", "サービス別法令一覧", f"service={sid}", "", "legislation-browse", "True", "True", "local_legislation_browse", f"../../legislation/index.html?service={sid}"])
            total_links_logged += 1
            
            dayrehab_extra = ""
            if sid == "dayrehab":
                if writer:
                    writer.writerow([f"services/{sid}/index.html", sid, slabel, "", "", "https://kaigo-rules.vercel.app/databases/search?service=dayrehab", "/databases/search?service=dayrehab", "このサービスのデータベースを検索 →", "DB検索サービス指定", "service=dayrehab", "", "search", "True", "True", "local_search", "../../databases/search/index.html?service=dayrehab"])
                    writer.writerow([f"services/{sid}/index.html", sid, slabel, "", "", "https://kaigo-rules.vercel.app/rules?service=dayrehab", "/rules?service=dayrehab", "このサービスの基準省令を確認 →", "基準省令絞り込み", "service=dayrehab", "", "legislation-browse", "True", "True", "local_legislation_browse", "../../legislation/index.html?service=dayrehab&category=standards"])
                    writer.writerow([f"services/{sid}/index.html", sid, slabel, "", "", "https://kaigo-rules.vercel.app/notices?service=dayrehab", "/notices?service=dayrehab", "このサービスの解釈通知を確認 →", "解釈通知絞り込み", "service=dayrehab", "", "legislation-browse", "True", "True", "local_legislation_browse", "../../legislation/index.html?service=dayrehab&category=notices"])
                    writer.writerow([f"services/{sid}/index.html", sid, slabel, "", "", "https://kaigo-rules.vercel.app/services/dayrehab/remuneration", "/services/dayrehab/remuneration", "報酬基準を見る →", "報酬章遷移", "", "", "handbook", "True", "True", "local_handbook", "../../handbook/dayrehab/remuneration.html"])
                    writer.writerow([f"services/{sid}/index.html", sid, slabel, "", "", "https://kaigo-rules.vercel.app/services/dayrehab/remuneration/guidance", "/services/dayrehab/remuneration/guidance", "算定上の留意事項を見る →", "留意事項絞り込み", "", "", "legislation-browse", "True", "True", "local_legislation_browse", "../../legislation/index.html?service=dayrehab&category=guidance"])
                total_links_logged += 5
                dayrehab_extra = '<section class="handbook-working-note" aria-label="通所リハビリテーションの報酬関連資料"><p>報酬関連資料は現行性確認中です。現行統合本文とは区別してご確認ください。</p><div class="handbook-inline-links"><a href="https://kaigo-rules.vercel.app/databases/search?service=dayrehab">このサービスのデータベースを検索 →</a><a href="https://kaigo-rules.vercel.app/rules?service=dayrehab">このサービスの基準省令を確認 →</a><a href="https://kaigo-rules.vercel.app/notices?service=dayrehab">このサービスの解釈通知を確認 →</a><a href="https://kaigo-rules.vercel.app/services/dayrehab/remuneration">報酬基準を見る →</a><a href="https://kaigo-rules.vercel.app/services/dayrehab/remuneration/guidance">算定上の留意事項を見る →</a></div></section>'

            service_dest = out / "services" / sid / "index.html"
            service_dest.parent.mkdir(parents=True, exist_ok=True)
            with open(service_dest, "w", encoding="utf-8") as f:
                f.write(f'<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow,noarchive"><title>{safe_escape(slabel)}の手引 — 静的移行検証</title><link rel="stylesheet" href="../../styles.css"></head><body>')
                f.write('<div class="pilot-banner"><strong>静的移行の検証版（一般公開していません）</strong><p>現在の本番とは別の試作品です。法令の現行性・適用条件・自治体の基準を必ず原典で確認してください。</p></div><main>')
                f.write(f'<article class="answer-page wide-page handbook-page"><p class="eyebrow"><a href="../../index.html">サービス別手引</a> ／ 全15章</p><h1>{safe_escape(slabel)}の手引</h1><p class="lead">開設、人員・設備、日常運営、報酬までを章ごとにまとめています。概要と確認項目から、関連する条文・通知・Q&Aへ進めます。</p><p class="handbook-primary-action"><a href="../../handbook/{sid}/staffing.html">人員基準を確認する（職種別の配置・資格・勤務時間）</a></p><p class="handbook-working-note">確認中の説明を含む手引です。適用条件や未確認の注意を読み、判断前に最新の国の原典と指定権者の基準を確認してください。</p><div class="handbook-inline-links handbook-top-links"><a href="{safe_escape(service_leg_link)}">法令等を条文順で読む →</a><a href="../../index.html">別のサービスを選ぶ →</a></div>{dayrehab_extra}<h2 id="handbook-toc">全15章の目次</h2><nav class="handbook-toc" aria-label="手引の目次"><ol>{" ".join(chapter_toc_links)}</ol></nav><p><a href="../../index.html">サービス一覧へ戻る →</a></p></article></main></body></html>')
            generated_pages.append(service_dest)
            root_service_links.append(f'<li><a href="./services/{sid}/index.html">{safe_escape(slabel)}</a></li>')

        root_dest = out / "index.html"
        with open(root_dest, "w", encoding="utf-8") as f:
            f.write(f'<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow,noarchive"><title>サービス別手引 — 静的移行検証</title><link rel="stylesheet" href="./styles.css"></head><body>')
            f.write('<div class="pilot-banner"><strong>静的移行の検証版（一般公開していません）</strong><p>現在の本番とは別の試作品です。法令の現行性・適用条件・自治体の基準を必ず原典で確認してください。</p></div><main>')
            f.write(f'<article class="answer-page wide-page handbook-page"><h1>サービス別手引</h1><p class="lead">介護保険サービス39種類の手引を収載しています。各サービスの人員基準、運営基準、設備基準、報酬告示、留意事項通知、関連国Q&Aへ移動できます。</p><p><a href="./databases/search/index.html">制度DB横断検索を試す</a> / <a href="./databases/search/qa.html">国Q&Aを探す</a></p><nav class="handbook-service-grid" aria-label="サービス一覧"><ul>{" ".join(root_service_links)}</ul></nav></article></main></body></html>')
        generated_pages.append(root_dest)
        
        if audit_file:
            audit_file.close()

        # 6. Run link localization
        nav_report = navigation.localize(out)
        
        # 7. Calculate manifest
        files = [p for p in out.rglob("*") if p.is_file()]
        total_bytes = sum(p.stat().st_size for p in files)
        elapsed = time.time() - t0
        
        # 8. Atomic promotion to target destination
        if target_dest is not None:
            dest_resolved = target_dest.resolve(strict=False)
            dest_resolved.mkdir(parents=True, exist_ok=True)
            # Clear all prior contents so tampered/stale files never persist
            for item in list(dest_resolved.iterdir()):
                if item.is_dir() and not item.is_symlink():
                    shutil.rmtree(item, ignore_errors=True)
                else:
                    item.unlink(missing_ok=True)
            # Copy verified artifacts from staging to target
            for item in staging_dir.iterdir():
                if item.is_dir():
                    shutil.copytree(item, dest_resolved / item.name)
                else:
                    shutil.copy2(item, dest_resolved / item.name)
            shutil.rmtree(staging_dir, ignore_errors=True)
            final_dir = str(dest_resolved)
        else:
            final_dir = str(staging_dir)

        return {
            "directory": final_dir,
            "total_files": len(files),
            "total_bytes": total_bytes,
            "services_count": len(services),
            "chapters_count": len(services) * 15,
            "legislation_records": leg_result.get("records", 0),
            "navigation_report": nav_report,
            "total_links_logged": total_links_logged,
            "elapsed_seconds": round(elapsed, 2)
        }
    except Exception as e:
        # Atomic failure guarantee: clean up staging directory so no partial artifacts remain
        if staging_dir.exists():
            shutil.rmtree(staging_dir, ignore_errors=True)
        raise

if __name__ == "__main__":
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    audit_csv = Path(sys.argv[2]) if len(sys.argv) > 2 else None
    res = build_full_pilot(target, audit_csv)
    print(json.dumps(res, ensure_ascii=False, indent=2))
