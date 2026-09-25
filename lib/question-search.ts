export type SearchableQuestion = {
  slug: string;
  title: string;
  category?: string;
  aliases?: string[];
  short_answer?: string;
};

const QUESTION_MATCH_THRESHOLD = 0.75;

const synonymGroups = [
  ["看護師", "看護職員", "准看護師"],
  ["生活相談員", "相談員"],
  ["ハンコ", "判子", "押印", "捺印", "印鑑"],
  ["サイン", "署名", "自署"],
  ["bcp", "業務継続計画"],
  ["デイサービス", "通所介護"],
  ["計画書", "通所介護計画"],
  ["機能訓練室", "機能訓練"],
  ["運営規定", "運営規程"],
  ["兼務", "兼ねる", "兼ねられる", "掛け持ち"],
  ["人数", "何人"],
  ["面積", "平米", "平方メートル", "㎡"],
  ["毎年", "年1回", "年間"],
  ["ウェブ", "ホームページ"],
  ["記載", "内容", "項目", "何を書く", "書き方"],
  ["頻度", "何回"],
] as const;

const normalize = (value: string) =>
  value.normalize("NFKC").toLowerCase();

const canonicalize = (value: string) => {
  let result = normalize(value);
  synonymGroups.forEach((group, index) => {
    const marker = `§${index}§`;
    [...group]
      .sort((a, b) => b.length - a.length)
      .forEach((variant) => {
        result = result.split(normalize(variant)).join(marker);
      });
  });
  return result.replace(/[?？!！。、・「」『』（）()\[\]【】\s]/g, "");
};

const bigrams = (value: string) => {
  const output = new Set<string>();
  for (let index = 0; index < value.length - 1; index += 1) {
    output.add(value.slice(index, index + 2));
  }
  return output;
};

const fieldSimilarity = (query: string, value: string) => {
  const q = canonicalize(query);
  const v = canonicalize(value);
  if (!q || !v) return 0;

  const qgrams = bigrams(q);
  const vgrams = bigrams(v);
  if (!qgrams.size || !vgrams.size) return 0;

  let overlap = 0;
  qgrams.forEach((gram) => {
    if (vgrams.has(gram)) overlap += 1;
  });

  const recall = overlap / qgrams.size;
  const precision = overlap / vgrams.size;
  const f1 = recall + precision
    ? (2 * recall * precision) / (recall + precision)
    : 0;
  const containmentBonus = q.includes(v) || v.includes(q) ? 0.5 : 0;
  return f1 + containmentBonus;
};

export const scoreQuestionQuery = (
  query: string,
  question: SearchableQuestion,
) => {
  const aliases = question.aliases || [];
  const aliasScore = aliases.length
    ? Math.max(...aliases.map((alias) => fieldSimilarity(query, alias)))
    : 0;
  const titleScore = fieldSimilarity(query, question.title || "");
  const answerScore = fieldSimilarity(query, question.short_answer || "");

  return aliasScore * 3 + titleScore * 2 + answerScore * 0.3;
};

export const rankQuestionMatches = <T extends SearchableQuestion>(
  questions: T[],
  query: string,
  threshold = QUESTION_MATCH_THRESHOLD,
) => {
  if (!query.trim()) return [];

  return questions
    .map((question, index) => ({
      question,
      index,
      score: scoreQuestionQuery(query, question),
    }))
    .filter((row) => row.score >= threshold)
    .sort((a, b) => b.score - a.score || a.index - b.index)
    .map((row) => row.question);
};
