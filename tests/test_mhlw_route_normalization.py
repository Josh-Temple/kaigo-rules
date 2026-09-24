from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from validate_cross_layer_source_chain_independent_audit import (  # noqa: E402
    equivalent_mhlw_doc_route,
)


class MhlwRouteNormalizationTests(unittest.TestCase):
    def test_page_number_does_not_change_document_identity(self):
        left = "https://www.mhlw.go.jp/web/t_doc?dataId=82aa0253&dataType=0"
        right = "https://www.mhlw.go.jp/web/t_doc?dataId=82aa0253&dataType=0&pageNo=1"
        self.assertTrue(equivalent_mhlw_doc_route(left, right))

    def test_data_id_change_is_not_equivalent(self):
        left = "https://www.mhlw.go.jp/web/t_doc?dataId=82aa0253&dataType=0"
        right = "https://www.mhlw.go.jp/web/t_doc?dataId=82aa0261&dataType=0&pageNo=1"
        self.assertFalse(equivalent_mhlw_doc_route(left, right))

    def test_path_change_is_not_equivalent(self):
        left = "https://www.mhlw.go.jp/web/t_doc?dataId=82aa0253&dataType=0"
        right = "https://www.mhlw.go.jp/other?dataId=82aa0253&dataType=0"
        self.assertFalse(equivalent_mhlw_doc_route(left, right))


if __name__ == "__main__":
    unittest.main()
