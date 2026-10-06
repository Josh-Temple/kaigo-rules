import ordinanceMetaData from "../data/ordinance37-meta.json" with { type: "json" };
import ordinanceNodesData from "../data/ordinance37-nodes.json" with { type: "json" };
import preventiveMetaData from "../data/shared/standards/preventive-services-standards/meta.json" with { type: "json" };
import preventiveNodesData from "../data/shared/standards/preventive-services-standards/nodes.json" with { type: "json" };
import unitPriceMetaData from "../data/unit-price-dayservice-meta.json" with { type: "json" };
import unitPriceMappingsData from "../data/unit-price-service-multipliers.json" with { type: "json" };
import unitPriceItemBodyData from "../data/unit-price-item-body-assurance.json" with { type: "json" };
import delegatedManifestData from "../data/shared/remuneration-delegated/manifest.json" with { type: "json" };
import delegatedCorpusData from "../data/shared/remuneration-delegated/national-corpus.json" with { type: "json" };
import delegatedApplicabilityData from "../data/shared/remuneration-delegated/service-applicability.json" with { type: "json" };
import delegatedItemBodyData from "../data/shared/remuneration-delegated/item-body-verification.json" with { type: "json" };
import delegatedLegacyNodesData from "../data/remuneration-delegated-nodes.json" with { type: "json" };

export const GOVERNING_STANDARDS_SOURCE_FAMILY =
  "governing_standards_ordinance";
export const UNIT_PRICE_SOURCE_FAMILY =
  "unit_price_regional_classification";
export const DELEGATED_REMUNERATION_SOURCE_FAMILY =
  "delegated_remuneration_criteria";
export const DELEGATED_REMUNERATION_CANONICAL_SOURCE_ID =
  "delegated-remuneration-national";

export type RuntimeSourceRecord = {
  id: string;
  node_type?: string;
  article_num?: string;
  article_title?: string;
  caption?: string;
  label?: string;
  path?: string[];
  official_text?: string;
  source_url?: string;
  source_locator?: string;
  region_class?: string;
  service?: string;
  ratio_text?: string;
  ratio_per_thousand?: number;
  unit_price_yen?: number;
  source_id?: string;
  canonical_node_id?: string;
  legacy_node_id?: string;
  item_label?: string;
  heading?: string;
  source_document_title?: string;
};

type RuntimeSourceIdentity = {
  canonical_source_id?: string;
  law_id?: string;
  title?: string;
  official_source_url?: string;
  official_page_urls?: string[];
  version_id?: string;
  effective_date?: string;
  verified_at?: string;
  current_official_display_observed_on?: string;
  currentness_class?: string;
  expected_page_sha256?: string[];
};

type RuntimeApplicabilityProof = {
  state?: string;
  inherited_from_sibling_service?: boolean;
  direct_service_chapter_verified?: boolean;
  direct_service_scope_verified?: boolean;
  target_articles?: string[];
  common_source_node_ids?: string[];
  primary_range?: {
    from_node_id?: string;
    through_node_id?: string;
    include_inserted_articles?: boolean;
  };
  variant_ranges?: Array<{
    from_node_id?: string;
    through_node_id?: string;
  }>;
  discrepancies?: number;
  official_service_name?: string;
  multiplier_profile_id?: string;
  source_locator?: string;
  mapped_item_count?: number;
};

export type RuntimePromotion = {
  service_id?: string;
  source_family?: string;
  source_identity?: RuntimeSourceIdentity;
  canonical_source_identity?: RuntimeSourceIdentity;
  applicability_proof?: RuntimeApplicabilityProof;
  service_applicability_evidence?: RuntimeApplicabilityProof;
  currentness_evidence?: {
    official_source_locator?: string;
    observed_on?: string;
    effective_date?: string;
    supersession_check?: string;
    live_verifier?: string;
    workflow?: string;
  };
  allowed_publication_units?: string[];
  mapped_node_count?: number;
  mapped_node_ids?: string[];
  mapped_source_ids?: string[];
  source_currentness_evidence?: string[];
  source_identity_matches_item_body_source?: boolean;
  projection_gate?: {
    kind?: string;
    allowed?: boolean;
    identity?: string;
    scope?: string;
  };
  source_version_contains_scope?: boolean;
  ingestion_state?: string;
  item_body_state?: string;
  projected_currentness_state?: string;
  promotion_applied?: boolean;
};

