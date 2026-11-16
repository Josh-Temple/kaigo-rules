"""Reader guide to selected equipment standards for community-based facilities."""
from __future__ import annotations

import hashlib
import re
from pathlib import Path

PAGE = Path('handbook/community-elderly-facility/equipment.html')
INSERT_AFTER = ('<p class="handbook-quick-link"><a href="#handbook-sources-equipment">'
                'この章の関連資料へ移動 ↓</a></p>')
# The guide refers to these exact national-ordinance extracts and effective dates.
SOURCES = {
    '第百三十二条': ('（設備）', 'community-facility-equipment-132', 'd9019b4112e0df4f1ef520ab2610051551d8382b1e90bda840ddae37279e7210'),
    '第百六十条': ('（設備）', 'community-facility-equipment-160', '5297abeebd3a3df92ac298fba4314fa4d9fdec71599416760d12aca7a4f5af3b'),
}
OVERVIEW = '''<section class="handbook-role" aria-labelledby="community-facility-equipment-guide">
<h3 id="community-facility-equipment-guide">施設の類型別に設備を確認する</h3>
<p class="handbook-working-note">国の基準省令の2025年4月1日施行版にある主な設備を整理しています。ここに示すものは一部です。適用時点の改正、施設の設置時期による経過措置、所在地の条例、個別の適用を必ず確認してください。</p>
<section class="handbook-role"><h4>通常型（ユニット型以外）の居室</h4>
<p>居室の定員は原則1人です。入所者へのサービスの提供上、必要と認められる場合は2人とすることができます。床面積は入所者1人当たり10.65平方メートル以上とし、ブザーまたは代わりの設備を設けます。<a href="#community-facility-equipment-132">基準第132条へ</a></p></section>
<section class="handbook-role"><h4>ユニット型の居室・共同生活室</h4>
<p>居室の定員は原則1人ですが、入居者へのサービスの提供上、必要と認められる場合は2人とすることができます。1室の床面積等は10.65平方メートル以上、2人とする場合は21.3平方メートル以上です。居室にはブザーまたは代わりの設備を設けます。</p>
<p>居室はユニットに属し、共同生活室に近接して一体的に設けます。ユニットの入居定員は原則おおむね10人以下、15人を超えないものとします。共同生活室の床面積は、ユニットの入居定員1人当たり2平方メートルを標準とします。<a href="#community-facility-equipment-160">基準第160条へ</a></p></section>
<section class="handbook-role"><h4>食堂・機能訓練室と廊下</h4>
<p>通常型では、食堂と機能訓練室はそれぞれ必要な広さを有し、合計面積は入所定員1人当たり3平方メートル以上です。食事や訓練に支障がない広さを確保できる場合は、同じ場所とすることができます。<a href="#community-facility-equipment-132">基準第132条へ</a></p>
<p>通常型・ユニット型とも、廊下幅は1.5メートル以上、中廊下は1.8メートル以上です。廊下の一部の幅を広げるなどして円滑な往来に支障がないと認められる場合には、例外があります。<a href="#community-facility-equipment-132">第132条</a> ／ <a href="#community-facility-equipment-160">第160条</a></p></section>
<p>図面・居室別定員表・設備台帳を用意し、施設の類型や既存施設に関する取扱いを指定権者に確認してください。上記以外にも洗面設備、便所、浴室、医務室、非常災害に必要な設備等の基準があります。</p>
<p><a href="https://www.mhlw.go.jp/web/t_doc?dataId=82aa7858&amp;dataType=0&amp;pageNo=3">国の基準省令を開く</a></p>
</section>'''


def add_community_facility_equipment_overview(content: str, path: Path) -> tuple[str, int]:
    if path != PAGE:
        return content, 0
    if content.count(INSERT_AFTER) != 1 or 'id="community-facility-equipment-guide"' in content:
        raise RuntimeError('Unexpected community facility equipment structure')
    for number, (label, anchor, expected_hash) in SOURCES.items():
        start = ('<details class="handbook-source"><summary><span class="handbook-source-label">'
                 + number + '</span><span>' + label + '</span></summary>')
        if content.count(start) != 1:
            raise RuntimeError('Missing or duplicate community facility source: ' + number)
        pos = content.index(start)
        end = content.find('</details>', pos)
        if end < 0:
            raise RuntimeError('Unclosed community facility source: ' + number)
        record = content[pos:end]
        original = re.findall(r'<p class="handbook-original">(.*?)</p>', record, flags=re.DOTALL)
        if (len(original) != 1 or '収載資料の版・施行日：2025-04-01' not in record or
                hashlib.sha256(original[0].encode('utf-8')).hexdigest() != expected_hash):
            raise RuntimeError('Community facility source changed; review before publication: ' + number)
        content = content.replace(start, start.replace('<summary>', f'<summary id="{anchor}">', 1), 1)
    return content.replace(INSERT_AFTER, INSERT_AFTER + OVERVIEW, 1), 1
