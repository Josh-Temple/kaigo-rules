import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";

const readText = (relativePath) => fs.readFileSync(relativePath, "utf8");

test("global navigation is service-neutral and exposes one database entry", () => {
  const source = readText("components/service-navigation.tsx");

  assert.match(source, /サイト共通ナビゲーション/);
  assert.match(source, /サービス別/);
  assert.match(source, /DB一覧/);
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

test("published services have dedicated service landing pages", () => {
  const index = readText("app/services/page.tsx");
  const dayservice = readText("app/services/dayservice/page.tsx");
  const dayrehab = readText("app/services/dayrehab/page.tsx");

  assert.match(index, /"\/services\/" \+ serviceId/);
  assert.match(dayservice, /<h1>通所介護<\/h1>/);
  assert.match(dayrehab, /<h1>通所リハビリテーション<\/h1>/);
});

test("home exposes the database-wide entry before service-specific content", () => {
  const source = readText("app/page.tsx");

  assert.match(source, /キーワードから制度資料を探す/);
  assert.match(source, /特定のサービスから見る/);
  assert.match(source, /href="\/databases\/search"/);
  assert.match(source, /サービスを先に決めなくても/);
  assert.ok(
    source.indexOf('href="/databases/search"') < source.indexOf('href="/services"'),
    "database-wide search must remain before service-specific entry",
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

test("services page uses user-facing groups and a database fallback instead of manifest order", () => {
  const source = readText("app/services/page.tsx");

  assert.match(source, /publicServiceNavigationGroups/);
  assert.match(source, /案内上の分類/);
  assert.match(source, /介護予防支援は独立/);
  assert.match(source, /DB全体から名称検索/);
  assert.match(source, /検索結果が少ない場合も、制度資料そのものが存在しないとは限りません/);
});
