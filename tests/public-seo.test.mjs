import test from "node:test";
import assert from "node:assert/strict";
import { existsSync, readFileSync } from "node:fs";
import { SITE_ORIGIN, INDEXABLE_ROUTES, pageMetadata } from "../lib/site-metadata.ts";

const source = (path) => readFileSync(new URL("../" + path, import.meta.url), "utf8");
const fileExists = (path) => existsSync(new URL("../" + path, import.meta.url));

test("canonical URL and noindex metadata follow the public origin", () => {
  assert.equal(SITE_ORIGIN, "https://kaigo-rules.vercel.app");
  assert.equal(pageMetadata("法令", "説明", "/law").alternates.canonical, "/law");
  assert.deepEqual(pageMetadata("検索", "説明", "/search", false).robots, { index: false, follow: true });
  assert.throws(() => pageMetadata("x", "y", "/qa?q=test"), /Canonical/);
  assert.throws(() => pageMetadata("x", "y", "https://elsewhere.example"), /Canonical/);
});

test("sitemap lists only unique existing public entry URLs with canonicals", () => {
  assert.equal(new Set(INDEXABLE_ROUTES).size, INDEXABLE_ROUTES.length);
  assert.ok(INDEXABLE_ROUTES.includes("/"));
  for (const route of INDEXABLE_ROUTES) {
    assert.match(route, /^\/(?:[a-z0-9-]+(?:\/[a-z0-9-]+)*)?$/);
    const path = route === "/" ? "app/page.tsx" : "app" + route + "/page.tsx";
    assert.ok(fileExists(path), "Missing public entry route " + route);
    assert.match(source(path), /alternates:\s*\{\s*canonical:|pageMetadata\(/, "Canonical metadata missing: " + route);
  }
  for (const omitted of ["/search", "/databases/search", "/feedback", "/notices/review", "/services/dayrehab/search", "/services/dayrehab"]) {
    assert.ok(!INDEXABLE_ROUTES.includes(omitted), "Not a stable sitemap entry: " + omitted);
  }
});

test("search result, feedback and review pages are noindex", () => {
  for (const route of ["/search", "/databases/search", "/notices/review", "/services/dayrehab/search"]) {
    const body = source("app" + route + "/page.tsx");
    assert.match(body, /pageMetadata\([\s\S]*?false\);/, "noindex missing: " + route);
  }
  assert.match(source("app/feedback/layout.tsx"), /false,\s*\)/);
});

test("robots exposes sitemap without blocking pages that use noindex", () => {
  const robots = source("app/robots.ts");
  const sitemap = source("app/sitemap.ts");
  assert.match(robots, /sitemap:/);
  assert.match(robots, /disallow:\s*"\/api\/"/);
  assert.doesNotMatch(robots, /disallow:\s*"\/(search|databases)"/);
  assert.match(sitemap, /INDEXABLE_ROUTES\.map/);
  assert.match(sitemap, /new URL\(path, SITE_ORIGIN\)/);
  assert.doesNotMatch(sitemap, /lastModified/);
  assert.match(source("app/layout.tsx"), /metadataBase:\s*new URL\(SITE_ORIGIN\)/);
});
