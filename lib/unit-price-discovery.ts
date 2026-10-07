import { rankDatabaseSearch } from "./database-search.ts";
import {
  UNIT_PRICE_SOURCE_FAMILY,
  getProgressivePublicationTrust,
  getProgressiveSourceRecords,
  listProgressivePublicationCells,
  projectProgressiveRecords,
} from "./publication-policy.ts";

export type PublicUnitPriceRow = {
  id: string;
  service_id: string;
  service_label: string;
  region_class: string;
  ratio_text: string;
  ratio_per_thousand: number;
  unit_price_yen: number;
  source_url: string;
  source_locator: string;
  checked_at: string;
};

export function listPublicUnitPriceServices() {
  return listProgressivePublicationCells(UNIT_PRICE_SOURCE_FAMILY)
    .filter((cell) => {
      const trust = getProgressivePublicationTrust(
        cell.service_id,
        UNIT_PRICE_SOURCE_FAMILY,
      );
      return Boolean(
        trust &&
          getProgressiveSourceRecords(
            cell.service_id,
            UNIT_PRICE_SOURCE_FAMILY,
          ).length > 0,
      );
    })
    .map(({ service_id, label }) => ({ service_id, label }));
}

// Use the same bounded runtime projection as the public API; never read
// the ingested service multiplier table as an alternative public source.
export function publicUnitPriceRows(serviceId?: string): PublicUnitPriceRow[] {
  const cells = listPublicUnitPriceServices().filter(
    (cell) => !serviceId || cell.service_id === serviceId,
  );
  return cells.flatMap((cell) => {
    const trust = getProgressivePublicationTrust(
      cell.service_id,
      UNIT_PRICE_SOURCE_FAMILY,
    );
    const records = getProgressiveSourceRecords(
      cell.service_id,
      UNIT_PRICE_SOURCE_FAMILY,
    );
    if (!trust || !records.length) return [];

    const projected = projectProgressiveRecords(
      cell.service_id,
      UNIT_PRICE_SOURCE_FAMILY,
      records,
    ) as Array<any>;
    // Do not display a partial or malformed projection as a complete table.
    if (projected.length !== records.length) return [];
    const rows: PublicUnitPriceRow[] = [];
    for (let index = 0; index < projected.length; index += 1) {
      const item = projected[index];
      const body = item?.item_body || {};
      const regionClass = String(body.region_class || "");
      const rate = Number(body.unit_price_yen);
      const ratio = Number(body.ratio_per_thousand);
      if (
        !regionClass ||
        !Number.isFinite(rate) ||
        rate <= 0 ||
        !Number.isFinite(ratio) ||
        ratio <= 0 ||
        !String(body.ratio_text || "")
      ) {
        return [];
      }
      rows.push({
        id: String(records[index].id),
        service_id: cell.service_id,
        service_label: cell.label,
        region_class: regionClass,
        ratio_text: String(body.ratio_text),
        ratio_per_thousand: ratio,
        unit_price_yen: rate,
        source_url: String(item.source_locator?.url || trust.source_url),
        source_locator: String(item.source_locator?.locator || ""),
        checked_at: String(trust.checked_at || ""),
      });
    }
    return rows;
  });
}

export function searchPublicUnitPrices(query: string, serviceId?: string) {
  const rows = publicUnitPriceRows(serviceId);
  if (!query.trim()) return rows;
  return rankDatabaseSearch(rows, query, (row) => [
    {
      value: [row.region_class, row.service_label].join(" "),
      weight: 10,
    },
    {
      value: [row.ratio_text, String(row.unit_price_yen) + "円"].join(" "),
      weight: 8,
    },
    { value: "地域区分 一単位単価 単価", weight: 4 },
    { value: row.source_locator, weight: 1 },
  ]);
}

export function unitPriceHref(serviceId: string, query = "") {
  const params = new URLSearchParams({ service: serviceId });
  if (query) params.set("q", query);
  return "/fees/unit-price?" + params.toString();
}
