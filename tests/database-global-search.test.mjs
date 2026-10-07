import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import { publicNoticeRecords } from "../lib/notice-database.ts";

import {
  databaseSearchExcerpt,
  databaseSearchTerms,
  matchesDatabaseSearch,
  rankDatabaseSearch,
  scoreDatabaseSearch,
} from "../lib/database-search.ts";

test("database-wide search expands key service synonyms", () => {
  assert.equal(matchesDatabaseSearch("業務継続計画の策定等", "BCP"), true);
  assert.equal(matchesDatabaseSearch("通所介護の基本方針", "デイサービス"), true);
  assert.equal(
    matchesDatabaseSearch("通所リハビリテーション費", "デイケア"),
    true,
  );
});

test("database-wide search requires every query term", () => {
  assert.equal(matchesDatabaseSearch("通所介護 認知症加算", "通所介護 認知症"), true);
  assert.equal(matchesDatabaseSearch("通所介護 認知症加算", "通所介護 BCP"), false);
  assert.equal(databaseSearchTerms("   ").length, 0);
});


test("database-wide ranking prefers title matches over body-only matches", () => {
  const records = [
    {
      id: "body-only",
      title: "別の見出し",
      body: "業務継続計画について定める。",
    },
    {
      id: "title-match",
      title: "業務継続計画",
      body: "本文",
    },
  ];

  const ranked = rankDatabaseSearch(records, "BCP", (record) => [
    { value: record.title, weight: 8 },
    { value: record.body, weight: 1 },
  ]);

  assert.deepEqual(ranked.map((record) => record.id), [
    "title-match",
    "body-only",
  ]);
});

test("database-wide ranking keeps AND semantics across separate fields", () => {
  const records = [
    {
      id: "complete",
      title: "看護職員",
      service: "通所介護",
      body: "配置基準",
    },
    {
      id: "partial",
      title: "看護職員",
      service: "訪問看護",
      body: "配置基準",
    },
  ];

  const ranked = rankDatabaseSearch(
    records,
    "デイサービス 看護師",
    (record) => [
      { value: record.title, weight: 8 },
      { value: record.service, weight: 4 },
      { value: record.body, weight: 1 },
    ],
  );

  assert.deepEqual(ranked.map((record) => record.id), ["complete"]);
});

test("database-wide score rewards exact high-value field matches", () => {
  const titleScore = scoreDatabaseSearch(
    [{ value: "認知症", weight: 8 }],
    "認知症",
  );
  const bodyScore = scoreDatabaseSearch(
    [{ value: "認知症の利用者に対する支援", weight: 1 }],
    "認知症",
  );

  assert.ok(titleScore > bodyScore);
});


test("database-wide snippets show matched context instead of only the beginning", () => {
  const text =
    "前置き".repeat(80) +
    "業務継続計画について、研修及び訓練を定期的に実施する。" +
    "後続".repeat(80);

  const snippet = databaseSearchExcerpt(text, "BCP", 120);

  assert.match(snippet, /業務継続計画/);
  assert.ok(snippet.startsWith("…"));
  assert.ok(snippet.endsWith("…"));
});

test("database-wide snippets honor synonym matches", () => {
  const text =
    "説明".repeat(60) +
    "看護職員は利用者の健康状態を確認する。" +
    "補足".repeat(60);

  assert.match(databaseSearchExcerpt(text, "看護師", 100), /看護職員/);
});

test("database-wide notice corpus includes independently published homebath history", () => {
  const homebath = publicNoticeRecords.filter(
    (record) => record.service_id === "homebath",
  );
  assert.equal(homebath.length, 13);
  assert.ok(
    homebath.every(
      (record) =>
        record.source_state === "OFFICIAL_HISTORICAL_HTML" &&
        record.currentness_state === "GAP",
    ),
  );
});

test("database-wide notice corpus includes the independently published next service wave", () => {
  const expected = new Map([
    ["homenursing", 12],
    ["homerehab", 7],
    ["homecaremanagement", 9],
    ["shortstay-life", 34],
  ]);

  for (const [serviceId, count] of expected) {
    const records = publicNoticeRecords.filter(
      (record) => record.service_id === serviceId,
    );
    assert.equal(records.length, count);
    assert.ok(
      records.every(
        (record) =>
          record.source_state === "OFFICIAL_HISTORICAL_HTML" &&
          record.currentness_state === "GAP" &&
          record.human_review_state === "NOT_REVIEWED",
      ),
    );
  }
});

test("database hub exposes a service-neutral cross-database search", () => {
  const hub = fs.readFileSync("app/databases/page.tsx", "utf8");
  const search = fs.readFileSync("app/databases/search/page.tsx", "utf8");

  assert.match(hub, /action="\/databases\/search"/);
  assert.match(hub, /全体横断検索/);
  assert.match(search, /care-insurance-act-nodes\.json/);
  assert.match(search, /ordinance37-nodes\.json/);
  assert.match(search, /publicNoticeRecords/);
  assert.match(search, /\/notices\?service=/);
  assert.match(search, /qa-corpus\.json/);
  assert.match(search, /rankDatabaseSearch/);
  assert.match(search, /databaseSearchExcerpt/);
  assert.match(search, /weight: 8/);
  assert.doesNotMatch(search, /dayserviceQaServiceCodes/);
  assert.doesNotMatch(search, /remuneration-current-skeleton/);
});

