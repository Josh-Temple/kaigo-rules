"""Secure static extraction and exact rendered parity for the 29 fee detail routes."""
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "private_fees", ROOT / "scripts/build_github_pages_fee_details_pilot.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class PrivateFeeDetailsTest(unittest.TestCase):
    def test_current_manifest_matches_static_next_routes(self):
        rows = mod.select_routes()
        self.assertEqual(len(rows), 29)
        self.assertEqual(len({slug for slug, _ in rows}), 29)
        self.assertIn(("note.1", "基本報酬の算定・利用者数／人員基準"), rows)
        self.assertIn(("treatment-improvement", "介護職員等処遇改善加算"), rows)

    def test_handles_dot_route_and_keeps_original_warning(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "data").mkdir()
            (root / ".next/server/app/fees").mkdir(parents=True)
            (root / ".next/BUILD_ID").write_text("validated", encoding="utf-8")
            (root / "data/remuneration-current-skeleton.json").write_text(json.dumps([
                {"id": "fee.dayservice.root", "parent_id": None, "title": "root"},
                {"id": "fee.dayservice.note.1", "parent_id": "fee.dayservice.root", "title": "注意"},
            ]), encoding="utf-8")
            (root / ".next/server/app/fees/note.1.html").write_text(
                '<html><body><article class="answer-page rules-page fee-detail-page">'
                '<h1>注意</h1><p>現行公式本文を取込済み・人手確認待ち</p>'
                '<a href="/fees/criteria#criteria">関連する基準</a>'
                '</article><script>secret hydration</script></body></html>',
                encoding="utf-8",
            )
            out = root / "private"
            out.mkdir()
            with patch.object(mod, "ROOT", root):
                self.assertEqual(mod.select_routes(), [("note.1", "注意")])
                result = mod.add_pages(out)
            self.assertEqual(result["pages"], 1)
            content = (out / "fees/note.1/index.html").read_text(encoding="utf-8")
            self.assertIn("人手確認待ち", content)
            self.assertIn('href="https://kaigo-rules.vercel.app/fees/criteria#criteria"', content)
            self.assertIn('href="../../styles.css"', content)
            self.assertNotIn("secret hydration", content)

    def test_rejects_path_traversal_and_duplicate_routes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "data").mkdir()
            f = root / "data/remuneration-current-skeleton.json"
            f.write_text(json.dumps([
                {"id": "fee.dayservice.../secrets", "parent_id": "fee.dayservice.root", "title": "X"},
            ]), encoding="utf-8")
            with patch.object(mod, "ROOT", root), self.assertRaises(RuntimeError):
                mod.select_routes()
            f.write_text(json.dumps([
                {"id": "fee.dayservice.note.1", "parent_id": "fee.dayservice.root", "title": "X"},
                {"id": "fee.dayservice.note.1", "parent_id": "fee.dayservice.root", "title": "X"},
            ]), encoding="utf-8")
            with patch.object(mod, "ROOT", root), self.assertRaises(RuntimeError):
                mod.select_routes()
