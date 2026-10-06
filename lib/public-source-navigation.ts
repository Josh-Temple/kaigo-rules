import { isProgressiveRouteCell } from "./publication-policy";
import { listServices } from "./service-catalog";

export type PublicSourceFamilyNavigation = {
  source_family: string;
  label: string;
  short_label: string;
  description: string;
  href: string;
};

type PublicSourceFamilyDefinition = {
  source_family: string;
  label: string;
  short_label: string;
  description: string;
  service_ids?: readonly string[];
  hrefForService: (serviceId: string) => string;
};

export const GOVERNING_STANDARDS_SOURCE_FAMILY =
  "governing_standards_ordinance";
export const UNIT_PRICE_SOURCE_FAMILY =
  "unit_price_regional_classification";

const DEFINITIONS: readonly PublicSourceFamilyDefinition[] = [
  {
    source_family: GOVERNING_STANDARDS_SOURCE_FAMILY,
    label: "基準省令",
    short_label: "基準省令",
    description: "人員・設備・運営などの基準本文",
    hrefForService: (serviceId) =>
      "/rules?service=" + encodeURIComponent(serviceId),
  },
  {
    source_family: UNIT_PRICE_SOURCE_FAMILY,
    label: "一単位単価・地域区分",
    short_label: "単価・地域区分",
    description: "報酬単位数を金額へ換算する地域区分別の一単位単価",
    service_ids: ["dayservice"],
    hrefForService: () => "/fees/unit-price",
  },
];

export function publicSourceFamiliesForService(
  serviceId: string,
): PublicSourceFamilyNavigation[] {
  return DEFINITIONS.filter(
    (definition) =>
      (!definition.service_ids ||
        definition.service_ids.includes(serviceId)) &&
      isProgressiveRouteCell(serviceId, definition.source_family),
  ).map((definition) => ({
    source_family: definition.source_family,
    label: definition.label,
    short_label: definition.short_label,
    description: definition.description,
    href: definition.hrefForService(serviceId),
  }));
}

export function publicSourceNavigationMetrics() {
  const serviceRows = listServices().map((service) => ({
    service_id: service.service_id,
    source_families: publicSourceFamiliesForService(service.service_id),
  }));
  const cells = serviceRows.flatMap((row) =>
    row.source_families.map((source) => ({
      service_id: row.service_id,
      source_family: source.source_family,
    })),
  );
  const runtimeFamilies = new Set(cells.map((cell) => cell.source_family));

  return {
    runtime_supported_source_families: runtimeFamilies.size,
    runtime_supported_source_family_ids: [...runtimeFamilies].sort(),
    cross_source_searchable_cells: cells.length,
    service_pages_with_2plus_published_source_families: serviceRows.filter(
      (row) => row.source_families.length >= 2,
    ).length,
  };
}
