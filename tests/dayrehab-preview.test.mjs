import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(__dirname, "..");
const readJson = (relativePath) =>
  JSON.parse(fs.readFileSync(path.join(root, relativePath), "utf8"));
const readText = (relativePath) =>
  fs.readFileSync(path.join(root, relativePath), "utf8");

test("dayrehab index separates direct Chapter 8 text from Article 119 incorporated scope", () => {
  const index = readJson("data/services/dayrehab/ordinance37-index.generated.json");
  assert.equal(index.service_id, "dayrehab");
  assert.deepEqual(
    index.selectors.resolved_direct_articles,
    ["110", "111", "112", "113", "114", "115", "116", "117", "118", "118-2", "119"],
  );
  assert.equal(index.counts.direct_articles, 11);
  assert.equal(index.counts.incorporated_articles_total, 25);
  assert.equal(index.counts.incorporated_articles_local, 24);
  assert.deepEqual(index.selectors.missing_shared_corpus_articles, ["64"]);
  assert.equal(index.node_ids_by_basis.direct.length, 69);
  assert.ok(index.node_ids_by_basis.incorporated.length > 0);
  assert.equal(index.assurance.legal_text_duplicated, false);
});

test("dayrehab independent audit is PASS without human/current overclaim", () => {
  const audit = readJson("data/dayrehab-ordinance37-independent-audit.json");
  assert.equal(audit.audit_result, "PASS");
  assert.equal(audit.observed.articles, 11);
  assert.equal(audit.observed.nodes, 69);
  assert.equal(audit.safety.human_verified, false);
  assert.equal(audit.safety.verified_current, false);

  const report = readJson("data/verification/layers/ordinance37-dayrehab.json");
  assert.equal(report.content_verification.status, "PASS");
  assert.equal(report.currentness.status, "LIVE_SOURCE_REPARSE_SCHEDULED");
  assert.equal(report.human_review.status, "NOT_REVIEWED");
});

test("dayrehab remains preview while shortstay-life remains unpublished", () => {
  const manifest = readJson("data/services/manifest.json");
  const dayrehab = manifest.services.find((item) => item.service_id === "dayrehab");
  const shortstay = manifest.services.find((item) => item.service_id === "shortstay-life");
  assert.equal(dayrehab.status, "ACTIVE_PREVIEW");
  assert.equal(shortstay.status, "PARTIAL_INGESTION");

  const dayrehabConfig = readJson("data/services/dayrehab.json");
  const shortstayConfig = readJson("data/services/shortstay-life.json");
  assert.equal(dayrehabConfig.routing.future_service_base_enabled, true);
  assert.equal(dayrehabConfig.publication_gate.public_routes_enabled, true);
  assert.equal(dayrehabConfig.publication_gate.independent_verification_complete, true);
  assert.equal(dayrehabConfig.publication_gate.human_review_complete, false);
  assert.deepEqual(dayrehabConfig.verification_layer_ids, ["ordinance37-dayrehab", "rouki25-dayrehab", "remuneration-dayrehab", "fee-guidance-dayrehab"]);
  assert.equal(shortstayConfig.routing.future_service_base_enabled, false);
  assert.equal(shortstayConfig.publication_gate.public_routes_enabled, false);
});

test("dayrehab public pages render shared full text with bounded verification wording", () => {
  const indexPage = readText("app/services/dayrehab/rules/page.tsx");
  const detailPage = readText("app/services/dayrehab/rules/[article]/page.tsx");
  assert.match(indexPage, /直接本文と準用関係を別々に検証しています/);
  assert.match(indexPage, /ordinance37-dayrehab/);
  assert.doesNotMatch(indexPage, /本文全文はまだ公開していません/);
  assert.match(detailPage, /articleNode\.official_text|node\.official_text/);
  assert.match(detailPage, /第119条による準用関係を独立監査済み/);
  assert.match(detailPage, /e-Govで原文を確認/);
});

test("shared Ordinance 37 corpus expanded without changing dayservice surface scope", () => {
  const meta = readJson("data/ordinance37-meta.json");
  assert.equal(meta.counts.articles_total, 67);
  assert.equal(meta.counts.nodes_total, 340);
  const nodes = readJson("data/ordinance37-nodes.json");
  const dayrehabArticle = nodes.find((item) => item.id === "ordinance37.article.110");
  assert.ok(dayrehabArticle);
  assert.equal(dayrehabArticle.applicable_via, null);
});

