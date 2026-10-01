import test from "node:test";
import assert from "node:assert/strict";
import { searchDayrehabPublicLayers } from "../lib/dayrehab-search.ts";

const layers = (query) =>
  new Set(searchDayrehabPublicLayers(query).map((result) => result.layer));

test("dayrehab search spans remuneration and fee-guidance for an add-on query", () => {
  const results = searchDayrehabPublicLayers("入浴介助");
  assert.ok(layers("入浴介助").has("remuneration"));
  assert.ok(layers("入浴介助").has("fee-guidance"));
  assert.ok(results.some((row) => row.title.includes("入浴介助加算")));
  assert.ok(results.some((row) => row.href.includes("/services/dayrehab/remuneration#")));
  assert.ok(results.some((row) => row.href.includes("/services/dayrehab/remuneration/guidance#R6-8-12")));
});

test("dayrehab search spans ordinance and interpretation notice for management query", () => {
  const results = searchDayrehabPublicLayers("管理者");
  assert.ok(layers("管理者").has("ordinance37"));
  assert.ok(layers("管理者").has("rouki25"));
  assert.ok(results.some((row) => row.href === "/services/dayrehab/rules/116"));
  assert.ok(results.some((row) => row.href.endsWith("#dayrehab.rouki25.3.2")));
});

test("dayrehab search keeps every result inside dayrehab public routes", () => {
  const queries = ["管理者", "入浴介助", "送迎", "感染症"];
  for (const query of queries) {
    const results = searchDayrehabPublicLayers(query);
    assert.ok(results.length > 0, query);
    for (const result of results) {
      assert.ok(
        result.href.startsWith("/services/dayrehab/"),
        `${query}: unexpected cross-service href ${result.href}`,
      );
    }
  }
});

test("dayrehab search preserves layer-specific verification identities", () => {
  const results = [
    ...searchDayrehabPublicLayers("管理者"),
    ...searchDayrehabPublicLayers("入浴介助"),
  ];
  const ids = new Set(results.map((row) => row.verificationLayerId));
  assert.ok(ids.has("ordinance37-dayrehab"));
  assert.ok(ids.has("rouki25-dayrehab"));
  assert.ok(ids.has("remuneration-dayrehab"));
  assert.ok(ids.has("fee-guidance-dayrehab"));
});
