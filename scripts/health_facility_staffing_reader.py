"""Reader guide bound to the published health-facility staffing articles.

Changing the underlying 2024-04-01 ordinance extract requires review of this
guide. The hashes do not establish later currentness or local applicability.
"""
from __future__ import annotations

import hashlib
import re
from pathlib import Path

PAGE = Path('handbook/elderly-health-facility/staffing.html')
INSERT_AFTER = ('<p class="handbook-quick-link"><a href="#handbook-sources-staffing">'
                'この章の関連資料へ移動 ↓</a></p>')
OLD_NOTE = ('省令第40号の通常型の範囲とユニット型第39～50条が収載されています。'
            '職員数や常勤・専従条件は施設の種類と施行版・指定権者条例によって照合が必要なため、'
            '掲載対象の範囲だけで固定数値を記載しません。')
NEW_NOTE = ('省令第40号の通常型の範囲とユニット型第39～50条を収載しています。'
            '職種別の説明は収載版に基づく案内です。施設の種類、後の改正、指定権者の条例・取扱いを必ず確認してください。')
SOURCE_HASHES = {
    '第二条': '32c81401b4126f7f9ad61c3c0e44a93cf67ba5aaf065e4c4b4d0148a5cbb427a',
    '第二十三条': '930f65e87637eb8d9ecb9f2911abfe8a634175cee76d97c3dc75205ed25d5255',
    '第四十八条': '071bead6bd69d7ca99d6ca2adebed838268c4b0e6cf3e9f32e957a20788db116',
}
SOURCE_LABELS = {'第二条': '（従業者の員数）', '第二十三条': '（管理者による管理）',
                 '第四十八条': '（勤務体制の確保等）'}
SOURCE_IDS = {'第二条': 'health-staff-article2', '第二十三条': 'health-staff-article23',
              '第四十八条': 'health-staff-article48'}

