"""Staffing guide for the separately regulated preventive group-home service."""
from __future__ import annotations

import hashlib
import re
from pathlib import Path

PAGE = Path('handbook/preventive-dementia-group-home/staffing.html')
INSERT_AFTER = ('<p class="handbook-quick-link"><a href="#handbook-sources-staffing">'
                'この章の関連資料へ移動 ↓</a></p>')
OLD_NOTE = ('原典候補は省令第36号の介護予防認知症対応型共同生活介護章（介護予防認知症対応型共同生活介護の基準の参照対象一覧）。'
            '計画作成担当者や介護従業者の役割は予防地域密着型基準に照合し、通常型の資格・兼務要件をそのまま転用しません。'
            '対象範囲の登録は現行適用・読替えの確認ではありません。施行版、指定権者条例及び個別適用は未確認です'
            '（作成中・未レビュー）。')
NEW_NOTE = ('原典候補は平成18年厚生労働省令第36号の介護予防認知症対応型共同生活介護に関する基準です。'
            '職種別の説明は収載版に基づきます。介護側との一体運営などの条件、後の改正、指定権者の条例・取扱いを'
            '確認してください（人による確認前の下書きです）。')
SOURCES = {
    '第七十条': ('（従業者の員数）', 'preventive-group-staff-article70',
              'e45aab0081f1336f7e4b4e66e6a26d0a590bf64cbcafd8663dc8e26e81386225'),
    '第七十一条': ('（管理者）', 'preventive-group-staff-article71',
               'b9fcaddbf59ff74a71036a9882501ca836921255996141ec831ba9b847e91646'),
    '第七十二条': ('（指定介護予防認知症対応型共同生活介護事業者の代表者）', 'preventive-group-staff-article72',
               '18cb9bb85972197098802fca9f78fdcc0afb7549822d4e9f2dfe2d48602373f7'),
    '第八十条': ('（勤務体制の確保等）', 'preventive-group-staff-article80',
              '43ba9c0ce120c305fd79c2426641b366b5a0ede3f21c9f12f28b4fb7c6612147'),
}

