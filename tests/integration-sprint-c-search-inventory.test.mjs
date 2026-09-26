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

test("C1 inventory: cross-source search directly wires the four current source families", () => {
  for (const dataPath of [
    "data/questions.json",
    "data/ordinance37-nodes.json",
    "data/qa-corpus.json",
    "data/remuneration-current-skeleton.json",
    "data/remuneration-current-text.json",
  ]) {
    assert.ok(searchPage.includes(dataPath), `expected /search to import ${dataPath}`);
  }

  for (const excludedPath of [
    "data/notice-nodes.json",
    "data/fee-guidance-current-skeleton.json",
    "data/care-insurance-act-nodes.json",
    "data/relationships.json",
  ]) {
    assert.ok(!searchPage.includes(excludedPath), `expected /search not to import ${excludedPath} at the C1 baseline`);
  }
});

test("C1 inventory: FAQ authority links are detail-page-only and verified-gated", () => {
  assert.match(questionPage, /const linkedRules = isVerified \?/);
  assert.match(questionPage, /const linkedNotices = isVerified \?/);
  assert.match(questionPage, /const linkedQa = isVerified \?/);
  assert.match(questionPage, /question\.source_refs\?\.filter/);

  assert.ok(!searchPage.includes("notice_node_ids"));
  assert.ok(!searchPage.includes("qa_item_ids"));
  assert.ok(!searchPage.includes("rule_node_ids"));
});
