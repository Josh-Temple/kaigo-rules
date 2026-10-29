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
  for (const omitted of ["/search", "/databases/search", "/feedback", "/notices/review", "/services/dayrehab/search", "/services/dayrehab", "/services/dayservice"]) {
    assert.ok(!INDEXABLE_ROUTES.includes(omitted), "Not a stable sitemap entry: " + omitted);
  }
});

test("search result, review, feedback and unreviewed handbook chapter pages are noindex", () => {
  for (const route of ["/search", "/databases/search", "/notices/review", "/services/dayrehab/search"]) {
    const body = source("app" + route + "/page.tsx");
    assert.match(body, /pageMetadata\([\s\S]*?false\);/, "noindex missing: " + route);
  }
  const handbookChapter = source("app/handbook/[serviceId]/[chapter]/page.tsx");
  assert.match(handbookChapter, /handbookChapterHref\(service\.service_id,\s*chapter\.section_id\),\s*false\s*\)/, "unreviewed handbook chapters must remain noindex");
  assert.match(handbookChapter, /未確認の説明を含みます/, "unreviewed status warning must remain visible");
  assert.match(handbookChapter, /条件・例外と確認状況を読み/, "conditions and exceptions must remain visible");
  for (const route of ["app/services/[serviceId]/page.tsx", "app/services/dayservice/page.tsx", "app/services/dayrehab/page.tsx"]) {
    assert.match(source(route), /pageMetadata\([\s\S]*?false\)/, "unreviewed service handbook overview must remain noindex: " + route);
  }
  assert.match(source("app/feedback/layout.tsx"), /false,\s*\)/);
});

test("robots exposes sitemap without blocking pages that use noindex", () => {
  const robots = source("app/robots.ts");
  const sitemap = source("app/sitemap.ts");
  assert.match(robots, /sitemap:/);
  assert.match(robots, /disallow:\s*"\/api\/"/);
  assert.doesNotMatch(robots, /disallow:\s*"\/(search|databases)"/);
  assert.match(sitemap, /new Set<string>\(INDEXABLE_ROUTES\)/);
  assert.doesNotMatch(sitemap, /serviceHandbooks/);
  assert.match(sitemap, /return \[\.\.\.paths\]\.map/);
  assert.match(sitemap, /new URL\(path, SITE_ORIGIN\)/);
  assert.doesNotMatch(sitemap, /lastModified/);
  assert.match(source("app/layout.tsx"), /metadataBase:\s*new URL\(SITE_ORIGIN\)/);
});
