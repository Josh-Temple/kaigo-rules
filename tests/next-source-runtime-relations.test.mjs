import test from "node:test";
import assert from "node:assert/strict";

import {
  DELEGATED_REMUNERATION_CANONICAL_SOURCE_ID,
  DELEGATED_REMUNERATION_SOURCE_FAMILY,
  GOVERNING_STANDARDS_SOURCE_FAMILY,
  UNIT_PRICE_SOURCE_FAMILY,
  projectRuntimeRecord,
  runtimeAdapterForPromotion,
  runtimeRecordsForPromotion,
} from "../lib/publication-runtime-adapters.ts";
import { verifiedRelatedPrimarySources } from "../lib/verified-related-sources.ts";

function delegatedPromotion(serviceId = "dayservice") {
  return {
    service_id: serviceId,
    source_family: DELEGATED_REMUNERATION_SOURCE_FAMILY,
    source_identity: {
      canonical_source_id:
        DELEGATED_REMUNERATION_CANONICAL_SOURCE_ID,
      title:
        "介護報酬の算定方法・厚生労働大臣基準（別告示）",
      version_id: "worker-b-current-source-set",
      effective_date: "2026-06-01",
      verified_at: "2026-10-06",
    },
    source_version_contains_scope: true,
    ingestion_state: "INGESTED",
    item_body_state: "PASS",
    projected_currentness_state: "PASS",
    promotion_applied: true,
  };
}

test("delegated remuneration adapter publishes only canonical mapped nodes", () => {
  const promotion = delegatedPromotion("dayservice");
  const adapter = runtimeAdapterForPromotion(promotion);
  assert.ok(adapter);
  assert.equal(
    adapter.canonicalSourceId,
    DELEGATED_REMUNERATION_CANONICAL_SOURCE_ID,
  );
  assert.equal(
    adapter.sourceFamily,
    DELEGATED_REMUNERATION_SOURCE_FAMILY,
  );
  assert.equal(adapter.recordKind, "DELEGATED_CRITERIA");

  const records = runtimeRecordsForPromotion(promotion);
  assert.equal(records.length, 20);
  assert.ok(
    records.every(
      (record) =>
        record.id.startsWith("notice") &&
        record.official_text &&
        record.source_url &&
        record.source_locator,
    ),
  );

  const trust = {
    service_id: "dayservice",
    service_label: "通所介護",
    source_family: DELEGATED_REMUNERATION_SOURCE_FAMILY,
    canonical_source_id:
      DELEGATED_REMUNERATION_CANONICAL_SOURCE_ID,
    source_title: promotion.source_identity.title,
    source_url: "",
    source_version: promotion.source_identity.version_id,
    effective_date: promotion.source_identity.effective_date,
    checked_at: promotion.source_identity.verified_at,
  };
  const projection = projectRuntimeRecord(
    promotion,
    trust,
    records[0],
  );
  assert.ok(projection);
  assert.equal(
    projection.source_metadata.source_family,
    DELEGATED_REMUNERATION_SOURCE_FAMILY,
  );
  assert.equal(
    projection.item_body.canonical_node_id,
    records[0].id,
  );
  assert.match(
    projection.source_locator.url,
    /mhlw\.go\.jp/,
  );
  assert.ok(projection.source_locator.locator);
});

test("delegated remuneration adapter fails closed for blocked and not-applicable cells", () => {
  const notApplicable = delegatedPromotion(
    "specific-welfare-equipment-sale",
  );
  assert.equal(
    runtimeAdapterForPromotion(notApplicable),
    null,
  );
  assert.deepEqual(
    runtimeRecordsForPromotion(notApplicable),
    [],
  );

  const preventiveNotApplicable = delegatedPromotion(
    "specific-preventive-welfare-equipment-sale",
  );
  assert.equal(
    runtimeAdapterForPromotion(preventiveNotApplicable),
    null,
  );

  const blocked = delegatedPromotion("dayservice");
  blocked.projected_currentness_state = "NOT_ESTABLISHED";
  assert.equal(runtimeAdapterForPromotion(blocked), null);

  const unsupportedIdentity = delegatedPromotion("dayservice");
  unsupportedIdentity.source_identity.canonical_source_id =
    "unsupported-source";
  assert.equal(
    runtimeAdapterForPromotion(unsupportedIdentity),
    null,
  );

  const wrongFamily = delegatedPromotion("dayservice");
  wrongFamily.source_family =
    GOVERNING_STANDARDS_SOURCE_FAMILY;
  assert.equal(runtimeAdapterForPromotion(wrongFamily), null);
});

