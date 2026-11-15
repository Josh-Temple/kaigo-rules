"""Staffing guide for care medical facilities tied to its source articles."""
from __future__ import annotations

import hashlib
import re
from pathlib import Path

PAGE = Path('handbook/care-medical-institution/staffing.html')
INSERT_AFTER = ('<p class="handbook-quick-link"><a href="#handbook-sources-staffing">'
                'この章の関連資料へ移動 ↓</a></p>')
OLD_NOTE = ('原典候補は平成30年厚生労働省令第5号の介護医療院基準（介護医療院の基準の参照対象一覧）。'
            '療養棟・施設類型ごとに職種の配置や兼務条件が異なる可能性を確認し、原典未照合の人員数値を本文には記載しません。'
            '掲載対象の範囲は個別適用や準用・読替えの確定ではありません。'
            '現行施行版・指定権者条例・個別事業所への適用は未確認です（作成中・未レビュー）。')
NEW_NOTE = ('原典候補は平成30年厚生労働省令第5号の介護医療院に関する基準です。'
            '職種別の説明は収載版に基づきます。療養床・施設の類型、後の改正、許可権者の条例・取扱いと'
            '個別施設への適用を確認してください（人による確認前の下書きです）。')
SOURCES = {
    '第四条': ('（従業者の員数）', 'care-medical-staff-article4',
             '066f2c0761f590f018cb6aa7e93de6b6d0f2e6797c90680915da3769444974c7'),
    '第二十六条': ('（管理者による管理）', 'care-medical-staff-article26',
                '7d8f5dbf8bdaa28960b5fbeae39977fdd49a6e24946b88503982a070b5ee4ba4'),
    '第二十七条': ('（管理者の責務）', 'care-medical-staff-article27',
                '3a3f9d7585c57ee064be11cc6e525f7fd061d01686ca5a36e13c130bbf6d72f4'),
    '第三十条': ('（勤務体制の確保等）', 'care-medical-staff-article30',
               '4a90e08c69b96f86c58685ea701960355767cadf07a5fbf2a300ddb1030d9dae'),
    '第五十二条': ('（勤務体制の確保等）', 'care-medical-staff-article52',
                '04fd2deb2e2d972e8293d30ce071b926e72704481f5565516a94ffd26e6b10f6'),
}
LAW_SOURCES = {
    Path('handbook/elderly-health-facility/staffing.html'): (
        'careact.article.95', '1fc5ee0322e41f6140aada4f52ca38786302474471981df9a955ca6740e06d05'),
    PAGE: ('careact.article.109', '97753e56636954fa4fad3a075a7d70ca26c70009709eab3345099858fa051508'),
}


def validate_facility_manager_law_sources(root: Path) -> None:
    """Tie both manager qualification summaries to the captured Act text."""
    for staffing_page, (record_id, expected_hash) in LAW_SOURCES.items():
        if not (root / staffing_page).exists():
            continue
        record_file = root / 'legislation' / 'record' / (hashlib.sha256(record_id.encode()).hexdigest() + '.html')
        if record_file.is_symlink() or not record_file.is_file() or not record_file.resolve().is_relative_to(root):
            raise RuntimeError(f'Missing or unsafe manager law source: {record_id}')
        content = record_file.read_text(encoding='utf-8')
        original = re.findall(r'<div class="dayservice-original" style="white-space:pre-wrap">(.*?)</div>',
                              content, flags=re.DOTALL)
        if len(original) != 1 or hashlib.sha256(original[0].encode()).hexdigest() != expected_hash:
            raise RuntimeError(f'Manager law source changed; review before publication: {record_id}')