test("legacy cross-source search keeps its day-service scope contract", () => {
  const legacy = fs.readFileSync("app/search/page.tsx", "utf8");

  assert.match(legacy, /dayserviceQaServiceCodes/);
  assert.match(legacy, /getDefaultService/);
  assert.match(legacy, /filterRecordsForService/);
});


test("public database search ranks primary-source text above metadata-only matches", () => {
  const records = [
    { id: "metadata", body: "", metadata: "業務継続計画" },
    { id: "body", body: "業務継続計画を策定する。", metadata: "" },
  ];
  const ranked = rankDatabaseSearch(records, "BCP", (record) => [
    { value: record.body, weight: 10 },
    { value: record.metadata, weight: 2 },
  ]);
  assert.deepEqual(ranked.map((record) => record.id), ["body", "metadata"]);
});

test("public database search groups service filters and treats no-match as a partial public state", () => {
  const search = fs.readFileSync("app/databases/search/page.tsx", "utf8");

  assert.match(search, /publicServiceNavigationGroups/);
  assert.match(search, /一次資料の本文・質問文への直接一致を優先/);
  assert.match(search, /未確認の制度間関係や内部の確認スコアは順位付けに使いません/);
  assert.match(search, /現在公開している範囲では一致する資料が見つかりませんでした/);
  assert.match(search, /資料そのものが存在しないことを意味しません/);
  assert.match(search, /実務ガイドから探す/);
  assert.doesNotMatch(search, /READY_FOR_PUBLICATION_REVIEW|blocking_reasons/);
});


test("multi-source search is gated by the shared publication policy", () => {
  const search = fs.readFileSync("app/databases/search/page.tsx", "utf8");

  assert.match(search, /unit-price-dayservice\.json/);
  assert.match(search, /publicSourceFamiliesForService/);
  assert.match(search, /UNIT_PRICE_SOURCE_FAMILY/);
  assert.match(search, /一単位単価・地域区分/);
  assert.match(search, /公開条件を満たした現行資料/);
  assert.match(search, /厚生労働省の告示原文/);
  assert.match(search, /見つからない資料を知らせる/);
  assert.doesNotMatch(
    search,
    /READY_FOR_PUBLICATION_REVIEW|blocking_reasons|BLOCKED_CURRENTNESS/,
  );
});

test("public source navigation delegates exposure and metrics to the shared route policy", () => {
  const source = fs.readFileSync("lib/public-source-navigation.ts", "utf8");

  assert.match(source, /isProgressiveRouteCell/);
  assert.match(
    source,
    /isProgressiveRouteCell\(serviceId, definition\.source_family\)/,
  );
  assert.match(source, /GOVERNING_STANDARDS_SOURCE_FAMILY/);
  assert.match(source, /UNIT_PRICE_SOURCE_FAMILY/);
  assert.match(source, /runtime_supported_source_families/);
  assert.match(source, /cross_source_searchable_cells/);
  assert.match(source, /service_pages_with_2plus_published_source_families/);
  assert.doesNotMatch(
    source,
    /READY_FOR_PUBLICATION_REVIEW|blocking_reasons|promotion_applied/,
  );
});


test("public database search offers practical-topic discovery without exposing internal source-family codes", () => {
  const search = fs.readFileSync("app/databases/search/page.tsx", "utf8");

  assert.match(search, /practicalTopicSearches/);
  assert.match(search, /実務テーマから探す/);
  for (const label of ["人員基準", "設備基準", "運営基準", "報酬・算定", "地域区分・単価", "指定", "更新・届出"]) {
    assert.match(search, new RegExp(label));
  }
  assert.match(search, /filterHref\(item\.query, selectedService\?\.service_id\)/);
  assert.doesNotMatch(
    search,
    /READY_FOR_PUBLICATION_REVIEW|BLOCKED_CURRENTNESS|blocking_reasons/,
  );
});

test("public database search renders only verified related-primary-source navigation", () => {
  const search = fs.readFileSync("app/databases/search/page.tsx", "utf8");
  const relations = fs.readFileSync("lib/verified-related-sources.ts", "utf8");

  assert.match(search, /verifiedRelatedPrimarySources/);
  assert.match(search, /関連する一次資料/);
  assert.match(relations, /check\.result === "PASS"/);
  assert.match(relations, /basis_independent_verification === "PASS"/);
  assert.doesNotMatch(search, /SEMANTIC_TEXT_CHECK_REQUIRED|HUMAN_SEMANTIC_REVIEW_REQUIRED/);
});


test("public database search offers a bounded contextual handoff to Kaigo Ops", () => {
  const search = fs.readFileSync("app/databases/search/page.tsx", "utf8");

  assert.match(search, /制度上の要件を確認した後、業務の見直しへ/);
  assert.match(
    search,
    /https:\/\/ops-site-pi\.vercel\.app\/issues\/information-search/,
  );
  assert.match(
    search,
    /https:\/\/ops-site-pi\.vercel\.app\/issues\/documentation/,
  );
  assert.match(search, /介護業務改善では制度適合を確定しません/);
  assert.doesNotMatch(
    search,
    /ops-site-pi\.vercel\.app\/issues\/(training-handover|communication-collaboration|productivity-utilization)/,
  );
});
