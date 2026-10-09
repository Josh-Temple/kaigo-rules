#!/usr/bin/env python3
"""Read-only external HTTP evidence for the public Kaigo Ops alias.

Unlike the deploy-state verifier, this does not query private APIs, trigger
deployments, advance a marker, or assert any human-device/browser result.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import socket
import sys
import urllib.error
import urllib.parse
import urllib.request

ALIAS = "https://ops-site-pi.vercel.app"
OLD_ROUTES = (
    "/", "/issues/information-search", "/issues/documentation",
    "/issues/training-handover", "/issues/communication-collaboration",
    "/issues/productivity-utilization", "/tools/information-inventory",
    "/tools/documentation-review", "/tools/training-handover-inventory",
    "/tools/communication-review", "/tools/work-time-review",
)
GUIDE = "/guides/medication-incident-sources"
PREVIEW = "/tools/medication-safety-preview"
ROUTES = OLD_ROUTES + (GUIDE, PREVIEW, "/robots.txt", "/sitemap.xml")


class PageFacts(HTMLParser):
    def __init__(self):
        super().__init__()
        self.canonical = []
        self.og_titles = []
        self.ids = set()
        self.external_sources = set()

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if a.get("id"):
            self.ids.add(a["id"])
        if tag == "link" and a.get("rel") == "canonical":
            self.canonical.append(a.get("href", ""))
        if tag == "meta" and a.get("property") == "og:title":
            self.og_titles.append(a.get("content", ""))
        if tag == "a" and a.get("href", "").startswith("https://"):
            host = urllib.parse.urlparse(a["href"]).hostname or ""
            if host in ("www.mhlw.go.jp", "www.pmda.go.jp", "laws.e-gov.go.jp"):
                self.external_sources.add(host)


def check(path, timeout):
    url = ALIAS + path
    row = {"path": path, "requested_url": url, "status": None,
           "content_type": None, "final_url": None, "pass": False}
    req = urllib.request.Request(
        url, headers={"User-Agent": "KaigoOpsReadOnlyPublicProbe/1.0",
                      "Accept": "text/html,application/xml,text/plain",
                      "Cache-Control": "no-cache"})
    try:
        try:
            response = urllib.request.urlopen(req, timeout=timeout)
        except urllib.error.HTTPError as exc:
            response = exc  # A real HTTP 404 is evidence, unlike DNS failure.
        with response:
            row["status"] = response.status
            row["content_type"] = response.headers.get("Content-Type", "")
            row["final_url"] = response.geturl()
            data = response.read(1_000_000)
        body = data.decode("utf-8", errors="replace")
    except (OSError, urllib.error.URLError, TimeoutError):
        row["error"] = "NETWORK_OR_DNS_UNREACHABLE"
        return row

    if path == PREVIEW:
        row["pass"] = row["status"] == 404
    elif path == "/robots.txt":
        row["pass"] = row["status"] == 200 and "sitemap" in body.lower()
    elif path == "/sitemap.xml":
        row["pass"] = row["status"] == 200 and GUIDE in body
    else:
        row["html"] = "<html" in body.lower()
        row["site_shell"] = "介護" in body
        row["pass"] = (row["status"] == 200
                       and "text/html" in row["content_type"].lower()
                       and row["html"] and row["site_shell"])
        if path == GUIDE and row["pass"]:
            scanner = PageFacts()
            scanner.feed(body)
            row["canonical"] = scanner.canonical[:2]
            row["og_title_present"] = bool(scanner.og_titles)
            row["source_anchor_count"] = sum(
                ident.startswith("source-") for ident in scanner.ids)
            row["official_source_hosts"] = sorted(scanner.external_sources)
            row["pass"] = (ALIAS + GUIDE in scanner.canonical
                           and row["og_title_present"]
                           and row["source_anchor_count"] >= 5
                           and len(scanner.external_sources) >= 3)
    return row


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    parser.add_argument("--timeout", type=int, default=12)
    args = parser.parse_args()
    if not 1 <= args.timeout <= 30:
        parser.error("--timeout must be 1..30 seconds")
    try:
        socket.getaddrinfo("ops-site-pi.vercel.app", 443)
        dns_ok = True
    except OSError:
        dns_ok = False
    rows = [check(path, args.timeout) for path in ROUTES]
    report = {"checked_at_utc": datetime.now(timezone.utc).isoformat(),
              "runner": "GitHub Actions" if os.getenv("GITHUB_ACTIONS") else "local",
              "alias": ALIAS, "dns_resolution_success": dns_ok,
              "http_results": rows, "passed": sum(bool(r["pass"]) for r in rows),
              "total": len(rows),
              "http_confirmed": all(r["pass"] for r in rows),
              "limits": ["Does not independently verify Vercel deployment identity or exact SHA",
                         "No native Android, screen-reader, print or human-browser testing",
                         "Does not prove the external official sources are accessible",
                         "No deploy-state update or deploy/promotion operation"]}
    dest = Path(args.output)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n",
                    encoding="utf-8")
    summary = ("Kaigo Ops read-only HTTP probe: "
               + str(report["passed"]) + "/" + str(report["total"]) + " passed; "
               + "HTTP_CONFIRMED" if report["http_confirmed"] else
               "Kaigo Ops read-only HTTP probe: "
               + str(report["passed"]) + "/" + str(report["total"]) + " passed; HTTP_NOT_CONFIRMED")
    print(summary)
    for row in rows:
        print(row["path"], "status=" + str(row["status"]),
              "PASS" if row["pass"] else "NOT_CONFIRMED",
              row.get("error", ""))
    if os.getenv("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as f:
            f.write("## Public HTTP probe (no deployment)\n\n" + summary + "\n\n")
            f.write("| Path | HTTP | Result |\n|---|---:|---|\n")
            for row in rows:
                f.write("| `" + row["path"] + "` | "
                        + str(row["status"] or "DNS/network") + " | "
                        + ("PASS" if row["pass"] else "NOT_CONFIRMED") + " |\n")
            f.write("\nThis is an external HTTP probe, **not** Vercel identity verification, "
                    "native browser validation, or permission to advance deploy-state.\n")
    if not report["http_confirmed"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
