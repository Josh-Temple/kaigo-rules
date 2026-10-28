/** Display-only label cleanup. Legal text and uncertainty must remain intact. */
export function readerLabel(value: string): string {
  return value.replace(/（Research Mesh未審査）/gu, "").trim();
}

/** Navigation changes presentation only: it does not change the chapter's role IDs or content. */
export function isStaffingScopeOrException(title: string): boolean {
  return /利用者数|算定方法|算定対象|サテライト|特例|例外|ユニット型|基準該当|共生型|一体運営|提供単位|配置の計算/u.test(title);
}

const aspectHeadings = {
  placement: "配置・員数", qualification: "資格", concurrency: "兼務",
  shifts: "勤務体制", exception: "条件・例外", other: "確認事項",
} as const;

/** Use only the existing aspect when an authored heading contains no distinction. */
export function readerRequirementTitle(
  title: string, aspect: keyof typeof aspectHeadings, sameAspectIndex: number, sameAspectCount: number,
): string {
  const clean = readerLabel(title);
  if (!/^(確認事項|要件|確認すること)$/u.test(clean)) return clean;
  const label = aspectHeadings[aspect];
  return sameAspectCount > 1 ? `${label}（${sameAspectIndex + 1}）` : label;
}

/** Never promote a machine identifier into a visible source title. */
export function readerEvidenceTitle(title: string): { label: string; technical: boolean } {
  const technical = /^(?:data|docs|scripts|tests)\/[A-Za-z0-9_./-]+(?:\.(?:json|md|pdf|txt))?$/u.test(title)
    || /^(?:[a-f0-9]{40}|[a-f0-9]{64})$/iu.test(title);
  return { label: technical ? "資料識別情報（名称未確認）" : readerLabel(title), technical };
}

/** Only navigable HTTP(S) URLs can be rendered as evidence links. */
export function safeHandbookEvidenceUrl(value?: string): string | null {
  if (!value || value !== value.trim() || /[\u0000-\u001f\u007f]/u.test(value)) return null;
  try {
    const url = new URL(value);
    if (!["http:", "https:"].includes(url.protocol) || !url.hostname || url.username || url.password) return null;
    return url.href;
  } catch {
    return null;
  }
}

/** Hide only an isolated repository file path, never surrounding legal conditions. */
export function readerEvidenceLocator(value: string): string {
  const standalonePath = /^(?:data|docs|scripts|tests)\/[A-Za-z0-9_.\/-]+\.(?:json|md|txt)$/u.test(value.trim());
  return standalonePath ? "原典の該当箇所を確認中" : value;
}

export function requirementCopy(value: string): string {
  // Only an exact internal prefix is removed; the reader warning is rendered
  // separately. Never remove a sentence about versions, conditions or exceptions.
  return value.replace(/^【Research Mesh隔離候補・法令適合未審査】/u, "");
}

/**
 * An authority category applies only to the exact authored text fragment, not
 * to the rest of a paragraph or to all text citing a source. The source
 * reference must be present before an editor can mark a fragment classified.
 */
export type HandbookAuthoritySegment = {
  text: string;
  authority: "national_law" | "national_standard" | "national_interpretation"
    | "national_qa" | "national_fee_notice" | "municipal_ordinance"
    | "municipal_regulation" | "municipal_handbook";
  source_ref: string;
  jurisdiction?: string;
};
export type HandbookDisplaySegment =
  | HandbookAuthoritySegment
  | { text: string; authority: "unclassified" };

/**
 * A verified source is a checked evidence row for the requirement itself, not
 * a URL or keyword found elsewhere in the repository. Source references are
 * exact URLs because HandbookEvidence has no stable source ID today.
 */
export type HandbookAuthorityEvidence = {
  kind: string;
  url?: string;
  verification_state: string;
};

const categoryEvidenceKinds: Record<HandbookAuthoritySegment["authority"], string> = {
  national_law: "national_law",
  national_standard: "national_standard",
  national_interpretation: "national_interpretation",
  national_qa: "national_qa",
  national_fee_notice: "national_fee_notice",
  municipal_ordinance: "yokohama_ordinance",
  municipal_regulation: "yokohama_regulation",
  municipal_handbook: "yokohama_handbook",
};

export function splitDayserviceRegionalText(
  value: string, authored?: readonly HandbookAuthoritySegment[],
  verifiedEvidence?: readonly HandbookAuthorityEvidence[],
): { segments: HandbookDisplaySegment[]; classified: boolean } {
  const unresolved = (): { segments: HandbookDisplaySegment[]; classified: false } =>
    ({ segments: [{ text: value, authority: "unclassified" }], classified: false });
  if (!authored?.length) return unresolved();
  const national = new Set([
    "national_law", "national_standard", "national_interpretation", "national_qa", "national_fee_notice",
  ]);
  const local = new Set(["municipal_ordinance", "municipal_regulation", "municipal_handbook"]);
  for (const segment of authored) {
    if (!segment || typeof segment.text !== "string" || !segment.text ||
        typeof segment.source_ref !== "string" || !segment.source_ref.trim()) return unresolved();
    if (national.has(segment.authority)) {
      if (segment.jurisdiction) return unresolved();
    } else if (local.has(segment.authority)) {
      if (!segment.jurisdiction?.trim()) return unresolved();
    } else return unresolved();
  }
  // The public UI always supplies the requirement's actual evidence rows. A
  // self-authored source_ref alone must never turn unreviewed material into an
  // apparently authoritative national or local rule.
  if (verifiedEvidence !== undefined && !authored.every(segment => {
    // The current evidence schema only models Yokohama municipal sources.
    // Other municipalities stay unclassified until their own evidence exists.
    if (segment.authority.startsWith("municipal_") && !segment.jurisdiction?.includes("横浜市")) return false;
    return verifiedEvidence.some(evidence =>
      evidence.verification_state === "PRIMARY_TEXT_CHECKED_SCOPED" &&
      typeof evidence.url === "string" &&
      evidence.url.trim() === segment.source_ref.trim() &&
      evidence.kind === categoryEvidenceKinds[segment.authority]
    );
  })) return unresolved();
  // Exact equality catches missing clauses, punctuation changes and reordering.
  // Never guess the boundary from a municipality name in free text.
  if (authored.map(segment => segment.text).join("") !== value) return unresolved();
  return { segments: [...authored], classified: true };
}

/**
 * Only a complete, standalone technical reference can leave the reader body.
 * Mixed paragraphs are never split: everything after a path may be a condition.
 * Returning the original strings preserves their correspondence with the source.
 */
export function separateHandbookParagraphs(paragraphs: string[]): { reader: string[]; editorial: string[] } {
  const reader: string[] = [];
  const editorial: string[] = [];
  for (const paragraph of paragraphs) {
    const technicalOnly = /^(?:出典候補：|参照ファイル：)\s*data\/[A-Za-z0-9_./-]+\.json[。]?$/u.test(paragraph);
    (technicalOnly ? editorial : reader).push(paragraph);
  }
  return { reader, editorial };
}
