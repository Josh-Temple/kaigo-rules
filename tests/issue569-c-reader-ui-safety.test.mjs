import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import { readerEvidenceLocator, safeHandbookEvidenceUrl, requirementCopy, separateHandbookParagraphs, splitDayserviceRegionalText } from "../lib/handbook/reader-content.ts";

const renderer = fs.readFileSync("components/service-handbook.tsx", "utf8");
const css = fs.readFileSync("app/globals.css", "utf8");
const data = JSON.parse(fs.readFileSync("data/handbook-content.json", "utf8"));

test("source links fail closed on script, data, credentials, controls and relative URLs", () => {
  for (const bad of [
    undefined, "", "javascript:alert(1)", "data:text/html,test",
    "//evil.example/s", "/relative", "https://user:pass@www.mhlw.go.jp/",
    "https://www.mhlw.go.jp/\n.evil.example", " https://www.mhlw.go.jp/",
  ]) assert.equal(safeHandbookEvidenceUrl(bad), null, String(bad));
  assert.equal(safeHandbookEvidenceUrl("https://www.mhlw.go.jp/"), "https://www.mhlw.go.jp/");
  assert.equal(safeHandbookEvidenceUrl("http://www.mhlw.go.jp/source"), "http://www.mhlw.go.jp/source");
  assert.match(renderer, /safeHandbookEvidenceUrl\(evidence\.url\)/u);
  assert.doesNotMatch(renderer, /href=\{evidence\.url\}/u);
});

test("only a whole technical source locator is translated, not legal conditions", () => {
  assert.equal(readerEvidenceLocator("data/ordinance37-nodes.json"), "原典の該当箇所を確認中");
  assert.equal(readerEvidenceLocator("docs/review.md"), "原典の該当箇所を確認中");
  for (const original of [
    "第93条第1項", "第93条第1項。data/ordinance37-nodes.json との照合が必要",
    "2026年の改正附則の適用を確認中", "第94条（管理者）",
  ]) assert.equal(readerEvidenceLocator(original), original);
  assert.match(renderer, /readerEvidenceLocator\(evidence\.locator\)/u);
});

test("reader display retains legal uncertainty, source category and applicability", () => {
  assert.match(renderer, /requirement\.verification_state === "EVIDENCE_GAP"/u);
  assert.match(renderer, /requirement\.applicability/u);
  assert.match(renderer, /requirement\.evidence/u);
  assert.match(renderer, /splitDayserviceRegionalText\(copy, requirement\.authority_segments, requirement\.evidence\)/u);
  const notice = "【Research Mesh隔離候補・法令適合未審査】要件の適用は現行の通知と附則の確認を要する。";
  assert.equal(requirementCopy(notice), "要件の適用は現行の通知と附則の確認を要する。");
  const mixed = "出典候補：data/ordinance37-nodes.json。兼務条件は原典確認が必要。";
  assert.deepEqual(separateHandbookParagraphs([mixed]).reader, [mixed]);
  const unsourced = splitDayserviceRegionalText("国・自治体の未確認事項。");
  assert.equal(unsourced.classified, false);
  assert.equal(unsourced.segments.map(s => s.text).join(""), "国・自治体の未確認事項。");
  assert.equal(data.services.dayservice.chapters.staffing.role_sections.length, 5);
  for (const role of data.services.dayservice.chapters.staffing.role_sections) {
    for (const item of role.requirements) {
      assert.equal(item.verification_state, "EVIDENCE_GAP");
    }
  }
});

test("staffing roles offer a keyboard-accessible return target without modifying original anchors", () => {
  assert.match(renderer, /id=\{\x60\$\{anchor\}-navigation\x60\}/u);
  assert.match(renderer, /href=\{\x60#\$\{anchor\}-navigation\x60\}/u);
  assert.match(renderer, /職種一覧に戻る/u);
  assert.match(renderer, /id=\{\x60\$\{anchor\}-\$\{role\.id\}\x60\}/u);
  assert.match(css, /handbook-role-return a:focus-visible/u);
  assert.match(css, /@media\(max-width:390px\)/u);
  assert.match(css, /handbook-role-return a\{[^}]*min-height:48px/u);
  assert.match(css, /@media print\{\.handbook-role-return\{display:none\}/u);
});

test("five staffing roles and 39 services / 585 chapters are unchanged", () => {
  const services = Object.keys(data.services);
  assert.equal(services.length, 39);
  assert.equal(Object.values(data.services).reduce((n, s) => n + Object.keys(s.chapters).length, 0), 585);
  assert.deepEqual(data.services.dayservice.chapters.staffing.role_sections.map(r => r.title),
    ["生活相談員", "看護職員", "介護職員", "機能訓練指導員", "管理者"]);
});

test("Muse reader-only links keep nursing legal uncertainty and an exact handbook return", () => {
  const qpage = fs.readFileSync("app/questions/[slug]/page.tsx", "utf8");
  assert.match(renderer, /href="\/questions\/nurse-staffing"/u);
  assert.match(renderer, /連携・兼務の適用条件は、国の解釈通知・Q&Aの現行内容を別途確認してください/u);
  assert.match(qpage, /slug === "nurse-staffing"/u);
  assert.match(qpage, /href="\/services\/dayservice#staffing"/u);
  assert.match(renderer, /「サ責」は「サービス提供責任者」の略称です/u);
  const homevisit = data.services.homevisit.chapters.staffing.paragraphs.join("\n");
  assert.match(homevisit, /利用者50人ごとに1人以上とできます/u);
  assert.doesNotMatch(homevisit, /利用者50人又はその端数を増すごとに1人以上とすることができます/u);
});
