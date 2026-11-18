import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import { createHash } from 'node:crypto';
import { spawnSync } from 'node:child_process';
import { serviceHandbooks } from '../lib/working-handbook.ts';

const read=p=>JSON.parse(fs.readFileSync(p,'utf8'));
const authored=read('data/handbook-content.json');
const ledger=read('docs/handbook-quality/2026-10-25-research-mesh-integration.json');
const baseline=read('tests/fixtures/research-mesh-20261025-baseline.json');
const stable=v=>JSON.stringify(v&&typeof v==='object'?(Array.isArray(v)?v.map(x=>JSON.parse(stable(x))):Object.fromEntries(Object.keys(v).sort().map(k=>[k,JSON.parse(stable(v[k]))]))):v);
const hash=v=>createHash('sha256').update(stable(v)).digest('hex');
const targetMap=new Map(ledger.inputs.map(a=>[`${a.service_id}/${a.chapter_id}`,a]));
const bRuleTargets=new Set(['designation','deductions','additions','remuneration','applicability'].map(id=>`community-elderly-facility/${id}`));
const reqs=a=>authored.services[a.service_id].chapters[a.chapter_id][a.field].flatMap(g=>g.requirements);

test('20 additive projections retain every field of all 585 main chapters, including old Mesh candidates',()=>{
 assert.equal(baseline.baseline_commit,'39298844165ce5df7c2ac0ae02fe8a599719c5e3');
 assert.equal(targetMap.size,20);assert.equal(new Set(ledger.inputs.map(x=>x.service_id)).size,13);
 assert.equal(Object.keys(authored.services).length,39);let count=0;
 for(const [sid,service] of Object.entries(authored.services))for(const [cid,chapter] of Object.entries(service.chapters)){
  const key=`${sid}/${cid}`,target=targetMap.get(key),copy=structuredClone(chapter);
  if(target)delete copy[target.field];
  if(bRuleTargets.has(key))delete copy.rule_sections;
  assert.equal(hash(copy),baseline.chapters[key],key);count++;
 }
 assert.equal(count,585);
 assert.deepEqual([...targetMap.keys()].sort(),[...baseline.targets].sort());
 for(const a of ledger.inputs){
  const chapter=serviceHandbooks.find(s=>s.service_id===a.service_id).chapters.find(c=>c.section_id===a.chapter_id);
  assert.deepEqual(chapter[a.field],authored.services[a.service_id].chapters[a.chapter_id][a.field]);
 }
});

test('every selected source rule maps once; Japanese conditions, exceptions, numeric units and uncertainty remain visible',()=>{
 let count=0;
 for(const a of ledger.inputs){
  const actual=reqs(a);assert.equal(actual.length,a.selected_rules);assert.equal(a.mapping.length,actual.length);
  assert.equal(new Set(a.mapping.map(x=>x.source_rule_id)).size,actual.length);
  assert.match(a.source_zip_sha256,/^[0-9a-f]{64}$/);assert.ok(a.review_library_id&&a.integrate_library_id);
  for(const m of a.mapping){
   const q=actual.find(x=>x.id===m.requirement_id);assert.ok(q);assert.equal(hash(q),m.reader_text_sha256);
   const text=q.description+' '+q.applicability,src=m.source_rule;
   for(const field of ['conditions','condition','exceptions','exception','note','verification_required','frequency_text','read_across','employee_read_across','obligation_wording']){
    const vals=Array.isArray(src[field])?src[field]:[src[field]];
    for(const value of vals)if(typeof value==='string'&&/[ぁ-んァ-ン一-龯]/.test(value))assert.ok(text.includes(value),`${a.service_id}/${m.source_rule_id}: lost ${field}`);
   }
   for(const n of [src.min_count,src.ratio_users_per,src.measurement?.value])if(n!==undefined&&n!==null)assert.ok(text.includes(String(n)),`${a.service_id}/${m.source_rule_id}: lost numeric value ${n}`);
   assert.equal(q.verification_state,'EVIDENCE_GAP');assert.match(text,/未完了/);
   assert.ok(q.evidence.every(e=>e.verification_state==='SOURCE_CANDIDATE_UNVERIFIED'&&!e.url&&!e.checked_at_jst));
   count++;
  }
 }
 assert.equal(count,459);
 assert.equal(ledger.offline_tests.reduce((n,x)=>n+x.test_count,0),459);
 assert.ok(ledger.offline_tests.every(x=>x.exit_code===0&&x.test_count>0));
});

test('important revision conditions and jurisdiction/source distinctions survive adaptation',()=>{
 const find=(sid,id)=>reqs(targetMap.get(sid+'/staffing')).find(x=>x.id===id);
 assert.match(find('shortstay-life','mesh-life-counselor').description,/通常型と介護予防型の両方の利用者数/);
 const bathing=find('homebath','mesh-d-preventive-link').description;
 for(const phrase of ['両サービスの指定','同一事業所','一体的に運営','第47条第1項','第47条第2項','1人追加'])assert.ok(bathing.includes(phrase));
 const all=ledger.inputs.filter(x=>x.service_id==='community-elderly-facility');
 for(const a of all)for(const m of a.mapping){
  const q=reqs(a).find(x=>x.id===m.requirement_id);
  if(m.source_rule.scope==='yokohama_unit')assert.equal(q.evidence[0].kind,'yokohama_ordinance');
  if(a.chapter_id==='notifications')assert.equal(q.evidence.length,0,'forms and city rules must not be mislabeled as standards or ordinances');
  if(m.source_rule.retention_years===null)assert.match(q.description,/保存期間を確定できません/);
  if(m.source_rule.measurement?.comparison==='STANDARD')assert.match(q.description,/最低義務と同一視しない/);
 }
});

test('nonstaffing rule schema remains restricted to explicitly allowlisted chapters and rejects false verification, XSS and unsafe links',()=>{
 const a=targetMap.get('community-elderly-facility/equipment');
 const valid=authored.services[a.service_id].chapters[a.chapter_id].rule_sections;
 const validate=(sid,cid,rows,field='rule_sections')=>spawnSync('python',['-B','-c',`import importlib.util,json,sys
s=importlib.util.spec_from_file_location('b','scripts/build_handbook_site.py');b=importlib.util.module_from_spec(s);s.loader.exec_module(b)
sid,cid,rows,field=json.load(sys.stdin)
try:b.validate_role_sections(sid,cid,rows,field=field)
except ValueError:sys.exit(2)
`],{input:JSON.stringify([sid,cid,rows,field]),encoding:'utf8'}).status;
 assert.equal(validate(a.service_id,a.chapter_id,valid),0);
 assert.equal(validate('homevisit','equipment',valid),2);
 assert.equal(validate(a.service_id,'designation',authored.services[a.service_id].chapters.designation.rule_sections),0);
 assert.equal(validate(a.service_id,'national_qa',valid),2);
 assert.equal(validate(a.service_id,a.chapter_id,valid,'role_sections'),2);
 for(const mutate of [r=>r[0].requirements[0].verification_state='PRIMARY_TEXT_CHECKED_SCOPED',r=>r[0].requirements[0].description='<img src=x onerror=alert(1)>',r=>r[0].requirements[0].evidence[0].url='javascript:alert(1)',r=>r[0].requirements[0].evidence[0].url='https://www.mhlw.go.jp.evil.test/a']){
  const copy=structuredClone(valid);mutate(copy);assert.equal(validate(a.service_id,a.chapter_id,copy),2);
 }
});