export type RuntimeProjectionTrust = {
  service_id: string;
  service_label: string;
  source_family: string;
  canonical_source_id: string;
  source_title: string;
  source_url: string;
  source_version: string;
  effective_date: string;
  checked_at: string;
};

export type RuntimeSourceAdapter = {
  canonicalSourceId: string;
  sourceFamily: string;
  recordKind: "RULE" | "UNIT_PRICE" | "DELEGATED_CRITERIA";
  supportsPromotion: (promotion: RuntimePromotion) => boolean;
  recordsForPromotion: (
    promotion: RuntimePromotion,
  ) => RuntimeSourceRecord[];
  recordIsPublished: (
    promotion: RuntimePromotion,
    record: RuntimeSourceRecord,
  ) => boolean;
  sourceTitle: (promotion: RuntimePromotion) => string;
  defaultSourceUrl: (promotion: RuntimePromotion) => string;
  applicabilityLabel: (serviceLabel: string) => string;
  currentnessLabel: string;
  projectItemBody: (
    record: RuntimeSourceRecord,
  ) => Record<string, unknown>;
  sourceText: (record: RuntimeSourceRecord) => string;
  sourceLocator: (
    record: RuntimeSourceRecord,
    promotion: RuntimePromotion,
  ) => { url: string; locator: string };
};

const SAFE_UNIT_PRICE_PUBLICATION_UNITS = [
  "SOURCE_TEXT_ITEM_BODY",
  "SOURCE_METADATA_LOCATOR",
  "CURRENTNESS_STATEMENT",
  "SERVICE_APPLICABILITY_STATEMENT",
];

function sourceIdentity(promotion: RuntimePromotion) {
  return (
    promotion.source_identity ||
    promotion.canonical_source_identity ||
    {}
  );
}

function applicabilityProof(promotion: RuntimePromotion) {
  return (
    promotion.applicability_proof ||
    promotion.service_applicability_evidence ||
    {}
  );
}

function normalizeRuleNodes(data: any): RuntimeSourceRecord[] {
  if (Array.isArray(data)) return data as RuntimeSourceRecord[];
  return Array.isArray(data?.nodes)
    ? (data.nodes as RuntimeSourceRecord[])
    : [];
}

function articleNumberFromRecordId(
  recordId: string,
  nodePrefix: string,
) {
  const escapedPrefix = nodePrefix.replace(
    /[.*+?^$()|[\]\\]/g,
    "\\$&",
  );
  const match = recordId.match(
    new RegExp(
      "^" +
        escapedPrefix +
        "\\.article\\.([0-9]+(?:-[0-9]+)?)(?:\\.|$)",
    ),
  );
  return match?.[1] || null;
}

function articleKey(value: string) {
  return value
    .split("-")
    .map((part) => Number.parseInt(part, 10) || 0);
}

function compareArticleNumber(a: string, b: string) {
  const ak = articleKey(a);
  const bk = articleKey(b);
  for (
    let i = 0;
    i < Math.max(ak.length, bk.length);
    i += 1
  ) {
    const diff = (ak[i] || 0) - (bk[i] || 0);
    if (diff) return diff;
  }
  return 0;
}

function publishedRuleArticles(
  promotion: RuntimePromotion,
  nodePrefix: string,
  mode: "TARGET_ARTICLES" | "RANGES",
) {
  const proof = applicabilityProof(promotion);
  if (mode === "TARGET_ARTICLES") {
    return new Set(
      (proof.target_articles || []).map(String),
    );
  }

  const selected = new Set<string>();
  for (const nodeId of proof.common_source_node_ids || []) {
    const article = articleNumberFromRecordId(
      String(nodeId),
      nodePrefix,
    );
    if (article) selected.add(article);
  }

  const ranges = [
    proof.primary_range,
    ...(proof.variant_ranges || []),
  ].filter(Boolean) as Array<{
    from_node_id?: string;
    through_node_id?: string;
  }>;

  const nodes =
    nodePrefix === "standards35"
      ? normalizeRuleNodes(preventiveNodesData)
      : normalizeRuleNodes(ordinanceNodesData);

  for (const range of ranges) {
    const from = range.from_node_id
      ? articleNumberFromRecordId(
          range.from_node_id,
          nodePrefix,
        )
      : null;
    const through = range.through_node_id
      ? articleNumberFromRecordId(
          range.through_node_id,
          nodePrefix,
        )
      : null;
    if (!from || !through) continue;
    for (const node of nodes) {
      if (node.node_type !== "article") continue;
      const article = String(node.article_num || "");
      if (
        article &&
        compareArticleNumber(article, from) >= 0 &&
        compareArticleNumber(article, through) <= 0
      ) {
        selected.add(article);
      }
    }
  }

  return selected;
}

