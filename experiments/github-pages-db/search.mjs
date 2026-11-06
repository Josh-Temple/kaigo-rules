import { rankDatabaseSearch } from "./rank-core.mjs";

export const GROUPS = ["law", "ordinance", "unitPrice", "delegated", "notice", "qa"];

export function runSearch(data, query, category = "") {
  return Object.fromEntries(GROUPS.map((key) => [
    key, category && category !== key ? [] :
      rankDatabaseSearch(data[key] || [], query, (row) => row.fields),
  ]));
}

export function resultHref(group, row, query) {
  if (group !== "unitPrice" || !query.trim()) return row.href;
  const params = new URLSearchParams({ service: row.serviceId });
  params.set("q", query.trim());
  return "/fees/unit-price?" + params.toString();
}
