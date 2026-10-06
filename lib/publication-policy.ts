import allowlistData from "../data/bounded-publication-allowlist.json" with { type: "json" };
import readinessData from "../data/publication-readiness.generated.json" with { type: "json" };
import governingCurrentnessData from "../data/verification/bounded-currentness-closure-worker-b.json" with { type: "json" };
import highValueCurrentnessData from "../data/verification/high-value-currentness-closure-worker-b.json" with { type: "json" };
import {
  DELEGATED_REMUNERATION_CANONICAL_SOURCE_ID,
  DELEGATED_REMUNERATION_SOURCE_FAMILY,
  GOVERNING_STANDARDS_SOURCE_FAMILY,
  RUNTIME_SOURCE_ADAPTERS,
  UNIT_PRICE_SOURCE_FAMILY,
  isRuntimeRecordPublished,
  projectRuntimeRecord,
  runtimeAdapterForPromotion,
  runtimeRecordsForPromotion,
  type RuntimePromotion,
  type RuntimeSourceRecord,
} from "./publication-runtime-adapters.ts";

export const PROGRESSIVE_SOURCE_FAMILY =
  GOVERNING_STANDARDS_SOURCE_FAMILY;
export {
  DELEGATED_REMUNERATION_SOURCE_FAMILY,
  UNIT_PRICE_SOURCE_FAMILY,
};

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

const allowlist = allowlistData as any;
const readiness = readinessData as { cells?: ReadinessRow[] };
const governingCurrentness =
  governingCurrentnessData as { promotions?: RuntimePromotion[] };
const highValueCurrentness =
  highValueCurrentnessData as { promotions?: RuntimePromotion[] };

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
  "specific-preventive-welfare-equipment-sale":
    "specific-welfare-equipment-sale",
};

export function publicationServicePresentationGroup(serviceId: string) {
  return PREVENTIVE_COUNTERPARTS[serviceId] || serviceId;
}

export function isPreventivePublicationService(serviceId: string) {
  return Object.prototype.hasOwnProperty.call(
    PREVENTIVE_COUNTERPARTS,
    serviceId,
  );
}

export function isSupportedPublicationContract(
  canonicalSourceId: string,
  applicabilityState: string,
  verified: boolean,
) {
  if (verified !== true) return false;
  if (canonicalSourceId === "ordinance37") {
    return applicabilityState === "PASS_DIRECT_SERVICE_CHAPTER";
  }
  if (
    canonicalSourceId === "preventive-services-standards" ||
    canonicalSourceId === "mhlw-unit-price-current"
  ) {
    return applicabilityState === "PASS_DIRECT_SERVICE_SCOPE";
  }
  if (
    canonicalSourceId ===
    DELEGATED_REMUNERATION_CANONICAL_SOURCE_ID
  ) {
    return applicabilityState === "MAPPED";
  }
  return false;
}

const cellKey = (serviceId: string, sourceFamily: string) =>
  `${serviceId}|${sourceFamily}`;

const publicationKeys = new Set<string>(
  (allowlist.publication_cell_allowlist || []).map(
    (cell: PublicationCell) =>
      cellKey(
        String(cell.service_id || ""),
        String(cell.source_family || ""),
      ),
  ),
);

const routeKeys = new Set<string>(
  (allowlist.route_allowlist || []).map((cell: PublicationCell) =>
    cellKey(
      String(cell.service_id || ""),
      String(cell.source_family || ""),
    ),
  ),
);

const readinessByKey = new Map(
  (readiness.cells || []).map((row) => [
    cellKey(
      String(row.service_id || ""),
      String(row.source_family || ""),
    ),
    row,
  ]),
);

const promotions = [
  ...(governingCurrentness.promotions || []),
  ...(highValueCurrentness.promotions || []),
];

const promotionByKey = new Map<string, RuntimePromotion>();
for (const [key, binding] of Object.entries(
  allowlist.runtime_source_binding_by_cell || {},
)) {
  const promotion = (binding as any)?.promotion as
    | RuntimePromotion
    | undefined;
  if (promotion) {
    promotionByKey.set(key, promotion);
  }
}
for (const row of promotions) {
  const key = cellKey(
    String(row.service_id || ""),
    String(row.source_family || ""),
  );
  if (!promotionByKey.has(key)) {
    promotionByKey.set(key, row);
  }
}

const runtimeBindingEstablished =
  allowlist.runtime_binding?.established === true;

