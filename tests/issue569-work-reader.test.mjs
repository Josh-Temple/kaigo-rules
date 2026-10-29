import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import { createHash } from 'node:crypto';
import { handbookReaderText, readerReferenceTokens } from '../lib/handbook/public-copy.ts';
import { safeHandbookEvidenceUrl } from '../lib/handbook/reader-content.ts';
import { staffingReadingGuides } from '../lib/handbook/staffing-reading-guide.ts';

const raw = fs.readFileSync('data/handbook-content.json');
const handbook = JSON.parse(raw);
const walkStrings = value => typeof value === 'string' ? [value] : Array.isArray(value)
  ? value.flatMap(walkStrings) : value && typeof value === 'object' ? Object.values(value).flatMap(walkStrings) : [];

test('all legal prose, role conditions, source states and 585 canonical chapters are byte-identical to the starting candidate', () => {
  assert.equal(createHash('sha256').update(raw).digest('hex'), '47a0ed8e1837e6f76ee0a6230f7bc0dcb0d5f5a62529bdb346ac3f4dc592a2f4');
  assert.equal(Object.keys(handbook.services).length, 39);
  assert.equal(Object.values(handbook.services).reduce((n, s) => n + Object.keys(s.chapters).length, 0), 585);
  for (const requirement of handbook.services.dayrehab.chapters.staffing.role_sections.flatMap(role => role.requirements)) {
    assert.equal(requirement.verification_state, 'EVIDENCE_GAP');
  }
});

test('display substitutions retain numbers, legal qualifications and explicit uncertainty around internal references', () => {
  const source = '出典候補：data/ordinance37-nodes.json。scopeは未確認。15人以下は1人以上。兼務は処遇に支障がない場合に限る。';
  assert.equal(handbookReaderText(source), '出典候補：基準省令第37号の掲載条文。対象範囲は未確認。15人以下は1人以上。兼務は処遇に支障がない場合に限る。');
  const unknown = 'data/private/new.json は未照合。第93条の例外は削除しない。';
  assert.equal(handbookReaderText(unknown), unknown);
  assert.equal(handbookReaderText('【Research Mesh隔離候補・法令適合未審査】施行版は未確認。'), '【法令との適合性は未確認】施行版は未確認。');
  assert.equal(handbookReaderText('EVIDENCE_GAP'), '根拠・適用条件を確認中');
  assert.equal(handbookReaderText('Research Meshの隔離候補： 常勤換算2以上とする候補。'), '未審査の説明候補： 常勤換算2以上とする候補。');
  assert.equal(handbookReaderText('Research Mesh固定資料における基準省令の参考条項'), '作成時に参照した基準省令の条項（適用関係は確認中）');
  // Every numeric clause outside a repository token remains available to readers.
  for (const value of walkStrings(handbook.services)) {
    let withoutPaths = value;
    for (const token of readerReferenceTokens) withoutPaths = withoutPaths.split(token).join('');
    const result = handbookReaderText(value);
    for (const number of withoutPaths.match(/[0-9０-９]+(?:[.．][0-9０-９]+)?/gu) || []) assert.ok(result.includes(number), number);
    for (const condition of ['未確認', '未照合', '未完了', '場合に限る', '全国共通', '横浜市', '常勤', '専従', '兼務']) {
      if (withoutPaths.includes(condition)) assert.ok(result.includes(condition), condition);
    }
  }
});

test('source links reject executable schemes, credentials, controls and local file paths', () => {
  for (const value of ['javascript:alert(1)', 'data:text/html,<script>', 'file:///etc/passwd', '/workspace/data/a.json', 'https://u:p@example.com', 'https://example.com\n']) assert.equal(safeHandbookEvidenceUrl(value), null);
  assert.equal(safeHandbookEvidenceUrl('https://www.mhlw.go.jp/web/t_doc?dataId=82999404'), 'https://www.mhlw.go.jp/web/t_doc?dataId=82999404');
  const renderer = fs.readFileSync('components/legal-record.tsx', 'utf8');
  assert.match(renderer, /safeHandbookEvidenceUrl\(record.url\)/);
  assert.match(renderer, /\{record.text\}/); // Original law quotations are not passed through display substitutions.
  assert.doesNotMatch(renderer, /dangerouslySetInnerHTML/);
});

test('priority services receive reading advice while unsupported services receive no new legal claims', () => {
  assert.deepEqual(Object.keys(staffingReadingGuides).sort(), ['dayrehab', 'dayservice', 'homevisit']);
  for (const guide of Object.values(staffingReadingGuides)) {
    assert.equal(guide.checks.length, 3);
    assert.doesNotMatch(guide.lead, /確認済み|適合済み|資格不要/);
  }
});
