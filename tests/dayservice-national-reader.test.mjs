import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { createHash } from "node:crypto";
import { dayserviceChapterGroups, dayserviceChapterIntros, dayserviceStaffingTopics, dayserviceQa, dayserviceQaIndex, nationalSourceUrl, numberedNoticePart, readerExcerpt } from "../lib/handbook/dayservice-national-reader.ts";
import { readerTextParagraphs } from "../lib/handbook/dayservice-reader-editorial.ts";

const read = path => JSON.parse(readFileSync(path, "utf8"));
const standards = read("data/ordinance37-nodes.json");
const corpus = read("data/qa-corpus.json");
const topics = Object.values(dayserviceChapterGroups).flatMap(groups => groups.flatMap(group => group.topics));
const references = topics.flatMap(topic => [...topic.basis, ...topic.interpretation || []]);

test("all displayed national references resolve and retain the complete registered source text", () => {
  for (const ref of references) {
    const excerpt = readerExcerpt(ref);
    assert.ok(excerpt.text.length > 0, ref.id);
    assert.ok(excerpt.links.length > 0, ref.id);
    for (const link of excerpt.links) assert.ok(nationalSourceUrl(link.url), link.url);
    if (ref.family === "standard") assert.equal(excerpt.text, standards.find(row => row.id === ref.id).official_text);
    if (ref.family === "fee") assert.equal(excerpt.text, read("data/remuneration-current-text.json").find(row => row.fee_id === ref.id).official_text);
    assert.equal(readerTextParagraphs(excerpt.text).join(""), excerpt.text);
  }
  assert.throws(() => readerExcerpt({ family: "standard", id: "fictional" }), /Missing standard text/);
  assert.throws(() => readerExcerpt({ family: "notice", id: "fictional" }), /Missing notice text/);
});

