import delegatedManifestData from "../../data/shared/remuneration-delegated/manifest.json" with { type: "json" };
import delegatedCorpusData from "../../data/shared/remuneration-delegated/national-corpus.json" with { type: "json" };
import delegatedApplicabilityData from "../../data/shared/remuneration-delegated/service-applicability.json" with { type: "json" };
import delegatedItemBodyData from "../../data/shared/remuneration-delegated/item-body-verification.json" with { type: "json" };
import delegatedLegacyNodesData from "../../data/remuneration-delegated-nodes.json" with { type: "json" };
import {
  DELEGATED_REMUNERATION_CANONICAL_SOURCE_ID,
  DELEGATED_REMUNERATION_SOURCE_FAMILY,
  commonPromotionSafety,
  sourceIdentity,
  type RuntimePromotion,
  type RuntimeSourceAdapter,
  type RuntimeSourceRecord,
} from "./types.ts";

const delegatedManifest = delegatedManifestData as any;
const delegatedCorpus = delegatedCorpusData as any;
const delegatedApplicability = delegatedApplicabilityData as any;
const delegatedItemBody = delegatedItemBodyData as any;
const delegatedLegacyNodes = delegatedLegacyNodesData as any[];

const delegatedNodeById = new Map<string, any>(
  (delegatedCorpus.nodes || []).map((node: any) => [
    String(node.canonical_node_id || ""),
    node,
  ]),
);
const delegatedLegacyNodeById = new Map<string, any>(
  delegatedLegacyNodes.map((node: any) => [
    String(node.id || ""),
    node,
  ]),
);
const delegatedDocumentById = new Map<string, any>(
  (delegatedCorpus.documents || []).map((document: any) => [
    String(document.source_id || ""),
    document,
  ]),
);

function delegatedServiceContract(serviceId: string) {
  const service = (delegatedApplicability.services || []).find(
    (row: any) => row.service_id === serviceId,
  );
  if (
    !service ||
    service.scope_state !== "SCOPE_DEFINED" ||
    service.applicability_state !== "MAPPED" ||
    service.ingestion_state !== "INGESTED" ||
    service.assurance?.item_body_verification !== "PASS"
  ) {
    return null;
  }

  const mappedNodeIds = (service.mapped_node_ids || []).map(String);
  if (
    !mappedNodeIds.length ||
    Number(service.mapped_node_count) !== mappedNodeIds.length ||
    !mappedNodeIds.every((nodeId: string) =>
      delegatedNodeById.has(nodeId),
    )
  ) {
    return null;
  }

  if (
    delegatedManifest.corpus_id !==
      DELEGATED_REMUNERATION_CANONICAL_SOURCE_ID ||
    delegatedManifest.source_family !==
      DELEGATED_REMUNERATION_SOURCE_FAMILY ||
    delegatedManifest.assurance?.item_body_verification !== "PASS" ||
    delegatedItemBody.assurance_boundaries?.item_body_verification !==
      "PASS"
  ) {
    return null;
  }

  return { service, mappedNodeIds };
}

function delegatedNodeText(node: any) {
  if (String(node.official_text || "").trim()) {
    return String(node.official_text);
  }
  const legacyNodeId = String(
    node.text_storage?.legacy_node_id || "",
  );
  if (!legacyNodeId) return "";
  return String(
    delegatedLegacyNodeById.get(legacyNodeId)?.official_text || "",
  );
}

function delegatedNodeLocator(node: any) {
  const pages = (node.source_locator?.pages || []).map(String);
  const heading = String(
    node.source_locator?.heading || node.heading || "",
  );
  return [
    pages.length
      ? "公式HTML " + pages.map((page: string) => "p." + page).join(", ")
      : "",
    heading,
  ]
    .filter(Boolean)
    .join(" / ");
}

function delegatedRecordsForService(
  serviceId: string,
): RuntimeSourceRecord[] {
  const contract = delegatedServiceContract(serviceId);
  if (!contract) return [];

  const records: RuntimeSourceRecord[] = [];
  for (const nodeId of contract.mappedNodeIds) {
    const node = delegatedNodeById.get(nodeId);
    if (!node) return [];

    const sourceId = String(node.source_id || "");
    const document = delegatedDocumentById.get(sourceId);
    const officialText = delegatedNodeText(node);
    if (
      !sourceId ||
      !document ||
      !String(document.official_url || "") ||
      !officialText ||
      !delegatedNodeLocator(node)
    ) {
      return [];
    }

    records.push({
      id: nodeId,
      canonical_node_id: nodeId,
      legacy_node_id: String(
        node.text_storage?.legacy_node_id || "",
      ),
      item_label: String(node.item_label || ""),
      heading: String(node.heading || ""),
      official_text: officialText,
      source_id: sourceId,
      source_document_title: String(document.title || ""),
      source_url: String(document.official_url || ""),
      source_locator: delegatedNodeLocator(node),
    });
  }

  return records;
}

