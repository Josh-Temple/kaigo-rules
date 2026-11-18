import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {createHash} from 'node:crypto';

const file=JSON.parse(fs.readFileSync('data/handbook-content.json','utf8'));
const baseline=JSON.parse(fs.readFileSync('tests/fixtures/research-mesh-20261025-baseline.json','utf8'));
const service=file.services['community-elderly-facility'];
const expected={designation:8,deductions:8,additions:19,remuneration:8,applicability:2};
const stable=v=>JSON.stringify(v&&typeof v==='object'
 ?(Array.isArray(v)?v.map(x=>JSON.parse(stable(x))):Object.fromEntries(Object.keys(v).sort().map(k=>[k,JSON.parse(stable(v[k]))])))
 :v);
const hash=v=>createHash('sha256').update(stable(v)).digest('hex');

test('B 2026-10-26 retains the exact pre-B chapter fields and all 585 chapters',()=>{
 assert.equal(Object.keys(file.services).length,39);
 assert.equal(Object.values(file.services).reduce((n,s)=>n+Object.keys(s.chapters).length,0),585);
 let total=0;
 for(const [chapterId,count] of Object.entries(expected)){
  const chapter=service.chapters[chapterId];
  const preserved=structuredClone(chapter);delete preserved.rule_sections;
  assert.equal(hash(preserved),baseline.chapters[`community-elderly-facility/${chapterId}`],chapterId);
  assert.equal(chapter.rule_sections.length,1,chapterId);
  const req=chapter.rule_sections.flatMap(s=>s.requirements);
  assert.equal(req.length,count,chapterId);
  assert.equal(new Set(req.map(r=>r.id)).size,count,chapterId);
  for(const r of req){
    assert.equal(r.verification_state,'EVIDENCE_GAP',r.id);
    assert.ok(r.description.includes('未完了'),r.id);
    assert.ok(r.applicability.length>0,r.id);
    assert.ok(r.practical_checks.length>0,r.id);
    for(const e of r.evidence){
     assert.equal(e.verification_state,'SOURCE_CANDIDATE_UNVERIFIED',r.id);
     assert.equal(e.checked_at_jst,'',r.id);
     assert.equal('url' in e,false,r.id);
    }
    total++;
  }
 }
 assert.equal(total,45);
});

test('read-across states two direct replacements of a common original, not a chain',()=>{
 const r=service.chapters.applicability.rule_sections.flatMap(g=>g.requirements);
 const conventional=r.find(x=>x.id==='mesh-b-a5');
 const unit=r.find(x=>x.id==='mesh-b-a6');
 assert.match(conventional.description,/第157条/);
 assert.match(conventional.description,/「入所の際に」/);
 assert.match(unit.description,/第169条/);
 assert.match(unit.description,/「入居の際に」/);
 assert.match(unit.description,/直接「入居の際に」へ変えるのではありません/);
 assert.equal(conventional.verification_state,'EVIDENCE_GAP');
 assert.equal(unit.verification_state,'EVIDENCE_GAP');
});

test('fee unit displays are not billing decisions or yen prices',()=>{
 const r=service.chapters.remuneration.rule_sections.flatMap(g=>g.requirements);
 assert.equal(r.length,8);
 for(const x of r) {
  assert.match(x.description,/単位／日/);
  assert.match(x.description,/円ではなく/);
  assert.match(x.description,/経過措置/);
  assert.equal(x.verification_state,'EVIDENCE_GAP');
 }
});
