#!/usr/bin/env python3
"""Replace supported legacy links with existing local destinations.

No fee amounts or legal text are generated here. Unknown links are not silently
rewritten, and the operation refuses to run if the expected pages have changed.
"""
from __future__ import annotations

import html
import hashlib
import json
import posixpath
import re
import sys
from functools import lru_cache
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlsplit

if __package__:
    from .community_staffing_reader import add_community_staffing_overview
    from .health_facility_staffing_reader import add_health_facility_staffing_overview
    from .welfare_facility_staffing_reader import add_welfare_facility_staffing_overview, validate_welfare_facility_care_sources
    from .fee_version_labels import label_fee_version
    from .group_home_staffing_reader import add_group_home_staffing_overview
    from .preventive_group_home_staffing_reader import add_preventive_group_home_staffing_overview
    from .night_homevisit_manager_clarification import clarify_night_homevisit_manager
    from .care_medical_staffing_reader import add_care_medical_staffing_overview, validate_facility_manager_law_sources
    from .nursing_small_scale_roles_clarification import clarify_nursing_small_scale_roles
    from .care_management_staffing_reader import add_care_management_staffing_overview
    from .dementia_dayservice_staffing_reader import add_dementia_dayservice_staffing_overview
    from .preventive_dementia_dayservice_staffing_reader import add_preventive_dementia_dayservice_staffing_overview
    from .homebath_staffing_reader import add_homebath_staffing_overview
    from .preventive_homebath_staffing_reader import add_preventive_homebath_staffing_overview
    from .community_facility_equipment_reader import add_community_facility_equipment_overview
else:
    from community_staffing_reader import add_community_staffing_overview
    from health_facility_staffing_reader import add_health_facility_staffing_overview
    from welfare_facility_staffing_reader import add_welfare_facility_staffing_overview, validate_welfare_facility_care_sources
    from fee_version_labels import label_fee_version
    from group_home_staffing_reader import add_group_home_staffing_overview
    from preventive_group_home_staffing_reader import add_preventive_group_home_staffing_overview
    from night_homevisit_manager_clarification import clarify_night_homevisit_manager
    from care_medical_staffing_reader import add_care_medical_staffing_overview, validate_facility_manager_law_sources
    from nursing_small_scale_roles_clarification import clarify_nursing_small_scale_roles
    from care_management_staffing_reader import add_care_management_staffing_overview
    from dementia_dayservice_staffing_reader import add_dementia_dayservice_staffing_overview
    from preventive_dementia_dayservice_staffing_reader import add_preventive_dementia_dayservice_staffing_overview
    from homebath_staffing_reader import add_homebath_staffing_overview
    from preventive_homebath_staffing_reader import add_preventive_homebath_staffing_overview
    from community_facility_equipment_reader import add_community_facility_equipment_overview

ORIGIN = "https://kaigo-rules.vercel.app"
QUERY = "q=%E5%9C%B0%E5%9F%9F%E5%8C%BA%E5%88%86"
COMMON = [
    ("/rules?service=dayservice", "基準DB", "legislation/index.html?service=dayservice&category=standards", "基準DB"),
    ("/notices?service=dayservice", "通知DB", "legislation/index.html?service=dayservice&category=notices", "通知DB"),
    ("/fees/unit-price", "単価・地域区分", f"databases/search/index.html?{QUERY}", "地域区分の資料検索"),
]
PAGES = {
    "fees/index.html": COMMON + [
        ("/fees/criteria", "告示27号・95号の構造化データを見る →", "legislation/index.html?category=criteria", "告示の関連資料を探す（第27号・第95号など） →"),
        ("/fees/unit-price", "通所介護の一単位単価を見る →", f"databases/search/index.html?{QUERY}", "地域区分の関連資料を検索（一単位単価表ではありません） →"),
    ],
    "fees/guidance/index.html": COMMON + [
        ("/fees/root", "通所介護費", "fees/index.html", "通所介護の報酬一覧"),
    ],
}
ANCHOR = re.compile(r'(<a\b[^>]*?\bhref=")([^"]+)(")', re.IGNORECASE)
SIMPLE_ANCHOR = re.compile(r'(<a\b[^>]*?\bhref=")([^"]+)("[^>]*>)([^<]*)</a>', re.IGNORECASE)
FULL_ANCHOR = re.compile(r'(<a\b[^>]*?\bhref=")([^"]+)("[^>]*>)(.*?)</a>', re.IGNORECASE | re.DOTALL)
DAYREHAB_SCOPE_NOTE = re.compile(
    r'<p class="scope-note">通所リハの準用relation・読み替えを含む詳細表示は'
    r'<a href="https://kaigo-rules\.vercel\.app/services/dayrehab/rules/([0-9]+(?:-[0-9]+)*)">'
    r'サービス別ページ</a>でも確認できます。</p>')
SERVICE = re.compile(r"[a-z0-9-]+")
LEGAL_NOTICE = ("<p>収載資料には人手確認前の部分があります。準用・読替え・例外・施行日や"
                "自治体ごとの取扱いは公式原典で確認してください。</p>")
READING_NOTICE = ('<p class="notice">別のサービス名が書かれた条文は、そのまま選択したサービスに'
                  '当てはめず、準用・読替えの規定と原典を確認してください。</p>')
