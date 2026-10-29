import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import { dayserviceChapterParagraphHeading, dayserviceChecklistText, dayserviceReadableText, readerTextParagraphs } from "../lib/handbook/dayservice-reader-editorial.ts";
import { handbookReaderText, readerReferenceTokens } from "../lib/handbook/public-copy.ts";

const chapters = JSON.parse(fs.readFileSync("data/handbook-content.json", "utf8")).services.dayservice.chapters;

function allStrings(value) {
  if (typeof value === "string") return [value];
  if (Array.isArray(value)) return value.flatMap(allStrings);
  return value && typeof value === "object" ? Object.values(value).flatMap(allStrings) : [];
}

test("paragraph breaks preserve every character of all dayservice conditions, evidence and examples", () => {
  for (const value of allStrings(chapters)) assert.equal(readerTextParagraphs(value).join(""), value);
  const source = "原則として常勤です。".repeat(10) + "ただし、管理に支障がない場合に限り兼務できます（第94条）。";
  const result = readerTextParagraphs(source);
  assert.ok(result.length > 1);
  assert.equal(result.join(""), source);
  assert.ok(result.some(p => p.includes("ただし、管理に支障がない場合に限り兼務できます（第94条）。")));
});

test("quoted and parenthesized full stops do not create fragmentary paragraphs", () => {
  const source = "本文「これは説明です。条件は別です。」を確認します。（補足。例外。）次を確認します。";
  assert.deepEqual(readerTextParagraphs(source, 1), ["本文「これは説明です。条件は別です。」を確認します。", "（補足。例外。）次を確認します。"]);
  assert.deepEqual(readerTextParagraphs(""), []);
});

test("all fifteen dayservice chapters have topic headings for every original paragraph", () => {
  assert.equal(Object.keys(chapters).length, 15);
  for (const [id, chapter] of Object.entries(chapters)) {
    chapter.paragraphs.forEach((_, index) => assert.ok(dayserviceChapterParagraphHeading(id, index), `${id}/${index}`));
  }
});

test("reader reductions preserve legal numbers, exceptions and unresolved applicability", () => {
  for (const [id, chapter] of Object.entries(chapters)) {
    for (const source of [...chapter.paragraphs, ...chapter.checkpoints]) {
      let withoutPaths = source;
      for (const token of readerReferenceTokens) withoutPaths = withoutPaths.replaceAll(token, "");
      const before = handbookReaderText(withoutPaths);
      const after = handbookReaderText(dayserviceReadableText(id, source));
      // Internal file names are not legal numbers and are translated first.
      for (const number of before.match(/[0-9０-９]+(?:[.．][0-9０-９]+)?/gu) || []) assert.ok(after.includes(number), `${id}: ${number}`);
      for (const qualification of ["未確認", "未照合", "未完了", "場合に限る", "常勤", "専従", "兼務", "準用", "除外", "個別適用"]) {
        if (before.includes(qualification)) assert.ok(after.includes(qualification), `${id}: ${qualification}`);
      }
      const paper = dayserviceChecklistText(after);
      assert.equal(paper.replaceAll("\n", ""), after.replaceAll("\n", ""));
    }
  }
  assert.match(dayserviceReadableText("records", chapters.records.paragraphs[2]), /2年間|未確認|内容は未審査/);
  const unknown = "新しい特例。data/new-reference.json。常時1人以上。未確認です。";
  assert.equal(dayserviceReadableText("operations", unknown), unknown);
});

test("redundant production instructions leave the display without removing the action or caveat", () => {
  const display = dayserviceReadableText("equipment", chapters.equipment.paragraphs[0]);
  assert.doesNotMatch(display, /事業所で使用する書類と現況を対応付けて確認する/u);
  assert.match(display, /図面と現物で照合する/u);
  assert.match(display, /点検記録と使用状況を突き合わせる/u);
  assert.match(dayserviceReadableText("equipment", chapters.equipment.paragraphs[1]), /準用・読替え、指定権者の条例や個別適用は確定しない/u);
});