function fieldsAreSafe(serviceId: string, sourceFamily: string) {
  const fields =
    allowlist.field_allowlist_by_cell?.[
      cellKey(serviceId, sourceFamily)
    ];
  if (!Array.isArray(fields)) return false;
  const selected = new Set(fields.map(String));
  return (
    SAFE_PUBLICATION_FIELDS.every((field) => selected.has(field)) &&
    [...selected].every((field) =>
      (SAFE_PUBLICATION_FIELDS as readonly string[]).includes(field),
    )
  );
}

function readinessAllows(
  serviceId: string,
  sourceFamily: string,
) {
  const row = readinessByKey.get(
    cellKey(serviceId, sourceFamily),
  );
  if (
    !row ||
    row.readiness !== "READY_FOR_PUBLICATION_REVIEW"
  ) {
    return false;
  }
  if ((row.blocking_reasons || []).length) return false;
  const units = new Set(row.ready_publication_units || []);
  return REQUIRED_PUBLICATION_UNITS.every((unit) =>
    units.has(unit),
  );
}

function promotionAllows(
  serviceId: string,
  sourceFamily: string,
) {
  const row = promotionByKey.get(
    cellKey(serviceId, sourceFamily),
  );
  const adapter = runtimeAdapterForPromotion(row);
  return Boolean(
    row &&
      adapter &&
      adapter.sourceFamily === sourceFamily,
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

export function listProgressivePublicationCells(
  sourceFamily?: string,
) {
  return [...publicationKeys]
    .map((key) => readinessByKey.get(key))
    .filter((row): row is ReadinessRow => Boolean(row))
    .filter(
      (row) =>
        Boolean(row.service_id) &&
        Boolean(row.source_family) &&
        (!sourceFamily ||
          row.source_family === sourceFamily) &&
        isProgressiveRouteCell(
          String(row.service_id),
          String(row.source_family),
        ),
    )
    .map((row) => ({
      service_id: String(row.service_id),
      label: String(row.service_label || row.service_id),
      source_family: String(row.source_family),
    }));
}

export function listProgressivePublicationServices(
  sourceFamily = PROGRESSIVE_SOURCE_FAMILY,
) {
  return listProgressivePublicationCells(sourceFamily);
}

export function listProgressivePublicationServicesAcrossFamilies() {
  const services = new Map<
    string,
    {
      service_id: string;
      label: string;
      source_families: string[];
    }
  >();

  for (const cell of listProgressivePublicationCells()) {
    const current = services.get(cell.service_id);
    if (current) {
      if (
        !current.source_families.includes(cell.source_family)
      ) {
        current.source_families.push(cell.source_family);
      }
      continue;
    }
    services.set(cell.service_id, {
      service_id: cell.service_id,
      label: cell.label,
      source_families: [cell.source_family],
    });
  }

  return [...services.values()].map((service) => ({
    ...service,
    source_families: [...service.source_families].sort(),
  }));
}

export function getProgressiveSourceRecords(
  serviceId: string,
  sourceFamily = PROGRESSIVE_SOURCE_FAMILY,
): RuntimeSourceRecord[] {
  if (!isProgressiveRouteCell(serviceId, sourceFamily)) {
    return [];
  }
  const promotion = promotionByKey.get(
    cellKey(serviceId, sourceFamily),
  );
  return runtimeRecordsForPromotion(promotion);
}

export function isProgressiveRecordPublished(
  serviceId: string,
  sourceFamily: string,
  recordId: string,
) {
  if (!isProgressiveRouteCell(serviceId, sourceFamily)) {
    return false;
  }
  const promotion = promotionByKey.get(
    cellKey(serviceId, sourceFamily),
  );
  const records = runtimeRecordsForPromotion(promotion);
  const record = records.find((item) => item.id === recordId);
  return Boolean(
    record &&
      isRuntimeRecordPublished(promotion, record),
  );
}

export function filterProgressivePublishedRecords<T>(
  serviceId: string,
  sourceFamily: string,
  records: readonly T[],
  recordId: (record: T) => string,
): T[] {
  return records.filter((record) =>
    isProgressiveRecordPublished(
      serviceId,
      sourceFamily,
      recordId(record),
    ),
  );
}

export function isProgressiveRulePublished(
  serviceId: string,
  recordId: string,
) {
  return isProgressiveRecordPublished(
    serviceId,
    PROGRESSIVE_SOURCE_FAMILY,
    recordId,
  );
}

export function filterProgressivePublishedRules<T>(
  serviceId: string,
  records: readonly T[],
  recordId: (record: T) => string,
): T[] {
  return filterProgressivePublishedRecords(
    serviceId,
    PROGRESSIVE_SOURCE_FAMILY,
    records,
    recordId,
  );
}

export function progressiveServicesForRule(recordId: string) {
  return listProgressivePublicationServices().filter(
    (service) =>
      isProgressiveRulePublished(
        service.service_id,
        recordId,
      ),
  );
}

function nodePrefixForCanonicalSource(
  canonicalSourceId: string,
) {
  if (canonicalSourceId === "ordinance37") {
    return "ordinance37";
  }
  if (
    canonicalSourceId ===
    "preventive-services-standards"
  ) {
    return "standards35";
  }
  if (canonicalSourceId === "mhlw-unit-price-current") {
    return "unitprice";
  }
  if (
    canonicalSourceId ===
    DELEGATED_REMUNERATION_CANONICAL_SOURCE_ID
  ) {
    return "delegated-remuneration";
  }
  return "";
}

export function getProgressivePublicationTrust(
  serviceId: string,
  sourceFamily = PROGRESSIVE_SOURCE_FAMILY,
) {
  if (!isProgressiveRouteCell(serviceId, sourceFamily)) {
    return null;
  }
  const row = readinessByKey.get(
    cellKey(serviceId, sourceFamily),
  );
  const promotion = promotionByKey.get(
    cellKey(serviceId, sourceFamily),
  );
  const adapter = runtimeAdapterForPromotion(promotion);
  if (!row || !promotion || !adapter) return null;

  return {
    service_id: String(row.service_id),
    service_label: String(
      row.service_label || row.service_id,
    ),
    source_family: sourceFamily,
    canonical_source_id: adapter.canonicalSourceId,
    node_prefix: nodePrefixForCanonicalSource(
      adapter.canonicalSourceId,
    ),
    source_title: adapter.sourceTitle(promotion),
    source_url: adapter.defaultSourceUrl(promotion),
    source_version: String(
      promotion.source_identity?.version_id || "",
    ),
    effective_date: String(
      promotion.source_identity?.effective_date || "",
    ),
    checked_at: String(
      promotion.source_identity?.verified_at ||
        promotion.source_identity
          ?.current_official_display_observed_on ||
        "",
    ),
  };
}

export function projectProgressiveRecord(
  serviceId: string,
  sourceFamily: string,
  record: RuntimeSourceRecord,
) {
  if (
    !isProgressiveRecordPublished(
      serviceId,
      sourceFamily,
      record.id,
    )
  ) {
    return null;
  }

  const trust = getProgressivePublicationTrust(
    serviceId,
    sourceFamily,
  );
  const promotion = promotionByKey.get(
    cellKey(serviceId, sourceFamily),
  );
  if (!trust || !promotion) return null;

  return projectRuntimeRecord(
    promotion,
    trust,
    record,
  );
}

export function projectProgressiveRule(
  serviceId: string,
  node: RuntimeSourceRecord,
) {
  return projectProgressiveRecord(
    serviceId,
    PROGRESSIVE_SOURCE_FAMILY,
    node,
  );
}

export function projectProgressiveRecords(
  serviceId: string,
  sourceFamily: string,
  records: readonly RuntimeSourceRecord[],
) {
  return filterProgressivePublishedRecords(
    serviceId,
    sourceFamily,
    records,
    (record) => record.id,
  )
    .map((record) =>
      projectProgressiveRecord(
        serviceId,
        sourceFamily,
        record,
      ),
    )
    .filter(Boolean);
}

export function projectProgressiveRules<
  T extends RuntimeSourceRecord,
>(serviceId: string, records: readonly T[]) {
  return filterProgressivePublishedRules(
    serviceId,
    records,
    (record) => record.id,
  )
    .map((record) =>
      projectProgressiveRule(serviceId, record),
    )
    .filter(Boolean);
}

export function runtimePublicationAdapterRegistry() {
  return Object.values(RUNTIME_SOURCE_ADAPTERS).map(
    (adapter) => ({
      canonical_source_id: adapter.canonicalSourceId,
      source_family: adapter.sourceFamily,
      record_kind: adapter.recordKind,
    }),
  );
}
