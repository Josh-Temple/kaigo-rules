"""Approved Pages presentation preparation tests (no publication)."""
import importlib.util
import tempfile
import unittest
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "scripts/prepare_github_pages_public_candidate.py"
spec = importlib.util.spec_from_file_location("pages_public_prep", SRC)
prep = importlib.util.module_from_spec(spec)
spec.loader.exec_module(prep)


class PublicPresentationTest(unittest.TestCase):
    def test_strips_private_labels_but_retains_regulatory_warnings(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source = (root / "handbook.html")
            source.write_text(
                '<meta name="robots" content="noindex,nofollow,noarchive">'
                '<title>資料 — 静的移行検証</title>'
                '<strong>' + prep.PRIVATE_LABEL + '</strong>'
                '<p>' + prep.OLD_NOTICE + '</p>'
                '<p>' + prep.OLD_INTERACTIVE + '</p>'
                '<p>法令の現行性・適用条件・自治体の基準を必ず原典で確認してください。</p>',
                encoding="utf-8",
            )
            report = prep.prepare(root)
            self.assertEqual(report["html_pages"], 1)
            self.assertEqual(report["banners_rewritten"], 1)
            content = source.read_text(encoding="utf-8")
            self.assertIn(prep.PUBLIC_LABEL, content)
            self.assertIn("必ず原典で確認", content)
            self.assertNotIn("noindex", content)
            self.assertNotIn(prep.PRIVATE_LABEL, content)

    def test_rejects_unknown_noindex_and_symlinks(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            page = root / "index.html"
            page.write_text('<meta content="noindex" name="robots">', encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "private/noindex"):
                prep.prepare(root)
            page.unlink()
            page.symlink_to(root / "missing.html")
            with self.assertRaisesRegex(RuntimeError, "unsafe HTML"):
                prep.prepare(root)


if __name__ == "__main__":
    unittest.main()
