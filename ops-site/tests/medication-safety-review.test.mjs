import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import {
  CHECK_FIELDS, CHECK_STATES, PROCESS_STAGES,
  deriveReview, emptyReview, fictionalReview,
} from "../lib/medication-safety-review.ts";
import { actionToolRoutes } from "../lib/action-tools.ts";
import { issueRegistry } from "../app/issues/registry.ts";

test("empty review remains explicitly unverified", () => {
  const state = emptyReview();
  const result = deriveReview(state);
  assert.equal(result.valid, true);
  assert.match(result.lines[0], /未選択/);
  assert.equal(result.lines.length, CHECK_FIELDS.length + 1);
  assert.match(result.note, /評価するものではありません/);
});

test("fictional selections lead to fixed workflow questions, not medicine advice", () => {
  const result = deriveReview(fictionalReview());
  assert.equal(result.valid, true);
  assert.equal(result.lines.length, 4);
  assert.ok(result.lines.some(item => item.includes("役割") || item.includes("担当")));
  assert.ok(result.lines.some(item => item.includes("変更情報")));
  assert.ok(!result.lines.some(item => /投与量|再投与|服薬を中止|事故確率|適合保証/.test(item)));
});

test("not-applicable and fully confirmed selections never provide reassurance", () => {
  const state = emptyReview();
  state.stage = "preparation";
  for (const field of CHECK_FIELDS) state.checks[field.key] = "not-applicable";
  const notApplicable = deriveReview(state);
  assert.equal(notApplicable.lines.length, CHECK_FIELDS.length);
  assert.ok(notApplicable.lines.every(line => line.includes("範囲と理由")));
  for (const field of CHECK_FIELDS) state.checks[field.key] = "confirmed";
  const confirmed = deriveReview(state);
  assert.deepEqual(confirmed.lines, []);
  assert.match(confirmed.note, /自己申告/);
  assert.match(confirmed.note, /保証しません/);
});

test("unknown stages, unknown fields and unexpected structures fail closed", () => {
  const sample = emptyReview();
  const tampered = [
    null,
    {},
    { ...sample, stage: "medicine-X" },
    { ...sample, checks: { ...sample.checks, procedure: "ADMINISTER_NOW" } },
    { ...sample, checks: { ...sample.checks, extra: "病名" } },
    { ...sample, checks: { procedure: "confirmed" } },
    { ...sample, extra: "person-identifier" },
    { ...sample, checks: null },
  ];
  for (const payload of tampered) {
    const result = deriveReview(payload);
    assert.equal(result.valid, false);
    assert.equal(result.lines.length, 1);
    assert.ok(!JSON.stringify(result).includes("ADMINISTER_NOW"));
    assert.ok(!JSON.stringify(result).includes("medicine-X"));
    assert.ok(!JSON.stringify(result).includes("person-identifier"));
  }
});

test("all input choices are bounded enums with no free text", () => {
  assert.equal(new Set(CHECK_FIELDS.map(field => field.key)).size, CHECK_FIELDS.length);
  assert.equal(new Set(CHECK_STATES.map(choice => choice.value)).size, CHECK_STATES.length);
  assert.equal(new Set(PROCESS_STAGES.map(stage => stage.value)).size, PROCESS_STAGES.length);
  const worksheet = readFileSync(new URL("../app/tools/medication-safety-preview/worksheet.tsx", import.meta.url), "utf8");
  const page = readFileSync(new URL("../app/tools/medication-safety-preview/page.tsx", import.meta.url), "utf8");
  assert.doesNotMatch(worksheet, /<(input|textarea)\b/i);
  assert.match(page, /MEDICATION_SAFETY_PREVIEW !== "enabled"/);
  assert.match(page, /notFound\(\)/);
  assert.match(page, /index: false/);
  assert.doesNotMatch(worksheet + page, /(?:localStorage|sessionStorage|sendBeacon|XMLHttpRequest|fetch\(|navigator\.clipboard|URLSearchParams)/);
  assert.match(worksheet, /window\.print\(\)/);
});

test("public registries remain at five entries without the preview route", () => {
  assert.equal(issueRegistry.length, 5);
  assert.equal(actionToolRoutes.length, 5);
  const published = [...issueRegistry.map(issue => issue.href), ...actionToolRoutes.map(tool => tool.href)];
  assert.ok(!published.some(href => href.includes("medication-safety")));
});
