#!/usr/bin/env python3
"""Extract Q&A count, page and visible detail links from rendered Next.js HTML."""
from __future__ import annotations

import json
import re
import sys
from html.parser import HTMLParser

VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}


class QaSnapshot(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.depth = 0
        self.summary_depth = None
        self.row_depth = None
        self.pagination_depth = None
        self.summary = []
        self.pagination = []
        self.links = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag not in VOID:
            self.depth += 1
        classes = (attrs.get("class") or "").split()
        if tag == "div" and "qa-search-summary" in classes:
            self.summary_depth = self.depth
        if tag == "section" and "qa-row" in classes:
            self.row_depth = self.depth
        if tag == "nav" and "qa-pagination" in classes:
            self.pagination_depth = self.depth
        href = attrs.get("href") or ""
        if tag == "a" and self.row_depth is not None and href.startswith("/qa/"):
            self.links.append(href)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID:
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        if tag == "div" and self.summary_depth == self.depth:
            self.summary_depth = None
        if tag == "section" and self.row_depth == self.depth:
            self.row_depth = None
        if tag == "nav" and self.pagination_depth == self.depth:
            self.pagination_depth = None
        if tag not in VOID:
            self.depth -= 1

    def handle_data(self, value):
        if self.summary_depth is not None:
            self.summary.append(value)
        if self.pagination_depth is not None:
            self.pagination.append(value)


def extract(text: str) -> dict:
    parser = QaSnapshot()
    parser.feed(text)
    count = re.search(r"([\d,]+)\s*件", "".join(parser.summary))
    if not count:
        raise ValueError("Missing Q&A result count")
    total = int(count.group(1).replace(",", ""))
    pages = max(1, (total + 29) // 30)
    pagination = re.search(r"(\d+)\s*/\s*(\d+)\s*ページ", "".join(parser.pagination))
    page = int(pagination.group(1)) if pagination else 1
    if pagination and int(pagination.group(2)) != pages:
        raise ValueError("Inconsistent Q&A pagination")
    if pages > 1 and not pagination:
        raise ValueError("Missing Q&A pagination")
    return {"total": total, "page": page, "totalPages": pages, "links": parser.links}


if __name__ == "__main__":
    print(json.dumps(extract(sys.stdin.read()), ensure_ascii=False))
