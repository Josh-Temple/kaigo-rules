import type { Metadata } from "next";
import { notFound } from "next/navigation";
import dayservice from "../../docs/prototypes/evidence-bridges/dayservice.json";
import dayrehab from "../../docs/prototypes/evidence-bridges/dayrehab.json";
import PreviewWorkspace, { type PreviewService } from "./PreviewWorkspace";
import { handbookSourceProjectionForService } from "../../lib/handbook/projection";

// Server-only boundary: this DRAFT body must never render in production.
export const dynamic = "force-dynamic";
export const metadata: Metadata = {
  title: "サービス別手引（未レビュー・限定プレビュー）",
  description: "通所系サービスの原典確認に向けた限定的な試用画面。現行性・適用・算定可否は未確認です。",
  robots: { index: false, follow: false, nocache: true },
};

const drafts = [
  { data: dayservice, name: "通所介護", id: "dayservice", expected: 11 },
  { data: dayrehab, name: "通所リハビリテーション", id: "dayrehab", expected: 18 },
] as const;

type Draft = typeof dayservice | typeof dayrehab;

function officialUrl(raw: string): string | null {
  try {
    const url = new URL(raw);
    if (
      url.protocol !== "https:" || url.username || url.password ||
      url.port || url.hash ||
      !["www.mhlw.go.jp", "laws.e-gov.go.jp"].includes(url.hostname)
    ) return null;
    return url.toString();
  } catch {
    return null;
  }
}

function validDraft(data: Draft, expectedService: string, expectedCount: number): boolean {
  if (
    data.schema !== "KAIGO_EVIDENCE_CHAPTER_BRIDGE_DRAFT_V1" ||
    data.service_id !== expectedService ||
    data.release_gate !== "HOLD_NO_GO" ||
    data.publication !== "BLOCKED" ||
    data.currentness !== "NOT_ESTABLISHED" ||
    data.applicability !== "NOT_ESTABLISHED" ||
    data.human_review !== "NOT_REVIEWED" ||
    data.legal_explanations_accepted !== 0 ||
    data.real_project_work_enabled !== false ||
    data.chapter_count !== 15 ||
    data.chapters.length !== 15 ||
    data.candidate_paragraph_count !== expectedCount ||
    data.source_evidence.length !== 6
  ) return false;

  const ids = new Set<string>();
  const chapters = new Set<string>();
  const evidence = new Map(data.source_evidence.map((entry) => [entry.task_id, entry]));
  if (evidence.size !== 6 || data.source_evidence.some((entry) => entry.service_id !== expectedService)) return false;
  let count = 0;
  for (const chapter of data.chapters) {
    if (!chapter.section_id || !chapter.title || chapters.has(chapter.section_id)) return false;
    chapters.add(chapter.section_id);
    for (const item of chapter.candidate_paragraphs) {
      const source = evidence.get(item.evidence_task_id);
      if (
        !source || source.library_file_id !== item.evidence_library_file_id ||
        source.source_url !== item.source_url_from_evidence ||
        item.draft_review_state !== "DRAFT_UNREVIEWED" ||
        !item.bridge_id || ids.has(item.bridge_id) ||
        typeof item.text !== "string" || !item.text.length ||
        !Array.isArray(item.source_identifiers)
      ) return false;
      ids.add(item.bridge_id);
      count++;
    }
  }
  return chapters.size === 15 && count === expectedCount && ids.size === expectedCount;
}

export default function HandbookEvidencePreviewPage() {
  // Vercel SSO protects previews; this route additionally denies production.
  if (process.env.VERCEL_ENV !== "preview" && process.env.NODE_ENV !== "development") notFound();
  if (drafts.some(({ data, id, expected }) => !validDraft(data, id, expected))) notFound();

  const services: PreviewService[] = drafts.map(({ data, name, id }) => {
    const evidence = new Map(data.source_evidence.map((entry) => [entry.task_id, entry]));
    const projection = handbookSourceProjectionForService(id);
    if (!projection || projection.service_id !== id ||
        projection.chapters.length !== 15 ||
        projection.publication !== "BLOCKED" ||
        projection.currentness !== "NOT_ESTABLISHED" ||
        projection.human_review !== "NOT_REVIEWED") notFound();
    const bySection = new Map(projection.chapters.map(c => [c.section_id, c]));
    return {
      serviceId: id,
      title: name,
      chapters: data.chapters.map((chapter) => {
        const info = bySection.get(chapter.section_id);
        if (!info || info.title !== chapter.title) notFound();
        return {
          sectionId: chapter.section_id,
          title: chapter.title,
          candidates: chapter.candidate_paragraphs.map(item => ({
            bridgeId: item.bridge_id,
            text: item.text,
            evidenceTaskId: item.evidence_task_id,
            sourceIdentifiers: item.source_identifiers,
            officialUrl: officialUrl(evidence.get(item.evidence_task_id)?.source_url ?? ""),
          })),
          questionsToCheck: info.questions_to_check,
          unresolved: info.unresolved,
          publicSearchHref: info.public_search_href,
          sourceCandidates: info.source_candidates.map(source => ({
            candidateId: source.candidate_id,
            kind: source.candidate_type,
            sourceName: source.source_title,
            sourceVersion: source.source_version,
            officialUrl: source.official_url_candidate,
            historical: source.source_record_status === "HISTORICAL",
          })),
        };
      }),
    };
  });
  return <PreviewWorkspace services={services} />;
}
