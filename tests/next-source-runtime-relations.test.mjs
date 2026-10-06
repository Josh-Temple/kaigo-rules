import test from "node:test";
import assert from "node:assert/strict";

import applicabilityData from "../data/shared/remuneration-delegated/service-applicability.json" with { type: "json" };
import corpusData from "../data/shared/remuneration-delegated/national-corpus.json" with { type: "json" };
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

const nodeById = new Map(
  (corpusData.nodes || []).map((node) => [
    node.canonical_node_id,
    node,
  ]),
);

function delegatedPromotion(serviceId = "homevisit") {
  const service = (applicabilityData.services || []).find(
    (row) => row.service_id === serviceId,
  );
  const mappedNodeIds = (service?.mapped_node_ids || []).map(String);
  const mappedSourceIds = [
    ...new Set(
      mappedNodeIds
        .map((nodeId) => nodeById.get(nodeId)?.source_id)
        .filter(Boolean),
    ),
  ].sort();

  return {
    service_id: serviceId,
    source_family: DELEGATED_REMUNERATION_SOURCE_FAMILY,
    source_identity: {
      canonical_source_id:
        DELEGATED_REMUNERATION_CANONICAL_SOURCE_ID,
      title:
        "介護報酬の算定方法・厚生労働大臣基準（別告示）",
      current_official_display_observed_on: "2026-10-06",
    },
    mapped_node_count: mappedNodeIds.length,
    mapped_node_ids: mappedNodeIds,
    mapped_source_ids: mappedSourceIds,
    applicability_proof: {
      state: "PASS_EXPLICIT_CANONICAL_SERVICE_MAPPING",
      inherited_from_sibling_service: false,
    },
    source_currentness_evidence: mappedSourceIds.map(
      (sourceId) =>
        "data/shared/remuneration-delegated/currentness-source-contract.json#" +
        sourceId,
    ),
    source_identity_matches_item_body_source: true,
    projection_gate: {
      kind: "EXPLICIT_BOUNDED_ALLOWLIST",
      allowed: true,
      identity:
        serviceId + "::" + DELEGATED_REMUNERATION_SOURCE_FAMILY,
      scope: "currentness_only",
    },
    source_version_contains_scope: true,
    ingestion_state: "INGESTED",
    item_body_state: "PASS",
    projected_currentness_state: "PASS",
    promotion_applied: true,
  };
}

test("delegated remuneration adapter publishes only canonical mapped nodes", () => {
  const promotion = delegatedPromotion("homevisit");
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
  assert.equal(records.length, 9);
  assert.deepEqual(
    records.map((record) => record.id),
    promotion.mapped_node_ids,
  );
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
    service_id: "homevisit",
    service_label: "訪問介護",
    source_family: DELEGATED_REMUNERATION_SOURCE_FAMILY,
    canonical_source_id:
      DELEGATED_REMUNERATION_CANONICAL_SOURCE_ID,
    source_title: promotion.source_identity.title,
    source_url: "",
    source_version: "",
    effective_date: "",
    checked_at:
      promotion.source_identity
        .current_official_display_observed_on,
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

test("delegated remuneration adapter fails closed for blocked, not-applicable, and drifted cells", () => {
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

  const blocked = delegatedPromotion("homevisit");
  blocked.projected_currentness_state = "NOT_ESTABLISHED";
  assert.equal(runtimeAdapterForPromotion(blocked), null);

  const unsupportedIdentity = delegatedPromotion("homevisit");
  unsupportedIdentity.source_identity.canonical_source_id =
    "unsupported-source";
  assert.equal(
    runtimeAdapterForPromotion(unsupportedIdentity),
    null,
  );

  const wrongFamily = delegatedPromotion("homevisit");
  wrongFamily.source_family =
    GOVERNING_STANDARDS_SOURCE_FAMILY;
  assert.equal(runtimeAdapterForPromotion(wrongFamily), null);

  const wrongNodes = delegatedPromotion("homevisit");
  wrongNodes.mapped_node_ids =
    wrongNodes.mapped_node_ids.slice(1);
  wrongNodes.mapped_node_count =
    wrongNodes.mapped_node_ids.length;
  assert.equal(runtimeAdapterForPromotion(wrongNodes), null);

  const wrongSources = delegatedPromotion("homevisit");
  wrongSources.mapped_source_ids = [
    "mhlw-fee-criteria95-current",
  ];
  assert.equal(
    runtimeAdapterForPromotion(wrongSources),
    null,
  );

  const missingCurrentnessEvidence =
    delegatedPromotion("homevisit");
  missingCurrentnessEvidence.source_currentness_evidence = [];
  assert.equal(
    runtimeAdapterForPromotion(missingCurrentnessEvidence),
    null,
  );
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

  const delegatedRelations =
    verifiedRelatedPrimarySources(
      "dayservice",
      DELEGATED_REMUNERATION_SOURCE_FAMILY,
      {
        id: "notice95.item.14-6",
        legacy_node_id:
          "criteria95.dayservice.14-6",
      },
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

  assert.deepEqual(
    verifiedRelatedPrimarySources(
      "dayservice",
      DELEGATED_REMUNERATION_SOURCE_FAMILY,
      {
        id: "notice95.item.14-3",
        legacy_node_id:
          "criteria95.dayservice.14-3",
      },
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
