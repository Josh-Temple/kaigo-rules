import test from "node:test";
import assert from "node:assert/strict";
import { issueRegistry } from "../app/issues/registry.ts";
import robots from "../app/robots.ts";
import sitemap from "../app/sitemap.ts";
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

test("robots allows public crawling and points to the canonical sitemap", () => {
  const config = robots();
  assert.deepEqual(config.rules, { userAgent: "*", allow: "/" });
  assert.equal(config.sitemap, `${OPS_SITE_URL}/sitemap.xml`);
  assert.equal(config.host, OPS_SITE_URL);
});

test("sitemap contains home and the five Issue entry pages, not action tools", () => {
  const urls = sitemap().map((entry) => entry.url);
  assert.deepEqual(urls, [
    `${OPS_SITE_URL}/`,
    ...issueRegistry.map((issue) => `${OPS_SITE_URL}${issue.href}`),
  ]);
  assert.equal(urls.length, 6);
  assert.ok(urls.every((url) => !url.includes("/tools/")));
});
