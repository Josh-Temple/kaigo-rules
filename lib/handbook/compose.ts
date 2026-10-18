/**
 * Restricted handbook preparation: source locators, not legal findings.
 *
 * No draft paragraph text crosses this projection. Never use its candidate
 * URLs/IDs or manuscript counts as publication, currentness or review grants.
 * The ONLY published resource routes are passed by the publication-policy
 * backed publicSourceFamiliesForService() caller.
 */
export type BridgeCandidate = {
  bridge_id: string;
  evidence_task_id: string;
  evidence_library_file_id: string;
  source_identifiers: string[];
  source_url_from_evidence: string;
  draft_review_state: string;
};
export type BridgeEvidence = {
  task_id: string;
  service_id: string;
  library_file_id: string;
  source_url: string;
  byte_sha256: string;
  size_bytes: number;
  unresolved?: string[];
};
export type BridgeInventory = {
  schema: string;
  service_id: string;
  chapter_count: number;
  candidate_paragraph_count: number;
  publication: string;
  release_gate: string;
  currentness: string;
  applicability: string;
  human_review: string;
  legal_explanations_accepted: number;
  real_project_work_enabled: boolean;
  chapters: Array<{
    section_id: string;
    title: string;
    candidate_paragraphs: BridgeCandidate[];
  }>;
  source_evidence: BridgeEvidence[];
};
export type ExistingDraft = {
  service_id: string;
  publication_state: string;
  human_review_state: string;
  legal_explanations_accepted: number;
  sections: Array<{
    section_id: string;
    intended_user_questions: string[];
    draft_statements: Array<{ statement_id: string; review_state: string }>;
    gaps: Array<{ issue: string; status: string }>;
  }>;
};
export type ExistingSourceCandidates = {
  service_id: string;
  publication_status: string;
  human_review_status: string;
  legal_currentness_acceptance: string;
  sections: Array<{
    section_id: string;
    candidates: Array<{
      section_id: string;
      candidate_id: string;
      source_id: string;
      source_url: string;
      source_version: string | null;
      source_locator: string;
      candidate_status: string;
      title: string;
    }>;
  }>;
};
export type SourceRegistryEntry = { id: string; url: string; title: string };
export type PublicFamilyRoute = {
  source_family: string;
  label: string;
  href: string;
};
export type ChapterSourceCandidate = {
  candidate_id: string;
  candidate_type: "EVIDENCE_BRIDGE" | "OLD_SOURCE_CANDIDATE";
  source_record_status: "DRAFT_UNREVIEWED" | "CANDIDATE" | "HISTORICAL";
  evidence_task_id: string | null;
  library_file_id: string | null;
  source_identifiers: string[];
  source_registry_id: string | null;
  source_version: string | null;
  source_locator: string | null;
  source_title: string | null;
  official_url_candidate: string | null;
  publication: "NOT_GRANTED";
  currentness: "NOT_ESTABLISHED";
  human_review: "NOT_REVIEWED";
  applicability: "NOT_ESTABLISHED";
};
export type HandbookChapterProjection = {
  section_id: string;
  title: string;
  questions_to_check: string[];
  unresolved: string[];
  source_candidates: ChapterSourceCandidate[];
  historical_draft_statement_count: number;
  public_search_href: string;
};
export type HandbookProjection = {
  service_id: string;
  chapters: HandbookChapterProjection[];
  published_service_routes: PublicFamilyRoute[];
  candidate_count: number;
  old_source_candidate_count: number;
  historical_draft_statement_count: number;
  publication: "BLOCKED";
  currentness: "NOT_ESTABLISHED";
  human_review: "NOT_REVIEWED";
  legal_explanations_accepted: 0;
};

type ComposeInput = {
  serviceId: string;
  registeredServiceIds: readonly string[];
  bridge: BridgeInventory;
  registry: readonly SourceRegistryEntry[];
  publishedServiceRoutes: readonly PublicFamilyRoute[];
  oldDraft?: ExistingDraft;
  oldSourceCandidates?: ExistingSourceCandidates;
};

function requireValid(ok: unknown, message: string): asserts ok {
  if (!ok) throw new Error("Handbook projection rejected: " + message);
}

/** Permit government site locators, NOT an assertion that a URL is current. */
export function safeOfficialSourceUrl(value: string): string | null {
  try {
    const u = new URL(value);
    if (u.protocol !== "https:" || u.username || u.password || u.port ||
        u.hash || !["www.mhlw.go.jp", "laws.e-gov.go.jp"].includes(u.hostname)) {
      return null;
    }
    return u.toString();
  } catch {
    return null;
  }
}

