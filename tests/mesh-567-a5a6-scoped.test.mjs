import { test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';

const handbook = JSON.parse(fs.readFileSync('data/handbook-content.json','utf8'));
const service = handbook.services['community-elderly-facility'];
const section = service.chapters.applicability;
const rules = section.rule_sections;

test('A5 and A6 are the only new draft candidates from PR567, not its other 43', () => {
  assert.equal(Object.keys(handbook.services).length,39);
  assert.equal(Object.values(handbook.services).reduce((n,s)=>n+Object.keys(s.chapters).length,0),585);
  assert.equal(rules.length,1);
  assert.equal(rules[0].id,'mesh-b-readacross');
  assert.deepEqual(rules[0].requirements.map(x=>x.id),['mesh-b-a5','mesh-b-a6']);
  for(const id of ['designation','deductions','additions','remuneration']){
    assert.equal(service.chapters[id].rule_sections,undefined,id+' must not import PR567 holdlist');
  }
});

test('A5 uses original Article 3-11 through Article 157, A6 independently through Article 169', () => {
  const [ordinary,unit]=rules[0].requirements;
  assert.match(ordinary.description,/第3条の11第1項/);
  assert.match(ordinary.description,/第157条.*入所の際に/);
  assert.match(unit.description,/第3条の11第1項/);
  assert.match(unit.description,/第169条.*入居の際に/);
  assert.match(unit.description,/第169条が第157条の読替え結果.*直接.*ではありません/);
  assert.match(ordinary.applicability,/通常型/);
  assert.match(unit.applicability,/ユニット型/);
  assert.ok(!ordinary.applicability.includes('ユニット型'));
  assert.ok(!unit.applicability.includes('通常型'));
});

test('all A5/A6 editorial details stay unverified and source URLs are not invented',()=>{
  for(const q of rules[0].requirements) {
    assert.equal(q.verification_state,'EVIDENCE_GAP');
    assert.equal(q.evidence.length,1);
    assert.equal(q.evidence[0].kind,'national_standard');
    assert.equal(q.evidence[0].verification_state,'SOURCE_CANDIDATE_UNVERIFIED');
    assert.equal(q.evidence[0].url,undefined);
    assert.equal(q.evidence[0].checked_at_jst,'');
    assert.match(q.description,/改正附則.*地域の条例.*個別施設.*未確認/);
    assert.match(q.applicability,/施行版は確認が必要/);
    assert.ok(q.practical_checks.length>=2);
    assert.ok(!('authority_segments' in q),'do not author unverified source segments');
  }
});

test('the all-service chapter baselines still include prior 459 Research Mesh candidate requirements',()=>{
  const ledger=JSON.parse(fs.readFileSync('docs/handbook-quality/2026-10-25-research-mesh-integration.json','utf8'));
  const total=ledger.inputs.reduce((n,row)=>n+handbook.services[row.service_id].chapters[row.chapter_id][row.field].reduce((k,g)=>k+g.requirements.length,0),0);
  assert.equal(ledger.inputs.length,20);
  assert.equal(total,459);
});

test('new applicability rule section is accessible in the reader renderer for chapter and overview', () => {
  const source=fs.readFileSync('components/service-handbook.tsx','utf8');
  assert.match(source,/const ruleChapters = \["applicability"/);
  assert.match(source,/const roles = staffing \? chapter\.role_sections : chapter\.rule_sections/);
  assert.match(source,/\!full\) return <section className="handbook-role-preview"/);
  assert.match(source,/className="handbook-role-warning"/);
});
