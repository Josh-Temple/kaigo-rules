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
import { getDefaultService } from "../lib/service-catalog.ts";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const scope = JSON.parse(
  fs.readFileSync(path.join(ROOT, "data/ordinance37-scope.json"), "utf8"),
);
const meta = JSON.parse(
  fs.readFileSync(path.join(ROOT, "data/ordinance37-meta.json"), "utf8"),
);

test("day-service article count uses the canonical service-scope contract", () => {
  const serviceId = getDefaultService().service_id;
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
  assert.equal(meta.counts.articles_total, 56);

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

test("rules UI distinguishes shared corpus totals from day-service totals", () => {
  const source = fs.readFileSync(
    path.join(ROOT, "app/rules/page.tsx"),
    "utf8",
  );

  assert.match(source, /filterRecordsForService\(/);
  assert.match(source, /共有コーパスノード/);
  assert.match(source, /共有コーパス条文/);
  assert.match(source, /通所介護対象条文/);
  assert.match(source, /dayServiceArticles\.length/);
  assert.doesNotMatch(source, /全182ノード/);
  assert.doesNotMatch(
    source,
    /reviewed_articles \|\| \[\]\)\.length} \/ \{meta\.counts\.articles_total/,
  );
});