OVERVIEW = '''<section class="handbook-role" aria-labelledby="care-medical-staff-roles">
<h3 id="care-medical-staff-roles">職種別の配置基準</h3>
<p class="handbook-working-note">国の基準省令の2025年11月20日施行版をもとに整理しています。Ⅰ型・Ⅱ型の療養床、医療機関併設型、併設型小規模施設の区分で条件が異なります。後の改正と許可権者の条例・取扱いを適用前に確認してください。</p>
<nav aria-label="職種別の配置基準"><ul>
<li><a href="#care-medical-staff-doctor">医師</a></li>
<li><a href="#care-medical-staff-pharmacist">薬剤師</a></li>
<li><a href="#care-medical-staff-nursing">看護職員</a></li>
<li><a href="#care-medical-staff-care">介護職員</a></li>
<li><a href="#care-medical-staff-other">リハビリ職・栄養士等</a></li>
<li><a href="#care-medical-staff-caremanager">介護支援専門員</a></li>
<li><a href="#care-medical-staff-manager">管理者</a></li>
<li><a href="#care-medical-staff-small">併設型小規模介護医療院</a></li>
<li><a href="#care-medical-staff-unit">ユニット型の勤務体制</a></li>
<li><a href="#care-medical-staff-training">研修・勤務体制</a></li>
</ul></nav>
<section class="handbook-role"><h4 id="care-medical-staff-doctor">医師</h4>
<p>一般の基準では、常勤換算で「Ⅰ型入所者数÷48」と「Ⅱ型入所者数÷100」を合計し、1人に満たない端数は切り上げ、3人未満なら3人とします。第27条第3項に基づき医師を宿直させない場合は、入所者数を100で割り、1人に満たない端数を切り上げる取扱いがあります。宿直を要しない場合の条件は、省令に加え<a href="https://www.mhlw.go.jp/kaigoiryouin/assets/docs/kaigoiryouin_3.pdf">国の解釈通知を掲載した資料</a>と、その後の改正を確認してください。</p>
<p>医療機関併設型の医師は、別に定める「Ⅰ型入所者数÷48＋Ⅱ型入所者数÷100」以上とする規定があります。さらに定員19人以下の併設型小規模施設には、併設先との連携による条件付きの例外があります。施設類型と宿直の条件を確認してください。<a href="#care-medical-staff-article4">基準第4条へ</a> ／ <a href="#care-medical-staff-article27">医師の宿直：第27条へ</a></p></section>
<section class="handbook-role"><h4 id="care-medical-staff-pharmacist">薬剤師</h4>
<p>常勤換算で「Ⅰ型入所者数÷150」と「Ⅱ型入所者数÷300」の合計以上を確保します。併設型小規模施設には、併設先と入所者の処遇に関する条件付きの例外があります。<a href="#care-medical-staff-article4">基準第4条へ</a></p></section>
<section class="handbook-role"><h4 id="care-medical-staff-nursing">看護職員</h4>
<p>看護師または准看護師を、常勤換算で入所者数を6で割った数以上確保します。介護職員とは別に計算し、ユニット型の場合は時間帯ごとの配置も確認します。<a href="#care-medical-staff-article4">基準第4条へ</a> ／ <a href="#care-medical-staff-article52">ユニット型：第52条へ</a></p></section>
<section class="handbook-role"><h4 id="care-medical-staff-care">介護職員</h4>
<p>一般の基準では、常勤換算で「Ⅰ型入所者数÷5」と「Ⅱ型入所者数÷6」の合計以上を確保します。併設型小規模施設では、入所者数を6で割った数以上とする別の基準があります。<a href="#care-medical-staff-article4">基準第4条へ</a></p></section>
<section class="handbook-role"><h4 id="care-medical-staff-other">リハビリ職・栄養士等</h4>
<p>理学療法士、作業療法士または言語聴覚士、診療放射線技師、調理員や事務員等は、施設の実情に応じた適当数を置きます。栄養士または管理栄養士は、入所定員100人以上の施設では1人以上を置きます。併設型小規模施設のリハビリ職には条件付きの別の規定があります。<a href="#care-medical-staff-article4">基準第4条へ</a></p></section>
<section class="handbook-role"><h4 id="care-medical-staff-caremanager">介護支援専門員</h4>
<p>原則として1人以上を置き、入所者100人またはその端数ごとに1人は省令上の<strong>標準</strong>です。常勤で専ら職務に従事する者とし、入所者の処遇に支障がない場合の施設内兼務や、医療機関併設型で併設先の病院・診療所の職務に従事する場合には条件があります。併設型小規模施設では実情に応じた適当数とする規定があります。<a href="#care-medical-staff-article4">基準第4条へ</a></p></section>
<section class="handbook-role"><h4 id="care-medical-staff-manager">管理者</h4>
<p>介護保険法第109条では、開設者は原則として都道府県知事の承認を受けた医師に管理させます。医師以外の者も、都道府県知事の承認を受けて管理できる規定があります（法令は2026年11月15日に確認）。<a href="https://www.mhlw.go.jp/web/t_doc?dataId=82998034&amp;dataType=0">介護保険法第109条</a></p>
<p>施設の基準では、管理者は常勤で専ら施設の職務に従事する者とします。施設の管理上支障がない場合は、他の事業所・施設等や所定のサテライト型施設の職務に従事できます。<a href="#care-medical-staff-article26">基準第26条へ</a></p></section>
<section class="handbook-role"><h4 id="care-medical-staff-small">併設型小規模介護医療院</h4>
<p>医療機関併設型のうち、入所定員19人以下の施設には、医師、薬剤師、リハビリ職、介護職員、介護支援専門員について別の基準があります。医師等を置かないことができるかは、併設先が病院か診療所か、誰が入所者の処遇を適切に行うかによって条件が異なります。定員だけで判断せず第4条第7項を確認してください。<a href="#care-medical-staff-article4">基準第4条へ</a></p></section>
<section class="handbook-role"><h4 id="care-medical-staff-unit">ユニット型の勤務体制</h4>
<p>昼間はユニットごとに常時1人以上、夜間・深夜は2ユニットごとに1人以上の介護職員または看護職員を配置し、ユニットごとに常勤のユニットリーダーを配置します。<a href="#care-medical-staff-article52">基準第52条へ</a></p></section>
<section class="handbook-role"><h4 id="care-medical-staff-training">研修・勤務体制</h4>
<p>適切なサービスを提供できる勤務体制を定め、従業者の研修の機会を確保します。認知症介護の基礎的な研修の受講に必要な措置と、看護師・介護福祉士等の資格を持つ者などの除外範囲を確認します。<a href="#care-medical-staff-article30">基準第30条へ</a></p></section>
<p>算定に用いる入所者数は原則として前年度の平均値です。新規許可時の推定数、常勤換算、勤務実績や兼務を施設の実態と照合してください。<a href="https://www.mhlw.go.jp/kaigoiryouin/about/">厚生労働省の介護医療院の案内</a>も参照できます。</p>
</section>'''


