import test from 'node:test';
import assert from 'node:assert/strict';
import { issueRegistry } from '../app/issues/registry.ts';
import { actionToolForIssue, actionToolRoutes } from '../lib/action-tools.ts';

const expected = new Map([
  ['/issues/information-search', '/tools/information-inventory'],
  ['/issues/documentation', '/tools/documentation-review'],
  ['/issues/training-handover', '/tools/training-handover-inventory'],
  ['/issues/communication-collaboration', '/tools/communication-review'],
  ['/issues/productivity-utilization', '/tools/work-time-review'],
]);

test('all five public issues have exactly one action tool', () => {
  assert.equal(actionToolRoutes.length, issueRegistry.length);
  assert.equal(new Set(actionToolRoutes.map((tool) => tool.href)).size, issueRegistry.length);
  assert.equal(new Set(actionToolRoutes.map((tool) => tool.issueHref)).size, issueRegistry.length);

  for (const issue of issueRegistry) {
    assert.equal(actionToolForIssue(issue.href)?.href, expected.get(issue.href), issue.href);
  }
});

test('every action tool returns to its issue evidence', () => {
  for (const tool of actionToolRoutes) {
    assert.ok(tool.evidenceHref.startsWith(tool.issueHref));
    assert.ok(tool.evidenceHref.endsWith('#evidence'));
  }
});
