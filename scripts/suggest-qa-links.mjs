import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(here, "..");
const read = (name) => JSON.parse(fs.readFileSync(path.join(root, "data", name), "utf8"));

const questions = read("questions.json");
const corpus = read("qa-corpus.json");
const meta = read("qa-corpus-meta.json");

const normalize = (value = "") =>
  String(value)
    .normalize("NFKC")
    .toLowerCase()
    .replace(/[\s・、。,.!?！？()（）「」『』【】\[\]／/：:;；―–—_-]+/g, "");

const splitParts = (value = "") =>
  String(value)
    .normalize("NFKC")
    .split(/[\s・、。,.!?！？()（）「」『』【】\[\]／/：:;；―–—_-]+/)
    .map(normalize)
    .filter(Boolean);

const genericTerms = new Set([
  "必要", "ですか", "できますか", "どのくらい", "何人", "何を", "どう", "同じ",
  "職員", "事業所", "サービス", "配置", "配置基準", "内容", "記載", "研修", "訓練",
  "年間", "頻度", "計画書", "利用者"
]);

const specificShortTerms = new Set([
  "管理者", "兼務", "食堂", "面積", "定員", "署名", "サイン", "押印", "捺印",
  "ハンコ", "印鑑", "掲示", "bcp"
]);

const categoryHints = {
  "人員・勤務": ["人員", "勤務", "従業者"],
  "設備": ["設備"],
  "運営": ["運営"],
  "計画・記録": ["運営", "計画", "記録"],
  "説明・同意・署名": ["運営", "同意", "説明"],
  "研修・委員会・訓練": ["運営", "研修", "訓練"],
};

const scopeBoost = { "16": 2, "06": 1.5, "02": 1, "01": 0.5 };

function searchTerms(question) {
  const raw = [question.title, ...(question.aliases || [])];
  const values = new Set();

  for (const value of raw) {
    const compact = normalize(value);
    if (compact.length >= 4 && !compact.includes("通所介護で")) values.add(compact);
    for (const token of splitParts(value)) {
      if (token.length >= 2) values.add(token);
    }
  }

  return [...values].map((value) => ({
    value,
    generic: genericTerms.has(value) || value === "通所介護" || value === "デイサービス",
    anchor: value.length >= 4 || specificShortTerms.has(value),
  }));
}

function scoreItem(question, item) {
  const terms = searchTerms(question);
  const questionText = normalize(item.question);
  const answerText = normalize(item.answer);
  const topicText = normalize(item.topic);
  const standardText = normalize(item.standard_label);
  let score = scopeBoost[item.service_code] || 0;
  const matched = [];
  const anchors = [];

  for (const term of terms) {
    let termScore = 0;
    if (questionText.includes(term.value)) termScore += term.generic ? 2 : Math.min(9, 4 + term.value.length);
    if (topicText.includes(term.value)) termScore += term.generic ? 1.5 : Math.min(6, 2 + term.value.length / 2);
    if (answerText.includes(term.value)) termScore += term.generic ? 0.5 : Math.min(3, 1 + term.value.length / 4);

    if (termScore > 0) {
      score += termScore;
      matched.push(term.value);
      if (term.anchor && !term.generic) anchors.push(term.value);
    }
  }

  if (!anchors.length) return { score: 0, matched: [], anchors: [] };

  const hints = categoryHints[question.category] || [];
  if (hints.some((hint) => standardText.includes(normalize(hint)))) score += 2;

  if (item.standard_code === "4" && question.category !== "報酬") score -= 4;

  return {
    score: Math.round(score * 10) / 10,
    matched: [...new Set(matched)],
    anchors: [...new Set(anchors)],
  };
}

const groups = questions.map((question) => {
  const ranked = corpus
    .map((item) => ({ item, ...scoreItem(question, item) }))
    .filter((entry) => entry.score >= 6 && entry.anchors.length > 0)
    .sort((a, b) =>
      b.anchors.length - a.anchors.length ||
      b.score - a.score ||
      a.item.id.localeCompare(b.item.id)
    )
    .slice(0, 5)
    .map((entry) => ({
      qa_id: entry.item.id,
      score: entry.score,
      anchor_terms: entry.anchors,
      matched_terms: entry.matched,
      scope: entry.item.scope,
      standard_label: entry.item.standard_label,
      topic: entry.item.topic,
      question_preview: entry.item.question.slice(0, 180),
      status: "CANDIDATE_UNREVIEWED",
    }));

  return {
    question_slug: question.slug,
    question_title: question.title,
    status: "CANDIDATE_UNREVIEWED",
    candidates: ranked,
  };
});

const output = {
  format_version: 2,
  corpus_sha256: meta.source_sha256,
  method: "deterministic_anchor_match_v2",
  status: "CANDIDATE_UNREVIEWED",
  candidates: groups,
};

fs.writeFileSync(
  path.join(root, "data", "qa-link-candidates.json"),
  JSON.stringify(output, null, 2) + "\n",
  "utf8"
);

const total = groups.reduce((sum, item) => sum + item.candidates.length, 0);
const empty = groups.filter((item) => item.candidates.length === 0).map((item) => item.question_slug);
console.log(`Q&A link candidates generated: ${total} candidates for ${groups.length} questions.`);
if (empty.length) console.log(`No candidate above threshold: ${empty.join(", ")}`);
