"""Correct the different manager and representative requirements in the checklist."""
from __future__ import annotations

import hashlib
import re
from pathlib import Path

PAGE = Path('handbook/nursing-small-scale-multifunctional/staffing.html')
SOURCE_HASHES = {
    '第百七十二条': '6ffc9eccf4677bafefbeba067cfb061478f41058a933719351be56c12de170d2',
    '第百七十三条': '6683a9ca3333f07de4ceaab4bc7488f146e0a58c9ac3e2ea7227688b02266b8f',
}
OLD = ('管理者が事業所ごとに常勤かつ専らその職務に従事しているか。'
       '管理者は認知症介護3年以上経験＋研修修了又は保健師・看護師の要件を満たしているか。'
       '代表者も同様の要件を満たしているか（第172条第3項、第173条第1項）')
NEW = ('管理者は常勤・原則専従か。管理者は、所定の認知症介護の経験3年以上と所定の研修修了、'
       '又は保健師・看護師の要件を満たすか（第172条）。'
       '代表者は、所定の認知症介護又は保健医療・福祉サービスの経営の経験と所定の研修修了、'
       '又は保健師・看護師の要件を満たすか（第173条）。')


def clarify_nursing_small_scale_roles(content: str, path: Path) -> tuple[str, int]:
    if path != PAGE:
        return content, 0
    if content.count(OLD) != 1:
        raise RuntimeError('Unexpected nursing small-scale role checklist')
    for article, expected_hash in SOURCE_HASHES.items():
        start = ('<details class="handbook-source"><summary><span class="handbook-source-label">'
                 + article + '</span>')
        if content.count(start) != 1:
            raise RuntimeError('Unexpected nursing small-scale source structure: ' + article)
        pos = content.index(start)
        end = content.find('</details>', pos)
        if end < 0:
            raise RuntimeError('Unclosed nursing small-scale source: ' + article)
        record = content[pos:end]
        original = re.findall(r'<p class="handbook-original">(.*?)</p>', record, flags=re.DOTALL)
        if (len(original) != 1 or '収載資料の版・施行日：2025-04-01' not in record or
                hashlib.sha256(original[0].encode('utf-8')).hexdigest() != expected_hash):
            raise RuntimeError('Nursing small-scale source changed; review before publication: ' + article)
    return content.replace(OLD, NEW, 1), 1