UNIT_PRICE_NOTICE = 'https://www.mhlw.go.jp/web/t_doc?dataId=82ab4582&dataType=0&pageNo=1'
OFFICIAL_CRITERIA = {
    'criteria-mhlw-fee-criteria95-current': 'https://www.mhlw.go.jp/web/t_doc?dataId=82ab4584&dataType=0&pageNo=1',
    'criteria-mhlw-fee-facility-criteria96-current': 'https://www.mhlw.go.jp/web/t_doc?dataId=82ab4585&dataType=0&pageNo=1',
    'criteria-mhlw-fee-notice27-base': 'https://www.mhlw.go.jp/web/t_doc?dataId=82aa0261&dataType=0&pageNo=1',
}
ORDINANCE37_SOURCE = 'https://laws.e-gov.go.jp/law/411M50000100037'
# These links are official, but the cited sources are partial or historical.
# Do not describe a redline or an older text as a current consolidated notice.
PARTIAL_NOTICE_SOURCES = {
    'https://www.mhlw.go.jp/file/06-Seisakujouhou-12300000-Roukenkyoku/0000080875.pdf':
        ('notices', '平成27年度の改正資料（新旧対照表・抄）', 'redline'),
    'https://www.mhlw.go.jp/content/12300000/000869798.pdf':
        ('notices', '令和3年度の改正資料（新旧対照表・抄）', 'redline'),
    'https://www.mhlw.go.jp/content/12300000/001227935.pdf':
        ('notices', '令和6年度の改正資料（新旧対照表・抄）', 'redline'),
    'https://www.mhlw.go.jp/content/12300000/001227887.pdf':
        ('guidance', '令和6年度の改正資料（新旧対照表・抄）', 'redline'),
    'https://www.mhlw.go.jp/web/t_doc?dataId=00ta4369&dataType=1':
        ('notices', '解釈通知（厚生労働省・後の改正は別途確認）', 'partial'),
    'https://www.mhlw.go.jp/web/t_doc?dataId=00ta4369&dataType=1&pageNo=1':
        ('notices', '解釈通知（厚生労働省・後の改正は別途確認）', 'partial'),
    # These official PDFs were inspected as new/old comparison documents.
    # Their dates are not inferred here when the document itself does not state them.
    **{url: ('notices', '改正資料（新旧対照表・抄）', 'redline') for url in (
        'https://www.mhlw.go.jp/content/12300000/001221591.pdf',
        'https://www.mhlw.go.jp/content/12300000/001221586.pdf',
        'https://www.mhlw.go.jp/content/12300000/001227942.pdf',
        'https://www.mhlw.go.jp/content/12404000/000772387.pdf',
        'https://www.mhlw.go.jp/file/06-Seisakujouhou-12300000-Roukenkyoku/0000080882.pdf',
        'https://www.mhlw.go.jp/content/12404000/001623024.pdf',
        'https://www.mhlw.go.jp/content/12300000/001227939.pdf',
        'https://www.mhlw.go.jp/content/12301000/000750727.pdf',
        'https://www.mhlw.go.jp/topics/kaigo/housyu/dl/c09.pdf',
        'https://www.mhlw.go.jp/content/12404000/001623023.pdf',
        'https://www.mhlw.go.jp/file/06-Seisakujouhou-12300000-Roukenkyoku/0000199106.pdf',
        'https://www.mhlw.go.jp/content/12304250/001453049.pdf',
        'https://www.mhlw.go.jp/content/12404000/001623026.pdf',
        'https://www.mhlw.go.jp/content/12300000/001227943.pdf',
        'https://www.mhlw.go.jp/content/12300000/001227945.pdf',
        'https://www.mhlw.go.jp/content/12300000/001227947.pdf',
    )},
    'https://www.mhlw.go.jp/content/12300000/001225905.pdf':
        ('notices', '解釈通知の改正案（新旧比較・抄）', 'draft'),
    'https://www.mhlw.go.jp/file/06-Seisakujouhou-12300000-Roukenkyoku/0000202201.pdf':
        ('notices', '平成30年の通知（後の改正は別途確認）', 'partial'),
}
MISLINKED_COMMUNITY_NOTICES = {
    'community-dayservice.notice.015': '指定療養通所介護の基本方針',
    'community-dayservice.notice.019': '内容及び手続の説明及び同意',
}
COMMUNITY_HISTORICAL_NOTICES = {
    **MISLINKED_COMMUNITY_NOTICES,
    'community-dayservice.notice.021': '療養通所介護計画の作成',
}
COMMUNITY_HISTORICAL_PDF = (
    'https://www2.wam.go.jp/gyoseiShiryou-files/resources/'
    'aaff6e9a-72ef-4fd8-b8ae-207ee20f0076/'
    '%E4%BB%8B%E8%AD%B7%E4%BF%9D%E9%99%BA%E6%9C%80%E6%96%B0%E6%83%85%E5%A0%B1Vol.524.pdf'
)
COMMUNITY_R6_REDLINE = 'https://www.mhlw.go.jp/content/12300000/001227939.pdf'
COMMUNITY_R3_REDLINE = 'https://www.mhlw.go.jp/content/12301000/000750727.pdf'
COMMUNITY_UNVERIFIED_CLAIM = '厚生労働省の過去の解釈通知全文で見出しと説明を確認。'
COMMUNITY_OLD_019 = (COMMUNITY_UNVERIFIED_CLAIM +
                     'サービス開始前に運営規程、勤務体制、緊急時対応医療機関との連絡体制、'
                     '苦情処理等の重要事項を文書で説明し同意を得る趣旨を扱う。')
COMMUNITY_CORRECTED_019 = ('指定療養通所介護の提供開始前に重要事項を文書で交付・説明し、利用者の同意を得ることなどを扱う。'
                           '国の基準省令第40条の5を参照。厚生労働省が掲載する解釈通知の該当箇所は未確認。')
COMMUNITY_OLD_LOCATOR = ('第三 地域密着型サービス／二の二／5 指定療養通所介護の事業／'
                         '(4) 運営に関する基準／④〜⑨')
COMMUNITY_CORRECTED_LOCATOR = ('第三 地域密着型サービス／二の二／5 指定療養通所介護の事業／'
                               '(4) 運営に関する基準／④、⑥〜⑨（⑤は省略）')
COMMUNITY_WRONG_SOURCE = 'https://www.mhlw.go.jp/content/12300000/001225905.pdf'

# These mappings come from the existing delegated-remuneration node identity
# map. The two notice 27 subitems are not separate published records, so the
# link explicitly says that it opens their parent item.
CRITERIA_RECORDS = {
    **{f'criteria95.dayservice.{number}': (f'notice95.item.{number}',
       'criteria-mhlw-fee-criteria95-current', '')
       for number in ('14-6', '15', '16', '17', '18-2', '19', '23', '24')},
    **{f'calc27.dayservice.1.{part}': ('notice27.item.1',
       'criteria-mhlw-fee-notice27-base', '（告示第1号全体）')
       for part in ('capacity', 'staffing')},
}


def local_href(source: Path, root: Path, target: str) -> str | None:
    parts = urlsplit(target)
    dest = root / parts.path
    if dest.is_symlink() or not dest.is_file() or not dest.resolve().is_relative_to(root):
        return None
    relative = posixpath.relpath(parts.path, source.parent.as_posix())
    return relative + ('?' + parts.query if parts.query else '')


def rewrite_simple_link(match: re.Match, source: Path, root: Path, counts: dict) -> str:
    url = urlsplit(html.unescape(match.group(2)))
    label = html.unescape(match.group(4))
    if url.scheme != 'https' or url.netloc != 'kaigo-rules.vercel.app':
        return match.group(0)
    if url.path == '/fees/criteria' and not url.query and url.fragment in CRITERIA_RECORDS:
        identifier, document, suffix = CRITERIA_RECORDS[url.fragment]
        entry = record_index(root).get(identifier)
        if (not isinstance(entry, dict) or entry.get('document') != document or
                entry.get('category') != 'criteria' or not isinstance(entry.get('services'), list) or
                'dayservice' not in entry['services']):
            return match.group(0)
        target = 'legislation/record/' + hashlib.sha256(identifier.encode()).hexdigest() + '.html'
        href = local_href(source, root, target)
        if href:
            counts['criteria_records'] += 1
            return match.group(1) + html.escape(href, quote=True) + match.group(3) + html.escape(label + suffix) + '</a>'
        return match.group(0)
    if not url.query and not url.fragment:
        simple = {
            ('/fees/unit-price', '単価・地域区分'): (f'databases/search/index.html?{QUERY}', '地域区分の資料検索'),
            ('/services/dayrehab/remuneration', '報酬DB'): ('handbook/dayrehab/remuneration.html', '基本報酬の手引'),
            ('/services/dayrehab/remuneration/guidance', '算定上の留意事項'): ('legislation/index.html?service=dayrehab&category=guidance', '算定上の留意事項の関連資料'),
            ('/services/dayservice/remuneration/guidance', '算定上の留意事項'): ('fees/guidance/index.html', '算定上の留意事項'),
            ('/services/dayservice/remuneration', '通所介護の報酬基準'): ('fees/index.html', '通所介護の報酬一覧'),
            ('/databases', '制度DBをまとめて見る →'): ('databases/search/index.html', '制度DBを検索する →'),
        }
        item = simple.get((url.path, label))
        if item:
            href = local_href(source, root, item[0])
            if href:
                counts['simple_links'] += 1
                return match.group(1) + html.escape(href, quote=True) + match.group(3) + html.escape(item[1]) + '</a>'
        # The unscoped old URL defaults to a different ordinance for some
        # services. Do not expose it as an equivalent "all" view.
        source_match = re.fullmatch(r'databases/search/legal/rules/([a-z0-9-]+)/([0-9]+(?:-[0-9]+)*)\.html', source.as_posix())
        if (source_match and source_match.group(1) != 'all' and label == 'すべて' and
                url.path == '/rules/' + source_match.group(2) and
                not (root / 'databases/search/legal/rules/all' / (source_match.group(2) + '.html')).is_file()):
            counts['unavailable_all_views'] += 1
            return '<span>全サービスでの表示は未対応</span>'
    return match.group(0)


