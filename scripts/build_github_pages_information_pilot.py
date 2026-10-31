#!/usr/bin/env python3
"""Extract a small, explicit set of already-prerendered reader information pages.

Never copy a Next.js hydration payload, preview, or a source data file. This
stays inside the unpublished integration experiment, not a deployable export.
"""
from __future__ import annotations

import hashlib
from pathlib import Path
from urllib.parse import urlsplit

import build_github_pages_qa_details_pilot as qa
import build_github_pages_handbook_pilot as handbook

ROOT = Path(__file__).resolve().parents[1]
PAGES = {
    "start": "利用開始",
    "overview": "介護制度の全体像",
    "guide": "介護制度の使い方ガイド",
}


def preserve_original_link(href: str):
    parts = urlsplit(href)
    if parts.path.startswith("/handbook-preview"):
        raise RuntimeError("Preview link in reader information page")
    if href.startswith("/") and not href.startswith("//"):
        return "https://kaigo-rules.vercel.app" + href
    return handbook.link_target(href)


def add_pages(root: Path) -> dict:
    if not root.is_dir() or root.is_symlink() or root.resolve() == ROOT:
        raise RuntimeError("Invalid unpublished static output")
    source_root = ROOT / ".next/server/app"
    if not (ROOT / ".next/BUILD_ID").is_file():
        raise RuntimeError("Next.js validated build required before extraction")
    output = []
    for route, label in PAGES.items():
        source = source_root / (route + ".html")
        dest = root / route / "index.html"
        if not source.is_file() or source.is_symlink() or dest.exists():
            raise RuntimeError("Missing or duplicate pre-rendered reader page: " + route)
        full_html = source.read_text(encoding="utf-8")
        rendered, original = qa.render_article(
            full_html, label, preserve_original_link, "../styles.css",
        )
        if not original.done or not "".join(original.text).strip() or "<script" in rendered.split("<main>", 1)[-1]:
            raise RuntimeError("Incomplete reader information extract: " + route)
        dest.parent.mkdir(parents=True, exist_ok=False)
        dest.write_text(rendered, encoding="utf-8")
        output.append({
            "route": route, "bytes": dest.stat().st_size,
            "visible_text_sha256": hashlib.sha256("".join(original.text).encode("utf-8")).hexdigest(),
            "source_links": len(original.links),
        })
    return {"pages": len(output), "bytes": sum(row["bytes"] for row in output), "routes": output}
