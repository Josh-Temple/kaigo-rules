import test from 'node:test';
import assert from 'node:assert/strict';
import { actionToolForIssue, actionToolRoutes } from '../lib/action-tools.ts';

test('Worker B action tools cover information search and training/handover once each', () => {
  assert.equal(actionToolRoutes.length, 2);
  assert.equal(new Set(actionToolRoutes.map((tool) => tool.href)).size, 2);
  assert.equal(actionToolForIssue('/issues/information-search')?.href, '/tools/information-inventory');
  assert.equal(actionToolForIssue('/issues/training-handover')?.href, '/tools/training-handover-inventory');
});

test('every action tool returns to its issue evidence', () => {
  for (const tool of actionToolRoutes) {
    assert.ok(tool.evidenceHref.startsWith(tool.issueHref));
    assert.ok(tool.evidenceHref.endsWith('#evidence'));
  }
});
