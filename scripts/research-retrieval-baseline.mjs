import fs from "node:fs";
import path from "node:path";

const root = process.cwd();
const questions = JSON.parse(
  fs.readFileSync(path.join(root, "data/questions.json"), "utf8"),
);
const rules = JSON.parse(
  fs.readFileSync(path.join(root, "data/rule-nodes.json"), "utf8"),
).filter((node) => node.verification_status === "VERIFIED_CURRENT");

function normalize(text) {
  return String(text ?? "")
    .normalize("NFKC")
    .toLowerCase()
    .replace(/[\s　。、，．・「」『』（）()【】［］\[\]：:；;！？!?／/\\\-–—]/g, "");
}

function ngrams(text, n = 2) {
  const value = normalize(text);
  if (!value) return [];
  if (value.length < n) return [value];

  const grams = [];
  for (let index = 0; index <= value.length - n; index += 1) {
    grams.push(value.slice(index, index + n));
  }
  return grams;
}

function termFrequency(tokens) {
  const counts = new Map();
  for (const token of tokens) {
    counts.set(token, (counts.get(token) ?? 0) + 1);
  }
  return counts;
}

function buildIndex(documents, toText) {
  const termFrequencies = documents.map((document) =>
    termFrequency(ngrams(toText(document))),
  );

  const documentFrequency = new Map();
  for (const frequency of termFrequencies) {
    for (const token of frequency.keys()) {
      documentFrequency.set(
        token,
        (documentFrequency.get(token) ?? 0) + 1,
      );
    }
  }

  const documentCount = documents.length;

  const vectors = termFrequencies.map((frequency) => {
    const vector = new Map();
    let sumSquares = 0;

    for (const [token, count] of frequency) {
      const weight =
        (1 + Math.log(count)) *
        Math.log(
          (documentCount + 1) /
            ((documentFrequency.get(token) ?? 0) + 1) +
            1,
        );
      vector.set(token, weight);
      sumSquares += weight * weight;
    }

    return { vector, norm: Math.sqrt(sumSquares) };
  });

  return {
    documentCount,
    documentFrequency,
    vectors,
  };
}

function rank(query, index) {
  const queryFrequency = termFrequency(ngrams(query));
  const queryVector = new Map();
  let querySumSquares = 0;

  for (const [token, count] of queryFrequency) {
    const weight =
      (1 + Math.log(count)) *
      Math.log(
        (index.documentCount + 1) /
          ((index.documentFrequency.get(token) ?? 0) + 1) +
          1,
      );
    queryVector.set(token, weight);
    querySumSquares += weight * weight;
  }

  const queryNorm = Math.sqrt(querySumSquares);

  return index.vectors
    .map((document, documentIndex) => {
      let dot = 0;
      for (const [token, weight] of queryVector) {
        dot += weight * (document.vector.get(token) ?? 0);
      }

      const score =
        queryNorm && document.norm
          ? dot / (queryNorm * document.norm)
          : 0;

      return { documentIndex, score };
    })
    .sort((left, right) => right.score - left.score);
}

const ruleIndex = buildIndex(rules, (node) =>
  [
    ...(node.topic ?? []),
    ...(node.path ?? []),
    node.official_text ?? "",
  ].join(" "),
);

const faqIndex = buildIndex(questions, (question) =>
  [
    question.title,
    ...(question.aliases ?? []),
    question.short_answer ?? "",
  ].join(" "),
);

const tests = [];

for (let index = 0; index < questions.length; index += 1) {
  const question = questions[index];
  tests.push({
    id: `KQ-${String(index + 1).padStart(3, "0")}`,
    kind: "canonical",
    query: question.title,
    goldSlug: question.slug,
    goldRules: question.rule_node_ids ?? [],
  });
}

for (
  let index = 0;
  index < Math.min(8, questions.length);
  index += 1
) {
  const question = questions[index];
  const alias = question.aliases?.[0];
  if (!alias) continue;

  tests.push({
    id: `KQ-${String(tests.length + 1).padStart(3, "0")}`,
    kind: "paraphrase",
    query: `${alias}について教えてください。`,
    goldSlug: question.slug,
    goldRules: question.rule_node_ids ?? [],
  });
}

let faqHit1 = 0;
let faqHit3 = 0;
let ruleHit1 = 0;
let ruleHit3 = 0;
let ruleHit5 = 0;

const detail = [];

for (const test of tests) {
  const faqRanking = rank(test.query, faqIndex);
  const ruleRanking = rank(test.query, ruleIndex);

  const faqTop3 = faqRanking
    .slice(0, 3)
    .map(({ documentIndex }) => questions[documentIndex].slug);

  const ruleTop5 = ruleRanking
    .slice(0, 5)
    .map(({ documentIndex }) => rules[documentIndex].id);

  const ruleHit = (k) =>
    ruleTop5
      .slice(0, k)
      .some((id) => test.goldRules.includes(id));

  if (faqTop3[0] === test.goldSlug) faqHit1 += 1;
  if (faqTop3.includes(test.goldSlug)) faqHit3 += 1;
  if (ruleHit(1)) ruleHit1 += 1;
  if (ruleHit(3)) ruleHit3 += 1;
  if (ruleHit(5)) ruleHit5 += 1;

  detail.push({
    id: test.id,
    kind: test.kind,
    query: test.query,
    gold_question: test.goldSlug,
    faq_top1: faqTop3[0],
    faq_hit1: faqTop3[0] === test.goldSlug,
    rule_top1: ruleTop5[0],
    rule_hit1: ruleHit(1),
    rule_hit3: ruleHit(3),
    rule_hit5: ruleHit(5),
    rule_top5: ruleTop5,
  });
}

const divide = (value) => value / tests.length;

console.log(
  JSON.stringify(
    {
      method: "deterministic char-bigram TF-IDF cosine baseline",
      corpus: {
        verified_questions: questions.length,
        verified_rule_nodes: rules.length,
      },
      tests: tests.length,
      metrics: {
        faq_hit_at_1: divide(faqHit1),
        faq_hit_at_3: divide(faqHit3),
        raw_rule_hit_at_1: divide(ruleHit1),
        raw_rule_hit_at_3: divide(ruleHit3),
        raw_rule_hit_at_5: divide(ruleHit5),
      },
      limitations: [
        "Seed questions are derived from the existing verified question titles and aliases.",
        "This is a retrieval hit test, not answer-generation accuracy.",
        "The corpus is intentionally limited to VERIFIED_CURRENT rule nodes.",
        "Results must not be treated as production-search performance.",
      ],
      detail,
    },
    null,
    2,
  ),
);
