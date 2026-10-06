import ordinanceMetaData from "../data/ordinance37-meta.json" with { type: "json" };
import ordinanceNodesData from "../data/ordinance37-nodes.json" with { type: "json" };
import preventiveMetaData from "../data/shared/standards/preventive-services-standards/meta.json" with { type: "json" };
import preventiveNodesData from "../data/shared/standards/preventive-services-standards/nodes.json" with { type: "json" };
import unitPriceRatesData from "../data/unit-price-dayservice.json" with { type: "json" };
import unitPriceMetaData from "../data/unit-price-dayservice-meta.json" with { type: "json" };
import unitPriceMappingsData from "../data/unit-price-service-multipliers.json" with { type: "json" };
import unitPriceItemBodyData from "../data/unit-price-item-body-assurance.json" with { type: "json" };

export const GOVERNING_STANDARDS_SOURCE_FAMILY = "governing_standards_ordinance";
export const UNIT_PRICE_SOURCE_FAMILY = "unit_price_regional_classification";

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
};

export type RuntimePromotion = {
  service_id?: string;
  source_family?: string;
  source_identity?: {
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
  applicability_proof?: {
    state?: string;
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
  recordKind: "RULE" | "UNIT_PRICE";
  supportsPromotion: (promotion: RuntimePromotion) => boolean;
  recordsForPromotion: (promotion: RuntimePromotion) => RuntimeSourceRecord[];
  recordIsPublished: (
    promotion: RuntimePromotion,
    record: RuntimeSourceRecord,
  ) => boolean;
  sourceTitle: (promotion: RuntimePromotion) => string;
  defaultSourceUrl: (promotion: RuntimePromotion) => string;
  applicabilityLabel: (serviceLabel: string) => string;
  currentnessLabel: string;
  projectItemBody: (record: RuntimeSourceRecord) => Record<string, unknown>;
  sourceText: (record: RuntimeSourceRecord) => string;
  sourceLocator: (
    record: RuntimeSourceRecord,
    promotion: RuntimePromotion,
  ) => { url: string; locator: string };
};

function normalizeRuleNodes(data: any): RuntimeSourceRecord[] {
  if (Array.isArray(data)) return data as RuntimeSourceRecord[];
  return Array.isArray(data?.nodes)
    ? (data.nodes as RuntimeSourceRecord[])
    : [];
}

function articleNumberFromRecordId(recordId: string, nodePrefix: string) {
  const escapedPrefix = nodePrefix.replace(/[.*+?^$()|[\]\\]/g, "\\$&");
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
  return value.split("-").map((part) => Number.parseInt(part, 10) || 0);
}

function compareArticleNumber(a: string, b: string) {
  const ak = articleKey(a);
  const bk = articleKey(b);
  for (let i = 0; i < Math.max(ak.length, bk.length); i += 1) {
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
  const proof = promotion.applicability_proof || {};
  if (mode === "TARGET_ARTICLES") {
    return new Set((proof.target_articles || []).map(String));
  }

  const selected = new Set<string>();
  for (const nodeId of proof.common_source_node_ids || []) {
    const article = articleNumberFromRecordId(String(nodeId), nodePrefix);
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
      ? articleNumberFromRecordId(range.from_node_id, nodePrefix)
      : null;
    const through = range.through_node_id
      ? articleNumberFromRecordId(range.through_node_id, nodePrefix)
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

function commonPromotionSafety(promotion: RuntimePromotion) {
  return (
    promotion.promotion_applied === true &&
    promotion.projected_currentness_state === "PASS" &&
    promotion.ingestion_state === "INGESTED" &&
    promotion.item_body_state === "PASS" &&
    promotion.source_version_contains_scope === true
  );
}

const ordinanceMeta = ordinanceMetaData as any;
const preventiveMeta = preventiveMetaData as any;
const ordinanceNodes = normalizeRuleNodes(ordinanceNodesData);
const preventiveNodes = normalizeRuleNodes(preventiveNodesData);

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

  const supportsPromotion = (promotion: RuntimePromotion) => {
    if (
      !commonPromotionSafety(promotion) ||
      promotion.source_family !== GOVERNING_STANDARDS_SOURCE_FAMILY
    ) {
      return false;
    }

    const source = promotion.source_identity || {};
    const proof = promotion.applicability_proof || {};
    const sourceLawId = String(source.law_id || "");
    const adapterLawId = String(meta?.law_id || "");
    const sourceVersion = String(source.version_id || "");
    const adapterVersion = String(
      meta?.current_revision?.law_revision_id || "",
    );

    if (
      source.canonical_source_id !== canonicalSourceId ||
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
      publishedRuleArticles(promotion, nodePrefix, scopeMode).size > 0
    );
  };

  const recordIsPublished = (
    promotion: RuntimePromotion,
    record: RuntimeSourceRecord,
  ) => {
    if (!supportsPromotion(promotion)) return false;
    const article =
      record.article_num ||
      articleNumberFromRecordId(String(record.id || ""), nodePrefix);
    return Boolean(
      article &&
        publishedRuleArticles(promotion, nodePrefix, scopeMode).has(
          String(article),
        ),
    );
  };

  return {
    canonicalSourceId,
    sourceFamily: GOVERNING_STANDARDS_SOURCE_FAMILY,
    recordKind: "RULE",
    supportsPromotion,
    recordsForPromotion: (promotion) =>
      supportsPromotion(promotion)
        ? nodes.filter((record) => recordIsPublished(promotion, record))
        : [],
    recordIsPublished,
    sourceTitle: () => String(meta?.law_title || ""),
    defaultSourceUrl: (promotion) =>
      String(
        promotion.source_identity?.official_source_url ||
          meta?.source_page ||
          "",
      ),
    applicabilityLabel: label,
    currentnessLabel: "現行のe-Gov本文を確認済み",
    projectItemBody: (record) => ({
      article_num: String(record.article_num || ""),
      article_title: String(record.article_title || ""),
      caption: String(record.caption || ""),
      label: String(record.label || ""),
      path: Array.isArray(record.path)
        ? record.path.map(String)
        : [],
    }),
    sourceText: (record) => String(record.official_text || ""),
    sourceLocator: (record, promotion) => ({
      url: String(
        record.source_url ||
          promotion.source_identity?.official_source_url ||
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

const dayserviceMapping = (unitPriceMappings.service_mappings || []).find(
  (row: any) => row.service_id === "dayservice",
);
const dayserviceProjection = (unitPriceItemBody.service_projections || []).find(
  (row: any) => row.service_id === "dayservice",
);
const dayserviceProfile = (unitPriceItemBody.profile_verification || []).find(
  (row: any) =>
    row.profile_id === dayserviceProjection?.multiplier_profile_id,
);
const dayserviceLocatorByRegion = new Map(
  (dayserviceProfile?.rows || []).map((row: any) => [
    String(row.region_class || ""),
    String(row.source_locator || ""),
  ]),
);
const unitPriceRecords = (unitPriceRatesData as Array<any>).map((row) => ({
  ...row,
  source_locator: dayserviceLocatorByRegion.get(
    String(row.region_class || ""),
  ),
})) as RuntimeSourceRecord[];

const unitPriceAdapter: RuntimeSourceAdapter = {
  canonicalSourceId: "mhlw-unit-price-current",
  sourceFamily: UNIT_PRICE_SOURCE_FAMILY,
  recordKind: "UNIT_PRICE",
  supportsPromotion: (promotion) => {
    if (
      !commonPromotionSafety(promotion) ||
      promotion.service_id !== "dayservice" ||
      promotion.source_family !== UNIT_PRICE_SOURCE_FAMILY
    ) {
      return false;
    }

    const source = promotion.source_identity || {};
    const proof = promotion.applicability_proof || {};
    if (
      source.canonical_source_id !== "mhlw-unit-price-current" ||
      source.currentness_class !== "CURRENT_OFFICIAL_CONSOLIDATED" ||
      !source.version_id ||
      source.effective_date !==
        unitPriceItemBody?.source_identity?.effective_reference_date
    ) {
      return false;
    }

    const expectedUrls = (unitPriceMeta.source_urls || []).map(String);
    const expectedHashes = (unitPriceMeta.source_sha256 || []).map(String);
    if (
      JSON.stringify(source.official_page_urls || []) !==
        JSON.stringify(expectedUrls) ||
      JSON.stringify(source.expected_page_sha256 || []) !==
        JSON.stringify(expectedHashes)
    ) {
      return false;
    }

    if (
      !dayserviceMapping ||
      dayserviceMapping.applicability !== "APPLIES" ||
      dayserviceMapping.official_service_name !== "通所介護" ||
      !dayserviceProjection ||
      dayserviceProjection.service_level_item_body !== "PASS" ||
      dayserviceProjection.applicability !== "APPLIES" ||
      dayserviceProjection.multiplier_profile_id !==
        dayserviceMapping.multiplier_profile_id
    ) {
      return false;
    }

    if (
      proof.state !== "PASS_DIRECT_SERVICE_SCOPE" ||
      proof.official_service_name !==
        dayserviceMapping.official_service_name ||
      proof.multiplier_profile_id !==
        dayserviceMapping.multiplier_profile_id ||
      proof.mapped_item_count !==
        dayserviceProjection.mapped_item_count ||
      proof.source_locator !== dayserviceProjection.source_locator
    ) {
      return false;
    }

    return (
      unitPriceRecords.length === dayserviceProjection.mapped_item_count &&
      unitPriceRecords.every(
        (record) =>
          record.source_id === "mhlw-unit-price-current" &&
          Boolean(record.source_locator),
      )
    );
  },
  recordsForPromotion: (promotion) =>
    unitPriceAdapter.supportsPromotion(promotion)
      ? [...unitPriceRecords]
      : [],
  recordIsPublished: (promotion, record) =>
    unitPriceAdapter.supportsPromotion(promotion) &&
    unitPriceRecords.some((candidate) => candidate.id === record.id),
  sourceTitle: (promotion) =>
    String(
      promotion.source_identity?.title ||
        "厚生労働大臣が定める一単位の単価",
    ),
  defaultSourceUrl: (promotion) =>
    String(promotion.source_identity?.official_source_url || ""),
  applicabilityLabel: (serviceLabel) =>
    serviceLabel + "の直接適用行として確認済み",
  currentnessLabel: "厚生労働省の現行統合表示を確認済み",
  projectItemBody: (record) => ({
    region_class: String(record.region_class || ""),
    service: String(record.service || ""),
    ratio_text: String(record.ratio_text || ""),
    ratio_per_thousand: Number(record.ratio_per_thousand),
    unit_price_yen: Number(record.unit_price_yen),
  }),
  sourceText: (record) => String(record.ratio_text || ""),
  sourceLocator: (record, promotion) => ({
    url: String(promotion.source_identity?.official_source_url || ""),
    locator: String(
      record.source_locator ||
        promotion.applicability_proof?.source_locator ||
        "",
    ),
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
    applicabilityState: "PASS_DIRECT_SERVICE_CHAPTER",
    verifiedFlag: "direct_service_chapter_verified",
    scopeMode: "TARGET_ARTICLES",
    label: (serviceLabel) =>
      serviceLabel + "の直接適用章に含まれる条文として確認済み",
  }),
  "preventive-services-standards": ruleAdapter({
    canonicalSourceId: "preventive-services-standards",
    meta: preventiveMeta,
    nodes: preventiveNodes,
    nodePrefix: "standards35",
    applicabilityState: "PASS_DIRECT_SERVICE_SCOPE",
    verifiedFlag: "direct_service_scope_verified",
    scopeMode: "RANGES",
    label: (serviceLabel) =>
      serviceLabel + "の直接適用範囲に含まれる条文として確認済み",
  }),
  "mhlw-unit-price-current": unitPriceAdapter,
};

export function runtimeAdapterForPromotion(
  promotion: RuntimePromotion | undefined,
) {
  const canonicalSourceId = String(
    promotion?.source_identity?.canonical_source_id || "",
  );
  const adapter = RUNTIME_SOURCE_ADAPTERS[canonicalSourceId];
  if (!promotion || !adapter || !adapter.supportsPromotion(promotion)) {
    return null;
  }
  if (promotion.source_family !== adapter.sourceFamily) return null;
  return adapter;
}

export function runtimeSupportedSourceIdentities() {
  return Object.keys(RUNTIME_SOURCE_ADAPTERS).sort();
}

export function runtimeSupportedSourceFamilies() {
  return [
    ...new Set(
      Object.values(RUNTIME_SOURCE_ADAPTERS).map(
        (adapter) => adapter.sourceFamily,
      ),
    ),
  ].sort();
}

export function isSupportedRuntimePromotion(
  promotion: RuntimePromotion | undefined,
) {
  return Boolean(runtimeAdapterForPromotion(promotion));
}

export function runtimeRecordsForPromotion(
  promotion: RuntimePromotion | undefined,
) {
  const adapter = runtimeAdapterForPromotion(promotion);
  return adapter && promotion
    ? adapter.recordsForPromotion(promotion)
    : [];
}

export function isRuntimeRecordPublished(
  promotion: RuntimePromotion | undefined,
  record: RuntimeSourceRecord,
) {
  const adapter = runtimeAdapterForPromotion(promotion);
  return Boolean(
    adapter &&
      promotion &&
      adapter.recordIsPublished(promotion, record),
  );
}

export function projectRuntimeRecord(
  promotion: RuntimePromotion | undefined,
  trust: RuntimeProjectionTrust,
  record: RuntimeSourceRecord,
) {
  const adapter = runtimeAdapterForPromotion(promotion);
  if (
    !adapter ||
    !promotion ||
    !adapter.recordIsPublished(promotion, record)
  ) {
    return null;
  }

  return {
    source_text: adapter.sourceText(record),
    item_body: adapter.projectItemBody(record),
    source_metadata: {
      service_id: trust.service_id,
      service_label: trust.service_label,
      source_family: trust.source_family,
      canonical_source_id: trust.canonical_source_id,
      source_title: trust.source_title,
      source_version: trust.source_version,
      effective_date: trust.effective_date,
    },
    source_locator: adapter.sourceLocator(record, promotion),
    currentness_statement: {
      label: adapter.currentnessLabel,
      effective_date: trust.effective_date,
      checked_at: trust.checked_at,
    },
    service_applicability_statement: {
      label: adapter.applicabilityLabel(trust.service_label),
    },
  };
}
