import hashlib
from pathlib import Path
import unittest
from unittest.mock import patch

from scripts import preventive_group_home_staffing_reader as guide


class PreventiveGroupHomeStaffingReaderTest(unittest.TestCase):
    def fixture(self):
        def source(number, label):
            return (f'<details class="handbook-source"><summary><span class="handbook-source-label">'
                    f'{number}</span><span>{label}</span></summary>'
                    '<p>収載資料の版・施行日：2024-04-01</p>'
                    f'<p class="handbook-original">{number}のテスト本文</p></details>')
        return ('<article>' + guide.INSERT_AFTER + f'<p>{guide.OLD_NOTE}</p>' +
                ''.join(source(number, record[0]) for number, record in guide.SOURCES.items()) + '</article>')

    def hashes(self):
        return {number: (label, anchor, hashlib.sha256(f'{number}のテスト本文'.encode()).hexdigest())
                for number, (label, anchor, _) in guide.SOURCES.items()}

    def test_preventive_exception_and_integrated_operation_are_separate(self):
        with patch.dict(guide.SOURCES, self.hashes()):
            content, count = guide.add_preventive_group_home_staffing_overview(self.fixture(), guide.PAGE)
        self.assertEqual(count, 1)
        for text in ('利用者3人またはその端数ごとに1人以上を常勤換算',
                     '宿直勤務を含みません', 'すべて同一階で隣接',
                     '安全対策が講じられ利用者の安全が確保されていると認められる場合',
                     '併設する小規模多機能型居宅介護の介護支援専門員との連携',
                     '効果的な運営が期待でき、利用者の処遇に支障がない場合',
                     '両方の指定を受け、同じ事業所で一体的に運営する場合',
                     '介護側の基準第90条第1項から第10項まで',
                     '認知症の人の介護に3年以上従事した経験'):
            self.assertIn(text, content)
        self.assertNotIn('看護小規模多機能型居宅介護', content)
        for number, (_, anchor, _) in guide.SOURCES.items():
            self.assertIn(f'<p class="handbook-original">{number}のテスト本文</p>', content)
            self.assertIn(f'id="{anchor}"', content)
            self.assertIn(f'href="#{anchor}"', content)

    def test_changed_source_or_version_stops_publication(self):
        for content in (self.fixture().replace('第七十条のテスト本文', '変更された本文'),
                        self.fixture().replace('2024-04-01', '2025-04-01', 1),
                        self.fixture().replace('第七十一条のテスト本文', '')):
            with self.subTest(content=content[:100]), patch.dict(guide.SOURCES, self.hashes()):
                with self.assertRaisesRegex(RuntimeError, 'source changed'):
                    guide.add_preventive_group_home_staffing_overview(content, guide.PAGE)

    def test_ordinary_group_home_is_not_changed(self):
        content = self.fixture()
        self.assertEqual(guide.add_preventive_group_home_staffing_overview(
            content, Path('handbook/dementia-group-home/staffing.html')), (content, 0))


if __name__ == '__main__':
    unittest.main()
