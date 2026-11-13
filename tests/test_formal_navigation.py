"""Verify published fee navigation without inventing a unit-price table."""
import tempfile
import hashlib
import json
import unittest
from pathlib import Path

from scripts.rewrite_public_navigation import rewrite

ORIGIN = "https://kaigo-rules.vercel.app"
COMMON = (
    f'<a href="{ORIGIN}/rules?service=dayservice">基準DB</a>'
    f'<a href="{ORIGIN}/notices?service=dayservice">通知DB</a>'
    f'<a href="{ORIGIN}/fees/unit-price">単価・地域区分</a>'
)


class FeeNavigationTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for name in ("fees", "fees/guidance", "legislation", "databases/search"):
            (self.root / name).mkdir(parents=True, exist_ok=True)
        (self.root / "legislation/index.html").write_text(
            '<p>収載資料には人手確認前の部分があります。準用・読替え・例外・施行日や自治体ごとの取扱いは公式原典で確認してください。</p>')
        (self.root / "databases/search/index.html").write_text("search")
        self.fees = self.root / "fees/index.html"
        self.guidance = self.root / "fees/guidance/index.html"
        self.fees.write_text(COMMON +
            f'<a href="{ORIGIN}/fees/criteria">告示27号・95号の構造化データを見る →</a>' +
            f'<a href="{ORIGIN}/fees/unit-price">通所介護の一単位単価を見る →</a>' +
            '<p>制度の現行性は原典で確認してください。</p>')
        self.guidance.write_text(COMMON + f'<a href="{ORIGIN}/fees/root">通所介護費</a>')

    def test_known_links_are_local_and_the_search_is_not_labeled_a_price_table(self):
        self.assertEqual(rewrite(self.root), {"pages_changed": 3, "search_scripts_changed": 0, "fee_links_changed": 9,
                                              "index_links_changed": {"standards": 0, "law": 0, "notices": 0, "notice_records": 0},
                                              "additional_changes": {"criteria_records": 0, "simple_links": 0, "unavailable_all_views": 0,
                                                                     "scoped_rule_links": 0, "dayrehab_scope_notes": 0, "fee_root_records": 0}})
        fees = self.fees.read_text()
        guidance = self.guidance.read_text()
        self.assertNotIn(ORIGIN, fees + guidance)
        self.assertIn('../legislation/index.html?service=dayservice&amp;category=standards', fees)
        self.assertIn('../../legislation/index.html?service=dayservice&amp;category=notices', guidance)
        self.assertIn('../legislation/index.html?category=criteria', fees)
        self.assertIn('href="../index.html">通所介護の報酬一覧', guidance)
        self.assertIn('地域区分の関連資料を検索（一単位単価表ではありません）', fees)
        self.assertIn('制度の現行性は原典で確認してください。', fees)
        self.assertNotIn('通所介護の一単位単価を見る', fees)
        self.assertIn('別のサービス名が書かれた条文は、そのまま選択したサービスに当てはめず',
                      (self.root / 'legislation/index.html').read_text())

    def test_changed_link_fails_before_either_page_is_modified(self):
        self.guidance.write_text(self.guidance.read_text().replace("通所介護費", "別のラベル"))
        original_fees = self.fees.read_text()
        original_guidance = self.guidance.read_text()
        with self.assertRaisesRegex(RuntimeError, "Expected legacy fee link"):
            rewrite(self.root)
        self.assertEqual(self.fees.read_text(), original_fees)
        self.assertEqual(self.guidance.read_text(), original_guidance)

    def test_missing_target_fails_before_modifying_pages(self):
        (self.root / "legislation/index.html").unlink()
        original = self.fees.read_text()
        with self.assertRaisesRegex(RuntimeError, "target missing"):
            rewrite(self.root)
        self.assertEqual(self.fees.read_text(), original)

    def test_changed_legal_notice_stops_all_rewrites(self):
        (self.root / "legislation/index.html").write_text("予期しない法令一覧")
        original = self.fees.read_text()
        with self.assertRaisesRegex(RuntimeError, "Unexpected legislation index caution"):
            rewrite(self.root)
        self.assertEqual(self.fees.read_text(), original)

    def test_unknown_legacy_link_is_not_silently_dropped(self):
        self.guidance.write_text(self.guidance.read_text() + f'<a href="{ORIGIN}/unknown">unknown</a>')
        original = self.fees.read_text()
        with self.assertRaisesRegex(RuntimeError, "unrecognized legacy link"):
            rewrite(self.root)
        self.assertEqual(self.fees.read_text(), original)

    def test_legal_index_links_preserve_service_and_reject_unknown_parameters(self):
        service = self.root / "services/dayservice/index.html"
        service.parent.mkdir(parents=True)
        service.write_text("service")
        other_service = self.root / "services/homevisit/index.html"
        other_service.parent.mkdir(parents=True)
        other_service.write_text("service")
        page = self.root / "databases/search/details.html"
        identifier = 'notice.dayservice.operation.policy'
        (self.root / 'legislation/record').mkdir()
        record_file = hashlib.sha256(identifier.encode()).hexdigest() + '.html'
        (self.root / 'legislation/record' / record_file).write_text('notice')
        (self.root / 'legislation/record-index.json').write_text(json.dumps({
            identifier: {'category': 'notices', 'services': ['dayservice']}
        }))
        page.write_text(
            f'<a href="{ORIGIN}/rules?service=dayservice">基準へ</a>'
            f'<a href="{ORIGIN}/law">法律へ</a>'
            f'<a href="{ORIGIN}/notices?service=dayservice">通知一覧へ</a>'
            f'<a href="{ORIGIN}/notices?service=dayservice#{identifier}">通知の該当箇所</a>'
            f'<a href="{ORIGIN}/notices?service=homevisit#{identifier}">別サービスの通知</a>'
            f'<a href="{ORIGIN}/rules?service=unknown">未知のサービス</a>'
            f'<a href="{ORIGIN}/rules?service=dayservice&amp;extra=1">未知の条件</a>'
            f'<a href="{ORIGIN}/rules?service=dayservice#part">項目指定</a>'
        )
        result = rewrite(self.root)
        updated = page.read_text()
        self.assertEqual(result["index_links_changed"], {"standards": 1, "law": 1, "notices": 1, "notice_records": 1})
        self.assertIn('../../legislation/index.html?service=dayservice&amp;category=standards', updated)
        self.assertIn('../../legislation/index.html?category=law', updated)
        self.assertIn('../../legislation/index.html?service=dayservice&amp;category=notices', updated)
        self.assertIn('../../legislation/record/' + record_file, updated)
        self.assertIn(f'{ORIGIN}/notices?service=homevisit#{identifier}', updated)
        self.assertIn(f'{ORIGIN}/rules?service=unknown', updated)
        self.assertIn(f'{ORIGIN}/rules?service=dayservice&amp;extra=1', updated)
        self.assertIn(f'{ORIGIN}/rules?service=dayservice#part', updated)

    def test_known_criteria_links_use_the_matching_published_record(self):
        folder = self.root / 'legislation/record'
        folder.mkdir()
        entries = {}
        for identifier, document in [('notice95.item.24', 'criteria-mhlw-fee-criteria95-current'),
                                     ('notice27.item.1', 'criteria-mhlw-fee-notice27-base')]:
            entries[identifier] = {'document': document, 'category': 'criteria', 'services': ['dayservice']}
            (folder / (hashlib.sha256(identifier.encode()).hexdigest() + '.html')).write_text('record')
        (self.root / 'legislation/record-index.json').write_text(json.dumps(entries))
        page = self.root / 'fees/example.html'
        page.write_text(f'<a href="{ORIGIN}/fees/criteria#criteria95.dayservice.24">処遇改善加算</a>'
                        f'<a href="{ORIGIN}/fees/criteria#calc27.dayservice.1.capacity">利用定員超過</a>'
                        f'<a href="{ORIGIN}/fees/criteria#criteria95.dayservice.99">未知</a>')
        result = rewrite(self.root)
        content = page.read_text()
        self.assertEqual(result['additional_changes']['criteria_records'], 2)
        self.assertIn(hashlib.sha256('notice95.item.24'.encode()).hexdigest() + '.html', content)
        self.assertIn(hashlib.sha256('notice27.item.1'.encode()).hexdigest() + '.html', content)
        self.assertIn('利用定員超過（告示第1号全体）', content)
        self.assertIn(f'{ORIGIN}/fees/criteria#criteria95.dayservice.99', content)

    def test_criteria_link_is_not_rewritten_if_scope_or_document_differs(self):
        identifier = 'notice95.item.24'
        folder = self.root / 'legislation/record'
        folder.mkdir()
        (folder / (hashlib.sha256(identifier.encode()).hexdigest() + '.html')).write_text('record')
        (self.root / 'legislation/record-index.json').write_text(json.dumps({identifier: {
            'document': 'other', 'category': 'criteria', 'services': ['dayservice']}}))
        page = self.root / 'fees/example.html'
        original = f'<a href="{ORIGIN}/fees/criteria#criteria95.dayservice.24">処遇改善加算</a>'
        page.write_text(original)
        rewrite(self.root)
        self.assertEqual(page.read_text(), original)

    def test_missing_generic_article_view_is_not_linked_to_a_different_ordinance(self):
        page = self.root / 'databases/search/legal/rules/care-management/21-2.html'
        page.parent.mkdir(parents=True)
        page.write_text(f'<a class="" href="{ORIGIN}/rules/21-2">すべて</a>'
                        f'<a class="" href="{ORIGIN}/rules/22">すべて</a>')
        result = rewrite(self.root)
        self.assertEqual(result['additional_changes']['unavailable_all_views'], 1)
        self.assertIn('<span>全サービスでの表示は未対応</span>', page.read_text())
        self.assertIn(f'{ORIGIN}/rules/22', page.read_text())

    def test_simple_navigation_preserves_honest_labels(self):
        target = self.root / 'handbook/dayrehab/remuneration.html'
        target.parent.mkdir(parents=True)
        target.write_text('手引')
        page = self.root / 'databases/search/example.html'
        page.write_text(f'<a href="{ORIGIN}/services/dayrehab/remuneration">報酬DB</a>'
                        f'<a href="{ORIGIN}/services/dayrehab/remuneration/guidance">算定上の留意事項</a>'
                        f'<a href="{ORIGIN}/fees/unit-price">単価・地域区分</a>')
        result = rewrite(self.root)
        content = page.read_text()
        self.assertEqual(result['additional_changes']['simple_links'], 3)
        self.assertIn('基本報酬の手引', content)
        self.assertIn('service=dayrehab&amp;category=guidance', content)
        self.assertIn('算定上の留意事項の関連資料', content)
        self.assertIn('地域区分の資料検索', content)
        self.assertNotIn(ORIGIN, content)

    def test_guide_points_to_scoped_material_and_the_official_unit_price_notice(self):
        guide = self.root / 'guide/index.html'
        guide.parent.mkdir()
        rows = [
            ('/databases#remuneration', '報酬基準DBの入口を見る', '公開済みのサービス別報酬基準へ進みます。'),
            ('/databases#fee-guidance', '算定上の留意事項の入口を見る', 'サービス別に保持している算定上の留意事項へ進みます。'),
            ('/databases#fee-guidance', '算定上の留意事項の入口を見る', '公開済みの算定上の留意事項DBへ進みます。'),
            ('/fees/unit-price', '一単位単価・地域区分DBを見る', '現在公開中の通所介護向け地域区分・一単位単価DBを確認します。'),
        ]
        introduction = '一単位単価の告示と、公開中の地域区分DBを分けて確認します。'
        closing = ('公開中の一単位単価DBは通所介護向けです。他サービスは、厚生労働省告示の'
                   'サービス区分と地域区分を原文で確認してください。')
        guide.write_text(introduction * 2 + closing + ''.join(
            ('<h4>DB内で確認する</h4><div class="entry-links">' if href == '/fees/unit-price' else '') +
            f'<a class="entry-row" href="{ORIGIN}{href}"><span>{title}'
            f'<small>{description}</small></span><small>開く →</small></a>' for href, title, description in rows))
        rewrite(self.root)
        content = guide.read_text()
        self.assertIn('../legislation/index.html?category=remuneration', content)
        self.assertEqual(content.count('../legislation/index.html?category=guidance'), 2)
        self.assertIn('https://www.mhlw.go.jp/web/t_doc?dataId=82ab4582&amp;dataType=0&amp;pageNo=1', content)
        self.assertIn('一単位単価の告示を確認する', content)
        self.assertIn('一単位単価の専用表はこのサイトでは公開していません', content)
        self.assertIn('<h4>確認先</h4>', content)
        self.assertNotIn('公開中の地域区分DB', content)
        self.assertNotIn('現在公開中の通所介護向け', content)

    def test_scoped_links_explain_when_the_common_article_is_used(self):
        identifier = 'ordinance37.article.21'
        (self.root / 'legislation/record-index.json').write_text(json.dumps({identifier: {
            'document': 'ordinance37', 'category': 'standards', 'services': ['dayservice']}}))
        parent = self.root / 'databases/search/legal/rules'
        common = parent / 'all/21.html'
        common.parent.mkdir(parents=True)
        common.write_text('<section class="rule-application-note"><span>通所介護・準用</span></section>'
                          f'<a href="{ORIGIN}/rules/21?service=dayservice">通所介護</a>')
        scoped = parent / 'dayservice/105.html'
        scoped.parent.mkdir()
        scoped.write_text(f'<a class="rule-row" href="{ORIGIN}/rules/21?service=dayservice">'
                          '<span class="rule-number">第21条</span>'
                          '<span class="rule-status">第105条で準用</span></a>')
        result = rewrite(self.root)
        self.assertEqual(result['additional_changes']['scoped_rule_links'], 2)
        self.assertIn('通所介護（共通本文）', common.read_text())
        self.assertIn('../all/21.html', scoped.read_text())
        self.assertIn('第105条で準用・共通本文', scoped.read_text())

    def test_scoped_link_stays_unmodified_without_matching_application(self):
        identifier = 'ordinance37.article.21'
        (self.root / 'legislation/record-index.json').write_text(json.dumps({identifier: {
            'document': 'ordinance37', 'category': 'standards', 'services': ['dayservice']}}))
        common = self.root / 'databases/search/legal/rules/all/21.html'
        common.parent.mkdir(parents=True)
        original = ('<section class="rule-application-note"><span>訪問介護・直接規定</span></section>'
                    f'<a href="{ORIGIN}/rules/21?service=dayservice">通所介護</a>')
        common.write_text(original)
        rewrite(self.root)
        self.assertEqual(common.read_text(), original)

    def test_dayrehab_incorporation_note_and_fee_root_use_matching_records(self):
        entries = {
            'ordinance37.article.119': {'document': 'ordinance37', 'category': 'standards', 'services': ['dayrehab']},
            'fee.dayservice.root': {'document': 'remuneration-dayservice', 'category': 'remuneration', 'services': ['dayservice']},
        }
        (self.root / 'legislation/record-index.json').write_text(json.dumps(entries))
        folder = self.root / 'legislation/record'
        folder.mkdir()
        for identifier in entries:
            (folder / (hashlib.sha256(identifier.encode()).hexdigest() + '.html')).write_text('record')
        dayrehab = self.root / 'databases/search/legal/rules/dayrehab/118.html'
        dayrehab.parent.mkdir(parents=True)
        dayrehab.write_text('<p class="scope-note">通所リハの準用relation・読み替えを含む詳細表示は'
                            f'<a href="{ORIGIN}/services/dayrehab/rules/118">サービス別ページ</a>でも確認できます。</p>')
        fee = self.root / 'fees/relationship.html'
        fee.write_text(f'<a href="{ORIGIN}/fees/root"><span><strong>通所介護費</strong><small>6</small></span></a>')
        result = rewrite(self.root)
        self.assertEqual(result['additional_changes']['dayrehab_scope_notes'], 1)
        self.assertEqual(result['additional_changes']['fee_root_records'], 1)
        self.assertIn('第119条の本文', dayrehab.read_text())
        self.assertIn(hashlib.sha256('fee.dayservice.root'.encode()).hexdigest(), fee.read_text())

    def test_search_results_use_verified_local_notice_and_official_price_source(self):
        search = self.root / 'databases/search'
        identifier = 'notice.dayservice.staffing'
        criterion = 'notice95.item.24'
        (self.root / 'legislation/record-index.json').write_text(json.dumps({
            identifier: {'document': 'notice', 'category': 'notices', 'services': ['dayservice']},
            criterion: {'document': 'criteria', 'category': 'criteria', 'services': ['dayservice']}}))
        folder = self.root / 'legislation/record'
        folder.mkdir()
        (folder / (hashlib.sha256(identifier.encode()).hexdigest() + '.html')).write_text('record')
        (folder / (hashlib.sha256(criterion.encode()).hexdigest() + '.html')).write_text('record')
        (search / 'global.json').write_text(json.dumps({
            'notice': [{'href': '/notices?service=dayservice#' + identifier}],
            'delegated': [{'href': '/fees/criteria?service=dayservice#' + criterion}]}))
        (search / 'app.mjs').write_text(
            'const localQaDetails = document.querySelector(\'meta[name="kaigo-qa-local-details"]\')?.content === "true";\n'
            f'{ORIGIN}\n{ORIGIN}\n' + '  } else {\n    link.href = destination.href;\n  }\n  return link;')
        (search / 'qa-app.mjs').write_text('''    const link = element("a", item.question);
    link.href = localDetails
      ? "./qa-details/" + encodeURIComponent(item.id) + (current.reader ? "/reader.html" : "/index.html")
      : "https://kaigo-rules.vercel.app/qa/" + encodeURIComponent(item.id) + (current.reader ? "?reader=1" : "");''')
        result = rewrite(self.root)
        code = (search / 'app.mjs').read_text()
        self.assertEqual(result['search_scripts_changed'], 2)
        self.assertIn(hashlib.sha256(identifier.encode()).hexdigest() + '.html', code)
        self.assertIn(hashlib.sha256(criterion.encode()).hexdigest() + '.html', code)
        self.assertIn('厚生労働省の告示', code)
        self.assertIn('詳細ページ未収載', code)
        self.assertNotIn(ORIGIN, code + (search / 'qa-app.mjs').read_text())


if __name__ == "__main__":
    unittest.main()
