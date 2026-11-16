import hashlib
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts import community_facility_equipment_reader as reader


class CommunityFacilityEquipmentReaderTest(unittest.TestCase):
    def setUp(self):
        self.sources = {}
        chunks = [reader.INSERT_AFTER]
        for number, (label, anchor, _) in reader.SOURCES.items():
            original = f'{number}の条文本文'
            self.sources[number] = (label, anchor, hashlib.sha256(original.encode()).hexdigest())
            chunks.append(f'<details class="handbook-source"><summary><span class="handbook-source-label">{number}</span><span>{label}</span></summary>'
                          f'<p>収載資料の版・施行日：2025-04-01</p><p class="handbook-original">{original}</p></details>')
        self.html = ''.join(chunks)

    def test_guide_distinguishes_nonunit_and_unit_facilities(self):
        with patch.object(reader, 'SOURCES', self.sources):
            result, count = reader.add_community_facility_equipment_overview(self.html, reader.PAGE)
        self.assertEqual(count, 1)
        self.assertIn('床面積は入所者1人当たり10.65平方メートル以上', result)
        self.assertIn('2人とする場合は21.3平方メートル以上', result)
        self.assertIn('共同生活室の床面積は、ユニットの入居定員1人当たり2平方メートルを標準', result)
        self.assertIn('施設の設置時期による経過措置', result)
        self.assertIn('洗面設備は居室のある階ごと', result)
        self.assertIn('洗面設備と便所は居室ごと、または共同生活室ごと', result)
        self.assertIn('医務室を設けなくてもよい', result)
        self.assertIn('浴室・医務室・廊下・非常災害に必要な設備について原則', result)
        for number, (_, anchor, _) in self.sources.items():
            self.assertIn(f'id="{anchor}"', result)
            self.assertIn(f'{number}の条文本文', result)

    def test_changed_source_or_effective_date_is_rejected(self):
        with patch.object(reader, 'SOURCES', self.sources):
            for damaged in (self.html.replace('第百六十条の条文本文', '内容変更'),
                            self.html.replace('2025-04-01', '2026-04-01', 1)):
                with self.subTest(damaged=damaged), self.assertRaisesRegex(RuntimeError, 'source changed'):
                    reader.add_community_facility_equipment_overview(damaged, reader.PAGE)

    def test_unrelated_facility_is_unchanged(self):
        page = Path('handbook/elderly-facility/equipment.html')
        self.assertEqual(reader.add_community_facility_equipment_overview(self.html, page), (self.html, 0))

    def test_duplicate_source_is_rejected(self):
        with patch.object(reader, 'SOURCES', self.sources):
            with self.assertRaisesRegex(RuntimeError, 'Missing or duplicate'):
                reader.add_community_facility_equipment_overview(self.html + self.html[len(reader.INSERT_AFTER):], reader.PAGE)


if __name__ == '__main__':
    unittest.main()
