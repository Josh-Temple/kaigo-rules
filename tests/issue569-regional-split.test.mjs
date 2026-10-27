import { test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import { splitDayserviceRegionalText } from '../lib/handbook/reader-content.ts';

test('dayservice regional separation retains every sentence in order', () => {
  const data = JSON.parse(fs.readFileSync('data/handbook-content.json', 'utf8'));
  const roles = data.services.dayservice.chapters.staffing.role_sections;
  for (const role of roles) for (const requirement of role.requirements) {
    const original = requirement.description;
    const { national, regional } = splitDayserviceRegionalText(original);
    assert.equal((national + regional).replace(/\s/g, ''), original.replace(/\s/g, ''));
    if (original.includes('横浜市')) assert.ok(regional.includes('横浜市'));
    else assert.equal(regional, '');
  }
});
