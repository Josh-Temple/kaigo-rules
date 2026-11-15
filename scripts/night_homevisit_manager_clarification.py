"""Clarify the different manager compatibility conditions in ordinance 7."""
from __future__ import annotations

import hashlib
import re
from pathlib import Path

PAGE = Path('handbook/night-homevisit/staffing.html')
SOURCE_HASH = '52937671304372d1128039e43f6e3c939915d73847b701091b56dc28a744266c'
OLD = ('管理者は、事業所ごとに専らその職務に従事する常勤の者を置かなければなりません（第7条）。'
       'ただし、事業所の管理上支障がない場合は、当該事業所の他の職務又は他の事業所・施設等の職務に従事できます'
       '（定期巡回事業者の指定を併せ受けて一体的に運営している場合に限る）。'
       '日中のオペレーションセンターサービスを実施する場合で、指定訪問介護事業者の指定を併せ受けて'
       '一体的に運営するときは、指定訪問介護事業所の職務に従事できます。')
NEW = ('管理者は、事業所ごとに専らその職務に従事する常勤の者を置きます（第7条）。'
       '事業所の管理上支障がない場合は、その事業所の他の職務に従事できます。'
       '他の事業所・施設等の職務については、管理上支障がなく、'
       '指定定期巡回・随時対応型訪問介護看護事業者の指定を併せて受け、'
       'その相手先と一体的に運営している場合に従事できます。'
       '日中のオペレーションセンターサービスを実施し、指定訪問介護事業者の指定を併せ受けて'
       '一体的に運営するときは、指定訪問介護事業所の職務に従事できます。')


def clarify_night_homevisit_manager(content: str, path: Path) -> tuple[str, int]:
    if path != PAGE:
        return content, 0
    start = ('<details class="handbook-source"><summary><span class="handbook-source-label">'
             '第七条</span><span>（管理者）</span></summary>')
    if content.count(start) != 1 or content.count(OLD) != 1:
        raise RuntimeError('Unexpected night homevisit manager structure')
    pos = content.index(start)
    end = content.find('</details>', pos)
    if end < 0:
        raise RuntimeError('Unclosed night homevisit manager source')
    record = content[pos:end]
    original = re.findall(r'<p class="handbook-original">(.*?)</p>', record, flags=re.DOTALL)
    if (len(original) != 1 or '収載資料の版・施行日：2025-04-01' not in record or
            hashlib.sha256(original[0].encode('utf-8')).hexdigest() != SOURCE_HASH):
        raise RuntimeError('Night homevisit manager source changed; review before publication')
    return content.replace(OLD, NEW, 1), 1
