"""Reader-facing guide to the existing community-dayservice staffing source.

The text is based on the already published 2025-04-01 ordinance extract.
Changing the underlying source requires a fresh review of this guide.
"""
from __future__ import annotations

import hashlib
import re
from pathlib import Path

PAGE = Path('handbook/community-dayservice/staffing.html')
# Ministry ordinance No. 34, Articles 20 and 21:
# https://www.mhlw.go.jp/web/t_doc?dataId=82aa7858&dataType=0
# Nursing coordination: 2021 redline, section 二の二 1(1)⑥ and 2024
# Q&A Vol. 1 question 59, linked and dated beside the reader-facing text.
# These hashes bind the summary to the published 2025-04-01 extract; they do
# not establish that the extract reflects later amendments or local ordinances.
SOURCE_HASHES = {
    '第二十条': '1d717f2824fc716c044ea8f5016ce7f1b6131a968558c179b8b94e8c355abeef',
    '第二十一条': '3bdba8c8df018eb304b418bc71e4f76ba0f887ec7075a40829217009c2858b2c',
}
SOURCE_LABELS = {'第二十条': '（従業者の員数）', '第二十一条': '（管理者）'}
SOURCE_IDS = {'第二十条': 'community-staff-article20', '第二十一条': 'community-staff-article21'}
INSERT_AFTER = ('<p class="handbook-quick-link"><a href="#handbook-sources-staffing">'
                'この章の関連資料へ移動 ↓</a></p>')

