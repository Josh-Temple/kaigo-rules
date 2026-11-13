#!/usr/bin/env python3
"""Replace specific legacy fee-page links with existing local destinations.

No fee amounts or legal text are generated here. Unknown links are not silently
rewritten, and the operation refuses to run if the expected pages have changed.
"""
from __future__ import annotations

import html
import posixpath
import sys
from pathlib import Path
from urllib.parse import urlsplit

ORIGIN = "https://kaigo-rules.vercel.app"
QUERY = "q=%E5%9C%B0%E5%9F%9F%E5%8C%BA%E5%88%86"
COMMON = [
    ("/rules?service=dayservice", "基準DB", "legislation/index.html?service=dayservice&category=standards", "基準DB"),
    ("/notices?service=dayservice", "通知DB", "legislation/index.html?service=dayservice&category=notices", "通知DB"),
    ("/fees/unit-price", "単価・地域区分", f"databases/search/index.html?{QUERY}", "地域区分の資料検索"),
]
PAGES = {
    "fees/index.html": COMMON + [
        ("/fees/criteria", "告示27号・95号の構造化データを見る →", "legislation/index.html?category=criteria", "告示の関連資料を探す（第27号・第95号など） →"),
        ("/fees/unit-price", "通所介護の一単位単価を見る →", f"databases/search/index.html?{QUERY}", "地域区分の関連資料を検索（一単位単価表ではありません） →"),
    ],
    "fees/guidance/index.html": COMMON + [
        ("/fees/root", "通所介護費", "fees/index.html", "通所介護の報酬一覧"),
    ],
}


def rewrite(root: Path) -> dict:
    if root.is_symlink():
        raise RuntimeError("Site root must not be a symbolic link")
    root = root.resolve(strict=True)
    if not root.is_dir():
        raise RuntimeError("Site root is not a directory")
    changes = {}
    for source, links in PAGES.items():
        path = root / source
        if path.is_symlink() or not path.is_file():
            raise RuntimeError(f"Expected fee page is missing or unsafe: {source}")
        before = path.read_text(encoding="utf-8")
        after = before
        for old_path, old_label, target, label in links:
            target_parts = urlsplit(target)
            target_path = root / target_parts.path
            if target_path.is_symlink() or not target_path.is_file() or not target_path.resolve().is_relative_to(root):
                raise RuntimeError(f"Local fee navigation target missing or unsafe: {target_parts.path}")
            old_anchor = f'<a href="{ORIGIN}{old_path}">{old_label}</a>'
            if after.count(old_anchor) != 1:
                raise RuntimeError(f"Expected legacy fee link changed or is duplicated: {source}: {old_path}")
            relative = posixpath.relpath(target_parts.path, posixpath.dirname(source))
            href = relative + ("?" + target_parts.query if target_parts.query else "")
            new_anchor = f'<a href="{html.escape(href, quote=True)}">{html.escape(label)}</a>'
            after = after.replace(old_anchor, new_anchor, 1)
        if f'href="{ORIGIN}/' in after:
            raise RuntimeError(f"An unrecognized legacy link remains on {source}")
        changes[path] = after
    # Validate both pages and all destinations before changing either one.
    for path, after in changes.items():
        path.write_text(after, encoding="utf-8")
    return {"pages_changed": len(changes), "links_changed": sum(map(len, PAGES.values()))}


if __name__ == "__main__":
    import json
    if len(sys.argv) != 2:
        raise SystemExit("Usage: rewrite_fee_navigation.py SITE_DIRECTORY")
    print(json.dumps(rewrite(Path(sys.argv[1])), ensure_ascii=False))
