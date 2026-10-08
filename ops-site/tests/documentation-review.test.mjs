import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { emptyPhase, phaseSummary } from '../lib/documentation-review.ts';

test('unmeasured, invalid times and zero/invalid counts do not produce a comparison', () => {
  assert.equal(phaseSummary(emptyPhase()), null);
  const phase = { ...emptyPhase(), count: '20', times: { record: '60', copy: '40', search: '20', later: '20', review: '10' } };
  for (const count of ['', '0', '-1', '1.5', 'Infinity', 'oops']) assert.equal(phaseSummary({ ...phase, count }), null);
  for (const review of ['', '-1', 'Infinity', 'oops']) assert.equal(phaseSummary({ ...phase, times: { ...phase.times, review } }), null);
});
test('review effort can reverse an apparent reduction in writing time', () => {
  const phase = { ...emptyPhase(), count: '10', times: { record: '10', copy: '0', search: '0', later: '0', review: '0' } };
  const after = { ...phase, times: { ...phase.times, record: '5', review: '10' } };
  assert.equal(phaseSummary(phase)?.perRecord, 1);
  assert.equal(phaseSummary(after)?.perRecord, 1.5);
});
test('normalizes unequal workloads and accepts explicitly measured zero effort', () => {
  const phase = { ...emptyPhase(), count: '20', times: { record: '60', copy: '40', search: '20', later: '20', review: '10' } };
  assert.deepEqual(phaseSummary(phase), { count: 20, total: 150, perRecord: 7.5 });
  assert.equal(phaseSummary({ ...phase, count: '40' })?.perRecord, 3.75);
  assert.equal(phaseSummary({ ...phase, times: { record: '0', copy: '0', search: '0', later: '0', review: '0' } })?.total, 0);
});
