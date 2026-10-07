"""Synthetic, offline coverage for the public reliability black-box gate.

The real HTTP check must still run against an exact deployed commit.
"""
import json
import unittest
from urllib.parse import parse_qs, urlparse
from unittest.mock import patch

from scripts.verify_public_reliability_wave import (
    CANONICAL_ORIGIN,
    MAIN_ROUTES,
    UNIT_PRICE_FAMILY,
    PublicReliabilityProbe,
    extract_head,
    public_unit_price_rows,
    published_unit_price_service_ids,
    sitemap_urls,
    rendered_unit_price_rows,
)

REGIONS = ["一級地", "二級地", "三級地", "四級地",
           "五級地", "六級地", "七級地", "その他"]


def make_head(path, *, noindex=False):
    title = f"ページ {path} | 介護ルール"
    return (
        "<html><head><meta charset=\"utf-8\">"
        f"<title>{title}</title>"
        f"<meta name=\"description\" content=\"説明 {path}\">"
        f"<link href=\"{CANONICAL_ORIGIN}{path if path != '/' else ''}\" rel=\"canonical\">"
        + ('<meta content="noindex, follow" name="robots">' if noindex else "")
        + "</head><body>"
    )


def make_items():
    return [
        {
            "item_body": {
                "region_class": region,
                "unit_price_yen": 11.4 - 0.1 * i,
                "ratio_per_thousand": 1140 - 10 * i,
            },
            "currentness_statement": {"state": "VERIFIED"},
        }
        for i, region in enumerate(REGIONS)
    ]


class FakeProbe(PublicReliabilityProbe):
    def __init__(self):
        super().__init__("http://127.0.0.1:3000", "abc123")
        self.omit_region = None
        self.bad_api = False

    def get(self, path):
        parsed = urlparse(path)
        query = parse_qs(parsed.query)
        route = parsed.path
        if route == "/api/version":
            return 200, json.dumps({"service": "kaigo-rules", "commit_sha": "abc123"})
        if route == "/robots.txt":
            return 200, f"User-agent: *\nSitemap: {CANONICAL_ORIGIN}/sitemap.xml\n"
        if route == "/sitemap.xml":
            return 200, (
                '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
                + "".join(f"<url><loc>{CANONICAL_ORIGIN}{p}</loc></url>" for p in MAIN_ROUTES)
                + "</urlset>"
            )
        if route == "/api/context/services/__wave_d_missing__/sources":
            return 404, '{"error":"SERVICE_SOURCE_CONTEXT_NOT_PUBLISHED"}'
        if route.startswith("/api/context/services/") and route.endswith("/sources"):
            service = route.split("/")[4]
            rows = make_items()
            if self.bad_api:
                rows[0]["item_body"]["unit_price_yen"] = "NaN"
            return 200, json.dumps({
                "service": {"id": service},
                "sources": [{"source_family": UNIT_PRICE_FAMILY, "items": rows}],
            }, ensure_ascii=False)
        if route == "/__wave_d_missing_page__":
            return 404, "<html>not found</html>"
        if route == "/fees/unit-price":
            if query.get("service") == ["__wave_d_missing__"]:
                return 200, "このサービスの単価は現在公開していません"
            if query.get("q") == ["__wave_d_no_match__"]:
                return 200, "現在公開している範囲では一致しませんでした"
            body = "人手確認が完了していない"
            for item in make_items():
                region = item["item_body"]["region_class"]
                if region != self.omit_region:
                    yen = f"{item['item_body']['unit_price_yen']:.2f}"
                    # React SSR separates an expression and adjacent text with a comment.
                    body += (
                        f'<div class="unit-price-row"><strong>{region}</strong>'
                        f'<span>{yen}<!-- -->円</span></div>'
                    )
            return 200, make_head(route) + body + "</body></html>"
        if route == "/databases/search":
            if query.get("q") == ["BCP"]:
                return 200, make_head(route, noindex=True) + "</body></html>"
            body = "一単位単価・地域区分" + "".join(REGIONS[:3])
            return 200, make_head(route, noindex=True) + body + "</body></html>"
        if route == "/search":
            return 200, make_head(route, noindex=True) + "</body></html>"
        if route in MAIN_ROUTES:
            return 200, make_head(route) + "</body></html>"
        return 404, "unknown"


