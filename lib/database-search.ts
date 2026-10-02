const synonymGroups = [
  ["bcp", "業務継続計画"],
  ["デイサービス", "通所介護"],
  ["デイケア", "通所リハビリテーション", "通所リハ"],
  ["看護師", "看護職員", "准看護師"],
  ["相談員", "生活相談員"],
  ["計画書", "計画"],
] as const;

export const normalizeDatabaseSearch = (value: string) =>
  value.normalize("NFKC").toLowerCase().replace(/\s+/g, " ").trim();

const expandTerm = (term: string) => {
  const normalized = normalizeDatabaseSearch(term);
  const group = synonymGroups.find((items) =>
    items.some((item) => normalizeDatabaseSearch(item) === normalized),
  );
  return group
    ? group.map((item) => normalizeDatabaseSearch(item))
    : [normalized];
};

export const databaseSearchTerms = (query: string) =>
  normalizeDatabaseSearch(query)
    .split(" ")
    .filter(Boolean)
    .map(expandTerm);

export function matchesDatabaseSearch(value: string, query: string) {
  const terms = databaseSearchTerms(query);
  if (!terms.length) return false;
  const haystack = normalizeDatabaseSearch(value);
  return terms.every((alternatives) =>
    alternatives.some((term) => haystack.includes(term)),
  );
}
