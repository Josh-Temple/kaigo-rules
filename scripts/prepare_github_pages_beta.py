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
BANNER = ('<aside role="note" style="box-sizing:border-box;max-width:100%;'
          'padding:12px 16px;margin:0;background:#fff1c7;color:#222;'
          'font:normal 14px/1.6 system-ui,sans-serif;border-bottom:2px solid #a76c00">'
          '<strong>'+BETA_LABEL+'</strong>：'+NOTICE+'</aside>')
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
        content, n=BODY.subn(lambda m: m.group(0)+BANNER,content,count=1)
        if n!=1 or FALSE_PRIVATE in content:
            raise RuntimeError("Cannot visibly identify beta output: "+page.name)
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
