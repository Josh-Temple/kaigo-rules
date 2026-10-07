import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";

import {
  UNIT_PRICE_SOURCE_FAMILY,
  getProgressivePublicationTrust,
  getProgressiveSourceRecords,
  projectProgressiveRecords,
} from "../lib/publication-policy.ts";
import {
  listPublicUnitPriceServices,
  publicUnitPriceRows,
  searchPublicUnitPrices,
  unitPriceHref,
} from "../lib/unit-price-discovery.ts";

test("unit price discovery lists exactly the presently gated public services", () => {
  const services = listPublicUnitPriceServices();
  assert.equal(services.length, 19);
  assert.equal(new Set(services.map((item) => item.service_id)).size, 19);
  assert.ok(services.some((item) => item.service_id === "dayservice"));
  assert.ok(services.some((item) => item.service_id === "homevisit"));
  assert.ok(!services.some((item) => item.service_id === "dayrehab"));
  assert.ok(!services.some((item) => item.service_id === "care-management"));
});

test("public unit prices use the API's exact gated source projection", () => {
  for (const service of listPublicUnitPriceServices()) {
    const trust = getProgressivePublicationTrust(
      service.service_id, UNIT_PRICE_SOURCE_FAMILY,
    );
    const records = getProgressiveSourceRecords(
      service.service_id, UNIT_PRICE_SOURCE_FAMILY,
    );
    const apiItems = projectProgressiveRecords(
      service.service_id, UNIT_PRICE_SOURCE_FAMILY, records,
    );
    const rows = publicUnitPriceRows(service.service_id);
    assert.ok(trust, service.service_id);
    assert.equal(apiItems.length, 8, service.service_id);
    assert.equal(rows.length, apiItems.length, service.service_id);
    assert.deepEqual(
      rows.map((row) => [row.region_class, row.ratio_per_thousand, row.unit_price_yen]),
      apiItems.map((item) => [
        item.item_body.region_class,
        item.item_body.ratio_per_thousand,
        item.item_body.unit_price_yen,
      ]),
      service.service_id,
    );
    assert.ok(rows.every((row) => row.source_url === trust.source_url));
  }
});

test("unsupported services are not inferred from unverified multiplier mappings", () => {
  assert.deepEqual(publicUnitPriceRows("dayrehab"), []);
  assert.deepEqual(publicUnitPriceRows("care-management"), []);
  assert.deepEqual(publicUnitPriceRows("unrecognized"), []);
  assert.deepEqual(searchPublicUnitPrices("地域区分", "dayrehab"), []);
});

test("service and region class search returns the correct published prices", () => {
  const all = searchPublicUnitPrices("地域区分");
  assert.equal(all.length, 19 * 8);
  assert.equal(new Set(all.map((row) => row.service_id)).size, 19);
  const homevisit = searchPublicUnitPrices("訪問介護 一級地", "homevisit");
  assert.equal(homevisit.length, 1);
  assert.equal(homevisit[0].region_class, "一級地");
  assert.equal(homevisit[0].unit_price_yen, 11.4);
  assert.equal(searchPublicUnitPrices("該当しない語", "homevisit").length, 0);
  assert.equal(searchPublicUnitPrices("", "homevisit").length, 8);
});

test("unit price links and interfaces are service-scoped without claiming municipal review", () => {
  const url = unitPriceHref("homevisit", "一級地");
  assert.equal(url, "/fees/unit-price?service=homevisit&q=%E4%B8%80%E7%B4%9A%E5%9C%B0");
  const page = fs.readFileSync("app/fees/unit-price/page.tsx", "utf8");
  const global = fs.readFileSync("app/databases/search/page.tsx", "utf8");
  const hub = fs.readFileSync("app/databases/page.tsx", "utf8");
  assert.match(page, /listPublicUnitPriceServices/);
  assert.match(page, /人手確認が完了していない/);
  assert.match(page, /自動的に「その他」と判定しません/);
  assert.match(page, /publicUnitPriceRows/);
  assert.match(global, /searchPublicUnitPrices/);
  assert.match(global, /unitPriceByService/);
  assert.match(hub, /href="\/fees\/unit-price"/);
  assert.doesNotMatch(page, /displayedRates = runtimeRates.length \? runtimeRates : rates/);
});
