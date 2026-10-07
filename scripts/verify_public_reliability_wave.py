#!/usr/bin/env python3
"""Black-box regression gate for the Kaigo Rules public reliability wave.

Run against a built local Next.js server or production. This checks deployed
HTTP behavior, not merely source-code strings. An exact expected commit SHA
is mandatory to avoid treating an unrelated deployment as verified.

The test does not establish human review, legal currentness, or browser layout.
"""
from __future__ import annotations

import argparse
from html.parser import HTMLParser
import json
from pathlib import Path
import sys
from urllib.error import HTTPError
from urllib.parse import quote, urlencode, urlparse
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET

CANONICAL_ORIGIN = "https://kaigo-rules.vercel.app"
UNIT_PRICE_FAMILY = "unit_price_regional_classification"
MAIN_ROUTES = ("/", "/databases", "/services", "/law", "/rules",
               "/notices", "/qa", "/fees/unit-price")


class PageHead(HTMLParser):
    """Extract DOM-head metadata regardless of HTML attribute order."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.in_head = False
        self.in_title = False
        self.title = ""
        self.canonical: list[str] = []
        self.description: list[str] = []
        self.robots: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if tag == "head":
            self.in_head = True
        # Next.js may stream metadata outside the initial head markup.
        # Validate parsed metadata tags independent of location/attribute order.
        if tag == "title":
            self.in_title = True
        elif tag == "link" and "canonical" in (values.get("rel") or "").split():
            self.canonical.append(values.get("href") or "")
        elif tag == "meta" and values.get("name") == "description":
            self.description.append(values.get("content") or "")
        elif tag == "meta" and values.get("name") == "robots":
            self.robots.append(values.get("content") or "")

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self.in_title = False
        elif tag == "head":
            self.in_head = False

    def handle_data(self, data: str) -> None:
        if self.in_title:
            self.title += data


def extract_head(html: str) -> PageHead:
    head = PageHead()
    head.feed(html)
    return head


def sitemap_urls(xml: str) -> list[str]:
    root = ET.fromstring(xml)
    return [(item.text or "").strip() for item in root.findall(".//{*}loc")]


def public_unit_price_rows(payload: dict) -> list[dict]:
    sources = payload.get("sources")
    if not isinstance(sources, list):
        raise AssertionError("source API must return a sources array")
    matching = [s for s in sources if s.get("source_family") == UNIT_PRICE_FAMILY]
    if len(matching) != 1:
        raise AssertionError("expected exactly one published unit-price source")
    items = matching[0].get("items")
    if not isinstance(items, list) or not items:
        raise AssertionError("published unit-price source has no items")
    for row in items:
        body = row.get("item_body") or {}
        if not body.get("region_class"):
            raise AssertionError("API item lacks region_class")
        yen = body.get("unit_price_yen")
        ratio = body.get("ratio_per_thousand")
        if (isinstance(yen, bool) or not isinstance(yen, (int, float))
                or yen <= 0 or isinstance(ratio, bool)
                or not isinstance(ratio, (int, float)) or ratio <= 0):
            raise AssertionError("API unit-price or ratio is invalid")
        if not row.get("currentness_statement"):
            raise AssertionError("API item lacks currentness statement")
    return items


def published_unit_price_service_ids() -> list[str]:
    """Use the exact deployed revision's allowlist, not old conversation counts."""
    root = Path(__file__).resolve().parents[1]
    allowlist = json.loads(
        (root / "data/bounded-publication-allowlist.json").read_text(
            encoding="utf-8"
        )
    )
    ids = sorted({
        row["service_id"]
        for row in allowlist.get("publication_cell_allowlist", [])
        if row.get("source_family") == UNIT_PRICE_FAMILY
        and isinstance(row.get("service_id"), str)
    })
    if not ids:
        raise AssertionError("no allowed unit-price services in this revision")
    return ids