test("national Q&A keeps every question, answer and unreviewed state, with seven checked original locators", () => {
  const index = dayserviceQaIndex();
  assert.equal(index.length, 7);
  assert.equal(new Set(index.map(item => item.qa.id)).size, 7);
  const expected = ["44", "58", "59", "62", "63", "64", "184"];
  assert.deepEqual(index.map(item => item.qa.number).sort((a,b) => +a-+b), expected);
  for (const item of index) {
    const original = corpus.find(row => row.id === item.qa.id);
    assert.equal(item.qa.question, original.question);
    assert.equal(item.qa.answer, original.answer);
    assert.equal(item.qa.issued_source, original.issued_source);
    assert.equal(item.qa.ingestion_status, "INGESTED_UNREVIEWED");
    assert.ok(nationalSourceUrl(item.qa.originalUrl));
    assert.match(item.qa.originalUrl, /\.pdf#page=\d+$/);
    assert.ok(dayserviceChapterGroups[item.chapterId].some(group => group.topics.some(topic => topic.id === item.topicId && topic.qa.includes(item.qa.id))));
  }
  assert.match(dayserviceQa("qa.mhlw.d9a7f5b49c1ba8a9326e").answer, /問 50 の修正/);
  assert.throws(() => dayserviceQa("qa.mhlw.749ca43b6096d305a35e"), /no scoped original locator/);
  assert.throws(() => dayserviceQa("qa.mhlw.19ff5348270062de7154"), /no scoped original locator/);
});

test("care-worker and qualification passages retain exceptions and are not cut at self-references", () => {
  const staffing = read("data/notice-personnel-current-text-candidates.json").items.find(row => row.notice_id.endsWith("staffing")).candidate_text;
  const part = numberedNoticePart(staffing, "⑤");
  assert.ok(part.includes("以下⑤について同じ"));
  assert.ok(part.includes("常時１名以上"));
  assert.ok(part.includes("利用者の処遇に支障がない場合"));
  assert.ok(part.endsWith("柔軟な配置が可能である。"));
  assert.ok(!part.includes("⑥看護職員"));
  assert.throws(() => numberedNoticePart(staffing, "⑨"), /Missing notice marker/);
  assert.throws(() => numberedNoticePart(staffing, "nonsense"), /Invalid notice marker/);
  const training = references.find(ref => ref.id === "notice.dayservice.personnel.function-training");
  assert.match(readerExcerpt(training).text, /はり師|きゅう師/);
  assert.match(readerExcerpt(training).text, /レクリエーション/);
  assert.match(readerExcerpt({ family: "notice", id: "notice.dayservice.personnel.staffing", part: "⑤" }).caution, /旧規定/);
});

test("five role anchors and national first-category, continuous duty and management conditions stay available", () => {
  assert.deepEqual(dayserviceStaffingTopics.map(topic => topic.id), ["life-counselor", "nurse", "care-worker", "functional-training", "manager"].map(id => `staffing-role-${id}`));
  const shownStandards = references.filter(ref => ref.family === "standard").map(readerExcerpt).map(row => row.text).join("\n");
  for (const condition of ["第一号通所事業", "常時一人以上", "常勤", "他の事業所、施設等の職務"]) assert.ok(shownStandards.includes(condition), condition);
  const readAcross = references.filter(ref => ref.readAcross);
  const source = standards.find(row => row.id === "ordinance37.article.105").official_text;
  assert.ok(source.includes("第五十二条"));
  assert.ok(readAcross.some(ref => ref.id === "ordinance37.article.52"));
  assert.ok(readAcross.every(ref => readerExcerpt(ref).readAcross));
});

test("workflow groups, named fee topics and question index contain no municipal handbook references or generic draft instructions", () => {
  assert.deepEqual(dayserviceChapterGroups.operations.map(group => group.title), ["サービス開始前", "利用開始と計画の作成", "サービス提供時", "事業所の運営"]);
  assert.equal(Object.keys(dayserviceChapterIntros).length, 15);
  for (const groups of Object.values(dayserviceChapterGroups)) {
    const ids = groups.flatMap(group => group.topics.map(topic => topic.id));
    assert.equal(new Set(ids).size, ids.length);
  }
  for (const chapter of ["additions", "deductions"]) for (const group of dayserviceChapterGroups[chapter]) for (const topic of group.topics) assert.ok(!/^(?:note\.|service-provision|treatment-improvement)/.test(topic.title));
  const display = JSON.stringify({ dayserviceChapterGroups, dayserviceChapterIntros, excerpts: references.map(readerExcerpt), qa: dayserviceQaIndex() });
  assert.doesNotMatch(display, /横浜|city\.yokohama|45分|Research Mesh|追記できる|個別質問を特定/);
  assert.ok(dayserviceStaffingTopics.filter(topic => topic.local).every(topic => topic.local.includes("指定権者")));
});

test("official links fail closed on controls, credentials, misleading hosts and nonstandard ports", () => {
  for (const bad of ["javascript:alert(1)", "data:text/html,x", "https://mhlw.go.jp.bad.example/", "https://user@www.mhlw.go.jp/", "https://www.mhlw.go.jp:8443/", " https://www.mhlw.go.jp/", "https://www.mhlw.go.jp/\n", "https://www.mhlw.go.jp\\@evil.example/"]) assert.equal(nationalSourceUrl(bad), null, bad);
  assert.ok(nationalSourceUrl("https://www.mhlw.go.jp/content/12300000/001230308.pdf#page=36"));
  assert.ok(nationalSourceUrl("https://laws.e-gov.go.jp/law/411M50000100037"));
});

test("canonical handbook bytes and all 39 services remain unchanged", () => {
  const raw = readFileSync("data/handbook-content.json");
  assert.equal(createHash("sha256").update(raw).digest("hex"), "47a0ed8e1837e6f76ee0a6230f7bc0dcb0d5f5a62529bdb346ac3f4dc592a2f4");
  assert.equal(Object.keys(JSON.parse(raw).services).length, 39);
});
