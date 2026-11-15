"""Verify published fee navigation without inventing a unit-price table."""
import tempfile
import hashlib
import json
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts import community_staffing_reader, health_facility_staffing_reader, welfare_facility_staffing_reader
from scripts.rewrite_public_navigation import clarify_handbook_review_status, label_qa_search_scopes, rewrite

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

    def test_unknown_or_duplicate_search_renderer_is_rejected(self):
        marker = '      card.append(internalLink(row.title, resultHref(group, row, q)));'
        for code in ('unexpected renderer', marker + '\n' + marker):
            with self.subTest(code=code), self.assertRaisesRegex(RuntimeError, 'search result rendering'):
                label_qa_search_scopes(code)

    def test_known_links_are_local_and_the_search_is_not_labeled_a_price_table(self):
        self.assertEqual(rewrite(self.root), {"pages_changed": 3, "search_scripts_changed": 0,
                                              "missing_record_text_labeled": 0, "partial_sources_labeled": 0,
                                              "fee_links_changed": 9,
                                              "index_links_changed": {"standards": 0, "law": 0, "notices": 0, "notice_records": 0},
                                              "additional_changes": {"criteria_records": 0, "simple_links": 0, "unavailable_all_views": 0,
                                                                     "scoped_rule_links": 0, "dayrehab_scope_notes": 0, "fee_root_links": 0,
                                                                     "community_handbook_sources": 0, "handbook_source_versions": 0,
                                                                     "handbook_review_status": 0, "community_staffing_overview": 0,
                                                                     "health_facility_staffing_overview": 0,
                                                                     "welfare_facility_staffing_overview": 0}})
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

    def test_review_status_is_readable_and_remains_unconfirmed(self):
        status = ('現在の確認状態は検証状態（NOT_VERIFIED）、現行性（NOT_ESTABLISHED）、'
                  '人手レビュー（NOT_REVIEWED）として扱い、更新時は差分と確認根拠を残してください。')
        markup = (f'<p>{status}</p><p>個別の適用は未確認（DRAFT_UNREVIEWED）。</p>'
                  '<a title="（DRAFT_UNREVIEWED）">原典</a>'
                  '<script>const status="（DRAFT_UNREVIEWED）";</script>')
        result, count = clarify_handbook_review_status(markup)
        self.assertEqual(count, 2)
        self.assertIn('資料の内容と現行性は未確認で、人による確認も行われていません', result)
        self.assertIn('個別の適用は未確認（人による確認前の下書きです）', result)
        self.assertIn('<a title="（DRAFT_UNREVIEWED）">原典</a>', result)
        self.assertIn('<script>const status="（DRAFT_UNREVIEWED）";</script>', result)

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
            (folder / (hashlib.sha256(identifier.encode()).hexdigest() + '.html')).write_text('<article>record</article>')
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
        self.assertIn('dataId=82ab4584', (folder / (hashlib.sha256('notice95.item.24'.encode()).hexdigest() + '.html')).read_text())
        self.assertIn('dataId=82aa0261', (folder / (hashlib.sha256('notice27.item.1'.encode()).hexdigest() + '.html')).read_text())

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

    def test_dayrehab_note_links_to_the_source_and_fee_root_uses_the_nonempty_list(self):
        entries = {
            'ordinance37.article.119': {'document': 'ordinance37', 'category': 'standards', 'services': ['dayrehab']},
            'fee.dayservice.root': {'document': 'remuneration-dayservice', 'category': 'remuneration', 'services': ['dayservice']},
        }
        (self.root / 'legislation/record-index.json').write_text(json.dumps(entries))
        folder = self.root / 'legislation/record'
        folder.mkdir()
        for identifier in entries:
            (folder / (hashlib.sha256(identifier.encode()).hexdigest() + '.html')).write_text('<article>record</article>')
        dayrehab = self.root / 'databases/search/legal/rules/dayrehab/118.html'
        dayrehab.parent.mkdir(parents=True)
        dayrehab.write_text('<p class="scope-note">通所リハの準用relation・読み替えを含む詳細表示は'
                            f'<a href="{ORIGIN}/services/dayrehab/rules/118">サービス別ページ</a>でも確認できます。</p>')
        fee = self.root / 'databases/search/legal/rules/all/92.html'
        fee.parent.mkdir(parents=True)
        fee.write_text(f'<a href="{ORIGIN}/fees/root"><span><strong>通所介護費</strong><small>6</small></span></a>')
        result = rewrite(self.root)
        self.assertEqual(result['additional_changes']['dayrehab_scope_notes'], 1)
        self.assertEqual(result['additional_changes']['fee_root_links'], 1)
        self.assertIn('第119条の本文', dayrehab.read_text())
        self.assertIn('fees/index.html', fee.read_text())
        self.assertIn('報酬一覧', fee.read_text())
        self.assertIn('laws.e-gov.go.jp/law/411M50000100037',
                      (folder / (hashlib.sha256('ordinance37.article.119'.encode()).hexdigest() + '.html')).read_text())

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
            f'{ORIGIN}\n{ORIGIN}\n' + '  } else {\n    link.href = destination.href;\n  }\n  return link;\n'
            '      card.append(internalLink(row.title, resultHref(group, row, q)));')
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
        self.assertIn('対象：', code)
        self.assertIn('収載済み・現行性未確認', code)
        self.assertNotIn(ORIGIN, code + (search / 'qa-app.mjs').read_text())

    def test_title_only_record_is_not_presented_as_full_text(self):
        folder = self.root / 'legislation/record'
        folder.mkdir()
        identifier = 'guidance.title-only'
        filename = hashlib.sha256(identifier.encode()).hexdigest() + '.html'
        (self.root / 'legislation/record-index.json').write_text(json.dumps({identifier: {
            'document': 'guidance-unknown', 'category': 'guidance', 'services': ['dayservice']}}))
        (self.root / 'legislation/records.json').write_text(json.dumps({'records': [{
            'id': identifier, 'file': filename, 'text': '', 'document': 'guidance-unknown', 'category': 'guidance'}]}))
        listing = self.root / 'legislation/app.mjs'
        listing.write_text('const excerpt = node("p", row.text.length > 260 ? row.text.slice(0, 260) + "…" : row.text);')
        page = folder / filename
        page.write_text('<article><div class="dayservice-original" style="white-space:pre-wrap"></div></article>')
        result = rewrite(self.root)
        self.assertEqual(result['missing_record_text_labeled'], 1)
        self.assertIn('見出しのみを掲載しています。本文は未収載です。', page.read_text())
        self.assertIn('本文未収載：見出しのみを掲載しています。', listing.read_text())

    def test_unmatched_title_only_record_stops_before_any_write(self):
        identifier = 'guidance.title-only'
        filename = hashlib.sha256(identifier.encode()).hexdigest() + '.html'
        (self.root / 'legislation/record-index.json').write_text(json.dumps({identifier: {
            'document': 'different-document', 'category': 'guidance', 'services': []}}))
        (self.root / 'legislation/records.json').write_text(json.dumps({'records': [{
            'id': identifier, 'file': filename, 'text': '', 'document': 'guidance-unknown', 'category': 'guidance'}]}))
        original = self.fees.read_text()
        with self.assertRaisesRegex(RuntimeError, 'Unmatched title-only legal record'):
            rewrite(self.root)
        self.assertEqual(self.fees.read_text(), original)

    def test_partial_sources_are_labeled_without_changing_other_links(self):
        folder = self.root / 'legislation/record'
        folder.mkdir()
        rows = [
            ('notice.staffing', 'interpretation-rouki25', 'notices', '本文あり',
             'https://www.mhlw.go.jp/file/06-Seisakujouhou-12300000-Roukenkyoku/0000080875.pdf'),
            ('guidance.dayrehab', 'guidance-r6', 'guidance', '',
             'https://www.mhlw.go.jp/content/12300000/001227887.pdf'),
            ('notice.draft', 'notice-draft', 'notices', '本文あり',
             'https://www.mhlw.go.jp/content/12300000/001225905.pdf'),
            ('notice.unknown', 'unknown-doc', 'notices', '本文あり',
             'https://www.mhlw.go.jp/content/unknown.pdf'),
        ]
        index = {}
        records = []
        for identifier, document, category, text, url in rows:
            filename = hashlib.sha256(identifier.encode()).hexdigest() + '.html'
            index[identifier] = {'document': document, 'category': category, 'services': ['dayservice']}
            records.append({'id': identifier, 'file': filename, 'text': text,
                            'document': document, 'category': category})
            body = ('<div class="dayservice-original" style="white-space:pre-wrap">' + text + '</div>')
            caution = '<p>制度の改正・適用範囲・自治体ごとの扱いは、必ず原典と指定権者に確認してください。</p>'
            (folder / filename).write_text('<article>' + caution + body +
                f'<p><a href="{url}" rel="noopener noreferrer">公式原典を確認</a></p></article>')
        (self.root / 'legislation/record-index.json').write_text(json.dumps(index))
        (self.root / 'legislation/records.json').write_text(json.dumps({'records': records}))
        result = rewrite(self.root)
        self.assertEqual(result['partial_sources_labeled'], 3)
        self.assertEqual(result['missing_record_text_labeled'], 1)
        old = (folder / (hashlib.sha256('notice.staffing'.encode()).hexdigest() + '.html')).read_text()
        newer = (folder / (hashlib.sha256('guidance.dayrehab'.encode()).hexdigest() + '.html')).read_text()
        draft = (folder / (hashlib.sha256('notice.draft'.encode()).hexdigest() + '.html')).read_text()
        unknown = (folder / (hashlib.sha256('notice.unknown'.encode()).hexdigest() + '.html')).read_text()
        self.assertIn('平成27年度の改正資料（新旧対照表・抄）', old)
        self.assertIn('掲載本文とリンク先の版・範囲が異なる場合', old)
        self.assertLess(old.index('掲載本文とリンク先の版・範囲が異なる場合'), old.index('本文あり'))
        self.assertIn('令和6年度の改正資料（新旧対照表・抄）', newer)
        self.assertIn('本文は未収載です。', newer)
        self.assertIn('解釈通知の改正案（新旧比較・抄）', draft)
        self.assertIn('施行された内容とは限りません。', draft)
        self.assertLess(draft.index('施行された内容とは限りません。'), draft.index('本文あり'))
        self.assertIn('公式原典を確認', unknown)

    def test_changed_partial_source_layout_stops_before_any_write(self):
        folder = self.root / 'legislation/record'
        folder.mkdir()
        identifier = 'notice.staffing'
        filename = hashlib.sha256(identifier.encode()).hexdigest() + '.html'
        (self.root / 'legislation/record-index.json').write_text(json.dumps({identifier: {
            'document': 'interpretation-rouki25', 'category': 'notices', 'services': ['dayservice']}}))
        (self.root / 'legislation/records.json').write_text(json.dumps({'records': [{
            'id': identifier, 'file': filename, 'text': '本文',
            'document': 'interpretation-rouki25', 'category': 'notices'}]}))
        (folder / filename).write_text('<article><a href="https://www.mhlw.go.jp/file/'
            '06-Seisakujouhou-12300000-Roukenkyoku/0000080875.pdf">異なる表示</a></article>')
        original = self.fees.read_text()
        with self.assertRaisesRegex(RuntimeError, 'Unexpected notice source link layout'):
            rewrite(self.root)
        self.assertEqual(self.fees.read_text(), original)

    def test_mislinked_community_notices_show_relevant_but_incomplete_source(self):
        folder = self.root / 'legislation/record'
        folder.mkdir()
        items = {
            'community-dayservice.notice.015': '指定療養通所介護の基本方針',
            'community-dayservice.notice.019': '内容及び手続の説明及び同意',
            'community-dayservice.notice.021': '療養通所介護計画の作成',
        }
        records, index = [], {}
        for identifier, title in items.items():
            name = hashlib.sha256(identifier.encode()).hexdigest() + '.html'
            claim = '厚生労働省の過去の解釈通知全文で見出しと説明を確認。' if identifier.endswith('.019') else ''
            records.append({'id': identifier, 'file': name, 'text': claim + '掲載内容', 'title': title,
                            'document': 'notice-summary-community-dayservice', 'category': 'notices'})
            index[identifier] = {'document': 'notice-summary-community-dayservice', 'category': 'notices',
                                 'services': ['community-dayservice']}
            url = ('https://www.mhlw.go.jp/content/12301000/000750727.pdf'
                   if identifier.endswith('.021') else 'https://www.mhlw.go.jp/content/12300000/001225905.pdf')
            (folder / name).write_text('<article>'
                '<p>制度の改正・適用範囲・自治体ごとの扱いは、必ず原典と指定権者に確認してください。</p>'
                '<div class="dayservice-original" style="white-space:pre-wrap">' + claim + '掲載内容</div>'
                f'<p><a href="{url}" rel="noopener noreferrer">公式原典を確認</a></p></article>')
        (self.root / 'legislation/record-index.json').write_text(json.dumps(index))
        dataset = self.root / 'legislation/records.json'
        dataset.write_text(json.dumps({'records': records}, ensure_ascii=False))
        handbook = self.root / 'handbook/community-dayservice/example.html'
        handbook.parent.mkdir(parents=True)
        filename = hashlib.sha256('community-dayservice.notice.019'.encode()).hexdigest() + '.html'
        handbook.write_text('<p>厚生労働省の過去の解釈通知全文で見出しと説明を確認。掲載内容</p>'
            '<a href="https://www.mhlw.go.jp/content/12300000/001225905.pdf">公式原典を開く ↗</a>'
            f'<a href="../../legislation/record/{filename}">この項目へのリンク</a>')
        result = rewrite(self.root)
        self.assertEqual(result['partial_sources_labeled'], 3)
        self.assertEqual(result['additional_changes']['community_handbook_sources'], 1)
        self.assertNotIn('過去の解釈通知全文で見出しと説明を確認', dataset.read_text())
        self.assertNotIn('001225905.pdf', handbook.read_text())
        self.assertNotIn('過去の解釈通知全文で見出しと説明を確認', handbook.read_text())
        self.assertIn('原典の確認状況を見る', handbook.read_text())
        for identifier in items:
            page = (folder / (hashlib.sha256(identifier.encode()).hexdigest() + '.html')).read_text()
            if not identifier.endswith('.021'):
                self.assertIn('001227939.pdf', page)
            else:
                self.assertIn('000750727.pdf', page)
            self.assertNotIn('001225905.pdf', page)
            self.assertNotIn('過去の解釈通知全文で見出しと説明を確認', page)
            self.assertIn('省略されています', page)
            self.assertIn('平成28年の改正通知', page)
            self.assertIn('福祉医療機構掲載', page)
            self.assertIn('現行の通知全文は確認中', page)
            self.assertIn('www2.wam.go.jp', page)
            self.assertLess(page.index('省略されています'), page.index('掲載内容'))

    def test_mislinked_notice_with_different_service_stops_before_any_write(self):
        folder = self.root / 'legislation/record'
        folder.mkdir()
        identifier = 'community-dayservice.notice.015'
        filename = hashlib.sha256(identifier.encode()).hexdigest() + '.html'
        document = 'notice-summary-community-dayservice'
        (self.root / 'legislation/record-index.json').write_text(json.dumps({identifier: {
            'document': document, 'category': 'notices', 'services': ['other-service']}}))
        (self.root / 'legislation/records.json').write_text(json.dumps({'records': [{
            'id': identifier, 'file': filename, 'text': '掲載内容',
            'title': '指定療養通所介護の基本方針', 'document': document, 'category': 'notices'}]}))
        page = folder / filename
        page.write_text('<article><p><a href="https://www.mhlw.go.jp/content/12300000/001225905.pdf" '
                        'rel="noopener noreferrer">公式原典を確認</a></p></article>')
        original_fees = self.fees.read_text()
        original_page = page.read_text()
        with self.assertRaisesRegex(RuntimeError, 'Unmatched community notice'):
            rewrite(self.root)
        self.assertEqual(self.fees.read_text(), original_fees)
        self.assertEqual(page.read_text(), original_page)

    def test_unmatched_handbook_source_stops_before_any_write(self):
        handbook = self.root / 'handbook/community-dayservice/example.html'
        handbook.parent.mkdir(parents=True)
        handbook.write_text('<a href="https://www.mhlw.go.jp/content/12300000/001225905.pdf">unexpected</a>')
        original_fees = self.fees.read_text()
        with self.assertRaisesRegex(RuntimeError, 'Unmatched handbook source'):
            rewrite(self.root)
        self.assertEqual(self.fees.read_text(), original_fees)

    def test_handbook_identifies_partial_source_without_changing_its_url(self):
        handbook = self.root / 'handbook/dayservice/example.html'
        handbook.parent.mkdir(parents=True)
        url = 'https://www.mhlw.go.jp/file/06-Seisakujouhou-12300000-Roukenkyoku/0000080875.pdf'
        handbook.write_text(f'<p>掲載内容</p><a href="{url}">公式原典を開く ↗</a>')
        result = rewrite(self.root)
        self.assertEqual(result['additional_changes']['handbook_source_versions'], 1)
        self.assertIn(f'href="{url}"', handbook.read_text())
        self.assertIn('平成27年度の改正資料（新旧対照表・抄）', handbook.read_text())
        self.assertIn('<p>掲載内容</p>', handbook.read_text())

    def test_unknown_handbook_source_layout_stops_before_any_write(self):
        handbook = self.root / 'handbook/dayservice/example.html'
        handbook.parent.mkdir(parents=True)
        handbook.write_text('<a href="https://www.mhlw.go.jp/file/'
            '06-Seisakujouhou-12300000-Roukenkyoku/0000080875.pdf">異なる表示</a>')
        original = self.fees.read_text()
        with self.assertRaisesRegex(RuntimeError, 'Unexpected handbook source layout'):
            rewrite(self.root)
        self.assertEqual(self.fees.read_text(), original)

    def test_community_source_change_stops_all_publication_rewrites(self):
        handbook = self.root / 'handbook/community-dayservice/staffing.html'
        handbook.parent.mkdir(parents=True)
        handbook.write_text(CommunityStaffingOverviewTest.fixture('changed', 'manager'))
        before_handbook = handbook.read_text()
        before_fees = self.fees.read_text()
        with self.assertRaisesRegex(RuntimeError, 'Staffing source changed'):
            rewrite(self.root)
        self.assertEqual(handbook.read_text(), before_handbook)
        self.assertEqual(self.fees.read_text(), before_fees)


