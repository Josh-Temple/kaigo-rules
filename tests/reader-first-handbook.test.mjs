import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import { createHash } from 'node:crypto';
import { isStaffingScopeOrException, readerEvidenceTitle, readerLabel, readerRequirementTitle, requirementCopy, separateHandbookParagraphs } from '../lib/handbook/reader-content.ts';
const h=JSON.parse(fs.readFileSync('data/handbook-content.json','utf8'));
const baseline=JSON.parse(fs.readFileSync('tests/fixtures/reader-first-baseline-sha256.json','utf8'));
const latest=JSON.parse(fs.readFileSync("docs/handbook-quality/2026-10-25-research-mesh-integration.json","utf8")).inputs;
const hash=value=>createHash('sha256').update(JSON.stringify(value)).digest('hex');
const chapter=sid=>h.services[sid].chapters.staffing;

test('585 chapters retain original fields; only scoped staffing projections and one inaccurate checkpoint change',()=>{
 assert.equal(Object.keys(h.services).length,39);
 let count=0;
 for(const [key,expected] of Object.entries(baseline.chapters)) {
  const [sid,cid]=key.split('/');count++;
  const current=structuredClone(h.services[sid].chapters[cid]);
  const added=latest.find(x=>x.service_id===sid&&x.chapter_id===cid);
  if(added) delete current[added.field];
  if(key==='community-elderly-facility/applicability') delete current.rule_sections;
  const {role_sections,...rest}=current;
  if(key==='dayservice/staffing') {
   assert.equal(rest.checkpoints[3],"生活相談員は事業所単位で提供日ごとの勤務時間を、看護職員・介護職員は提供単位ごとの配置を、機能訓練指導員は事業所ごとの配置を満たしているか");
   rest.checkpoints=[...rest.checkpoints];rest.checkpoints[3]="生活相談員・看護職員・介護職員・機能訓練指導員の員数基準（第93条第1項）を単位ごとに満たしているか（生活相談員・介護職員は時間数ベースの算定）";
  }
  assert.equal(hash(['dayservice','dayrehab'].includes(sid)&&cid==='staffing'?rest:current),expected,key);
 }
 assert.equal(Object.values(h.services).reduce((n,s)=>n+Object.keys(s.chapters).length,0),585);
 assert.equal(count,585);
});

test('mixed metadata, exceptions and uncertainty never leave ordinary reader body',()=>{
 const originals=[
  '出典候補：data/a.json。施行版は未確認。例外として常時1人以上を確保する。',
  '勤務表を確認。根拠候補は収載済みの data/services/a.json。兼務は処遇に支障がない場合のみ。',
  '出典候補：e-Gov。適用条件は未確認。',
  '出典候補：data/a.json',
 ];
 const r=separateHandbookParagraphs(originals);
 assert.deepEqual(r.reader,originals.slice(0,3));
 assert.deepEqual(r.editorial,[originals[3]]);
 for(const service of Object.values(h.services)) for(const c of Object.values(service.chapters)) {
  const split=separateHandbookParagraphs(c.paragraphs);
  for(const p of c.paragraphs) assert.ok(split.reader.includes(p)||split.editorial.includes(p));
  for(const p of split.editorial) assert.doesNotMatch(p,/未確認|条件|例外|施行|兼務|常勤|以上/);
 }
 const text='【Research Mesh隔離候補・法令適合未審査】原則専従。施行版・改正附則・条例・準用先との最終照合は未完了です。';
 assert.equal(requirementCopy(text),'原則専従。施行版・改正附則・条例・準用先との最終照合は未完了です。');
 assert.equal(readerLabel('管理者（Research Mesh未審査）'),'管理者');
});

test('dayservice five roles separate average hours, continuous duty and regional exceptions',()=>{
 const roles=chapter('dayservice').role_sections;
 assert.deepEqual(roles.map(r=>r.title),['生活相談員','看護職員','介護職員','機能訓練指導員','管理者']);
 const byId=Object.fromEntries(roles.map(r=>[r.id,r.requirements[0]]));
 const care=byId['care-worker'];
 assert.match(care.description,/利用者ごとの提供時間数の合計を利用者数で割/);
 assert.match(care.description,/15人以下/);
 assert.match(care.description,/1＋（利用者数－15）÷5/);
 assert.match(care.description,/10時間/);
 assert.match(care.description,/単位ごとに介護職員を常時1人以上/);
 assert.doesNotMatch(care.description,/合計を単位のサービス提供時間数で割/);
 assert.match(care.applicability,/指定を併せて受け、同一事業所/);
 assert.match(byId.nurse.description,/営業日ごとに利用者全員/);
 assert.match(byId.nurse.description,/契約先から適切な指示/);
 assert.match(byId.nurse.description,/Vol.1問59/);
 assert.ok(byId.nurse.evidence.some(e=>e.kind==='national_qa'&&e.locator.includes('問59')));
 assert.match(byId['life-counselor'].description,/9時間/);
 assert.match(byId['life-counselor'].description,/相談・援助に支障がない範囲/);
 assert.match(byId['life-counselor'].applicability,/事業所として1人以上は常勤/);
 assert.match(byId['functional-training'].description,/併設先の生活相談員又は機能訓練指導員により/);
 assert.match(byId.manager.description,/全国一律の法定勤務時間ではありません/);
 assert.ok(roles.every(r=>r.requirements.every(q=>q.verification_state==='EVIDENCE_GAP')));
});

test('dayrehab remains seven unverified requirements; clinic nurse experience is explicit',()=>{
 const q=chapter('dayrehab').role_sections.flatMap(r=>r.requirements);
 assert.equal(q.length,7); assert.ok(q.every(x=>x.verification_state==='EVIDENCE_GAP'));
 assert.match(q.find(x=>x.id==='clinic-exception').description,/1年以上/);
 assert.match(q.find(x=>x.id==='clinic-exception').description,/常勤換算0.1以上/);
 assert.match(q.find(x=>x.id==='specialist-one-per-hundred').description,/内数/);
 assert.equal(hash(chapter('homevisit')),baseline.chapters['homevisit/staffing']);
});


test('role navigation distinguishes staff from arithmetic and exceptions without changing anchors',()=>{
 assert.equal(isStaffingScopeOrException('看護職員'),false);
 assert.equal(isStaffingScopeOrException('介護職員'),false);
 assert.equal(isStaffingScopeOrException('利用者数の算定'),true);
 assert.equal(isStaffingScopeOrException('サテライトの特例'),true);
 assert.equal(readerRequirementTitle('確認事項','placement',0,1),'配置・員数');
 assert.equal(readerRequirementTitle('確認事項','concurrency',0,2),'兼務（1）');
 assert.equal(readerRequirementTitle('確認事項','concurrency',1,2),'兼務（2）');
 assert.equal(readerRequirementTitle('常勤の取扱い','other',0,1),'常勤の取扱い');
});

test('source titles keep audit metadata out of reader headings but never discard identifiers',()=>{
 assert.deepEqual(readerEvidenceTitle('data/shared/example.json'),{label:'資料識別情報（名称未確認）',technical:true});
 assert.deepEqual(readerEvidenceTitle('a'.repeat(64)),{label:'資料識別情報（名称未確認）',technical:true});
 assert.deepEqual(readerEvidenceTitle('横浜市運営の手引き'),{label:'横浜市運営の手引き',technical:false});
 const source=fs.readFileSync('components/service-handbook.tsx','utf8');
 assert.ok(source.includes('staffing-role'));
 assert.match(source,/handbook-role-requirement/);
 assert.ok(source.includes('readerEvidenceTitle(evidence.title)'));
});