function commonPromotionSafety(
  promotion: RuntimePromotion,
) {
  return (
    promotion.promotion_applied === true &&
    promotion.projected_currentness_state === "PASS" &&
    promotion.ingestion_state === "INGESTED" &&
    promotion.item_body_state === "PASS"
  );
}

const ordinanceMeta = ordinanceMetaData as any;
const preventiveMeta = preventiveMetaData as any;
const ordinanceNodes = normalizeRuleNodes(ordinanceNodesData);
const preventiveNodes =
  normalizeRuleNodes(preventiveNodesData);

function ruleAdapter(args: {
  canonicalSourceId: string;
  meta: any;
  nodes: RuntimeSourceRecord[];
  nodePrefix: string;
  applicabilityState: string;
  verifiedFlag:
    | "direct_service_chapter_verified"
    | "direct_service_scope_verified";
  scopeMode: "TARGET_ARTICLES" | "RANGES";
  label: (serviceLabel: string) => string;
}): RuntimeSourceAdapter {
  const {
    canonicalSourceId,
    meta,
    nodes,
    nodePrefix,
    applicabilityState,
    verifiedFlag,
    scopeMode,
    label,
  } = args;

  const supportsPromotion = (
    promotion: RuntimePromotion,
  ) => {
    if (
      !commonPromotionSafety(promotion) ||
      promotion.source_version_contains_scope !== true ||
      promotion.source_family !==
        GOVERNING_STANDARDS_SOURCE_FAMILY
    ) {
      return false;
    }

    const source = sourceIdentity(promotion);
    const proof = applicabilityProof(promotion);
    const sourceLawId = String(source.law_id || "");
    const adapterLawId = String(meta?.law_id || "");
    const sourceVersion = String(
      source.version_id || "",
    );
    const adapterVersion = String(
      meta?.current_revision?.law_revision_id || "",
    );

    if (
      source.canonical_source_id !==
        canonicalSourceId ||
      !sourceLawId ||
      !adapterLawId ||
      sourceLawId !== adapterLawId ||
      !sourceVersion ||
      !adapterVersion ||
      sourceVersion !== adapterVersion
    ) {
      return false;
    }

    if (
      proof.state !== applicabilityState ||
      proof[verifiedFlag] !== true ||
      proof.discrepancies !== 0
    ) {
      return false;
    }

    return (
      publishedRuleArticles(
        promotion,
        nodePrefix,
        scopeMode,
      ).size > 0
    );
  };

  const recordIsPublished = (
    promotion: RuntimePromotion,
    record: RuntimeSourceRecord,
  ) => {
    if (!supportsPromotion(promotion)) return false;
    const article =
      record.article_num ||
      articleNumberFromRecordId(
        String(record.id || ""),
        nodePrefix,
      );
    return Boolean(
      article &&
        publishedRuleArticles(
          promotion,
          nodePrefix,
          scopeMode,
        ).has(String(article)),
    );
  };

  return {
    canonicalSourceId,
    sourceFamily: GOVERNING_STANDARDS_SOURCE_FAMILY,
    recordKind: "RULE",
    supportsPromotion,
    recordsForPromotion: (promotion) =>
      supportsPromotion(promotion)
        ? nodes.filter((record) =>
            recordIsPublished(promotion, record),
          )
        : [],
    recordIsPublished,
    sourceTitle: () =>
      String(meta?.law_title || ""),
    defaultSourceUrl: (promotion) =>
      String(
        sourceIdentity(promotion).official_source_url ||
          meta?.source_page ||
          "",
      ),
    applicabilityLabel: label,
    currentnessLabel:
      "現行のe-Gov本文を確認済み",
    projectItemBody: (record) => ({
      article_num: String(record.article_num || ""),
      article_title: String(
        record.article_title || "",
      ),
      caption: String(record.caption || ""),
      label: String(record.label || ""),
      path: Array.isArray(record.path)
        ? record.path.map(String)
        : [],
    }),
    sourceText: (record) =>
      String(record.official_text || ""),
    sourceLocator: (record, promotion) => ({
      url: String(
        record.source_url ||
          sourceIdentity(promotion)
            .official_source_url ||
          meta?.source_page ||
          "",
      ),
      locator: String(record.source_locator || ""),
    }),
  };
}

