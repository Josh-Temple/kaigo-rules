"""Reader guide to the identified national preventive dementia day-service staffing rules."""
from __future__ import annotations

import hashlib
import re
from pathlib import Path

PAGE = Path('handbook/preventive-dementia-dayservice/staffing.html')
INSERT_AFTER = ('<p class="handbook-quick-link"><a href="#handbook-sources-staffing">'
                'この章の関連資料へ移動 ↓</a></p>')
# National ordinance No. 36, 2024-04-01 source extract. Hashes bind the
# explanation to the actual published text, not to a claim of currentness.
SOURCES = {
    '第五条': ('（従業者の員数）', 'preventive-dementia-day-staff-article5',
                 'a97bcbca47d3c09229b2190aca315d1d3192c6548d49b87c94fd6f2a5f6df395'),
    '第六条': ('（管理者）', 'preventive-dementia-day-staff-article6',
                 'f6ca0a5583f9d8291ac55e7bafe783f3f72e7476b9ec4fe2784b2306b3550497'),
    '第八条': ('（従業者の員数）', 'preventive-dementia-day-staff-article8',
                 '4edbaba1e4153dc86c9fddea2f6d1fff76874283ea90acfea7bae61e1d08a2aa'),
    '第十条': ('（管理者）', 'preventive-dementia-day-staff-article10',
                 '73f1dd1fe1509eab1cc3bc579716a0b194d6e8345343633c2e4292c1a8150f73'),
}

OVERVIEW = '''<section class="handbook-role" aria-labelledby="preventive-dementia-day-staff-roles">
<h3 id="preventive-dementia-day-staff-roles">類型・職種別の配置基準</h3>
<p class="handbook-working-note">介護予防に関する国の基準省令の2024年4月1日施行版をもとに整理しています。単独型・併設型と共用型では基準が異なります。後の改正、指定権者の条例・取扱いと個別の適用を確認してください。</p>
<nav aria-label="類型・職種別の配置基準"><ul>
<li><a href="#preventive-dementia-day-staff-consultant">単独型・併設型の生活相談員</a></li>
<li><a href="#preventive-dementia-day-staff-care">単独型・併設型の看護職員・介護職員</a></li>
<li><a href="#preventive-dementia-day-staff-training">単独型・併設型の機能訓練指導員</a></li>
<li><a href="#preventive-dementia-day-staff-manager">単独型・併設型の管理者</a></li>
<li><a href="#preventive-dementia-day-staff-shared">共用型の人員・管理者</a></li>
</ul></nav>
<section class="handbook-role"><h4 id="preventive-dementia-day-staff-consultant">生活相談員（単独型・併設型）</h4>
<p>提供日ごとに、サービスの提供に専ら当たる生活相談員の勤務時間の合計を、事業所の提供時間数で割った数が1以上となるように配置します。</p>
<p>提供日ごとの時間帯と勤務表を照合し、資格や兼務の取扱いも確認してください。<a href="#preventive-dementia-day-staff-article5">基準第5条へ</a></p></section>
<section class="handbook-role"><h4 id="preventive-dementia-day-staff-care">看護職員または介護職員（単独型・併設型）</h4>
<p>提供単位ごとに、サービスの提供に専ら当たる看護職員または介護職員を1人以上置きます。また、その勤務時間の合計を単位の提供時間数で割った数が1以上となるよう、必要な人数を配置します。</p>
<p>時間数の計算とは別に、単位ごとに看護職員または介護職員が常時1人以上従事する必要があります。利用者の処遇に支障がない場合は、他の単位との兼務に関する規定があります。<a href="#preventive-dementia-day-staff-article5">基準第5条へ</a></p>
<p>生活相談員、看護職員または介護職員のうち1人以上は常勤です。</p></section>
<section class="handbook-role"><h4 id="preventive-dementia-day-staff-training">機能訓練指導員（単独型・併設型）</h4>
<p>1人以上を置きます。日常生活に必要な機能の低下を防ぐ訓練を行う能力を有する者とされ、当該事業所の他の職務に従事することもできます。資格や兼務の具体的な取扱いは確認してください。<a href="#preventive-dementia-day-staff-article5">基準第5条へ</a></p></section>
<section class="handbook-role"><h4 id="preventive-dementia-day-staff-manager">管理者（単独型・併設型）</h4>
<p>事業所ごとに常勤の管理者を置き、原則として管理の職務に専ら従事します。管理上支障がない場合は、当該事業所や他の事業所・施設等の職務に従事できます。</p>
<p>必要な知識・経験と、厚生労働大臣が定める研修の修了が必要です。研修の種類や経過措置は、適用時点の資料と指定権者に確認してください。<a href="#preventive-dementia-day-staff-article6">基準第6条へ</a></p></section>
<section class="handbook-role"><h4 id="preventive-dementia-day-staff-shared">共用型の人員・管理者</h4>
<p>共用型では、居間や食堂などを共用する本体事業所・施設の利用者・入居者等と、共用型の利用者を合わせた人数について、本体事業所・施設に適用される人員基準を満たすために必要な人数を確認します。単独型・併設型の配置をそのまま当てはめないでください。<a href="#preventive-dementia-day-staff-article8">基準第8条へ</a></p>
<p>共用型にも常勤の管理者を置き、原則として管理の職務に専従します。管理に支障がない場合の兼務や、必要な知識・経験と研修修了について確認します。<a href="#preventive-dementia-day-staff-article10">基準第10条へ</a></p></section>
<p>認知症対応型通所介護と同一事業所で一体的に運営し、双方の指定を受けている場合には、介護側の基準を満たすことで介護予防側も満たすとみなせる規定があります。類型ごとの条件と利用者の数え方を原典で確認してください。<a href="#preventive-dementia-day-staff-article5">第5条</a> ／ <a href="#preventive-dementia-day-staff-article8">第8条</a></p>
<p><a href="https://www.mhlw.go.jp/web/t_doc?dataId=82aa7860&amp;dataType=0&amp;pageNo=1">国の基準省令を開く</a></p>
</section>'''


def add_preventive_dementia_dayservice_staffing_overview(content: str, path: Path) -> tuple[str, int]:
    if path != PAGE:
        return content, 0
    if content.count(INSERT_AFTER) != 1 or 'id="preventive-dementia-day-staff-roles"' in content:
        raise RuntimeError('Unexpected dementia day-service staffing structure')
    for number, (label, anchor, expected_hash) in SOURCES.items():
        start = ('<details class="handbook-source"><summary><span class="handbook-source-label">'
                 + number + '</span><span>' + label + '</span></summary>')
        if content.count(start) != 1:
            raise RuntimeError('Missing or duplicate dementia day-service source: ' + number)
        pos = content.index(start)
        end = content.find('</details>', pos)
        if end < 0:
            raise RuntimeError('Unclosed dementia day-service source: ' + number)
        record = content[pos:end]
        original = re.findall(r'<p class="handbook-original">(.*?)</p>', record, flags=re.DOTALL)
        if (len(original) != 1 or '収載資料の版・施行日：2024-04-01' not in record or
                hashlib.sha256(original[0].encode('utf-8')).hexdigest() != expected_hash):
            raise RuntimeError('Dementia day-service source changed; review before publication: ' + number)
        content = content.replace(start, start.replace('<summary>', f'<summary id="{anchor}">', 1), 1)
    return content.replace(INSERT_AFTER, INSERT_AFTER + OVERVIEW, 1), 1
