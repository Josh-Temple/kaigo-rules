import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import { DAY_SERVICE_STAFFING, DAY_SERVICE_STAFFING_SHARED, separateHandbookParagraphs } from "../lib/handbook/reader-content.ts";

const handbook = JSON.parse(fs.readFileSync("data/handbook-content.json", "utf8"));

test("dayservice reader shows five professions with one-to-one page anchors and original article references", () => {
  assert.deepEqual(DAY_SERVICE_STAFFING.map(role => role.heading), [
    "生活相談員", "看護職員", "介護職員", "機能訓練指導員", "管理者",
  ]);
  assert.equal(new Set(DAY_SERVICE_STAFFING.map(role => role.id)).size, 5);
  assert.ok(DAY_SERVICE_STAFFING.every(role => role.points.length > 0 && role.reference.startsWith("基準省令第")));
  const original = handbook.services.dayservice.chapters.staffing.paragraphs.join("\n");
  for (const token of ["生活相談員", "看護職員", "介護職員", "機能訓練指導員", "管理者", "1以上", "15人まで", "第93条", "第94条"]) {
    assert.ok(original.includes(token), "reader explanation has no original anchor: " + token);
  }
  assert.equal(DAY_SERVICE_STAFFING[1].reference, "基準省令第93条第1項第2号");
  assert.match(DAY_SERVICE_STAFFING[2].points.join(" "), /常時1人以上/);
  assert.match(DAY_SERVICE_STAFFING[2].points.join(" "), /15人を超えた人数÷5/);
  assert.equal(DAY_SERVICE_STAFFING_SHARED.length, 2);
  assert.match(DAY_SERVICE_STAFFING_SHARED[0].text, /生活相談員または介護職員/);
  assert.match(DAY_SERVICE_STAFFING_SHARED[1].text, /第一号通所事業/);
});

test("internal-source notes are separated only for recognizable repository references and never dropped", () => {
  const original = [
    "設備を確認する。根拠候補は収載済みの data/services/homebath/ordinance37-scope.json と関連する原典索引である。",
    "数を確認する。出典候補：e-Gov法令検索。法令の版は未確認。",
    "出典候補：e-Gov法令検索。本文は未確認。",
    "指定事業者は必要な職員を配置します。",
    "例示ファイル data/services/a.json を勤務記録と照合します。",
  ];
  const result = separateHandbookParagraphs(original);
  assert.deepEqual(result.reader, [
    "設備を確認する。", "数を確認する。", "指定事業者は必要な職員を配置します。",
    "例示ファイル data/services/a.json を勤務記録と照合します。",
  ]);
  assert.equal(result.editorial.length, 3);
  assert.ok(result.editorial[0].startsWith("根拠候補は収載済みの"));
  for (const source of original) {
    assert.ok(result.reader.includes(source) || result.editorial.includes(source) ||
      result.reader.some(head => result.editorial.some(tail => head + tail === source)),
    "original paragraph lost: " + source);
  }
});

test("reader rendering is guarded, internal-source details are optional, and all original data remains authoritative", () => {
  const source = fs.readFileSync("components/service-handbook.tsx", "utf8");
  assert.match(source, /service\.service_id === "dayservice" && chapter\.section_id === "staffing"/);
  assert.match(source, /DayserviceStaffingReader full=\{full\}/);
  assert.match(source, /<h4>\{role\.heading\}<\/h4>/);
  assert.match(source, /<details className="handbook-editorial-details">/);
  assert.match(source, /separateHandbookParagraphs\(chapter\.paragraphs\)\.editorial/);
  assert.match(source, /<summary>根拠条文と確認状況<\/summary>/);
  assert.doesNotMatch(source, /className="handbook-role-warning"/);
  assert.deepEqual(Object.keys(handbook.services).length, 39);
  assert.equal(Object.values(handbook.services).reduce((n, s) => n + Object.keys(s.chapters).length, 0), 585);
  assert.ok(!handbook.services.dayservice.chapters.staffing.role_sections, "unreviewed #553 roles must not be silently imported");
});
