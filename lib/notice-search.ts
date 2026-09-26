export type SearchableNotice = {
  id: string;
  document?: string;
  service?: string;
  path?: string[];
  verification_status?: string;
  editorial_summary?: string;
  source_ids?: string[];
};

export type NoticeQuestion = {
  slug: string;
  status?: string;
  notice_node_ids?: string[];
};

export type NoticeSource = {
  id: string;
  [key: string]: unknown;
};

type SearchableNoticeInput = {
  notices: SearchableNotice[];
  questions: NoticeQuestion[];
  sources: NoticeSource[];
};

export function getSearchableNotices({
  notices,
  questions,
  sources,
}: SearchableNoticeInput): SearchableNotice[] {
  const publishedNoticeIds = new Set(
    questions
      .filter((question) => question.status === "verified")
      .flatMap((question) => question.notice_node_ids || []),
  );
  const sourceIds = new Set(sources.map((source) => source.id));

  return notices.filter((notice) => {
    const evidenceIds = notice.source_ids || [];
    return (
      publishedNoticeIds.has(notice.id) &&
      notice.verification_status !== "UNKNOWN" &&
      Boolean(notice.editorial_summary?.trim()) &&
      evidenceIds.length > 0 &&
      evidenceIds.every((sourceId) => sourceIds.has(sourceId))
    );
  });
}

const normalize = (value: string) =>
  value.normalize("NFKC").toLowerCase().replace(/\s+/g, " ").trim();

export function matchesNoticeTerms(
  notice: SearchableNotice,
  expandedTerms: string[][],
): boolean {
  const haystack = normalize(
    [
      notice.document || "",
      notice.service || "",
      ...(notice.path || []),
      notice.editorial_summary || "",
    ].join(" "),
  );

  return expandedTerms.every((alternatives) =>
    alternatives.some((term) => haystack.includes(normalize(term))),
  );
}
