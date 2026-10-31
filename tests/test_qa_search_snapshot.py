import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("qa_snapshot", ROOT / "scripts/extract_qa_search_snapshot.py")
snapshot = importlib.util.module_from_spec(spec)
spec.loader.exec_module(snapshot)


class QaSnapshotTest(unittest.TestCase):
    def test_extracts_pagination_and_only_result_links(self):
        doc = ('<div class="qa-search-summary"><p><strong>31件</strong> 見つかりました</p></div>'
               '<section class="qa-row"><h2><a href="/qa/abc?reader=1">質問</a></h2></section>'
               '<nav class="qa-pagination"><a href="/qa?page=1">前へ</a><span>2 / 2ページ</span></nav>')
        self.assertEqual(snapshot.extract(doc), {
            "total": 31, "page": 2, "totalPages": 2, "links": ["/qa/abc?reader=1"],
        })

    def test_rejects_missing_pagination(self):
        with self.assertRaises(ValueError):
            snapshot.extract('<div class="qa-search-summary">31件</div>')
