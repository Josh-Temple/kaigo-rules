import allowlistData from "../data/bounded-publication-allowlist.json" with { type: "json" };
import readinessData from "../data/publication-readiness.generated.json" with { type: "json" };
import currentnessData from "../data/verification/bounded-currentness-closure-worker-b.json" with { type: "json" };
import ordinanceMetaData from "../data/ordinance37-meta.json" with { type: "json" };
import ordinanceNodesData from "../data/ordinance37-nodes.json" with { type: "json" };
import preventiveMetaData from "../data/shared/standards/preventive-services-standards/meta.json" with { type: "json" };
import preventiveNodesData from "../data/shared/standards/preventive-services-standards/nodes.json" with { type: "json" };

export const PROGRESSIVE_SOURCE_FAMILY = "governing_standards_ordinance";

export const REQUIRED_PUBLICATION_UNITS = [
  "SOURCE_TEXT_ITEM_BODY",
  "SOURCE_METADATA_LOCATOR",
  "CURRENTNESS_STATEMENT",
  "SERVICE_APPLICABILITY_STATEMENT",
] as const;

export const SAFE_PUBLICATION_FIELDS = [
  "source_text",
  "item_body",
  "source_metadata",
  "source_locator",
  "currentness_statement",
  "service_applicability_statement",
] as const;

type RuleNode = {
  id: string;
  node_type: string;
  article_num: string;
  article_title?: string;
  caption?: string;
  label?: string;
  path?: string[];
  official_text?: string;
  source_url?: string;
  source_locator?: string;
};

type PublicationCell = {
  service_id?: string;
  source_family?: string;
};

type ReadinessRow = {
  service_id?: string;
  service_label?: string;
  source_family?: string;
  readiness?: string;
  blocking_reasons?: string[];
  ready_publication_units?: string[];
};

type Promotion = {
  service_id?: string;
  source_family?: string;
  source_identity?: {
    canonical_source_id?: string;
    law_id?: string;
    official_source_url?: string;
    version_id?: string;
    effective_date?: string;
    verified_at?: string;
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
  };
  source_version_contains_scope?: boolean;
  ingestion_state?: string;
  item_body_state?: string;
  projected_currentness_state?: string;
  promotion_applied?: boolean;
};

const allowlist = allowlistData as any;
const readiness = readinessData as { cells?: ReadinessRow[] };
const currentness = currentnessData as { promotions?: Promotion[] };
const ordinanceMeta = ordinanceMetaData as any;
const preventiveMeta = preventiveMetaData as any;

type SourceAdapter = {
  canonicalSourceId: string;
  nodePrefix: string;
  meta: any;
  nodes: RuleNode[];
  applicabilityState: string;
  verifiedFlag: "direct_service_chapter_verified" | "direct_service_scope_verified";
  applicabilityLabel: (serviceLabel: string) => string;
};

function normalizeRuleNodes(data: any): RuleNode[] {
  if (Array.isArray(data)) return data as RuleNode[];
  return Array.isArray(data?.nodes) ? (data.nodes as RuleNode[]) : [];
}

const SOURCE_ADAPTERS: Record<string, SourceAdapter> = {
  ordinance37: {
    canonicalSourceId: "ordinance37",
    nodePrefix: "ordinance37",
    meta: ordinanceMeta,
    nodes: normalizeRuleNodes(ordinanceNodesData),
    applicabilityState: "PASS_DIRECT_SERVICE_CHAPTER",
    verifiedFlag: "direct_service_chapter_verified",
    applicabilityLabel: (serviceLabel) =>
      serviceLabel + "の直接適用章に含まれる条文として確認済み",
  },
  "preventive-services-standards": {
    canonicalSourceId: "preventive-services-standards",
    nodePrefix: "standards35",
    meta: preventiveMeta,
    nodes: normalizeRuleNodes(preventiveNodesData),
    applicabilityState: "PASS_DIRECT_SERVICE_SCOPE",
    verifiedFlag: "direct_service_scope_verified",
    applicabilityLabel: (serviceLabel) =>
      serviceLabel + "の直接適用範囲に含まれる条文として確認済み",
  },
};

