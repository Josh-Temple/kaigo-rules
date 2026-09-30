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

test("dayrehab shared index contains exactly the accepted 11-article scope", () => {
  const index = readJson("data/services/dayrehab/ordinance37-index.generated.json");
  assert.equal(index.service_id, "dayrehab");
  assert.deepEqual(
    index.selectors.resolved_direct_articles,
    ["110", "111", "112", "113", "114", "115", "116", "117", "118", "118-2", "119"],
  );
  assert.equal(index.counts.selected_articles, 11);
  assert.equal(index.counts.selected_nodes_total, 69);
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
  assert.deepEqual(dayrehabConfig.verification_layer_ids, ["ordinance37-dayrehab"]);
  assert.equal(shortstayConfig.routing.future_service_base_enabled, false);
  assert.equal(shortstayConfig.publication_gate.public_routes_enabled, false);
});

test("dayrehab public pages render shared full text with bounded verification wording", () => {
  const indexPage = readText("app/services/dayrehab/rules/page.tsx");
  const detailPage = readText("app/services/dayrehab/rules/[article]/page.tsx");
  assert.match(indexPage, /本文・構造は独立再照合済みです/);
  assert.match(indexPage, /ordinance37-dayrehab/);
  assert.doesNotMatch(indexPage, /本文全文はまだ公開していません/);
  assert.match(detailPage, /articleNode\.official_text|node\.official_text/);
  assert.match(detailPage, /人手確認はまだ実施していません/);
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
