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
    .replace(/[\s・、。,.!?！？()（）「」『』【】\[\]／/：:;；ー―–—_-]+/g, "");

const stop = new Set([
  "通所介護", "デイサービス", "必要", "ですか", "できますか", "どのくらい",
  "何人", "何を", "どう", "同じ", "職員", "計画書", "事業所"
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
  const terms = new Set();
  for (const value of raw) {
    const compact = normalize(value);
    if (compact.length >= 2 && !stop.has(compact)) terms.add(compact);
    for (const part of String(value).normalize("NFKC").split(/[\s・、。,.!?！？()（）「」『』【】\[\]／/：:;；ー―–—_-]+/)) {
      const token = normalize(part);
      if (token.length >= 2 && !stop.has(token)) terms.add(token);
    }
  }
  return [...terms];
}

function scoreItem(question, item) {
  const terms = searchTerms(question);
  const questionText = normalize(item.question);
  const answerText = normalize(item.answer);
  const topicText = normalize(item.topic);
  const standardText = normalize(item.standard_label);
  let score = scopeBoost[item.service_code] || 0;
  const matched = [];

  for (const term of terms) {
    let termScore = 0;
    if (questionText.includes(term)) termScore += Math.min(8, 3 + term.length);
    if (topicText.includes(term)) termScore += Math.min(5, 2 + term.length / 2);
    if (answerText.includes(term)) termScore += Math.min(3, 1 + term.length / 4);
    if (termScore > 0) {
      score += termScore;
      matched.push(term);
    }
  }

  const hints = categoryHints[question.category] || [];
  if (hints.some((hint) => standardText.includes(normalize(hint)))) score += 2;

  return { score: Math.round(score * 10) / 10, matched };
}

const groups = questions.map((question) => {
  const ranked = corpus
    .map((item) => ({ item, ...scoreItem(question, item) }))
    .filter((entry) => entry.score >= 4 && entry.matched.length > 0)
    .sort((a, b) => b.score - a.score || a.item.id.localeCompare(b.item.id))
    .slice(0, 8)
    .map((entry) => ({
      qa_id: entry.item.id,
      score: entry.score,
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
  format_version: 1,
  corpus_sha256: meta.source_sha256,
  method: "deterministic_phrase_match_v1",
  status: "CANDIDATE_UNREVIEWED",
  candidates: groups,
};

fs.writeFileSync(
  path.join(root, "data", "qa-link-candidates.json"),
  JSON.stringify(output, null, 2) + "\n",
  "utf8"
);

const total = groups.reduce((sum, item) => sum + item.candidates.length, 0);
console.log(`Q&A link candidates generated: ${total} candidates for ${groups.length} questions.`);
