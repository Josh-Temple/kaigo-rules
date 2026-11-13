#!/usr/bin/env python3
"""Replace supported legacy links with existing local destinations.

No fee amounts or legal text are generated here. Unknown links are not silently
rewritten, and the operation refuses to run if the expected pages have changed.
"""
from __future__ import annotations

import html
import posixpath
import re
import sys
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

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
ANCHOR = re.compile(r'(<a\b[^>]*?\bhref=")([^"]+)(")', re.IGNORECASE)
SERVICE = re.compile(r"[a-z0-9-]+")


def rewrite_index_link(match: re.Match, source: Path, root: Path, counts: dict) -> str:
    url = urlsplit(html.unescape(match.group(2)))
    if (url.scheme != "https" or url.netloc != "kaigo-rules.vercel.app" or
            url.path not in {"/rules", "/law"} or url.fragment):
        return match.group(0)
    try:
        params = parse_qs(url.query, keep_blank_values=True, strict_parsing=True, max_num_fields=2)
    except ValueError:
        return match.group(0)
    if set(params) - {"service"} or any(len(v) != 1 for v in params.values()):
        return match.group(0)
    service = params.get("service", [""])[0]
    if service and (not SERVICE.fullmatch(service) or
                    not (root / "services" / service / "index.html").is_file()):
        return match.group(0)
    if "service" in params and not service:
        return match.group(0)
    target = root / "legislation/index.html"
    if target.is_symlink() or not target.is_file():
        raise RuntimeError("Local legislation index is missing or unsafe")
    category = "standards" if url.path == "/rules" else "law"
    query = (("service=" + service + "&") if service else "") + "category=" + category
    relative = posixpath.relpath("legislation/index.html", source.parent.as_posix())
    counts[category] += 1
    return match.group(1) + html.escape(relative + "?" + query, quote=True) + match.group(3)


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
    counts = {"standards": 0, "law": 0}
    for path in root.rglob("*.html"):
        if path.is_symlink():
            raise RuntimeError(f"Symbolic link in site output: {path}")
        before = changes.get(path)
        if before is None:
            before = path.read_text(encoding="utf-8")
        after = ANCHOR.sub(lambda m: rewrite_index_link(m, path.relative_to(root), root, counts), before)
        if after != before:
            changes[path] = after
    # Validate the entire plan before changing any page. The build pipeline
    # subsequently audits all final local links before deploying the artifact.
    for path, after in changes.items():
        path.write_text(after, encoding="utf-8")
    return {"pages_changed": len(changes), "fee_links_changed": sum(map(len, PAGES.values())),
            "index_links_changed": counts}


if __name__ == "__main__":
    import json
    if len(sys.argv) != 2:
        raise SystemExit("Usage: rewrite_public_navigation.py SITE_DIRECTORY")
    print(json.dumps(rewrite(Path(sys.argv[1])), ensure_ascii=False))
