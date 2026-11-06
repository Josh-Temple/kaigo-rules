// Browser-compatible reproduction of /qa query/filter/pagination logic.
// This module contains no corpus and does not publish any data.
const synonyms = [
  ["看護師", "看護職員", "准看護師"],
  ["生活相談員", "相談員"],
  ["ハンコ", "判子", "押印", "捺印", "印鑑"],
  ["サイン", "署名", "自署"],
  ["bcp", "業務継続計画"],
  ["デイサービス", "通所介護"],
  ["計画書", "通所介護計画", "計画"],
  ["機能訓練室", "機能訓練"],
  ["常勤換算", "常勤換算方法"],
];

export const DAY_SERVICE_QA_CODES = Object.freeze(["01", "02", "06", "16"]);
export const QA_PAGE_SIZE = 30;

export function normalizeQa(value) {
  return String(value || "").normalize("NFKC").toLowerCase().replace(/\s+/g, " ").trim();
}

export function expandQaTerm(term) {
  const normalized = normalizeQa(term);
  const group = synonyms.find((items) => items.some((item) => normalizeQa(item) === normalized));
  return group ? group.map(normalizeQa) : [normalized];
}

export function searchQaEntries(entries, params = {}) {
  // Reproduce app/qa/page.tsx: service/standard filters, AND with exact synonym expansion,
  // corpus order, 30 records/page, clamp out-of-range page to last.
  const q = String(params.q || "").trim();
  const service = String(params.service || "");
  const standard = String(params.standard || "");
  const requestedPage = Math.max(1, Number.parseInt(String(params.page || "1"), 10) || 1);
  const terms = normalizeQa(q).split(" ").filter(Boolean);
  const expanded = terms.map(expandQaTerm);
  const filtered = entries.filter((item) => {
    if (service && item.service_code !== service) return false;
    if (standard && item.standard_label !== standard) return false;
    if (!terms.length) return true;
    const haystack = normalizeQa([
      item.scope, item.service_label, item.current_service_scope, item.standard_label,
      item.topic, item.question, item.answer, item.issued_source, item.number,
    ].join(" "));
    return expanded.every((alternatives) => alternatives.some((term) => haystack.includes(term)));
  });
  const totalPages = Math.max(1, Math.ceil(filtered.length / QA_PAGE_SIZE));
  const page = Math.min(requestedPage, totalPages);
  return {
    total: filtered.length,
    page,
    totalPages,
    visible: filtered.slice((page - 1) * QA_PAGE_SIZE, page * QA_PAGE_SIZE),
  };
}
