"""Small, build-free checks of the static Pages legacy-link inventory."""
import importlib.util
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "legacy_link_audit", ROOT / "scripts/audit_github_pages_legacy_links.py")
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


class LegacyLinkAuditTest(unittest.TestCase):
    def test_counts_exact_host_by_page_and_target(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "handbook/dayservice").mkdir(parents=True)
            (root / "index.html").write_text(
                '<a href="https://kaigo-rules.vercel.app/qa/item?reader=1">QA</a>'
                "<a href='https://kaigo-rules.vercel.app/legislation?service=x&amp;page=2'>法令</a>"
                '<a href="https://kaigo-rules.vercel.app.evil.example/qa">偽装ホスト</a>'
                '<a href="https://kaigo-rules.vercel.app@evil.example/qa">偽装情報</a>'
                '<script>const url="https://kaigo-rules.vercel.app/qa";</script>',
                encoding="utf-8")
            (root / "handbook/dayservice/staff.html").write_text(
                '<form action="http://kaigo-rules.vercel.app/services/dayservice">'
                '<link href="https://www.mhlw.go.jp/source.css"></form>',
                encoding="utf-8")
            report = audit.audit(root)
            self.assertEqual(report["html_pages_scanned"], 2)
            self.assertEqual(report["remaining_legacy_urls"], 3)
            self.assertEqual(report["by_source_route"], {"/": 2, "/handbook": 1})
            self.assertEqual(report["by_target_route"],
                             {"/legislation": 1, "/qa": 1, "/services": 1})
            self.assertEqual(sum(item["count"] for item in report["by_route_pair"]), 3)
            self.assertIn("service=x&page=2", report["samples"][1]["href"])
            self.assertIn("NOT_VERIFIED", report["coverage"])

    def test_fails_closed_for_missing_or_symlink_pages(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with self.assertRaisesRegex(ValueError, "No generated HTML"):
                audit.audit(root)
            (root / "index.html").write_text("ok", encoding="utf-8")
            self.assertEqual(audit.audit(root)["remaining_legacy_urls"], 0)
            (root / "linked.html").symlink_to(root / "index.html")
            with self.assertRaisesRegex(ValueError, "Unsafe HTML"):
                audit.audit(root)


if __name__ == "__main__":
    unittest.main()
