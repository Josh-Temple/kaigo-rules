"""Reader-oriented group-home staffing guide tied to the published source."""
from __future__ import annotations

import hashlib
import re
from pathlib import Path

PAGE = Path('handbook/dementia-group-home/staffing.html')
INSERT_AFTER = ('<p class="handbook-quick-link"><a href="#handbook-sources-staffing">'
                'この章の関連資料へ移動 ↓</a></p>')
OLD_NOTE = ('原典候補は省令第34号の認知症対応型共同生活介護章（認知症対応型共同生活介護の基準の参照対象一覧）。'
            '計画作成の担当者、管理者、介護従業者など役割ごとの資格と兼務条件をサービス別の基準で確認します。'
            '対象範囲の登録は現行適用・読替えの確認ではありません。施行版、指定権者条例及び個別適用は未確認です'
            '（作成中・未レビュー）。')
NEW_NOTE = ('原典候補は平成18年厚生労働省令第34号の認知症対応型共同生活介護に関する基準です。'
            '職種別の説明は収載版に基づきます。後の改正、指定権者の条例・取扱いと事業所への適用を'
            '確認してください（人による確認前の下書きです）。')
SOURCES = {
    '第九十条': ('（従業者の員数）', 'group-home-staff-article90',
              '451465b617790a3a7af40bd1add3e3e724a80de3d164d29e4388384495e0ca74'),
    '第九十一条': ('（管理者）', 'group-home-staff-article91',
               'd8a41667b9b554e66a66d9bb26170a6212a4e8c791f9f8ca71b1716df4c78d3f'),
    '第九十二条': ('（指定認知症対応型共同生活介護事業者の代表者）', 'group-home-staff-article92',
               '861e1f0308fca9cb1f76e832bce0cd5727eee562a9e8d3baa399a9f2c4d06c04'),
    '第百三条': ('（勤務体制の確保等）', 'group-home-staff-article103',
              'ce6f46376c225452085f5b8847ba02e1f40a97cf0b7f70cfd5c97e30f2fd0000'),
}

