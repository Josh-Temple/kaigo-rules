import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { createHash } from "node:crypto";
import { dayserviceChapterGroups, dayserviceChapterIntros, dayserviceStaffingTopics, dayserviceQa, dayserviceQaIndex, nationalSourceUrl, numberedNoticePart, readerExcerpt } from "../lib/handbook/dayservice-national-reader.ts";
import { readerTextParagraphs, sourceTextParagraphs } from "../lib/handbook/dayservice-reader-editorial.ts";
import { basicFeeTable, conciseFeeLocator, dayserviceAppliedText } from "../lib/handbook/dayservice-source-layout.ts";

const read = path => JSON.parse(readFileSync(path, "utf8"));
const standards = read("data/ordinance37-nodes.json");
const corpus = read("data/qa-corpus.json");
const topics = Object.values(dayserviceChapterGroups).flatMap(groups => groups.flatMap(group => group.topics));
const references = topics.flatMap(topic => [...topic.basis, ...topic.interpretation || [], ...topic.criteria || []]);

test("all displayed national references resolve and retain the complete registered source text", () => {
  for (const ref of references) {
    const excerpt = readerExcerpt(ref);
    assert.ok(excerpt.text.length > 0, ref.id);
    assert.ok(excerpt.links.length > 0, ref.id);
    for (const link of excerpt.links) assert.ok(nationalSourceUrl(link.url), link.url);
    if (ref.family === "standard") assert.equal(excerpt.text, standards.find(row => row.id === ref.id).official_text);
    if (ref.family === "fee") assert.equal(excerpt.text, read("data/remuneration-current-text.json").find(row => row.fee_id === ref.id).official_text);
    assert.equal(readerTextParagraphs(excerpt.text).join(""), excerpt.text);
    assert.equal(sourceTextParagraphs(excerpt.text).join(""), excerpt.text);
  }
  assert.throws(() => readerExcerpt({ family: "standard", id: "fictional" }), /Missing standard text/);
  assert.throws(() => readerExcerpt({ family: "notice", id: "fictional" }), /Missing notice text/);
});

