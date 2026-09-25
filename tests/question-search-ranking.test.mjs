import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

import { rankQuestionMatches } from "../lib/question-search.ts";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(__dirname, "..");
const questions = JSON.parse(
  fs.readFileSync(path.join(root, "data/questions.json"), "utf8"),
);
const benchmark = JSON.parse(
  fs.readFileSync(
    path.join(
      root,
      "docs/kaigo-ops/research/issues/information-search/machine-retrieval-benchmark-v0.1.json",
    ),
    "utf8",
  ),
);
const devSet = JSON.parse(
  fs.readFileSync(
    path.join(
      root,
      "docs/kaigo-ops/research/issues/information-search/machine-retrieval-dev-v0.1.json",
    ),
    "utf8",
  ),
);

test("all frozen machine-retrieval queries place the expected question in the top 3", () => {
  for (const scenario of benchmark.cases) {
    const ranked = rankQuestionMatches(questions, scenario.query);
    const rank =
      ranked.findIndex(
        (question) => question.slug === scenario.expected_question_slug,
      ) + 1;

    assert.ok(
      rank >= 1 && rank <= 3,
      `${scenario.id}: expected ${scenario.expected_question_slug} in top 3 for "${scenario.query}", got rank ${rank || "MISS"}`,
    );
  }
});

test("unrelated noise does not produce a practical-question hit", () => {
  assert.deepEqual(rankQuestionMatches(questions, "xyzabc123"), []);
});

test("development paraphrases place the expected question in the top 3", () => {
  for (const scenario of devSet.cases) {
    const ranked = rankQuestionMatches(questions, scenario.query);
    const rank =
      ranked.findIndex(
        (question) => question.slug === scenario.expected_question_slug,
      ) + 1;

    assert.ok(
      rank >= 1 && rank <= 3,
      `${scenario.id}: expected ${scenario.expected_question_slug} in top 3 for "${scenario.query}", got rank ${rank || "MISS"}`,
    );
  }
});

test("additional unrelated phrases do not produce practical-question hits", () => {
  for (const query of ["駐車場の料金", "今日は雨ですか", "介護保険とは関係ない雑談"]) {
    assert.deepEqual(rankQuestionMatches(questions, query), [], query);
  }
});
