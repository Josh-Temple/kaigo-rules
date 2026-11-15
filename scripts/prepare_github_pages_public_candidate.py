#!/usr/bin/env python3
"""Convert an approved *private* Pages build into a public presentation.

Does not authorize publication: release workflow must independently verify
scope/currentness, exact SHA, link completeness and final audit first.
"""
from __future__ import annotations
import re
import sys
from pathlib import Path

PRIVATE_LABEL = "静的移行の検証版（一般公開していません）"
PUBLIC_LABEL = "介護制度資料の参考閲覧版"
OLD_NOTICE = "現在の本番とは別の試作品です。"
NEW_NOTICE = "資料の確認状況や適用条件に注意してください。"
OLD_INTERACTIVE = "この試作品では印刷・対話操作やサイト内リンクの一部が本番と異なる場合があります。"
NEW_INTERACTIVE = "画面表示・印刷・関連リンクを利用する際は、原典を確認してください。"
ROBOTS = re.compile(r'<meta\s+name="robots"\s+content="noindex[^"]*"\s*/?>', re.I)
OTHER_NOINDEX = re.compile(r'<meta\b[^>]*\bnoindex\b[^>]*>', re.I)


def prepare(root: Path) -> dict:
    if not root.is_dir() or root.is_symlink():
        raise RuntimeError("Missing approved candidate")
    html_files = list(root.rglob("*.html"))
    if not html_files or any(p.is_symlink() for p in html_files):
        raise RuntimeError("Missing or unsafe HTML")
    changes = 0
    banners = 0
    removed_robots = 0
    for page in html_files:
        original = page.read_text(encoding="utf-8")
        text = original.replace(PRIVATE_LABEL, PUBLIC_LABEL)
        text = text.replace(OLD_NOTICE, NEW_NOTICE).replace(OLD_INTERACTIVE, NEW_INTERACTIVE)
        text = text.replace(" — 静的移行検証", " — Kaigo Rules")
        if PRIVATE_LABEL in original:
            banners += 1
        text, count = ROBOTS.subn("", text)
        removed_robots += count
        if OTHER_NOINDEX.search(text) or PRIVATE_LABEL in text or "この試作品では" in text:
            raise RuntimeError("Unreviewed private/noindex marker still present")
        if text != original:
            page.write_text(text, encoding="utf-8")
            changes += 1
    return {"html_pages": len(html_files), "changed": changes,
            "banners_rewritten": banners, "noindex_tags_removed": removed_robots}


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python scripts/prepare_github_pages_public_candidate.py DIRECTORY")
    import json
    print(json.dumps(prepare(Path(sys.argv[1])), ensure_ascii=False))
