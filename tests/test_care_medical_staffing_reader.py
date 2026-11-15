import hashlib
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from scripts import care_medical_staffing_reader as guide


class CareMedicalStaffingReaderTest(unittest.TestCase):
    def fixture(self):
        def source(number, label):
            return (f'<details class="handbook-source"><summary><span class="handbook-source-label">'
                    f'{number}</span><span>{label}</span></summary>'
                    '<p>収載資料の版・施行日：2025-11-20</p>'
                    f'<p class="handbook-original">{number}のテスト本文</p></details>')
        return ('<article>' + guide.INSERT_AFTER + f'<p>{guide.OLD_NOTE}</p>' +
                ''.join(source(number, record[0]) for number, record in guide.SOURCES.items()) + '</article>')

    def hashes(self):
        return {number: (label, anchor, hashlib.sha256(f'{number}のテスト本文'.encode()).hexdigest())
                for number, (label, anchor, _) in guide.SOURCES.items()}

    def test_staffing_formulas_and_facility_exceptions_are_not_combined(self):
        with patch.dict(guide.SOURCES, self.hashes()):
            content, count = guide.add_care_medical_staffing_overview(self.fixture(), guide.PAGE)
        self.assertEqual(count, 1)
        for text in ('Ⅰ型入所者数÷48', 'Ⅱ型入所者数÷100', '3人未満なら3人',
                     '第27条第3項に基づき医師を宿直させない場合', '国の解釈通知を掲載した資料',
                     '医療機関併設型の医師は、別に定める', '定員19人以下',
                     'Ⅰ型入所者数÷150', 'Ⅱ型入所者数÷300',
                     '入所者数を6で割った数以上', 'Ⅰ型入所者数÷5',
                     '入所定員100人以上', '省令上の<strong>標準</strong>',
                     '病院か診療所か', '夜間・深夜は2ユニットごとに1人以上',
                     '介護保険法第109条', '医師以外の者も、都道府県知事の承認'):
            self.assertIn(text, content)
        for number, (_, anchor, _) in guide.SOURCES.items():
            self.assertIn(f'<p class="handbook-original">{number}のテスト本文</p>', content)
            self.assertIn(f'id="{anchor}"', content)

    def test_source_drift_blocks_the_overview(self):
        for content in (self.fixture().replace('第四条のテスト本文', '変更'),
                        self.fixture().replace('2025-11-20', '2026-11-20', 1)):
            with self.subTest(content=content[:80]), patch.dict(guide.SOURCES, self.hashes()):
                with self.assertRaisesRegex(RuntimeError, 'source changed'):
                    guide.add_care_medical_staffing_overview(content, guide.PAGE)

    def test_other_service_is_not_changed(self):
        self.assertEqual(guide.add_care_medical_staffing_overview(
            self.fixture(), Path('handbook/elderly-health-facility/staffing.html')), (self.fixture(), 0))

    def test_manager_law_record_change_stops_publication(self):
        with TemporaryDirectory() as temp:
            root = Path(temp)
            (root / guide.PAGE).parent.mkdir(parents=True)
            (root / guide.PAGE).write_text('staffing')
            directory = root / 'legislation/record'
            directory.mkdir(parents=True)
            record_id = 'careact.article.109'
            record_file = directory / (hashlib.sha256(record_id.encode()).hexdigest() + '.html')
            record_file.write_text('<div class="dayservice-original" style="white-space:pre-wrap">法の本文</div>')
            expected = hashlib.sha256('法の本文'.encode()).hexdigest()
            with patch.dict(guide.LAW_SOURCES, {guide.PAGE: (record_id, expected)}):
                guide.validate_facility_manager_law_sources(root)
                record_file.write_text('<div class="dayservice-original" style="white-space:pre-wrap">改正後の本文</div>')
                with self.assertRaisesRegex(RuntimeError, 'law source changed'):
                    guide.validate_facility_manager_law_sources(root)


if __name__ == '__main__':
    unittest.main()