test("delegated remuneration service mappings do not cross regular and preventive canonical IDs", () => {
  const regular = runtimeRecordsForPromotion(
    delegatedPromotion("homebath"),
  );
  const preventive = runtimeRecordsForPromotion(
    delegatedPromotion("preventive-homebath"),
  );

  assert.equal(regular.length, 7);
  assert.equal(preventive.length, 8);
  assert.notDeepEqual(
    regular.map((record) => record.id),
    preventive.map((record) => record.id),
  );
  assert.ok(
    preventive.some(
      (record) => !regular.some((row) => row.id === record.id),
    ),
  );
});

test("verified related-source projection exposes only independent PASS edges with correct direction", () => {
  const ordinanceRelations =
    verifiedRelatedPrimarySources(
      "dayservice",
      GOVERNING_STANDARDS_SOURCE_FAMILY,
      { id: "ordinance37.article.93" },
    );
  assert.ok(ordinanceRelations.length > 0);
  assert.ok(
    ordinanceRelations.every(
      (relation) =>
        relation.relation_direction ===
          "REFERENCED_BY" &&
        relation.relation_kind === "EXPLICIT_REFERENCE" &&
        relation.label.includes("参照している"),
    ),
  );

  const delegatedRecords = runtimeRecordsForPromotion(
    delegatedPromotion("dayservice"),
  );
  const auditedDelegated = delegatedRecords.find(
    (record) =>
      record.legacy_node_id ===
      "criteria95.dayservice.14-6",
  );
  assert.ok(auditedDelegated);
  const delegatedRelations =
    verifiedRelatedPrimarySources(
      "dayservice",
      DELEGATED_REMUNERATION_SOURCE_FAMILY,
      auditedDelegated,
    );
  assert.equal(delegatedRelations.length, 1);
  assert.equal(
    delegatedRelations[0].relation_direction,
    "REFERENCED_BY",
  );
  assert.match(
    delegatedRelations[0].href,
    /^\/fees#/,
  );

  const unauditedDelegated = delegatedRecords.find(
    (record) =>
      record.legacy_node_id ===
      "criteria95.dayservice.14-3",
  );
  assert.ok(unauditedDelegated);
  assert.deepEqual(
    verifiedRelatedPrimarySources(
      "dayservice",
      DELEGATED_REMUNERATION_SOURCE_FAMILY,
      unauditedDelegated,
    ),
    [],
  );

  assert.deepEqual(
    verifiedRelatedPrimarySources(
      "homevisit",
      GOVERNING_STANDARDS_SOURCE_FAMILY,
      { id: "ordinance37.article.93" },
    ),
    [],
  );
});

test("verified source-chain projection keeps unit-price relation bounded to dayservice", () => {
  const relations = verifiedRelatedPrimarySources(
    "dayservice",
    UNIT_PRICE_SOURCE_FAMILY,
    {
      id: "unitprice.dayservice.1",
      source_id: "mhlw-unit-price-current",
    },
  );
  assert.equal(relations.length, 1);
  assert.equal(
    relations[0].relation_direction,
    "REFERENCED_BY",
  );
  assert.match(relations[0].title, /通所介護費/);

  assert.deepEqual(
    verifiedRelatedPrimarySources(
      "homevisit",
      UNIT_PRICE_SOURCE_FAMILY,
      {
        id: "unitprice.homevisit.1",
        source_id: "mhlw-unit-price-current",
      },
    ),
    [],
  );
});