def published_record(root: Path, identifier: str, category: str, service: str, document: str) -> str | None:
    entry = record_index(root).get(identifier)
    if (not isinstance(entry, dict) or entry.get('category') != category or
            entry.get('document') != document or not isinstance(entry.get('services'), list) or
            service not in entry['services']):
        return None
    return 'legislation/record/' + hashlib.sha256(identifier.encode()).hexdigest() + '.html'


def rewrite_scoped_link(match: re.Match, source: Path, root: Path, counts: dict) -> str:
    url = urlsplit(html.unescape(match.group(2)))
    if url.scheme != 'https' or url.netloc != 'kaigo-rules.vercel.app' or url.fragment:
        return match.group(0)
    if url.path == '/fees/root' and not url.query:
        href = local_href(source, root, 'fees/index.html')
        marker = '<strong>通所介護費</strong><small>6</small>'
        if (href and source.as_posix() == 'databases/search/legal/rules/all/92.html' and
                match.group(4).count(marker) == 1):
            counts['fee_root_links'] += 1
            body = match.group(4).replace(marker, '<strong>通所介護費</strong><small>報酬一覧</small>')
            return match.group(1) + html.escape(href, quote=True) + match.group(3) + body + '</a>'
        return match.group(0)
    route = re.fullmatch(r'/rules/([0-9]+(?:-[0-9]+)*)', url.path)
    if not route:
        return match.group(0)
    try:
        params = parse_qs(url.query, keep_blank_values=True, strict_parsing=True, max_num_fields=1)
    except ValueError:
        return match.group(0)
    if set(params) != {'service'} or len(params['service']) != 1:
        return match.group(0)
    service = params['service'][0]
    label = {'dayservice': '通所介護', 'dayrehab': '通所リハビリテーション'}.get(service)
    if not label:
        return match.group(0)
    article = route.group(1)
    if not published_record(root, 'ordinance37.article.' + article, 'standards', service, 'ordinance37'):
        return match.group(0)
    target = f'databases/search/legal/rules/all/{article}.html'
    href = local_href(source, root, target)
    if not href:
        return match.group(0)
    target_html = (root / target).read_text(encoding='utf-8')
    note = re.search(r'<section class="rule-application-note">(.*?)</section>', target_html, re.DOTALL)
    if not note or f'{label}・準用' not in note.group(1):
        return match.group(0)
    body = match.group(4)
    if source.as_posix() == target and body == label:
        counts['scoped_rule_links'] += 1
        return '<span>' + html.escape(label) + '（共通本文）</span>'
    status = '<span class="rule-status">第105条で準用</span>'
    if (source.as_posix() == 'databases/search/legal/rules/dayservice/105.html' and
            service == 'dayservice' and body.count(status) == 1):
        counts['scoped_rule_links'] += 1
        body = body.replace(status, '<span class="rule-status">第105条で準用・共通本文</span>')
        return match.group(1) + html.escape(href, quote=True) + match.group(3) + body + '</a>'
    return match.group(0)


def rewrite_dayrehab_note(match: re.Match, source: Path, root: Path, counts: dict) -> str:
    if source.as_posix() != f'databases/search/legal/rules/dayrehab/{match.group(1)}.html':
        return match.group(0)
    target = published_record(root, 'ordinance37.article.119', 'standards', 'dayrehab', 'ordinance37')
    href = local_href(source, root, target) if target else None
    if not href:
        return match.group(0)
    counts['dayrehab_scope_notes'] += 1
    return ('<p class="scope-note">通所リハに関する準用・読替えは、<a href="' +
            html.escape(href, quote=True) + '">第119条の本文</a>と原典で確認してください。</p>')


def rewrite_guide(content: str, root: Path) -> str:
    old_intro = '一単位単価の告示と、公開中の地域区分DBを分けて確認します。'
    old_description = ('公開中の一単位単価DBは通所介護向けです。他サービスは、厚生労働省告示の'
                       'サービス区分と地域区分を原文で確認してください。')
    heading = ('<h4>DB内で確認する</h4><div class="entry-links">'
               f'<a class="entry-row" href="{ORIGIN}/fees/unit-price">')
    if content.count(old_intro) != 2 or content.count(old_description) != 1 or content.count(heading) != 1:
        raise RuntimeError('Unexpected guide unit-price description')
    content = content.replace(old_intro, '一単位単価の告示と、地域区分の関連資料を確認します。')
    content = content.replace(old_description,
        '一単位単価の専用表はこのサイトでは公開していません。サービス区分と地域区分は厚生労働省の告示原文で確認してください。')
    content = content.replace(heading, heading.replace('DB内で確認する', '確認先'), 1)
    replacements = [
        ('/databases#remuneration', '報酬基準DBの入口を見る', '公開済みのサービス別報酬基準へ進みます。',
         'legislation/index.html?category=remuneration', '報酬告示の関連資料を探す', '収載済みの報酬告示を一覧から確認します。'),
        ('/databases#fee-guidance', '算定上の留意事項の入口を見る', 'サービス別に保持している算定上の留意事項へ進みます。',
         'legislation/index.html?category=guidance', '算定上の留意事項の関連資料を探す', '収載済みの関連資料を一覧から確認します。'),
        ('/databases#fee-guidance', '算定上の留意事項の入口を見る', '公開済みの算定上の留意事項DBへ進みます。',
         'legislation/index.html?category=guidance', '算定上の留意事項の関連資料を探す', '収載済みの関連資料を一覧から確認します。'),
        ('/fees/unit-price', '一単位単価・地域区分DBを見る', '現在公開中の通所介護向け地域区分・一単位単価DBを確認します。',
         UNIT_PRICE_NOTICE, '一単位単価の告示を確認する', '厚生労働省の告示でサービスと地域に応じた区分を確認します。'),
    ]
    for old_path, old_title, old_detail, target, title, detail in replacements:
        old = (f'<a class="entry-row" href="{ORIGIN}{old_path}"><span>{old_title}'
               f'<small>{old_detail}</small></span><small>開く →</small></a>')
        if content.count(old) != 1:
            raise RuntimeError(f'Expected guide link changed or duplicated: {old_path}: {old_detail}')
        href = target if target == UNIT_PRICE_NOTICE else local_href(Path('guide/index.html'), root, target)
        if not href:
            raise RuntimeError(f'Missing guide target: {target}')
        new = (f'<a class="entry-row" href="{html.escape(href, quote=True)}"><span>{title}'
               f'<small>{detail}</small></span><small>開く →</small></a>')
        content = content.replace(old, new, 1)
    return content


