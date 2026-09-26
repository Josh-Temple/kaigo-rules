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

test("ordinance detail route generation and lookup are wired to the same scope contract", () => {
  const source = readText("app/rules/[article]/page.tsx");

  assert.match(
    source,
    /generateStaticParams\(\)[\s\S]*filterRecordsForService\(/,
    "static params must use the canonical scope filter",
  );
  assert.match(
    source,
    /const articleNode = findRecordForService\(/,
    "detail lookup must fail closed through the canonical scope helper",
  );
});

test("Care Insurance Act list and counts use the canonical service scope", () => {
  const source = readText("app/law/page.tsx");

  assert.match(
    source,
    /const scopedNodes=filterRecordsForService\(/,
    "law list must build its corpus through the canonical helper",
  );
  assert.match(
    source,
    /const articles=scopedNodes\.filter\(/,
    "law list must render scoped articles rather than the shared corpus",
  );
  assert.match(
    source,
    /<strong>{articles\.length}<\/strong><span>対象条文<\/span>/,
    "article count must use the scoped article collection",
  );
  assert.match(
    source,
    /<strong>{scopedNodes\.length}<\/strong><span>構造ノード<\/span>/,
    "node count must use the scoped node collection",
  );
  assert.doesNotMatch(
    source,
    /meta\.counts\?\.articles_total|meta\.counts\?\.nodes_total/,
    "service-facing counts must not fall back to shared-corpus totals",
  );
});

test("Care Insurance Act detail route generation and lookup are wired to the same scope contract", () => {
  const source = readText("app/law/[article]/page.tsx");

  assert.match(
    source,
    /generateStaticParams\(\)[\s\S]*filterRecordsForService\(/,
    "Care Insurance Act static params must use the canonical scope filter",
  );
  assert.match(
    source,
    /const root=findRecordForService\(/,
    "Care Insurance Act detail lookup must fail closed through the canonical scope helper",
  );
});
