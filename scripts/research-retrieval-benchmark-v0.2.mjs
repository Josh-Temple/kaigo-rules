import fs from "node:fs";
import path from "node:path";

const root = process.cwd();

const questions = JSON.parse(fs.readFileSync(path.join(root, "data/questions.json"), "utf8"));
const rules = JSON.parse(fs.readFileSync(path.join(root, "data/rule-nodes.json"), "utf8"))
  .filter((x) => x.verification_status === "VERIFIED_CURRENT");
const notices = JSON.parse(fs.readFileSync(path.join(root, "data/notice-nodes.json"), "utf8"))
  .filter((x) => ["VERIFIED_SOURCE_TEXT", "KNOWN_AFTER_TEXT"].includes(x.verification_status));
const qa = JSON.parse(fs.readFileSync(path.join(root, "data/qa-items.json"), "utf8"))
  .filter((x) => x.status === "STRUCTURED");
const benchmark = JSON.parse(
  fs.readFileSync(
    path.join(root, "docs/kaigo-ops/research/issues/information-search/benchmark/benchmark-v0.2.json"),
    "utf8",
  ),
);

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
  for (let i = 0; i <= value.length - n; i += 1) grams.push(value.slice(i, i + n));
  return grams;
}

function tf(tokens) {
  const counts = new Map();
  for (const token of tokens) counts.set(token, (counts.get(token) ?? 0) + 1);
  return counts;
}

function buildIndex(documents, toText) {
  const frequencies = documents.map((doc) => tf(ngrams(toText(doc))));
  const df = new Map();

  for (const frequency of frequencies) {
    for (const token of frequency.keys()) df.set(token, (df.get(token) ?? 0) + 1);
  }

  const N = documents.length;
  const vectors = frequencies.map((frequency) => {
    const vector = new Map();
    let sumSquares = 0;

    for (const [token, count] of frequency) {
      const weight =
        (1 + Math.log(count)) *
        Math.log((N + 1) / ((df.get(token) ?? 0) + 1) + 1);
      vector.set(token, weight);
      sumSquares += weight * weight;
    }

    return { vector, norm: Math.sqrt(sumSquares) };
  });

  return { N, df, vectors };
}

function rank(query, index) {
  const frequency = tf(ngrams(query));
  const queryVector = new Map();
  let querySumSquares = 0;

  for (const [token, count] of frequency) {
    const weight =
      (1 + Math.log(count)) *
      Math.log((index.N + 1) / ((index.df.get(token) ?? 0) + 1) + 1);
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
      return {
        documentIndex,
        score:
          queryNorm && document.norm
            ? dot / (queryNorm * document.norm)
            : 0,
      };
    })
    .sort((a, b) => b.score - a.score);
}

function questionText(x) {
  return [
    x.title,
    ...(x.aliases ?? []),
    x.short_answer ?? "",
    ...(x.practical_steps ?? []),
    ...(x.cautions ?? []),
  ].join(" ");
}

function questionBundle(x) {
  return new Set([
    ...(x.rule_node_ids ?? []),
    ...(x.notice_node_ids ?? []),
    ...(x.qa_item_ids ?? []),
  ]);
}

const sourceDocs = [
  ...rules.map((x) => ({
    id: x.id,
    type: "rule",
    text: [...(x.topic ?? []), ...(x.path ?? []), x.official_text ?? ""].join(" "),
  })),
  ...notices.map((x) => ({
    id: x.id,
    type: "notice",
    text: [...(x.path ?? []), x.editorial_summary ?? "", x.official_text ?? ""].join(" "),
  })),
  ...qa.map((x) => ({
    id: x.id,
    type: "qa",
    text: [...(x.topic ?? []), x.question_summary ?? "", x.answer_summary ?? ""].join(" "),
  })),
];

const faqIndex = buildIndex(questions, questionText);
const sourceIndex = buildIndex(sourceDocs, (x) => x.text);

