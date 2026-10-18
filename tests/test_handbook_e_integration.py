"""Focused E integration boundary checks, executed by existing prebuild unittest discovery."""
import unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]

class HandbookEIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.page = (ROOT / "app/handbook-preview/page.tsx").read_text(encoding="utf-8")
        cls.ui = (ROOT / "app/handbook-preview/PreviewWorkspace.tsx").read_text(encoding="utf-8")
        cls.compose = (ROOT / "lib/handbook/compose.ts").read_text(encoding="utf-8")
        cls.public = (ROOT / "app/handbook-sources/page.tsx").read_text(encoding="utf-8")

    def test_protected_server_only_projection(self):
        self.assertIn('process.env.VERCEL_ENV !== "preview"', self.page)
        self.assertIn('process.env.NODE_ENV !== "development"', self.page)
        self.assertIn("handbookSourceProjectionForService(id)", self.page)
        self.assertIn('projection.publication !== "BLOCKED"', self.page)
        self.assertIn('projection.human_review !== "NOT_REVIEWED"', self.page)

    def test_new_metadata_only_on_preview(self):
        self.assertIn("sourceCandidates: info.source_candidates.map", self.page)
        self.assertIn("questionsToCheck: info.questions_to_check", self.page)
        self.assertIn("unresolved: info.unresolved", self.page)
        self.assertNotIn("handbookSourceProjectionForService", self.public)
        self.assertNotIn("{item.text}", self.public)

    def test_historical_status_is_never_assumed_current(self):
        self.assertIn('"UNVERIFIED"', self.compose)
        self.assertIn('"HISTORICAL" ? "HISTORICAL" : "UNVERIFIED"', self.compose)
        self.assertIn('"NOT_ESTABLISHED"', self.compose)
        self.assertIn('"NOT_GRANTED"', self.compose)

    def test_client_renders_candidate_as_unreviewed(self):
        self.assertIn("旧版の可能性・現行性未確認", self.ui)
        self.assertIn("過去資料として登録（現行性未確認）", self.ui)
        self.assertIn("chapter.publicSearchHref", self.ui)
        self.assertNotIn("dangerouslySetInnerHTML", self.ui)
        self.assertNotIn("fetch(", self.ui)

    def test_personal_notes_do_not_grant_review(self):
        self.assertIn("review_completed: false", self.ui)
        self.assertIn("window.localStorage.setItem", self.ui)
        self.assertIn("setExportFallback(json)", self.ui)

if __name__ == "__main__":
    unittest.main()