test("national Q&A keeps every question, answer and unreviewed state, with checked original locators", () => {
  const index = dayserviceQaIndex();
  assert.equal(index.length, 10);
  assert.equal(new Set(index.map(item => item.qa.id)).size, 10);
  const expected = ["11", "12", "44", "45", "58", "59", "62", "63", "64", "184"];
  assert.deepEqual(index.map(item => item.qa.number).sort((a,b) => +a-+b), expected);
  for (const item of index) {
    const original = corpus.find(row => row.id === item.qa.id);
    assert.equal(item.qa.question, original.question);
    assert.equal(item.qa.answer, original.answer);
    assert.equal(sourceTextParagraphs(item.qa.answer).join(""), original.answer);
    assert.equal(item.qa.topic, original.topic);
    assert.equal(item.qa.issued_source, original.issued_source);
    assert.equal(item.qa.ingestion_status, "INGESTED_UNREVIEWED");
    assert.ok(nationalSourceUrl(item.qa.originalUrl));
    if (["11", "12"].includes(item.qa.number)) {
      assert.match(item.qa.originalUrl, /\.xlsx$/);
      assert.match(item.qa.citationLabel, /Q&A集/);
    } else assert.match(item.qa.originalUrl, /\.pdf#page=\d+$/);
    assert.ok(dayserviceChapterGroups[item.chapterId].some(group => group.topics.some(topic => topic.id === item.topicId && topic.qa.includes(item.qa.id))));
  }
  assert.match(dayserviceQa("qa.mhlw.d9a7f5b49c1ba8a9326e").answer, /問 50 の修正/);
  assert.equal(dayserviceQa("qa.mhlw.98d49d29f427379ec4b3").topic, "入浴介助加算（Ⅱ）");
  assert.throws(() => dayserviceQa("qa.mhlw.749ca43b6096d305a35e"), /no scoped original locator/);
  assert.equal(dayserviceQa("qa.mhlw.19ff5348270062de7154").number, "45");
});

test("a source line wrap inside a Japanese word does not become a separate paragraph", () => {
  const source = "機能訓練指導員は事業所ご\nとに１以上とされている。\n①配置の条件。\n②兼務の条件。\n※参照先の注意。";
  const paragraphs = sourceTextParagraphs(source);
  assert.equal(paragraphs.join(""), source);
  assert.ok(paragraphs[0].includes("事業所ご\nとに"));
  assert.ok(paragraphs.some(paragraph => paragraph.startsWith("①")));
  assert.ok(paragraphs.some(paragraph => paragraph.startsWith("②")));
  assert.ok(paragraphs.some(paragraph => paragraph.startsWith("※")));
});

test("source line wraps keep compound names and circled references together", () => {
  const source = "口 腔\n・栄養スクリーニング加算は、以下\n①\n⑤ をすべて満たす。\n①配置の条件。\n②実施の条件。\n・なお、記録も行う。";
  const paragraphs = sourceTextParagraphs(source);
  assert.equal(paragraphs.join(""), source);
  assert.ok(paragraphs[0].includes("口 腔\n・栄養"));
  assert.ok(paragraphs[0].includes("以下\n①\n⑤ をすべて満たす。"));
  assert.ok(paragraphs.some(paragraph => paragraph.startsWith("①配置")));
  assert.ok(paragraphs.some(paragraph => paragraph.startsWith("②実施")));
  assert.ok(paragraphs.some(paragraph => paragraph.startsWith("・なお")));
  const range = "次の\n①〜⑤を満たす。";
  assert.deepEqual(sourceTextParagraphs(range), [range]);
  const fee = read("data/remuneration-current-text.json").find(row => row.fee_id === "fee.dayservice.note.19");
  assert.ok(fee);
  assert.ok(!sourceTextParagraphs(fee.official_text).some(paragraph => paragraph.startsWith("・栄養")));
  const answer = dayserviceQa("qa.mhlw.98d49d29f427379ec4b3").answer;
  assert.ok(sourceTextParagraphs(answer).some(paragraph => paragraph.includes("以下 ① ⑤ をすべて満たす")));
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

test("readers meet the unit definition before role-specific rules, with precise staffing source pages", () => {
  const ordered = dayserviceChapterGroups.staffing.flatMap(group => group.topics);
  assert.equal(ordered[0].id, "staffing-unit");
  assert.ok(ordered.findIndex(topic => topic.id === "staffing-integrated") > ordered.findIndex(topic => topic.id === "staffing-role-manager"));
  const counselor = readerExcerpt({ family: "notice", id: "notice.dayservice.personnel.staffing", part: "④" });
  const care = readerExcerpt({ family: "notice", id: "notice.dayservice.personnel.staffing", part: "⑤" });
  assert.match(counselor.links[0].url, /0000080875\.pdf#page=46$/);
  assert.match(care.links[0].url, /0000080875\.pdf#page=47$/);
  assert.match(counselor.text, /午前９時から正午、午後１時から午後６時/u);
  assert.match(counselor.text, /正午から午後１時までを除く/u);
  assert.match(counselor.text, /８時間の勤務延時間数分/u);
  assert.match(counselor.caution, /後続改正との照合は未完了/u);
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

test("all ninety fee cells keep the exact source values; incomplete or changed tables fall back to prose", () => {
  const fees = read("data/remuneration-current-text.json");
  for (const id of ["standard", "large1", "large2"]) {
    const source = fees.find(row => row.fee_id === `fee.dayservice.${id}`).official_text;
    const rows = basicFeeTable(source);
    assert.equal(rows.length, 6);
    assert.deepEqual(rows.flatMap(row => row.units), [...source.matchAll(/要介護[1-5] ([0-9,]+)単位/gu)].map(match => match[1]));
    assert.equal(basicFeeTable(source.replace(/要介護3 /u, "要介護6 ")), null);
    assert.equal(basicFeeTable(source + "\nただし、追加条件がある。"), null);
  }
  assert.equal(basicFeeTable("不完全な表"), null);
  assert.equal(conciseFeeLocator("6 通所介護費 / 13 別に厚生労働大臣が定める基準に適合する場合"), "6 通所介護費 / 注13");
});

test("a read-across view preserves conditions and original text while replacing the article 105 references", () => {
  for (const ref of references.filter(row => row.readAcross)) {
    const original = readerExcerpt(ref).text;
    const applied = dayserviceAppliedText(ref.id, original);
    assert.ok(applied, ref.id);
    assert.doesNotMatch(applied, /指定訪問(?:入浴)?介護|訪問介護員等/u);
    assert.equal(readerExcerpt(ref).text, original);
    assert.deepEqual([...applied.matchAll(/[0-9０-９]+/gu)].map(m => m[0]), [...original.matchAll(/[0-9０-９]+/gu)].map(m => m[0]));
  }
  const article8 = standards.find(row => row.id === "ordinance37.article.8").official_text;
  assert.match(dayserviceAppliedText("ordinance37.article.8", article8), /第百条に規定する運営規程/u);
  assert.equal(dayserviceAppliedText("ordinance37.article.119", "未知の準用"), null);
});

test("criteria are complete references to already published national bodies, without changing their review status", () => {
  const nodes = read("data/remuneration-delegated-nodes.json");
  const criteria = references.filter(ref => ref.family === "delegated");
  assert.ok(criteria.some(ref => ref.id === "criteria95.dayservice.16"));
  assert.ok(criteria.some(ref => ref.id === "criteria95.dayservice.14-6"));
  for (const ref of criteria) {
    assert.equal(readerExcerpt(ref).text, nodes.find(row => row.id === ref.id).official_text);
    assert.match(readerExcerpt(ref).caution, /照合は未完了/u);
  }
});

test("reader prompts and Q&A searches cover four priority decisions without altering national source data", () => {
  const roleIds = ["staffing-role-nurse", "staffing-role-care-worker"];
  const feeIds = ["fee-note-13", "fee-note-6"];
  for (const id of [...roleIds, ...feeIds]) {
    const topic = topics.find(item => item.id === id);
    assert.ok(topic, id);
    assert.ok(topic.readerQuestions?.length >= 3, id);
    assert.ok(topic.readerQuestions.every(question => question.endsWith("？")), id);
    assert.ok(topic.qaSearchQuery, id);
    assert.ok(!/横浜|scope|JSON|Research Mesh/u.test(JSON.stringify(topic.readerQuestions)), id);
  }
  assert.ok(topics.find(topic => topic.id === "fee-note-13")?.criteria?.length);
  assert.ok(topics.find(topic => topic.id === "fee-note-6")?.basis?.length);
  assert.ok(topics.find(topic => topic.id === "staffing-role-nurse")?.qa?.length);
});

test("individual training has government source page links for Q&A 55-57, distinct from unreviewed corpus", () => {
  const item = topics.find(topic => topic.id === "fee-note-13");
  assert.deepEqual(item.officialQaFurther.map(row => row.number), ["55", "56", "57"]);
  for (const row of item.officialQaFurther) {
    assert.ok(nationalSourceUrl(row.url));
    assert.match(row.url, /001230308\.pdf#page=3[45]$/);
    assert.ok(row.label);
  }
  assert.deepEqual(topics.find(topic => topic.id === "fee-note-6")?.officialQaFurther?.map(row => row.number), ["56", "57", "58", "59", "5"]);
});

test("reader summaries preserve staffing thresholds and extension non-claim scenarios", () => {
  const byId = id => topics.find(item => item.id === id);
  for (const id of ["staffing-role-life-counselor", "staffing-role-nurse", "staffing-role-care-worker", "staffing-role-functional-training", "staffing-role-manager", "fee-note-13", "fee-note-6"]) {
    const item = byId(id);
    assert.ok(item.readerSummary, id);
    assert.ok(item.readerConditions?.length >= 2, id);
    assert.ok(item.readerExceptions?.length, id);
  }
  assert.match(byId("staffing-role-care-worker").readerConditions.join(""), /15人/);
  assert.match(byId("fee-note-6").readerExceptions.join(""), /宿泊サービス/);
  assert.deepEqual(byId("fee-note-6").officialQaFurther.map(row => row.number), ["56", "57", "58", "59", "5"]);
  assert.ok(byId("fee-note-6").officialQaFurther.every(row => nationalSourceUrl(row.url) && row.explanation));
  assert.match(byId("fee-note-6").officialQaFurther.find(row => row.number === "5").url, /0000093219\.pdf#page=4$/);
  assert.match(byId("fee-note-13").officialQaFurther.find(row=>row.number==="55").explanation, /事前/);
  assert.match(byId("fee-note-13").officialQaFurther.find(row=>row.number==="56").explanation, /外部/);
  assert.match(byId("fee-note-6").officialQaFurther.find(row => row.number === "5").label, /口腔機能向上サービス/);
  assert.match(byId("fee-note-6").officialQaFurther.find(row => row.number === "5").explanation, /延長加算全般を認めるものではありません/);
  assert.match(byId("fee-note-6").readerExceptions.join(""), /限定的な取扱い/);
  assert.match(byId("staffing-role-life-counselor").readerSummary, /勤務延時間数/);
  assert.match(byId("staffing-role-functional-training").readerSummary, /事業所ごとに1人以上/);
  assert.match(byId("staffing-role-manager").readerSummary, /常勤/);
});

test("2026 treatment improvement fee amendment is visibly flagged without overwriting historical sources", () => {
  const item = topics.find(row => row.id === "fee-treatment-improvement");
  assert.ok(item, "treatment improvement topic exists");
  assert.ok(item.basis.some(ref => ref.id === "fee.dayservice.treatment-improvement"));
  assert.match(item.regulatoryUpdate?.message || "", /令和8年厚生労働省告示第87号/);
  assert.match(item.regulatoryUpdate?.message || "", /請求・届出/);
  assert.equal(item.regulatoryUpdate?.officialUrl, "https://www.mhlw.go.jp/content/12404000/001675895.pdf#page=7");
  assert.ok(nationalSourceUrl(item.regulatoryUpdate.officialUrl), "official link passes allowlist");
  assert.match(item.regulatoryUpdate.message, /4月・5月と6月以降/);
  assert.deepEqual(item.regulatoryUpdate.relatedDocuments?.map(row => row.url), [
    "https://www.mhlw.go.jp/content/12404000/001675724.pdf#page=3",
    "https://www.mhlw.go.jp/content/12404000/001675724.pdf#page=18",
    "https://www.mhlw.go.jp/content/12404000/001675711.pdf",
    "https://www.mhlw.go.jp/stf/seisakunitsuite/bunya/0000188411_00073.html",
  ]);
  assert.ok(item.regulatoryUpdate.relatedDocuments.every(row => row.label && nationalSourceUrl(row.url)));
  assert.equal(topics.find(row => row.id === "fee-note-6")?.regulatoryUpdate, undefined);
});
