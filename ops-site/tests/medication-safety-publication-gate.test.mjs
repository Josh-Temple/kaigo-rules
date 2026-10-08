// Safety release guard: the medication-safety prototype must not be public before
// claim qualification, independent expert review, and explicit content approval.
// This is an exposure test, NOT a clinical safety test or authorization to publish.
// Once publication is explicitly approved, this gate must be replaced together
// with a traceable approval/version record and full adversarial browser tests.
import assert from 'node:assert/strict';
import { readFile, readdir } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import test from 'node:test';

const opsRoot = fileURLToPath(new URL('../', import.meta.url));
const read = (relativePath) =>
  readFile(path.join(opsRoot, relativePath), 'utf8');
const medicationPattern = /medication[-_]?safety|medication[-_]?review|誤薬|与薬|服薬/iu;

async function discoverPages(directory) {
  const entries = await readdir(directory, { withFileTypes: true });
  const paths = [];
  for (const entry of entries) {
    const fullPath = path.join(directory, entry.name);
    if (entry.isDirectory()) {
      paths.push(...await discoverPages(fullPath));
    } else if (entry.isFile() && /^page\.(?:js|jsx|ts|tsx|mdx)$/.test(entry.name)) {
      paths.push(path.relative(path.join(opsRoot, 'app'), fullPath));
    }
  }
  return paths;
}

test('unapproved medication safety is absent from public issue/tool registries', async () => {
  for (const relativePath of [
    'app/issues/registry.ts',
    'lib/action-tools.ts',
  ]) {
    const content = await read(relativePath);
    assert.doesNotMatch(
      content,
      medicationPattern,
      `${relativePath} must not advertise medication-safety content before approval`,
    );
  }
});

test('any medication-safety preview route is server-gated and noindex', async () => {
  const routes = await discoverPages(path.join(opsRoot, 'app'));
  const candidatePages = routes.filter((route) => medicationPattern.test(route));
  for (const page of candidatePages) {
    const source = await read(path.join('app', page));
    assert.match(source, /MEDICATION_SAFETY_PREVIEW\s*!==\s*["']enabled["']/);
    assert.match(source, /notFound\(\)/);
    assert.match(source, /index:\s*false/);
    assert.match(source, /force-dynamic/);
  }
  // This checks only source-level default denial. Production environment
  // and direct URL response must be independently verified by Worker E.
});

test('sitemap derives public issue URLs only from the reviewed registry', async () => {
  const sitemap = await read('app/sitemap.ts');
  assert.match(sitemap, /issueRegistry\.map/);
  assert.doesNotMatch(sitemap, medicationPattern);
});
