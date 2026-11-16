import hashlib
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts import homebath_staffing_reader as reader


class HomebathStaffingReaderTest(unittest.TestCase):
    def setUp(self):
        self.sources = {}
        self.pages = {}
        for page, records in reader.SOURCES.items():
            self.sources[page] = {}
            chunks = [reader.INSERT_AFTER] if page == reader.STAFFING else []
            for number, (label, anchor, _) in records.items():
                original = f'{number}の条文本文'
                self.sources[page][number] = (label, anchor, hashlib.sha256(original.encode()).hexdigest())
                chunks.append(f'<details class="handbook-source"><summary><span class="handbook-source-label">{number}</span><span>{label}</span></summary>'
                              f'<p>収載資料の版・施行日：2025-04-01</p><p class="handbook-original">{original}</p></details>')
            self.pages[page] = ''.join(chunks)

    def test_guide_distinguishes_office_and_visit_requirements(self):
        with patch.object(reader, 'SOURCES', self.sources):
            staffing, count = reader.add_homebath_staffing_overview(self.pages[reader.STAFFING], reader.STAFFING)
            operations, operations_count = reader.add_homebath_staffing_overview(self.pages[reader.OPERATIONS], reader.OPERATIONS)
        self.assertEqual((count, operations_count), (1, 1))
        self.assertIn('看護師または准看護師を1人以上、介護職員を2人以上', staffing)
        self.assertIn('主治医の意見を確認した上で', staffing)
        self.assertIn('事業所ごとの看護職員の配置を免除するものではありません', staffing)
        self.assertIn('介護予防側の人員基準を満たした上で介護職員を1人置く', staffing)
        self.assertIn('href="operations.html#homebath-staff-article50"', staffing)
        self.assertIn('id="homebath-staff-article50"', operations)
        self.assertIn('第五十条の条文本文', operations)

    def test_changed_source_or_version_is_rejected_in_either_chapter(self):
        with patch.object(reader, 'SOURCES', self.sources):
            for page, number in ((reader.STAFFING, '第四十五条'), (reader.OPERATIONS, '第五十条')):
                for damaged in (self.pages[page].replace(number + 'の条文本文', '変更された本文'),
                                self.pages[page].replace('2025-04-01', '2026-04-01', 1)):
                    with self.subTest(page=page), self.assertRaisesRegex(RuntimeError, 'source changed'):
                        reader.add_homebath_staffing_overview(damaged, page)

    def test_unrelated_preventive_page_is_unchanged(self):
        page = Path('handbook/preventive-homebath/staffing.html')
        self.assertEqual(reader.add_homebath_staffing_overview(self.pages[reader.STAFFING], page),
                         (self.pages[reader.STAFFING], 0))

    def test_duplicate_source_is_rejected(self):
        with patch.object(reader, 'SOURCES', self.sources):
            page = self.pages[reader.OPERATIONS]
            with self.assertRaisesRegex(RuntimeError, 'Missing or duplicate'):
                reader.add_homebath_staffing_overview(page + page, reader.OPERATIONS)


if __name__ == '__main__':
    unittest.main()
