import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";

import {
  filterPublicNotices,
  noticeServiceCount,
  publicNoticePublishedServiceCount,
  publicNoticeRegisteredServiceCount,
  publicNoticeRecords,
  publicNoticeServiceOptions,
} from "../lib/notice-database.ts";

test("notice database is catalog-driven across registered services", () => {
  assert.equal(publicNoticeRegisteredServiceCount, 4);
  assert.deepEqual(
    publicNoticeServiceOptions.map((service) => service.service_id),
    ["dayservice", "homevisit", "dayrehab", "shortstay-life"],
  );
  assert.equal(publicNoticePublishedServiceCount, 2);
  assert.equal(publicNoticeRecords.length, 31);
});

test("published notice records remain separated by service assurance", () => {
  assert.equal(noticeServiceCount("dayservice"), 22);
  assert.equal(noticeServiceCount("dayrehab"), 9);
  assert.equal(filterPublicNotices("dayservice").length, 22);
  assert.equal(filterPublicNotices("dayrehab").length, 9);

  const dayservice = filterPublicNotices("dayservice");
  const dayrehab = filterPublicNotices("dayrehab");

  assert.ok(dayservice.every((row) => row.source_state === "RECONSTRUCTED_CANDIDATE"));
  assert.ok(dayservice.every((row) => row.currentness_state === "HOLD"));
  assert.ok(dayrehab.every((row) => row.source_state === "OFFICIAL_HISTORICAL_HTML"));
  assert.ok(dayrehab.every((row) => row.currentness_state === "GAP"));
  assert.ok(publicNoticeRecords.every((row) => row.human_review_state === "NOT_REVIEWED"));
});

test("registered services without repository notice text fail closed at zero records", () => {
  assert.equal(noticeServiceCount("homevisit"), 0);
  assert.equal(noticeServiceCount("shortstay-life"), 0);
  assert.equal(filterPublicNotices("homevisit").length, 0);
  assert.equal(filterPublicNotices("shortstay-life").length, 0);
  assert.equal(filterPublicNotices("unknown-service").length, 0);

  const homevisit = publicNoticeServiceOptions.find(
    (service) => service.service_id === "homevisit",
  );
  const shortstay = publicNoticeServiceOptions.find(
    (service) => service.service_id === "shortstay-life",
  );

  assert.equal(homevisit?.notice_status, "SCOPE_DEFINED_NOT_RECONSTRUCTED");
  assert.equal(
    shortstay?.notice_status,
    "WORK_CONTROL_ACCEPTED_NOT_REPOSITORY_INGESTED",
  );
  assert.equal(homevisit?.verification_layer_id, undefined);
  assert.equal(shortstay?.verification_layer_id, undefined);
});

test("global notice page exposes the service catalog without inferring applicability", () => {
  const source = fs.readFileSync("app/notices/page.tsx", "utf8");

  assert.match(source, /publicNoticeServiceOptions\.map/);
  assert.match(source, /service catalogに登録されたサービス/);
  assert.match(source, /本文未収録/);
  assert.match(source, /「共通」や他サービスへの適用は自動推定しません/);
  assert.doesNotMatch(source, /公開済み2サービス/);
  assert.doesNotMatch(source, /31項目を同じ保証水準として扱いません/);
  assert.doesNotMatch(source, /service === "dayservice"[\s\S]*VerificationSummary/);
});
