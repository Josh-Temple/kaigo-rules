import hashlib
from pathlib import Path
import re
import unittest
from unittest.mock import patch

from scripts import care_management_staffing_reader as guide


class CareManagementStaffingTest(unittest.TestCase):
    def fixture(self):
        parts = ['<article>', guide.INSERT_AFTER, '<p>', guide.OLD_NOTE, '</p>']
        for number, (label, _anchor, _hash) in guide.SOURCES.items():
            parts.append('<details class="handbook-source"><summary><span class="handbook-source-label">'
                         + number + '</span><span>' + label + '</span></summary>'
                         '<p>収載資料の版・施行日：2024-04-01</p>'
                         '<p class="handbook-original">' + number + 'の原文</p></details>')
        return ''.join(parts) + '</article>'

    def sources(self):
        return {number: (label, anchor, hashlib.sha256((number + 'の原文').encode()).hexdigest())
                for number, (label, anchor, _) in guide.SOURCES.items()}

    def test_staffing_counts_and_manager_exceptions(self):
        with patch.dict(guide.SOURCES, self.sources()):
            content, count = guide.add_care_management_staffing_overview(self.fixture(), guide.PAGE)
        self.assertEqual(count, 1)
        for required in ('常勤の介護支援専門員を1人以上', '44人またはその端数',
                         '49人またはその端数', 'かつ事務職員を配置', '同一法人内の配置',
                         '42＋9÷3＝45人', '44人の基準では2人', '49人の基準を適用できる場合は1人',
                         'やむを得ない理由', '2027年3月31日', '後の改正'):
            self.assertIn(required, content)
        self.assertNotIn(guide.OLD_NOTE, content)
        for number, (_label, anchor, _hash) in guide.SOURCES.items():
            self.assertIn('<p class="handbook-original">' + number + 'の原文</p>', content)
            self.assertEqual(content.count('id="' + anchor + '"'), 1)
        for anchor in re.findall(r'href="#(care-management-staff-[^"]+)"', guide.OVERVIEW):
            self.assertEqual(content.count('id="' + anchor + '"'), 1, anchor)

    def test_missing_duplicate_or_changed_source_fails_closed(self):
        variations = (self.fixture().replace('2024-04-01', '2026-04-01', 1),
                      self.fixture().replace('第二条の原文', '変更された原文'),
                      self.fixture().replace(guide.OLD_NOTE, ''),
                      self.fixture() + guide.INSERT_AFTER)
        with patch.dict(guide.SOURCES, self.sources()):
            for content in variations:
                with self.subTest(content=content), self.assertRaises(RuntimeError):
                    guide.add_care_management_staffing_overview(content, guide.PAGE)

    def test_other_service_untouched(self):
        content = self.fixture()
        self.assertEqual(guide.add_care_management_staffing_overview(
            content, Path('handbook/dayservice/staffing.html')), (content, 0))


if __name__ == '__main__':
    unittest.main()
