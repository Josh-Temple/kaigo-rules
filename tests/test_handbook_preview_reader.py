"""Focused data and safety-boundary regression for the protected handbook reader.

This is a source/data contract test, NOT a browser or TypeScript execution test.
Run: python -m unittest discover -s tests -p 'test_handbook_preview_reader.py' -v
"""
import json
import pathlib
import unittest
from urllib.parse import urlsplit

ROOT = pathlib.Path(__file__).resolve().parents[1]
PREVIEW = ROOT / "app" / "handbook-preview"
DATA = ROOT / "docs" / "prototypes" / "evidence-bridges"


class HandbookPreviewReaderContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.page = (PREVIEW / "page.tsx").read_text(encoding="utf-8")
        cls.client = (PREVIEW / "PreviewWorkspace.tsx").read_text(encoding="utf-8")
        cls.style = (PREVIEW / "preview-workspace.module.css").read_text(encoding="utf-8")
        cls.public = (ROOT / "app" / "handbook-sources" / "page.tsx").read_text(encoding="utf-8")
        cls.drafts = {
            service: json.loads((DATA / (service + ".json")).read_text(encoding="utf-8"))
            for service in ("dayservice", "dayrehab")
        }

    def test_two_services_have_15_chapters_and_29_distinct_paragraphs(self):
        ids = set()
        self.assertEqual(
            [self.drafts[x]["candidate_paragraph_count"] for x in ("dayservice", "dayrehab")],
            [11, 18],
        )
        for service, draft in self.drafts.items():
            self.assertEqual(draft["service_id"], service)
            self.assertEqual(len(draft["chapters"]), 15)
            self.assertEqual(len({x["section_id"] for x in draft["chapters"]}), 15)
            self.assertEqual(
                sum(len(x["candidate_paragraphs"]) for x in draft["chapters"]),
                draft["candidate_paragraph_count"],
            )
            for chapter in draft["chapters"]:
                for item in chapter["candidate_paragraphs"]:
                    self.assertNotIn((service, item["bridge_id"]), ids)
                    ids.add((service, item["bridge_id"]))
        self.assertEqual(len(ids), 29)

    def test_all_candidates_reference_a_matching_source_record(self):
        for service, draft in self.drafts.items():
            sources = {x["task_id"]: x for x in draft["source_evidence"]}
            self.assertEqual(len(sources), 6)
            for source in sources.values():
                self.assertEqual(source["service_id"], service)
            for chapter in draft["chapters"]:
                for item in chapter["candidate_paragraphs"]:
                    source = sources[item["evidence_task_id"]]
                    self.assertEqual(item["evidence_library_file_id"], source["library_file_id"])
                    self.assertEqual(item["source_url_from_evidence"], source["source_url"])

    def test_no_promotion_of_unreviewed_material(self):
        for draft in self.drafts.values():
            for key, value in {
                "release_gate": "HOLD_NO_GO",
                "publication": "BLOCKED",
                "currentness": "NOT_ESTABLISHED",
                "applicability": "NOT_ESTABLISHED",
                "human_review": "NOT_REVIEWED",
                "legal_explanations_accepted": 0,
                "real_project_work_enabled": False,
            }.items():
                self.assertEqual(draft[key], value)
            for chapter in draft["chapters"]:
                for item in chapter["candidate_paragraphs"]:
                    self.assertEqual(item["draft_review_state"], "DRAFT_UNREVIEWED")

    def test_server_environment_denies_production(self):
        self.assertIn('process.env.VERCEL_ENV !== "preview"', self.page)
        self.assertIn('process.env.NODE_ENV !== "development"', self.page)
        self.assertIn('notFound()', self.page)
        self.assertIn('export const dynamic = "force-dynamic"', self.page)

    def test_runtime_service_and_source_identity_validation(self):
        for marker in (
            "data.service_id !== expectedService",
            "data.currentness !== \"NOT_ESTABLISHED\"",
            "data.human_review !== \"NOT_REVIEWED\"",
            "source.library_file_id !== item.evidence_library_file_id",
            "source.source_url !== item.source_url_from_evidence",
            "ids.has(item.bridge_id)",
        ):
            self.assertIn(marker, self.page)

    def test_no_public_page_or_search_uses_unreviewed_paragraph_text(self):
        self.assertNotIn("item.text", self.public)
        self.assertNotIn("candidate.text", self.public)
        self.assertNotIn("PreviewWorkspace", self.public)
        self.assertIn("未レビューの手引本文29文は、この公開ページには掲載していません", self.public)

    def test_official_url_is_restricted_to_expected_hosts(self):
        for literal in (
            'url.protocol !== "https:"',
            "url.username || url.password",
            "url.port || url.hash",
            '"www.mhlw.go.jp", "laws.e-gov.go.jp"',
        ):
            self.assertIn(literal, self.page)
        for draft in self.drafts.values():
            for source in draft["source_evidence"]:
                url = urlsplit(source["source_url"])
                if url.hostname in ("www.mhlw.go.jp", "laws.e-gov.go.jp"):
                    self.assertEqual(url.scheme, "https")
                else:
                    # Non-official locators must not be used as an external official link.
                    self.assertNotIn(url.hostname, ("www.mhlw.go.jp", "laws.e-gov.go.jp"))

    def test_no_raw_html_or_client_network_transmission(self):
        for source in (self.page, self.client):
            for forbidden in ("dangerouslySetInnerHTML", "innerHTML =", "eval(", "XMLHttpRequest(", "sendBeacon(", "fetch("):
                self.assertNotIn(forbidden, source)

    def test_search_and_keyboard_accessible_controls(self):
        for marker in (
            'type="search"', 'aria-expanded={isExpanded}', "aria-controls=",
            "aria-pressed=", "<label>", "<select", "<textarea",
            'role="status"', 'role="alert"',
            "candidate.text", "candidate.bridgeId", "chapter.title",
        ):
            self.assertIn(marker, self.client)

    def test_local_storage_error_does_not_erase_unsaved_notes(self):
        for marker in (
            "window.localStorage.getItem", "window.localStorage.setItem",
            "setCanPersist(false)", "setStorageError(", "setRecords((prev) =>",
            "JSON.stringify({ version: 1, review_completed: false, sections: records })",
        ):
            self.assertIn(marker, self.client)
        self.assertNotIn(".slice(0,", self.client)
        self.assertNotIn(".substring(", self.client)

    def test_download_error_preserves_full_json(self):
        for marker in (
            "new Blob([json]", "URL.createObjectURL(blob)",
            "setExportFallback(json)", "<textarea readOnly",
            "review_completed: false", "downloadError",
        ):
            self.assertIn(marker, self.client)

    def test_mobile_width_and_focus_visible(self):
        self.assertIn("@media (max-width: 430px)", self.style)
        self.assertIn("min-height: 44px", self.style)
        self.assertIn(":focus-visible", self.style)
        self.assertIn("overflow-wrap: anywhere", self.style)


if __name__ == "__main__":
    unittest.main()
