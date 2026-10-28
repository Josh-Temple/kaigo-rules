import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import { dayserviceChapterParagraphHeading, dayserviceReadableText, dayserviceRoleParagraphHeading } from "../lib/handbook/dayservice-reader-editorial.ts";

const data = JSON.parse(fs.readFileSync("data/handbook-content.json", "utf8"));
const renderer = fs.readFileSync("components/service-handbook.tsx", "utf8");
const chapters = data.services.dayservice.chapters;

test("dayservice chapter text is readable without exposing internal JSON paths or scope labels", () => {
  const ids = ["staffing", "equipment", "operations", "remuneration", "additions", "deductions"];
  for (const id of ids) {
    const content = [...chapters[id].paragraphs, ...chapters[id].checkpoints]
      .map(text => dayserviceReadableText(id, text)).join("\n");
    assert.doesNotMatch(content, /data\/[A-Za-z0-9_./-]+\.json|\bscope\b|収載省令37号/u, id);
    assert.ok(content.length > 100, id);
  }
  assert.match(dayserviceReadableText("equipment", chapters.equipment.paragraphs[1]), /準用・読替え、指定権者の条例や個別適用は確定しない/u);
  assert.match(dayserviceReadableText("remuneration", chapters.remuneration.paragraphs[0]), /算定の可否・単位数・現行性を確認できたことにはなりません/u);
  assert.match(dayserviceReadableText("additions", chapters.additions.paragraphs[0]), /算定要件を確定することはできません/u);
  assert.match(dayserviceReadableText("deductions", chapters.deductions.paragraphs[0]), /この事業所への減算の適用を示しません/u);
});

test("five statutory staffing roles have descriptive headings but keep their complete source and review status", () => {
  const roles = chapters.staffing.role_sections;
  assert.deepEqual(roles.map(r => r.title), ["生活相談員", "看護職員", "介護職員", "機能訓練指導員", "管理者"]);
  for (const role of roles) {
    const description = role.requirements[0].description;
    const paragraphs = description.split("\n").filter(Boolean);
    assert.ok(paragraphs.length >= 3, role.id);
    for (let index = 0; index < paragraphs.length; index++) {
      assert.ok(dayserviceRoleParagraphHeading(role.id, index), `${role.id} ${index}`);
    }
    for (const req of role.requirements) {
      assert.equal(req.verification_state, "EVIDENCE_GAP");
      assert.ok(req.applicability.length > 0 && req.practical_checks.length > 0);
      assert.ok(req.evidence.length > 0);
    }
  }
  assert.match(roles.find(r => r.id === "care-worker").requirements[0].description, /15人以下|15人を超える/u);
  assert.match(roles.find(r => r.id === "manager").requirements[0].description, /全国一律の法定勤務時間ではありません/u);
  assert.match(roles.find(r => r.id === "functional-training").requirements[0].description, /横浜市条例第91条第8項/u);
});

test("new heading structure is wired into actual reader and paper checklist", () => {
  for (const chapter of ["equipment", "operations", "remuneration", "additions", "deductions"]) {
    assert.ok(dayserviceChapterParagraphHeading(chapter, 0), chapter);
  }
  assert.match(renderer, /dayserviceRoleParagraphHeading\(role\.id, paragraphIndex\)/);
  assert.match(renderer, /dayserviceChapterParagraphHeading\(chapter\.section_id, index\)/);
  assert.match(renderer, /dayserviceReadableText\(chapter\.section_id, paragraph\)/);
  assert.match(renderer, /chapter\.checkpoints\.map\(item => dayserviceReadableText\(chapter\.section_id, item\)\)/);
  assert.match(renderer, /requirement\.verification_state === "EVIDENCE_GAP"/);
  assert.match(renderer, /splitDayserviceRegionalText\(copy, requirement\.authority_segments, requirement\.evidence\)/);
  assert.equal(Object.keys(data.services).length, 39);
  assert.equal(Object.values(data.services).reduce((sum, service) => sum + Object.keys(service.chapters).length, 0), 585);
});

test("unknown and changed source phrases are not silently removed", () => {
  const source = "原文には特例・適用条件があります。data/private/internal.json は出典候補で、現行性は未確認です。";
  for (const chapter of ["staffing", "equipment", "operations", "remuneration", "additions", "deductions"]) {
    assert.equal(dayserviceReadableText(chapter, source), source, chapter);
  }
  assert.equal(dayserviceReadableText("staffing", "未確認：専従・兼務の条件を確認する"), "未確認：専従・兼務の条件を確認する");
});