class PublicReliabilityProbe:
    def __init__(self, base_url: str, expected_sha: str,
                 service_ids: tuple[str, ...] = ("dayservice", "homevisit")):
        self.base_url = base_url.rstrip("/")
        self.expected_sha = expected_sha
        self.service_ids = service_ids
        self.results: list[dict] = []

    def get(self, path: str) -> tuple[int, str]:
        request = Request(self.base_url + path, headers={
            "Accept": "text/html,application/json,application/xml,text/plain",
            "User-Agent": "KaigoRulesPublicRegression/1.0",
        })
        try:
            with urlopen(request, timeout=25) as response:
                return response.status, response.read().decode("utf-8")
        except HTTPError as exc:
            return exc.code, exc.read().decode("utf-8", errors="replace")

    def require(self, path: str, status: int = 200) -> str:
        actual, body = self.get(path)
        if actual != status:
            raise AssertionError(f"{path}: HTTP {actual}, expected {status}")
        return body

    def check(self, name: str, callback) -> None:
        try:
            callback()
        except Exception as exc:
            self.results.append({"check": name, "status": "FAIL", "detail": str(exc)})
        else:
            self.results.append({"check": name, "status": "PASS"})

    def verify_version(self) -> None:
        payload = json.loads(self.require("/api/version"))
        if payload.get("service") != "kaigo-rules":
            raise AssertionError("unexpected API service identity")
        if payload.get("commit_sha") != self.expected_sha:
            raise AssertionError(
                f"production commit mismatch: expected {self.expected_sha}, "
                f"got {payload.get('commit_sha')}"
            )

    def verify_urls(self) -> None:
        titles = []
        for path in MAIN_ROUTES:
            html = self.require(path)
            head = extract_head(html)
            expected = CANONICAL_ORIGIN + path
            if head.canonical != [expected]:
                raise AssertionError(f"{path}: canonical {head.canonical}, expected {expected}")
            if not head.title.strip() or len(head.description) != 1 or not head.description[0]:
                raise AssertionError(f"{path}: title/description missing or duplicated")
            titles.append(head.title)
        if len(set(titles)) != len(titles):
            raise AssertionError("duplicate titles among principal public pages")
        for path in ("/databases/search?q=BCP", "/search?q=BCP"):
            head = extract_head(self.require(path))
            if not any("noindex" in item.lower() for item in head.robots):
                raise AssertionError(f"{path}: noindex missing")
        self.require("/__wave_d_missing_page__", status=404)

    def verify_discovery(self) -> None:
        robots = self.require("/robots.txt")
        if f"Sitemap: {CANONICAL_ORIGIN}/sitemap.xml" not in robots:
            raise AssertionError("robots.txt does not reference canonical sitemap")
        urls = sitemap_urls(self.require("/sitemap.xml"))
        if len(urls) != len(set(urls)):
            raise AssertionError("duplicate sitemap URLs")
        for path in ("/", "/databases", "/services", "/law", "/rules", "/notices", "/qa"):
            if CANONICAL_ORIGIN + path not in urls:
                raise AssertionError(f"sitemap omits {path}")
        if not urls or any(urlparse(u).scheme != "https"
                           or not u.startswith(CANONICAL_ORIGIN + "/")
                           or urlparse(u).query or urlparse(u).fragment
                           for u in urls):
            raise AssertionError("sitemap contains unsafe/noncanonical URL")
        if any("/api/" in url or "/search" in url for url in urls):
            raise AssertionError("sitemap exposes API/search-result pages")

    def verify_unit_price(self, service_id: str) -> None:
        qs = urlencode({"source_family": UNIT_PRICE_FAMILY})
        payload = json.loads(self.require(
            f"/api/context/services/{quote(service_id)}/sources?{qs}"
        ))
        if payload.get("service", {}).get("id") != service_id:
            raise AssertionError("API returned wrong service")
        items = public_unit_price_rows(payload)
        page = self.require(f"/fees/unit-price?{urlencode({'service': service_id, 'q': '地域区分'})}")
        results = self.require(f"/databases/search?{urlencode({'service': service_id, 'q': '地域区分'})}")
        if "現在公開している範囲では一致しませんでした" in page:
            raise AssertionError("published region-class search returned no matches")
        if "一単位単価・地域区分" not in results:
            raise AssertionError("global search omitted unit-price result group")
        if len(items) != 8:
            raise AssertionError(f"unexpected published rate count for {service_id}: {len(items)}")
        for item in items:
            body = item["item_body"]
            region = str(body["region_class"])
            formatted_yen = f"{body['unit_price_yen']:.2f}円"
            if region not in page or formatted_yen not in page:
                raise AssertionError(f"{service_id}/{region}: API rate absent from detail page")
            # Global search intentionally summarizes only the first three
            # matching classes per service; the detail page holds all eight.
            if item in items[:3] and region not in results:
                raise AssertionError(f"{service_id}/{region}: missing from global search")
        if "人手確認が完了していない" not in page:
            raise AssertionError("municipal assignment human-review warning missing")

    def verify_unpublished_and_no_match(self) -> None:
        self.require("/api/context/services/__wave_d_missing__/sources"
                     f"?source_family={UNIT_PRICE_FAMILY}", status=404)
        unpub = self.require("/fees/unit-price?service=__wave_d_missing__")
        if "このサービスの単価は現在公開していません" not in unpub:
            raise AssertionError("unpublished service is not explicitly distinguished")
        no_match = self.require("/fees/unit-price?service=homevisit&q=__wave_d_no_match__")
        if "現在公開している範囲では一致しませんでした" not in no_match:
            raise AssertionError("no-match case is not explicitly distinguished")

    def run(self) -> dict:
        self.check("exact_deployed_commit", self.verify_version)
        self.check("canonical_metadata_and_http_routes", self.verify_urls)
        self.check("robots_sitemap", self.verify_discovery)
        for service_id in self.service_ids:
            self.check(f"unit_price_api_vs_html_{service_id}",
                       lambda sid=service_id: self.verify_unit_price(sid))
        self.check("unpublished_vs_no_match", self.verify_unpublished_and_no_match)
        passed = sum(row["status"] == "PASS" for row in self.results)
        return {
            "status": "PASS" if passed == len(self.results) else "FAIL",
            "base_url": self.base_url,
            "expected_sha": self.expected_sha,
            "unit_price_services_checked": len(self.service_ids),
            "passed": passed,
            "total": len(self.results),
            "checks": self.results,
            "not_verified": ["mobile/browser E2E", "legal currentness",
                             "human review", "deploy-hook acceptance"],
        }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", required=True)
    parser.add_argument("--expected-sha", required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    ids = tuple(published_unit_price_service_ids())
    report = PublicReliabilityProbe(args.base_url, args.expected_sha, ids).run()
    output = json.dumps(report, ensure_ascii=False, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(output + "\n", encoding="utf-8")
    print(output)
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