const PREVENTIVE_COUNTERPARTS: Record<string, string> = {
  "preventive-homebath": "homebath",
  "preventive-homenursing": "homenursing",
  "preventive-homerehab": "homerehab",
  "preventive-homecaremanagement": "homecaremanagement",
  "preventive-dayrehab": "dayrehab",
  "preventive-shortstay-life": "shortstay-life",
  "preventive-shortstay-medical": "shortstay-medical",
  "preventive-specific-facility": "specific-facility",
  "preventive-welfare-equipment-rental": "welfare-equipment-rental",
  "specific-preventive-welfare-equipment-sale": "specific-welfare-equipment-sale",
};

export function publicationServicePresentationGroup(serviceId: string) {
  return PREVENTIVE_COUNTERPARTS[serviceId] || serviceId;
}

export function isPreventivePublicationService(serviceId: string) {
  return Object.prototype.hasOwnProperty.call(PREVENTIVE_COUNTERPARTS, serviceId);
}

export function isSupportedPublicationContract(
  canonicalSourceId: string,
  applicabilityState: string,
  verified: boolean,
) {
  const adapter = SOURCE_ADAPTERS[canonicalSourceId];
  return Boolean(
    adapter &&
      applicabilityState === adapter.applicabilityState &&
      verified === true,
  );
}

const cellKey = (serviceId: string, sourceFamily: string) =>
  `${serviceId}|${sourceFamily}`;

const publicationKeys = new Set<string>(
  (allowlist.publication_cell_allowlist || []).map((cell: PublicationCell) =>
    cellKey(String(cell.service_id || ""), String(cell.source_family || "")),
  ),
);

const routeKeys = new Set<string>(
  (allowlist.route_allowlist || []).map((cell: PublicationCell) =>
    cellKey(String(cell.service_id || ""), String(cell.source_family || "")),
  ),
);

const readinessByKey = new Map(
  (readiness.cells || []).map((row) => [
    cellKey(String(row.service_id || ""), String(row.source_family || "")),
    row,
  ]),
);

const promotionByKey = new Map(
  (currentness.promotions || []).map((row) => [
    cellKey(String(row.service_id || ""), String(row.source_family || "")),
    row,
  ]),
);

const runtimeBindingEstablished =
  allowlist.runtime_binding?.established === true;

function fieldsAreSafe(serviceId: string, sourceFamily: string) {
  const fields =
    allowlist.field_allowlist_by_cell?.[cellKey(serviceId, sourceFamily)];
  if (!Array.isArray(fields)) return false;
  const selected = new Set(fields.map(String));
  return (
    SAFE_PUBLICATION_FIELDS.every((field) => selected.has(field)) &&
    [...selected].every((field) =>
      (SAFE_PUBLICATION_FIELDS as readonly string[]).includes(field),
    )
  );
}

function readinessAllows(serviceId: string, sourceFamily: string) {
  const row = readinessByKey.get(cellKey(serviceId, sourceFamily));
  if (!row || row.readiness !== "READY_FOR_PUBLICATION_REVIEW") return false;
  if ((row.blocking_reasons || []).length) return false;
  const units = new Set(row.ready_publication_units || []);
  return REQUIRED_PUBLICATION_UNITS.every((unit) => units.has(unit));
}

function adapterForPromotion(row: Promotion | undefined) {
  const canonicalSourceId = String(row?.source_identity?.canonical_source_id || "");
  const adapter = SOURCE_ADAPTERS[canonicalSourceId];
  if (!adapter) return null;

  const sourceLawId = String(row?.source_identity?.law_id || "");
  const adapterLawId = String(adapter.meta?.law_id || "");
  if (!sourceLawId || !adapterLawId || sourceLawId !== adapterLawId) return null;

  const sourceVersion = String(row?.source_identity?.version_id || "");
  const adapterVersion = String(adapter.meta?.current_revision?.law_revision_id || "");
  if (!sourceVersion || !adapterVersion || sourceVersion !== adapterVersion) return null;

  const proof = row?.applicability_proof;
  const verified = Boolean(proof?.[adapter.verifiedFlag]);
  if (
    !isSupportedPublicationContract(
      canonicalSourceId,
      String(proof?.state || ""),
      verified,
    )
  ) return null;

  return adapter;
}

