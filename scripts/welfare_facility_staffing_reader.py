"""Staffing guide tied to the published welfare-facility ordinance extract."""
from __future__ import annotations

import hashlib
import re
from pathlib import Path

PAGE = Path('handbook/elderly-welfare-facility/staffing.html')
INSERT_AFTER = ('<p class="handbook-quick-link"><a href="#handbook-sources-staffing">'
                'この章の関連資料へ移動 ↓</a></p>')
OLD_NOTE = ('原典候補は平成11年厚生省令第39号の介護老人福祉施設基準（介護老人福祉施設の基準の参照対象一覧）。'
            '常勤・兼務・従来型とユニット型等の条件は施設基準の該当する類型で確認し、数値を原典に照合せず転記しません。'
            '収載された対象範囲はサービスへの適用確定を意味しません。現行施行版・指定権者条例・個別施設への適用は未確認です'
            '（作成中・未レビュー）。')
NEW_NOTE = ('原典候補は平成11年厚生省令第39号の指定介護老人福祉施設基準です。'
            '職種別の説明は収載版に基づきます。収載された対象範囲はサービスへの適用確定を意味しません。'
            '後の改正、指定権者の条例と個別施設への適用を確認してください（人による確認前の下書きです）。')
SOURCE_HASHES = {
    '第二条': 'e8186562db186851384a8a23eb1be12450e8a919f4b38a8430ebb3b9aea16be9',
    '第二十一条': '0d56c1baad1c3fcde0a8836c14c75e3e6e5165acbc4628518b800ad820f883df',
    '第四十七条': '39f483ad790b754021a2f647728136bfa178baaf454d8872c8b496fd96953eef',
}
SOURCE_LABELS = {'第二条': '（従業者の員数）', '第二十一条': '（管理者による管理）',
                 '第四十七条': '（勤務体制の確保等）'}
SOURCE_IDS = {'第二条': 'welfare-staff-article2', '第二十一条': 'welfare-staff-article21',
              '第四十七条': 'welfare-staff-article47'}

