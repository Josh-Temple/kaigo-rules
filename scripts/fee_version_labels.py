"""Describe the version and evidence for the pinned fee pages accurately.

These replacements affect explanatory UI only.  The imported legal text and
the underlying verification records are not rewritten.
"""
from pathlib import Path
import re


FEE_DETAILS = frozenset({
    'standard', 'large1', 'large2', 'service-provision', 'treatment-improvement',
    *(f'note.{n}' for n in range(1, 25)),
})
SPECIAL_DETAILS = frozenset({'note.7', 'note.8', 'treatment-improvement'})

ROOT_CHANGES = (
    ('厚生労働省の現行統合HTMLから通所介護費を区画ごとに取り込み、人手確認できる形にしています。',
     '厚生労働省の資料から通所介護費を区画ごとに取り込み、人手確認できる形にしています。', 1),
    ('<strong>公式現行本文は取り込み済みですが、人手確認は別工程です。</strong>',
     '<strong>公式資料の本文を収載していますが、現行性と人による確認は別途必要です。</strong>', 1),
    ('厚生労働省の現行HTMLには令和8年告示第87号まで反映されています。',
     '収載資料には令和8年告示第87号が反映されています。後の改正・訂正は原典で確認してください。', 1),
    ('<h2>現在の取得元</h2>', '<h2>収載資料の取得元</h2>', 1),
    ('<dt>現行告示</dt>', '<dt>収載した告示</dt>', 1),
    ('<dt>最新反映</dt>', '<dt>収載版に反映した改正</dt>', 1),
    ('通所介護費の現行本文・単位数・注・加算減算の取得元',
     '通所介護費の収載本文・単位数・注・加算減算の取得元', 1),
    ('各項目を開くと、厚生労働省の現行HTMLから取り込んだ本文と取得証跡を確認できます。',
     '各項目を開くと、厚生労働省の資料から取り込んだ本文と出典を確認できます。', 1),
    ('<p class="meta">現行公式本文を取込済み</p>', '<p class="meta">公式資料から本文を取込済み</p>', 28),
    ('<span class="fee-status">現行構造・人手確認待ち</span>', '<span class="fee-status">人手確認待ち</span>', 26),
    ('注意：機械構造化した各ノードは人手照合完了までVERIFIED_CURRENTにしない',
     '注意：機械で整理した各項目は、人による照合が終わっていません', 1),
)

SUMMARY_CHANGES = (
    ('<dt>本文</dt><dd>確認済み</dd>', '<dt>本文（機械照合）</dt><dd>確認済み</dd>', 1),
    ('<dt>現行性</dt><dd>確認中</dd>', '<dt>現行性</dt><dd>未確認</dd>', 1),
    ('現行性確認の対象末日：各ページの出典情報を参照',
     '収載版に反映した改正と原典は、出典情報を確認してください', 1),
    ('本文の独立確認、現行性の確認、人手確認は別々に管理しています。未確認の項目を確認済みとして表示しません。',
     '機械照合は2026年9月23日時点の収載資料について行ったものです。現行性の確認と人による確認は別です。', 1),
)


def replace_checked(content: str, changes: tuple, name: str) -> str:
    for old, new, expected in changes:
        actual = content.count(old)
        if actual != expected:
            raise RuntimeError(f'Unexpected fee label in {name}: {old!r}: {actual}, expected {expected}')
        content = content.replace(old, new)
    return content


def label_fee_version(content: str, relative: Path) -> tuple[str, str | None]:
    """Label known fee pages; reject source drift before any files are written."""
    if relative == Path('fees/index.html'):
        # Small synthetic navigation fixtures have no fee data or summary.
        if '<section class="rules-stats fee-stats">' not in content:
            return content, None
        content = replace_checked(content, ROOT_CHANGES, str(relative))
        return replace_checked(content, SUMMARY_CHANGES, str(relative)), 'fee_root_version_labels'

    parts = relative.parts
    if len(parts) != 3 or parts[0] != 'fees' or parts[2] != 'index.html' or parts[1] not in FEE_DETAILS:
        return content, None
    slug = parts[1]
    texts = re.findall(r'<div class="fee-official-text">.*?</div>', content, flags=re.DOTALL)
    if len(texts) != 1:
        raise RuntimeError(f'Unexpected imported fee text in {relative}')
    changes = [
        ('<dt>最新改正</dt><dd>令和8年厚生労働省告示第87号</dd>',
         '<dt>収載版に反映した改正</dt><dd>令和8年厚生労働省告示第87号</dd>', 1),
    ]
    if slug not in SPECIAL_DETAILS:
        changes.extend((
            ('<strong>現行公式本文を取込済み・人手確認待ち</strong>',
             '<strong>公式資料の本文を取込済み・人手確認待ち</strong>', 1),
            ('厚生労働省の現行HTMLから機械抽出した本文です。',
             '厚生労働省の資料から機械抽出した収載本文です。後の改正・訂正も原典で確認してください。', 1),
        ))
    if slug != 'treatment-improvement':
        changes.append(('<h2>現行公式本文</h2>', '<h2>収載した公式本文</h2>', 1))
    content = replace_checked(content, tuple(changes), str(relative))
    content = replace_checked(content, SUMMARY_CHANGES, str(relative))
    if re.findall(r'<div class="fee-official-text">.*?</div>', content, flags=re.DOTALL) != texts:
        raise RuntimeError(f'Imported fee text changed in {relative}')
    return content, 'fee_detail_version_labels'
