"""Bounded, offline migration-readiness audit tests; no deploy."""
import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

MODULE = Path(__file__).resolve().parents[1] / "scripts/audit_github_pages_migration_readiness.py"
spec = importlib.util.spec_from_file_location("readiness", MODULE)
readiness = importlib.util.module_from_spec(spec)
spec.loader.exec_module(readiness)


class MigrationReadinessTest(unittest.TestCase):
    def fixture(self, base):
        for name in readiness.REQUIRED:
            file = base / name
            file.parent.mkdir(parents=True, exist_ok=True)
            file.write_text('{"law": [{"href": "/law/1"}], "qa": []}' if file.suffix == ".json"
                            else '<html><body>検証ページ</body></html>', encoding="utf-8")
        return base / "index.html"

    def test_reports_fallbacks_missing_assets_and_project_base_path(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            index = self.fixture(root)
            (root / "app.mjs").write_text('const old = "kaigo-rules.vercel.app";', encoding="utf-8")
            index.write_text('''<html><body>
                <a href="services/dayservice/index.html">サービス</a>
                <a href="https://kaigo-rules.vercel.app/notices/12">旧サイト</a>
                <a href="https://www.mhlw.go.jp/">原典</a>
                <a href="/databases">ルート直下</a>
                <a href="missing.html">未実装</a>
                <script src="app.mjs"></script>
                </body></html>''', encoding="utf-8")
            report = readiness.inspect(root)
            self.assertEqual(report["status"], "HOLD_NO_DEPLOY")
            self.assertEqual(report["blockers"], {
                "production_fallback_links": 1, "root_relative_links": 1,
                "missing_local_links": 1, "unsafe_or_invalid_links": 0,
                "javascript_references_to_production": 1,
                "private_preview_pages": 0, "noindex_pages": 0,
            })
            self.assertEqual(report["local_links_resolved"], 2)
            self.assertEqual(report["global_search_rows_by_group"]["law"], 1)
            self.assertEqual(report["production_fallback_by_section"], {"notices": 1})

    def test_refuses_private_or_noindex_preview_markers_in_release_gate(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            index = self.fixture(root)
            index.write_text(
                '<meta name="robots" content="noindex,nofollow,noarchive">'
                '<p>静的移行の検証版（一般公開していません）</p>', encoding="utf-8"
            )
            blockers = readiness.inspect(root)["blockers"]
            self.assertEqual(blockers["private_preview_pages"], 1)
            self.assertEqual(blockers["noindex_pages"], 1)

    def test_refuses_symlink_and_raw_private_files(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.fixture(root)
            private = root / "data" / "unreviewed.json"
            private.parent.mkdir()
            private.write_text("{}", encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "Blocked"):
                readiness.inspect(root)
            private.unlink()
            private.parent.rmdir()
            (root / "linked").symlink_to(root / "index.html")
            with self.assertRaisesRegex(RuntimeError, "Symlink"):
                readiness.inspect(root)

    def test_rejects_unsafe_external_schemes_and_scheme_relative_urls(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            index = self.fixture(root)
            index.write_text(
                '<a href="javascript:alert(1)">unsafe</a>'
                '<a href="//example.org/tracker">scheme-relative</a>'
                '<a href="data:text/html,unsafe">unsafe data</a>',
                encoding="utf-8",
            )
            report = readiness.inspect(root)
            self.assertEqual(report["blockers"]["unsafe_or_invalid_links"], 3)

    def test_limits_site_size_and_requires_valid_manifest(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.fixture(root)
            with self.assertRaisesRegex(RuntimeError, "budget"):
                with patch.object(readiness, "PAGES_BUDGET_BYTES", 10):
                    readiness.inspect(root)
            (root / "databases/search/global.json").write_text('[]', encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "global search"):
                readiness.inspect(root)


if __name__ == "__main__":
    unittest.main()
