#!/usr/bin/env python3
"""Generate a PRIVATE, reviewed-scope Pages candidate, never a release.

No existing pilot files are copied: raw legal/QA/search/handbook content must
never reach this output by a link, JSON, compressed file or static HTML.
Approval records must be independently verified; this script does not grant them.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import html
import json
import re
import tempfile
from pathlib import Path
from urllib.parse import urlsplit

SCHEMA = "kaigo-reviewed-scope-v1"
APPROVED = "APPROVED_FOR_SCOPED_REVIEW"
ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,120}$")
MONTH = re.compile(r"^20\d\d-(0[1-9]|1[0-2])$")
DATE = re.compile(r"^20\d\d-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])$")
OFFICIAL_HOSTS = {"www.mhlw.go.jp", "mhlw.go.jp", "laws.e-gov.go.jp"}
WARNING = "試験用の審査候補です。制度の現行性・適用条件は国の原典と指定権者で確認してください。"
CSS = """body{font:1rem/1.65 system-ui,sans-serif;color:#222;max-width:54rem;margin:auto;padding:1rem}a{color:#12528c}aside{background:#fff1c7;border-left:4px solid #a76c00;padding:1rem}main{min-height:50vh}input,button{font:inherit;min-height:44px}input{width:100%;box-sizing:border-box}article{border-top:1px solid #aaa;padding:1rem 0}.body{white-space:pre-wrap;overflow-wrap:anywhere}nav{display:flex;flex-wrap:wrap;gap:1rem}@media print{nav,form,button{display:none}body{padding:0;font-size:11pt}aside{background:white;border:1px solid #444}}"""
JS = r"""const root=document.querySelector('#results'),status=document.querySelector('#status'),box=document.querySelector('#q'),nav=document.querySelector('#pages');
let all=[]; const size=20;
const state=()=>new URLSearchParams(location.search);
function draw(){const p=state(),q=(p.get('q')||'').trim().toLowerCase(),raw=Number(p.get('page')||1),rows=all.filter(r=>(r.title+' '+r.excerpt).toLowerCase().includes(q));
const pages=Math.max(1,Math.ceil(rows.length/size)),page=Number.isInteger(raw)&&raw>=1?Math.min(raw,pages):1;box.value=p.get('q')||'';
root.replaceChildren();status.textContent=rows.length+'件（'+page+'/'+pages+'ページ）';
for(const r of rows.slice((page-1)*size,page*size)){const a=document.createElement('article'),h=document.createElement('h2'),link=document.createElement('a'),p=document.createElement('p');link.href=r.href;link.textContent=r.title;h.append(link);p.textContent=r.excerpt;a.append(h,p);root.append(a)}
if(!rows.length)root.textContent='該当する資料はありません。';nav.replaceChildren();
for(const [label,target] of [['前へ',page-1],['次へ',page+1]]){const b=document.createElement('button');b.type='button';b.textContent=label;b.disabled=target<1||target>pages;b.onclick=()=>{const s=state();s.set('page',String(target));history.pushState(null,'','?'+s);draw()};nav.append(b)}}
document.querySelector('#search').onsubmit=e=>{e.preventDefault();const p=new URLSearchParams();if(box.value.trim())p.set('q',box.value.trim());p.set('page','1');history.pushState(null,'','?'+p);draw()};
addEventListener('popstate',draw);
fetch('./rows.json',{cache:'no-store'}).then(r=>{if(!r.ok)throw Error('HTTP '+r.status);return r.json()}).then(d=>{if(!Array.isArray(d.rows)||d.rows.some(x=>!x.href||!x.title))throw Error('JSON');all=d.rows;draw()}).catch(()=>{status.textContent='資料を読み込めません。原典を確認してください。';root.replaceChildren();nav.replaceChildren()});"""


def fail(message: str):
    raise RuntimeError(message)


def digest(row: dict) -> str:
    return hashlib.sha256(json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def source_url(value: str) -> str:
    if not isinstance(value, str) or any(ord(c) < 32 for c in value):
        fail("Source URL missing or unsafe")
    parts = urlsplit(value)
    if parts.scheme != "https" or parts.hostname not in OFFICIAL_HOSTS or parts.username or parts.password or parts.port:
        fail("Unverified official source URL")
    return value


def page(title: str, content: str, back: str, stylesheet: str) -> str:
    esc = lambda value: html.escape(value, quote=True)
    return (f'<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<meta name="robots" content="noindex,nofollow,noarchive"><title>{esc(title)} — 審査候補</title>'
            f'<link rel="stylesheet" href="{stylesheet}"></head><body><aside role="note"><strong>Kaigo Rules 試験用</strong>：{WARNING}</aside>'
            f'<nav><a href="{back}">資料を探す</a></nav><main>{content}</main></body></html>')


def read(path: Path):
    if not path.is_file() or path.is_symlink():
        fail("Input file missing or symlink")
    return json.loads(path.read_text(encoding="utf-8"))


def build(manifest_path: Path, legal_path: Path, qa_path: Path, qa_meta_path: Path, output: Path) -> dict:
    manifest, legal, qa, qa_meta = [read(p) for p in (manifest_path, legal_path, qa_path, qa_meta_path)]
    if not isinstance(manifest, dict) or manifest.get("schema") != SCHEMA or manifest.get("purpose") != "PRIVATE_ACCEPTANCE_ONLY":
        fail("Invalid or unapproved manifest schema")
    approvals = manifest.get("approvals")
    if not isinstance(approvals, list) or not approvals:
        fail("Empty approval set; no candidate can be generated")
    if not isinstance(legal, dict) or not isinstance(legal.get("documents"), list) or not isinstance(legal.get("records"), list):
        fail("Invalid legal corpus")
    if not isinstance(qa, list) or not isinstance(qa_meta, dict):
        fail("Invalid Q&A corpus")
    docs, legal_rows, qa_rows = {}, {}, {}
    for doc in legal["documents"]:
        if not isinstance(doc, dict) or not isinstance(doc.get("id"), str) or not isinstance(doc.get("title"), str) or doc["id"] in docs:
            fail("Missing or duplicate legal document")
        docs[doc["id"]] = doc
    for kind, values, target in (("legal", legal["records"], legal_rows), ("qa", qa, qa_rows)):
        for row in values:
            if not isinstance(row, dict) or not isinstance(row.get("id"), str) or row["id"] in target:
                fail("Missing or duplicate source ID: " + kind)
            target[row["id"]] = row
    approved = []
    seen = set()
    for entry in approvals:
        if not isinstance(entry, dict) or entry.get("kind") not in {"legal", "qa"}:
            fail("Unknown approval kind")
        kind, key = entry["kind"], entry.get("id")
        if not isinstance(key, str) or not (ID.fullmatch(key) if kind == "qa" else 1 <= len(key) <= 2048 and not any(ord(c) < 32 or ord(c) == 127 for c in key)) or (kind, key) in seen:
            fail("Invalid or duplicate approval ID")
        seen.add((kind, key))
        if entry.get("state") != APPROVED or entry.get("publish_approved") is not True:
            fail("Candidate/unreviewed entries may not become approved")
        for name in ("approved_by", "approval_reference", "evidence_reference"):
            if not isinstance(entry.get(name), str) or len(entry[name].strip()) < 6:
                fail("Missing independently reviewable approval evidence")
        if not isinstance(entry.get("approved_at"), str) or not DATE.fullmatch(entry["approved_at"]):
            fail("Missing approval date")
        start, end = entry.get("period_start"), entry.get("period_end")
        if not isinstance(start, str) or not isinstance(end, str) or not MONTH.fullmatch(start) or not MONTH.fullmatch(end) or start > end:
            fail("Unknown or invalid applicable months")
        row = (legal_rows if kind == "legal" else qa_rows).get(key)
        if row is None or entry.get("row_sha256") != digest(row):
            fail("Missing or changed source row")
        if row.get("period_start") != start or row.get("period_end") != end:
            fail("Source and approval period mismatch or source period unknown")
        url = source_url(entry.get("source_url"))
        if kind == "legal":
            if row.get("state") != "REVIEWED_CURRENT" or row.get("document_id") not in docs:
                fail("Legal row currentness or document unverified")
            if entry.get("document_id") != row["document_id"] or source_url(row.get("url")) != url:
                fail("Legal document or official source mismatch")
            if not isinstance(row.get("service_ids"), list) or not row["service_ids"] or sorted(row["service_ids"]) != sorted(entry.get("service_ids", [])):
                fail("Legal service applicability mismatch")
            content = row.get("text")
            title = row.get("label") or row.get("title")
        else:
            if qa_meta.get("review_status") != "REVIEWED_SCOPE_ONLY" or row.get("review_state") != "REVIEWED_CURRENT":
                fail("Q&A currentness unreviewed")
            if entry.get("service_code") != row.get("service_code") or source_url(qa_meta.get("source_workbook")) != url:
                fail("Q&A service or official workbook mismatch")
            if not isinstance(row.get("issued_source"), str) or not row["issued_source"].strip():
                fail("Q&A original issue reference absent")
            title = row.get("question")
            content = "問：" + str(row.get("question", "")) + "\n\n答：" + str(row.get("answer", ""))
        if not isinstance(content, str) or not content.strip() or not isinstance(title, str) or not title.strip():
            fail("Missing reviewed display text")
        approved.append((kind, key, title, content, url, start, end))
    if output.exists() or output.is_symlink() or not output.parent.is_dir() or output.parent.is_symlink():
        fail("Output must be a new, non-symlink private directory")
    if not output.parent.resolve().is_relative_to(Path(tempfile.gettempdir()).resolve()):
        fail("Candidate must remain under the temporary directory")
    output.mkdir()
    rows, generated = [], set()
    for kind, key, title, content, url, start, end in approved:
        if kind == "qa":
            rel = Path("qa") / key / "index.html"
        else:
            rel = Path("legislation") / "record" / (hashlib.sha256(key.encode()).hexdigest() + ".html")
        href = "../../search/index.html" if kind == "qa" else "../../search/index.html"
        body = (f'<article><h1>{html.escape(title)}</h1><p>適用確認期間：{start}～{end}</p>'
                f'<div class="body">{html.escape(content)}</div><p><a href="{html.escape(url, quote=True)}" rel="noopener noreferrer">国の原典を開く</a></p></article>')
        file = output / rel
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_text(page(title, body, href, "../../style.css"), encoding="utf-8")
        generated.add(rel.as_posix())
        rows.append({"id": key, "kind": kind, "title": title, "excerpt": content[:180],
                     "href": "../" + rel.as_posix(), "period_start": start, "period_end": end})
    (output / "style.css").write_text(CSS, encoding="utf-8")
    root = output / "index.html"
    root.write_text(page("承認範囲の資料", '<h1>審査候補の資料一覧</h1><p><a href="./search/index.html">資料を検索する</a></p>', "./search/index.html", "./style.css"), encoding="utf-8")
    search = output / "search"
    search.mkdir()
    form = '<h1>承認範囲の資料検索</h1><form id="search"><label for="q">キーワード</label><input id="q" type="search"><button>検索</button></form><p role="status" id="status">読込中</p><div id="results"></div><nav id="pages" aria-label="ページ送り"></nav><script type="module" src="./app.mjs"></script>'
    (search / "index.html").write_text(page("資料検索", form, "../index.html", "../style.css"), encoding="utf-8")
    (search / "app.mjs").write_text(JS, encoding="utf-8")
    packed = json.dumps({"rows": rows}, ensure_ascii=False, separators=(",", ":")).encode()
    (search / "rows.json").write_bytes(packed)
    (search / "rows.json.gz").write_bytes(gzip.compress(packed, mtime=0))
    # Self-audit: exact projection, unique destinations, no other inherited files.
    files = {p.relative_to(output).as_posix() for p in output.rglob("*") if p.is_file()}
    expected = generated | {"index.html", "style.css", "search/index.html", "search/app.mjs", "search/rows.json", "search/rows.json.gz"}
    if files != expected or len(rows) != len(seen) or gzip.decompress((search / "rows.json.gz").read_bytes()) != packed:
        fail("Candidate files, approved IDs or compressed search do not match")
    for file in output.rglob("*.html"):
        rendered = file.read_text(encoding="utf-8")
        if 'name="robots" content="noindex' not in rendered or WARNING not in rendered:
            fail("Missing noindex or review warning")
    return {"status": "PRIVATE_REVIEW_CANDIDATE_NOT_RELEASED", "records": len(rows),
            "legal": sum(k == "legal" for k, *_ in approved), "qa": sum(k == "qa" for k, *_ in approved),
            "files": len(files), "html": len(generated) + 2,
            "bytes": sum(p.stat().st_size for p in output.rglob("*") if p.is_file()),
            "approved_ids_sha256": hashlib.sha256(json.dumps(sorted(seen)).encode()).hexdigest(),
            "legacy_vercel_urls": 0, "deploy_approved": False}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--approvals", required=True, type=Path)
    p.add_argument("--legal", required=True, type=Path)
    p.add_argument("--qa", required=True, type=Path)
    p.add_argument("--qa-meta", required=True, type=Path)
    p.add_argument("--private-output", required=True, type=Path)
    a = p.parse_args()
    print(json.dumps(build(a.approvals, a.legal, a.qa, a.qa_meta, a.private_output), ensure_ascii=False))


if __name__ == "__main__":
    main()