const detail = [];
for (const test of benchmark.retrieval_tests) {
  const faqTop3 = rank(test.question, faqIndex)
    .slice(0, 3)
    .map(({ documentIndex }) => questions[documentIndex]);

  const sourceTop5 = rank(test.question, sourceIndex)
    .slice(0, 5)
    .map(({ documentIndex }) => sourceDocs[documentIndex].id);

  const directHits = test.gold_sources.filter((id) => sourceTop5.includes(id));
  const directRecall = directHits.length / test.gold_sources.length;

  const bundleTop1 = questionBundle(faqTop3[0]);
  const bundleTop3 = new Set(
    faqTop3.flatMap((x) => [...questionBundle(x)]),
  );

  const bundle1Hits = test.gold_sources.filter((id) => bundleTop1.has(id));
  const bundle3Hits = test.gold_sources.filter((id) => bundleTop3.has(id));

  detail.push({
    id: test.id,
    kind: test.kind,
    question: test.question,
    faq_top1: faqTop3[0].slug,
    faq_top3: faqTop3.map((x) => x.slug),
    faq_hit_at_1: test.gold_faq.includes(faqTop3[0].slug),
    faq_hit_at_3: faqTop3.some((x) => test.gold_faq.includes(x.slug)),
    direct_source_top5: sourceTop5,
    direct_source_recall_at_5: directRecall,
    direct_source_complete_at_5: directRecall === 1,
    faq_bundle_top1_recall: bundle1Hits.length / test.gold_sources.length,
    faq_bundle_top1_complete: bundle1Hits.length === test.gold_sources.length,
    faq_bundle_top3_union_recall: bundle3Hits.length / test.gold_sources.length,
    faq_bundle_top3_union_complete: bundle3Hits.length === test.gold_sources.length,
  });
}

function mean(values) {
  return values.reduce((a, b) => a + b, 0) / values.length;
}

function summarize(rows) {
  return {
    n: rows.length,
    faq_hit_at_1: mean(rows.map((x) => (x.faq_hit_at_1 ? 1 : 0))),
    faq_hit_at_3: mean(rows.map((x) => (x.faq_hit_at_3 ? 1 : 0))),
    direct_source_mean_recall_at_5: mean(rows.map((x) => x.direct_source_recall_at_5)),
    direct_source_complete_at_5: mean(rows.map((x) => (x.direct_source_complete_at_5 ? 1 : 0))),
    faq_bundle_top1_mean_recall: mean(rows.map((x) => x.faq_bundle_top1_recall)),
    faq_bundle_top1_complete: mean(rows.map((x) => (x.faq_bundle_top1_complete ? 1 : 0))),
    faq_bundle_top3_union_mean_recall: mean(rows.map((x) => x.faq_bundle_top3_union_recall)),
    faq_bundle_top3_union_complete: mean(rows.map((x) => (x.faq_bundle_top3_union_complete ? 1 : 0))),
  };
}

const result = {
  benchmark_version: benchmark.version,
  method: "deterministic character-bigram TF-IDF cosine baseline",
  corpus: {
    verified_questions: questions.length,
    verified_rule_nodes: rules.length,
    eligible_notice_fragments: notices.length,
    structured_qa_items: qa.length,
    direct_source_documents: sourceDocs.length,
  },
  overall: summarize(detail),
  by_kind: {
    unseen: summarize(detail.filter((x) => x.kind === "unseen")),
    multi_source: summarize(detail.filter((x) => x.kind === "multi_source")),
  },
  safety_tests: {
    count: benchmark.safety_tests.length,
    note: "Safety tests require answer-level evaluation and are not scored by this retrieval-only script.",
  },
  limitations: [
    "Queries are manually authored from already verified coverage and are not sampled from production logs.",
    "The benchmark is small.",
    "Retrieval success does not prove answer correctness.",
    "KNOWN_AFTER_TEXT notice fragments are included only where they are already connected to verified questions; their status must remain visible at answer time.",
  ],
  detail,
};

console.log(JSON.stringify(result, null, 2));
