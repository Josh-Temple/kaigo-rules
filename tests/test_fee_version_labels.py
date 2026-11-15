import unittest
from pathlib import Path

from scripts.fee_version_labels import label_fee_version


class FeeVersionLabelsTest(unittest.TestCase):
    def detail(self):
        return (
            '<strong>現行公式本文を取込済み・人手確認待ち</strong>'
            '厚生労働省の現行HTMLから機械抽出した本文です。'
            '<dt>本文</dt><dd>確認済み</dd><dt>現行性</dt><dd>確認中</dd>'
            '現行性確認の対象末日：各ページの出典情報を参照'
            '本文の独立確認、現行性の確認、人手確認は別々に管理しています。未確認の項目を確認済みとして表示しません。'
            '<h2>現行公式本文</h2>'
            '<div class="fee-official-text">本文：1,234単位<br>注：条件あり</div>'
            '<dt>最新改正</dt><dd>令和8年厚生労働省告示第87号</dd>'
        )

    def test_fee_version_and_assurance_labels_do_not_change_legal_text(self):
        result, kind = label_fee_version(self.detail(), Path('fees/standard/index.html'))
        self.assertEqual(kind, 'fee_detail_version_labels')
        self.assertIn('<div class="fee-official-text">本文：1,234単位<br>注：条件あり</div>', result)
        self.assertIn('<dt>本文（機械照合）</dt><dd>確認済み</dd>', result)
        self.assertIn('<dt>現行性</dt><dd>未確認</dd>', result)
        self.assertIn('2026年9月23日時点の収載資料', result)
        self.assertIn('<dt>収載版に反映した改正</dt>', result)
        self.assertNotIn('現行公式本文', result)
        self.assertNotIn('<dt>最新改正</dt>', result)

    def test_unknown_version_or_changed_structure_fails_closed(self):
        for content in (self.detail().replace('告示第87号', '告示第99号'),
                        self.detail().replace('fee-official-text', 'changed'),
                        self.detail() + '<dt>最新改正</dt><dd>令和8年厚生労働省告示第87号</dd>'):
            with self.subTest(content=content), self.assertRaises(RuntimeError):
                label_fee_version(content, Path('fees/standard/index.html'))

    def test_other_fees_are_not_relabelled(self):
        content = '<div>異なる資料の表記</div>'
        self.assertEqual(label_fee_version(content, Path('fees/guidance/index.html')), (content, None))


if __name__ == '__main__':
    unittest.main()