OVERVIEW = '''<section class="handbook-role" aria-labelledby="welfare-staff-roles">
<h3 id="welfare-staff-roles">職種別の配置基準</h3>
<p class="handbook-working-note">国の基準省令の2025年4月1日施行版をもとに、指定介護老人福祉施設の配置を整理しています。後の改正、指定権者の条例・取扱い、施設の種類や兼務の条件を適用前に確認してください。サテライト型や離島・過疎地域等の施設には、条件付きの別の規定があります。</p>
<nav aria-label="職種別の配置基準"><ul>
<li><a href="#welfare-staff-doctor">医師</a></li>
<li><a href="#welfare-staff-counselor">生活相談員</a></li>
<li><a href="#welfare-staff-care">介護職員・看護職員</a></li>
<li><a href="#welfare-staff-nursing">看護職員の人数</a></li>
<li><a href="#welfare-staff-dietitian">栄養士・管理栄養士</a></li>
<li><a href="#welfare-staff-training">機能訓練指導員</a></li>
<li><a href="#welfare-staff-caremanager">介護支援専門員</a></li>
<li><a href="#welfare-staff-manager">管理者</a></li>
<li><a href="#welfare-staff-units">ユニット型の勤務体制</a></li>
</ul></nav>
<section class="handbook-role"><h4 id="welfare-staff-doctor">医師</h4>
<p>入所者の健康管理と療養上の指導を行うために必要な人数を置きます。サテライト型居住施設の本体施設に当たる場合には、算定対象となる入所者数の取扱いを確認します。<a href="#welfare-staff-article2">基準第2条へ</a></p></section>
<section class="handbook-role"><h4 id="welfare-staff-counselor">生活相談員</h4>
<p>入所者100人またはその端数を増すごとに1人以上を置きます。生活相談員は常勤の者とされています。算定上の入所者数と勤務表、資格を確認します。<a href="#welfare-staff-article2">基準第2条へ</a></p></section>
<section class="handbook-role"><h4 id="welfare-staff-care">介護職員・看護職員の合計</h4>
<p>合計で、常勤換算により、入所者3人またはその端数を増すごとに1人以上を配置します。例えば、算定上の入所者数が100人なら、100÷3の端数を切り上げ、合計34人分以上を常勤換算で確保します。</p>
<p>合計人数に加え、下の看護職員の人数と、夜間を含む勤務体制を確認します。常勤の介護職員が常時1人以上介護に従事することは、介護の実施に関する基準でも定められています。<a href="#welfare-staff-article2">基準第2条へ</a> ／ <a href="https://www.mhlw.go.jp/web/t_doc?dataId=82999406&amp;dataType=0&amp;pageNo=1">国の基準省令第13条・第43条</a></p></section>
<section class="handbook-role"><h4 id="welfare-staff-nursing">看護職員の人数</h4>
<p>看護職員は、次の人数以上を<strong>常勤換算</strong>で確保し、そのうち1人以上は常勤の者とします。</p>
<ul><li>入所者30人以下：1人以上</li><li>30人を超え50人以下：2人以上</li><li>50人を超え130人以下：3人以上</li><li>130人を超える場合：3人に、130人を超える部分について50人またはその端数ごとに1人を加えた数以上</li></ul>
<p>入所者100人の例では、看護職員は常勤換算で3人以上です。これは、介護職員と看護職員を合わせた34人分以上の<strong>内数</strong>です。<a href="#welfare-staff-article2">基準第2条へ</a></p></section>
<section class="handbook-role"><h4 id="welfare-staff-dietitian">栄養士・管理栄養士</h4>
<p>1人以上を置きます。ただし、入所定員40人以下の施設で、他の社会福祉施設等の栄養士・管理栄養士との連携により効果的な運営が期待でき、入所者の処遇に支障がない場合は、置かないことができる規定があります。定員だけで判断せず、連携と処遇の条件を確認します。<a href="#welfare-staff-article2">基準第2条へ</a></p></section>
<section class="handbook-role"><h4 id="welfare-staff-training">機能訓練指導員</h4>
<p>1人以上を置き、日常生活に必要な機能の改善や低下防止の訓練を行う能力を有する者とします。施設内の他の職務に従事することができます。資格と兼務の取扱いは通知と指定権者の基準を確認します。<a href="#welfare-staff-article2">基準第2条へ</a></p></section>
<section class="handbook-role"><h4 id="welfare-staff-caremanager">介護支援専門員</h4>
<p>常勤で専ら職務に従事する者を1人以上置きます。入所者100人またはその端数を増すごとに1人は、基準省令上の<strong>標準</strong>です。入所者の処遇に支障がない場合、施設内の他の職務を兼ねることができます。<a href="#welfare-staff-article2">基準第2条へ</a></p></section>
<section class="handbook-role"><h4 id="welfare-staff-manager">管理者</h4>
<p>常勤で施設の職務に専ら従事する者を置きます。管理上支障がない場合には、他の事業所・施設や当該施設のサテライト型居住施設の職務を兼ねることができます。<a href="#welfare-staff-article21">基準第21条へ</a></p></section>
<section class="handbook-role"><h4 id="welfare-staff-units">ユニット型の勤務体制</h4>
<p>ユニット型では、昼間はユニットごとに常時1人以上、夜間・深夜は2ユニットごとに1人以上の介護職員または看護職員を配置し、ユニットごとに常勤のユニットリーダーを配置します。常勤の介護職員の常時従事も別に確認します。<a href="#welfare-staff-article47">基準第47条へ</a></p></section>
<p>算定に用いる入所者数は原則として前年度の平均値です。新規指定時や増減床時などは別の取扱いを確認してください。常勤換算、勤務表、兼務や夜間配置は、施設の実態に応じて確認します。</p>
<p><a href="https://www.mhlw.go.jp/web/t_doc?dataId=00ta4387&amp;dataType=1">国の平成12年通知（人員基準の解釈）</a>。後の改正・訂正と指定権者の取扱いを確認してください。</p>
</section>'''


def add_welfare_facility_staffing_overview(content: str, path: Path) -> tuple[str, int]:
    if path != PAGE:
        return content, 0
    if (content.count(INSERT_AFTER) != 1 or content.count(OLD_NOTE) != 1 or
            'id="welfare-staff-roles"' in content):
        raise RuntimeError('Unexpected welfare facility staffing structure')

    for number, expected_hash in SOURCE_HASHES.items():
        start = ('<details class="handbook-source"><summary><span class="handbook-source-label">'
                 + number + '</span><span>' + SOURCE_LABELS[number] + '</span></summary>')
        if content.count(start) != 1:
            raise RuntimeError(f'Missing or duplicate welfare facility staffing source: {number}')
        pos = content.index(start)
        end = content.find('</details>', pos)
        if end < 0:
            raise RuntimeError(f'Unclosed welfare facility staffing source: {number}')
        record = content[pos:end]
        original = re.findall(r'<p class="handbook-original">(.*?)</p>', record, flags=re.DOTALL)
        if (len(original) != 1 or '収載資料の版・施行日：2025-04-01' not in record or
                hashlib.sha256(original[0].encode('utf-8')).hexdigest() != expected_hash):
            raise RuntimeError(f'Welfare facility staffing source changed; review summary before publication: {number}')
        content = content.replace(start, start.replace('<summary>', f'<summary id="{SOURCE_IDS[number]}">', 1), 1)

    content = content.replace(OLD_NOTE, NEW_NOTE, 1)
    return content.replace(INSERT_AFTER, INSERT_AFTER + OVERVIEW, 1), 1
