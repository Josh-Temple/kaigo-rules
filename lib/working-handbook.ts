export type HandbookEvidence = {
  kind: "national_standard" | "national_interpretation" | "national_qa" | "yokohama_ordinance" | "yokohama_handbook";
  title: string; issuer: string; locator: string; version: string; scope: string;
  checked_at_jst: string;
  verification_state: "PRIMARY_TEXT_CHECKED_SCOPED" | "SOURCE_CANDIDATE_UNVERIFIED" | "EVIDENCE_GAP";
  url?: string; note?: string; effective_date?: string;
};
export type HandbookRoleRequirement = {
  id: string; title: string;
  aspect: "placement" | "qualification" | "concurrency" | "shifts" | "exception" | "other";
  description: string; applicability: string;
  verification_state: "PRIMARY_TEXT_CHECKED_SCOPED" | "EVIDENCE_GAP";
  evidence: HandbookEvidence[];
  practical_checks: string[];
};
export type HandbookRoleSection = { id: string; title: string; requirements: HandbookRoleRequirement[] };

import handbookData from "../data/handbook.generated.json" with { type: "json" };
import legalData from "../data/legal-browser.generated.json" with { type: "json" };

export type HandbookChapter = {
  section_id: string;
  number: number;
  title: string;
  summary: string;
  paragraphs: string[];
  checkpoints: string[];
  reference_ids: string[];
  role_sections?: HandbookRoleSection[];
  editorial_state: string;
};
export type ServiceHandbookData = {
  service_id: string;
  label: string;
  chapters: HandbookChapter[];
  source_record_count: number;
  qa_codes: string[];
  qa_direct_codes: string[];
  qa_count: number;
};
export type LegalDocument = {
  id: string;
  category: string;
  title: string;
  url: string;
  version: string;
  number: string;
};
export type LegalRecord = {
  id: string;
  document_id: string;
  label: string;
  title: string;
  text: string;
  locator: string;
  state: string;
  source_file: string;
  url: string;
  service_ids: string[];
  service_references: Record<string, Array<{ basis: string; node_id: string; label: string }>>;
  order: number[];
};

export const serviceHandbooks = handbookData.services as ServiceHandbookData[];
export const legalDocuments = legalData.documents as LegalDocument[];
export const legalRecords = legalData.records as LegalRecord[];
const handbookByService = new Map(serviceHandbooks.map(s => [s.service_id, s]));
const recordsById = new Map(legalRecords.map(r => [r.id, r]));
const documentsById = new Map(legalDocuments.map(d => [d.id, d]));

export function serviceHandbook(serviceId: string) {
  return handbookByService.get(serviceId);
}

export function handbookChapterHref(serviceId: string, sectionId: string) {
  return `/handbook/${serviceId}/${sectionId.replaceAll("_", "-")}`;
}

export function chapterRecords(chapter: HandbookChapter): LegalRecord[] {
  return chapter.reference_ids.flatMap(id => {
    const record = recordsById.get(id);
    return record ? [record] : [];
  });
}

export function legalDocument(documentId: string) {
  return documentsById.get(documentId);
}

export const LEGAL_CATEGORIES = [
  { id: "law", label: "介護保険法" },
  { id: "standards", label: "基準省令" },
  { id: "notices", label: "基準解釈通知" },
  { id: "remuneration", label: "報酬基準" },
  { id: "guidance", label: "算定上の留意事項" },
  { id: "criteria", label: "報酬算定基準（別告示）" },
];

export type LegalFilters = { service?: string; category?: string; document?: string; q?: string; record?: string };

export function filterLegalRecords(filters: LegalFilters): LegalRecord[] {
  if (filters.service && !handbookByService.has(filters.service)) return [];
  const terms = (filters.q || "").normalize("NFKC").toLocaleLowerCase("ja").trim().split(/\s+/u).filter(Boolean);
  return legalRecords.filter(record => {
    const doc = documentsById.get(record.document_id);
    if (filters.record && filters.record !== record.id) return false;
    if (filters.service && !record.service_ids.includes(filters.service)) return false;
    if (filters.category && filters.category !== doc?.category) return false;
    if (filters.document && filters.document !== record.document_id) return false;
    if (!terms.length) return true;
    const article = record.id.match(/\.article\.([0-9]+(?:-[0-9]+)*)$/)?.[1];
    const numberLabel = article ? `第${article.split("-")[0]}条${article.split("-").slice(1).map(n => "の" + n).join("")} ${article}` : "";
    const haystack = `${record.id} ${record.label} ${numberLabel} ${record.title} ${record.locator} ${record.text} ${doc?.title || ""}`.normalize("NFKC").toLocaleLowerCase("ja");
    return terms.every(term => haystack.includes(term));
  });
}

export function legalHref(filters: LegalFilters & { page?: number }) {
  const params = new URLSearchParams();
  for (const [key, value] of Object.entries(filters)) {
    if (value) params.set(key, String(value));
  }
  return "/legislation" + (params.size ? "?" + params.toString() : "");
}
