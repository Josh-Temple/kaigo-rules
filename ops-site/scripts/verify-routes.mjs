import assert from 'node:assert/strict';
import { issueRegistry } from '../app/issues/registry.ts';
const base = process.argv[2] || 'http://localhost:3000';
const home = await fetch(`${base}/`);
assert.equal(home.status, 200, 'home route');
const homeText = await home.text();
for (const issue of issueRegistry) {
  assert.ok(homeText.includes(`href="${issue.href}"`), `${issue.href}: homepage link`);
  const response = await fetch(`${base}${issue.href}`);
  assert.equal(response.status, 200, issue.href);
  const html = await response.text();
  assert.ok(html.includes('<h1>'), `${issue.href}: heading`);
  assert.ok(html.includes('id="evidence"'), `${issue.href}: evidence anchor`);
  assert.ok(html.includes('class="sourceRow"'), `${issue.href}: source links`);
  assert.ok(html.includes('https://kaigo-rules.vercel.app/'), `${issue.href}: rules link`);
  console.log(`PASS ${issue.href}`);
}
const documentation = await (await fetch(`${base}/issues/documentation`)).text();
assert.ok(documentation.includes('href="/tools/documentation-review"'), 'worksheet reachable from documentation');
const worksheet = await fetch(`${base}/tools/documentation-review`);
assert.equal(worksheet.status, 200, 'worksheet route');
const worksheetText = await worksheet.text();
for (const text of ['記録業務の', '確認・修正', '架空例を読み込む', '印刷・PDF保存', '送信・自動保存されません']) assert.ok(worksheetText.includes(text), `worksheet: ${text}`);
console.log('PASS /tools/documentation-review');
const actionTools = [
  {
    issue: '/issues/communication-collaboration',
    route: '/tools/communication-review',
    link: 'href="/tools/communication-review"',
    texts: ['問い合わせ・確認往復の', '送信・自動保存されません', '個人名', '例外時のエスカレーション', '改善成功とは判断しません'],
  },
  {
    issue: '/issues/productivity-utilization',
    route: '/tools/work-time-review',
    link: 'href="/tools/work-time-review"',
    texts: ['業務時間・待ち・間接業務の', '送信・自動保存されません', '個人評価', '直接ケア', '時間差だけでは改善成功'],
  },
];

for (const tool of actionTools) {
  const issueHtml = await (await fetch(`${base}${tool.issue}`)).text();
  assert.ok(issueHtml.includes(tool.link), `${tool.issue}: action tool link`);
  const response = await fetch(`${base}${tool.route}`);
  assert.equal(response.status, 200, tool.route);
  const html = await response.text();
  for (const expected of tool.texts) {
    assert.ok(html.includes(expected), `${tool.route}: ${expected}`);
  }
  assert.ok(html.includes('https://kaigo-rules.vercel.app/'), `${tool.route}: rules link`);
  console.log(`PASS ${tool.route}`);
}
