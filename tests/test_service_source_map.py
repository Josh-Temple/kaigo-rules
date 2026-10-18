"""Offline structural regression for the 39-service public-source navigation.

Run without GitHub Actions:
    python -m unittest discover -s tests -p 'test_service_source_map.py' -v
The source-map is a finder; these tests do not attest current legal applicability.
"""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "data/services/catalog.generated.json"
NAVIGATION = ROOT / "data/public-service-navigation.json"
PAGE = ROOT / "app/services/source-map/page.tsx"
CLIENT = ROOT / "components/service-source-map.tsx"
SERVICE_INDEX = ROOT / "app/services/page.tsx"
POLICY = ROOT / "lib/public-source-navigation.ts"


class ServiceSourceMapTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
        cls.navigation = json.loads(NAVIGATION.read_text(encoding="utf-8"))
        cls.page = PAGE.read_text(encoding="utf-8")
        cls.client = CLIENT.read_text(encoding="utf-8")
        cls.index = SERVICE_INDEX.read_text(encoding="utf-8")
        cls.policy = POLICY.read_text(encoding="utf-8")

    def test_existing_universe_has_39_distinct_services(self):
        ids = [s["service_id"] for s in self.catalog["services"]]
        nav_ids = [
            sid
            for group in self.navigation["groups"]
            for unit in group["units"]
            for sid in unit["service_ids"]
        ]
        self.assertEqual(len(self.navigation["groups"]), 7)
        self.assertEqual(len(ids), 39)
        self.assertEqual(len(set(ids)), 39)
        self.assertEqual(len(nav_ids), 39)
        self.assertEqual(set(nav_ids), set(ids))
        self.assertEqual(nav_ids.count("preventive-support"), 1)

    def test_page_uses_existing_catalog_navigation_and_publication_policy(self):
        for marker in [
            "listServices()",
            "validatePublicServiceNavigation()",
            "publicServiceNavigationGroups()",
            "publicSourceFamiliesForService(entry.service_id)",
            "validated.service_entries !== 39",
            "services.length !== 39",
            '"/services/source-map",',
            "false,",
        ]:
            self.assertIn(marker, self.page)
        self.assertIn('href="/services/source-map"', self.index)
        self.assertIn("isProgressiveRouteCell(serviceId, definition.source_family)", self.policy)
        self.assertNotIn("publishedLayerLabels", self.page)
        self.assertNotIn("verification_layer_ids", self.page)
        self.assertNotIn("public_routes_enabled = true", self.page)

    def test_unreviewed_content_is_not_exposed(self):
        for marker in [
            "handbook_href:", "public_sources:", "公開", "未レビュー",
            "法令上の適用範囲", "人手レビュー完了",
        ]:
            self.assertIn(marker, self.page)
        for src in [self.page, self.client]:
            for disallowed in [
                "dangerouslySetInnerHTML", "candidate_paragraphs",
                "evidence-bridges/dayservice", "evidence-bridges/dayrehab",
                "human_review = \"REVIEWED\"", "publication = \"ALLOWED\"",
            ]:
                self.assertNotIn(disallowed, src)
        self.assertIn('entry.service_id === "dayservice" || entry.service_id === "dayrehab"', self.page)

    def test_mobile_search_accessibility_and_source_fallback(self):
        for marker in [
            'type="search"', "aria-live=\"polite\"",
            'htmlFor="service-source-query"',
            'htmlFor="service-source-family"',
            "onChange={(event) => setQuery(event.target.value)}",
            "onChange={(event) => setFamily(event.target.value)}",
            "setQuery(\"\")", "setFamily(\"all\")",
            "service.public_sources.length === 0",
            "資料が存在しないという意味ではありません",
            "encodeURIComponent(service.service_id)",
            "role=\"status\"",
        ]:
            self.assertIn(marker, self.client)
        self.assertNotIn("localStorage", self.client)
        self.assertNotIn("fetch(", self.client)


if __name__ == "__main__":
    unittest.main()
