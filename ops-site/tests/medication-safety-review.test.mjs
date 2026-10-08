import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import {
  CHECK_FIELDS, CHECK_STATES, PROCESS_STAGES, WORKFLOW_BOUNDARY,
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
  assert.match(result.note, /評価・認証するものではありません/);
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
  assert.ok(notApplicable.lines.every(line => line.includes("責任者・関係職種")));
  for (const field of CHECK_FIELDS) state.checks[field.key] = "confirmed";
  const confirmed = deriveReview(state);
  assert.deepEqual(confirmed.lines, []);
  assert.match(confirmed.note, /自己申告・未検証/);
  assert.match(confirmed.note, /実施権限、制度適合を保証しません/);
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

test("B-05 vocabulary is consistent, descriptive and not a validated safety scale", () => {
  assert.deepEqual(CHECK_STATES.map(choice => choice.label), [
    "まだ確認していない",
    "取扱いを把握している（自己申告・未検証）",
    "相談したい点がある",
    "取り決めが見つからない",
    "自分の担当範囲では扱わない（責任者確認前）",
  ]);
  assert.deepEqual(PROCESS_STAGES.slice(1).map(stage => stage.label), [
    "変更情報の受領・共有",
    "配薬準備の運用",
    "配薬・服薬確認に関する運用",
    "記録・引き継ぎ",
  ]);
  const state = emptyReview();
  state.stage = "instruction-update";
  for (const field of CHECK_FIELDS) state.checks[field.key] = "confirmed";
  const allReported = deriveReview(state);
  assert.equal(allReported.valid, true);
  assert.equal(allReported.lines.length, 0);
  assert.match(allReported.note, /未検証/);
  assert.match(allReported.note, /安全性、事故防止、実施権限、制度適合を保証しません/);
  state.checks.procedure = "not-applicable";
  const mixed = deriveReview(state);
  assert.equal(mixed.valid, true);
  assert.match(mixed.lines[0], /担当権限を責任者・関係職種に確認/);
  assert.doesNotMatch(mixed.note + mixed.lines.join(""), /安全が確認されました|法令適合を認定|次の服薬を指示/);
});

test("shared B-08.2 result-and-print warning is fixed and never gives medical or legal clearance", () => {
  assert.equal(WORKFLOW_BOUNDARY, "この結果は平時の業務工程に関する自己申告を整理したものです。安全性・医療上の正しさ・職種権限・制度適合・事故報告の要否を判定しません。事故や服薬上の疑義が現にある場合は、このシートを使わず、所属先の正式手順に従い、管理者・関係する医療専門職に連絡してください。");
  assert.match(WORKFLOW_BOUNDARY, /事故報告の要否を判定しません/);
  const worksheet = readFileSync(new URL("../app/tools/medication-safety-preview/worksheet.tsx", import.meta.url), "utf8");
  assert.equal((worksheet.match(/\{WORKFLOW_BOUNDARY\}/g) ?? []).length, 2);
});

test("printed and interactive content retain the accident and self-report boundary", () => {
  const worksheet = readFileSync(new URL("../app/tools/medication-safety-preview/worksheet.tsx", import.meta.url), "utf8");
  const page = readFileSync(new URL("../app/tools/medication-safety-preview/page.tsx", import.meta.url), "utf8");
  assert.match(page, /事故や服薬上の疑義が発生している場合、このシートは使わないでください/);
  assert.match(worksheet, /事故・服薬上の疑義が現にある場合は使用しないでください/);
  assert.match(worksheet, /独自の設計案/);
  assert.match(worksheet, /未検証/);
  assert.match(worksheet, /医療上の判断を保証しません/);
  assert.match(worksheet, /必要な緊急対応、適用される法令・自治体の手続/);
  assert.match(worksheet, /本人の意思・尊厳を尊重してください/);
  assert.match(worksheet, /処方指示の正しさ・真正性/);
});