function promotionHasExplicitScope(row: Promotion, adapter: SourceAdapter) {
  const proof = row.applicability_proof;
  if (!proof) return false;
  if (adapter.canonicalSourceId === "ordinance37") {
    return Array.isArray(proof.target_articles) && proof.target_articles.length > 0;
  }
  return (
    (Array.isArray(proof.common_source_node_ids) &&
      proof.common_source_node_ids.length > 0) ||
    Boolean(proof.primary_range?.from_node_id && proof.primary_range?.through_node_id) ||
    Boolean(
      proof.variant_ranges?.some(
        (range) => range.from_node_id && range.through_node_id,
      ),
    )
  );
}

function promotionAllows(serviceId: string, sourceFamily: string) {
  const row = promotionByKey.get(cellKey(serviceId, sourceFamily));
  if (!row) return false;
  const adapter = adapterForPromotion(row);
  if (!adapter) return false;
  return (
    row.promotion_applied === true &&
    row.projected_currentness_state === "PASS" &&
    row.ingestion_state === "INGESTED" &&
    row.item_body_state === "PASS" &&
    row.source_version_contains_scope === true &&
    row.applicability_proof?.discrepancies === 0 &&
    promotionHasExplicitScope(row, adapter)
  );
}

export function isProgressivePublicationCell(
  serviceId: string,
  sourceFamily = PROGRESSIVE_SOURCE_FAMILY,
) {
  const key = cellKey(serviceId, sourceFamily);
  return (
    runtimeBindingEstablished &&
    publicationKeys.has(key) &&
    readinessAllows(serviceId, sourceFamily) &&
    fieldsAreSafe(serviceId, sourceFamily) &&
    promotionAllows(serviceId, sourceFamily)
  );
}

export function isProgressiveRouteCell(
  serviceId: string,
  sourceFamily = PROGRESSIVE_SOURCE_FAMILY,
) {
  return (
    isProgressivePublicationCell(serviceId, sourceFamily) &&
    routeKeys.has(cellKey(serviceId, sourceFamily))
  );
}

export function listProgressivePublicationServices() {
  return [...publicationKeys]
    .map((key) => readinessByKey.get(key))
    .filter((row): row is ReadinessRow => Boolean(row))
    .filter(
      (row) =>
        row.source_family === PROGRESSIVE_SOURCE_FAMILY &&
        Boolean(row.service_id) &&
        isProgressiveRouteCell(String(row.service_id), PROGRESSIVE_SOURCE_FAMILY),
    )
    .map((row) => ({
      service_id: String(row.service_id),
      label: String(row.service_label || row.service_id),
      source_family: PROGRESSIVE_SOURCE_FAMILY,
    }));
}

export function getProgressiveSourceRecords(serviceId: string): RuleNode[] {
  if (!isProgressiveRouteCell(serviceId, PROGRESSIVE_SOURCE_FAMILY)) return [];
  const promotion = promotionByKey.get(cellKey(serviceId, PROGRESSIVE_SOURCE_FAMILY));
  const adapter = adapterForPromotion(promotion);
  return adapter ? [...adapter.nodes] : [];
}