class CommunityStaffingOverviewTest(unittest.TestCase):
    @staticmethod
    def fixture(staff='staff', manager='manager'):
        def source(number, label, text):
            return (f'<details class="handbook-source"><summary><span class="handbook-source-label">'
                    f'{number}</span><span>{label}</span></summary>'
                    '<p class="meta">収載資料の版・施行日：2025-04-01</p>'
                    f'<p class="handbook-original">{text}</p></details>')
        return ('<article><p>未確認の説明を含みます。</p>' + community_staffing_reader.INSERT_AFTER +
                '<h3>確認すること</h3>' +
                source('第二十条', '（従業者の員数）', staff) +
                source('第二十一条', '（管理者）', manager) + '</article>')

    def test_role_guide_preserves_source_and_exceptions(self):
        values = {'第二十条': hashlib.sha256(b'staff').hexdigest(),
                  '第二十一条': hashlib.sha256(b'manager').hexdigest()}
        with patch.dict(community_staffing_reader.SOURCE_HASHES, values):
            content, count = community_staffing_reader.add_community_staffing_overview(
                self.fixture(), community_staffing_reader.PAGE)
        self.assertEqual(count, 1)
        for label in ('生活相談員', '看護職員', '介護職員', '機能訓練指導員', '管理者'):
            self.assertIn(f'>{label}</h4>', content)
        self.assertIn('2025年4月1日施行版', content)
        self.assertIn('療養通所介護と共生型には別の規定', content)
        self.assertIn('定員10人以下の特例', content)
        self.assertIn('病院・診療所・訪問看護ステーションとの連携', content)
        self.assertIn('令和6年度 国Q&amp;A Vol.1 問59', content)
        self.assertIn('後続の改正・訂正がないか確認', content)
        self.assertIn('国の基準省令の収載版では、生活相談員または介護職員のうち1人以上は常勤', content)
        self.assertIn('第3項の読替えにより、この介護職員には看護職員も含まれます', content)
        self.assertIn('横浜市の令和8年度の手引', content)
        self.assertIn('指定権者の条例・手引も確認', content)
        self.assertIn('同じ事業所で一体的に運営', content)
        self.assertIn('利用者それぞれの提供時間の合計÷利用者数', content)
        self.assertIn('（18−15）÷5＋1＝1.6', content)
        self.assertIn('5時間×1.6＝<strong>延べ8時間</strong>', content)
        self.assertIn('単位ごとに常時1人以上が従事することも別に確認', content)
        self.assertIn('はり師・きゅう師', content)
        self.assertIn('はり師・きゅう師以外の資格を持つ機能訓練指導員', content)
        self.assertIn('6か月以上', content)
        self.assertIn('基本の人員基準と、個別機能訓練加算', content)
        self.assertIn('<p class="handbook-original">staff</p>', content)
        self.assertIn('<p class="handbook-original">manager</p>', content)
        self.assertIn('id="community-staff-article20"', content)
        self.assertIn('href="#community-staff-article20"', content)
        self.assertIn('id="community-staff-article21"', content)
        self.assertLess(content.index('職種別の配置基準'), content.index('<h3>確認すること</h3>'))

    def test_other_services_are_not_modified(self):
        original = self.fixture()
        self.assertEqual(community_staffing_reader.add_community_staffing_overview(
            original, Path('handbook/dayservice/staffing.html')), (original, 0))

    def test_changed_version_is_not_used(self):
        values = {'第二十条': hashlib.sha256(b'staff').hexdigest(),
                  '第二十一条': hashlib.sha256(b'manager').hexdigest()}
        changed = self.fixture().replace('2025-04-01', '2026-04-01')
        with patch.dict(community_staffing_reader.SOURCE_HASHES, values):
            with self.assertRaisesRegex(RuntimeError, 'Staffing source changed'):
                community_staffing_reader.add_community_staffing_overview(changed, community_staffing_reader.PAGE)