OVERVIEW = '''<section class="handbook-role" aria-labelledby="health-staff-roles">
<h3 id="health-staff-roles">職種別の配置基準</h3>
<p class="handbook-working-note">国の基準省令の2024年4月1日施行版と、発出時期を示した通知をもとに、一般的な施設の配置を整理しています。後の改正、指定権者の条例・取扱い、施設の種類や兼務の条件を適用前に確認してください。サテライト型・医療機関併設型の小規模施設には職種ごとに別の規定があります。</p>
<nav aria-label="職種別の配置基準"><ul>
<li><a href="#health-staff-doctor">医師・薬剤師</a></li>
<li><a href="#health-staff-care">看護職員・介護職員</a></li>
<li><a href="#health-staff-counselor">支援相談員</a></li>
<li><a href="#health-staff-rehab">リハビリテーション職</a></li>
<li><a href="#health-staff-dietitian">栄養士・管理栄養士</a></li>
<li><a href="#health-staff-caremanager">介護支援専門員</a></li>
<li><a href="#health-staff-others">管理者・その他の職員</a></li>
<li><a href="#health-staff-units">ユニット型の勤務体制</a></li>
</ul></nav>
<section class="handbook-role"><h4 id="health-staff-doctor">医師・薬剤師</h4>
<p><strong>医師：</strong>常勤換算で、入所者数を100で割った数以上を配置します。平成12年の国の通知は、原則として常勤医師1人以上が必要とし、病院・診療所との併設等について条件付きの取扱いを示しています。</p>
<p><strong>薬剤師：</strong>施設の実情に応じた適当数を置きます。平成12年の通知は、入所者数を300で割った数以上を標準としています。<a href="#health-staff-article2">基準第2条へ</a></p></section>
<section class="handbook-role"><h4 id="health-staff-care">看護職員・介護職員</h4>
<p>合計で、常勤換算により、入所者3人またはその端数を増すごとに1人以上を配置します。内訳は、看護職員が合計の7分の2程度、介護職員が7分の5程度をそれぞれ標準とします。</p>
<p>例えば、算定上の入所者数が100人なら、100÷3の端数を切り上げ、合計34人分以上を常勤換算で確保します。平成12年の国の通知は、一部に非常勤職員を充てる場合に、必要数の7割程度の常勤職員を確保するなどの条件を示しています。<a href="#health-staff-article2">基準第2条へ</a></p></section>
<section class="handbook-role"><h4 id="health-staff-counselor">支援相談員</h4>
<p>1人以上を置きます。入所者が100人を超える場合は、常勤の支援相談員1人に加え、超える部分を100で割った数以上を常勤換算で確保します。平成12年の国の通知は、原則として常勤職員を充てる取扱いを示しています。<a href="#health-staff-article2">基準第2条へ</a></p></section>
<section class="handbook-role"><h4 id="health-staff-rehab">理学療法士・作業療法士・言語聴覚士</h4>
<p>これらの職種について、常勤換算で入所者数を100で割った数以上を確保します。勤務表で施設の業務と併設する通所リハビリテーションの業務を区別し、それぞれの勤務時間を確認します。<a href="#health-staff-article2">基準第2条へ</a></p></section>
<section class="handbook-role"><h4 id="health-staff-dietitian">栄養士・管理栄養士</h4>
<p>入所定員100人以上の施設では1人以上を置きます。平成12年の国の通知は、常勤職員の配置と、同一敷地内の病院等との条件付き兼務を示しています。入所者数ではなく<strong>入所定員</strong>で確認します。<a href="#health-staff-article2">基準第2条へ</a></p></section>
<section class="handbook-role"><h4 id="health-staff-caremanager">介護支援専門員</h4>
<p>原則として常勤専従の者を1人以上配置し、入所者の処遇に支障がない場合には施設内の他の職務を兼ねることができます。入所者100人またはその端数を増すごとに1人は、基準省令上の<strong>標準</strong>です。<a href="#health-staff-article2">基準第2条へ</a></p></section>
<section class="handbook-role"><h4 id="health-staff-others">管理者・その他の職員</h4>
<p>管理者は原則として常勤で施設の職務に専ら従事します。管理上支障がない場合等には、他の事業所・施設の職務を兼ねる取扱いがあります。調理員・事務員等は施設の実情に応じた適当数を置きます。<a href="#health-staff-article23">管理者の基準第23条へ</a> ／ <a href="#health-staff-article2">従業者の員数の基準第2条へ</a></p></section>
<section class="handbook-role"><h4 id="health-staff-units">ユニット型の勤務体制</h4>
<p>ユニット型では、別に、昼間はユニットごとに常時1人以上、夜間・深夜は2ユニットごとに1人以上の看護職員または介護職員を配置します。ユニットごとに常勤のユニットリーダーも配置します。<a href="#health-staff-article48">基準第48条へ</a></p></section>
<p>算定に用いる入所者数は原則として前年度の平均値です。新規許可時や増減床時などは別の取扱いを確認してください。常勤換算、勤務表の作り方と兼務の条件も、施設の実態に応じて確認します。</p>
<p><a href="https://www.mhlw.go.jp/web/t_doc?dataId=00ta4388&amp;dataType=1">国の平成12年通知（人員基準の解釈）</a> ／ <a href="https://www.city.yokohama.lg.jp/kenko-iryo-fukushi/fukushi-kaigo/shakaifukushi/20150205154255.files/0112_20250613.pdf">横浜市の令和7年度集団指導資料</a>。通知や資料の後の改正・訂正と、施設を所管する指定権者の取扱いを確認してください。</p>
</section>'''


def add_health_facility_staffing_overview(content: str, path: Path) -> tuple[str, int]:
    if path != PAGE:
        return content, 0
    if (content.count(INSERT_AFTER) != 1 or content.count(OLD_NOTE) != 1 or
            'id="health-staff-roles"' in content):
        raise RuntimeError('Unexpected health facility staffing structure')

    for number, expected_hash in SOURCE_HASHES.items():
        start = ('<details class="handbook-source"><summary><span class="handbook-source-label">'
                 + number + '</span><span>' + SOURCE_LABELS[number] + '</span></summary>')
        if content.count(start) != 1:
            raise RuntimeError(f'Missing or duplicate health facility staffing source: {number}')
        pos = content.index(start)
        end = content.find('</details>', pos)
        if end < 0:
            raise RuntimeError(f'Unclosed health facility staffing source: {number}')
        record = content[pos:end]
        original = re.findall(r'<p class="handbook-original">(.*?)</p>', record, flags=re.DOTALL)
        if (len(original) != 1 or '収載資料の版・施行日：2024-04-01' not in record or
                hashlib.sha256(original[0].encode('utf-8')).hexdigest() != expected_hash):
            raise RuntimeError(f'Health facility staffing source changed; review summary before publication: {number}')
        replacement = start.replace('<summary>', f'<summary id="{SOURCE_IDS[number]}">', 1)
        content = content.replace(start, replacement, 1)

    content = content.replace(OLD_NOTE, NEW_NOTE, 1)
    return content.replace(INSERT_AFTER, INSERT_AFTER + OVERVIEW, 1), 1
