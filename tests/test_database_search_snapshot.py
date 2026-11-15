import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("search_snapshot", ROOT / "scripts/extract_database_search_snapshot.py")
snapshot = importlib.util.module_from_spec(spec)
spec.loader.exec_module(snapshot)


class SearchSnapshotTest(unittest.TestCase):
    def test_counts_and_links_ignore_unrelated_sections(self):
        blocks = []
        for label, group in snapshot.LABELS.items():
            prefix = snapshot.PREFIXES[group]
            blocks.append('<section class="section"><h2>' + label +
                          ' <span>(2件)</span></h2><a href="' + prefix +
                          'a&amp;b">結果</a><p>説明</p></section>')
        doc = '<article><section class="section"><h2>実務テーマ</h2></section>' + "".join(blocks) + '</article>'
        result = snapshot.extract(doc)
        self.assertEqual(set(result), set(snapshot.PREFIXES))
        self.assertEqual(result["unitPrice"]["count"], 2)
        self.assertEqual(result["unitPrice"]["links"], ["/fees/unit-price?a&b"])

    def test_missing_group_fails_closed(self):
        with self.assertRaises(ValueError):
            snapshot.extract("<section class='section'><h2>国Q&amp;A (0件)</h2></section>")
