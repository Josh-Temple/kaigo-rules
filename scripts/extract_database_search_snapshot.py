#!/usr/bin/env python3
"""Extract only result counts and local result links from rendered DB search."""
from __future__ import annotations

import json
import re
import sys
from html.parser import HTMLParser

LABELS = {
    "介護保険法": "law",
    "基準省令": "ordinance",
    "一単位単価・地域区分": "unitPrice",
    "報酬算定基準（別告示）": "delegated",
    "基準解釈通知": "notice",
    "国Q&A": "qa",
}
PREFIXES = {
    "law": "/law/", "ordinance": "/rules/", "unitPrice": "/fees/unit-price?",
    "delegated": "/fees/criteria?", "notice": "/notices?", "qa": "/qa/",
}
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}


class SearchSnapshot(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.depth = 0
        self.section = None
        self.heading_depth = None
        self.heading = []
        self.results = {}

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag not in VOID:
            self.depth += 1
        if tag == "section" and "section" in attrs.get("class", "").split() and self.section is None:
            self.section = {"depth": self.depth, "seen_heading": False, "group": None, "links": []}
        if not self.section:
            return
        if tag == "h2" and not self.section["seen_heading"]:
            self.section["seen_heading"] = True
            self.heading_depth = self.depth
            self.heading = []
        group = self.section["group"]
        href = attrs.get("href") or ""
        if tag == "a" and group and href.startswith(PREFIXES[group]):
            self.section["links"].append(href)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID:
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        if self.section and tag == "h2" and self.heading_depth == self.depth:
            text = "".join(self.heading).strip()
            group = next((group for label, group in LABELS.items() if text.startswith(label)), None)
            if group:
                match = re.search(r"[(（]\s*([\d,]+)\s*(?:条|件)", text)
                if not match:
                    raise ValueError("Missing result count for " + group)
                self.section["group"] = group
                self.section["count"] = int(match.group(1).replace(",", ""))
            self.heading_depth = None
        if self.section and tag == "section" and self.section["depth"] == self.depth:
            group = self.section["group"]
            if group:
                if group in self.results:
                    raise ValueError("Duplicate search result group")
                self.results[group] = {"count": self.section["count"], "links": self.section["links"]}
            self.section = None
        if tag not in VOID:
            self.depth -= 1

    def handle_data(self, value):
        if self.heading_depth is not None:
            self.heading.append(value)


def extract(text: str) -> dict:
    parser = SearchSnapshot()
    parser.feed(text)
    if set(parser.results) != set(PREFIXES):
        raise ValueError("Search results are missing one or more groups")
    return parser.results


if __name__ == "__main__":
    print(json.dumps(extract(sys.stdin.read()), ensure_ascii=False))