OVERVIEW = '''<section class="handbook-role" aria-labelledby="community-staff-roles">
<h3 id="community-staff-roles">職種別の配置基準</h3>
<p class="handbook-working-note">ここでは、通常の地域密着型通所介護について、国の基準省令の2025年4月1日施行版と、発出時期を示した通知・Q&amp;Aをもとに要点を整理しています。後の改正、指定権者の条例・取扱い、資格や兼務の条件は、適用前に原典で確認してください。療養通所介護と共生型には別の規定があります。</p>
<nav aria-label="職種別の配置基準"><ul>
<li><a href="#community-staff-consultant">生活相談員</a></li>
<li><a href="#community-staff-nursing">看護職員</a></li>
<li><a href="#community-staff-care">介護職員</a></li>
<li><a href="#community-staff-training">機能訓練指導員</a></li>
<li><a href="#community-staff-manager">管理者</a></li>
<li><a href="#community-staff-exceptions">定員10人以下などの特例</a></li>
</ul></nav>
<section class="handbook-role"><h4 id="community-staff-consultant">生活相談員</h4>
<p>提供日ごとに、提供時間帯に専ら地域密着型通所介護に従事する生活相談員の勤務時間の合計を、事業所の提供時間数で割った数が1以上となるよう配置します。</p>
<p>提供時間と勤務表を日ごとに照合し、資格と兼務の取扱いも確認します。<a href="#community-staff-article20">基準第20条の資料へ</a></p></section>
<details><summary>生活相談員の勤務時間の計算例・地域での活動</summary>
<p>例えば、事業所のサービス提供時間が6時間の日は、生活相談員の勤務時間を合計して6時間以上確保することを確認します。複数人の勤務時間を合計できます。相談・援助に支障がないことも確認してください。</p>
<p>平成28年の国の通知では、利用者の地域生活を支える取組として、サービス担当者会議や地域ケア会議、利用者宅での相談などに要する時間を、一定の条件のもとで勤務延時間数に含める取扱いが示されています。利用者への相談・援助に支障がない範囲で、対象となる時間や活動記録の取扱いを指定権者に確認します。</p>
<p><a href="https://www2.wam.go.jp/gyoseiShiryou-files/resources/aaff6e9a-72ef-4fd8-b8ae-207ee20f0076/%E4%BB%8B%E8%AD%B7%E4%BF%9D%E9%99%BA%E6%9C%80%E6%96%B0%E6%83%85%E5%A0%B1Vol.524.pdf">平成28年の通知（福祉医療機構掲載）</a>。後の改正・Q&amp;Aも確認してください。</p></details>
<section class="handbook-role"><h4 id="community-staff-nursing">看護職員</h4>
<p>原則として、提供単位ごとに、専らサービスの提供に当たる看護師または准看護師が1人以上確保されるために必要な人数を置きます。</p>
<p>国の令和3年度改正資料では、提供時間帯を通じて事業所内で専従する必要はなく、事業所との密接かつ適切な連携が必要とされています。病院・診療所・訪問看護ステーションとの連携による確保も示されています。</p>
<p>外部と連携する場合の利用者全員の健康状態の確認や、提供時間帯を通じた連絡体制などの条件を確認してください。<a href="https://www.mhlw.go.jp/content/12300000/000869799.pdf">令和3年度の改正資料（新旧対照表・抄）</a> ／ <a href="https://www.mhlw.go.jp/content/12300000/001246407.pdf">令和6年度 国Q&amp;A Vol.1 問59</a>。いずれも後続の改正・訂正がないか確認してください。</p>
<p>利用定員が10人以下の場合は、看護職員と介護職員の配置に関する特例があります。<a href="#community-staff-exceptions">特例を確認する</a> ／ <a href="#community-staff-article20">基準第20条の資料へ</a></p></section>
<section class="handbook-role"><h4 id="community-staff-care">介護職員</h4>
<p>原則として、提供単位ごとに、専らサービスの提供に当たる介護職員の勤務時間の合計を提供単位時間数で割った割合が、利用者15人までは1以上、15人を超える場合は「1＋（15人を超える人数÷5）」以上となるよう、必要な人数を置きます。</p>
<p>さらに、単位ごとに常時1人以上の介護職員が従事します。利用定員10人以下の特例を適用する場合は、この常時従事の対象は看護職員または介護職員です。<a href="#community-staff-exceptions">特例を確認する</a> ／ <a href="#community-staff-article20">基準第20条の資料へ</a></p></section>
<details><summary>介護職員の勤務時間の計算例</summary>
<p>平成28年の国の通知では、この計算に用いる提供時間数は、単位ごとの「利用者それぞれの提供時間の合計÷利用者数」で求める平均提供時間数と説明されています。</p>
<p>例えば、1単位の利用者が18人、平均提供時間が5時間の場合は、（18−15）÷5＋1＝1.6、5時間×1.6＝<strong>延べ8時間</strong>分の介護職員の勤務が必要です。時間数を満たすだけでなく、単位ごとに常時1人以上が従事することも別に確認します。</p>
<p>利用定員10人以下の特例を適用するときは、第20条第2項の看護職員または介護職員による計算を確認します。一体運営時の利用者の数え方も別に確認してください。<a href="https://www2.wam.go.jp/gyoseiShiryou-files/resources/aaff6e9a-72ef-4fd8-b8ae-207ee20f0076/%E4%BB%8B%E8%AD%B7%E4%BF%9D%E9%99%BA%E6%9C%80%E6%96%B0%E6%83%85%E5%A0%B1Vol.524.pdf">平成28年の通知（福祉医療機構掲載）</a>。後の改正・Q&amp;Aも確認してください。</p></details>
<section class="handbook-role"><h4 id="community-staff-training">機能訓練指導員</h4>
<p>事業所ごとに1人以上を置きます。日常生活に必要な機能の低下を防ぐ訓練を行う能力を持つ者とされ、当該事業所の他の職務に従事することもできます。</p>
<p>資格や兼務の取扱いを確認します。<a href="#community-staff-article20">基準第20条の資料へ</a></p></section>
<details><summary>機能訓練指導員の資格・兼務の確認</summary>
<p>平成30年度の国の改正資料には、理学療法士、作業療法士、言語聴覚士、看護職員、柔道整復師、あん摩マッサージ指圧師、はり師またはきゅう師が挙げられています。はり師・きゅう師は、対象資格の機能訓練指導員を配置した事業所で6か月以上、機能訓練指導に従事した経験が必要とされています。</p>
<p>同資料には、日常生活やレクリエーション、行事を通じた訓練については、生活相談員または介護職員が兼務できる取扱いも示されています。基本の人員基準と、個別機能訓練加算を算定する場合の配置要件は分けて確認してください。</p>
<p><a href="https://www.mhlw.go.jp/file/06-Seisakujouhou-12300000-Roukenkyoku/0000199106.pdf">平成30年度の改正資料（新旧対照表・抄）</a>。後の改正や指定権者の取扱いを確認してください。</p></details>
<section class="handbook-role"><h4 id="community-staff-manager">管理者</h4>
<p>事業所ごとに常勤の管理者を置き、原則として管理の職務に専ら従事します。管理に支障がない場合は、当該事業所や他の事業所・施設等の職務を兼ねることができます。</p>
<p>兼務する場合も、管理業務に支障がないかを確認します。<a href="#community-staff-article21">基準第21条の資料へ</a></p></section>
<section class="handbook-role"><h4 id="community-staff-exceptions">定員10人以下などの特例・共通の確認</h4>
<ul><li><strong>利用定員10人以下：</strong>特例を適用すると、単位ごとに、看護職員または介護職員の専従勤務時間の合計を提供単位時間数で割った数が1以上となる人数とすることができます。別に、看護職員または介護職員を単位ごとに常時1人以上従事させます。</li>
<li><strong>常勤者：</strong>国の基準省令の収載版では、生活相談員または介護職員のうち1人以上は常勤です。定員10人以下の特例における看護職員の扱いは、指定権者の条例・手引も確認してください。例えば<a href="https://www.city.yokohama.lg.jp/business/bunyabetsu/fukushi-kaigo/kaigo/shinsei/service/henkou_unei/mittyaku-dei.files/0187_20260527.pdf">横浜市の令和8年度の手引</a>は、定員10人以下で看護職員を配置する場合には看護職員も含めています。</li>
<li><strong>第一号通所事業との一体運営：</strong>両方の指定を受け、同じ事業所で一体的に運営する場合には、市町村が定める第一号通所事業の人員基準を満たすことで、基準第20条の人員基準を満たすものとみなすことができる規定があります。指定・運営の実態と市町村の基準を確認します。</li></ul>
<p>一体運営では利用者数の数え方にも規定があります。定員表、単位別の利用者数、提供時間、勤務実績を突き合わせ、<a href="#community-staff-article20">基準第20条の全文</a>と適用される条例を確認してください。</p></section>
</section>'''


