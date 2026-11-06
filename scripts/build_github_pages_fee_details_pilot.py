#!/usr/bin/env python3
"""Extract only already-prerendered, publicly routable fee detail articles.

The selected IDs are exactly the existing Next.js generateStaticParams()
projection (direct children of fee.dayservice.root). No source corpus or Next
hydration data enters the output. All legal warnings remain visible. No deploy.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_github_pages_qa_details_pilot as qa
import build_github_pages_information_pilot as info

ROOT = Path(__file__).resolve().parents[1]
PREFIX = "fee.dayservice."
SAFE = re.compile(r"^[a-z0-9]+(?:[.-][a-z0-9]+)*$")


def select_routes():
    records = json.loads((ROOT / "data/remuneration-current-skeleton.json").read_text(encoding="utf-8"))
    if not isinstance(records, list):
        raise RuntimeError("Invalid official fee structure")
    selected = []
    slugs = set()
    for record in records:
        if not isinstance(record, dict) or record.get("parent_id") != "fee.dayservice.root":
            continue
        name = record.get("id")
        title = record.get("title")
        if not isinstance(name, str) or not name.startswith(PREFIX):
            raise RuntimeError("Unexpected fee detail source ID")
        slug = name[len(PREFIX):]
        if not SAFE.fullmatch(slug) or slug in slugs or not isinstance(title, str) or not title:
            raise RuntimeError("Unsafe, missing or duplicate fee detail route")
        slugs.add(slug)
        selected.append((slug, title))
    if not selected:
        raise RuntimeError("No existing public fee detail routes")
    return selected


def add_pages(root: Path) -> dict:
    if not root.is_dir() or root.is_symlink() or root.resolve() == ROOT:
        raise RuntimeError("Invalid private output root")
    if not (ROOT / ".next/BUILD_ID").is_file():
        raise RuntimeError("Existing validated Next.js build is required")
    source = ROOT / ".next/server/app/fees"
    rows = []
    for slug, title in select_routes():
        origin = source / (slug + ".html")
        destination = root / "fees" / slug / "index.html"
        if not origin.is_file() or origin.is_symlink() or destination.exists():
            raise RuntimeError("Missing/duplicate prerendered public fee article: " + slug)
        result, original = qa.render_article(
            origin.read_text(encoding="utf-8"), title,
            info.preserve_original_link, "../../styles.css",
        )
        if not "".join(original.text).strip():
            raise RuntimeError("Missing visible fee detail content: " + slug)
        if "<script" in result.split("<main>", 1)[-1] or "__next" in result:
            raise RuntimeError("Unsafe fee article extract: " + slug)
        destination.parent.mkdir(parents=True, exist_ok=False)
        destination.write_text(result, encoding="utf-8")
        rows.append({
            "slug": slug, "bytes": destination.stat().st_size, "links": len(original.links),
            "visible_text_sha256": hashlib.sha256("".join(original.text).encode("utf-8")).hexdigest(),
        })
    return {"pages": len(rows), "bytes": sum(r["bytes"] for r in rows),
            "source_links": sum(r["links"] for r in rows), "routes": rows}
