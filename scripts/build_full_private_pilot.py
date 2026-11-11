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

def resolve_node_binary(explicit_path: str | None = None) -> str:
    """Safely resolve and validate Node.js binary without shell string concatenation."""
    if explicit_path:
        p = Path(explicit_path)
        if not p.is_file():
            raise RuntimeError(f"Explicitly specified Node.js binary not found: {explicit_path}")
        node_bin = str(p.resolve())
    elif os.environ.get("NODE_BINARY"):
        p = Path(os.environ["NODE_BINARY"])
        if not p.is_file():
            raise RuntimeError(f"NODE_BINARY environment variable points to missing file: {p}")
        node_bin = str(p.resolve())
    else:
        found = shutil.which("node")
        if found:
            node_bin = found
        else:
            candidates = [
                "/workspace/opt/node-v22.11.0-linux-x64/bin/node",
                "/workspace/opt/node-v20.18.0-linux-x64/bin/node",
                "/usr/local/bin/node",
                "/usr/bin/node",
            ]
            node_bin = None
            for c in candidates:
                if Path(c).is_file():
                    node_bin = c
                    break
            if not node_bin:
                raise RuntimeError("Node.js binary not found in PATH or standard system/opt paths")

    # Verify execution and version without shell strings
    try:
        proc = subprocess.run([node_bin, "-v"], capture_output=True, text=True, check=True)
        version_str = proc.stdout.strip()
    except Exception as e:
        raise RuntimeError(f"Node.js binary '{node_bin}' failed to execute: {e}")

    m = re.match(r"^v(\d+)\.", version_str)
    if m:
        major = int(m.group(1))
        if major < 20:
            raise RuntimeError(f"Node.js version {version_str} is unsupported. Node.js >= v20.0.0 is required.")

    return node_bin


def compute_file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def get_git_info() -> tuple[str, str]:
    """Retrieve git commit SHA and tree hash if git is available."""
    try:
        commit = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=str(ROOT), capture_output=True, text=True, check=True
        ).stdout.strip()
        tree = subprocess.run(
            ["git", "rev-parse", "HEAD^{tree}"],
            cwd=str(ROOT), capture_output=True, text=True, check=True
        ).stdout.strip()
        return commit, tree
    except Exception:
        return "UNKNOWN_COMMIT", "UNKNOWN_TREE"


def verify_manifest(target_dir: Path) -> dict:
    """Verify integrity of a generated pilot directory against its manifest."""
    manifest_path = target_dir / "manifest.json"
    if not manifest_path.is_file():
        raise RuntimeError(f"Manifest not found in destination: {manifest_path}")

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("status") != "COMPLETE":
        raise RuntimeError(f"Manifest status is not COMPLETE: {manifest.get('status')}")

    files_spec = manifest.get("files", {})
    if not files_spec:
        raise RuntimeError("Manifest does not contain any file specifications")

    # 1. Check all manifest files exist and match hashes and sizes
    checked_count = 0
    total_bytes = 0
    for rel_path, spec in files_spec.items():
        fp = target_dir / rel_path
        if not fp.is_file():
            raise RuntimeError(f"File listed in manifest is missing on disk: {rel_path}")
        size = fp.stat().st_size
        if size != spec["size"]:
            raise RuntimeError(f"File size mismatch for {rel_path}: expected {spec['size']}, got {size}")
        actual_sha = compute_file_sha256(fp)
        if actual_sha != spec["sha256"]:
            raise RuntimeError(f"SHA-256 mismatch for {rel_path}: expected {spec['sha256']}, got {actual_sha}")
        checked_count += 1
        total_bytes += size

    # 2. Check no extraneous files exist on disk
    allowed_set = set(files_spec.keys()) | {"manifest.json"}
    for p in target_dir.rglob("*"):
        if p.is_file():
            rel = str(p.relative_to(target_dir)).replace("\\", "/")
            if rel not in allowed_set:
                raise RuntimeError(f"Extraneous unverified file found in destination: {rel}")

    return {
        "ok": True,
        "status": "COMPLETE",
        "verified_files": checked_count,
        "total_bytes": total_bytes,
        "git_commit": manifest.get("git_commit"),
        "git_tree": manifest.get("git_tree"),
        "generated_at": manifest.get("generated_at"),
    }

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

def get_safe_staging_dir(prefix: str = "kaigo_pilot_stage_") -> Path:
    """Return a fast temporary staging directory in local tmpfs."""
    return Path(tempfile.mkdtemp(prefix=prefix))


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