def label_qa_search_scopes(code: str) -> str:
    """Distinguish Q&A records without collapsing distinct service scopes."""
    anchor = '      card.append(internalLink(row.title, resultHref(group, row, q)));'
    if code.count(anchor) != 1:
        raise RuntimeError('Unexpected database search result rendering')
    addition = '''
      if (group === "qa") {
        const scope = typeof row.scope === "string" ? row.scope.trim() : "";
        card.append(element("p", (scope ? "資料上の分類：" + scope + " / " : "") + "収載済み・現行性未確認"));
      }'''
    return code.replace(anchor, anchor + addition, 1)


def label_unit_price_check_date(code: str) -> str:
    """A historical display check is not a continuing currentness guarantee."""
    old = '''        card.append(element("p", "現行性：公開条件を満たした現行資料" +
          (first.checkedAt ? " / 公式表示確認日：" + first.checkedAt : "")));'''
    new = '''        card.append(element("p", "公式表示の確認日：" +
          (first.checkedAt || "未記録") + " / その後の改正・適用は原典で確認してください。"));'''
    if code.count(old) != 1:
        raise RuntimeError('Unexpected unit price search status')
    return code.replace(old, new, 1)


def expand_unit_price_results(code: str) -> str:
    """Keep all matched regions available without overwhelming the initial view."""
    anchor = '''        card.append(element("p", matches.length + "区分が検索条件に一致 / " +
          matches.slice(0, 3).map((r) => r.regionClass + "：" + r.unitPrice.toFixed(2) + "円").join("、") +
          (matches.length > 3 ? " ほか" : "")));'''
    addition = '''
        if (matches.length > 3) {
          const details = document.createElement("details");
          details.append(element("summary", "残り" + (matches.length - 3) + "区分を表示"));
          const list = document.createElement("ul");
          for (const row of matches.slice(3)) {
            list.append(element("li", row.regionClass + "：" + row.unitPrice.toFixed(2) + "円"));
          }
          details.append(list);
          card.append(details);
        }'''
    if code.count(anchor) != 1:
        raise RuntimeError('Unexpected unit price search rendering')
    return code.replace(anchor, anchor + addition, 1)


def rewrite_search_scripts(root: Path) -> dict[Path, str]:
    """Keep dynamically generated search results on published pages or official sources."""
    search = root / 'databases/search'
    app, qa = search / 'app.mjs', search / 'qa-app.mjs'
    for path in (app, qa, search / 'global.json'):
        if path.is_symlink() or not path.is_file():
            raise RuntimeError(f'Missing or unsafe search resource: {path}')
    record_links = {}
    datasets = [search / 'global.json', *sorted(search.glob('service-*.json'))]
    for dataset in datasets:
        if dataset.is_symlink():
            raise RuntimeError('Unsafe search dataset')
        data = json.loads(dataset.read_text(encoding='utf-8'))
        for group, route, category in [('notice', '/notices', 'notices'),
                                        ('delegated', '/fees/criteria', 'criteria')]:
            for row in data.get(group, []):
                href = row.get('href', '')
                parts = urlsplit(href)
                try:
                    params = parse_qs(parts.query, keep_blank_values=True, strict_parsing=True, max_num_fields=1)
                except ValueError as error:
                    raise RuntimeError('Invalid legal search result link') from error
                if (parts.scheme or parts.netloc or parts.path != route or set(params) != {'service'} or
                        len(params['service']) != 1 or not SERVICE.fullmatch(params['service'][0]) or
                        not re.fullmatch(r'[A-Za-z0-9._:-]{1,200}', parts.fragment)):
                    raise RuntimeError('Unsupported legal search result link')
                entry = record_index(root).get(parts.fragment)
                if (not isinstance(entry, dict) or entry.get('category') != category or
                        not isinstance(entry.get('services'), list) or params['service'][0] not in entry['services']):
                    raise RuntimeError('Legal search result does not match its published scope')
                target = 'legislation/record/' + hashlib.sha256(parts.fragment.encode()).hexdigest() + '.html'
                local = local_href(Path('databases/search/index.html'), root, target)
                if not local:
                    raise RuntimeError('Legal search destination is missing')
                record_links[href] = local
    if not record_links:
        raise RuntimeError('Legal search has no verified record destinations')
    code = app.read_text(encoding='utf-8')
    anchor = 'const localQaDetails = document.querySelector(\'meta[name="kaigo-qa-local-details"]\')?.content === "true";'
    old_fallback = '  } else {\n    link.href = destination.href;\n  }\n  return link;'
    if code.count(anchor) != 1 or code.count(old_fallback) != 1 or code.count('https://kaigo-rules.vercel.app') != 2:
        raise RuntimeError('Unexpected database search implementation')
    code = code.replace(anchor, anchor + '\nconst localRecordDetails = ' + json.dumps(record_links, ensure_ascii=True, sort_keys=True) + ';', 1)
    code = code.replace('https://kaigo-rules.vercel.app', 'https://local.invalid')
    fallback = '''  } else if (localRecordDetails[destination.pathname + destination.search + destination.hash]) {
    link.href = localRecordDetails[destination.pathname + destination.search + destination.hash];
  } else if (destination.pathname === "/fees/unit-price" && !destination.hash &&
      params.every((key) => key === "service" || key === "q") &&
      params.filter((key) => key === "service").length === 1 &&
      params.filter((key) => key === "q").length <= 1 && /^[a-z0-9-]+$/.test(selectedService)) {
    link.textContent = label + "（厚生労働省の告示）";
    link.href = "https://www.mhlw.go.jp/web/t_doc?dataId=82ab4582&dataType=0&pageNo=1";
    link.rel = "noopener noreferrer";
  } else {
    return element("span", label + "（詳細ページ未収載）");
  }
  return link;'''
    code = code.replace(old_fallback, fallback, 1)
    code = label_qa_search_scopes(code)
    code = label_unit_price_check_date(code)
    code = expand_unit_price_results(code)
    code = code.replace('// This prototype does not include destination pages. Keep navigation on\n'
                        '      // the current site, and do not trust a row with an off-origin URL.',
                        '// Use verified local destinations or an explicitly labelled official source.')
    qa_code = qa.read_text(encoding='utf-8')
    old_qa = '''    const link = element("a", item.question);
    link.href = localDetails
      ? "./qa-details/" + encodeURIComponent(item.id) + (current.reader ? "/reader.html" : "/index.html")
      : "https://kaigo-rules.vercel.app/qa/" + encodeURIComponent(item.id) + (current.reader ? "?reader=1" : "");'''
    new_qa = '''    const link = element(localDetails ? "a" : "span", item.question);
    if (localDetails) {
      link.href = "./qa-details/" + encodeURIComponent(item.id) + (current.reader ? "/reader.html" : "/index.html");
    } else {
      link.textContent += "（詳細ページ未収載）";
    }'''
    if qa_code.count(old_qa) != 1:
        raise RuntimeError('Unexpected Q&A search implementation')
    qa_code = qa_code.replace(old_qa, new_qa, 1)
    return {app: code, qa: qa_code}


