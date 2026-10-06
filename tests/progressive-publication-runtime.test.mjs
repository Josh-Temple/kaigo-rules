import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import highValueCurrentnessData from "../data/verification/high-value-currentness-closure-worker-b.json" with { type: "json" };

import {
  UNIT_PRICE_SOURCE_FAMILY as UNIT_PRICE_ADAPTER_FAMILY,
  projectRuntimeRecord,
  runtimeAdapterForPromotion,
  runtimeRecordsForPromotion,
} from "../lib/publication-runtime-adapters.ts";

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

test("Unit Price adapter accepts only the exact dayservice publication contract", () => {
  const promotion = highValueCurrentnessData.promotions[0];
  const adapter = runtimeAdapterForPromotion(promotion);
  assert.ok(adapter);
  assert.equal(adapter.canonicalSourceId, "mhlw-unit-price-current");
  assert.equal(adapter.sourceFamily, UNIT_PRICE_ADAPTER_FAMILY);
  assert.equal(adapter.recordKind, "UNIT_PRICE");

  const records = runtimeRecordsForPromotion(promotion);
  assert.equal(records.length, 8);
  assert.deepEqual(
    records.map((row) => row.region_class),
    ["一級地", "二級地", "三級地", "四級地", "五級地", "六級地", "七級地", "その他"],
  );
  assert.ok(records.every((row) => row.source_locator));

  const trust = {
    service_id: "dayservice",
    service_label: "通所介護",
    source_family: UNIT_PRICE_ADAPTER_FAMILY,
    canonical_source_id: "mhlw-unit-price-current",
    source_title: promotion.source_identity.title,
    source_url: promotion.source_identity.official_source_url,
    source_version: promotion.source_identity.version_id,
    effective_date: promotion.source_identity.effective_date,
    checked_at: promotion.source_identity.current_official_display_observed_on,
  };
  const projection = projectRuntimeRecord(promotion, trust, records[0]);
  assert.ok(projection);
  assert.deepEqual(
    Object.keys(projection).sort(),
    [...SAFE_PUBLICATION_FIELDS].sort(),
  );
  assert.equal(
    projection.source_metadata.source_family,
    "unit_price_regional_classification",
  );
  assert.equal(projection.item_body.region_class, "一級地");
  assert.equal(projection.item_body.ratio_per_thousand, 1090);
  assert.match(projection.source_locator.url, /mhlw\.go\.jp/);
  assert.match(projection.source_locator.locator, /第一号 表/);
  assert.equal(
    projection.service_applicability_statement.label,
    "通所介護の直接適用行として確認済み",
  );

  const unsupported = structuredClone(promotion);
  unsupported.source_identity.canonical_source_id = "unsupported-source";
  assert.equal(runtimeAdapterForPromotion(unsupported), null);

  const crossFamily = structuredClone(promotion);
  crossFamily.source_family = "governing_standards_ordinance";
  assert.equal(runtimeAdapterForPromotion(crossFamily), null);

  const wrongProfile = structuredClone(promotion);
  wrongProfile.applicability_proof.multiplier_profile_id = "group-1140";
  assert.equal(runtimeAdapterForPromotion(wrongProfile), null);
});

test("Unit Price adapter accepts Worker C-shaped bounded service promotions without source-family broadcast", () => {
  const dayservice = highValueCurrentnessData.promotions[0];
  const promotion = {
    service_id: "homevisit",
    source_family: "unit_price_regional_classification",
    canonical_source_identity: {
      canonical_source_id: "mhlw-unit-price-current",
      title: dayservice.source_identity.title,
      official_source_url: dayservice.source_identity.official_source_url,
      official_page_urls: dayservice.source_identity.official_page_urls,
      version_id: dayservice.source_identity.version_id,
      effective_date: "2024-04-01",
      source_form: "OFFICIAL_CURRENT_CONSOLIDATED_DISPLAY",
      currentness_class: "CURRENT_OFFICIAL_CONSOLIDATED",
    },
    service_applicability_evidence: {
      state: "PASS_DIRECT_SERVICE_SCOPE",
      official_service_name: "訪問介護",
      multiplier_profile_id: "group-1140",
      source_locator: "第一号 表 / 訪問介護 / 地域区分別割合",
      mapped_item_count: 8,
    },
    currentness_evidence: {
      official_source_locator: dayservice.source_identity.official_source_url,
      observed_on: "2026-10-06",
      effective_date: "2024-04-01",
      supersession_check: "OFFICIAL_MHLW_CONSOLIDATED_DISPLAY_REVERIFIED",
      live_verifier: "scripts/verify_unit_price_currentness.py",
    },
    allowed_publication_units: [
      "SOURCE_TEXT_ITEM_BODY",
      "SOURCE_METADATA_LOCATOR",
      "CURRENTNESS_STATEMENT",
      "SERVICE_APPLICABILITY_STATEMENT",
    ],
    ingestion_state: "INGESTED",
    item_body_state: "PASS",
    projected_currentness_state: "PASS",
    promotion_applied: true,
  };

  const adapter = runtimeAdapterForPromotion(promotion);
  assert.ok(adapter);
  const records = runtimeRecordsForPromotion(promotion);
  assert.equal(records.length, 8);
  assert.equal(records[0].id, "unitprice.homevisit.1");
  assert.equal(records[0].service, "訪問介護");
  assert.equal(records[0].ratio_per_thousand, 1140);
  assert.equal(records[0].unit_price_yen, 11.4);
  assert.match(records[0].source_locator, /第一号 表/);

  const wrongServiceProof = structuredClone(promotion);
  wrongServiceProof.service_applicability_evidence.official_service_name = "通所介護";
  assert.equal(runtimeAdapterForPromotion(wrongServiceProof), null);

  const missingLiveProof = structuredClone(promotion);
  missingLiveProof.currentness_evidence.live_verifier = "unsupported-verifier.py";
  assert.equal(runtimeAdapterForPromotion(missingLiveProof), null);
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
    "app/api/context/services/[serviceId]/sources/route.ts",
    "app/fees/unit-price/page.tsx",
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
    "app/api/context/services/[serviceId]/sources/route.ts",
    "app/fees/unit-price/page.tsx",
  ]) {
    const source = fs.readFileSync(surface, "utf8");
    assert.match(source, /getProgressiveSourceRecords/);
  }
});
