import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";

import {
  filterPublicNotices,
  noticeServiceCount,
  publicNoticeRecords,
} from "../lib/notice-database.ts";

test("shared notice database keeps published service records separate", () => {
  assert.equal(publicNoticeRecords.length, 31);
  assert.equal(noticeServiceCount("dayservice"), 22);
  assert.equal(noticeServiceCount("dayrehab"), 9);
  assert.equal(filterPublicNotices("dayservice").length, 22);
  assert.equal(filterPublicNotices("dayrehab").length, 9);
});

test("notice assurance does not collapse across services", () => {
  const dayservice = filterPublicNotices("dayservice");
  const dayrehab = filterPublicNotices("dayrehab");

  assert.ok(dayservice.every((row) => row.source_state === "RECONSTRUCTED_CANDIDATE"));
  assert.ok(dayservice.every((row) => row.currentness_state === "HOLD"));
  assert.ok(dayrehab.every((row) => row.source_state === "OFFICIAL_HISTORICAL_HTML"));
  assert.ok(dayrehab.every((row) => row.currentness_state === "GAP"));
  assert.ok(publicNoticeRecords.every((row) => row.human_review_state === "NOT_REVIEWED"));
});

test("global notice page exposes all/dayservice/dayrehab filters without inferring common applicability", () => {
  const source = fs.readFileSync("app/notices/page.tsx", "utf8");
  assert.match(source, /すべて/);
  assert.match(source, /service=dayservice/);
  assert.match(source, /service=dayrehab/);
  assert.match(source, /公開済み2サービス/);
  assert.match(source, /「共通」や他サービスへの適用は、明示的なscope根拠が整うまで自動推定しません/);
  assert.match(source, /31項目を同じ保証水準として扱いません/);
});
