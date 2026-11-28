import unitPriceMetaData from "../../data/unit-price-dayservice-meta.json" with { type: "json" };
import unitPriceMappingsData from "../../data/unit-price-service-multipliers.json" with { type: "json" };
import unitPriceItemBodyData from "../../data/unit-price-item-body-assurance.json" with { type: "json" };
import {
  UNIT_PRICE_SOURCE_FAMILY,
  applicabilityProof,
  commonPromotionSafety,
  sourceIdentity,
  type RuntimePromotion,
  type RuntimeSourceAdapter,
  type RuntimeSourceRecord,
} from "./types.ts";

const SAFE_UNIT_PRICE_PUBLICATION_UNITS = [
  "SOURCE_TEXT_ITEM_BODY",
  "SOURCE_METADATA_LOCATOR",
  "CURRENTNESS_STATEMENT",
  "SERVICE_APPLICABILITY_STATEMENT",
];

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

export const UNIT_PRICE_ADAPTER: RuntimeSourceAdapter = {
  canonicalSourceId: "mhlw-unit-price-current",
  sourceFamily: UNIT_PRICE_SOURCE_FAMILY,
  nodePrefix: "unitprice",
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