def add_community_staffing_overview(content: str, path: Path) -> tuple[str, int]:
    if path != PAGE:
        return content, 0
    if content.count(INSERT_AFTER) != 1 or 'id="community-staff-roles"' in content:
        raise RuntimeError('Unexpected community staffing structure')

    for number, expected_hash in SOURCE_HASHES.items():
        label = SOURCE_LABELS[number]
        start = ('<details class="handbook-source"><summary><span class="handbook-source-label">'
                 + number + '</span><span>' + label + '</span></summary>')
        if content.count(start) != 1:
            raise RuntimeError(f'Missing or duplicate staffing source: {number}')
        pos = content.index(start)
        end = content.find('</details>', pos)
        if end < 0:
            raise RuntimeError(f'Unclosed staffing source: {number}')
        record = content[pos:end]
        original = re.findall(r'<p class="handbook-original">(.*?)</p>', record, flags=re.DOTALL)
        if (len(original) != 1 or '収載資料の版・施行日：2025-04-01' not in record or
                hashlib.sha256(original[0].encode('utf-8')).hexdigest() != expected_hash):
            raise RuntimeError(f'Staffing source changed; review summary before publication: {number}')
        replacement = start.replace('<summary>', f'<summary id="{SOURCE_IDS[number]}">', 1)
        content = content.replace(start, replacement, 1)

    return content.replace(INSERT_AFTER, INSERT_AFTER + OVERVIEW, 1), 1