def add_official_record_links(root: Path) -> dict[Path, str]:
    """Add a source link only when the published record's document is known."""
    updates = {}
    for identifier, entry in record_index(root).items():
        if not isinstance(entry, dict):
            continue
        document = entry.get('document')
        if entry.get('category') == 'criteria' and document in OFFICIAL_CRITERIA:
            url, label = OFFICIAL_CRITERIA[document], '厚生労働省の告示原文を確認'
        elif (identifier == 'ordinance37.article.119' and entry.get('category') == 'standards'
              and document == 'ordinance37'):
            url, label = ORDINANCE37_SOURCE, 'e-Govで省令の原文を確認'
        else:
            continue
        filename = hashlib.sha256(identifier.encode()).hexdigest() + '.html'
        page = root / 'legislation/record' / filename
        if page.is_symlink() or not page.is_file():
            raise RuntimeError(f'Missing or unsafe official-source record: {identifier}')
        content = page.read_text(encoding='utf-8')
        if url in html.unescape(content):
            continue
        if content.count('</article>') != 1:
            raise RuntimeError(f'Unexpected official-source record layout: {identifier}')
        source = '<p><a href="' + html.escape(url, quote=True) + '">' + label + '</a></p>'
        updates[page] = content.replace('</article>', source + '</article>', 1)
    return updates


def mark_missing_record_text(root: Path, changes: dict) -> int:
    """Make existing title-only records explicit without fabricating content."""
    source = root / 'legislation/records.json'
    if not source.exists():
        return 0
    if source.is_symlink() or not source.is_file():
        raise RuntimeError('Unsafe legal records dataset')
    data = json.loads(source.read_text(encoding='utf-8'))
    if not isinstance(data, dict) or not isinstance(data.get('records'), list):
        raise RuntimeError('Invalid legal records dataset')
    placeholder = '<div class="dayservice-original" style="white-space:pre-wrap"></div>'
    warning = '<p class="notice">この資料は見出しのみを掲載しています。本文は未収載です。原典を確認してください。</p>'
    count = 0
    for row in data['records']:
        if not isinstance(row, dict) or not isinstance(row.get('text'), str) or not isinstance(row.get('id'), str):
            raise RuntimeError('Invalid legal record')
        if row['text'].strip():
            continue
        identifier = row['id']
        name = hashlib.sha256(identifier.encode()).hexdigest() + '.html'
        entry = record_index(root).get(identifier)
        if (row.get('file') != name or not isinstance(entry, dict) or
                entry.get('document') != row.get('document') or entry.get('category') != row.get('category')):
            raise RuntimeError(f'Unmatched title-only legal record: {identifier}')
        page = root / 'legislation/record' / name
        if page.is_symlink() or not page.is_file():
            raise RuntimeError(f'Missing title-only legal page: {identifier}')
        content = changes.get(page)
        if content is None:
            content = page.read_text(encoding='utf-8')
        if content.count(placeholder) != 1:
            raise RuntimeError(f'Unexpected title-only legal page layout: {identifier}')
        changes[page] = content.replace(placeholder, warning, 1)
        count += 1
    return count


def mark_missing_text_in_listing(root: Path) -> tuple[Path, str]:
    page = root / 'legislation/app.mjs'
    if page.is_symlink() or not page.is_file():
        raise RuntimeError('Missing or unsafe legal listing script')
    code = page.read_text(encoding='utf-8')
    old = 'const excerpt = node("p", row.text.length > 260 ? row.text.slice(0, 260) + "…" : row.text);'
    new = ('const excerpt = node("p", row.text.trim() ? '
           '(row.text.length > 260 ? row.text.slice(0, 260) + "…" : row.text) : '
           '"本文未収載：見出しのみを掲載しています。");')
    if code.count(old) != 1:
        raise RuntimeError('Unexpected legal listing implementation')
    return page, code.replace(old, new, 1)


