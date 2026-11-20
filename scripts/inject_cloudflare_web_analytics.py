#!/usr/bin/env python3
"""Attach Cloudflare Web Analytics to generated GitHub Pages HTML.

The Next.js layout's Vercel Analytics component is stripped from the
standalone static site. Run this on the final, verified Pages artifact,
not on Next.js source files. The site token is a public browser tag.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

BEACON_URL = "https://static.cloudflareinsights.com/beacon.min.js"
TOKEN_RE = re.compile(r"[a-f0-9]{32}\Z")
BODY_END_RE = re.compile(r"</body\s*>", re.IGNORECASE)


def snippet(token: str) -> str:
    if not TOKEN_RE.fullmatch(token):
        raise ValueError("Expected a 32-character Cloudflare Web Analytics site token")
    return (
        "<!-- Cloudflare Web Analytics -->\n"
        f'<script type="module" src="{BEACON_URL}" '
        f'data-cf-beacon=\'{{"token":"{token}"}}\'></script>\n'
        "<!-- End Cloudflare Web Analytics -->\n"
    )


def inject(root: Path, token: str, *, check_only: bool = False) -> dict[str, int]:
    tag = snippet(token)
    if not root.is_dir() or root.is_symlink():
        raise RuntimeError("Expected a real generated site directory")
    root = root.resolve(strict=True)
    pages = sorted(root.rglob("*.html"))
    if not pages:
        raise RuntimeError("No generated HTML pages to instrument")

    changed = 0
    existing = 0
    for page in pages:
        if page.is_symlink() or not page.resolve(strict=True).is_relative_to(root):
            raise RuntimeError(f"Unsafe generated page: {page}")
        html = page.read_text(encoding="utf-8")
        beacon_count = html.count(BEACON_URL)
        if beacon_count:
            if beacon_count != 1 or html.count(tag) != 1:
                raise RuntimeError(f"Unknown, duplicate or mismatched analytics tag: {page}")
            existing += 1
            continue
        if check_only:
            raise RuntimeError(f"Analytics tag missing: {page}")
        if "<head" not in html.lower() or "<body" not in html.lower():
            raise RuntimeError(f"Not a complete HTML document: {page}")
        closing_tags = list(BODY_END_RE.finditer(html))
        if len(closing_tags) != 1:
            raise RuntimeError(f"Expected exactly one closing body tag: {page}")
        pos = closing_tags[0].start()
        page.write_text(html[:pos] + "\n" + tag + html[pos:], encoding="utf-8")
        changed += 1

    return {"html_pages": len(pages), "inserted": changed, "already_instrumented": existing}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("site_dir", type=Path, help="Final GitHub Pages artifact directory")
    parser.add_argument("--token", required=True, help="Public Cloudflare site token")
    parser.add_argument("--check", action="store_true", help="Verify only; do not modify pages")
    args = parser.parse_args()
    print(json.dumps(inject(args.site_dir, args.token, check_only=args.check)))


if __name__ == "__main__":
    main()