test("dayrehab Article 119 relation audit covers 25 current targets and fails closed on Article 64 corpus gap", () => {
  const audit = readJson("data/dayrehab-article119-relation-independent-audit.json");
  const relations = readJson("data/services/dayrehab/ordinance37-relations.generated.json");
  assert.equal(audit.audit_result, "PASS");
  assert.equal(audit.coverage.relations_passed, 25);
  assert.equal(relations.length, 25);
  assert.ok(relations.some((row) => row.to === "ordinance37.article.64"));
});

test("dayrehab Rouki 25 route exposes historical-source text without currentness overclaim", () => {
  const data = readJson("data/services/dayrehab/rouki25-historical.generated.json");
  const audit = readJson("data/dayrehab-rouki25-historical-independent-audit.json");
  const page = readText("app/services/dayrehab/notices/page.tsx");
  assert.equal(data.item_count, 9);
  assert.equal(audit.audit_result, "PASS");
  assert.equal(audit.safety.current_integrated_text, false);
  assert.match(page, /これは現行統合本文ではありません/);
  assert.match(page, /現行性はGAP/);
});


test("dayrehab remuneration publishes bounded source-specific inventory and a separate R8 patch", () => {
  const data = readJson("data/services/dayrehab/remuneration-index.json");
  const audit = readJson("data/dayrehab-remuneration-independent-audit.json");
  const report = readJson("data/verification/layers/remuneration-dayrehab.json");
  const page = readText("app/services/dayrehab/remuneration/page.tsx");
  assert.equal(data.service_id, "dayrehab");
  assert.equal(data.items.length, 42);
  assert.equal(data.counts.base_tariff_rate_values, 70);
  assert.equal(data.amendment_patches[0].rates.length, 6);
  assert.deepEqual(data.amendment_patches[0].omitted_sections, ["イ", "ロ", "ハ", "ニ", "ホ"]);
  assert.equal(audit.audit_result, "PASS_BOUNDED_SCOPE_ONLY");
  assert.equal(report.content_verification.status, "PASS_BOUNDED_SCOPE_ONLY");
  assert.equal(report.currentness.status, "GAP");
  assert.equal(report.human_review.status, "NOT_REVIEWED");
  assert.match(page, /これは現行統合本文ではありません/);
  assert.match(page, /自動適用した表は作っていません/);
});

test("dayrehab fee guidance preserves R6 slots, child markers, and currentness gaps", () => {
  const data = readJson("data/services/dayrehab/fee-guidance-index.json");
  const audit = readJson("data/dayrehab-fee-guidance-independent-audit.json");
  const report = readJson("data/verification/layers/fee-guidance-dayrehab.json");
  const page = readText("app/services/dayrehab/remuneration/guidance/page.tsx");
  assert.equal(data.service_id, "dayrehab");
  assert.equal(data.items.length, 33);
  assert.equal(data.items.reduce((n, item) => n + item.children.length, 0), 88);
  assert.equal(data.currentness_ledger[0].status, "GAP");
  assert.equal(audit.audit_result, "PASS_BOUNDED_SCOPE_ONLY");
  assert.equal(report.currentness.status, "GAP");
  assert.equal(report.human_review.status, "NOT_REVIEWED");
  assert.equal(data.policy.combine_source_versions, false);
  assert.equal(data.policy.interpret_r8_omission_as_no_change, false);
  assert.match(page, /これは現行統合本文ではありません/);
  assert.match(page, /第8節の変更有無を示しません/);
});

test("dayrehab fee layer additions do not publish shortstay-life", () => {
  const shortstay = readJson("data/services/shortstay-life.json");
  assert.equal(shortstay.routing.future_service_base_enabled, false);
  assert.equal(shortstay.publication_gate.public_routes_enabled, false);
  assert.doesNotMatch(readText("app/services/page.tsx"), /shortstay-life.*href|href.*shortstay-life/);
});

test("dayrehab landing page exposes the four-layer cross-source search", () => {
  const page = readText("app/services/dayrehab/page.tsx");
  const searchPage = readText("app/services/dayrehab/search/page.tsx");
  assert.match(page, /公開4レイヤーを横断検索/);
  assert.match(page, /\/services\/dayrehab\/search/);
  assert.match(searchPage, /基準省令、基準解釈通知、報酬基準、算定上の留意事項/);
  assert.doesNotMatch(searchPage, /基準省令に限定しています/);
});
