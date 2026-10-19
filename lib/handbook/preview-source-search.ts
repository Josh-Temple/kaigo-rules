/** Literal, service-local search of recorded source metadata for the restricted preview.
 * This does not infer absent locators, currentness, or publication permissions.
 */
export type PreviewSearchSource = {
  candidateId: string;
  sourceName: string | null;
  sourceVersion: string | null;
  sourceLocator: string | null;
};

export function sourceCandidateMatchesQuery(
  source: PreviewSearchSource,
  rawQuery: string,
): boolean {
  const query = rawQuery.trim().toLocaleLowerCase("ja-JP");
  if (!query) return true;
  return [source.candidateId, source.sourceName, source.sourceVersion, source.sourceLocator]
    .some((value) => typeof value === "string" && value.toLocaleLowerCase("ja-JP").includes(query));
}