function distinct(items: string[]): string[] {
  return [...new Set(items.filter(Boolean))];
}

export function composeHandbookProjection(input: ComposeInput): HandbookProjection {
  const { serviceId, bridge, oldDraft, oldSourceCandidates } = input;
  requireValid(input.registeredServiceIds.includes(serviceId), "unknown service ID");
  requireValid(bridge.service_id === serviceId, "bridge belongs to another service");
  requireValid(bridge.schema === "KAIGO_EVIDENCE_CHAPTER_BRIDGE_DRAFT_V1", "bridge schema");
  requireValid(
    bridge.publication === "BLOCKED" && bridge.release_gate === "HOLD_NO_GO" &&
    bridge.currentness === "NOT_ESTABLISHED" && bridge.applicability === "NOT_ESTABLISHED" &&
    bridge.human_review === "NOT_REVIEWED" && bridge.legal_explanations_accepted === 0 &&
    bridge.real_project_work_enabled === false, "bridge release/review gate"
  );
  requireValid(bridge.chapter_count === 15 && bridge.chapters.length === 15, "chapter count");

  const evidenceById = new Map<string, BridgeEvidence>();
  for (const evidence of bridge.source_evidence) {
    requireValid(evidence.service_id === serviceId, "cross-service evidence");
    requireValid(!evidenceById.has(evidence.task_id), "duplicate evidence ID");
    requireValid(/^KR-EVIDENCE-[0-9]{3}$/.test(evidence.task_id), "evidence ID");
    requireValid(/^libfile_[a-zA-Z0-9]+$/.test(evidence.library_file_id), "evidence library ID");
    requireValid(/^[0-9a-f]{64}$/.test(evidence.byte_sha256) &&
      Number.isSafeInteger(evidence.size_bytes) && evidence.size_bytes > 0, "evidence provenance");
    evidenceById.set(evidence.task_id, evidence);
  }
  const registry = new Map<string, SourceRegistryEntry>();
  for (const s of input.registry) {
    requireValid(s.id && !registry.has(s.id), "duplicate source registry ID");
    registry.set(s.id, s);
  }
  if (oldDraft) {
    requireValid(oldDraft.service_id === serviceId &&
      oldDraft.publication_state === "PUBLICATION_BLOCKED" &&
      oldDraft.human_review_state === "HUMAN_REVIEW_NOT_DONE" &&
      oldDraft.legal_explanations_accepted === 0, "old draft trust boundary");
  }
  if (oldSourceCandidates) {
    requireValid(oldSourceCandidates.service_id === serviceId &&
      oldSourceCandidates.publication_status === "PUBLICATION_BLOCKED" &&
      oldSourceCandidates.human_review_status === "HUMAN_REVIEW_NOT_DONE" &&
      oldSourceCandidates.legal_currentness_acceptance === "NOT_ESTABLISHED",
      "old candidate trust boundary");
  }

  const oldDraftBySection = new Map(oldDraft?.sections.map(s => [s.section_id, s]) ?? []);
  const oldCandidatesBySection = new Map(oldSourceCandidates?.sections.map(s => [s.section_id, s]) ?? []);
  const seenSections = new Set<string>();
  const seenCandidateIds = new Set<string>();
  const seenDraftIds = new Set<string>();
  let evidenceCandidateCount = 0;
  let legacyCandidateCount = 0;
  let draftStatementCount = 0;

  const chapters = bridge.chapters.map(chapter => {
    requireValid(Boolean(chapter.section_id && chapter.title) &&
      !seenSections.has(chapter.section_id), "duplicate/empty chapter");
    seenSections.add(chapter.section_id);
    const sources: ChapterSourceCandidate[] = [];
    const unresolved: string[] = [];
    for (const candidate of chapter.candidate_paragraphs) {
      const evidence = evidenceById.get(candidate.evidence_task_id);
      requireValid(evidence !== undefined, "missing evidence reference");
      requireValid(candidate.draft_review_state === "DRAFT_UNREVIEWED" &&
        evidence.library_file_id === candidate.evidence_library_file_id &&
        evidence.source_url === candidate.source_url_from_evidence &&
        /^KR-BRIDGE-[0-9]{3}-[0-9]{2}$/.test(candidate.bridge_id) &&
        !seenCandidateIds.has(candidate.bridge_id), "invalid/duplicate evidence candidate");
      requireValid(Array.isArray(candidate.source_identifiers) &&
        candidate.source_identifiers.every(x => typeof x === "string" && x.length <= 250),
        "invalid source identifier");
      seenCandidateIds.add(candidate.bridge_id);
      evidenceCandidateCount++;
      // An evidence link can refer to a GitHub PR. Such a link is NOT an
      // official legal source, and is never relabeled as one.
      sources.push({
        candidate_id: candidate.bridge_id, candidate_type: "EVIDENCE_BRIDGE",
        source_record_status: "DRAFT_UNREVIEWED",
        evidence_task_id: evidence.task_id, library_file_id: evidence.library_file_id,
        source_identifiers: distinct(candidate.source_identifiers),
        source_registry_id: null, source_version: null, source_locator: null,
        source_title: null, official_url_candidate: safeOfficialSourceUrl(evidence.source_url),
        publication: "NOT_GRANTED", currentness: "NOT_ESTABLISHED",
        human_review: "NOT_REVIEWED", applicability: "NOT_ESTABLISHED",
      });
      unresolved.push(...(evidence.unresolved ?? []));
    }
    const old = oldCandidatesBySection.get(chapter.section_id);
    if (old) {
      for (const candidate of old.candidates) {
        const record = registry.get(candidate.source_id);
        requireValid(record !== undefined, "missing registry source");
        requireValid(candidate.section_id === chapter.section_id &&
          ["CANDIDATE", "HISTORICAL"].includes(candidate.candidate_status) &&
          !!candidate.candidate_id && !seenCandidateIds.has(candidate.candidate_id) &&
          record.url === candidate.source_url, "legacy source reference/mismatch");
        seenCandidateIds.add(candidate.candidate_id);
        legacyCandidateCount++;
        sources.push({
          candidate_id: candidate.candidate_id, candidate_type: "OLD_SOURCE_CANDIDATE",
          source_record_status: candidate.candidate_status === "HISTORICAL" ? "HISTORICAL" : "CANDIDATE",
          evidence_task_id: null, library_file_id: null,
          source_identifiers: [candidate.source_id], source_registry_id: candidate.source_id,
          source_version: candidate.source_version,
          source_locator: candidate.source_locator, source_title: record.title,
          official_url_candidate: safeOfficialSourceUrl(record.url),
          publication: "NOT_GRANTED", currentness: "NOT_ESTABLISHED",
          human_review: "NOT_REVIEWED", applicability: "NOT_ESTABLISHED",
        });
      }
    }
    const draft = oldDraftBySection.get(chapter.section_id);
    if (draft) {
      for (const statement of draft.draft_statements) {
        requireValid(statement.review_state === "DRAFT_UNREVIEWED" &&
          statement.statement_id.startsWith(serviceId + "." + chapter.section_id + ".") &&
          !seenDraftIds.has(statement.statement_id), "old statement trust boundary");
        seenDraftIds.add(statement.statement_id);
        draftStatementCount++;
      }
      unresolved.push(...draft.gaps.filter(g => g.status === "UNRESOLVED").map(g => g.issue));
    }
    // This is a service-scoped search entrance, NOT a chapter-scoped publication.
    return {
      section_id: chapter.section_id, title: chapter.title,
      questions_to_check: distinct(draft?.intended_user_questions ?? []),
      unresolved: distinct(unresolved),
      source_candidates: sources,
      historical_draft_statement_count: draft?.draft_statements.length ?? 0,
      public_search_href: "/databases/search?service=" + encodeURIComponent(serviceId),
    };
  });
  requireValid(evidenceCandidateCount === bridge.candidate_paragraph_count,
    "bridge candidate count mismatch");
  requireValid([...oldDraftBySection.keys()].every(id => seenSections.has(id)),
    "old draft chapter outside bridge");
  requireValid([...oldCandidatesBySection.keys()].every(id => seenSections.has(id)),
    "legacy source chapter outside bridge");
  const routes = input.publishedServiceRoutes.map(route => {
    requireValid(!!route.source_family && !!route.label &&
      route.href.startsWith("/") && !route.href.startsWith("//") &&
      !route.href.includes("\\") && !/[\u0000-\u001f]/.test(route.href), "unsafe published route");
    return { source_family: route.source_family, label: route.label, href: route.href };
  });
  requireValid(new Set(routes.map(r => r.source_family)).size === routes.length,
    "duplicate published source family");
  return {
    service_id: serviceId, chapters, published_service_routes: routes,
    candidate_count: evidenceCandidateCount, old_source_candidate_count: legacyCandidateCount,
    historical_draft_statement_count: draftStatementCount,
    publication: "BLOCKED", currentness: "NOT_ESTABLISHED",
    human_review: "NOT_REVIEWED", legal_explanations_accepted: 0,
  };
}
