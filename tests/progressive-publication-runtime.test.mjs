import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";

import {
  SAFE_PUBLICATION_FIELDS,
  filterProgressivePublishedRules,
  isProgressivePublicationCell,
  isProgressiveRulePublished,
  listProgressivePublicationServices,
  projectProgressiveRule,
} from "../lib/publication-policy.ts";

const expectedServices = [
  "homevisit",
  "homebath",
  "homenursing",
  "homerehab",
  "homecaremanagement",
  "shortstay-life",
  "shortstay-medical",
  "specific-facility",
  "welfare-equipment-rental",
  "specific-welfare-equipment-sale",
];

test("progressive publication exposes exactly the first ten ready ordinance cells", () => {
  assert.deepEqual(
    listProgressivePublicationServices().map((item) => item.service_id),
    expectedServices,
  );
  for (const serviceId of expectedServices) {
    assert.equal(isProgressivePublicationCell(serviceId), true);
  }
  assert.equal(isProgressivePublicationCell("dayservice"), false);
  assert.equal(isProgressivePublicationCell("care-management"), false);
});

test("service scope is enforced at article and child-node level", () => {
  assert.equal(
    isProgressiveRulePublished("homevisit", "ordinance37.article.18"),
    true,
  );
  assert.equal(
    isProgressiveRulePublished("homevisit", "ordinance37.article.18.p.1"),
    true,
  );
  assert.equal(
    isProgressiveRulePublished("homevisit", "ordinance37.article.44"),
    false,
  );
  assert.equal(
    isProgressiveRulePublished("homebath", "ordinance37.article.44"),
    true,
  );

  const records = [
    { id: "ordinance37.article.18", label: "homevisit" },
    { id: "ordinance37.article.44", label: "homebath" },
  ];
  assert.deepEqual(
    filterProgressivePublishedRules("homevisit", records, (row) => row.id),
    [records[0]],
  );
});

test("public projection contains only the bounded safe publication units", () => {
  const projection = projectProgressiveRule("homevisit", {
    id: "ordinance37.article.18",
    node_type: "article",
    article_num: "18",
    article_title: "第十八条",
    caption: "運営規程",
    path: ["第二章", "第四節"],
    official_text: "指定訪問介護事業者は、運営についての重要事項に関する規程を定めておかなければならない。",
    source_url: "https://laws.e-gov.go.jp/law/411M50000100037",
    source_locator: "Article=18",
  });

  assert.ok(projection);
  assert.deepEqual(Object.keys(projection).sort(), [...SAFE_PUBLICATION_FIELDS].sort());
  assert.match(projection.source_locator.url, /laws\.e-gov\.go\.jp/);
  assert.equal(
    projection.service_applicability_statement.label,
    "訪問介護の直接適用章に含まれる条文として確認済み",
  );

  const serialized = JSON.stringify(projection);
  for (const forbidden of [
    "human_review",
    "relation_verification",
    "blocking_reasons",
    "readiness",
    "source_fingerprint",
    "projection_provenance",
  ]) {
    assert.equal(serialized.includes(forbidden), false);
  }
});

test("blocked service cannot obtain a public projection", () => {
  assert.equal(
    projectProgressiveRule("care-management", {
      id: "ordinance37.article.18",
      node_type: "article",
      article_num: "18",
      official_text: "本文",
    }),
    null,
  );
});

test("UI, search, and API surfaces import the same canonical policy", () => {
  const surfaces = [
    "app/rules/page.tsx",
    "app/rules/[article]/page.tsx",
    "app/databases/search/page.tsx",
    "app/search/page.tsx",
    "app/api/context/services/[serviceId]/rules/route.ts",
  ];

  for (const path of surfaces) {
    const source = fs.readFileSync(path, "utf8");
    assert.match(source, /publication-policy/);
  }
});
