import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {createHash} from 'node:crypto';

const source=JSON.parse(fs.readFileSync('data/handbook-content.json','utf8'));
const ledger=JSON.parse(fs.readFileSync('docs/handbook-quality/2026-10-25-research-mesh-integration.json','utf8'));
const stable=v=>JSON.stringify(v&&typeof v==='object'?(Array.isArray(v)?v.map(x=>JSON.parse(stable(x))):Object.fromEntries(Object.keys(v).sort().map(k=>[k,JSON.parse(stable(v[k]))]))):v);
const hash=v=>createHash('sha256').update(stable(v)).digest('hex');
const cases=[
  ['homebath','mesh-d-nurse','137da2a407118321cb38e952e076c435b50712e4e9a5923cb7eae91803d0fe13',/第50条第6号/,/第45条の事業所ごとの配置/],
  ['homenursing','mesh-station-nursing-fte','db39dd68cfcd16d086f928a59c540cd959230565c9f51eb46601a7d0fde08621',/常勤換算と職種の区別/,/病院・診療所型/],
  ['homenursing','mesh-manager-qualification','4eb509b3d5a0ba225981dc4339fb8c3589d86040082ca25ce1fc3d85caffbb8c',/やむを得ない理由/,/准看護師等が一般に管理者/],
  ['shortstay-life','mesh-full-time-attached-exception','470e0abf39f4a1d901cd884b0a56b09ed80bf6d89749c3d1198d41eb71b38cad',/併設事業所/,/利用定員20人未満/],
  ['community-specific-facility','mesh-point-nine-ratio','e68e4a1130b6260cd4ecdd5b44004f9ce12653eba4d8673ac05fde6d17efe9d8',/第1項第2号イ/,/常時1人以上/],
  ['community-specific-facility','mesh-point-nine-committee','273cb4c8cc7d386464113115f285c0ca98371d666492e8bbacb4de358112fccc',/5事項/,/第2号～第4号/]
];
test('A: six scoped staffing explanations retain primary-law limits and unverified source state',()=>{
  assert.equal(Object.keys(source.services).length,39);
  for(const [sid,id,expected,...patterns] of cases){
    const chapter=source.services[sid].chapters.staffing;
    const req=chapter.role_sections.flatMap(g=>g.requirements).find(x=>x.id===id);
    const mapped=ledger.inputs.find(x=>x.service_id===sid&&x.chapter_id==='staffing')?.mapping.find(x=>x.requirement_id===id);
    assert.ok(req&&mapped,`${sid}/${id}: mapping missing`);
    assert.equal(hash(req),expected,`${sid}/${id}: unreviewed textual change`);
    assert.equal(mapped.reader_text_sha256,expected,`${sid}/${id}: ledger drift`);
    for(const re of patterns)assert.match(req.description,re,`${sid}/${id}: condition lost`);
    assert.equal(req.verification_state,'EVIDENCE_GAP');
    assert.ok(req.evidence.every(e=>e.verification_state==='SOURCE_CANDIDATE_UNVERIFIED'&&!e.url&&!e.checked_at_jst));
  }
  assert.equal(ledger.inputs.reduce((n,x)=>n+x.selected_rules,0),459);
});
