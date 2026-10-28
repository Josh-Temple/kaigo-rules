import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';

const component = fs.readFileSync('components/service-handbook.tsx', 'utf8');
const css = fs.readFileSync('app/globals.css', 'utf8');
const data = JSON.parse(fs.readFileSync('data/handbook-content.json', 'utf8'));

test('three pilot services read staffing requirements in the same handbook', () => {
  assert.match(component, /inlineStaffing = staffing && !full && \["dayservice", "dayrehab", "homevisit"\]\.includes\(service\.service_id\)/);
  assert.match(component, /if \(!full && !inlineStaffing\) return/);
  assert.match(component, /<RoleNavigation roles=\{roles\} staffing=\{staffing\} anchor=\{anchor\} detailHref=\{detailHref\} full=\{true\} \/>/);
  assert.match(component, /<h4>\{readerLabel\(role\.title\)\}<\/h4>/);
  assert.match(component, /requirement\.applicability/);
  assert.match(component, /requirement\.practical_checks/);
  assert.match(component, /requirement\.evidence/);
  for (const service of ['dayservice', 'dayrehab', 'homevisit']) {
    assert.ok(data.services[service].chapters.staffing.role_sections.length > 0, service);
  }
});

test('all services have an obvious staffing jump, full detail, return and chapter sequence', () => {
  assert.match(component, /href="#staffing"/);
  assert.match(component, /人員基準を確認する/);
  assert.match(component, /職種別の配置・勤務・資格を確認する/);
  assert.match(component, /前の章：/);
  assert.match(component, /次の章：/);
  assert.match(component, /の手引に戻る/);
  assert.match(css, /handbook-primary-action a:focus-visible/);
  assert.match(css, /min-height:48px/);
  assert.equal(Object.keys(data.services).length, 39);
  assert.equal(Object.values(data.services).reduce((n,s) => n + Object.keys(s.chapters).length,0),585);
});

test('readability changes do not hide original legal uncertainty or switch service roles', () => {
  assert.match(component, /requirement\.verification_state === "EVIDENCE_GAP"/);
  assert.match(component, /evidence\.verification_state === "PRIMARY_TEXT_CHECKED_SCOPED"/);
  assert.match(component, /parts\s*\?\s*parts\.segments/);
  assert.match(component, /isStaffingScopeOrException/);
  assert.ok(data.services.dayservice.chapters.staffing.role_sections.some(x => x.title === '生活相談員'));
  assert.ok(data.services.dayrehab.chapters.staffing.role_sections.some(x => x.title === '医師'));
  assert.ok(data.services.homevisit.chapters.staffing.role_sections.some(x => x.title.includes('訪問介護')));
});

test('dayservice nursing role links to the existing Q&A without implying legal verification', () => {
  const questions = JSON.parse(fs.readFileSync('data/questions.json', 'utf8'));
  assert.ok(questions.some(question => question.slug === 'nurse-staffing'));
  assert.ok(component.includes('service.service_id === "dayservice" && staffing && role.title.includes("看護職員")'));
  assert.ok(component.includes('href="/questions/nurse-staffing"'));
  assert.ok(component.includes('連携・兼務の適用条件は、国の解釈通知・Q&Aの現行内容を別途確認してください'));
  assert.match(component, /requirement\.verification_state === "EVIDENCE_GAP"/);
  assert.match(component, /requirement\.evidence\.map/);
});

test('nursing Q&A links back to the exact handbook staffing section', () => {
  const page = fs.readFileSync('app/questions/[slug]/page.tsx', 'utf8');
  assert.match(page, /slug === "nurse-staffing"/);
  assert.match(page, /href="\/services\/dayservice#staffing"/);
  assert.match(page, /通所介護の手引「人員基準」に戻る/);
  assert.match(component, /id=\{chapter.section_id\}/);
});

test('homevisit staffing explains the abbreviated service manager term', () => {
  assert.match(component, /service.service_id === "homevisit" && chapter.section_id === "staffing"/);
  assert.ok(component.includes('「サ責」は「サービス提供責任者」の略称です'));
  assert.match(component, /requirement\.verification_state === "EVIDENCE_GAP"/);
});

test('homevisit 50-user exception includes rounded-up remainder without relaxing its three conditions', () => {
  const staffing = data.services.homevisit.chapters.staffing;
  const text = staffing.paragraphs.join('\n');
  assert.ok(text.includes('利用者50人又はその端数を増すごとに1人以上とすることができます（第5条第5項）'));
  assert.ok(!text.includes('利用者50人ごとに1人以上とできます（第5条第5項）'));
  assert.ok(text.includes('常勤のサービス提供責任者を3人以上配置し'));
  assert.ok(text.includes('サービス提供責任者の業務に主として従事する者を1人以上配置している'));
  assert.ok(text.includes('業務が効率的に行われている場合'));
  assert.equal(Object.keys(data.services).length, 39);
  assert.equal(Object.values(data.services).reduce((total, service) => total + Object.keys(service.chapters).length, 0), 585);
});

test('dayrehab distinguishes facility-type entry points without asserting unverified staffing figures', () => {
  assert.ok(component.includes('service.service_id === "dayrehab" && staffing'));
  assert.ok(component.includes('施設の種類ごとに確認する条項'));
  for(const article of ['第111条第1項・第3項','第111条第2項','第111条第4項','第111条第5項']) {
    assert.ok(component.includes(article), article);
  }
  assert.ok(component.includes('各施設基準の具体的な員数は確認中です'));
  assert.ok(component.includes('第116条の管理代行の規定だけでは判断できません'));
  assert.ok(component.includes('https://laws.e-gov.go.jp/law/411M50000100037'));
  assert.ok(data.services.dayrehab.chapters.staffing.role_sections.every(role => role.requirements.every(req => req.verification_state === 'EVIDENCE_GAP')));
});
