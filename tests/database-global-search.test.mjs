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
