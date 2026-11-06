#!/usr/bin/env python3
"""Unpublished static detail projection of existing public /legislation records.

The Next.js page already reads this generated legal-browser corpus. This
projection does not export source_file, order, service_references or raw datasets.
It MUST NOT be published until content/scope and visual parity are accepted.
"""
from __future__ import annotations

import html
import json
import shutil
import hashlib
import sys
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
ALLOWED_FIELDS = {"id", "document_id", "label", "title", "text", "locator",
                  "state", "url", "service_ids"}


def clean_id(value):
    """Preserve existing canonical IDs while using a safe opaque filename."""
    if (not isinstance(value, str) or not 1 <= len(value) <= 2048
            or any(ord(char) < 32 or ord(char) == 127 for char in value)):
        raise RuntimeError("Unsafe legal record ID")
    return value


def filename(record_id: str) -> str:
    return hashlib.sha256(record_id.encode("utf-8")).hexdigest() + ".html"


def official_url(url):
    if not isinstance(url, str) or not url:
        return None
    from urllib.parse import urlsplit
    parts = urlsplit(url)
    if parts.scheme != "https" or not parts.netloc or parts.username or parts.password or any(
        ord(char) < 32 for char in url
    ):
        raise RuntimeError("Untrusted source URL")
    return url


def build(out: Path, corpus: Path = ROOT / "data/legal-browser.generated.json") -> dict:
    if not out.is_dir() or out.is_symlink():
        raise RuntimeError("Missing private static output")
    if not corpus.is_file() or corpus.is_symlink():
        raise RuntimeError("Missing validated generated legal browser corpus")
    data = json.loads(corpus.read_text(encoding="utf-8"))
    docs = data.get("documents")
    records = data.get("records")
    if not isinstance(docs, list) or not isinstance(records, list) or not records:
        raise RuntimeError("Missing legal browser records")
    document_map = {}
    document_category = {}
    for item in docs:
        if not isinstance(item, dict) or not isinstance(item.get("id"), str) or not isinstance(item.get("title"), str):
            raise RuntimeError("Invalid public document")
        if item["id"] in document_map:
            raise RuntimeError("Duplicate legal document ID")
        document_map[item["id"]] = item["title"]
        document_category[item["id"]] = item.get("category", "")
    dest = out / "legislation" / "record"
    if dest.exists():
        raise RuntimeError("Static legislation already generated")
    dest.mkdir(parents=True)
    manifest = {}
    browse_rows = []
    for row in records:
        if not isinstance(row, dict) or not ALLOWED_FIELDS.issubset(row):
            raise RuntimeError("Missing public legal record fields")
        record_id = clean_id(row["id"])
        if not isinstance(row["document_id"], str) or row["document_id"] not in document_map:
            raise RuntimeError("Legal document reference absent")
        if not all(isinstance(row[k], str) for k in ("label", "title", "text", "locator", "state")):
            raise RuntimeError("Invalid legal source text")
        if not isinstance(row["service_ids"], list) or any(not isinstance(s, str) for s in row["service_ids"]):
            raise RuntimeError("Invalid legal services")
        if len(row["text"]) > 1_000_000:
            raise RuntimeError("Unbounded legal text")
        if record_id in manifest:
            raise RuntimeError("Duplicate legal record")
        manifest[record_id] = {"document": row["document_id"], "category": document_category[row["document_id"]], "services": row["service_ids"]}
        browse_rows.append({
            "id": record_id, "file": filename(record_id),
            "label": row["label"], "title": row["title"], "text": row["text"],
            "locator": row["locator"], "document": row["document_id"],
            "document_title": document_map[row["document_id"]],
            "category": document_category[row["document_id"]],
            "services": row["service_ids"],
        })
        target = dest / filename(record_id)
        if target.exists():
            raise RuntimeError("Duplicate legal record")
        source = official_url(row["url"])
        source_link = ('<p><a href="' + html.escape(source, quote=True) +
                       '" rel="noopener noreferrer">公式原典を確認</a></p>') if source else ""
        label = html.escape(row["label"], quote=True)
        title = html.escape(row["title"], quote=True)
        doc_name = html.escape(document_map[row["document_id"]], quote=True)
        text = html.escape(row["text"], quote=False)
        page = (
            '<!doctype html><html lang="ja"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width,initial-scale=1">'
            '<meta name="robots" content="noindex,nofollow,noarchive">'
            '<title>' + label + ' — 静的移行検証</title>'
            '<link rel="stylesheet" href="../../databases/search/style.css">'
            '</head><body><main><article class="handbook-page">'
            '<h1>' + label + '</h1><h2>' + title + '</h2>'
            '<p>' + doc_name + '</p><p>制度の改正・適用範囲・自治体ごとの扱いは、必ず原典と指定権者に確認してください。</p>'
            '<div class="dayservice-original" style="white-space:pre-wrap">' + text + '</div>' +
            source_link + '</article></main></body></html>'
        )
        target.write_text(page, encoding="utf-8")
    handbook_path = ROOT / "data" / "handbook.generated.json"
    service_map = {}
    if handbook_path.is_file():
        handbook = json.loads(handbook_path.read_text(encoding="utf-8"))
        for service in handbook.get("services", []):
            sid, label = service.get("service_id"), service.get("label")
            if isinstance(sid, str) and isinstance(label, str):
                service_map[sid] = label
    ids = sorted({service for row in browse_rows for service in row["services"]})
    services = [{"id": sid, "label": service_map.get(sid, sid)} for sid in ids]
    browse = {"docs": [{"id": k, "title": v, "category": document_category[k]}
                        for k, v in document_map.items()],
              "records": browse_rows, "services": services}
    legislation_root = out / "legislation"
    (legislation_root / "records.json").write_text(
        json.dumps(browse, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    script = ROOT / "experiments" / "github-pages-legislation-app.mjs"
    if not script.is_file() or script.is_symlink():
        raise RuntimeError("Missing private static legislation application")
    shutil.copyfile(script, legislation_root / "app.mjs")
    browser = """<!doctype html><html lang="ja"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex,nofollow,noarchive">
<title>法令等を条文順で読む — 静的移行検証</title>
<link rel="stylesheet" href="../databases/search/style.css">
<style>main{max-width:920px;margin:auto;padding:1.5rem}form{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:12px}label{display:grid;gap:5px}input,select,button{padding:9px;font:inherit;min-height:44px}.legal-row{border-top:1px solid #bbb;padding:16px 0}.legal-row h2{margin:0;font-size:1.15rem}.excerpt{white-space:pre-wrap;overflow-wrap:anywhere}.source{color:#555}nav{display:flex;gap:12px;align-items:center;justify-content:center}</style>
</head><body><main><p><a href="../index.html">サービス別手引へ戻る</a></p>
<h1>法令等を条文順で読む</h1><p>介護保険法・基準省令・通知・報酬基準をサービス別に絞り込めます。</p>
<p>収載資料には人手確認前の部分があります。準用・読替え・例外・施行日や自治体ごとの取扱いは公式原典で確認してください。</p>
<form id="legal-form"><label>サービス<select id="service"><option value="">すべてのサービス</option></select></label>
<label>資料の種類<select id="category"><option value="">すべての種類</option></select></label>
<label>法令・通知<select id="document"><option value="">すべての法令・通知</option></select></label>
<label>キーワード・条文番号<input id="q" type="search" placeholder="例：人員、第一条"></label>
<button type="submit">絞り込む</button></form>
<p role="status" id="legal-summary">法令資料を読み込んでいます。</p><div id="legal-results"></div>
<nav id="legal-pagination" aria-label="法令一覧のページ送り"></nav>
</main><script type="module" src="./app.mjs"></script></body></html>"""
    (legislation_root / "index.html").write_text(browser, encoding="utf-8")
    (out / "legislation" / "record-index.json").write_text(json.dumps(manifest, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    return {"records": len(records), "bytes": sum(p.stat().st_size for p in dest.glob("*.html"))}


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python scripts/build_github_pages_legislation_pilot.py PRIVATE_DIR")
    print(json.dumps(build(Path(sys.argv[1])), ensure_ascii=False))