class HealthFacilityStaffingReaderTest(unittest.TestCase):
    def fixture(self):
        def source(number, label, text):
            return (f'<details class="handbook-source"><summary><span class="handbook-source-label">'
                    f'{number}</span><span>{label}</span></summary>'
                    '<p class="meta">収載資料の版・施行日：2024-04-01</p>'
                    f'<p class="handbook-original">{text}</p></details>')
        return ('<article>' + health_facility_staffing_reader.INSERT_AFTER +
                f'<p>{health_facility_staffing_reader.OLD_NOTE}</p>' +
                source('第二条', '（従業者の員数）', 'staff') +
                source('第二十三条', '（管理者による管理）', 'manager') +
                source('第四十八条', '（勤務体制の確保等）', 'units') + '</article>')

    def hashes(self):
        return {key: hashlib.sha256(value.encode()).hexdigest() for key, value in
                [('第二条', 'staff'), ('第二十三条', 'manager'), ('第四十八条', 'units')]}

    def test_guide_distinguishes_facility_types_and_preserves_sources(self):
        with patch.dict(health_facility_staffing_reader.SOURCE_HASHES, self.hashes()):
            content, count = health_facility_staffing_reader.add_health_facility_staffing_overview(
                self.fixture(), health_facility_staffing_reader.PAGE)
        self.assertEqual(count, 1)
        self.assertIn('サテライト型・医療機関併設型の小規模施設', content)
        self.assertIn('入所者数ではなく<strong>入所定員</strong>', content)
        self.assertIn('7分の2程度', content)
        self.assertIn('34人分以上を常勤換算', content)
        self.assertIn('100人またはその端数を増すごとに1人は、基準省令上の<strong>標準</strong>', content)
        self.assertIn('昼間はユニットごとに常時1人以上', content)
        self.assertIn('夜間・深夜は2ユニットごとに1人以上', content)
        self.assertNotIn(health_facility_staffing_reader.OLD_NOTE, content)
        for value in ('staff', 'manager', 'units'):
            self.assertIn(f'<p class="handbook-original">{value}</p>', content)
        for anchor in health_facility_staffing_reader.SOURCE_IDS.values():
            self.assertIn(f'id="{anchor}"', content)
            self.assertIn(f'href="#{anchor}"', content)

    def test_other_services_are_untouched(self):
        content = self.fixture()
        self.assertEqual(health_facility_staffing_reader.add_health_facility_staffing_overview(
            content, Path('handbook/dayservice/staffing.html')), (content, 0))

    def test_changes_to_source_or_version_stop_publication(self):
        for changed in (self.fixture().replace('>staff</p>', '>changed</p>'),
                        self.fixture().replace('2024-04-01', '2025-04-01', 1)):
            with self.subTest(changed=changed[:100]), patch.dict(
                    health_facility_staffing_reader.SOURCE_HASHES, self.hashes()):
                with self.assertRaisesRegex(RuntimeError, 'source changed'):
                    health_facility_staffing_reader.add_health_facility_staffing_overview(
                        changed, health_facility_staffing_reader.PAGE)

    def test_missing_or_duplicate_source_stops_publication(self):
        for changed in (self.fixture().replace('第二十三条', '別の条文'),
                        self.fixture() + self.fixture()):
            with self.subTest(changed=changed[-100:]), patch.dict(
                    health_facility_staffing_reader.SOURCE_HASHES, self.hashes()):
                with self.assertRaises(RuntimeError):
                    health_facility_staffing_reader.add_health_facility_staffing_overview(
                        changed, health_facility_staffing_reader.PAGE)


