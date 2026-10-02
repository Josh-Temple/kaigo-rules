import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";

import {
  databaseSearchTerms,
  matchesDatabaseSearch,
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

test("database hub exposes a service-neutral cross-database search", () => {
  const hub = fs.readFileSync("app/databases/page.tsx", "utf8");
  const search = fs.readFileSync("app/databases/search/page.tsx", "utf8");

  assert.match(hub, /action="\/databases\/search"/);
  assert.match(hub, /全体横断検索/);
  assert.match(search, /care-insurance-act-nodes\.json/);
  assert.match(search, /ordinance37-nodes\.json/);
  assert.match(search, /publicNoticeRecords/);
  assert.match(search, /qa-corpus\.json/);
  assert.doesNotMatch(search, /dayserviceQaServiceCodes/);
  assert.doesNotMatch(search, /remuneration-current-skeleton/);
});
