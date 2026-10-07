import test from 'node:test';
import assert from 'node:assert/strict';
import { issueRegistry } from '../app/issues/registry.ts';
import {
  buildOpsFeedbackHref,
  issueFollowThrough,
  RULES_HOME_HREF,
} from '../lib/issue-follow-through.ts';

test('all five public issues have a production-safe Rules bridge', () => {
  assert.deepEqual(
    Object.keys(issueFollowThrough).sort(),
    issueRegistry.map((issue) => issue.href).sort(),
  );

  const rulesOrigin = new URL(RULES_HOME_HREF).origin;
  for (const issue of issueRegistry) {
    const config = issueFollowThrough[issue.href];
    const url = new URL(config.rulesHref);
    assert.equal(url.origin, rulesOrigin, issue.href + ': Rules origin');
    assert.equal(url.pathname, '/databases/search', issue.href + ': public search route');
    assert.equal(url.searchParams.has('service'), false, issue.href + ': service applicability is not guessed');
  }
});

test('feedback reuses GitHub Issues and carries the three minimal prompts and privacy boundary', () => {
  for (const issue of issueRegistry) {
    const url = new URL(buildOpsFeedbackHref(issue.href));
    assert.equal(url.origin, 'https://github.com');
    assert.equal(url.pathname, '/Josh-Temple/kaigo-rules/issues/new');
    const body = url.searchParams.get('body') || '';
    for (const prompt of ['何を試したか', 'どこで止まったか', '何が足りなかったか']) {
      assert.ok(body.includes(prompt), issue.href + ': ' + prompt);
    }
    for (const forbiddenInput of ['氏名', '利用者情報', '介護記録', '事業所の非公開情報']) {
      assert.ok(body.includes(forbiddenInput), issue.href + ': privacy warning ' + forbiddenInput);
    }
  }
});
