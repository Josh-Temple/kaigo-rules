#!/usr/bin/env python3
"""Read-only freshness check for the MHLW介護サービスQ&A workbook."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import urllib.parse
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
META_PATH = ROOT / "data" / "qa-corpus-meta.json"


class WorkbookLinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.links: list[dict[str, str]] = []
        self.current_href: str | None = None
        self.current_text: list[str] = []

    def handle_starttag(self, tag: str, attrs) -> None:
        if tag.lower() != "a":
            return
        href = dict(attrs).get("href")
        if href and re.search(r"\.xlsx?(?:$|\?)", href, re.I):
            self.current_href = href
            self.current_text = []

    def handle_data(self, data: str) -> None:
        if self.current_href is not None:
            self.current_text.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "a" and self.current_href is not None:
            self.links.append({
                "href": self.current_href,
                "text": " ".join("".join(self.current_text).split()),
            })
            self.current_href = None
            self.current_text = []


def fetch(url: str) -> bytes:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "kaigo-rules-qa-source-monitor/1.0 (+https://github.com/Josh-Temple/kaigo-rules)"},
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        return response.read()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", help="Optional path for JSON report")
    args = parser.parse_args()

    meta = json.loads(META_PATH.read_text(encoding="utf-8"))
    page_url = meta["source_page"]
    stored_workbook = meta["source_workbook"]
    stored_sha = meta["source_sha256"]

    page_bytes = fetch(page_url)
    page_text = page_bytes.decode("utf-8", errors="replace")
    link_parser = WorkbookLinkParser()
    link_parser.feed(page_text)
    link_parser.close()

    candidates = []
    for link in link_parser.links:
        absolute = urllib.parse.urljoin(page_url, link["href"])
        candidates.append({"url": absolute, "text": link["text"]})

    urls = [item["url"] for item in candidates]
    differences = []

    if not candidates:
        differences.append({
            "field": "source_page",
            "difference": "no_excel_workbook_links_found",
        })
        live_sha = None
    elif stored_workbook not in urls:
        differences.append({
            "field": "source_workbook",
            "difference": "stored_workbook_no_longer_listed_on_source_page",
            "expected": stored_workbook,
            "observed_candidates": candidates,
        })
        live_sha = None
    else:
        workbook_bytes = fetch(stored_workbook)
        live_sha = hashlib.sha256(workbook_bytes).hexdigest()
        if live_sha != stored_sha:
            differences.append({
                "field": "source_sha256",
                "difference": "stored_workbook_content_changed",
                "expected": stored_sha,
                "observed": live_sha,
            })

    # The importer intentionally follows the first Excel link. Detect if that
    # discovery target would now differ, even when the old workbook remains listed.
    discovered_first = candidates[0]["url"] if candidates else None
    if discovered_first and discovered_first != stored_workbook:
        differences.append({
            "field": "source_workbook",
            "difference": "first_discovered_workbook_changed",
            "expected": stored_workbook,
            "observed": discovered_first,
            "observed_anchor_text": candidates[0]["text"],
        })

    result = "PASS" if not differences else "SOURCE_DRIFT_DETECTED"
    report = {
        "format_version": 1,
        "verification_kind": "MHLW_QA_SOURCE_FRESHNESS",
        "result": result,
        "source_page": page_url,
        "stored_workbook": stored_workbook,
        "stored_workbook_sha256": stored_sha,
        "observed_workbook_sha256": live_sha,
        "excel_link_count": len(candidates),
        "excel_links": candidates,
        "differences": differences,
        "safety": {
            "read_only": True,
            "updates_corpus": False,
            "promotes_review_status": False,
        },
    }

    rendered = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    print(rendered, end="")
    if args.report:
        path = Path(args.report)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(rendered, encoding="utf-8")

    return 0 if result == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
