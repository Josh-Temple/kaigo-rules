import assert from 'node:assert/strict';
import { issueRegistry } from '../app/issues/registry.ts';
import { issueFollowThrough, RULES_HOME_HREF } from '../lib/issue-follow-through.ts';
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
  const followThrough = issueFollowThrough[issue.href];
  assert.ok(followThrough, `${issue.href}: follow-through config`);
  assert.ok(html.includes(`href=\"${followThrough.rulesHref}\"`), `${issue.href}: contextual Rules link`);
  assert.ok(html.includes(`href=\"${RULES_HOME_HREF}\"`), `${issue.href}: generic Rules link`);
  assert.ok(html.includes('GitHub Issuesでフィードバックする'), `${issue.href}: feedback link`);
  for (const text of ['何を試したか', 'どこで止まったか', '何が足りなかったか', '介護記録']) {
    assert.ok(html.includes(text), `${issue.href}: follow-through ${text}`);
  }
  console.log(`PASS ${issue.href}`);
}
const documentation = await (await fetch(`${base}/issues/documentation`)).text();
assert.ok(documentation.includes('href="/tools/documentation-review"'), 'worksheet reachable from documentation');
assert.ok(!documentation.includes('/questions/care-plan-content'), 'documentation does not hard-code a day-service-only Rules route');
const worksheet = await fetch(`${base}/tools/documentation-review`);
assert.equal(worksheet.status, 200, 'worksheet route');
const worksheetText = await worksheet.text();
for (const text of ['記録業務の', '確認・修正', '架空例を読み込む', '印刷・PDF保存', '送信・自動保存されません']) assert.ok(worksheetText.includes(text), `worksheet: ${text}`);
console.log('PASS /tools/documentation-review');
