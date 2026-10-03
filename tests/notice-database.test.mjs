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
  assert.equal(publicNoticePublishedServiceCount, 8);
  assert.equal(publicNoticeRecords.length, 141);
});

test("published notice records remain separated by service assurance", () => {
  assert.equal(noticeServiceCount("dayservice"), 22);
  assert.equal(noticeServiceCount("homevisit"), 35);
  assert.equal(noticeServiceCount("homebath"), 13);
  assert.equal(noticeServiceCount("homenursing"), 12);
  assert.equal(noticeServiceCount("homerehab"), 7);
  assert.equal(noticeServiceCount("homecaremanagement"), 9);
  assert.equal(noticeServiceCount("dayrehab"), 9);
  assert.equal(noticeServiceCount("shortstay-life"), 34);
  assert.equal(filterPublicNotices("dayservice").length, 22);
  assert.equal(filterPublicNotices("homevisit").length, 35);
  assert.equal(filterPublicNotices("homebath").length, 13);
  assert.equal(filterPublicNotices("homenursing").length, 12);
  assert.equal(filterPublicNotices("homerehab").length, 7);
  assert.equal(filterPublicNotices("homecaremanagement").length, 9);
  assert.equal(filterPublicNotices("dayrehab").length, 9);
  assert.equal(filterPublicNotices("shortstay-life").length, 34);

  const dayservice = filterPublicNotices("dayservice");
  const homevisit = filterPublicNotices("homevisit");
  const homebath = filterPublicNotices("homebath");
  const homenursing = filterPublicNotices("homenursing");
  const homerehab = filterPublicNotices("homerehab");
  const homecaremanagement = filterPublicNotices("homecaremanagement");
  const shortstay = filterPublicNotices("shortstay-life");
  const dayrehab = filterPublicNotices("dayrehab");

  assert.ok(dayservice.every((row) => row.source_state === "RECONSTRUCTED_CANDIDATE"));
  assert.ok(dayservice.every((row) => row.currentness_state === "HOLD"));
  assert.ok(homevisit.every((row) => row.source_state === "OFFICIAL_HISTORICAL_HTML"));
  assert.ok(homevisit.every((row) => row.currentness_state === "GAP"));
  assert.ok(homevisit.every((row) => row.verification_layer_id === "rouki25-homevisit"));
  assert.ok(homebath.every((row) => row.source_state === "OFFICIAL_HISTORICAL_HTML"));
  assert.ok(homebath.every((row) => row.currentness_state === "GAP"));
  assert.ok(homebath.every((row) => row.verification_layer_id === "rouki25-homebath"));
  for (const [rows, layerId] of [
    [homenursing, "rouki25-homenursing"],
    [homerehab, "rouki25-homerehab"],
    [homecaremanagement, "rouki25-homecaremanagement"],
    [shortstay, "rouki25-shortstay-life"],
  ]) {
    assert.ok(rows.every((row) => row.source_state === "OFFICIAL_HISTORICAL_HTML"));
    assert.ok(rows.every((row) => row.currentness_state === "GAP"));
    assert.ok(rows.every((row) => row.verification_layer_id === layerId));
  }
  assert.ok(dayrehab.every((row) => row.source_state === "OFFICIAL_HISTORICAL_HTML"));
  assert.ok(dayrehab.every((row) => row.currentness_state === "GAP"));
  assert.ok(publicNoticeRecords.every((row) => row.human_review_state === "NOT_REVIEWED"));
});

test("published historical notice services expose records while service roots stay separate", () => {
  const expected = new Map([
    ["homevisit", [35, "rouki25-homevisit"]],
    ["homebath", [13, "rouki25-homebath"]],
    ["homenursing", [12, "rouki25-homenursing"]],
    ["homerehab", [7, "rouki25-homerehab"]],
    ["homecaremanagement", [9, "rouki25-homecaremanagement"]],
    ["dayrehab", [9, "rouki25-dayrehab"]],
    ["shortstay-life", [34, "rouki25-shortstay-life"]],
  ]);

  for (const [serviceId, [count, layerId]] of expected) {
    const service = publicNoticeServiceOptions.find(
      (candidate) => candidate.service_id === serviceId,
    );
    assert.equal(service?.record_count, count);
    assert.equal(
      service?.notice_status,
      "HISTORICAL_SOURCE_TEXT_PUBLISHED_CURRENTNESS_GAP",
    );
    assert.equal(service?.verification_layer_id, layerId);
  }

  assert.equal(filterPublicNotices("unknown-service").length, 0);
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
