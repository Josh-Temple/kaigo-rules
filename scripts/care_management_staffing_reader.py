"""Reader guide for care-management staffing based on identified source articles."""
from __future__ import annotations

import hashlib
import re
from pathlib import Path

PAGE = Path('handbook/care-management/staffing.html')
INSERT_AFTER = ('<p class="handbook-quick-link"><a href="#handbook-sources-staffing">'
                'この章の関連資料へ移動 ↓</a></p>')
OLD_NOTE = ('参照候補は省令第38号の人員・管理者関係と該当する解釈通知の収載範囲です。'
            '常勤・員数・管理者の条件や件数の取り扱いは改正の影響を受ける可能性があるため、'
            '数値をここで固定せず現行施行版・条例で確認します。')
NEW_NOTE = ('原典候補は平成11年厚生省令第38号の居宅介護支援の人員・管理者関係と解釈通知です。'
            '上記の説明は収載版に基づきます。後の改正、指定権者の条例・取扱いと事業所への適用を'
            '確認してください（人による確認前の下書きです）。')
SOURCES = {
    '第二条': ('（従業者の員数）', 'care-management-staff-article2',
              'c98684a041d0115e3b26b0df1125e15133a40e1ed41c079dae8254dd98efd8f4'),
    '第三条': ('（管理者）', 'care-management-staff-article3',
              '559e8eee4c9c415324006ebea7d6f04b0227a40fc02d4ab499b6d16112de21de'),
    '第十七条': ('（管理者の責務）', 'care-management-staff-article17',
              '3cb4b0709a4833bbb5df661407ac4908aa8ced9245a64c575b1ea6f08e43b948'),
    '第十九条': ('（勤務体制の確保）', 'care-management-staff-article19',
              'aab993e5c69cd0c7405c6eb2d1135e77a722c0a664bdae92659438d8fb5bf05a'),
}