def label_partial_notice_sources(root: Path, changes: dict) -> int:
    """Label known partial sources without asserting the age of other sources."""
    source = root / 'legislation/records.json'
    if not source.exists():
        return 0
    if source.is_symlink() or not source.is_file():
        raise RuntimeError('Unsafe legal records dataset')
    data = json.loads(source.read_text(encoding='utf-8'))
    if not isinstance(data, dict) or not isinstance(data.get('records'), list):
        raise RuntimeError('Invalid legal records dataset')
    count = 0
    for row in data['records']:
        if not isinstance(row, dict) or row.get('category') not in {'notices', 'guidance'}:
            continue
        identifier = row.get('id')
        if not isinstance(identifier, str):
            raise RuntimeError('Invalid legal record identifier')
        name = hashlib.sha256(identifier.encode()).hexdigest() + '.html'
        entry = record_index(root).get(identifier)
        if (row.get('file') != name or not isinstance(entry, dict) or
                entry.get('document') != row.get('document') or entry.get('category') != row.get('category')):
            raise RuntimeError(f'Unmatched notice record: {identifier}')
        page = root / 'legislation/record' / name
        if page.is_symlink() or not page.is_file():
            raise RuntimeError(f'Missing notice record page: {identifier}')
        content = changes.get(page)
        if content is None:
            content = page.read_text(encoding='utf-8')
        matched = 0
        for url, (category, label, source_type) in PARTIAL_NOTICE_SOURCES.items():
            if row['category'] != category:
                continue
            escaped = html.escape(url, quote=True)
            old = f'<p><a href="{escaped}" rel="noopener noreferrer">公式原典を確認</a></p>'
            if old not in content:
                if f'href="{escaped}"' in content:
                    raise RuntimeError(f'Unexpected notice source link layout: {identifier}')
                continue
            if content.count(old) != 1:
                raise RuntimeError(f'Duplicate notice source link: {identifier}')
            if matched:
                raise RuntimeError(f'Multiple partial notice sources: {identifier}')
            target_url = url
            if identifier in MISLINKED_COMMUNITY_NOTICES:
                if (row.get('document') != 'notice-summary-community-dayservice' or
                        row.get('title') != MISLINKED_COMMUNITY_NOTICES[identifier] or
                        entry.get('services') != ['community-dayservice']):
                    raise RuntimeError(f'Unmatched community notice: {identifier}')
                if url not in {COMMUNITY_WRONG_SOURCE, COMMUNITY_R6_REDLINE}:
                    raise RuntimeError(f'Unexpected community notice source: {identifier}')
                target_url = COMMUNITY_R6_REDLINE
                label = '令和6年度の改正資料（該当項目は省略）'
                warning = ('令和6年度の改正資料では該当箇所が省略されています。平成28年の通知も参照できますが、'
                           'その後の改正を反映した現行の通知全文は確認中です。'
                           '適用を判断する前に最新の通知と指定権者の基準を確認してください。')
            elif source_type == 'draft':
                warning = ('リンク先は改正案であり、施行された内容とは限りません。'
                           '正式な通知と後の改正、適用時点を確認してください。')
            elif source_type == 'redline':
                warning = ('改正の新旧対照表は抜粋です。掲載本文とリンク先の版・範囲が異なる場合があります。'
                           '後の改正と適用時点を確認してください。')
            else:
                warning = ('リンク先には後の改正が反映されていない場合があります。掲載本文とリンク先の版・範囲、'
                           '適用時点を確認してください。')
            if identifier in COMMUNITY_HISTORICAL_NOTICES:
                if (row.get('document') != 'notice-summary-community-dayservice' or
                        row.get('title') != COMMUNITY_HISTORICAL_NOTICES[identifier] or
                        entry.get('services') != ['community-dayservice']):
                    raise RuntimeError(f'Unmatched community historical notice: {identifier}')
                if identifier.endswith('.021'):
                    if url != COMMUNITY_R3_REDLINE:
                        raise RuntimeError(f'Unexpected community notice source: {identifier}')
                    warning = ('令和3年度の改正資料では計画作成に関する本文の一部が省略されています。'
                               '平成28年の通知も参照できますが、その後の改正を反映した現行の通知全文は確認中です。'
                               '適用を判断する前に最新の通知と指定権者の基準を確認してください。')
            replacement = (f'<p><a href="{html.escape(target_url, quote=True)}" rel="noopener noreferrer">'
                           f'{html.escape(label)}</a></p>')
            if identifier in COMMUNITY_HISTORICAL_NOTICES:
                replacement += (f'<p><a href="{html.escape(COMMUNITY_HISTORICAL_PDF, quote=True)}" '
                                'rel="noopener noreferrer">平成28年の改正通知 '
                                '（厚生労働省・福祉医療機構掲載、資料内の64〜68ページ）</a></p>')
            caution = '<p>制度の改正・適用範囲・自治体ごとの扱いは、必ず原典と指定権者に確認してください。</p>'
            if content.count(caution) != 1:
                raise RuntimeError(f'Unexpected notice caution layout: {identifier}')
            # Put the scope warning before the body, and keep the source link at its original location.
            content = content.replace(old, replacement, 1)
            content = content.replace(caution, caution + '<p class="notice">' + warning + '</p>', 1)
            matched += 1
        if matched:
            changes[page] = content
            count += matched
        elif identifier in COMMUNITY_HISTORICAL_NOTICES:
            raise RuntimeError(f'Missing community notice source: {identifier}')
    return count


def fix_community_record_claim(root: Path, changes: dict) -> None:
    """Use the corrected source summary and retain its unverified status."""
    source = root / 'legislation/records.json'
    if not source.is_file():
        return
    raw = source.read_text(encoding='utf-8')
    rows = json.loads(raw)['records']
    matches = [row for row in rows if row.get('id') == 'community-dayservice.notice.019']
    if not matches:
        return
    if len(matches) != 1:
        raise RuntimeError('Unexpected community notice verification claim')
    row = matches[0]
    page = root / 'legislation/record' / row['file']
    if page not in changes:
        raise RuntimeError('Community notice source was not corrected')
    text = row.get('text', '')
    if COMMUNITY_UNVERIFIED_CLAIM not in raw:
        # The source record may already contain the later correction.  Do not
        # treat an arbitrary missing claim as proof that it was corrected.
        if not isinstance(text, str):
            raise RuntimeError('Unexpected community notice verification claim')
        body = ('<div class="dayservice-original" style="white-space:pre-wrap">'
                + html.escape(text, quote=False) + '</div>')
        if text != COMMUNITY_CORRECTED_019 or changes[page].count(body) != 1:
            raise RuntimeError('Unexpected community notice verification claim')
        return
    if (text != COMMUNITY_OLD_019 or raw.count(COMMUNITY_OLD_019) != 1 or
            raw.count(COMMUNITY_UNVERIFIED_CLAIM) != 1):
        raise RuntimeError('Unexpected community notice verification claim')
    body = ('<div class="dayservice-original" style="white-space:pre-wrap">'
            + html.escape(COMMUNITY_OLD_019, quote=False) + '</div>')
    if changes[page].count(body) != 1:
        raise RuntimeError('Unexpected community notice body')
    changes[page] = changes[page].replace(body, body.replace(COMMUNITY_OLD_019, COMMUNITY_CORRECTED_019), 1)
    changes[source] = raw.replace(COMMUNITY_OLD_019, COMMUNITY_CORRECTED_019, 1)


def fix_community_handbook_sources(content: str, path: Path) -> tuple[str, int]:
    """Replace incorrect handbook citations with the matching record and its warning."""
    if COMMUNITY_WRONG_SOURCE not in content and COMMUNITY_R6_REDLINE not in content:
        return content, 0
    if path.parts[:2] != ('handbook', 'community-dayservice'):
        if COMMUNITY_WRONG_SOURCE in content:
            raise RuntimeError(f'Unexpected handbook source location: {path}')
        return content, 0
    count = 0
    for identifier in MISLINKED_COMMUNITY_NOTICES:
        filename = hashlib.sha256(identifier.encode()).hexdigest() + '.html'
        pairs = [(url, f'<a href="{url}">公式原典を開く ↗</a>'
                       f'<a href="../../legislation/record/{filename}">この項目へのリンク</a>')
                 for url in (COMMUNITY_WRONG_SOURCE, COMMUNITY_R6_REDLINE)]
        matched = [(url, old) for url, old in pairs if old in content]
        if len(matched) > 1 or any(content.count(old) != 1 for _, old in matched):
            raise RuntimeError(f'Duplicate handbook source: {identifier}')
        if matched:
            url, old = matched[0]
            content = content.replace(old, f'<a href="../../legislation/record/{filename}">'
                                      '原典の確認状況を見る</a>', 1)
            if identifier == 'community-dayservice.notice.019' and url == COMMUNITY_WRONG_SOURCE:
                if content.count(COMMUNITY_OLD_019) != 1:
                    raise RuntimeError('Unexpected handbook verification claim')
                content = content.replace(COMMUNITY_OLD_019, COMMUNITY_CORRECTED_019, 1)
            elif identifier == 'community-dayservice.notice.019' and content.count(COMMUNITY_CORRECTED_019) != 1:
                raise RuntimeError('Unexpected handbook notice correction')
            count += 1
    if COMMUNITY_WRONG_SOURCE in content:
        raise RuntimeError(f'Unmatched handbook source: {path}')
    return content, count


