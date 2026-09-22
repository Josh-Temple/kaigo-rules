import fs from "node:fs";
import path from "node:path";

const root = process.cwd();
const readJson = (relative) =>
  JSON.parse(fs.readFileSync(path.join(root, relative), "utf8"));

const benchmark = readJson(
  "docs/kaigo-ops/research/issues/information-search/benchmark/coverage-gap-v0.1.json",
);
const questions = readJson("data/questions.json");
const startupSteps = readJson("data/startup-steps.json");
const remunerationReview = readJson("data/remuneration-review.json");
const unitPriceReview = readJson("data/unit-price-review.json");
const feeGuidanceReview = readJson("data/fee-guidance-review.json");
const qaCorpusMeta = readJson("data/qa-corpus-meta.json");

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

function tf(tokens) {
  const map = new Map();
  for (const token of tokens) {
    map.set(token, (map.get(token) ?? 0) + 1);
  }
  return map;
}

function buildIndex(documents, toText) {
  const frequencies = documents.map((doc) =>
    tf(ngrams(toText(doc))),
  );
  const df = new Map();

  for (const frequency of frequencies) {
    for (const token of frequency.keys()) {
      df.set(token, (df.get(token) ?? 0) + 1);
    }
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
  let sumSquares = 0;

  for (const [token, count] of frequency) {
    const weight =
      (1 + Math.log(count)) *
      Math.log((index.N + 1) / ((index.df.get(token) ?? 0) + 1) + 1);
    queryVector.set(token, weight);
    sumSquares += weight * weight;
  }

  const queryNorm = Math.sqrt(sumSquares);

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

const issueIndex = buildIndex(questions, (q) =>
  [
    q.title,
    ...(q.aliases ?? []),
    q.short_answer ?? "",
    ...(q.practical_steps ?? []),
    ...(q.cautions ?? []),
  ].join(" "),
);

function issueRoute(query) {
  return rank(query, issueIndex)
    .slice(0, 3)
    .map(({ documentIndex, score }) => ({
      slug: questions[documentIndex].slug,
      score,
    }));
}

function hasStartupStep(id) {
  return startupSteps.some((step) => step.id === id);
}

function classify(query) {
  const compact = normalize(query);

  // Answerable service-boundary question must be checked before
  // the broad out-of-scope guard.
  if (
    /利用定員/.test(query) &&
    /(18人|19人未満)/.test(query) &&
    hasStartupStep("service-type")
  ) {
    return {
      label: "ANSWER",
      reason: "VERIFIED_SERVICE_TYPE_BOUNDARY",
      route: ["startup-steps.service-type"],
    };
  }

  if (
    /(指定申請|申請様式|締切|事前相談|申請先|窓口)/.test(query) &&
    /(市|区|町|村|都|道|府|県)/.test(query)
  ) {
    return {
      label: "LOCAL",
      reason: "LOCAL_AUTHORITY_PROCEDURE",
    };
  }

  if (
    /地域密着型通所介護|共生型通所介護|療養通所介護/.test(query)
  ) {
    return {
      label: "OUT_OF_SCOPE",
      reason: "SERVICE_OUTSIDE_INITIAL_CORE_SCOPE",
    };
  }

  if (
    /看護職員|看護師/.test(query) &&
    /訪問看護|外部.*連携|連携.*確保/.test(query)
  ) {
    return {
      label: "ANSWER",
      reason: "VERIFIED_NURSE_LINKAGE_ISSUE",
      route: ["nurse-staffing"],
    };
  }

  if (
    /(基本報酬|加算|減算|LIFE|単位数)/.test(query) &&
    remunerationReview.review_status !== "COMPLETE"
  ) {
    return {
      label: "REVIEW_REQUIRED",
      reason: "REMUNERATION_REVIEW_INCOMPLETE",
    };
  }

  if (
    /(一単位単価|1単位|級地|地域区分)/.test(query) &&
    unitPriceReview.review_status !== "COMPLETE"
  ) {
    return {
      label: "REVIEW_REQUIRED",
      reason: "UNIT_PRICE_REVIEW_INCOMPLETE",
    };
  }

  if (
    /(経過措置|未策定減算)/.test(query) &&
    feeGuidanceReview.review_status !== "COMPLETE"
  ) {
    return {
      label: "REVIEW_REQUIRED",
      reason: "FEE_GUIDANCE_CURRENTNESS_REVIEW_INCOMPLETE",
    };
  }

  if (
    /Q&A/.test(query) &&
    !/訪問看護|看護職員/.test(query) &&
    qaCorpusMeta.review_status !== "REVIEWED"
  ) {
    return {
      label: "REVIEW_REQUIRED",
      reason: "QA_CORPUS_UNREVIEWED",
    };
  }

  if (
    /開設.*(流れ|準備|順)|開業.*(流れ|準備|順)/.test(query) &&
    startupSteps.length > 0
  ) {
    return {
      label: "PARTIAL",
      reason: "NATIONAL_STARTUP_OUTLINE_AVAILABLE_LOCAL_DETAILS_REQUIRED",
      route: startupSteps.map((x) => `startup-steps.${x.id}`),
    };
  }

  if (
    /物件.*(契約|確認)/.test(query) &&
    hasStartupStep("property")
  ) {
    return {
      label: "PARTIAL",
      reason: "NATIONAL_PROPERTY_STANDARD_PARTIAL_LOCAL_CHECKS_REQUIRED",
      route: [
        "startup-steps.property",
        "startup-steps.authority",
      ],
    };
  }

  if (
    /標準様式|チェックリスト/.test(query) &&
    hasStartupStep("application")
  ) {
    return {
      label: "PARTIAL",
      reason: "NATIONAL_FORMS_AVAILABLE_LOCAL_ADDITIONS_POSSIBLE",
      route: ["startup-steps.application"],
    };
  }

  const routed = issueRoute(query);
  const top = routed[0];

  if (top && top.score >= 0.09) {
    return {
      label: "ANSWER",
      reason: "VERIFIED_ISSUE_ROUTE",
      route: routed,
    };
  }

  return {
    label: "REVIEW_REQUIRED",
    reason: "NO_CONFIDENT_VERIFIED_COVERAGE",
    route: routed,
  };
}

const results = benchmark.cases.map((test) => {
  const result = classify(test.question);
  return {
    id: test.id,
    expected: test.expected,
    actual: result.label,
    pass: test.expected === result.label,
    result,
  };
});

const counts = {};
for (const row of results) {
  counts[row.expected] ??= { total: 0, passed: 0 };
  counts[row.expected].total += 1;
  if (row.pass) counts[row.expected].passed += 1;
}

const regressionQueries = [
  "管理者は他の職務と兼務できますか？",
  "生活相談員は何人配置すればよいですか？",
  "看護職員は何人必要ですか？",
  "食堂・機能訓練室にはどのくらいの面積が必要ですか？",
  "運営規程には何を記載する必要がありますか？",
  "重要事項説明書には何を記載する必要がありますか？",
  "通所介護計画には何を記載すればよいですか？",
  "通所介護計画書に押印は必要ですか？",
  "通所介護で毎年実施する必要がある研修は何ですか？",
  "BCPの研修はどのくらいの頻度で行いますか？",
];

const regression = regressionQueries.map((question) => ({
  question,
  result: classify(question),
}));

console.log(
  JSON.stringify(
    {
      version: benchmark.version,
      pass_rate:
        results.filter((x) => x.pass).length / results.length,
      passed: results.filter((x) => x.pass).length,
      total: results.length,
      by_label: counts,
      regression_verified_issue_answer_rate:
        regression.filter((x) => x.result.label === "ANSWER")
          .length / regression.length,
      results,
      regression,
    },
    null,
    2,
  ),
);
