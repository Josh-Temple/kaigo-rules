import test from 'node:test';
import assert from 'node:assert/strict';
import { emptyWorkTimePhase, workTimeSummary } from '../lib/work-time-review.ts';

function completePhase() {
  return {
    ...emptyWorkTimePhase(),
    times: {
      directCare: '100',
      requiredRecord: '20',
      movement: '10',
      waiting: '5',
      search: '5',
      coordination: '10',
      reentry: '5',
      meeting: '10',
      review: '5',
      otherIndirect: '10',
    },
  };
}

test('blank, negative and non-numeric values do not produce a comparison', () => {
  assert.equal(workTimeSummary(emptyWorkTimePhase()), null);
  const phase = completePhase();
  for (const waiting of ['', '-1', 'Infinity', 'oops']) {
    assert.equal(workTimeSummary({ ...phase, times: { ...phase.times, waiting } }), null);
  }
});

test('zero minutes are valid when every category has been measured', () => {
  const phase = completePhase();
  const zeroIndirect = {
    ...phase,
    times: Object.fromEntries(Object.keys(phase.times).map(key => [key, key === 'directCare' ? '120' : '0'])),
  };
  assert.deepEqual(workTimeSummary(zeroIndirect), {
    total: 120,
    directCare: 120,
    otherMeasured: 0,
  });
});

test('summary separates direct care from the rest without judging success', () => {
  assert.deepEqual(workTimeSummary(completePhase()), {
    total: 180,
    directCare: 100,
    otherMeasured: 80,
  });
});
