#!/usr/bin/env python3
"""Inventory remaining production-origin URLs in a generated GitHub Pages site.

Read-only. No replacement or publication is performed. Runtime-created URLs
in JavaScript and CSS are outside the scope of this HTML-attribute audit.
"""
from __future__ import annotations

import argparse
from collections import Counter
from html.parser import HTMLParser
import json
from pathlib import Path
from urllib.parse import urlsplit

LEGACY_HOST = "kaigo-rules.vercel.app"
URL_ATTRIBUTES = {"href", "src", "action"}


def route_group(path: str) -> str:
    segments = [part for part in path.strip("/").split("/") if part]
    if not segments or segments == ["index.html"]:
        return "/"
    if segments[:2] == ["databases", "search"]:
        return "/databases/search"
    return "/" + segments[0]


class UrlAttributes(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.urls: list[tuple[str, str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        for name, value in attrs:
            if name in URL_ATTRIBUTES and value:
                self.urls.append((name, value))

    handle_startendtag = handle_starttag


def audit(root: Path) -> dict:
    if not root.is_dir() or root.is_symlink():
        raise ValueError("Missing or unsafe generated-site directory")
    pages = sorted(root.rglob("*.html"))
    if not pages:
        raise ValueError("No generated HTML pages found")
    if any(page.is_symlink() or not page.is_file() for page in pages):
        raise ValueError("Unsafe HTML file in generated site")

    source_counts: Counter[str] = Counter()
    destination_counts: Counter[str] = Counter()
    pairs: Counter[tuple[str, str, str]] = Counter()
    samples: list[dict] = []
    total = 0
    for page in pages:
        parser = UrlAttributes()
        parser.feed(page.read_text(encoding="utf-8"))
        relative_path = page.relative_to(root).as_posix()
        source = route_group(relative_path)
        for attribute, value in parser.urls:
            try:
                parsed = urlsplit(value)
                if parsed.scheme not in ("http", "https") or parsed.hostname != LEGACY_HOST:
                    continue
            except ValueError:
                continue
            target = route_group(parsed.path)
            total += 1
            source_counts[source] += 1
            destination_counts[target] += 1
            pairs[(source, target, attribute)] += 1
            if len(samples) < 25:
                samples.append({"source": relative_path, "attribute": attribute, "href": value})

    return {
        "html_pages_scanned": len(pages),
        "remaining_legacy_urls": total,
        "by_source_route": dict(sorted(source_counts.items())),
        "by_target_route": dict(sorted(destination_counts.items())),
        "by_route_pair": [
            {"source": src, "target": dst, "attribute": attr, "count": count}
            for (src, dst, attr), count in sorted(pairs.items())
        ],
        "samples": samples,
        "coverage": "Generated HTML URL attributes (href/src/action) only; "
                    "runtime JavaScript and CSS URL construction NOT_VERIFIED",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("site", type=Path, help="Built static site root")
    parser.add_argument("--output", type=Path, help="Write JSON audit at this path")
    parser.add_argument("--require-zero", action="store_true", help="Fail if any legacy URL remains")
    args = parser.parse_args()
    report = audit(args.site)
    payload = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8")
    else:
        print(payload, end="")
    return 1 if args.require_zero and report["remaining_legacy_urls"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