function articleNumberFromRecordId(recordId: string, nodePrefix: string) {
  const escapedPrefix = nodePrefix.replace(/[.*+?^$()|[\]\\]/g, "\\$&");
  const match = recordId.match(
    new RegExp("^" + escapedPrefix + "\\.article\\.([0-9]+(?:-[0-9]+)?)(?:\\.|$)"),
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

function articleFromBoundary(nodeId: string | undefined, adapter: SourceAdapter) {
  return nodeId ? articleNumberFromRecordId(nodeId, adapter.nodePrefix) : null;
}

function publishedArticleSet(serviceId: string) {
  if (!isProgressivePublicationCell(serviceId)) return new Set<string>();
  const promotion = promotionByKey.get(
    cellKey(serviceId, PROGRESSIVE_SOURCE_FAMILY),
  );
  const adapter = adapterForPromotion(promotion);
  if (!promotion || !adapter) return new Set<string>();

  const proof = promotion.applicability_proof || {};
  if (adapter.canonicalSourceId === "ordinance37") {
    return new Set((proof.target_articles || []).map(String));
  }

  const selected = new Set<string>();
  for (const nodeId of proof.common_source_node_ids || []) {
    const article = articleNumberFromRecordId(String(nodeId), adapter.nodePrefix);
    if (article) selected.add(article);
  }

  const ranges = [
    proof.primary_range,
    ...(proof.variant_ranges || []),
  ].filter(Boolean) as Array<{ from_node_id?: string; through_node_id?: string }>;

  for (const range of ranges) {
    const from = articleFromBoundary(range.from_node_id, adapter);
    const through = articleFromBoundary(range.through_node_id, adapter);
    if (!from || !through) continue;
    for (const node of adapter.nodes) {
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

export function isProgressiveRulePublished(
  serviceId: string,
  recordId: string,
) {
  if (!isProgressiveRouteCell(serviceId)) return false;
  const promotion = promotionByKey.get(
    cellKey(serviceId, PROGRESSIVE_SOURCE_FAMILY),
  );
  const adapter = adapterForPromotion(promotion);
  if (!adapter) return false;
  const article = articleNumberFromRecordId(recordId, adapter.nodePrefix);
  return Boolean(article && publishedArticleSet(serviceId).has(article));
}

export function filterProgressivePublishedRules<T>(
  serviceId: string,
  records: readonly T[],
  recordId: (record: T) => string,
): T[] {
  return records.filter((record) =>
    isProgressiveRulePublished(serviceId, recordId(record)),
  );
}

export function progressiveServicesForRule(recordId: string) {
  return listProgressivePublicationServices().filter((service) =>
    isProgressiveRulePublished(service.service_id, recordId),
  );
}

export function getProgressivePublicationTrust(serviceId: string) {
  if (!isProgressiveRouteCell(serviceId)) return null;
  const row = readinessByKey.get(
    cellKey(serviceId, PROGRESSIVE_SOURCE_FAMILY),
  );
  const promotion = promotionByKey.get(
    cellKey(serviceId, PROGRESSIVE_SOURCE_FAMILY),
  );
  const adapter = adapterForPromotion(promotion);
  if (!row || !promotion || !adapter) return null;

  return {
    service_id: String(row.service_id),
    service_label: String(row.service_label || row.service_id),
    canonical_source_id: adapter.canonicalSourceId,
    node_prefix: adapter.nodePrefix,
    source_title: String(adapter.meta?.law_title || ""),
    source_url: String(
      promotion.source_identity?.official_source_url ||
        adapter.meta?.source_page ||
        "",
    ),
    source_version: String(promotion.source_identity?.version_id || ""),
    effective_date: String(promotion.source_identity?.effective_date || ""),
    checked_at: String(promotion.source_identity?.verified_at || ""),
  };
}

export function projectProgressiveRule(
  serviceId: string,
  node: RuleNode,
) {
  if (!isProgressiveRulePublished(serviceId, node.id)) return null;
  const trust = getProgressivePublicationTrust(serviceId);
  if (!trust) return null;

  return {
    source_text: String(node.official_text || ""),
    item_body: {
      article_num: String(node.article_num || ""),
      article_title: String(node.article_title || ""),
      caption: String(node.caption || ""),
      label: String(node.label || ""),
      path: Array.isArray(node.path) ? node.path.map(String) : [],
    },
    source_metadata: {
      service_id: trust.service_id,
      service_label: trust.service_label,
      source_family: PROGRESSIVE_SOURCE_FAMILY,
      source_title: trust.source_title,
      source_version: trust.source_version,
      effective_date: trust.effective_date,
    },
    source_locator: {
      url: String(node.source_url || trust.source_url),
      locator: String(node.source_locator || ""),
    },
    currentness_statement: {
      label: "現行のe-Gov本文を確認済み",
      effective_date: trust.effective_date,
      checked_at: trust.checked_at,
    },
    service_applicability_statement: {
      label: SOURCE_ADAPTERS[trust.canonical_source_id].applicabilityLabel(trust.service_label),
    },
  };
}

export function projectProgressiveRules<T extends RuleNode>(
  serviceId: string,
  records: readonly T[],
) {
  return filterProgressivePublishedRules(serviceId, records, (record) => record.id)
    .map((record) => projectProgressiveRule(serviceId, record))
    .filter(Boolean);
}
