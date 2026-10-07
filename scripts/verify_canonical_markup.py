#!/usr/bin/env python3
"""Check a rendered page's unique absolute canonical, independent of attribute order."""
from html.parser import HTMLParser
import sys


class CanonicalLinks(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.urls = []

    def handle_starttag(self, tag, attrs):
        if tag != "link":
            return
        values = dict(attrs)
        if "canonical" in (values.get("rel") or "").split():
            self.urls.append(values.get("href") or "")


def canonical_urls(html):
    parser = CanonicalLinks()
    parser.feed(html)
    return parser.urls


def main():
    if len(sys.argv) != 2:
        raise SystemExit("usage: verify_canonical_markup.py EXPECTED_CANONICAL < html")
    # Next.js renders the site-root canonical without a trailing slash.
    expected = sys.argv[1]
    if expected == "https://kaigo-rules.vercel.app/":
        expected = "https://kaigo-rules.vercel.app"
    found = canonical_urls(sys.stdin.read())
    if found != [expected]:
        print(f"Canonical mismatch: expected {[expected]!r}, observed {found!r}", file=sys.stderr)
        return 1
    print(f"Canonical verified: {expected}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
