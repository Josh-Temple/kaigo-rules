import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";

const source = readFileSync(new URL("../app/guides/accident-medication-sources/page.tsx", import.meta.url), "utf8");
const css = readFileSync(new URL("../app/guides/accident-medication-sources/sources.module.css", import.meta.url), "utf8");
const home = readFileSync(new URL("../app/page.tsx", import.meta.url), "utf8");
const sitemap = readFileSync(new URL("../app/sitemap.ts", import.meta.url), "utf8");

test("draft page fails closed on public and Vercel preview runtimes", () => {
  assert.match(source, /KAIGO_OPS_SOURCE_GUIDE_REVIEW !== "local"/);
  assert.match(source, /process\.env\.VERCEL/);
  assert.match(source, /notFound\(\)/);
  assert.match(source, /force-dynamic/);
  assert.match(source, /index: false, follow: false/);
  assert.doesNotMatch(home, /accident-medication-sources/);
  assert.doesNotMatch(sitemap, /accident-medication-sources/);
});

test("four existing source-qualified origins and document contexts appear", () => {
  for (const fragment of [
    "001591418.pdf", "73_aruteppu.pdf", "001574219.pdf",
    "consultation-for-patients/on-drugs/0003.html",
    "2025年11月", "2017年3月", "2024年11月29日",
    "ガイドライン", "調査研究報告書", "通知", "一般向け相談案内",
    "介護保険施設", "高齢者向け住まい",
  ]) assert.ok(source.includes(fragment), fragment);
  // A has not qualified these new Wave candidates for B's finalized page copy.
  assert.ok(!source.includes("001094895.pdf"));
  assert.ok(!source.includes("001094896.pdf"));
  assert.ok(!source.includes("newpage_74909.html"));
});

test("human clinical and statutory decisions are not implemented", () => {
  assert.match(source, /正式な事故対応手順/);
  assert.match(source, /第1報の5日以内は国通知の目安/);
  assert.match(source, /法定受診義務/);
  assert.match(source, /医師の診断/);
  for (const forbidden of ["<input", "<textarea", "<form", "fetch(", "localStorage", "sessionStorage", "analytics.track", "penalcode", 'href="/guides/medication-incident-sources"', 'href="/guides/fall-prevention-sources"', "#law", "medication-safety-preview"]) {
    assert.ok(!source.includes(forbidden), forbidden);
  }
});

test("responsive, keyboard, reduced motion and printed full source URLs are specified", () => {
  assert.match(css, /max-width: 720px/);
  assert.match(css, /focus-visible/);
  assert.match(css, /prefers-reduced-motion/);
  assert.match(css, /@media print/);
  assert.match(css, /break-inside: avoid/);
  assert.match(source, /原典URL：/);
});
