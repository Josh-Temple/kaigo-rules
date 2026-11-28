import { DELEGATED_REMUNERATION_ADAPTER } from "./runtime-adapters/delegated-remuneration.ts";
import { GOVERNING_STANDARDS_ADAPTERS } from "./runtime-adapters/governing-standards.ts";
import {
  DELEGATED_REMUNERATION_CANONICAL_SOURCE_ID,
  sourceIdentity,
  type RuntimeProjectionTrust,
  type RuntimePromotion,
  type RuntimeSourceAdapter,
  type RuntimeSourceRecord,
} from "./runtime-adapters/types.ts";
import { UNIT_PRICE_ADAPTER } from "./runtime-adapters/unit-price.ts";

export {
  DELEGATED_REMUNERATION_CANONICAL_SOURCE_ID,
  DELEGATED_REMUNERATION_SOURCE_FAMILY,
  GOVERNING_STANDARDS_SOURCE_FAMILY,
  UNIT_PRICE_SOURCE_FAMILY,
  type RuntimeProjectionTrust,
  type RuntimePromotion,
  type RuntimeSourceAdapter,
  type RuntimeSourceRecord,
} from "./runtime-adapters/types.ts";

export const RUNTIME_SOURCE_ADAPTERS: Record<
  string,
  RuntimeSourceAdapter
> = {
  ...GOVERNING_STANDARDS_ADAPTERS,
  "mhlw-unit-price-current": UNIT_PRICE_ADAPTER,
  [DELEGATED_REMUNERATION_CANONICAL_SOURCE_ID]:
    DELEGATED_REMUNERATION_ADAPTER,
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