OVERVIEW = '''<section class="handbook-role" aria-labelledby="care-management-staff-roles">
<h3 id="care-management-staff-roles">職種別の配置基準</h3>
<p class="handbook-working-note">国の基準省令の2024年4月1日施行版に基づく案内です。後の改正、指定権者の条例・取扱いと、管理者の経過措置を適用前に確認してください。</p>
<nav aria-label="職種別の配置基準"><ul>
<li><a href="#care-management-staff-caremanager">介護支援専門員</a></li>
<li><a href="#care-management-staff-count">利用者数の数え方</a></li>
<li><a href="#care-management-staff-manager">管理者</a></li>
<li><a href="#care-management-staff-transition">管理者の例外・経過措置</a></li>
<li><a href="#care-management-staff-working">勤務・連絡体制</a></li>
</ul></nav>
<section class="handbook-role"><h4 id="care-management-staff-caremanager">介護支援専門員</h4>
<p>事業所ごとに、居宅介護支援の提供に当たる常勤の介護支援専門員を1人以上置きます。事業所の利用者数が44人またはその端数を増すごとに1人を配置します。</p>
<p>国民健康保険中央会が運用・管理する所定のケアプランデータ連携システムを利用し、かつ事務職員を配置している場合は、49人またはその端数ごとに1人とする規定があります。システム利用と事務職員配置の両方を確認してください。<a href="#care-management-staff-article2">基準第2条へ</a></p>
<p>国の2024年の解釈通知の改正資料は、増員する介護支援専門員は非常勤でも差し支えないこと、事務職員は常勤でなくてもよく同一法人内の配置も認められることを示しています。業務の実情に応じた配置が必要です。緊急の受入れ等やむを得ない理由で基準を超えた場合の取扱いも、指定権者と確認してください。<a href="https://www.mhlw.go.jp/content/12300000/001221591.pdf">国の解釈通知の改正資料</a></p></section>
<section class="handbook-role"><h4 id="care-management-staff-count">利用者数の数え方</h4>
<p>基準に該当する介護予防支援を同じ事業所で行う場合は、居宅介護支援の利用者数に、当該介護予防支援の利用者数の3分の1を加えます。対象となるのは、事業者が介護予防支援の指定を併せて受ける場合、または地域包括支援センターの設置者である指定介護予防支援事業者から委託を受ける場合です。</p>
<p>例えば居宅介護支援42人と対象となる介護予防支援9人なら、基準上の利用者数は42＋9÷3＝45人です。44人の基準では2人、49人の基準を適用できる場合は1人になります。これは事業所の人員基準であり、報酬の算定区分や各担当者の取扱いは別に確認します。<a href="#care-management-staff-article2">基準第2条へ</a></p></section>
<section class="handbook-role"><h4 id="care-management-staff-manager">管理者</h4>
<p>事業所ごとに常勤の管理者を置き、原則として主任介護支援専門員とします。管理者は原則専従ですが、自分が管理する事業所の介護支援専門員の職務を兼ねる場合や、管理上支障がない範囲で他の事業所の職務を兼ねる場合には例外があります。管理者は従業者の管理、利用申込みの調整、業務実施状況の把握などを一元的に行います。<a href="#care-management-staff-article3">基準第3条へ</a> ／ <a href="#care-management-staff-article17">第17条へ</a></p></section>
<section class="handbook-role"><h4 id="care-management-staff-transition">管理者の例外・経過措置</h4>
<p>主任介護支援専門員の確保が著しく困難など、やむを得ない理由がある場合は、主任ではない介護支援専門員を管理者とする例外があります。国の2020年通知は、急な退職等の不測の事態により確保できなくなり、理由と確保計画を保険者に届け出た場合の1年間の猶予や、一定の場合の延長を示しています。対象地域の加算に関する取扱いもあります。<a href="https://www.mhlw.go.jp/web/t_doc?dataId=00tc5125&amp;dataType=1&amp;pageNo=1">国の通知を開く</a></p>
<p>別の経過措置として、2021年3月31日時点で主任介護支援専門員ではない管理者が、同じ事業所の管理者を続ける場合には、2027年3月31日まで要件の適用を猶予する取扱いがあります。期限やその後の改正、個別の適用を指定権者に確認してください。<a href="https://www.mhlw.go.jp/content/12300000/001760887.pdf">国の管理者要件に関する資料</a></p></section>
<section class="handbook-role"><h4 id="care-management-staff-working">勤務・連絡体制</h4>
<p>事業所ごとに勤務体制を定め、介護支援専門員の研修機会を確保します。担当者が訪問や兼務で不在の場合も、利用者が適切に連絡できる体制を確認します。<a href="#care-management-staff-article19">基準第19条へ</a> ／ <a href="https://www.mhlw.go.jp/content/12300000/001221591.pdf">国の解釈通知の改正資料</a></p></section>
</section>'''


def add_care_management_staffing_overview(content: str, path: Path) -> tuple[str, int]:
    if path != PAGE:
        return content, 0
    if (content.count(INSERT_AFTER) != 1 or content.count(OLD_NOTE) != 1 or
            'id="care-management-staff-roles"' in content):
        raise RuntimeError('Unexpected care management staffing structure')
    for number, (label, anchor, expected_hash) in SOURCES.items():
        start = ('<details class="handbook-source"><summary><span class="handbook-source-label">'
                 + number + '</span><span>' + label + '</span></summary>')
        if content.count(start) != 1:
            raise RuntimeError('Missing or duplicate care management source: ' + number)
        pos = content.index(start)
        end = content.find('</details>', pos)
        if end < 0:
            raise RuntimeError('Unclosed care management source: ' + number)
        record = content[pos:end]
        original = re.findall(r'<p class="handbook-original">(.*?)</p>', record, flags=re.DOTALL)
        if (len(original) != 1 or '収載資料の版・施行日：2024-04-01' not in record or
                hashlib.sha256(original[0].encode('utf-8')).hexdigest() != expected_hash):
            raise RuntimeError('Care management source changed; review before publication: ' + number)
        content = content.replace(start, start.replace('<summary>', f'<summary id="{anchor}">', 1), 1)
    content = content.replace(OLD_NOTE, NEW_NOTE, 1)
    return content.replace(INSERT_AFTER, INSERT_AFTER + OVERVIEW, 1), 1
