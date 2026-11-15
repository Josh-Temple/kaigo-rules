import hashlib
from pathlib import Path
import unittest
from unittest.mock import patch

from scripts import nursing_small_scale_roles_clarification as guide


class NursingSmallScaleRolesTest(unittest.TestCase):
    def fixture(self):
        parts = ['<article><label>' + guide.OLD + '</label>']
        parts += ['<p>' + old + '</p>' for old in guide.REPLACEMENTS]
        for article in guide.SOURCE_HASHES:
            parts.append('<details class="handbook-source"><summary><span class="handbook-source-label">'
                         + article + '</span></summary><p>収載資料の版・施行日：2025-04-01</p>'
                         '<p class="handbook-original">' + article + 'の原文</p></details>')
        return ''.join(parts) + '</article>'

    def hashes(self):
        return {article: hashlib.sha256((article + 'の原文').encode()).hexdigest()
                for article in guide.SOURCE_HASHES}

    def test_roles_have_distinct_requirements_and_sources_remain_intact(self):
        with patch.dict(guide.SOURCE_HASHES, self.hashes()):
            content, count = guide.clarify_nursing_small_scale_roles(self.fixture(), guide.PAGE)
        self.assertEqual(count, 1)
        checklist = content.split('</label>', 1)[0]
        manager, representative = checklist.split('代表者は、', 1)
        self.assertIn('認知症介護の経験3年以上と所定の研修修了', manager)
        self.assertIn('保健医療・福祉サービスの経営の経験', representative)
        self.assertNotIn('3年以上', representative)
        self.assertIn('又は保健師・看護師の要件', manager)
        self.assertIn('又は保健師・看護師の要件', representative)
        self.assertNotIn(guide.OLD, content)
        for required in ('宿泊サービスの利用者がいない場合', '必要な連絡体制',
                         'サテライト型の看護職員は常勤換算で1以上',
                         '所定の併設施設等の職務', '本体事業所の介護支援専門員',
                         '看護小規模多機能型居宅介護計画の作成に専ら従事する所定の研修修了者',
                         '（省令34号第173条）'):
            self.assertIn(required, content)
        self.assertNotIn('（省令34号第173条第1項）', content)
        for article in guide.SOURCE_HASHES:
            self.assertIn('<p class="handbook-original">' + article + 'の原文</p>', content)

    def test_source_or_checklist_drift_fails_closed(self):
        variations = (self.fixture().replace('2025-04-01', '2026-04-01', 1),
                      self.fixture().replace('第百七十三条の原文', '変更された原文'),
                      self.fixture().replace(guide.OLD, ''), self.fixture() + guide.OLD,
                      self.fixture().replace(next(iter(guide.REPLACEMENTS)), ''))
        with patch.dict(guide.SOURCE_HASHES, self.hashes()):
            for content in variations:
                with self.subTest(content=content), self.assertRaises(RuntimeError):
                    guide.clarify_nursing_small_scale_roles(content, guide.PAGE)

    def test_other_service_is_untouched(self):
        content = self.fixture()
        self.assertEqual(guide.clarify_nursing_small_scale_roles(
            content, Path('handbook/dayservice/staffing.html')), (content, 0))


if __name__ == '__main__':
    unittest.main()