OVERVIEW = '''<section class="handbook-role" aria-labelledby="group-home-staff-roles">
<h3 id="group-home-staff-roles">職種別の配置基準</h3>
<p class="handbook-working-note">国の基準省令の2025年4月1日施行版をもとに、認知症対応型共同生活介護の配置を整理しています。後の改正、指定権者の条例・取扱い、併設やサテライト型の条件を適用前に確認してください。介護予防の事業を一体的に運営する場合には、別の取扱いがあります。</p>
<nav aria-label="職種別の配置基準"><ul>
<li><a href="#group-home-staff-day">介護従業者：日中</a></li>
<li><a href="#group-home-staff-night">介護従業者：夜間・深夜</a></li>
<li><a href="#group-home-staff-plan">計画作成担当者</a></li>
<li><a href="#group-home-staff-manager">管理者</a></li>
<li><a href="#group-home-staff-representative">事業者の代表者</a></li>
<li><a href="#group-home-staff-training">研修・勤務体制</a></li>
</ul></nav>
<section class="handbook-role"><h4 id="group-home-staff-day">介護従業者：日中</h4>
<p>夜間・深夜以外の時間帯は、共同生活住居（ユニット）ごとに、利用者3人またはその端数ごとに1人以上を常勤換算で確保します。算定する利用者数は原則として前年度の平均値で、新規指定時は推定数を用います。介護従業者のうち1人以上は常勤です。<a href="#group-home-staff-article90">基準第90条へ</a></p>
<p>国の解釈通知は、利用者8人、常勤者の勤務が1日8時間、日中が15時間の例で、介護従業者の勤務延時間を24時間確保し、その時間帯に常時1人以上を確保する考え方を示しています。夜間・深夜の時間帯は利用者の生活サイクルに応じて事業所ごとに設定します。<a href="https://www.mhlw.go.jp/content/12301000/000750727.pdf">国の解釈通知</a>の後の改正も確認してください。</p></section>
<section class="handbook-role"><h4 id="group-home-staff-night">介護従業者：夜間・深夜</h4>
<p>原則として、共同生活住居ごとに夜間・深夜を通じて1人以上が夜勤に当たるために必要な人数を確保します。ここでいう夜勤には宿直勤務を含みません。</p>
<p>3つの共同生活住居がすべて同一階で隣接し、利用者の状況を円滑に把握して速やかに対応できる構造で、安全対策が講じられ利用者の安全が確保されていると認められる場合は、事業所全体で夜間・深夜を通じて2人以上とする特例があります。住居の数だけで判断せず、構造と安全対策を確認します。<a href="#group-home-staff-article90">基準第90条へ</a></p></section>
<section class="handbook-role"><h4 id="group-home-staff-plan">計画作成担当者</h4>
<p>事業所ごとに、計画作成に必要な知識・経験と所定の研修を備えた担当者を置き、専らその職務に従事させます。利用者の処遇に支障がない場合は、その事業所の他の職務に従事できます。原則として担当者のうち1人以上は介護支援専門員です。</p>
<p>併設する小規模多機能型居宅介護または看護小規模多機能型居宅介護の介護支援専門員との連携で効果的な運営が期待でき、利用者の処遇に支障がない場合には、事業所に介護支援専門員を置かないことができる特例があります。サテライト型の事業所についても別の規定を確認します。<a href="#group-home-staff-article90">基準第90条へ</a></p></section>
<section class="handbook-role"><h4 id="group-home-staff-manager">管理者</h4>
<p>共同生活住居ごとに常勤で専ら管理の職務に従事する管理者を置きます。管理上支障がない場合の兼務や、サテライト型で本体事業所の管理者を充てる場合には条件があります。</p>
<p>所定の施設・事業所等で認知症の人の介護に3年以上従事した経験と、厚生労働大臣が定める研修の修了などが必要です。<a href="#group-home-staff-article91">基準第91条へ</a></p></section>
<section class="handbook-role"><h4 id="group-home-staff-representative">事業者の代表者</h4>
<p>認知症の人の介護に従事した経験、または保健医療・福祉サービスの経営に携わった経験に加え、厚生労働大臣が定める研修の修了が必要です。経験の対象を原典で確認します。<a href="#group-home-staff-article92">基準第92条へ</a></p></section>
<section class="handbook-role"><h4 id="group-home-staff-training">研修・勤務体制</h4>
<p>適切なサービスを提供できるよう勤務体制を定め、継続性に配慮し、介護従業者の研修の機会を確保します。認知症介護の基礎的な研修の受講に必要な措置と、看護師・介護福祉士等の資格を持つ者などの除外範囲を確認します。<a href="#group-home-staff-article103">基準第103条へ</a></p></section>
</section>'''


def add_group_home_staffing_overview(content: str, path: Path) -> tuple[str, int]:
    if path != PAGE:
        return content, 0
    if (content.count(INSERT_AFTER) != 1 or content.count(OLD_NOTE) != 1 or
            'id="group-home-staff-roles"' in content):
        raise RuntimeError('Unexpected group home staffing structure')
    for number, (label, anchor, expected_hash) in SOURCES.items():
        start = ('<details class="handbook-source"><summary><span class="handbook-source-label">'
                 + number + '</span><span>' + label + '</span></summary>')
        if content.count(start) != 1:
            raise RuntimeError(f'Missing or duplicate group home staffing source: {number}')
        pos = content.index(start)
        end = content.find('</details>', pos)
        if end < 0:
            raise RuntimeError(f'Unclosed group home staffing source: {number}')
        record = content[pos:end]
        original = re.findall(r'<p class="handbook-original">(.*?)</p>', record, flags=re.DOTALL)
        if (len(original) != 1 or '収載資料の版・施行日：2025-04-01' not in record or
                hashlib.sha256(original[0].encode('utf-8')).hexdigest() != expected_hash):
            raise RuntimeError(f'Group home staffing source changed; review summary before publication: {number}')
        content = content.replace(start, start.replace('<summary>', f'<summary id="{anchor}">', 1), 1)
    content = content.replace(OLD_NOTE, NEW_NOTE, 1)
    return content.replace(INSERT_AFTER, INSERT_AFTER + OVERVIEW, 1), 1
