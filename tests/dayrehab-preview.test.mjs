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

test("dayrehab preview publishes exactly the accepted 11-article index", () => {
  const index = readJson("data/services/dayrehab/standards-index.json");
  assert.equal(index.service_id, "dayrehab");
  assert.deepEqual(
    index.articles.map((item) => item.article_number),
    ["110", "111", "112", "113", "114", "115", "116", "117", "118", "118-2", "119"],
  );
  assert.equal(index.article_count, 11);
  assert.ok(index.articles.every((item) => item.currentness_state === "GAP"));
  assert.ok(index.articles.every((item) => item.human_review_state === "NOT_REVIEWED"));
  assert.ok(index.articles.every((item) => !("full_text" in item)));
});

test("dayrehab is public preview while shortstay-life remains unpublished", () => {
  const manifest = readJson("data/services/manifest.json");
  const dayrehab = manifest.services.find((item) => item.service_id === "dayrehab");
  const shortstay = manifest.services.find((item) => item.service_id === "shortstay-life");
  assert.equal(dayrehab.status, "ACTIVE_PREVIEW");
  assert.equal(shortstay.status, "PARTIAL_INGESTION");

  const dayrehabConfig = readJson("data/services/dayrehab.json");
  const shortstayConfig = readJson("data/services/shortstay-life.json");
  assert.equal(dayrehabConfig.routing.future_service_base_enabled, true);
  assert.equal(dayrehabConfig.publication_gate.public_routes_enabled, true);
  assert.equal(dayrehabConfig.publication_gate.independent_verification_complete, false);
  assert.equal(dayrehabConfig.publication_gate.human_review_complete, false);
  assert.equal(shortstayConfig.routing.future_service_base_enabled, false);
  assert.equal(shortstayConfig.publication_gate.public_routes_enabled, false);
});

test("dayrehab preview has its own verification layer and does not inherit dayservice state", () => {
  const config = readJson("data/services/dayrehab.json");
  const report = readJson("data/verification/layers/ordinance37-dayrehab-preview.json");
  assert.deepEqual(config.verification_layer_ids, ["ordinance37-dayrehab-preview"]);
  assert.equal(report.content_verification.status, "ACCEPTED_WORK_CONTROL_RECEIPT");
  assert.equal(report.currentness.status, "GAP");
  assert.equal(report.human_review.status, "NOT_REVIEWED");
  assert.notEqual(report.content_verification.status, "PASS");
});

test("dayrehab public pages expose limitations and source navigation", () => {
  const indexPage = readText("app/services/dayrehab/rules/page.tsx");
  const detailPage = readText("app/services/dayrehab/rules/[article]/page.tsx");
  assert.match(indexPage, /本文全文はまだ公開していません/);
  assert.match(indexPage, /ordinance37-dayrehab-preview/);
  assert.match(detailPage, /現行性.*GAP/);
  assert.match(detailPage, /e-Gov法令検索/);
});
