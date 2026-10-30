/** Display transformations only. Canonical source bodies are never rewritten. */
export type FeeTableRow = { duration: string; units: string[] };

/** Recognise a complete 6 × 5 fee table; unexpected text stays in the prose renderer. */
export function basicFeeTable(text: string): FeeTableRow[] | null {
  const lines = text.trim().split(/\r?\n/u);
  // The imported final fee table also retains the following section's standalone heading.
  if (lines.length === 38 && lines.at(-1) === "注") lines.pop();
  if (lines.length !== 37 || !/^[イロハ] /u.test(lines[0])) return null;
  const rows: FeeTableRow[] = [];
  for (let index = 0; index < 6; index++) {
    const offset = 1 + index * 6;
    const heading = new RegExp(`^\\(${index + 1}\\) 所要時間(.+の場合)$`, "u").exec(lines[offset]);
    if (!heading) return null;
    const units: string[] = [];
    for (let care = 1; care <= 5; care++) {
      const match = new RegExp(`^\\([一二三四五]\\) 要介護${care} ([0-9,]+)単位$`, "u").exec(lines[offset + care]);
      if (!match) return null;
      units.push(match[1]);
    }
    rows.push({ duration: heading[1].replace(/の場合$/u, ""), units });
  }
  return rows;
}

/** A locator is a location, not another copy of the substantive provision. */
export function conciseFeeLocator(locator: string): string {
  const match = /^(6 通所介護費 \/ )(\d+|[イロハニホ])(?:\s|$)/u.exec(locator);
  return match ? `${match[1]}${/^\d+$/u.test(match[2]) ? "注" : ""}${match[2]}` : locator;
}

const appliedArticles = new Set(["8", "9", "10", "11", "12", "13", "14", "15", "16", "17", "19", "21", "26", "27", "30-2", "32", "33", "34", "35", "36", "37-2", "38", "52"]);

/** Editorial reading view for the articles explicitly incorporated by article 105. */
export function dayserviceAppliedText(id: string, text: string): string | null {
  const match = /^ordinance37\.article\.([0-9-]+)$/u.exec(id);
  if (!match || !appliedArticles.has(match[1])) return null;
  let result = text.replaceAll("指定訪問入浴介護", "指定通所介護").replaceAll("指定訪問介護", "指定通所介護");
  // These exact personnel terms occur only in the paragraphs listed in article 105.
  if (["8", "27", "30-2", "32", "37-2"].includes(match[1])) result = result.replaceAll("訪問介護員等", "通所介護従業者");
  if (match[1] === "8") result = result.replace("第二十九条", "第百条");
  return result;
}