const unitPriceMeta = unitPriceMetaData as any;
const unitPriceMappings = unitPriceMappingsData as any;
const unitPriceItemBody = unitPriceItemBodyData as any;

function unitPriceServiceContract(
  serviceId: string,
) {
  const mapping = (
    unitPriceMappings.service_mappings || []
  ).find(
    (row: any) => row.service_id === serviceId,
  );
  const projection = (
    unitPriceItemBody.service_projections || []
  ).find(
    (row: any) => row.service_id === serviceId,
  );
  if (
    !mapping ||
    mapping.applicability !== "APPLIES" ||
    !projection ||
    projection.applicability !== "APPLIES" ||
    projection.service_level_item_body !== "PASS" ||
    projection.multiplier_profile_id !==
      mapping.multiplier_profile_id
  ) {
    return null;
  }

  const profile = (
    unitPriceItemBody.profile_verification || []
  ).find(
    (row: any) =>
      row.profile_id ===
      projection.multiplier_profile_id,
  );
  if (
    !profile ||
    profile.verification_state !== "PASS" ||
    profile.mapped_item_count !== 8 ||
    !Array.isArray(profile.rows) ||
    profile.rows.length !== 8
  ) {
    return null;
  }

  return { mapping, projection, profile };
}

function unitPriceRecordsForService(
  serviceId: string,
): RuntimeSourceRecord[] {
  const contract =
    unitPriceServiceContract(serviceId);
  if (!contract) return [];

  return contract.profile.rows.map(
    (row: any, index: number) => ({
      id:
        "unitprice." +
        serviceId +
        "." +
        (index === 7 ? "other" : String(index + 1)),
      region_class: String(row.region_class || ""),
      service: String(
        contract.mapping.official_service_name || "",
      ),
      ratio_text:
        String(row.ratio_per_thousand) + "/1000",
      ratio_per_thousand: Number(
        row.ratio_per_thousand,
      ),
      unit_price_yen: Number(row.unit_price_yen),
      source_id: "mhlw-unit-price-current",
      source_locator: String(
        row.source_locator || "",
      ),
    }),
  );
}

function unitPriceCurrentnessEvidenceIsSafe(
  promotion: RuntimePromotion,
) {
  if (
    promotion.source_version_contains_scope === true
  ) {
    return true;
  }

  const evidence = promotion.currentness_evidence;
  const units = new Set(
    promotion.allowed_publication_units || [],
  );
  return Boolean(
    evidence &&
      evidence.supersession_check ===
        "OFFICIAL_MHLW_CONSOLIDATED_DISPLAY_REVERIFIED" &&
      evidence.live_verifier ===
        "scripts/verify_unit_price_currentness.py" &&
      evidence.effective_date === "2024-04-01" &&
      SAFE_UNIT_PRICE_PUBLICATION_UNITS.every(
        (unit) => units.has(unit),
      ),
  );
}

