import hashlib
from pathlib import Path
import unittest
from unittest.mock import patch

from scripts import night_homevisit_manager_clarification as guide


class NightHomevisitManagerTest(unittest.TestCase):
    def fixture(self):
        return ('<article><p>' + guide.OLD + '</p>'
                '<details class="handbook-source"><summary><span class="handbook-source-label">'
                '第七条</span><span>（管理者）</span></summary>'
                '<p>収載資料の版・施行日：2025-04-01</p>'
                '<p class="handbook-original">原文のテスト</p></details></article>')

    def test_internal_and_external_roles_have_distinct_conditions(self):
        expected = hashlib.sha256('原文のテスト'.encode()).hexdigest()
        with patch.object(guide, 'SOURCE_HASH', expected):
            content, count = guide.clarify_night_homevisit_manager(self.fixture(), guide.PAGE)
        self.assertEqual(count, 1)
        self.assertIn('管理上支障がない場合は、その事業所の他の職務に従事できます。', content)
        self.assertIn('他の事業所・施設等の職務については、管理上支障がなく', content)
        self.assertIn('その相手先と一体的に運営している場合', content)
        self.assertIn('日中のオペレーションセンターサービス', content)
        self.assertIn('<p class="handbook-original">原文のテスト</p>', content)
        self.assertNotIn(guide.OLD, content)

    def test_source_drift_and_other_service(self):
        expected = hashlib.sha256('原文のテスト'.encode()).hexdigest()
        with patch.object(guide, 'SOURCE_HASH', expected):
            for content in (self.fixture().replace('原文のテスト', '変更'),
                            self.fixture().replace('2025-04-01', '2026-04-01')):
                with self.subTest(content=content), self.assertRaisesRegex(RuntimeError, 'source changed'):
                    guide.clarify_night_homevisit_manager(content, guide.PAGE)
        self.assertEqual(guide.clarify_night_homevisit_manager(
            self.fixture(), Path('handbook/homevisit/staffing.html')), (self.fixture(), 0))


if __name__ == '__main__':
    unittest.main()
