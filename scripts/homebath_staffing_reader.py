"""Reader guidance for office staffing and visit teams in home bathing care."""
from __future__ import annotations

import hashlib
import re
from pathlib import Path

STAFFING = Path('handbook/homebath/staffing.html')
OPERATIONS = Path('handbook/homebath/operations.html')
INSERT_AFTER = ('<p class="handbook-quick-link"><a href="#handbook-sources-staffing">'
                'この章の関連資料へ移動 ↓</a></p>')
# Bind each explanation to the 2025-04-01 source extract that will be displayed.
SOURCES = {
    STAFFING: {
        '第四十五条': ('（従業者の員数）', 'homebath-staff-article45', 'ee3305ad793846319d107cd13ff6f5dd5ae31eab7dc292c75e85ba3564a9f5df'),
        '第四十六条': ('（管理者）', 'homebath-staff-article46', '45f92cdd24c28feb19186074fc7106013c39ce23cad04cf1e3772c6da0e3b91e'),
    },
    OPERATIONS: {
        '第五十条': ('（指定訪問入浴介護の具体的取扱方針）', 'homebath-staff-article50', 'e69a1452e0aa66df379bac85d43f74e5d4a019076e5398ec63b2480764e0d508'),
    },
}
OVERVIEW = '''<section class="handbook-role" aria-labelledby="homebath-staffing-overview">
<h3 id="homebath-staffing-overview">事業所の配置と訪問時の編成</h3>
<p class="handbook-working-note">国の基準省令の2025年4月1日施行版をもとに整理しています。後の改正、指定権者の条例・取扱いと個別の適用を確認してください。</p>
<section class="handbook-role"><h4>事業所に置く従業者</h4>
<p>事業所ごとに、看護師または准看護師を1人以上、介護職員を2人以上置きます。これらの訪問入浴介護従業者のうち、1人以上は常勤でなければなりません。<a href="#homebath-staff-article45">基準第45条へ</a></p></section>
<section class="handbook-role"><h4>1回の訪問での編成</h4>
<p>原則として、看護職員1人と介護職員2人で訪問し、そのうち1人をサービス提供の責任者とします。</p>
<p>利用者の身体の状態が安定していることなどにより入浴による支障のおそれがないと認められる場合は、主治医の意見を確認した上で、看護職員に代えて介護職員を充てることができます。この例外は訪問時の編成についての規定です。事業所ごとの看護職員の配置を免除するものではありません。<a href="operations.html#homebath-staff-article50">基準第50条へ</a></p></section>
<section class="handbook-role"><h4>管理者</h4>
<p>事業所ごとに常勤の管理者を置き、原則として管理の職務に専ら従事します。管理上支障がない場合には、当該事業所や他の事業所・施設等の職務に従事できます。<a href="#homebath-staff-article46">基準第46条へ</a></p></section>
<p>介護予防訪問入浴介護と同じ事業所で一体的に運営し、双方の指定を受けている場合には、介護予防側の人員基準を満たした上で介護職員を1人置くことで、訪問入浴介護側の第45条の人員基準を満たすとみなせる規定があります。条件や勤務の実態は原典と指定権者に確認してください。<a href="#homebath-staff-article45">基準第45条第3項へ</a></p>
<p><a href="https://www.mhlw.go.jp/web/t_doc?dataId=82999404&amp;dataType=0&amp;pageNo=1">国の基準省令を開く</a></p>
</section>'''


def add_homebath_staffing_overview(content: str, path: Path) -> tuple[str, int]:
    sources = SOURCES.get(path)
    if sources is None:
        return content, 0
    if path == STAFFING and (content.count(INSERT_AFTER) != 1 or 'id="homebath-staffing-overview"' in content):
        raise RuntimeError('Unexpected home-bathing staffing structure')
    for number, (label, anchor, expected_hash) in sources.items():
        start = ('<details class="handbook-source"><summary><span class="handbook-source-label">'
                 + number + '</span><span>' + label + '</span></summary>')
        if content.count(start) != 1:
            raise RuntimeError('Missing or duplicate home-bathing source: ' + number)
        pos = content.index(start)
        end = content.find('</details>', pos)
        if end < 0:
            raise RuntimeError('Unclosed home-bathing source: ' + number)
        record = content[pos:end]
        original = re.findall(r'<p class="handbook-original">(.*?)</p>', record, flags=re.DOTALL)
        if (len(original) != 1 or '収載資料の版・施行日：2025-04-01' not in record or
                hashlib.sha256(original[0].encode('utf-8')).hexdigest() != expected_hash):
            raise RuntimeError('Home-bathing source changed; review before publication: ' + number)
        content = content.replace(start, start.replace('<summary>', f'<summary id="{anchor}">', 1), 1)
    if path == STAFFING:
        content = content.replace(INSERT_AFTER, INSERT_AFTER + OVERVIEW, 1)
    return content, 1
