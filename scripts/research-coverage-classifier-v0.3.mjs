import fs from "node:fs";
import path from "node:path";

const root = process.cwd();
const readJson = (relative) =>
  JSON.parse(fs.readFileSync(path.join(root, relative), "utf8"));

const questions = readJson("data/questions.json");
const startupSteps = readJson("data/startup-steps.json");
const remunerationReview = readJson("data/remuneration-review.json");
const unitPriceReview = readJson("data/unit-price-review.json");
const feeGuidanceReview = readJson("data/fee-guidance-review.json");
const qaCorpusMeta = readJson("data/qa-corpus-meta.json");

const coverage = readJson(
  "docs/kaigo-ops/research/issues/information-search/benchmark/coverage-gap-v0.1.json",
);
const stress = readJson(
  "docs/kaigo-ops/research/issues/information-search/benchmark/false-answer-stress-v0.1.json",
);
const external = readJson(
  "docs/kaigo-ops/research/issues/information-search/benchmark/external-qa-query-sample-v0.1.json",
);
const benchmarkV03 = readJson(
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
  const map = new Map();
  for (const token of tokens) {
    map.set(token, (map.get(token) ?? 0) + 1);
  }
  return map;
}

function buildIndex(documents, toText) {
  const frequencies = documents.map((doc) =>
    termFrequency(ngrams(toText(doc))),
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

  return { documentCount, documentFrequency, vectors };
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

const issueIndex = buildIndex(questions, (question) =>
  [
    question.title,
    ...(question.aliases ?? []),
    question.short_answer ?? "",
    ...(question.practical_steps ?? []),
    ...(question.cautions ?? []),
  ].join(" "),
);

const intentSignatures = {
  "manager-concurrent-role": (query) =>
    /管理者/.test(query) &&
    /(兼務|兼ねる|兼ね|他の職務|別の仕事|別職種|別の事業所|他の事業所)/.test(query),

  "life-counselor-staffing": (query) =>
    /生活相談員/.test(query) &&
    /(何人|人数|配置|勤務|時間|常に|足り)/.test(query),

  "nurse-staffing": (query) =>
    /(看護職員|看護師)/.test(query) &&
    /(何人|人数|配置|常駐|事業所|訪問看護|外部|連携|駆けつけ|確保|従事時間|距離)/.test(query),

  "multiple-roles": (query) =>
    /(兼務|兼ねる|兼ね|複数の職種|複数職種|複数の役割|別の職務|別職種)/.test(query) &&
    /(職員|機能訓練指導員|管理者|生活相談員|介護職員|看護職員)/.test(query),

  "dining-training-area": (query) =>
    /(食堂|食事.*場所|機能訓練室|機能訓練.*場所)/.test(query) &&
    /(面積|広さ|平方|同じ|別室|スペース|定員|場所)/.test(query),

  "operation-rules-content": (query) =>
    /運営規程/.test(query) &&
    /(記載|項目|内容|虐待|最低限|何を)/.test(query),

  "important-matters-content": (query) =>
    /(重要事項説明書|重要事項)/.test(query) &&
    /(記載|説明|掲示|ウェブ|ホームページ|様式|ひな形|事故|苦情|開始前|紙|閲覧)/.test(query),

  "care-plan-content": (query) =>
    /(通所介護計画|計画書|計画)/.test(query) &&
    /(記載|内容|目標|サービス内容|居宅サービス計画|説明|同意|交付|渡す|実施状況|達成状況|作成後)/.test(query),

  "care-plan-signature": (query) =>
    /(通所介護計画|計画書|計画)/.test(query) &&
    /(署名|サイン|電子|電磁|同意)/.test(query),

  "care-plan-seal": (query) =>
    /(通所介護計画|計画書|計画)/.test(query) &&
    /(押印|印鑑)/.test(query),

  "annual-training": (query) =>
    /(研修|教育)/.test(query) &&
    /(毎年|年間|年1回|法定|必須|感染症|虐待|認知症|BCP|業務継続|採用)/.test(query),

  "bcp-training": (query) =>
    /(BCP|業務継続)/i.test(query) &&
    /(研修|訓練|頻度|年|教育|定期)/.test(query),
};

function hasStartupStep(id) {
  return startupSteps.some((step) => step.id === id);
}

function route(query) {
  return rank(query, issueIndex)
    .slice(0, 3)
    .map(({ documentIndex, score }) => ({
      slug: questions[documentIndex].slug,
      score,
    }));
}

function classify(query) {
  if (
    /利用定員/.test(query) &&
    /(18人|19人未満)/.test(query) &&
    hasStartupStep("service-type")
  ) {
    return { label: "ANSWER", reason: "VERIFIED_SERVICE_TYPE_BOUNDARY" };
  }

  if (
    /(指定申請|申請様式|締切|事前相談|申請先|窓口)/.test(query) &&
    /(市|区|町|村|都|道|府|県)/.test(query)
  ) {
    return { label: "LOCAL", reason: "LOCAL_AUTHORITY_PROCEDURE" };
  }

  if (/地域密着型通所介護|共生型通所介護|療養通所介護/.test(query)) {
    return { label: "OUT_OF_SCOPE", reason: "SERVICE_OUTSIDE_INITIAL_CORE_SCOPE" };
  }

  if (
    /(基本報酬|加算|減算|LIFE|単位数|算定)/.test(query) &&
    remunerationReview.review_status !== "COMPLETE"
  ) {
    return { label: "REVIEW_REQUIRED", reason: "REMUNERATION_REVIEW_INCOMPLETE" };
  }

  if (
    /(一単位単価|1単位|級地|地域区分)/.test(query) &&
    unitPriceReview.review_status !== "COMPLETE"
  ) {
    return { label: "REVIEW_REQUIRED", reason: "UNIT_PRICE_REVIEW_INCOMPLETE" };
  }

  if (
    /(経過措置|未策定減算)/.test(query) &&
    feeGuidanceReview.review_status !== "COMPLETE"
  ) {
    return { label: "REVIEW_REQUIRED", reason: "FEE_GUIDANCE_CURRENTNESS_REVIEW_INCOMPLETE" };
  }

  // Known Issue, but current verified answer does not cover these Q&A-level subtopics.
  if (
    /生活相談員/.test(query) &&
    /(サービス担当者会議|町内会|自治会|ボランティア|社会資源|地域連携)/.test(query)
  ) {
    return { label: "REVIEW_REQUIRED", reason: "UNREVIEWED_LIFE_COUNSELOR_QA_SUBTOPIC" };
  }

  if (
    /生活相談員/.test(query) &&
    /介護職員/.test(query) &&
    /(人員配置|配置基準|具体的.*配置)/.test(query)
  ) {
    return { label: "PARTIAL", reason: "LIFE_COUNSELOR_VERIFIED_CARE_WORKER_COVERAGE_MISSING" };
  }

  if (
    /(食堂|機能訓練室)/.test(query) &&
    /(複数.*部屋|部屋.*合計|合計して|狭隘)/.test(query)
  ) {
    return { label: "REVIEW_REQUIRED", reason: "UNREVIEWED_ROOM_AGGREGATION_QA_SUBTOPIC" };
  }

  if (
    /Q&A/.test(query) &&
    !/訪問看護|看護職員/.test(query) &&
    qaCorpusMeta.review_status !== "REVIEWED"
  ) {
    return { label: "REVIEW_REQUIRED", reason: "QA_CORPUS_UNREVIEWED" };
  }

  if (
    /開設.*(流れ|準備|順)|開業.*(流れ|準備|順)/.test(query) &&
    startupSteps.length > 0
  ) {
    return { label: "PARTIAL", reason: "NATIONAL_STARTUP_OUTLINE_AVAILABLE_LOCAL_DETAILS_REQUIRED" };
  }

  if (/物件.*(契約|確認)/.test(query) && hasStartupStep("property")) {
    return { label: "PARTIAL", reason: "NATIONAL_PROPERTY_STANDARD_PARTIAL_LOCAL_CHECKS_REQUIRED" };
  }

  if (/標準様式|チェックリスト/.test(query) && hasStartupStep("application")) {
    return { label: "PARTIAL", reason: "NATIONAL_FORMS_AVAILABLE_LOCAL_ADDITIONS_POSSIBLE" };
  }

  const routed = route(query);
  const matches = routed.filter(({ slug }) => intentSignatures[slug]?.(query));

  if (matches.length > 0) {
    return {
      label: "ANSWER",
      reason: "VERIFIED_INTENT_AND_ISSUE_ROUTE",
      route: matches,
    };
  }

  return {
    label: "REVIEW_REQUIRED",
    reason: "NO_VERIFIED_INTENT_COVERAGE",
    route: routed,
  };
}

function evaluate(cases) {
  const rows = cases.map((test) => {
    const result = classify(test.question);
    return {
      id: test.id,
      expected: test.expected,
      actual: result.label,
      pass: test.expected === result.label,
      result,
    };
  });

  return {
    passed: rows.filter((row) => row.pass).length,
    total: rows.length,
    pass_rate: rows.filter((row) => row.pass).length / rows.length,
    failures: rows.filter((row) => !row.pass),
  };
}

const verifiedRegression = [
  ...benchmarkV03.retrieval_tests.map((test) => ({
    id: test.id,
    question: test.question,
    expected: "ANSWER",
  })),
  ...questions.map((question, index) => ({
    id: `CAN-${String(index + 1).padStart(3, "0")}`,
    question: question.title,
    expected: "ANSWER",
  })),
];

console.log(
  JSON.stringify(
    {
      classifier_version: "0.3",
      coverage_gap: evaluate(coverage.cases),
      false_answer_stress: evaluate(stress.cases),
      external_qa_query_sample: evaluate(external.cases),
      verified_regression: evaluate(verifiedRegression),
      note:
        "External Q&A answer text is not used. Only the public question preview is used to stress current coverage boundaries.",
    },
    null,
    2,
  ),
);
