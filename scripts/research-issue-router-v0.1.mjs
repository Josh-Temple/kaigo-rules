import fs from "node:fs";
import path from "node:path";

const root = process.cwd();
const readJson = (relative) =>
  JSON.parse(fs.readFileSync(path.join(root, relative), "utf8"));

const questions = readJson("data/questions.json");
const rules = readJson("data/rule-nodes.json")
  .filter((x) => x.verification_status === "VERIFIED_CURRENT");
const notices = readJson("data/notice-nodes.json")
  .filter((x) =>
    ["VERIFIED_SOURCE_TEXT", "KNOWN_AFTER_TEXT"].includes(x.verification_status),
  );
const qaItems = readJson("data/qa-items.json")
  .filter((x) => x.status === "STRUCTURED");

const remunerationReview = readJson("data/remuneration-review.json");
const unitPriceReview = readJson("data/unit-price-review.json");
const feeGuidanceReview = readJson("data/fee-guidance-review.json");
const qaCorpusMeta = readJson("data/qa-corpus-meta.json");

const benchmark = readJson(
  "docs/kaigo-ops/research/issues/information-search/benchmark/benchmark-v0.3.json",
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
  const result = [];
  for (let i = 0; i <= value.length - n; i += 1) {
    result.push(value.slice(i, i + n));
  }
  return result;
}

function termFrequency(tokens) {
  const counts = new Map();
  for (const token of tokens) {
    counts.set(token, (counts.get(token) ?? 0) + 1);
  }
  return counts;
}