class PublicReliabilityWaveTests(unittest.TestCase):
    def test_ssr_split_price_text_stays_in_its_own_row(self):
        html = (
            '<div class="unit-price-row"><strong>一級地</strong>'
            '<span>11.40<!-- -->円</span></div>'
            '<div class="unit-price-row"><strong>二級地</strong>'
            '<span>11.20<!-- -->円</span></div>'
        )
        self.assertEqual(rendered_unit_price_rows(html),
                         ["一級地11.40円", "二級地11.20円"])

    def test_head_parser_is_attribute_order_independent(self):
        html = ('<html><head><link href="https://x.example/" rel="canonical">'
                '<meta content="説明" name="description">'
                '<title>標題 &amp; 補足</title>'
                '<meta content="noindex,follow" name="robots"></head></html>')
        head = extract_head(html)
        self.assertEqual(head.canonical, ["https://x.example/"])
        self.assertEqual(head.description, ["説明"])
        self.assertEqual(head.title, "標題 & 補足")
        self.assertIn("noindex", head.robots[0])

    def test_sitemap_parser_and_duplicate_detection(self):
        xml = ('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
               '<url><loc>https://example.org/a</loc></url></urlset>')
        self.assertEqual(sitemap_urls(xml), ["https://example.org/a"])
        with self.assertRaises(Exception):
            sitemap_urls("<broken")

    def test_deployed_revision_allowlist_drives_all_service_checks(self):
        service_ids = published_unit_price_service_ids()
        self.assertGreaterEqual(len(service_ids), 2)
        self.assertEqual(service_ids, sorted(set(service_ids)))
        self.assertIn("dayservice", service_ids)
        self.assertIn("homevisit", service_ids)

    def test_api_projection_rejects_invalid_price_and_empty_data(self):
        valid = {"sources": [{"source_family": UNIT_PRICE_FAMILY, "items": make_items()}]}
        self.assertEqual(len(public_unit_price_rows(valid)), 8)
        for invalid in (
            {"sources": []},
            {"sources": [{"source_family": UNIT_PRICE_FAMILY, "items": []}]},
            {"sources": [{"source_family": UNIT_PRICE_FAMILY, "items": [
                {"item_body": {"region_class": "一級地", "unit_price_yen": "10.9",
                               "ratio_per_thousand": 1090},
                 "currentness_statement": "verified"}]}]},
        ):
            with self.assertRaises(AssertionError):
                public_unit_price_rows(invalid)

    def test_all_synthetic_checks_pass(self):
        report = FakeProbe().run()
        self.assertEqual(report["status"], "PASS", report)
        self.assertEqual(report["passed"], report["total"])
        self.assertIn("mobile/browser E2E", report["not_verified"])

    def test_api_invalid_value_is_reported_without_false_success(self):
        probe = FakeProbe()
        probe.bad_api = True
        report = probe.run()
        self.assertEqual(report["status"], "FAIL")
        failures = {row["check"] for row in report["checks"] if row["status"] == "FAIL"}
        self.assertIn("unit_price_api_vs_html_homevisit", failures)

    def test_missing_html_rate_is_reported(self):
        probe = FakeProbe()
        probe.omit_region = "二級地"
        report = probe.run()
        self.assertEqual(report["status"], "FAIL")
        self.assertTrue(any("二級地" in row.get("detail", "")
                            for row in report["checks"] if row["status"] == "FAIL"))

    def test_exact_commit_mismatch_is_rejected(self):
        probe = FakeProbe()
        probe.expected_sha = "different"
        report = probe.run()
        self.assertEqual(report["status"], "FAIL")
        self.assertEqual(report["checks"][0]["check"], "exact_deployed_commit")
        self.assertEqual(report["checks"][0]["status"], "FAIL")


if __name__ == "__main__":
    unittest.main()
