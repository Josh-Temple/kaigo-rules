import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

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

const nurse = questions.find((item) => item.slug === "nurse-staffing");

test("C2 expands a matched verified FAQ only through explicit stored relations", () => {
  const groups = expandQuestionAuthorities({
    questions: [nurse],
    relations: relationships,
    rules,
    notices,
    qaItems,
    feeNodes: fees,
  });

  assert.equal(groups.length, 1);
  assert.deepEqual(
    groups[0].authorities.map((item) => [item.kind, item.targetId]),
    [
      ["standard", "ordinance37.article93.1.2"],
      ["notice", "notice.dayservice.nurse.external-linkage"],
      ["qa", "qa.dayservice.nurse.external.2015.50"],
    ],
  );
});

test("C2 does not infer authority links from question fields when relation rows are absent", () => {
  const groups = expandQuestionAuthorities({
    questions: [nurse],
    relations: [],
    rules,
    notices,
    qaItems,
    feeNodes: fees,
  });

  assert.deepEqual(groups, []);
});

test("C2 does not expand an unverified FAQ even when an explicit relation exists", () => {
  const groups = expandQuestionAuthorities({
    questions: [{ ...nurse, status: "draft" }],
    relations: relationships,
    rules,
    notices,
    qaItems,
    feeNodes: fees,
  });

  assert.deepEqual(groups, []);
});

test("C2 fails closed when an explicit relation target cannot be resolved", () => {
  const groups = expandQuestionAuthorities({
    questions: [nurse],
    relations: [
      {
        from: "question:nurse-staffing",
        relation: "interpreted_by",
        to: "notice.missing",
      },
    ],
    rules,
    notices,
    qaItems,
    feeNodes: fees,
  });

  assert.deepEqual(groups, []);
});

test("C2 supports fee records only when an explicit fee relation is supplied", () => {
  const fee = fees.find((item) => item.id === "fee.dayservice.note.24");
  const groups = expandQuestionAuthorities({
    questions: [nurse],
    relations: [
      {
        from: "question:nurse-staffing",
        relation: "priced_by",
        to: fee.id,
      },
    ],
    rules,
    notices,
    qaItems,
    feeNodes: fees,
  });

  assert.equal(groups[0].authorities[0].kind, "fee");
  assert.equal(groups[0].authorities[0].targetId, "fee.dayservice.note.24");
});
