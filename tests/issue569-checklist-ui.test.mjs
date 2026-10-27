import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";

const checklist = fs.readFileSync("components/handbook-checklist.tsx", "utf8");
const css = fs.readFileSync("components/handbook-checklist.module.css", "utf8");
const handbook = fs.readFileSync("components/service-handbook.tsx", "utf8");
const finder = fs.readFileSync("app/handbook-sources/page.tsx", "utf8");
const preview = fs.readFileSync("app/handbook-preview/page.tsx", "utf8");

test("all service chapters use the same optional web checklist, without JSON as a reader requirement", () => {
  assert.match(handbook, /<HandbookChecklist items=\{chapter\.checkpoints\} chapterTitle=\{chapter\.title\} printable=\{full\} \/>/u);
  assert.match(checklist, /type="checkbox"/u);
  assert.match(checklist, /<label>/u);
  assert.match(checklist, /チェック状態は保存されず/u);
  assert.match(checklist, /法令への適合を証明するものではありません/u);
  assert.doesNotMatch(checklist, /localStorage|sessionStorage|fetch\(|\.json/u);
  assert.match(checklist, /items\.map\(\(point, index\)/u);
  assert.match(checklist, /\{point\}/u);
});

test("print is an explicit action and checked boxes remain visible on paper", () => {
  assert.match(checklist, /onClick=\{\(\) => window\.print\(\)\}/u);
  assert.match(css, /@media print/u);
  assert.match(css, /input:checked \+ \.printMark::before\{content:"☑"\}/u);
  assert.match(css, /\.printMark::before\{content:"☐"\}/u);
  assert.match(css, /break-inside:avoid/u);
  assert.match(css, /min-height:48px/u);
  assert.match(css, /focus-visible/u);
});

test("public source finder hides internal candidate IDs but preserves the source review warning", () => {
  assert.doesNotMatch(finder, /\{item\.bridge_id\}/u);
  assert.doesNotMatch(finder, /\{item\.evidence_task_id\}/u);
  assert.match(finder, /出典の現行性と適用条件は確認中/u);
  assert.match(finder, /掲載先の原典を個別に照合/u);
  // Non-rendered keys and integrity checks must remain intact.
  assert.match(finder, /key=\{item\.bridge_id\}/u);
  assert.match(finder, /p\.evidence_task_id !== r\.task_id|evidence\.get\(p\.evidence_task_id\)/u);
  assert.match(preview, /process\.env\.VERCEL_ENV !== "preview"/u);
  assert.match(preview, /notFound\(\)/u);
});