def fix_community_locator(root: Path, changes: dict) -> None:
    """Keep the 2021 notice locator from implying that omitted item ⑤ is present."""
    source = root / 'legislation/records.json'
    if not source.is_file():
        return
    raw = changes.get(source)
    if raw is None:
        raw = source.read_text(encoding='utf-8')
    rows = json.loads(raw)['records']
    matches = [row for row in rows if row.get('id') == 'community-dayservice.notice.021']
    if not matches:
        return
    if len(matches) != 1:
        raise RuntimeError('Unexpected community notice locator')
    row = matches[0]
    page = root / 'legislation/record' / row['file']
    if page not in changes:
        raise RuntimeError('Community notice source was not corrected')
    if row.get('locator') == COMMUNITY_CORRECTED_LOCATOR and raw.count(COMMUNITY_CORRECTED_LOCATOR) == 1:
        return
    if row.get('locator') != COMMUNITY_OLD_LOCATOR or raw.count(COMMUNITY_OLD_LOCATOR) != 1:
        raise RuntimeError('Unexpected community notice locator')
    changes[source] = raw.replace(COMMUNITY_OLD_LOCATOR, COMMUNITY_CORRECTED_LOCATOR, 1)


def fix_community_handbook_locator(content: str, path: Path) -> str:
    if COMMUNITY_OLD_LOCATOR not in content:
        return content
    filename = hashlib.sha256('community-dayservice.notice.021'.encode()).hexdigest() + '.html'
    link = f'<a href="../../legislation/record/{filename}">この項目へのリンク</a>'
    if (path.parts[:2] != ('handbook', 'community-dayservice') or
            content.count(COMMUNITY_OLD_LOCATOR) != 1 or content.count(link) != 1):
        raise RuntimeError(f'Unexpected community handbook locator: {path}')
    return content.replace(COMMUNITY_OLD_LOCATOR, COMMUNITY_CORRECTED_LOCATOR, 1)


def label_handbook_source_versions(content: str, path: Path) -> tuple[str, int]:
    """Identify known partial sources at their point of use in the handbook."""
    count = 0
    for url, (_, label, _) in PARTIAL_NOTICE_SOURCES.items():
        if url == COMMUNITY_WRONG_SOURCE:
            continue
        href = html.escape(url, quote=True)
        old = f'<a href="{href}">公式原典を開く ↗</a>'
        n = content.count(old)
        if content.count(f'href="{href}"') != n:
            raise RuntimeError(f'Unexpected handbook source layout: {path}')
        if n:
            content = content.replace(old, f'<a href="{href}">{html.escape(label)} ↗</a>')
            count += n
    return content, count


@lru_cache(maxsize=4)
def record_index(root: Path) -> dict:
    path = root / "legislation/record-index.json"
    if path.is_symlink() or not path.is_file():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or len(data) > 100000:
        raise RuntimeError("Invalid legislation record index")
    return data


def rewrite_index_link(match: re.Match, source: Path, root: Path, counts: dict) -> str:
    url = urlsplit(html.unescape(match.group(2)))
    if (url.scheme != "https" or url.netloc != "kaigo-rules.vercel.app" or
            url.path not in {"/rules", "/law", "/notices"}):
        return match.group(0)
    try:
        params = parse_qs(url.query, keep_blank_values=True, strict_parsing=True, max_num_fields=2)
    except ValueError:
        return match.group(0)
    if set(params) - {"service"} or any(len(v) != 1 for v in params.values()):
        return match.group(0)
    service = params.get("service", [""])[0]
    if service and (not SERVICE.fullmatch(service) or
                    not (root / "services" / service / "index.html").is_file()):
        return match.group(0)
    if "service" in params and not service:
        return match.group(0)
    if url.fragment:
        if url.path != "/notices":
            return match.group(0)
        identifier = unquote(url.fragment)
        if not re.fullmatch(r"[A-Za-z0-9._:-]{1,200}", identifier):
            return match.group(0)
        entry = record_index(root).get(identifier)
        if (not isinstance(entry, dict) or entry.get("category") != "notices" or
                not isinstance(entry.get("services"), list) or
                (service and service not in entry["services"])):
            return match.group(0)
        target = "legislation/record/" + hashlib.sha256(identifier.encode("utf-8")).hexdigest() + ".html"
        destination = root / target
        if destination.is_symlink() or not destination.is_file():
            return match.group(0)
        relative = posixpath.relpath(target, source.parent.as_posix())
        counts["notice_records"] += 1
        return match.group(1) + html.escape(relative, quote=True) + match.group(3)
    target = root / "legislation/index.html"
    if target.is_symlink() or not target.is_file():
        raise RuntimeError("Local legislation index is missing or unsafe")
    category = {"/rules": "standards", "/law": "law", "/notices": "notices"}[url.path]
    query = (("service=" + service + "&") if service else "") + "category=" + category
    relative = posixpath.relpath("legislation/index.html", source.parent.as_posix())
    counts[category] += 1
    return match.group(1) + html.escape(relative + "?" + query, quote=True) + match.group(3)


def clarify_handbook_review_status(content: str) -> tuple[str, int]:
    """Explain known internal status markers without changing their meaning."""
    replacements = {
        '（DRAFT_UNREVIEWED）': '（人による確認前の下書きです）',
        '現在の確認状態は検証状態（NOT_VERIFIED）、現行性（NOT_ESTABLISHED）、'
        '人手レビュー（NOT_REVIEWED）として扱い、更新時は差分と確認根拠を残してください。':
            '現在、資料の内容と現行性は未確認で、人による確認も行われていません。',
    }
    count = 0

    def replace_text(match: re.Match) -> str:
        nonlocal count
        opening, text, closing = match.groups()
        for before, after in replacements.items():
            count += text.count(before)
            text = text.replace(before, after)
        return opening + text + closing

    # Limit substitutions to plain paragraph text, not attributes, scripts,
    # citations or any markup nested inside a paragraph.
    result = re.sub(r'(<p(?:\s[^>]*)?>)([^<>]*)(</p>)', replace_text, content, flags=re.IGNORECASE)
    return result, count


