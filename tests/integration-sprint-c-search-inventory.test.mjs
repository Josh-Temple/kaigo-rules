import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(__dirname, "..");
const read = (relativePath) =>
  fs.readFileSync(path.join(root, relativePath), "utf8");

const searchPage = read("app/search/page.tsx");
const questionPage = read("app/questions/[slug]/page.tsx");
const inventory = read("docs/integration-sprint-c-search-inventory.md");

test("C1 inventory preserves the main-baseline source inventory as historical evidence", () => {
  assert.ok(inventory.includes("Baseline main SHA:"));
  assert.ok(inventory.includes("| Interpretation notices |"));
  assert.ok(inventory.includes("| Fee guidance / 老企第36号 |"));
  assert.ok(inventory.includes("| Care Insurance Act |"));
});

test("C2/C3 intentionally extend the C1 baseline without adding fee-guidance or Care Insurance Act search", () => {
  assert.ok(searchPage.includes("QuestionAuthorityPanel"));
  assert.ok(searchPage.includes("data/notice-nodes.json"));
  assert.ok(searchPage.includes("getSearchableNotices"));

  for (const stillExcludedPath of [
    "data/fee-guidance-current-skeleton.json",
    "data/care-insurance-act-nodes.json",
    "data/relationships.json",
  ]) {
    assert.ok(
      !searchPage.includes(stillExcludedPath),
      `expected /search not to directly import ${stillExcludedPath}`,
    );
  }
});

test("FAQ detail authority links remain verified-gated", () => {
  assert.match(questionPage, /const linkedRules = isVerified \?/);
  assert.match(questionPage, /const linkedNotices = isVerified \?/);
  assert.match(questionPage, /const linkedQa = isVerified \?/);
  assert.match(questionPage, /question\.source_refs\?\.filter/);
});