def add_care_medical_staffing_overview(content: str, path: Path) -> tuple[str, int]:
    if path != PAGE:
        return content, 0
    if (content.count(INSERT_AFTER) != 1 or content.count(OLD_NOTE) != 1 or
            'id="care-medical-staff-roles"' in content):
        raise RuntimeError('Unexpected care medical staffing structure')
    for number, (label, anchor, expected_hash) in SOURCES.items():
        start = ('<details class="handbook-source"><summary><span class="handbook-source-label">'
                 + number + '</span><span>' + label + '</span></summary>')
        if content.count(start) != 1:
            raise RuntimeError(f'Missing or duplicate care medical staffing source: {number}')
        pos = content.index(start)
        end = content.find('</details>', pos)
        if end < 0:
            raise RuntimeError(f'Unclosed care medical staffing source: {number}')
        record = content[pos:end]
        original = re.findall(r'<p class="handbook-original">(.*?)</p>', record, flags=re.DOTALL)
        if (len(original) != 1 or '収載資料の版・施行日：2025-11-20' not in record or
                hashlib.sha256(original[0].encode('utf-8')).hexdigest() != expected_hash):
            raise RuntimeError(f'Care medical staffing source changed; review summary before publication: {number}')
        content = content.replace(start, start.replace('<summary>', f'<summary id="{anchor}">', 1), 1)
    content = content.replace(OLD_NOTE, NEW_NOTE, 1)
    return content.replace(INSERT_AFTER, INSERT_AFTER + OVERVIEW, 1), 1
