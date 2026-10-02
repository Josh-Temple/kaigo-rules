const synonymGroups = [
  ["bcp", "業務継続計画"],
  ["デイサービス", "通所介護"],
  ["デイケア", "通所リハビリテーション", "通所リハ"],
  ["看護師", "看護職員", "准看護師"],
  ["相談員", "生活相談員"],
  ["計画書", "計画"],
] as const;

export type DatabaseSearchField = {
  value: string;
  weight?: number;
};

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

const fieldScoreForAlternatives = (
  field: DatabaseSearchField,
  alternatives: string[],
) => {
  const haystack = normalizeDatabaseSearch(field.value || "");
  if (!haystack) return 0;
  const weight = field.weight ?? 1;

  let best = 0;
  for (const alternative of alternatives) {
    if (!alternative || !haystack.includes(alternative)) continue;
    if (haystack === alternative) {
      best = Math.max(best, weight * 4);
    } else if (haystack.startsWith(alternative)) {
      best = Math.max(best, weight * 2);
    } else {
      best = Math.max(best, weight);
    }
  }
  return best;
};

export function scoreDatabaseSearch(
  fields: DatabaseSearchField[],
  query: string,
) {
  const terms = databaseSearchTerms(query);
  if (!terms.length) return 0;

  let score = 0;
  for (const alternatives of terms) {
    const best = Math.max(
      0,
      ...fields.map((field) =>
        fieldScoreForAlternatives(field, alternatives),
      ),
    );
    if (!best) return 0;
    score += best;
  }

  const normalizedQuery = normalizeDatabaseSearch(query);
  if (normalizedQuery) {
    const phraseBonus = Math.max(
      0,
      ...fields.map((field) => {
        const haystack = normalizeDatabaseSearch(field.value || "");
        const weight = field.weight ?? 1;
        return haystack.includes(normalizedQuery) ? weight * 2 : 0;
      }),
    );
    score += phraseBonus;
  }

  return score;
}

export function rankDatabaseSearch<T>(
  records: T[],
  query: string,
  fieldsForRecord: (record: T) => DatabaseSearchField[],
) {
  if (!query.trim()) return [];

  return records
    .map((record, index) => ({
      record,
      index,
      score: scoreDatabaseSearch(fieldsForRecord(record), query),
    }))
    .filter((row) => row.score > 0)
    .sort((a, b) => b.score - a.score || a.index - b.index)
    .map((row) => row.record);
}

export function databaseSearchExcerpt(
  value: string,
  query: string,
  max = 180,
) {
  const clean = String(value || "").replace(/\s+/g, " ").trim();
  if (clean.length <= max) return clean;

  const normalized = normalizeDatabaseSearch(clean);
  const alternatives = databaseSearchTerms(query).flat();
  const hitIndexes = alternatives
    .map((term) => normalized.indexOf(term))
    .filter((index) => index >= 0);
  const firstHit = hitIndexes.length ? Math.min(...hitIndexes) : -1;

  if (firstHit < 0) return clean.slice(0, max) + "…";

  const contextBefore = Math.floor(max * 0.35);
  let start = Math.max(0, firstHit - contextBefore);
  let end = Math.min(clean.length, start + max);

  if (end === clean.length) {
    start = Math.max(0, end - max);
  }

  return [
    start > 0 ? "…" : "",
    clean.slice(start, end),
    end < clean.length ? "…" : "",
  ].join("");
}

export function matchesDatabaseSearch(value: string, query: string) {
  return scoreDatabaseSearch([{ value }], query) > 0;
}
