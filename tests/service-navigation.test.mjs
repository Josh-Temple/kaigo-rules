import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";

const readText = (relativePath) => fs.readFileSync(relativePath, "utf8");

test("global navigation is service-neutral and keeps source search alongside handbooks", () => {
  const source = readText("components/service-navigation.tsx");

  assert.match(source, /サイト共通ナビゲーション/);
  assert.match(source, /サービス別/);
  assert.match(source, /資料を探す/);
  assert.match(source, /href: "\/databases"/);
  assert.match(source, /制度の見取り図/);
  assert.match(source, /根拠資料/);
  assert.match(source, /フィードバック/);
  assert.doesNotMatch(source, /通所介護|通所リハビリテーション|通所リハ/);
  assert.doesNotMatch(source, /usePathname/);
});

test("database hub exposes shared databases and service-specific remuneration routes", () => {
  const source = readText("app/databases/page.tsx");

  assert.match(source, /<h1>介護制度DB<\/h1>/);
  assert.match(source, /介護保険法DB/);
  assert.match(source, /基準省令DB/);
  assert.match(source, /基準解釈通知DB/);
  assert.match(source, /国Q&A DB/);
  assert.match(source, /href="\/fees"/);
  assert.match(source, /href="\/services\/dayrehab\/remuneration"/);
  assert.match(source, /DBごとに公開範囲が異なります/);
});

test("all services have handbook entries, including the two existing service routes", () => {
  const index = readText("app/services/page.tsx");
  const dayservice = readText("app/services/dayservice/page.tsx");
  const dayrehab = readText("app/services/dayrehab/page.tsx");

  assert.match(index, /"\/services\/" \+ serviceId/);
  assert.match(dayservice, /ServiceHandbook/);
  assert.match(dayservice, /serviceHandbook\("dayservice"\)/);
  assert.match(dayrehab, /ServiceHandbook/);
  assert.match(dayrehab, /serviceHandbook\("dayrehab"\)/);
});

test("home puts the service handbook first and retains keyword search", () => {
  const source = readText("app/page.tsx");

  assert.match(source, /キーワードから制度資料を探す/);
  assert.match(source, /サービスを選んで手引を読む/);
  assert.match(source, /href="\/databases\/search"/);
  assert.ok(
    source.indexOf('href="/services"') < source.indexOf('href="/databases/search"'),
    "service handbooks must be the first entry for readers",
  );
});


test("public service navigation covers every canonical service once and keeps preventive support independent", () => {
  const navigation = JSON.parse(readText("data/public-service-navigation.json"));
  const catalog = JSON.parse(readText("data/services/catalog.generated.json"));
  const units = navigation.groups.flatMap((group) => group.units);
  const serviceIds = units.flatMap((unit) => unit.service_ids);
  const catalogIds = catalog.services.map((service) => service.service_id);

  assert.equal(navigation.groups.length, 7);
  assert.equal(units.length, 26);
  assert.equal(serviceIds.length, 39);
  assert.equal(new Set(serviceIds).size, 39);
  assert.deepEqual(new Set(serviceIds), new Set(catalogIds));

  const preventiveSupportUnit = units.find((unit) =>
    unit.service_ids.includes("preventive-support")
  );
  assert.deepEqual(preventiveSupportUnit?.service_ids, ["preventive-support"]);

  for (const unit of units.filter((item) => item.service_ids.length > 1)) {
    assert.equal(unit.service_ids.length, 2);
    assert.match(unit.service_ids[1], /preventive|specific-preventive/);
  }
});

test("services page uses user-facing groups and opens complete handbooks", () => {
  const source = readText("app/services/page.tsx");

  assert.match(source, /publicServiceNavigationGroups/);
  assert.match(source, /案内上の分類/);
  assert.match(source, /介護予防支援は独立/);
  assert.match(source, /全15章の手引を読む/);
  assert.match(source, /確認前の内容も掲載/);
  assert.match(source, /\/legislation/);
});


test("working handbooks coexist with the existing publication-gated guide navigation", () => {
  const services = readText("app/services/page.tsx");
  const contextLinks = readText("components/service-context-links.tsx");
  const guide = readText("app/guide/page.tsx");

  assert.match(services, /"\/services\/" \+ serviceId/);
  assert.match(services, /39サービスすべて/);
  assert.match(contextLinks, /publicSourceFamiliesForService/);
  assert.match(contextLinks, /UNIT_PRICE_SOURCE_FAMILY/);
  assert.match(contextLinks, /\/fees\/unit-price/);
  assert.match(guide, /publicSourceFamiliesForService/);
  assert.match(guide, /現在公開している/);
  assert.doesNotMatch(guide, /READY_FOR_PUBLICATION_REVIEW|blocking_reasons/);
});
