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


def rewrite(root: Path) -> dict:
    if root.is_symlink():
        raise RuntimeError("Site root must not be a symbolic link")
    root = root.resolve(strict=True)
    if not root.is_dir():
        raise RuntimeError("Site root is not a directory")
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
    if (root / 'legislation/app.mjs').exists():
        script, content = mark_missing_text_in_listing(root)
        changes[script] = content
    counts = {"standards": 0, "law": 0, "notices": 0, "notice_records": 0}
    extra_counts = {'criteria_records': 0, 'simple_links': 0, 'unavailable_all_views': 0,
                    'scoped_rule_links': 0, 'dayrehab_scope_notes': 0, 'fee_root_links': 0}
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
        if after != before:
            changes[path] = after
    # Validate the entire plan before changing any page. The build pipeline
    # subsequently audits all final local links before deploying the artifact.
    for path, after in changes.items():
        path.write_text(after, encoding="utf-8")
    return {"pages_changed": sum(path.suffix == '.html' for path in changes),
            "search_scripts_changed": sum(path.suffix == '.mjs' for path in changes),
            "missing_record_text_labeled": missing_text_count,
            "fee_links_changed": sum(map(len, PAGES.values())),
            "index_links_changed": counts, "additional_changes": extra_counts}


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: rewrite_public_navigation.py SITE_DIRECTORY")
    print(json.dumps(rewrite(Path(sys.argv[1])), ensure_ascii=False))
