// Revalidated against revised A2 head 74f5b4c4723dd50974107798d8c01d42339e191a.
// #171 B3/B4 regression: service-specific counts must use #170's canonical scope contract.
import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

import {
  filterRecordsForService,
  isRecordApplicableToService,
  serviceApplicability,
} from "../lib/service-scope.ts";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const scope = JSON.parse(
  fs.readFileSync(path.join(ROOT, "data/ordinance37-scope.json"), "utf8"),
);
const meta = JSON.parse(
  fs.readFileSync(path.join(ROOT, "data/ordinance37-meta.json"), "utf8"),
);

test("day-service article count uses the canonical service-scope contract", () => {
  const serviceId = "dayservice";
  const dayServiceArticleNumbers = [
    ...(scope.direct_articles || []),
    ...(scope.incorporated_articles || []),
  ];
  const records = [
    ...dayServiceArticleNumbers.map((article) => ({
      id: `ordinance37.article.${article}`,
    })),
    { id: "ordinance37.article.18" },
  ];
  const scoped = filterRecordsForService(
    serviceId,
    "ordinance37",
    records,
    (record) => record.id,
  );

  assert.equal(serviceId, "dayservice");
  assert.equal(dayServiceArticleNumbers.length, 40);
  assert.equal(scoped.length, 40);
  assert.equal(
    scoped.some((record) => record.id === "ordinance37.article.18"),
    false,
  );
  assert.equal(meta.scope.mode, "FULL_MAIN_PROVISION");
  assert.ok(meta.counts.articles_total > scoped.length);

  assert.equal(
    isRecordApplicableToService(
      serviceId,
      "ordinance37",
      "ordinance37.article.18",
    ),
    false,
  );
  assert.equal(
    isRecordApplicableToService(
      serviceId,
      "ordinance37",
      "ordinance37.article.10",
    ),
    true,
  );
  assert.equal(
    serviceApplicability(
      serviceId,
      "ordinance37",
      "ordinance37.article.10",
    ).basis,
    "INCORPORATED_SCOPE",
  );
  assert.equal(
    serviceApplicability(
      serviceId,
      "ordinance37",
      "ordinance37.article.100",
    ).basis,
    "DIRECT_SCOPE",
  );
});

test("rules UI defaults to shared corpus totals and applies service scope only when selected", () => {
  const source = fs.readFileSync(
    path.join(ROOT, "app/rules/page.tsx"),
    "utf8",
  );

  assert.match(source, /filterRecordsForService\(/);
  assert.match(source, /共有コーパスノード/);
  assert.match(source, /共有コーパス条文/);
  assert.match(source, /表示中の条文/);
  assert.match(source, /selectedServiceId[\s\S]*progressiveSelection/);
  assert.match(source, /\? filterProgressivePublishedRules\(/);
  assert.match(source, /: filterRecordsForService\(/);
  assert.match(source, /: articles;/);
  assert.match(source, /すべて/);
  assert.match(source, /公開中サービスフィルタ/);
  assert.doesNotMatch(source, /通所介護対象条文/);
  assert.doesNotMatch(source, /dayServiceArticles\.length/);
  assert.doesNotMatch(source, /全182ノード/);
});
