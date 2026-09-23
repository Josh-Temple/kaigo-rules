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
const claimRegistry = readJson(
  "docs/kaigo-ops/research/claims/claims-v0.21.json",
);
const compositionRegistry = readJson(
  "docs/kaigo-ops/research/claims/claim-compositions-v0.5.json",
);

const coverage = readJson(
  "docs/kaigo-ops/research/issues/information-search/benchmark/coverage-gap-v0.2.json",
);
const stress = readJson(
  "docs/kaigo-ops/research/issues/information-search/benchmark/false-answer-stress-v0.1.json",
);
const external = readJson(
  "docs/kaigo-ops/research/issues/information-search/benchmark/external-qa-query-sample-v0.8.json",
);
const municipal = readJson(
  "docs/kaigo-ops/research/issues/information-search/benchmark/municipal-query-sample-v0.6.json",
);
const promotion = readJson(
  "docs/kaigo-ops/research/issues/information-search/benchmark/claim-promotion-benchmark-v0.1.json",
);
const naturalRouting = readJson(
  "docs/kaigo-ops/research/issues/information-search/benchmark/claim-routing-natural-language-v0.1.json",
);
const verifiedClaimRouting = readJson(
  "docs/kaigo-ops/research/issues/information-search/benchmark/verified-claim-routing-probe-v0.1.json",
);
const multiClaimRouting = readJson(
  "docs/kaigo-ops/research/issues/information-search/benchmark/multi-claim-routing-v0.1.json",
);
const importantMattersRouting = readJson(
  "docs/kaigo-ops/research/issues/information-search/benchmark/important-matters-claim-routing-v0.1.json",
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

const claimIndex = buildIndex(claimRegistry.claims, (claim) =>
  [
    claim.subtopic,
    claim.statement,
    ...(claim.boundaries ?? []),
  ].join(" "),
);

const verifiedClaimStatuses = new Set([
  "VERIFIED_CURRENT",
  "VERIFIED_SOURCE_TEXT",
  "VERIFIED_WITH_SOURCE_LIMITATION",
  "VERIFIED_INTERPRETATION",
]);

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

function hasExplicitLocalAuthorityContext(query) {
  return /(東京都|北海道|(?:都|道|府|県|市|区|町|村)(?:では|で|の|独自)|自治体|指定権者)/.test(
    query,
  );
}

function isLocalAuthoritySpecific(query) {
  return (
    hasExplicitLocalAuthorityContext(query) &&
    /(指定申請|新規指定|指定事業者|指定前|先に指定|営業開始|営業を開始|申請様式|締切|事前相談|申請先|窓口|移転|専用区画|用途変更|内法|新規指定前研修|管理者.{0,8}研修)/.test(
      query,
    )
  );
}


function hasCoreDayServiceMentionAlongsideOutsideService(query) {
  const withoutOutsideService = query
    .replace(/指定地域密着型通所介護/g, "")
    .replace(/地域密着型通所介護/g, "")
    .replace(/共生型通所介護/g, "")
    .replace(/療養通所介護/g, "");

  return /指定通所介護|通所介護/.test(withoutOutsideService);
}

function route(query) {
  return rank(query, issueIndex)
    .slice(0, 3)
    .map(({ documentIndex, score }) => ({
      slug: questions[documentIndex].slug,
      score,
    }));
}

function matchesClaimRouting(query, routing) {
  if (!routing) return false;

  const value = normalize(query);
  const excluded = routing.excluded_terms ?? [];
  if (excluded.some((term) => value.includes(normalize(term)))) {
    return false;
  }

  return routing.required_groups.every((group) =>
    group.some((term) => value.includes(normalize(term))),
  );
}

function relevantClaimEntries(query, routedIssues) {
  const issueIds = new Set(routedIssues.map(({ slug }) => slug));

  return rank(query, claimIndex)
    .map(({ documentIndex, score }) => ({
      claim: claimRegistry.claims[documentIndex],
      score,
    }))
    .filter(
      ({ claim }) =>
        claim.issue_id === null || issueIds.has(claim.issue_id),
    );
}

function claimCandidates(query, routedIssues, limit = 5) {
  return relevantClaimEntries(query, routedIssues)
    .slice(0, limit)
    .map(({ claim, score }) => ({
      claim_id: claim.claim_id,
      issue_id: claim.issue_id,
      subtopic: claim.subtopic,
      score,
      verification_status: claim.verification_status,
      answerability: claim.answerability,
    }));
}

function explicitClaimMatches(query, routedIssues) {
  const issueIds = new Set(routedIssues.map(({ slug }) => slug));

  return claimRegistry.claims
    .filter(
      (claim) =>
        claim.routing !== undefined &&
        (claim.issue_id === null || issueIds.has(claim.issue_id)),
    )
    .filter((claim) => matchesClaimRouting(query, claim.routing));
}

function explicitCompositionMatches(query, routedIssues) {
  const issueIds = new Set(routedIssues.map(({ slug }) => slug));

  return compositionRegistry.compositions
    .filter(
      (composition) =>
        composition.issue_id === null || issueIds.has(composition.issue_id),
    )
    .filter((composition) => matchesClaimRouting(query, composition));
}

function compositionDecision(composition) {
  const claimsById = new Map(
    claimRegistry.claims.map((claim) => [claim.claim_id, claim]),
  );

  const selectedClaims = composition.claim_ids
    .map((claimId) => claimsById.get(claimId))
    .filter(Boolean);

  const complete = selectedClaims.length === composition.claim_ids.length;
  const safe =
    complete &&
    selectedClaims.every(
      (claim) =>
        claim.answerability === "ANSWER" &&
        verifiedClaimStatuses.has(claim.verification_status),
    );

  if (!safe) {
    return {
      label: "REVIEW_REQUIRED",
      composition_id: composition.composition_id,
      missing_or_unverified_claim_ids: composition.claim_ids.filter(
        (claimId) => {
          const claim = claimsById.get(claimId);
          return (
            !claim ||
            claim.answerability !== "ANSWER" ||
            !verifiedClaimStatuses.has(claim.verification_status)
          );
        },
      ),
    };
  }

  return {
    label: "ANSWER",
    composition_id: composition.composition_id,
    claims: selectedClaims.map((claim) => ({
      claim_id: claim.claim_id,
      issue_id: claim.issue_id,
      subtopic: claim.subtopic,
      verification_status: claim.verification_status,
      source_node_ids: claim.source_node_ids,
      source_ids: claim.source_ids,
    })),
    boundaries: composition.boundaries ?? [],
  };
}

function claimFallbackGuards(query, routedIssues) {
  const issueIds = new Set(routedIssues.map(({ slug }) => slug));
  const value = normalize(query);

  return claimRegistry.claims
    .filter(
      (claim) =>
        claim.routing?.fallback_guard_terms?.length > 0 &&
        (claim.issue_id === null || issueIds.has(claim.issue_id)),
    )
    .filter((claim) =>
      claim.routing.fallback_guard_terms.some((term) =>
        value.includes(normalize(term)),
      ),
    );
}

function claimDecision(matches) {
  const priority = {
    REVIEW_REQUIRED: 5,
    PARTIAL: 4,
    LOCAL: 3,
    OUT_OF_SCOPE: 3,
    ANSWER: 1,
  };

  const selected = [...matches].sort(
    (left, right) =>
      (priority[right.answerability] ?? 0) -
      (priority[left.answerability] ?? 0),
  )[0];

  const label =
    selected.answerability === "ANSWER" &&
    !verifiedClaimStatuses.has(selected.verification_status)
      ? "REVIEW_REQUIRED"
      : selected.answerability;

  return {
    label,
    claim_id: selected.claim_id,
    issue_id: selected.issue_id,
    subtopic: selected.subtopic,
    verification_status: selected.verification_status,
    source_node_ids: selected.source_node_ids,
    source_ids: selected.source_ids,
  };
}

function classify(query) {
  if (
    /利用定員/.test(query) &&
    /(18人|19人未満)/.test(query) &&
    hasStartupStep("service-type")
  ) {
    return { label: "ANSWER", reason: "VERIFIED_SERVICE_TYPE_BOUNDARY" };
  }

  if (isLocalAuthoritySpecific(query)) {
    return { label: "LOCAL", reason: "LOCAL_AUTHORITY_SPECIFIC" };
  }

  if (
    hasCoreDayServiceMentionAlongsideOutsideService(query) &&
    /地域密着型通所介護|共生型通所介護|療養通所介護/.test(query) &&
    /(基本報酬|加算|減算|LIFE|単位数|算定)/.test(query)
  ) {
    return {
      label: "REVIEW_REQUIRED",
      reason: "MIXED_SERVICE_REMUNERATION_REVIEW_REQUIRED",
    };
  }

  if (/一部ユニット型施設|ユニット型施設/.test(query)) {
    return { label: "OUT_OF_SCOPE", reason: "UNIT_TYPE_FACILITY_OUTSIDE_CORE_SCOPE" };
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

  const routed = route(query);
  const routedClaimCandidates = claimCandidates(query, routed);
  const compositionMatches = explicitCompositionMatches(query, routed);

  if (compositionMatches.length > 0) {
    const composition = compositionDecision(compositionMatches[0]);
    return {
      label: composition.label,
      reason: "CLAIM_COMPOSITION_ROUTING",
      route: routed,
      claim_candidates: routedClaimCandidates,
      composition,
      claims: composition.claims ?? [],
    };
  }

  const explicitMatches = explicitClaimMatches(query, routed);

  if (explicitMatches.length > 0) {
    const decision = claimDecision(explicitMatches);
    return {
      label: decision.label,
      reason: "CLAIM_REGISTRY_ROUTING",
      route: routed,
      claim_candidates: routedClaimCandidates,
      claim: decision,
    };
  }

  const guardMatches = claimFallbackGuards(query, routed);

  if (guardMatches.length > 0) {
    return {
      label: "REVIEW_REQUIRED",
      reason: "CLAIM_REGISTRY_FALLBACK_GUARD",
      route: routed,
      claim_candidates: routedClaimCandidates,
      guard_claim_ids: guardMatches.map((claim) => claim.claim_id),
    };
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

  const matches = routed.filter(({ slug }) => intentSignatures[slug]?.(query));

  if (matches.length > 0) {
    return {
      label: "ANSWER",
      reason: "VERIFIED_INTENT_AND_ISSUE_ROUTE",
      route: matches,
      claim_candidates: routedClaimCandidates,
    };
  }

  return {
    label: "REVIEW_REQUIRED",
    reason: "NO_VERIFIED_INTENT_COVERAGE",
    route: routed,
    claim_candidates: routedClaimCandidates,
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


function evaluateComposition(cases) {
  const rows = cases.map((test) => {
    const result = classify(test.question);
    const actualClaimIds = (result.claims ?? [])
      .map((claim) => claim.claim_id)
      .sort();
    const expectedClaimIds = [...(test.expected_claim_ids ?? [])].sort();

    const labelOk = result.label === test.expected;
    const compositionOk =
      !test.expected_composition_id ||
      result.composition?.composition_id === test.expected_composition_id;
    const claimsOk =
      actualClaimIds.length === expectedClaimIds.length &&
      actualClaimIds.every(
        (claimId, index) => claimId === expectedClaimIds[index],
      );

    return {
      id: test.id,
      expected: test.expected,
      expected_composition_id: test.expected_composition_id ?? null,
      actual: result.label,
      actual_composition_id: result.composition?.composition_id ?? null,
      expected_claim_ids: expectedClaimIds,
      actual_claim_ids: actualClaimIds,
      pass: labelOk && compositionOk && claimsOk,
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

function evaluateExpectedProvenance(cases) {
  const rows = cases.map((test) => {
    const result = classify(test.question);
    const actualClaimIds = (result.claims ?? [])
      .map((claim) => claim.claim_id)
      .sort();
    const expectedClaimIds = [...(test.expected_claim_ids ?? [])].sort();

    const labelOk = result.label === test.expected;
    const claimOk =
      !test.expected_claim_id ||
      result.claim?.claim_id === test.expected_claim_id;
    const compositionOk =
      !test.expected_composition_id ||
      result.composition?.composition_id === test.expected_composition_id;
    const compositionClaimsOk =
      !test.expected_composition_id ||
      (actualClaimIds.length === expectedClaimIds.length &&
        actualClaimIds.every(
          (claimId, index) => claimId === expectedClaimIds[index],
        ));

    return {
      id: test.id,
      expected: test.expected,
      expected_claim_id: test.expected_claim_id ?? null,
      expected_composition_id: test.expected_composition_id ?? null,
      actual: result.label,
      actual_claim_id: result.claim?.claim_id ?? null,
      actual_composition_id: result.composition?.composition_id ?? null,
      expected_claim_ids: expectedClaimIds,
      actual_claim_ids: actualClaimIds,
      pass: labelOk && claimOk && compositionOk && compositionClaimsOk,
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

function evaluatePromotion(cases) {
  const rows = cases.map((test) => {
    const result = classify(test.question);
    const labelOk = result.label === test.expected;
    const claimOk =
      !test.expected_claim_id ||
      result.claim?.claim_id === test.expected_claim_id;

    return {
      id: test.id,
      expected: test.expected,
      expected_claim_id: test.expected_claim_id ?? null,
      actual: result.label,
      actual_claim_id: result.claim?.claim_id ?? null,
      pass: labelOk && claimOk,
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

const expectedSuiteSizes = {
  coverage_gap: 20,
  false_answer_stress: 12,
  external_qa_query_sample: 33,
  claim_promotion: 2,
  claim_routing_natural_language: 12,
  verified_claim_routing: 28,
  multi_claim_routing: 5,
  important_matters_claim_routing: 3,
  municipal_query_sample: 25,
};

const observedSuiteSizes = {
  coverage_gap: coverage.cases.length,
  false_answer_stress: stress.cases.length,
  external_qa_query_sample: external.cases.length,
  claim_promotion: promotion.cases.length,
  claim_routing_natural_language: naturalRouting.cases.length,
  verified_claim_routing: verifiedClaimRouting.cases.length,
  multi_claim_routing: multiClaimRouting.cases.length,
  important_matters_claim_routing: importantMattersRouting.cases.length,
  municipal_query_sample: municipal.cases.length,
};

for (const [name, expected] of Object.entries(expectedSuiteSizes)) {
  const actual = observedSuiteSizes[name];
  if (actual !== expected) {
    throw new Error(
      `benchmark suite cardinality mismatch: ${name} expected=${expected} actual=${actual}`,
    );
  }
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
      classifier_version: "0.29",
      harness: {
        municipal_sample: "municipal-query-sample-v0.6.json",
        external_sample: "external-qa-query-sample-v0.8.json",
        expected_suite_sizes: expectedSuiteSizes,
        observed_suite_sizes: observedSuiteSizes,
        expected_total_checks: 191,
      },
      coverage_gap: evaluate(coverage.cases),
      false_answer_stress: evaluate(stress.cases),
      external_qa_query_sample: evaluateExpectedProvenance(external.cases),
      claim_promotion: evaluatePromotion(promotion.cases),
      claim_routing_natural_language: evaluatePromotion(naturalRouting.cases),
      verified_claim_routing: evaluatePromotion(verifiedClaimRouting.cases),
      multi_claim_routing: evaluateComposition(multiClaimRouting.cases),
      important_matters_claim_routing: evaluatePromotion(importantMattersRouting.cases),
      municipal_query_sample: evaluateExpectedProvenance(municipal.cases),
      verified_regression: evaluate(verifiedRegression),
      note:
        "External Q&A answer text is not used. Only the public question preview is used to stress current coverage boundaries. Claim routing metadata is authoritative where present; all current ANSWER claims have explicit routing metadata in claims-v0.5. Verified Claim composition resolves multi-claim cases without inventing umbrella claims. Composition rules exclude queries that name a single covered subtopic, so atomic Claim routing keeps precedence in practice. The external gates use claims-v0.21 and composition-v0.5. Municipal regression uses municipal-query-sample-v0.6 (25 cases). EQ-002, EQ-003, EQ-005, and EQ-011 were promoted through source review without adding classifier special cases. Remuneration mechanics remain fail-closed.",
    },
    null,
    2,
  ),
);
