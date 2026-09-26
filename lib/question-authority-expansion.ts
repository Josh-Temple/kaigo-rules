export type QuestionAuthorityKind = "standard" | "notice" | "qa" | "fee";

export type QuestionAuthorityRelation = {
  from: string;
  relation: string;
  to: string;
};

export type QuestionMatch = {
  slug: string;
  title?: string;
  status?: string;
};

export type AuthorityRecord = {
  id: string;
  [key: string]: unknown;
};

export type QuestionAuthority = {
  kind: QuestionAuthorityKind;
  relation: string;
  targetId: string;
  record: AuthorityRecord;
};

export type QuestionAuthorityGroup = {
  questionSlug: string;
  questionTitle: string;
  authorities: QuestionAuthority[];
};

type ExpandQuestionAuthoritiesInput = {
  questions: QuestionMatch[];
  relations: QuestionAuthorityRelation[];
  rules: AuthorityRecord[];
  notices: AuthorityRecord[];
  qaItems: AuthorityRecord[];
  feeNodes: AuthorityRecord[];
};

export function expandQuestionAuthorities({
  questions,
  relations,
  rules,
  notices,
  qaItems,
  feeNodes,
}: ExpandQuestionAuthoritiesInput): QuestionAuthorityGroup[] {
  const verifiedQuestions = new Map(
    questions
      .filter((question) => question.status === "verified")
      .map((question) => [question.slug, question]),
  );
  if (!verifiedQuestions.size) return [];

  const indexes: Array<{
    kind: QuestionAuthorityKind;
    rows: Map<string, AuthorityRecord>;
  }> = [
    { kind: "standard", rows: new Map(rules.map((row) => [row.id, row])) },
    { kind: "notice", rows: new Map(notices.map((row) => [row.id, row])) },
    { kind: "qa", rows: new Map(qaItems.map((row) => [row.id, row])) },
    { kind: "fee", rows: new Map(feeNodes.map((row) => [row.id, row])) },
  ];

  const grouped = new Map<string, QuestionAuthority[]>();

  for (const edge of relations) {
    if (!edge.from.startsWith("question:")) continue;
    const slug = edge.from.slice("question:".length);
    if (!verifiedQuestions.has(slug)) continue;

    const resolved = indexes
      .map(({ kind, rows }) => ({ kind, record: rows.get(edge.to) }))
      .find((item) => item.record);
    if (!resolved?.record) continue;

    const authorities = grouped.get(slug) || [];
    if (!authorities.some((item) => item.targetId === edge.to)) {
      authorities.push({
        kind: resolved.kind,
        relation: edge.relation,
        targetId: edge.to,
        record: resolved.record,
      });
      grouped.set(slug, authorities);
    }
  }

  return [...verifiedQuestions.entries()]
    .map(([slug, question]) => ({
      questionSlug: slug,
      questionTitle: question.title || slug,
      authorities: grouped.get(slug) || [],
    }))
    .filter((group) => group.authorities.length > 0);
}
