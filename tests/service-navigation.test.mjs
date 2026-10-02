import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";

const readText = (relativePath) => fs.readFileSync(relativePath, "utf8");

test("global navigation is service-neutral", () => {
  const source = readText("components/service-navigation.tsx");

  assert.match(source, /サイト共通ナビゲーション/);
  assert.match(source, /サービス別/);
  assert.match(source, /基準DB/);
  assert.match(source, /通知DB/);
  assert.match(source, /制度の見取り図/);
  assert.match(source, /根拠資料/);
  assert.doesNotMatch(source, /通所介護|通所リハビリテーション|通所リハ/);
  assert.doesNotMatch(source, /usePathname/);
});

test("published services have dedicated service landing pages", () => {
  const index = readText("app/services/page.tsx");
  const dayservice = readText("app/services/dayservice/page.tsx");
  const dayrehab = readText("app/services/dayrehab/page.tsx");

  assert.match(index, /\/services\/\$\{serviceId\}/);
  assert.match(dayservice, /<h1>通所介護<\/h1>/);
  assert.match(dayrehab, /<h1>通所リハビリテーション<\/h1>/);
});

test("home starts from service selection instead of a default-service database menu", () => {
  const source = readText("app/page.tsx");

  assert.match(source, /サービスを選んで調べる/);
  assert.match(source, /サービスごとに公開範囲と確認状態を分けて整理します/);
  assert.doesNotMatch(source, /href="\/search"[\s\S]*疑問から根拠を横断検索する/);
});