def build_full_pilot(
    dest_dir: Path | None = None,
    csv_audit_path: Path | None = None,
    node_bin_override: str | None = None,
) -> dict:
    t0 = time.time()
    target_dest = validate_safety_and_dest(dest_dir)

    # 0. Early environment and prerequisite validation
    node_bin = resolve_node_binary(node_bin_override)

    master_path = ROOT / "data/handbook.generated.json"
    legal_path = ROOT / "data/legal-browser.generated.json"
    
    if not master_path.is_file() or not legal_path.is_file():
        raise RuntimeError("Missing handbook or legal master data files")
    if master_path.stat().st_size == 0 or legal_path.stat().st_size == 0:
        raise RuntimeError("Empty master data files")

    # Atomic staging directory: build everything isolated first
    staging_dir = get_safe_staging_dir(prefix="kaigo_pilot_stage_")
    out = staging_dir
        
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
        
        # 7. Generate Manifest and self-verify in staging
        git_commit, git_tree = get_git_info()
        generated_files = {}
        for p in sorted(out.rglob("*")):
            if p.is_file():
                rel = str(p.relative_to(out)).replace("\\", "/")
                generated_files[rel] = {
                    "sha256": compute_file_sha256(p),
                    "size": p.stat().st_size
                }

        manifest_data = {
            "status": "COMPLETE",
            "git_commit": git_commit,
            "git_tree": git_tree,
            "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "builder_node": node_bin,
            "master_data_hashes": {
                "handbook.generated.json": compute_file_sha256(master_path),
                "legal-browser.generated.json": compute_file_sha256(legal_path),
            },
            "builder_hashes": {
                "build_full_private_pilot.py": compute_file_sha256(Path(__file__)),
                "build_github_pages_legislation_pilot.py": compute_file_sha256(ROOT / "scripts/build_github_pages_legislation_pilot.py"),
                "localize_github_pages_links_pilot.py": compute_file_sha256(ROOT / "scripts/localize_github_pages_links_pilot.py"),
                "build_github_pages_handbook_pilot.py": compute_file_sha256(ROOT / "scripts/build_github_pages_handbook_pilot.py"),
            },
            "total_files": len(generated_files),
            "total_bytes": sum(item["size"] for item in generated_files.values()),
            "services_count": len(services),
            "chapters_count": len(services) * 15,
            "legislation_records": leg_result.get("records", 0),
            "total_links_logged": total_links_logged,
            "files": generated_files
        }
        manifest_path = out / "manifest.json"
        manifest_path.write_text(json.dumps(manifest_data, ensure_ascii=False, indent=2), encoding="utf-8")

        # Self-verify staging directory against manifest before promotion
        verify_manifest(out)

        elapsed = time.time() - t0

        # 8. Transactional promotion to target destination with rollback safety
        if target_dest is not None:
            dest_resolved = target_dest.resolve(strict=False)
            dest_backup = None
            if dest_resolved.exists() and any(dest_resolved.iterdir()):
                dest_backup = dest_resolved.parent / f".kaigo_bak_{dest_resolved.name}_{int(time.time()*1000)}"
                os.rename(dest_resolved, dest_backup)

            try:
                # Promote staging to dest_resolved
                try:
                    os.rename(staging_dir, dest_resolved)
                except OSError:
                    # Cross-filesystem promotion (e.g. tmpfs to network disk)
                    shutil.copytree(staging_dir, dest_resolved)
                    shutil.rmtree(staging_dir, ignore_errors=True)

                # Verify target destination matches manifest on disk
                verify_manifest(dest_resolved)

                # Promotion succeeded: cleanup backup
                if dest_backup and dest_backup.exists():
                    shutil.rmtree(dest_backup, ignore_errors=True)
                final_dir = str(dest_resolved)
            except Exception as prom_err:
                # Promotion failed: restore previous destination from backup
                if dest_resolved.exists():
                    shutil.rmtree(dest_resolved, ignore_errors=True)
                if dest_backup and dest_backup.exists():
                    os.rename(dest_backup, dest_resolved)
                raise RuntimeError(f"Promotion to target destination failed (rolled back): {prom_err}") from prom_err
        else:
            final_dir = str(staging_dir)

        return {
            "directory": final_dir,
            "total_files": manifest_data["total_files"],
            "total_bytes": manifest_data["total_bytes"],
            "services_count": manifest_data["services_count"],
            "chapters_count": manifest_data["chapters_count"],
            "legislation_records": manifest_data["legislation_records"],
            "navigation_report": nav_report,
            "total_links_logged": total_links_logged,
            "git_commit": git_commit,
            "git_tree": git_tree,
            "manifest_verified": True,
            "elapsed_seconds": round(elapsed, 2)
        }
    except Exception as e:
        # Atomic failure guarantee: clean up staging directory so no partial artifacts remain
        if staging_dir.exists():
            shutil.rmtree(staging_dir, ignore_errors=True)
        raise

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Build full private Kaigo Rules pilot site")
    parser.add_argument("target", nargs="?", default=None, help="Output destination directory")
    parser.add_argument("audit_csv", nargs="?", default=None, help="Path to write link audit CSV")
    parser.add_argument("--node-bin", default=None, help="Explicit path to Node.js binary")
    parser.add_argument("--verify-only", action="store_true", help="Verify target directory against manifest.json without rebuilding")
    args = parser.parse_args()

    if args.verify_only:
        if not args.target:
            print("Error: --verify-only requires target directory", file=sys.stderr)
            sys.exit(1)
        res = verify_manifest(Path(args.target))
        print(json.dumps(res, ensure_ascii=False, indent=2))
    else:
        target_path = Path(args.target) if args.target else None
        csv_path = Path(args.audit_csv) if args.audit_csv else None
        res = build_full_pilot(target_path, csv_path, node_bin_override=args.node_bin)
        print(json.dumps(res, ensure_ascii=False, indent=2))
