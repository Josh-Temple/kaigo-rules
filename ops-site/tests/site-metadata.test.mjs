import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { issueRegistry } from "../app/issues/registry.ts";
import {
  buildPublicPageMetadata,
  OPS_SITE_NAME,
  OPS_SITE_URL,
} from "../lib/site-metadata.ts";

test("public page metadata keeps canonical and share URLs on the public route", () => {
  const metadata = buildPublicPageMetadata({
    path: "/issues/documentation",
    title: "記録・文書作成に時間がかかる | 介護業務改善",
    description: "説明",
    type: "article",
  });

  assert.equal(metadata.alternates.canonical, "/issues/documentation");
  assert.equal(metadata.openGraph.url, "/issues/documentation");
  assert.equal(metadata.openGraph.siteName, OPS_SITE_NAME);
  assert.equal(metadata.openGraph.type, "article");
  assert.equal(metadata.twitter.card, "summary");
});

test("robots route allows public crawling and points to the canonical sitemap", () => {
  const source = readFileSync(new URL("../app/robots.ts", import.meta.url), "utf8");
  assert.match(source, /userAgent: "\*"/);
  assert.match(source, /allow: "\/"/);
  assert.match(source, /sitemap: `\$\{OPS_SITE_URL\}\/sitemap\.xml`/);
  assert.match(source, /host: OPS_SITE_URL/);
});

test("sitemap route stays Issue-first and uses the shared registry", () => {
  const source = readFileSync(new URL("../app/sitemap.ts", import.meta.url), "utf8");
  assert.equal(issueRegistry.length, 5);
  assert.match(source, /issueRegistry\.map/);
  assert.match(source, /\$\{OPS_SITE_URL\}\$\{issue\.href\}/);
  assert.ok(!source.includes("/tools/"));
  assert.ok(source.includes("/guides/medication-incident-sources"));
  assert.equal(OPS_SITE_URL, "https://ops-site-pi.vercel.app");
});
