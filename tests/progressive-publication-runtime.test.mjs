import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";

import {
  SAFE_PUBLICATION_FIELDS,
  filterProgressivePublishedRules,
  getProgressivePublicationTrust,
  getProgressiveSourceRecords,
  isProgressivePublicationCell,
  isProgressiveRulePublished,
  isSupportedPublicationContract,
  listProgressivePublicationServices,
  projectProgressiveRule,
  publicationServicePresentationGroup,
} from "../lib/publication-policy.ts";

const originalServices = [
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

const preventiveServices = [
  "preventive-homebath",
  "preventive-homenursing",
  "preventive-homerehab",
  "preventive-homecaremanagement",
  "preventive-dayrehab",
  "preventive-shortstay-life",
  "preventive-shortstay-medical",
  "preventive-specific-facility",
  "preventive-welfare-equipment-rental",
  "specific-preventive-welfare-equipment-sale",
];

const expectedServices = [...originalServices, ...preventiveServices];

test("progressive publication keeps the original ten cells and adds ten preventive cells", () => {
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

test("original ordinance37 service scope remains enforced", () => {
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

test("preventive standards use standards35 scope without cross-source projection", () => {
  assert.equal(
    isProgressiveRulePublished("preventive-homebath", "standards35.article.46"),
    true,
  );
  assert.equal(
    isProgressiveRulePublished("preventive-homebath", "standards35.article.46.p.1"),
    true,
  );
  assert.equal(
    isProgressiveRulePublished("preventive-homebath", "standards35.article.62"),
    false,
  );
  assert.equal(
    isProgressiveRulePublished("preventive-homebath", "ordinance37.article.46"),
    false,
  );

  const records = getProgressiveSourceRecords("preventive-homebath");
  assert.ok(records.some((row) => row.id === "standards35.article.46"));
  assert.equal(records.some((row) => row.id.startsWith("ordinance37.")), false);
});

test("source identity and applicability proof contracts fail closed", () => {
  assert.equal(
    isSupportedPublicationContract(
      "ordinance37",
      "PASS_DIRECT_SERVICE_CHAPTER",
      true,
    ),
    true,
  );
  assert.equal(
    isSupportedPublicationContract(
      "preventive-services-standards",
      "PASS_DIRECT_SERVICE_SCOPE",
      true,
    ),
    true,
  );
  assert.equal(
    isSupportedPublicationContract(
      "preventive-services-standards",
      "PASS_DIRECT_SERVICE_CHAPTER",
      true,
    ),
    false,
  );
  assert.equal(
    isSupportedPublicationContract(
      "unsupported-source",
      "PASS_DIRECT_SERVICE_SCOPE",
      true,
    ),
    false,
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

test("preventive projection preserves its own source identity and locator", () => {
  const records = getProgressiveSourceRecords("preventive-homebath");
  const node = records.find(
    (row) => row.id === "standards35.article.46",
  );
  assert.ok(node);

  const projection = projectProgressiveRule("preventive-homebath", node);
  const trust = getProgressivePublicationTrust("preventive-homebath");
  assert.ok(projection);
  assert.ok(trust);
  assert.equal(trust.canonical_source_id, "preventive-services-standards");
  assert.equal(
    projection.source_metadata.canonical_source_id,
    "preventive-services-standards",
  );
  assert.match(trust.source_url, /418M60000100035/);
  assert.match(projection.source_metadata.source_title, /介護予防サービス/);
  assert.equal(
    projection.service_applicability_statement.label,
    "介護予防訪問入浴介護の直接適用範囲に含まれる条文として確認済み",
  );
});

test("preventive variants retain a presentation group with their counterpart", () => {
  assert.equal(publicationServicePresentationGroup("homebath"), "homebath");
  assert.equal(
    publicationServicePresentationGroup("preventive-homebath"),
    "homebath",
  );
  assert.equal(
    publicationServicePresentationGroup("preventive-dayrehab"),
    "dayrehab",
  );
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

  for (const surface of surfaces) {
    const source = fs.readFileSync(surface, "utf8");
    assert.match(source, /publication-policy/);
  }
});

test("UI, search, and API source-switching surfaces consume adapter-selected records", () => {
  for (const surface of [
    "app/rules/page.tsx",
    "app/rules/[article]/page.tsx",
    "app/databases/search/page.tsx",
    "app/api/context/services/[serviceId]/rules/route.ts",
  ]) {
    const source = fs.readFileSync(surface, "utf8");
    assert.match(source, /getProgressiveSourceRecords/);
  }
});
