import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';

const priorityIssues = [
  {
    issue: 'information-search',
    tool: '/tools/information-inventory',
    actions: ['正本', '保管場所', '更新責任', '探す経路'],
  },
  {
    issue: 'documentation',
    tool: '/tools/documentation-review',
    actions: ['記録', '転記', '探索', '後追い', '確認修正', '処理件数'],
  },
];

test('priority issues offer a bounded early action that matches their existing tool', () => {
  for (const { issue, tool, actions } of priorityIssues) {
    const source = readFileSync(new URL(`../app/issues/${issue}/page.tsx`, import.meta.url), 'utf8');
    const heroStart = source.indexOf('<section className="issueHero">');
    const summaryStart = source.indexOf('<section className="section issueSummary">');
    assert.ok(heroStart !== -1 && summaryStart > heroStart, issue + ': hero before summary');
    const hero = source.slice(heroStart, summaryStart);
    assert.equal(hero.split('className="issueEarlyAction"').length - 1, 1, issue + ': one early entry');
    assert.ok(hero.includes(`className="primaryLink" href="${tool}"`), issue + ': direct tool link');
    for (const term of actions) {
      assert.ok(hero.includes(term), issue + ': first step matches tool field ' + term);
    }

    // The new entry supplements, rather than replaces, the later action and evidence.
    const later = source.slice(summaryStart);
    assert.ok(later.includes(`href="${tool}"`), issue + ': later CTA preserved');
    assert.ok(later.includes('className="section boundary"'), issue + ': limitations preserved');
    assert.ok(later.includes('id="evidence"'), issue + ': evidence anchor preserved');
    assert.ok(later.includes('<IssueFollowThrough issuePath='), issue + ': Rules and feedback preserved');
    assert.equal(source.split('className="issueEarlyAction"').length - 1, 1);
  }
});

test('early entry stays compact on narrow screens', () => {
  const css = readFileSync(new URL('../app/globals.css', import.meta.url), 'utf8');
  assert.ok(css.includes('.issueEarlyAction {'));
  assert.ok(css.includes('.issueEarlyAction .primaryLink { max-width: 100%; }'));
});
