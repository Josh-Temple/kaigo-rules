#!/usr/bin/env python3
"""Read-only, numeric migration audit of the *unpublished* GitHub Pages pilot.

A passing audit never authorizes deployment: legal/currentness, publication-scope,
interactive route parity, and independent Android review remain separate gates.
Never upload site content or lists of source URLs as a workflow artifact.
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

PAGES_BUDGET_BYTES = 1_000_000_000
PRODUCTION_HOST = "kaigo-rules.vercel.app"
REQUIRED = (
    "index.html", "services/dayservice/index.html", "databases/search/index.html",
    "databases/search/qa.html", "databases/search/global.json",
)
BLOCKED_PARTS = {".git", ".github", ".next", "node_modules", "private", "handbook-preview", "data"}


class HtmlReferences(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.refs: list[str] = []

    def handle_starttag(self, tag, attrs):
        fields = dict(attrs)
        if tag == "a" and fields.get("href") is not None:
            self.refs.append(fields["href"])
        elif tag in {"link", "script", "img"}:
            value = fields.get("href") if tag == "link" else fields.get("src")
            if value is not None:
                self.refs.append(value)


def destination_category(href: str) -> str:
    try:
        parts = urlsplit(href)
        return (unquote(parts.path).strip("/").split("/", 1)[0] or "home")[:48]
    except ValueError:
        return "invalid"


def inspect(root: Path) -> dict:
    if not root.is_dir() or root.is_symlink():
        raise RuntimeError("Expected an existing, non-symlink unpublished pilot directory")
    root = root.resolve(strict=True)
    entries = list(root.rglob("*"))
    if any(entry.is_symlink() for entry in entries):
        raise RuntimeError("Symlink in static output")
    files = [entry for entry in entries if entry.is_file()]
    if any(BLOCKED_PARTS.intersection(file.relative_to(root).parts) for file in files):
        raise RuntimeError("Blocked raw-data, preview, or repository directory in static output")
    if any(file.name.startswith(".env") for file in files):
        raise RuntimeError("Environment file in static output")
    if any(not (root / name).is_file() for name in REQUIRED):
        raise RuntimeError("Missing required pilot entry or manifest")
    total = sum(p.stat().st_size for p in files)
    if total > PAGES_BUDGET_BYTES:
        raise RuntimeError("Published output exceeds 1,000,000,000-byte review budget")

    refs = Counter()
    fallbacks = Counter()
    missing_local = Counter()
    for page in (p for p in files if p.suffix.lower() == ".html"):
        parser = HtmlReferences()
        parser.feed(page.read_text(encoding="utf-8"))
        for href in parser.refs:
            refs["total"] += 1
            if not href or href.startswith("#"):
                continue
            try:
                parts = urlsplit(href)
            except ValueError:
                refs["invalid_url"] += 1
                continue
            if parts.netloc or parts.scheme:
                if parts.scheme in {"http", "https"} and parts.hostname == PRODUCTION_HOST:
                    fallbacks[destination_category(href)] += 1
                else:
                    refs["other_external"] += 1
                continue
            if href.startswith("//"):
                refs["scheme_relative"] += 1
                continue
            if parts.path.startswith("/"):
                # Project Pages is hosted under /kaigo-rules/, not domain root.
                refs["root_relative"] += 1
                continue
            raw_path = unquote(parts.path)
            if "\" in raw_path or "\x00" in raw_path:
                refs["unsafe_local"] += 1
                continue
            if not raw_path:
                continue
            target = (page.parent / raw_path).resolve()
            if not target.is_relative_to(root) or not target.is_file():
                missing_local[destination_category(raw_path)] += 1
            else:
                refs["local_resolved"] += 1

    groups = Counter()
    global_index = json.loads((root / "databases/search/global.json").read_text(encoding="utf-8"))
    if not isinstance(global_index, dict):
        raise RuntimeError("Invalid global search manifest")
    for category, rows in global_index.items():
        if not isinstance(rows, list):
            raise RuntimeError("Invalid global search group")
        groups[category] = len(rows)

    javascript = [p for p in files if p.suffix in {".js", ".mjs"}]
    js_fallback_files = sum(PRODUCTION_HOST in p.read_text(encoding="utf-8") for p in javascript)
    blocked = {
        "production_fallback_links": sum(fallbacks.values()),
        "root_relative_links": refs["root_relative"],
        "missing_local_links": sum(missing_local.values()),
        "unsafe_or_invalid_links": refs["invalid_url"] + refs["scheme_relative"] + refs["unsafe_local"],
        "javascript_references_to_production": js_fallback_files,
    }
    return {
        "status": "HOLD_NO_DEPLOY",
        "reason": "Incomplete route, scope, currentness, and independent acceptance gates; this is a private pilot",
        "file_count": len(files),
        "html_count": sum(p.suffix.lower() == ".html" for p in files),
        "total_bytes": total,
        "pages_budget_bytes": PAGES_BUDGET_BYTES,
        "html_links_inspected": refs["total"],
        "local_links_resolved": refs["local_resolved"],
        "external_official_or_other_links": refs["other_external"],
        "blockers": blocked,
        "production_fallback_by_section": dict(sorted(fallbacks.items())),
        "missing_local_by_section": dict(sorted(missing_local.items())),
        "global_search_rows_by_group": dict(sorted(groups.items())),
    }


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python scripts/audit_github_pages_migration_readiness.py PRIVATE_DIR")
    print(json.dumps(inspect(Path(sys.argv[1])), ensure_ascii=False, sort_keys=True))
