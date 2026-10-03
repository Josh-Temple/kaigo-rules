import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

import {
  filterRecordsForService,
  findRecordForService,
  isRecordApplicableToService,
} from "../lib/service-scope.ts";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(__dirname, "..");

const readJson = (relativePath) =>
  JSON.parse(fs.readFileSync(path.join(root, relativePath), "utf8"));
const readText = (relativePath) =>
  fs.readFileSync(path.join(root, relativePath), "utf8");

const ordinanceNodes = readJson("data/ordinance37-nodes.json");
const ordinanceScope = readJson("data/ordinance37-scope.json");
const ordinanceArticles = ordinanceNodes.filter(
  (node) => node.node_type === "article",
);
const dayserviceOrdinanceArticles = filterRecordsForService(
  "dayservice",
  "ordinance37",
  ordinanceArticles,
  (node) => node.id,
);

const careActNodes = readJson("data/care-insurance-act-nodes.json");
const dayserviceCareActNodes = filterRecordsForService(
  "dayservice",
  "care_insurance_act",
  careActNodes,
  (node) => node.id,
);

test("dayservice surface corpus excludes homevisit-only articles and retains shared rules", () => {
  const articleIds = new Set(dayserviceOrdinanceArticles.map((node) => node.id));

  assert.equal(articleIds.has("ordinance37.article.18"), false);
  assert.equal(articleIds.has("ordinance37.article.10"), true);
  assert.equal(articleIds.has("ordinance37.article.100"), true);
});

test("dayrehab surface separates 11 direct articles from all 25 Article 119 targets", () => {
  const dayrehabArticles = filterRecordsForService(
    "dayrehab",
    "ordinance37",
    ordinanceArticles,
    (node) => node.id,
  );
  assert.equal(dayrehabArticles.length, 36);
  assert.equal(dayrehabArticles.some((node) => node.article_num === "110"), true);
  assert.equal(dayrehabArticles.some((node) => node.article_num === "10"), true);
  assert.equal(dayrehabArticles.some((node) => node.article_num === "64"), true);
  assert.equal(
    isRecordApplicableToService("dayservice", "ordinance37", "ordinance37.article.110"),
    false,
  );
});

test("dayservice scoped ordinance count equals explicit direct plus incorporated scope", () => {
  const expected = new Set([
    ...(ordinanceScope.direct_articles || []),
    ...(ordinanceScope.incorporated_articles || []),
  ]);

  assert.equal(dayserviceOrdinanceArticles.length, expected.size);
  assert.ok(
    ordinanceArticles.length > dayserviceOrdinanceArticles.length,
    "shared corpus must remain larger than the dayservice surface corpus",
  );
});

test("dayservice detail lookup fails closed for homevisit-only article and retains shared article", () => {
  const findArticle = (articleNum) =>
    findRecordForService(
      "dayservice",
      "ordinance37",
      ordinanceArticles,
      (node) => node.id,
      (node) => node.article_num === articleNum,
    );

  assert.equal(findArticle("18"), undefined);
  assert.equal(findArticle("10")?.id, "ordinance37.article.10");
});

test("mixed-scope Care Insurance Act Article 8 isolates child nodes symmetrically", () => {
  const dayserviceIds = new Set(dayserviceCareActNodes.map((node) => node.id));

  assert.equal(dayserviceIds.has("careact.article.8"), true);
  assert.equal(dayserviceIds.has("careact.article.8.p.7"), true);
  assert.equal(dayserviceIds.has("careact.article.8.p.2"), false);

  assert.equal(
    isRecordApplicableToService(
      "homevisit",
      "care_insurance_act",
      "careact.article.8.p.2",
    ),
    true,
  );
  assert.equal(
    isRecordApplicableToService(
      "homevisit",
      "care_insurance_act",
      "careact.article.8.p.7",
    ),
    false,
  );
});

test("cross-source search is wired to the scoped ordinance collection before matching", () => {
  const source = readText("app/search/page.tsx");

  assert.match(
    source,
    /const scopedRules = filterRecordsForService\(/,
    "search must build an explicit service-scoped ordinance corpus",
  );
  assert.match(
    source,
    /const articleNodes = scopedRules\.filter\(/,
    "search must match articles from the scoped corpus",
  );
  assert.doesNotMatch(
    source,
    /const articleNodes = rules\.filter\(/,
    "search must not match articles from the unscoped shared corpus",
  );
});

test("global ordinance detail generates the shared corpus and fails closed only when a selected service excludes the article", () => {
  const source = readText("app/rules/[article]/page.tsx");

  assert.match(
    source,
    /generateStaticParams\(\)[\s\S]*node_type === "article"/,
    "global static params must cover the shared article corpus",
  );
  assert.match(
    source,
    /selectedServiceId[\s\S]*!isRecordApplicableToService\(/,
    "service-filtered detail must fail closed outside the selected service scope",
  );
  assert.match(
    source,
    /resolveServiceScope\("ordinance37", articleNode\.id\)/,
    "global detail must expose committed service-scope membership",
  );
});

test("Care Insurance Act list defaults to the shared corpus and filters only when a service is selected", () => {
  const source = readText("app/law/page.tsx");

  assert.match(source, /selectedServiceId[\s\S]*filterRecordsForService/);
  assert.match(source, /: nodes;/);
  assert.match(source, /共有コーパスを全体表示中/);
  assert.match(source, />すべて<\/Link>/);
  assert.match(source, /meta\.counts\?\.articles_total/);
  assert.match(source, /meta\.counts\?\.nodes_total/);
});

test("Care Insurance Act detail generates the shared corpus and fails closed only for an explicit service filter", () => {
  const source = readText("app/law/[article]/page.tsx");

  assert.match(
    source,
    /generateStaticParams\(\)[\s\S]*node_type==="article"/,
    "Care Insurance Act static params must cover the shared article corpus",
  );
  assert.match(
    source,
    /selectedServiceId && !isRecordApplicableToService\(/,
    "service-filtered Care Insurance Act detail must fail closed outside scope",
  );
  assert.match(
    source,
    /selectedServiceId[\s\S]*filterRecordsForService/,
    "child nodes must be filtered only when a service is selected",
  );
});

test("global rules list defaults to the shared corpus and exposes only published service filters", () => {
  const source = readText("app/rules/page.tsx");
  assert.match(source, /selectedServiceId[\s\S]*filterRecordsForService/);
  assert.match(source, /: articles;/);
  assert.match(source, /future_service_base_enabled/);
  assert.match(source, /すべて/);
  assert.match(source, /公開中の通所介護と通所リハビリテーション/);
});