function buildIndex(documents, toText) {
  const frequencies = documents.map((document) =>
    termFrequency(ngrams(toText(document))),
  );

  const documentFrequency = new Map();
  for (const frequency of frequencies) {
    for (const token of frequency.keys()) {
      documentFrequency.set(
        token,
        (documentFrequency.get(token) ?? 0) + 1,
      );
    }
  }

  const documentCount = documents.length;
  const vectors = frequencies.map((frequency) => {
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
  const frequency = termFrequency(ngrams(query));
  const queryVector = new Map();
  let querySumSquares = 0;

  for (const [token, count] of frequency) {
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

      return {
        documentIndex,
        score:
          queryNorm && document.norm
            ? dot / (queryNorm * document.norm)
            : 0,
      };
    })
    .sort((left, right) => right.score - left.score);
}

function questionText(question) {
  return [
    question.title,
    ...(question.aliases ?? []),
    question.short_answer ?? "",
    ...(question.practical_steps ?? []),
    ...(question.cautions ?? []),
  ].join(" ");
}

function questionBundle(question) {
  return [
    ...(question.rule_node_ids ?? []),
    ...(question.notice_node_ids ?? []),
    ...(question.qa_item_ids ?? []),
  ];
}

const faqIndex = buildIndex(questions, questionText);

const sourceDocuments = [
  ...rules.map((x) => ({
    id: x.id,
    type: "rule",
    text: [
      ...(x.topic ?? []),
      ...(x.path ?? []),
      x.official_text ?? "",
    ].join(" "),
  })),
  ...notices.map((x) => ({
    id: x.id,
    type: "notice",
    text: [
      ...(x.path ?? []),
      x.editorial_summary ?? "",
      x.official_text ?? "",
    ].join(" "),
  })),
  ...qaItems.map((x) => ({
    id: x.id,
    type: "qa",
    text: [
      ...(x.topic ?? []),
      x.question_summary ?? "",
      x.answer_summary ?? "",
    ].join(" "),
  })),
];

const sourceIndex = buildIndex(sourceDocuments, (x) => x.text);

function route(query) {
  const ranked = rank(query, faqIndex)
    .slice(0, 3)
    .map(({ documentIndex, score }) => ({
      question: questions[documentIndex],
      score,
    }));

  return ranked;
}

function sourceUnion(rankedQuestions) {
  return [
    ...new Set(
      rankedQuestions.flatMap(({ question }) =>
        questionBundle(question),
      ),
    ),
  ];
}

function selectAnswerComponents(ranked) {
  if (!ranked.length) return [];
  const topScore = ranked[0].score;
  return ranked
    .filter(({ score }, index) =>
      index === 0 || score >= topScore * 0.8,
    )
    .map(({ question }) => ({
      slug: question.slug,
      answer: question.short_answer,
    }));
}

function guardDecision(query) {
  const compact = normalize(query);

  if (
    /(指定申請|締切|窓口|事前相談)/.test(query) &&
    /(市|区|町|村)/.test(query)
  ) {
    return {
      decision: "ABSTAIN_LOCAL",
      reason: "LOCAL_RULE_REQUIRES_AUTHORITY_SOURCE",
    };
  }

  if (/地域密着型通所介護|共生型通所介護/.test(query)) {
    return {
      decision: "ABSTAIN_SCOPE",
      reason: "OUT_OF_INITIAL_SCOPE",
    };
  }

  if (
    /(報酬|加算)/.test(query) &&
    /(全|一覧|確定|要件)/.test(query) &&
    remunerationReview.review_status !== "COMPLETE"
  ) {
    return {
      decision: "ABSTAIN_UNREVIEWED",
      reason: "REMUNERATION_HUMAN_REVIEW_INCOMPLETE",
    };
  }

  if (
    /一単位単価/.test(query) &&
    unitPriceReview.review_status !== "COMPLETE"
  ) {
    return {
      decision: "ABSTAIN_UNREVIEWED",
      reason: "UNIT_PRICE_HUMAN_REVIEW_INCOMPLETE",
    };
  }

  if (
    /経過措置/.test(query) &&
    feeGuidanceReview.review_status !== "COMPLETE"
  ) {
    return {
      decision: "ABSTAIN_STALE",
      reason: "GUIDANCE_CURRENTNESS_REVIEW_INCOMPLETE",
    };
  }

  if (
    /Q&A/.test(query) &&
    /(843|確認済|取り込)/.test(query)
  ) {
    return {
      decision: "ANSWER_METADATA",
      reason: "QA_CORPUS_STATUS",
      metadata: {
        review_status: qaCorpusMeta.review_status,
        rows_included: qaCorpusMeta.rows_included,
      },
    };
  }

  const ranked = route(query);
  const margin =
    ranked.length >= 2
      ? ranked[0].score - ranked[1].score
      : 1;

  if (
    compact.length <= 9 &&
    margin < 0.05
  ) {
    return {
      decision: "CLARIFY",
      reason: "SHORT_AMBIGUOUS_QUERY",
      candidates: ranked.slice(0, 2).map(({ question }) => question.slug),
      margin,
    };
  }

  return {
    decision: "ANSWER_VERIFIED",
    reason: "VERIFIED_ISSUE_ROUTING",
    top3: ranked.map(({ question, score }) => ({
      slug: question.slug,
      score,
    })),
    sources: sourceUnion(ranked),
    answer_components: selectAnswerComponents(ranked),
  };
}

function ratio(numerator, denominator) {
  return denominator ? numerator / denominator : 0;
}

const retrievalResults = benchmark.retrieval_tests.map((test) => {
  const rankedFaq = route(test.question);
  const faqTop3 = rankedFaq.map(({ question }) => question.slug);

  const sourceTop5 = rank(test.question, sourceIndex)
    .slice(0, 5)
    .map(({ documentIndex }) => sourceDocuments[documentIndex].id);

  const linkedSources = sourceUnion(rankedFaq);

  const directHits = test.gold_sources.filter((id) =>
    sourceTop5.includes(id),
  );
  const linkedHits = test.gold_sources.filter((id) =>
    linkedSources.includes(id),
  );

  return {
    id: test.id,
    kind: test.kind,
    faq_top1: faqTop3[0],
    faq_top3: faqTop3,
    faq_hit_at_1: test.gold_faq.includes(faqTop3[0]),
    faq_hit_at_3: faqTop3.some((slug) =>
      test.gold_faq.includes(slug),
    ),
    direct_source_recall_at_5: ratio(
      directHits.length,
      test.gold_sources.length,
    ),
    direct_source_complete_at_5:
      directHits.length === test.gold_sources.length,
    linked_source_recall: ratio(
      linkedHits.length,
      test.gold_sources.length,
    ),
    linked_source_complete:
      linkedHits.length === test.gold_sources.length,
  };
});

function summarize(rows) {
  const mean = (selector) =>
    ratio(
      rows.reduce((sum, row) => sum + selector(row), 0),
      rows.length,
    );

  return {
    n: rows.length,
    faq_hit_at_1: mean((x) => (x.faq_hit_at_1 ? 1 : 0)),
    faq_hit_at_3: mean((x) => (x.faq_hit_at_3 ? 1 : 0)),
    direct_source_mean_recall_at_5: mean(
      (x) => x.direct_source_recall_at_5,
    ),
    direct_source_complete_at_5: mean(
      (x) => (x.direct_source_complete_at_5 ? 1 : 0),
    ),
    linked_source_mean_recall: mean(
      (x) => x.linked_source_recall,
    ),
    linked_source_complete: mean(
      (x) => (x.linked_source_complete ? 1 : 0),
    ),
  };
}

const safetyResults = benchmark.safety_tests.map((test) => {
  const result = guardDecision(test.question);

  const decisionOk =
    result.decision === test.expected_decision;

  const faqOk =
    !test.expected_faq ||
    test.expected_faq.every((slug) => {
      if (result.decision === "CLARIFY") {
        return (result.candidates ?? []).includes(slug);
      }
      if (result.decision === "ANSWER_VERIFIED") {
        return (result.top3 ?? []).some((x) => x.slug === slug);
      }
      return false;
    });

  const sourceOk =
    !test.expected_sources ||
    test.expected_sources.every((id) =>
      (result.sources ?? []).includes(id),
    );

  const metadataOk =
    !test.expected_metadata_review_status ||
    result.metadata?.review_status ===
      test.expected_metadata_review_status;

  return {
    id: test.id,
    risk: test.risk,
    expected_decision: test.expected_decision,
    actual_decision: result.decision,
    decision_ok: decisionOk,
    faq_ok: faqOk,
    source_ok: sourceOk,
    metadata_ok: metadataOk,
    pass:
      decisionOk &&
      faqOk &&
      sourceOk &&
      metadataOk,
    result,
  };
});

const kinds = [
  ...new Set(
    benchmark.retrieval_tests.map((test) => test.kind),
  ),
];

const output = {
  benchmark_version: benchmark.version,
  cases: benchmark.counts,
  retrieval: {
    overall: summarize(retrievalResults),
    by_kind: Object.fromEntries(
      kinds.map((kind) => [
        kind,
        summarize(
          retrievalResults.filter((row) => row.kind === kind),
        ),
      ]),
    ),
  },
  safety: {
    passed: safetyResults.filter((row) => row.pass).length,
    total: safetyResults.length,
    pass_rate: ratio(
      safetyResults.filter((row) => row.pass).length,
      safetyResults.length,
    ),
    note:
      "This is deterministic guard/decision evaluation, not a full human review of generated prose.",
  },
  limitations: [
    "The 39 retrieval queries were authored against the currently verified coverage rather than sampled from production user logs.",
    "The corpus is small.",
    "Safety guards are explicit deterministic rules and must be tested against broader adversarial and benign queries before production use.",
    "Linked-source completeness does not prove that final prose preserves every condition.",
    "No RAG or free-form answer generation is evaluated here.",
  ],
  retrieval_results: retrievalResults,
  safety_results: safetyResults,
};

console.log(JSON.stringify(output, null, 2));