function delegatedPromotionSupported(
  promotion: RuntimePromotion,
) {
  if (
    !commonPromotionSafety(promotion) ||
    promotion.source_version_contains_scope !== true ||
    promotion.source_family !==
      DELEGATED_REMUNERATION_SOURCE_FAMILY
  ) {
    return false;
  }

  const source = sourceIdentity(promotion);
  if (
    source.canonical_source_id !==
      DELEGATED_REMUNERATION_CANONICAL_SOURCE_ID
  ) {
    return false;
  }

  const serviceId = String(promotion.service_id || "");
  const contract = delegatedServiceContract(serviceId);
  if (!contract) return false;

  const promotedNodeIds = (
    promotion.mapped_node_ids || []
  ).map(String);
  if (
    promotion.mapped_node_count !==
      contract.mappedNodeIds.length ||
    promotedNodeIds.length !==
      contract.mappedNodeIds.length ||
    promotedNodeIds.some(
      (nodeId, index) =>
        nodeId !== contract.mappedNodeIds[index],
    )
  ) {
    return false;
  }

  const records = delegatedRecordsForService(serviceId);
  if (
    records.length !== contract.mappedNodeIds.length ||
    !records.every(
      (record) =>
        Boolean(record.official_text) &&
        Boolean(record.source_url) &&
        Boolean(record.source_locator),
    )
  ) {
    return false;
  }

  const expectedSourceIds = [
    ...new Set(
      records
        .map((record) => String(record.source_id || ""))
        .filter(Boolean),
    ),
  ].sort();
  const promotedSourceIds = (
    promotion.mapped_source_ids || []
  )
    .map(String)
    .sort();
  if (
    expectedSourceIds.length !== promotedSourceIds.length ||
    expectedSourceIds.some(
      (sourceId, index) =>
        sourceId !== promotedSourceIds[index],
    )
  ) {
    return false;
  }

  const proof =
    promotion.applicability_proof ||
    promotion.service_applicability_evidence ||
    {};
  const gate = promotion.projection_gate || {};
  if (
    proof.state !==
      "PASS_EXPLICIT_CANONICAL_SERVICE_MAPPING" ||
    proof.inherited_from_sibling_service !== false ||
    promotion.source_identity_matches_item_body_source !==
      true ||
    gate.kind !== "EXPLICIT_BOUNDED_ALLOWLIST" ||
    gate.allowed !== true ||
    gate.identity !==
      serviceId +
        "::" +
        DELEGATED_REMUNERATION_SOURCE_FAMILY ||
    gate.scope !== "currentness_only"
  ) {
    return false;
  }

  const currentnessEvidence = (
    promotion.source_currentness_evidence || []
  ).map(String);
  return expectedSourceIds.every((sourceId) =>
    currentnessEvidence.some((evidence) =>
      evidence.endsWith("#" + sourceId),
    ),
  );
}

export const DELEGATED_REMUNERATION_ADAPTER: RuntimeSourceAdapter = {
  canonicalSourceId:
    DELEGATED_REMUNERATION_CANONICAL_SOURCE_ID,
  sourceFamily: DELEGATED_REMUNERATION_SOURCE_FAMILY,
  nodePrefix: "delegated-remuneration",
  recordKind: "DELEGATED_CRITERIA",
  supportsPromotion: delegatedPromotionSupported,
  recordsForPromotion: (promotion) =>
    delegatedPromotionSupported(promotion)
      ? delegatedRecordsForService(
          String(promotion.service_id || ""),
        )
      : [],
  recordIsPublished: (promotion, record) =>
    delegatedPromotionSupported(promotion) &&
    delegatedRecordsForService(
      String(promotion.service_id || ""),
    ).some((candidate) => candidate.id === record.id),
  sourceTitle: (promotion) =>
    String(
      sourceIdentity(promotion).title ||
        "介護報酬の算定方法・厚生労働大臣基準（別告示）",
    ),
  defaultSourceUrl: (promotion) =>
    String(
      sourceIdentity(promotion).official_source_url ||
        delegatedCorpus.documents?.[0]?.official_url ||
        "",
    ),
  applicabilityLabel: (serviceLabel) =>
    serviceLabel +
    "について、共有コーパスの収載対象を確認済み",
  currentnessLabel:
    "厚生労働省の現行資料との照合を確認済み",
  projectItemBody: (record) => ({
    canonical_node_id: String(
      record.canonical_node_id || record.id,
    ),
    item_label: String(record.item_label || ""),
    heading: String(record.heading || ""),
    source_id: String(record.source_id || ""),
    source_document_title: String(
      record.source_document_title || "",
    ),
  }),
  sourceText: (record) =>
    String(record.official_text || ""),
  sourceLocator: (record) => ({
    url: String(record.source_url || ""),
    locator: String(record.source_locator || ""),
  }),
};
