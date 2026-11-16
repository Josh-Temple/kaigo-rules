import hashlib
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts import dementia_dayservice_staffing_reader as reader


class DementiaDayserviceStaffingReaderTest(unittest.TestCase):
    def setUp(self):
        self.source = {}
        chunks = [reader.INSERT_AFTER]
        for number, (label, anchor, _) in reader.SOURCES.items():
            original = f'{number}の条文本文'
            self.source[number] = (label, anchor, hashlib.sha256(original.encode()).hexdigest())
            chunks.append(f'<details class="handbook-source"><summary><span class="handbook-source-label">{number}</span><span>{label}</span></summary>'
                          f'<p>収載資料の版・施行日：2025-04-01</p><p class="handbook-original">{original}</p></details>')
        self.html = ''.join(chunks)

    def test_guide_distinguishes_shared_and_nonshared_staffing(self):
        with patch.object(reader, 'SOURCES', self.source):
            result, count = reader.add_dementia_dayservice_staffing_overview(self.html, reader.PAGE)
        self.assertEqual(count, 1)
        self.assertIn('単独型・併設型と共用型では基準が異なります', result)
        self.assertIn('看護職員または介護職員が常時1人以上', result)
        self.assertIn('生活相談員、看護職員または介護職員のうち1人以上は常勤', result)
        self.assertIn('本体事業所・施設に適用される人員基準', result)
        self.assertIn('双方の指定を受けている場合', result)
        for number, (_, anchor, _) in self.source.items():
            self.assertIn(f'id="{anchor}"', result)
            self.assertIn(f'{number}の条文本文', result)

    def test_changed_source_or_effective_version_is_rejected(self):
        with patch.object(reader, 'SOURCES', self.source):
            for damaged in (self.html.replace('第四十二条の条文本文', '内容の変更'),
                            self.html.replace('2025-04-01', '2026-04-01', 1)):
                with self.subTest(damaged=damaged), self.assertRaisesRegex(RuntimeError, 'source changed'):
                    reader.add_dementia_dayservice_staffing_overview(damaged, reader.PAGE)

    def test_unrelated_service_is_unchanged(self):
        result, count = reader.add_dementia_dayservice_staffing_overview(self.html, Path('handbook/preventive-dementia-dayservice/staffing.html'))
        self.assertEqual((result, count), (self.html, 0))

    def test_duplicate_source_is_rejected(self):
        with patch.object(reader, 'SOURCES', self.source):
            with self.assertRaisesRegex(RuntimeError, 'Missing or duplicate'):
                reader.add_dementia_dayservice_staffing_overview(self.html + self.html[len(reader.INSERT_AFTER):], reader.PAGE)


if __name__ == '__main__':
    unittest.main()
