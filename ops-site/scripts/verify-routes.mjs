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
