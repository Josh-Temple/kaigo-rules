#!/usr/bin/env python3
"""Prepare a clearly labeled, noindex GitHub Pages public beta.

This does not certify any legal information or make the site a production release.
It intentionally retains the pilot's noindex safety markers.
"""
from __future__ import annotations
import re
import sys
import json
from pathlib import Path

FALSE_PRIVATE = "静的移行の検証版（一般公開していません）"
BETA_LABEL = "Kaigo Rules 試験公開版"
NOTICE = ("試験公開版です。未確認の法令情報や旧サイトへのリンクが含まれます。"
          "制度の現行性・適用条件は必ず国の原典と指定権者に確認してください。")
def site_header(home: str) -> str:
    return (
        '<header style="background:#16263a;color:#fff;border-bottom:3px solid #4078ae">'
        '<div style="box-sizing:border-box;max-width:1050px;margin:0 auto;padding:12px 18px">'
        f'<a href="{home}" style="display:inline-block;padding:6px 0;color:inherit;'
        'font:700 20px/1.5 system-ui,sans-serif;text-decoration:underline;text-underline-offset:.2em">'
        + BETA_LABEL + '</a></div></header>'
        '<aside role="note" aria-label="制度情報の利用上の注意" style="background:#f3f5f7;color:#263443">'
        '<p style="box-sizing:border-box;max-width:1050px;margin:0 auto;padding:10px 18px;'
        'font:normal 14px/1.65 system-ui,sans-serif">' + NOTICE + '</p></aside>'
    )


BODY = re.compile(r"<body(?=[\s>])[^>]*>",re.I)
FALSE_PRIVATE_RE = re.compile(re.escape(FALSE_PRIVATE))

def prepare(root: Path) -> dict:
    if not root.is_dir() or root.is_symlink():
        raise RuntimeError("Invalid beta candidate path")
    files=list(root.rglob("*.html"))
    if len(files) < 9000:
        raise RuntimeError("Incomplete beta export")
    if any(p.is_symlink() for p in files):
        raise RuntimeError("Symlink in beta output")
    changed=0
    private_replaced=0
    noindex_count=0
    for page in files:
        source=page.read_text(encoding="utf-8")
        if 'name="robots" content="noindex' not in source:
            raise RuntimeError("Beta page must remain noindex: "+page.name)
        noindex_count+=1
        content, n=FALSE_PRIVATE_RE.subn(BETA_LABEL,source)
        private_replaced+=n
        # The beta banner is written to every page, including ones with no
        # previous private-preview label.
        depth=len(page.relative_to(root).parts)-1
        home=("../"*depth or "./")+"index.html"
        content, n=BODY.subn(lambda m: m.group(0)+site_header(home),content,count=1)
        if n!=1 or FALSE_PRIVATE in content:
            raise RuntimeError("Cannot visibly identify beta output: "+page.name)
        report = ('<footer style="padding:1rem"><a href="https://github.com/Josh-Temple/kaigo-rules/issues/new">内容の誤り・更新漏れを報告</a>（該当ページのURLをお知らせください。個人情報は記載しないでください。）</footer>')
        content = re.sub(r"</body\s*>", lambda m: report + m.group(0), content, count=1, flags=re.I)
        if content!=source:
            page.write_text(content,encoding="utf-8")
            changed+=1
    return {"html_pages":len(files),"changed":changed,
            "private_labels_replaced":private_replaced,
            "noindex_retained":noindex_count}

if __name__=="__main__":
    if len(sys.argv)!=2:
        raise SystemExit("Usage: prepare_github_pages_beta.py OUTPUT_DIRECTORY")
    print(json.dumps(prepare(Path(sys.argv[1])),ensure_ascii=False))
