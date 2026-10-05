import allowlistData from "../data/bounded-publication-allowlist.json" with { type: "json" };
import readinessData from "../data/publication-readiness.generated.json" with { type: "json" };
import currentnessData from "../data/verification/bounded-currentness-closure-worker-b.json" with { type: "json" };
import ordinanceMetaData from "../data/ordinance37-meta.json" with { type: "json" };

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
    official_source_url?: string;
    version_id?: string;
    effective_date?: string;
    verified_at?: string;
  };
  applicability_proof?: {
    state?: string;
    direct_service_chapter_verified?: boolean;
    target_articles?: string[];
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

function promotionAllows(serviceId: string, sourceFamily: string) {
  const row = promotionByKey.get(cellKey(serviceId, sourceFamily));
  if (!row) return false;
  return (
    row.promotion_applied === true &&
    row.projected_currentness_state === "PASS" &&
    row.ingestion_state === "INGESTED" &&
    row.item_body_state === "PASS" &&
    row.source_version_contains_scope === true &&
    row.applicability_proof?.state === "PASS_DIRECT_SERVICE_CHAPTER" &&
    row.applicability_proof?.direct_service_chapter_verified === true &&
    row.applicability_proof?.discrepancies === 0 &&
    Array.isArray(row.applicability_proof?.target_articles) &&
    row.applicability_proof.target_articles.length > 0
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

function articleNumberFromRecordId(recordId: string) {
  const match = recordId.match(/^ordinance37\.article\.([0-9]+(?:-[0-9]+)?)(?:\.|$)/);
  return match?.[1] || null;
}

function publishedArticleSet(serviceId: string) {
  if (!isProgressivePublicationCell(serviceId)) return new Set<string>();
  const promotion = promotionByKey.get(
    cellKey(serviceId, PROGRESSIVE_SOURCE_FAMILY),
  );
  return new Set(
    (promotion?.applicability_proof?.target_articles || []).map(String),
  );
}

export function isProgressiveRulePublished(
  serviceId: string,
  recordId: string,
) {
  if (!isProgressiveRouteCell(serviceId)) return false;
  const article = articleNumberFromRecordId(recordId);
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
  if (!row || !promotion) return null;

  return {
    service_id: String(row.service_id),
    service_label: String(row.service_label || row.service_id),
    source_title: String(ordinanceMeta.law_title || ""),
    source_url: String(
      promotion.source_identity?.official_source_url ||
        ordinanceMeta.source_page ||
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
      label: `${trust.service_label}の直接適用章に含まれる条文として確認済み`,
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
