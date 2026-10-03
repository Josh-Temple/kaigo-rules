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
  assert.equal(publicNoticeRegisteredServiceCount, 13);
  assert.deepEqual(
    publicNoticeServiceOptions.map((service) => service.service_id),
    [
      "dayservice",
      "homevisit",
      "homebath",
      "homenursing",
      "homerehab",
      "homecaremanagement",
      "dayrehab",
      "shortstay-life",
      "community-dayservice",
      "regular-round",
      "night-homevisit",
      "care-management",
      "preventive-support",
    ],
  );
  assert.equal(publicNoticePublishedServiceCount, 3);
  assert.equal(publicNoticeRecords.length, 66);
});

test("published notice records remain separated by service assurance", () => {
  assert.equal(noticeServiceCount("dayservice"), 22);
  assert.equal(noticeServiceCount("homevisit"), 35);
  assert.equal(noticeServiceCount("dayrehab"), 9);
  assert.equal(filterPublicNotices("dayservice").length, 22);
  assert.equal(filterPublicNotices("homevisit").length, 35);
  assert.equal(filterPublicNotices("dayrehab").length, 9);

  const dayservice = filterPublicNotices("dayservice");
  const homevisit = filterPublicNotices("homevisit");
  const dayrehab = filterPublicNotices("dayrehab");

  assert.ok(dayservice.every((row) => row.source_state === "RECONSTRUCTED_CANDIDATE"));
  assert.ok(dayservice.every((row) => row.currentness_state === "HOLD"));
  assert.ok(homevisit.every((row) => row.source_state === "OFFICIAL_HISTORICAL_HTML"));
  assert.ok(homevisit.every((row) => row.currentness_state === "GAP"));
  assert.ok(homevisit.every((row) => row.verification_layer_id === "rouki25-homevisit"));
  assert.ok(dayrehab.every((row) => row.source_state === "OFFICIAL_HISTORICAL_HTML"));
  assert.ok(dayrehab.every((row) => row.currentness_state === "GAP"));
  assert.ok(publicNoticeRecords.every((row) => row.human_review_state === "NOT_REVIEWED"));
});

test("registered services without repository notice text fail closed at zero records", () => {
  assert.equal(noticeServiceCount("homebath"), 0);
  assert.equal(noticeServiceCount("shortstay-life"), 0);
  assert.equal(filterPublicNotices("homebath").length, 0);
  assert.equal(filterPublicNotices("shortstay-life").length, 0);
  assert.equal(filterPublicNotices("unknown-service").length, 0);

  const homevisit = publicNoticeServiceOptions.find(
    (service) => service.service_id === "homevisit",
  );
  const homebath = publicNoticeServiceOptions.find(
    (service) => service.service_id === "homebath",
  );
  const shortstay = publicNoticeServiceOptions.find(
    (service) => service.service_id === "shortstay-life",
  );

  assert.equal(
    homevisit?.notice_status,
    "HISTORICAL_SOURCE_TEXT_PUBLISHED_CURRENTNESS_GAP",
  );
  assert.equal(homevisit?.record_count, 35);
  assert.equal(homevisit?.verification_layer_id, "rouki25-homevisit");
  assert.equal(homebath?.record_count, 0);
  assert.equal(
    homebath?.notice_status,
    "STAGING_COMPLETE_NOT_REPOSITORY_INGESTED",
  );
  assert.equal(
    shortstay?.notice_status,
    "WORK_CONTROL_ACCEPTED_NOT_REPOSITORY_INGESTED",
  );
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