OVERVIEW = '''<section class="handbook-role" aria-labelledby="preventive-group-staff-roles">
<h3 id="preventive-group-staff-roles">職種別の配置基準</h3>
<p class="handbook-working-note">国の基準省令の2024年4月1日施行版をもとに、介護予防認知症対応型共同生活介護の配置を整理しています。介護側の基準と例外の対象が異なる部分があります。後の改正、指定権者の条例・取扱いと事業所への適用を確認してください。</p>
<nav aria-label="職種別の配置基準"><ul>
<li><a href="#preventive-group-staff-day">介護従業者：日中</a></li>
<li><a href="#preventive-group-staff-night">介護従業者：夜間・深夜</a></li>
<li><a href="#preventive-group-staff-plan">計画作成担当者</a></li>
<li><a href="#preventive-group-staff-manager">管理者</a></li>
<li><a href="#preventive-group-staff-representative">事業者の代表者</a></li>
<li><a href="#preventive-group-staff-training">研修・勤務体制</a></li>
<li><a href="#preventive-group-staff-integrated">介護側と一体的に運営する場合</a></li>
</ul></nav>
<section class="handbook-role"><h4 id="preventive-group-staff-day">介護従業者：日中</h4>
<p>夜間・深夜以外の時間帯は、共同生活住居（ユニット）ごとに、利用者3人またはその端数ごとに1人以上を常勤換算で確保します。利用者数は原則として前年度の平均値で、新規指定時は推定数を用います。介護従業者のうち1人以上は常勤です。<a href="#preventive-group-staff-article70">基準第70条へ</a></p></section>
<section class="handbook-role"><h4 id="preventive-group-staff-night">介護従業者：夜間・深夜</h4>
<p>原則として、共同生活住居ごとに夜間・深夜を通じて1人以上が夜勤に当たるために必要な人数を確保します。ここでいう夜勤には宿直勤務を含みません。</p>
<p>3つの共同生活住居がすべて同一階で隣接し、利用者の状況を円滑に把握して速やかに対応できる構造で、安全対策が講じられ利用者の安全が確保されていると認められる場合は、事業所全体で夜間・深夜を通じて2人以上とする特例があります。住居の数だけでなく構造と安全対策を確認します。<a href="#preventive-group-staff-article70">基準第70条へ</a></p></section>
<section class="handbook-role"><h4 id="preventive-group-staff-plan">計画作成担当者</h4>
<p>事業所ごとに、計画作成に必要な知識・経験と所定の研修を備えた担当者を置き、専らその職務に従事させます。利用者の処遇に支障がない場合は、その事業所の他の職務に従事できます。原則として担当者のうち1人以上は介護支援専門員です。</p>
<p>介護予防側の第70条第7項には、併設する小規模多機能型居宅介護の介護支援専門員との連携で効果的な運営が期待でき、利用者の処遇に支障がない場合、介護支援専門員を置かないことができる特例があります。サテライト型の事業所にも別の規定があります。<a href="#preventive-group-staff-article70">基準第70条へ</a></p></section>
<section class="handbook-role"><h4 id="preventive-group-staff-manager">管理者</h4>
<p>共同生活住居ごとに常勤で専ら管理の職務に従事する管理者を置きます。管理上支障がない場合の兼務や、サテライト型で本体事業所の管理者を充てる場合には条件があります。所定の施設・事業所等で認知症の人の介護に3年以上従事した経験と、厚生労働大臣が定める研修の修了などが必要です。<a href="#preventive-group-staff-article71">基準第71条へ</a></p></section>
<section class="handbook-role"><h4 id="preventive-group-staff-representative">事業者の代表者</h4>
<p>認知症の人の介護に従事した経験、または保健医療・福祉サービスの経営に携わった経験に加え、厚生労働大臣が定める研修の修了が必要です。経験の対象を原典で確認します。<a href="#preventive-group-staff-article72">基準第72条へ</a></p></section>
<section class="handbook-role"><h4 id="preventive-group-staff-training">研修・勤務体制</h4>
<p>適切なサービスを提供できるよう勤務体制を定め、継続性に配慮し、介護従業者の研修の機会を確保します。認知症介護の基礎的な研修の受講に必要な措置と、看護師・介護福祉士等の資格を持つ者などの除外範囲を確認します。<a href="#preventive-group-staff-article80">基準第80条へ</a></p></section>
<section class="handbook-role"><h4 id="preventive-group-staff-integrated">介護側と一体的に運営する場合</h4>
<p>介護予防と認知症対応型共同生活介護の両方の指定を受け、同じ事業所で一体的に運営する場合には、介護側の基準第90条第1項から第10項までの人員基準を満たすことをもって、介護予防側の人員基準を満たすとみなす規定があります。指定と一体運営の条件、対象となる利用者、併設・兼務を指定権者の基準と照合します。<a href="#preventive-group-staff-article70">基準第70条第11項へ</a></p></section>
</section>'''


def add_preventive_group_home_staffing_overview(content: str, path: Path) -> tuple[str, int]:
    if path != PAGE:
        return content, 0
    if (content.count(INSERT_AFTER) != 1 or content.count(OLD_NOTE) != 1 or
            'id="preventive-group-staff-roles"' in content):
        raise RuntimeError('Unexpected preventive group home staffing structure')
    for number, (label, anchor, expected_hash) in SOURCES.items():
        start = ('<details class="handbook-source"><summary><span class="handbook-source-label">'
                 + number + '</span><span>' + label + '</span></summary>')
        if content.count(start) != 1:
            raise RuntimeError(f'Missing or duplicate preventive group home staffing source: {number}')
        pos = content.index(start)
        end = content.find('</details>', pos)
        if end < 0:
            raise RuntimeError(f'Unclosed preventive group home staffing source: {number}')
        record = content[pos:end]
        original = re.findall(r'<p class="handbook-original">(.*?)</p>', record, flags=re.DOTALL)
        if (len(original) != 1 or '収載資料の版・施行日：2024-04-01' not in record or
                hashlib.sha256(original[0].encode('utf-8')).hexdigest() != expected_hash):
            raise RuntimeError(f'Preventive group home staffing source changed; review summary before publication: {number}')
        content = content.replace(start, start.replace('<summary>', f'<summary id="{anchor}">', 1), 1)
    content = content.replace(OLD_NOTE, NEW_NOTE, 1)
    return content.replace(INSERT_AFTER, INSERT_AFTER + OVERVIEW, 1), 1