def rewrite(root: Path) -> dict:
    if root.is_symlink():
        raise RuntimeError("Site root must not be a symbolic link")
    root = root.resolve(strict=True)
    if not root.is_dir():
        raise RuntimeError("Site root is not a directory")
    validate_welfare_facility_care_sources(root)
    validate_facility_manager_law_sources(root)
    changes = {}
    for source, links in PAGES.items():
        path = root / source
        if path.is_symlink() or not path.is_file():
            raise RuntimeError(f"Expected fee page is missing or unsafe: {source}")
        before = path.read_text(encoding="utf-8")
        after = before
        for old_path, old_label, target, label in links:
            target_parts = urlsplit(target)
            target_path = root / target_parts.path
            if target_path.is_symlink() or not target_path.is_file() or not target_path.resolve().is_relative_to(root):
                raise RuntimeError(f"Local fee navigation target missing or unsafe: {target_parts.path}")
            old_anchor = f'<a href="{ORIGIN}{old_path}">{old_label}</a>'
            if after.count(old_anchor) != 1:
                raise RuntimeError(f"Expected legacy fee link changed or is duplicated: {source}: {old_path}")
            relative = posixpath.relpath(target_parts.path, posixpath.dirname(source))
            href = relative + ("?" + target_parts.query if target_parts.query else "")
            new_anchor = f'<a href="{html.escape(href, quote=True)}">{html.escape(label)}</a>'
            after = after.replace(old_anchor, new_anchor, 1)
        if f'href="{ORIGIN}/' in after:
            raise RuntimeError(f"An unrecognized legacy link remains on {source}")
        changes[path] = after
    legal_page = root / "legislation/index.html"
    if legal_page.is_symlink() or not legal_page.is_file():
        raise RuntimeError("Local legislation index is missing or unsafe")
    legal_html = legal_page.read_text(encoding="utf-8")
    if legal_html.count(LEGAL_NOTICE) != 1 or READING_NOTICE in legal_html:
        raise RuntimeError("Unexpected legislation index caution")
    changes[legal_page] = legal_html.replace(LEGAL_NOTICE, LEGAL_NOTICE + READING_NOTICE, 1)
    guide = root / 'guide/index.html'
    if guide.exists():
        if guide.is_symlink() or not guide.is_file():
            raise RuntimeError('Guide page is unsafe')
        changes[guide] = rewrite_guide(guide.read_text(encoding='utf-8'), root)
    if (root / 'databases/search/app.mjs').exists() or (root / 'databases/search/qa-app.mjs').exists():
        changes.update(rewrite_search_scripts(root))
    if (root / 'legislation/record-index.json').is_file():
        changes.update(add_official_record_links(root))
    missing_text_count = mark_missing_record_text(root, changes)
    partial_source_count = label_partial_notice_sources(root, changes)
    fix_community_record_claim(root, changes)
    fix_community_locator(root, changes)
    if (root / 'legislation/app.mjs').exists():
        script, content = mark_missing_text_in_listing(root)
        changes[script] = content
    counts = {"standards": 0, "law": 0, "notices": 0, "notice_records": 0}
    extra_counts = {'criteria_records': 0, 'simple_links': 0, 'unavailable_all_views': 0,
                    'scoped_rule_links': 0, 'dayrehab_scope_notes': 0, 'fee_root_links': 0,
                    'community_handbook_sources': 0, 'handbook_source_versions': 0,
                    'handbook_review_status': 0, 'community_staffing_overview': 0,
                    'health_facility_staffing_overview': 0, 'welfare_facility_staffing_overview': 0,
                    'fee_root_version_labels': 0, 'fee_detail_version_labels': 0,
                    'group_home_staffing_overview': 0, 'preventive_group_home_staffing_overview': 0,
                    'night_homevisit_manager': 0, 'care_medical_staffing_overview': 0,
                    'nursing_small_scale_roles': 0, 'care_management_staffing_overview': 0,
                    'dementia_dayservice_staffing_overview': 0, 'preventive_dementia_dayservice_staffing_overview': 0, 'homebath_staffing_overview': 0, 'preventive_homebath_staffing_overview': 0, 'community_facility_equipment_overview': 0}
    for path in root.rglob("*.html"):
        if path.is_symlink():
            raise RuntimeError(f"Symbolic link in site output: {path}")
        before = changes.get(path)
        if before is None:
            before = path.read_text(encoding="utf-8")
        after = ANCHOR.sub(lambda m: rewrite_index_link(m, path.relative_to(root), root, counts), before)
        after = SIMPLE_ANCHOR.sub(lambda m: rewrite_simple_link(m, path.relative_to(root), root, extra_counts), after)
        after = DAYREHAB_SCOPE_NOTE.sub(lambda m: rewrite_dayrehab_note(m, path.relative_to(root), root, extra_counts), after)
        after = FULL_ANCHOR.sub(lambda m: rewrite_scoped_link(m, path.relative_to(root), root, extra_counts), after)
        if path.relative_to(root).parts[0] == 'fees':
            after, label_kind = label_fee_version(after, path.relative_to(root))
            if label_kind:
                extra_counts[label_kind] += 1
        if path.relative_to(root).parts[0] == 'handbook':
            after, n = fix_community_handbook_sources(after, path.relative_to(root))
            extra_counts['community_handbook_sources'] += n
            after = fix_community_handbook_locator(after, path.relative_to(root))
            after, n = label_handbook_source_versions(after, path.relative_to(root))
            extra_counts['handbook_source_versions'] += n
            after, n = clarify_handbook_review_status(after)
            extra_counts['handbook_review_status'] += n
            after, n = add_community_staffing_overview(after, path.relative_to(root))
            extra_counts['community_staffing_overview'] += n
            after, n = add_health_facility_staffing_overview(after, path.relative_to(root))
            extra_counts['health_facility_staffing_overview'] += n
            after, n = add_welfare_facility_staffing_overview(after, path.relative_to(root))
            extra_counts['welfare_facility_staffing_overview'] += n
            after, n = add_group_home_staffing_overview(after, path.relative_to(root))
            extra_counts['group_home_staffing_overview'] += n
            after, n = add_preventive_group_home_staffing_overview(after, path.relative_to(root))
            extra_counts['preventive_group_home_staffing_overview'] += n
            after, n = clarify_night_homevisit_manager(after, path.relative_to(root))
            extra_counts['night_homevisit_manager'] += n
            after, n = add_care_medical_staffing_overview(after, path.relative_to(root))
            extra_counts['care_medical_staffing_overview'] += n
            after, n = clarify_nursing_small_scale_roles(after, path.relative_to(root))
            extra_counts['nursing_small_scale_roles'] += n
            after, n = add_care_management_staffing_overview(after, path.relative_to(root))
            extra_counts['care_management_staffing_overview'] += n
            after, n = add_dementia_dayservice_staffing_overview(after, path.relative_to(root))
            extra_counts['dementia_dayservice_staffing_overview'] += n
            after, n = add_preventive_dementia_dayservice_staffing_overview(after, path.relative_to(root))
            extra_counts['preventive_dementia_dayservice_staffing_overview'] += n
            after, n = add_homebath_staffing_overview(after, path.relative_to(root))
            extra_counts['homebath_staffing_overview'] += n
            after, n = add_preventive_homebath_staffing_overview(after, path.relative_to(root))
            extra_counts['preventive_homebath_staffing_overview'] += n
            after, n = add_community_facility_equipment_overview(after, path.relative_to(root))
            extra_counts['community_facility_equipment_overview'] += n
        if COMMUNITY_UNVERIFIED_CLAIM in after:
            raise RuntimeError(f'Unsupported community verification claim remains: {path.relative_to(root)}')
        if after != before:
            changes[path] = after
    # Validate the entire plan before changing any page. The build pipeline
    # subsequently audits all final local links before deploying the artifact.
    for path, after in changes.items():
        path.write_text(after, encoding="utf-8")
    return {"pages_changed": sum(path.suffix == '.html' for path in changes),
            "search_scripts_changed": sum(path.suffix == '.mjs' for path in changes),
            "missing_record_text_labeled": missing_text_count,
            "partial_sources_labeled": partial_source_count,
            "fee_links_changed": sum(map(len, PAGES.values())),
            "index_links_changed": counts, "additional_changes": extra_counts}


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: rewrite_public_navigation.py SITE_DIRECTORY")
    print(json.dumps(rewrite(Path(sys.argv[1])), ensure_ascii=False))