function unitPricePromotionSupported(
  promotion: RuntimePromotion,
) {
  if (
    !commonPromotionSafety(promotion) ||
    !unitPriceCurrentnessEvidenceIsSafe(
      promotion,
    ) ||
    promotion.source_family !==
      UNIT_PRICE_SOURCE_FAMILY
  ) {
    return false;
  }

  const serviceId = String(
    promotion.service_id || "",
  );
  const contract =
    unitPriceServiceContract(serviceId);
  if (!contract) return false;

  const source = sourceIdentity(promotion);
  const proof = applicabilityProof(promotion);
  if (
    source.canonical_source_id !==
      "mhlw-unit-price-current" ||
    source.currentness_class !==
      "CURRENT_OFFICIAL_CONSOLIDATED" ||
    !source.version_id ||
    source.effective_date !==
      unitPriceItemBody?.source_identity
        ?.effective_reference_date
  ) {
    return false;
  }

  const expectedUrls = (
    unitPriceMeta.source_urls || []
  ).map(String);
  if (
    JSON.stringify(source.official_page_urls || []) !==
    JSON.stringify(expectedUrls)
  ) {
    return false;
  }

  const expectedHashes = (
    unitPriceMeta.source_sha256 || []
  ).map(String);
  if (
    source.expected_page_sha256 &&
    JSON.stringify(source.expected_page_sha256) !==
      JSON.stringify(expectedHashes)
  ) {
    return false;
  }

  if (
    proof.state !== "PASS_DIRECT_SERVICE_SCOPE" ||
    proof.official_service_name !==
      contract.mapping.official_service_name ||
    proof.multiplier_profile_id !==
      contract.mapping.multiplier_profile_id ||
    proof.mapped_item_count !==
      contract.projection.mapped_item_count ||
    proof.source_locator !==
      contract.projection.source_locator
  ) {
    return false;
  }

  const records =
    unitPriceRecordsForService(serviceId);
  return (
    records.length ===
      contract.projection.mapped_item_count &&
    records.every(
      (record) =>
        record.source_id ===
          "mhlw-unit-price-current" &&
        Boolean(record.source_locator),
    )
  );
}

const unitPriceAdapter: RuntimeSourceAdapter = {
  canonicalSourceId: "mhlw-unit-price-current",
  sourceFamily: UNIT_PRICE_SOURCE_FAMILY,
  recordKind: "UNIT_PRICE",
  supportsPromotion: unitPricePromotionSupported,
  recordsForPromotion: (promotion) =>
    unitPricePromotionSupported(promotion)
      ? unitPriceRecordsForService(
          String(promotion.service_id || ""),
        )
      : [],
  recordIsPublished: (promotion, record) =>
    unitPricePromotionSupported(promotion) &&
    unitPriceRecordsForService(
      String(promotion.service_id || ""),
    ).some(
      (candidate) => candidate.id === record.id,
    ),
  sourceTitle: (promotion) =>
    String(
      sourceIdentity(promotion).title ||
        "厚生労働大臣が定める一単位の単価",
    ),
  defaultSourceUrl: (promotion) =>
    String(
      sourceIdentity(promotion)
        .official_source_url || "",
    ),
  applicabilityLabel: (serviceLabel) =>
    serviceLabel + "の直接適用行として確認済み",
  currentnessLabel:
    "厚生労働省の現行統合表示を確認済み",
  projectItemBody: (record) => ({
    region_class: String(
      record.region_class || "",
    ),
    service: String(record.service || ""),
    ratio_text: String(record.ratio_text || ""),
    ratio_per_thousand: Number(
      record.ratio_per_thousand,
    ),
    unit_price_yen: Number(
      record.unit_price_yen,
    ),
  }),
  sourceText: (record) =>
    [
      record.region_class,
      record.service,
      record.ratio_text,
      record.unit_price_yen !== undefined
        ? record.unit_price_yen + "円"
        : "",
    ]
      .filter(Boolean)
      .join(" / "),
  sourceLocator: (record, promotion) => ({
    url: String(
      sourceIdentity(promotion)
        .official_source_url || "",
    ),
    locator: String(
      record.source_locator ||
        applicabilityProof(promotion)
          .source_locator ||
        "",
    ),
  }),
};


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