class WelfareFacilityStaffingReaderTest(unittest.TestCase):
    def fixture(self):
        def source(number, label, text):
            return (f'<details class="handbook-source"><summary><span class="handbook-source-label">'
                    f'{number}</span><span>{label}</span></summary>'
                    '<p class="meta">収載資料の版・施行日：2025-04-01</p>'
                    f'<p class="handbook-original">{text}</p></details>')
        return ('<article>' + welfare_facility_staffing_reader.INSERT_AFTER +
                f'<p>{welfare_facility_staffing_reader.OLD_NOTE}</p>' +
                source('第二条', '（従業者の員数）', 'staff') +
                source('第二十一条', '（管理者による管理）', 'manager') +
                source('第四十七条', '（勤務体制の確保等）', 'units') + '</article>')

    def hashes(self):
        return {key: hashlib.sha256(value.encode()).hexdigest() for key, value in
                [('第二条', 'staff'), ('第二十一条', 'manager'), ('第四十七条', 'units')]}

    def test_roles_keep_thresholds_separate_from_total_and_exceptions(self):
        with patch.dict(welfare_facility_staffing_reader.SOURCE_HASHES, self.hashes()):
            content, count = welfare_facility_staffing_reader.add_welfare_facility_staffing_overview(
                self.fixture(), welfare_facility_staffing_reader.PAGE)
        self.assertEqual(count, 1)
        for text in ('入所者30人以下：1人以上', '30人を超え50人以下：2人以上',
                     '50人を超え130人以下：3人以上', '130人を超える部分について50人またはその端数ごとに1人',
                     '看護職員を合わせた34人分以上の<strong>内数</strong>',
                     'そのうち1人以上は常勤', '入所定員40人以下',
                     '定員だけで判断せず、連携と処遇の条件を確認',
                     '常勤の介護職員が常時1人以上介護に従事',
                     '国の基準省令第13条・第43条', '基準省令上の<strong>標準</strong>',
                     '小規模多機能型居宅介護または看護小規模多機能型居宅介護',
                     '所定の離島・過疎地域に所在し、入所定員が30人の施設',
                     '施設の入所者の処遇を適切に行えると認められるとき', '施設に介護支援専門員を置かないことができます'):
            self.assertIn(text, content)
        self.assertNotIn(welfare_facility_staffing_reader.OLD_NOTE, content)
        for text in ('staff', 'manager', 'units'):
            self.assertIn(f'<p class="handbook-original">{text}</p>', content)
        for anchor in welfare_facility_staffing_reader.SOURCE_IDS.values():
            self.assertIn(f'id="{anchor}"', content)
            self.assertIn(f'href="#{anchor}"', content)

    def test_changed_source_or_version_stops_publication(self):
        for changed in (self.fixture().replace('>staff</p>', '>changed</p>'),
                        self.fixture().replace('2025-04-01', '2026-04-01', 1)):
            with self.subTest(changed=changed[:100]), patch.dict(
                    welfare_facility_staffing_reader.SOURCE_HASHES, self.hashes()):
                with self.assertRaisesRegex(RuntimeError, 'source changed'):
                    welfare_facility_staffing_reader.add_welfare_facility_staffing_overview(
                        changed, welfare_facility_staffing_reader.PAGE)

    def test_missing_duplicate_or_other_page(self):
        original = self.fixture()
        self.assertEqual(welfare_facility_staffing_reader.add_welfare_facility_staffing_overview(
            original, Path('handbook/dayservice/staffing.html')), (original, 0))
        for changed in (original.replace('第二十一条', '別の条文'), original + original):
            with self.subTest(changed=changed[-100:]), patch.dict(
                    welfare_facility_staffing_reader.SOURCE_HASHES, self.hashes()):
                with self.assertRaises(RuntimeError):
                    welfare_facility_staffing_reader.add_welfare_facility_staffing_overview(
                        changed, welfare_facility_staffing_reader.PAGE)

    def test_care_articles_on_operations_page_are_also_guarded(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            staff = root / welfare_facility_staffing_reader.PAGE
            staff.parent.mkdir(parents=True)
            staff.write_text('staffing', encoding='utf-8')
            operations = root / welfare_facility_staffing_reader.OPERATIONS_PAGE
            def source(number, text):
                return (f'<details class="handbook-source"><summary><span class="handbook-source-label">'
                        f'{number}</span><span>（介護）</span></summary>'
                        '<p class="meta">収載資料の版・施行日：2025-04-01</p>'
                        f'<p class="handbook-original">{text}</p></details>')
            care = source('第十三条', 'ordinary') + source('第四十三条', 'unit')
            hashes = {'第十三条': hashlib.sha256(b'ordinary').hexdigest(),
                      '第四十三条': hashlib.sha256(b'unit').hexdigest()}
            with patch.dict(welfare_facility_staffing_reader.CARE_SOURCE_HASHES, hashes):
                with self.assertRaisesRegex(RuntimeError, 'Missing or unsafe'):
                    welfare_facility_staffing_reader.validate_welfare_facility_care_sources(root)
                operations.write_text(care, encoding='utf-8')
                welfare_facility_staffing_reader.validate_welfare_facility_care_sources(root)
                operations.write_text(care.replace('>ordinary</p>', '>changed</p>'), encoding='utf-8')
                with self.assertRaisesRegex(RuntimeError, 'care source changed'):
                    welfare_facility_staffing_reader.validate_welfare_facility_care_sources(root)


if __name__ == "__main__":
    unittest.main()
