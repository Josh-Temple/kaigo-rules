/** Display-only label cleanup. Legal text and uncertainty must remain intact. */
export function readerLabel(value: string): string {
  return value.replace(/（Research Mesh未審査）/gu, "").trim();
}

export function requirementCopy(value: string): string {
  // Only an exact internal prefix is removed; the reader warning is rendered
  // separately. Never remove a sentence about versions, conditions or exceptions.
  return value.replace(/^【Research Mesh隔離候補・法令適合未審査】/u, "");
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