const delegatedRemunerationAdapter: RuntimeSourceAdapter = {
  canonicalSourceId:
    DELEGATED_REMUNERATION_CANONICAL_SOURCE_ID,
  sourceFamily: DELEGATED_REMUNERATION_SOURCE_FAMILY,
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

export const RUNTIME_SOURCE_ADAPTERS: Record<
  string,
  RuntimeSourceAdapter
> = {
  ordinance37: ruleAdapter({
    canonicalSourceId: "ordinance37",
    meta: ordinanceMeta,
    nodes: ordinanceNodes,
    nodePrefix: "ordinance37",
    applicabilityState:
      "PASS_DIRECT_SERVICE_CHAPTER",
    verifiedFlag:
      "direct_service_chapter_verified",
    scopeMode: "TARGET_ARTICLES",
    label: (serviceLabel) =>
      serviceLabel +
      "の直接適用章に含まれる条文として確認済み",
  }),
  "preventive-services-standards": ruleAdapter({
    canonicalSourceId:
      "preventive-services-standards",
    meta: preventiveMeta,
    nodes: preventiveNodes,
    nodePrefix: "standards35",
    applicabilityState:
      "PASS_DIRECT_SERVICE_SCOPE",
    verifiedFlag:
      "direct_service_scope_verified",
    scopeMode: "RANGES",
    label: (serviceLabel) =>
      serviceLabel +
      "の直接適用範囲に含まれる条文として確認済み",
  }),
  "mhlw-unit-price-current": unitPriceAdapter,
  [DELEGATED_REMUNERATION_CANONICAL_SOURCE_ID]:
    delegatedRemunerationAdapter,
};

export function runtimeAdapterForPromotion(
  promotion: RuntimePromotion | undefined,
) {
  const canonicalSourceId = String(
    promotion
      ? sourceIdentity(promotion)
          .canonical_source_id || ""
      : "",
  );
  const adapter =
    RUNTIME_SOURCE_ADAPTERS[canonicalSourceId];
  if (
    !promotion ||
    !adapter ||
    !adapter.supportsPromotion(promotion)
  ) {
    return null;
  }
  if (
    promotion.source_family !==
    adapter.sourceFamily
  ) {
    return null;
  }
  return adapter;
}

export function runtimeSupportedSourceIdentities() {
  return Object.keys(
    RUNTIME_SOURCE_ADAPTERS,
  ).sort();
}

export function runtimeSupportedSourceFamilies() {
  return [
    ...new Set(
      Object.values(
        RUNTIME_SOURCE_ADAPTERS,
      ).map(
        (adapter) => adapter.sourceFamily,
      ),
    ),
  ].sort();
}

export function isSupportedRuntimePromotion(
  promotion: RuntimePromotion | undefined,
) {
  return Boolean(
    runtimeAdapterForPromotion(promotion),
  );
}

export function runtimeRecordsForPromotion(
  promotion: RuntimePromotion | undefined,
) {
  const adapter =
    runtimeAdapterForPromotion(promotion);
  return adapter && promotion
    ? adapter.recordsForPromotion(promotion)
    : [];
}

export function isRuntimeRecordPublished(
  promotion: RuntimePromotion | undefined,
  record: RuntimeSourceRecord,
) {
  const adapter =
    runtimeAdapterForPromotion(promotion);
  return Boolean(
    adapter &&
      promotion &&
      adapter.recordIsPublished(
        promotion,
        record,
      ),
  );
}

export function projectRuntimeRecord(
  promotion: RuntimePromotion | undefined,
  trust: RuntimeProjectionTrust,
  record: RuntimeSourceRecord,
) {
  const adapter =
    runtimeAdapterForPromotion(promotion);
  if (
    !adapter ||
    !promotion ||
    !adapter.recordIsPublished(
      promotion,
      record,
    )
  ) {
    return null;
  }

  return {
    source_text: adapter.sourceText(record),
    item_body:
      adapter.projectItemBody(record),
    source_metadata: {
      service_id: trust.service_id,
      service_label: trust.service_label,
      source_family: trust.source_family,
      canonical_source_id:
        trust.canonical_source_id,
      source_title: trust.source_title,
      source_version: trust.source_version,
      effective_date: trust.effective_date,
    },
    source_locator: adapter.sourceLocator(
      record,
      promotion,
    ),
    currentness_statement: {
      label: adapter.currentnessLabel,
      effective_date: trust.effective_date,
      checked_at: trust.checked_at,
    },
    service_applicability_statement: {
      label: adapter.applicabilityLabel(
        trust.service_label,
      ),
    },
  };
}
