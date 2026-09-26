import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

import { rankQuestionMatches } from "../lib/question-search.ts";
import { expandQuestionAuthorities } from "../lib/question-authority-expansion.ts";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(__dirname, "..");
const load = (relativePath) =>
  JSON.parse(fs.readFileSync(path.join(root, relativePath), "utf8"));

const questions = load("data/questions.json");
const relationships = load("data/relationships.json");
const rules = load("data/rule-nodes.json");
const notices = load("data/notice-nodes.json");
const qaItems = load("data/qa-items.json");
const fees = load("data/remuneration-current-skeleton.json").filter(
  (node) => node.service_scope === "通所介護",
);
const benchmark = load(
  "docs/kaigo-ops/research/issues/information-search/machine-retrieval-benchmark-v0.1.json",
);

const cases = ["MR-03-B", "MR-09-B"].map((id) => {
  const item = benchmark.cases.find((row) => row.id === id);
  assert.ok(item, `missing frozen benchmark case ${id}`);
  return item;
});

const authoritySourceIds = (authorities) => {
  const ids = new Set();
  for (const authority of authorities) {
    const record = authority.record;
    if (typeof record.source_id === "string") ids.add(record.source_id);
    for (const sourceId of record.source_ids || []) ids.add(sourceId);
  }
  return ids;
};

test("C4 frozen natural-language queries preserve FAQ relevance and explicit authority reachability", () => {
  for (const scenario of cases) {
    const ranked = rankQuestionMatches(questions, scenario.query);
    const rank =
      ranked.findIndex(
        (question) => question.slug === scenario.expected_question_slug,
      ) + 1;

    assert.ok(
      rank >= 1 && rank <= 3,
      `${scenario.id}: FAQ lexical rank was ${rank || "MISS"}`,
    );

    const matchedQuestions = ranked.slice(0, 3);
    const groups = expandQuestionAuthorities({
      questions: matchedQuestions,
      relations: relationships,
      rules,
      notices,
      qaItems,
      feeNodes: fees,
    });
    const expectedGroup = groups.find(
      (group) => group.questionSlug === scenario.expected_question_slug,
    );

    assert.ok(
      expectedGroup,
      `${scenario.id}: expected FAQ had no explicit authority expansion`,
    );

    const reachedSourceIds = authoritySourceIds(expectedGroup.authorities);
    for (const sourceId of scenario.expected_source_ids) {
      assert.ok(
        reachedSourceIds.has(sourceId),
        `${scenario.id}: expected source ${sourceId} was not reachable through explicit relations`,
      );
    }
  }
});

test("C4 lexical FAQ relevance remains when relation expansion is removed", () => {
  const scenario = cases.find((item) => item.id === "MR-03-B");
  const ranked = rankQuestionMatches(questions, scenario.query);

  assert.equal(ranked[0].slug, "nurse-staffing");

  const groups = expandQuestionAuthorities({
    questions: ranked.slice(0, 3),
    relations: [],
    rules,
    notices,
    qaItems,
    feeNodes: fees,
  });

  assert.deepEqual(groups, []);
});

test("C4 relation expansion never substitutes for FAQ lexical matching", () => {
  const groups = expandQuestionAuthorities({
    questions: [],
    relations: relationships,
    rules,
    notices,
    qaItems,
    feeNodes: fees,
  });

  assert.deepEqual(groups, []);
});
