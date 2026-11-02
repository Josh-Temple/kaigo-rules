"""Private static legislation extraction and exact-link mapping checks."""
import importlib.util
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "legislation_pilot", ROOT / "scripts/build_github_pages_legislation_pilot.py")
legislation = importlib.util.module_from_spec(spec)
spec.loader.exec_module(legislation)
nav_spec = importlib.util.spec_from_file_location(
    "navigation_pilot", ROOT / "scripts/localize_github_pages_links_pilot.py")
nav = importlib.util.module_from_spec(nav_spec)
nav_spec.loader.exec_module(nav)


class StaticLegislationTest(unittest.TestCase):
    def dataset(self, root, record_id="legal.article.12"):
        corpus = root / "legal.json"
        corpus.write_text(json.dumps({
            "documents": [{"id": "official-standards", "title": "指定介護基準",
                           "category": "standards"}],
            "records": [
                {"id": record_id, "document_id": "official-standards", "label": "第12条",
                 "title": "人員", "text": "原文\n<確認対象>", "locator": "第12条",
                 "state": "PENDING", "url": "https://www.mhlw.go.jp/test.pdf",
                 "service_ids": ["dayservice", "homevisit"],
                 "source_file": "PRIVATE_INTERNAL_PATH"},
            ],
        }, ensure_ascii=False), encoding="utf-8")
        return corpus

    def test_static_record_keeps_text_and_filters_out_internal_fields(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            out = root / "out"
            out.mkdir()
            result = legislation.build(out, self.dataset(root))
            self.assertEqual(result["records"], 1)
            page = out / "legislation/record" / (hashlib.sha256("legal.article.12".encode()).hexdigest() + ".html")
            text = page.read_text(encoding="utf-8")
            self.assertIn("原文\n&lt;確認対象&gt;", text)
            self.assertIn("https://www.mhlw.go.jp/test.pdf", text)
            self.assertNotIn("PRIVATE_INTERNAL_PATH", text)
            self.assertNotIn("PENDING", text)
            self.assertEqual(nav.destination(out, "https://kaigo-rules.vercel.app/legislation?record=legal.article.12&service=dayservice")[1], page)
            self.assertIsNone(nav.destination(out, "https://kaigo-rules.vercel.app/legislation?record=legal.article.12&service=unrelated"))
            self.assertIsNone(nav.destination(out, "https://kaigo-rules.vercel.app/legislation?record=legal.article.12&category=notices"))
            self.assertIsNone(nav.destination(out, "https://kaigo-rules.vercel.app/legislation?record=legal.article.12&q=ignore"))
            self.assertIsNone(nav.destination(out, "https://kaigo-rules.vercel.app/legislation?record=legal.article.12&record=x"))

    def test_canonical_ids_with_colons_and_japanese_use_hashed_paths(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            out = root / "out"
            out.mkdir()
            record_id = "notice:令和8年/介護・第1条"
            legislation.build(out, self.dataset(root, record_id))
            encoded = hashlib.sha256(record_id.encode("utf-8")).hexdigest() + ".html"
            page = out / "legislation/record" / encoded
            self.assertTrue(page.is_file())
            from urllib.parse import urlencode
            url = "https://kaigo-rules.vercel.app/legislation?" + urlencode({"record":record_id,"service":"dayservice"})
            self.assertEqual(nav.destination(out, url)[1], page)

    def test_invalid_record_id_or_untrusted_source_refused(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            out = root / "out"
            out.mkdir()
            with self.assertRaisesRegex(RuntimeError, "Unsafe legal record ID"):
                legislation.build(out, self.dataset(root, "illegal\\x00id"))
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            out = root / "out"
            out.mkdir()
            corpus = self.dataset(root)
            data = json.loads(corpus.read_text(encoding="utf-8"))
            data["records"][0]["url"] = "javascript:alert(1)"
            corpus.write_text(json.dumps(data), encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "Untrusted source"):
                legislation.build(out, corpus)


if __name__ == "__main__":
    unittest.main()
