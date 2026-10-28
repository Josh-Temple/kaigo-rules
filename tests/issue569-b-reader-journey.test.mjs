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
