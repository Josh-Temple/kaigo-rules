import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { createHash } from "node:crypto";

const here = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(here, "..");
const read = (name) => JSON.parse(fs.readFileSync(path.join(root, "data", name), "utf8"));

const questions = read("questions.json");
const sources = read("sources.json");
const rules = read("rule-nodes.json");
const notices = read("notice-nodes.json");
const qa = read("qa-items.json");
const qaCorpusPath = path.join(root, "data", "qa-corpus.json");
const qaCorpus = fs.existsSync(qaCorpusPath)
  ? JSON.parse(fs.readFileSync(qaCorpusPath, "utf8"))
  : [];
const qaCandidatesPath = path.join(root, "data", "qa-link-candidates.json");
const qaCandidates = fs.existsSync(qaCandidatesPath)
  ? JSON.parse(fs.readFileSync(qaCandidatesPath, "utf8"))
  : { candidates: [] };
const ordinancePath = path.join(root, "data", "ordinance37-nodes.json");
const ordinanceNodes = fs.existsSync(ordinancePath)
  ? JSON.parse(fs.readFileSync(ordinancePath, "utf8"))
  : [];
const ordinanceRelationsPath = path.join(root, "data", "ordinance37-relations.json");
const ordinanceRelations = fs.existsSync(ordinanceRelationsPath)
  ? JSON.parse(fs.readFileSync(ordinanceRelationsPath, "utf8"))
  : [];
const ordinanceApplicationsPath = path.join(root, "data", "ordinance37-application-rules.json");
const ordinanceApplications = fs.existsSync(ordinanceApplicationsPath)
  ? JSON.parse(fs.readFileSync(ordinanceApplicationsPath, "utf8"))
  : [];
const ordinanceScopePath = path.join(root, "data", "ordinance37-scope.json");
const ordinanceScope = fs.existsSync(ordinanceScopePath)
  ? JSON.parse(fs.readFileSync(ordinanceScopePath, "utf8"))
  : null;
const ordinanceReviewPath = path.join(root, "data", "ordinance37-review.json");
const ordinanceReview = fs.existsSync(ordinanceReviewPath)
  ? JSON.parse(fs.readFileSync(ordinanceReviewPath, "utf8"))
  : { reviewed_articles: [], reviewed_application_rules: [] };

const noticeSkeletonPath = path.join(root, "data", "notice-current-skeleton.json");
const noticeSkeleton = fs.existsSync(noticeSkeletonPath)
  ? JSON.parse(fs.readFileSync(noticeSkeletonPath, "utf8"))
  : [];
const noticeRelationsPath = path.join(root, "data", "notice-ordinance-relations.json");
const noticeRelations = fs.existsSync(noticeRelationsPath)
  ? JSON.parse(fs.readFileSync(noticeRelationsPath, "utf8"))
  : [];
const noticeAmendmentsPath = path.join(root, "data", "notice-amendment-events.json");
const noticeAmendments = fs.existsSync(noticeAmendmentsPath)
  ? JSON.parse(fs.readFileSync(noticeAmendmentsPath, "utf8"))
  : [];
const noticeSourceChainPath = path.join(root, "data", "notice-source-chain.json");
const noticeSourceChain = fs.existsSync(noticeSourceChainPath)
  ? JSON.parse(fs.readFileSync(noticeSourceChainPath, "utf8"))
  : [];
const noticeCurrentMetaPath = path.join(root, "data", "notice-current-meta.json");
const noticeCurrentMeta = fs.existsSync(noticeCurrentMetaPath)
  ? JSON.parse(fs.readFileSync(noticeCurrentMetaPath, "utf8"))
  : null;
const noticeCurrentReviewPath = path.join(root, "data", "notice-current-review.json");
const noticeCurrentReview = fs.existsSync(noticeCurrentReviewPath)
  ? JSON.parse(fs.readFileSync(noticeCurrentReviewPath, "utf8"))
  : { reviewed_nodes: [], reviewed_relations: [] };
const noticeHistoryPath = path.join(root, "data", "notice-historical-backfill.json");
const noticeHistory = fs.existsSync(noticeHistoryPath)
  ? JSON.parse(fs.readFileSync(noticeHistoryPath, "utf8"))
  : [];
const feeSkeletonPath = path.join(root, "data", "remuneration-current-skeleton.json");
const feeSkeleton = fs.existsSync(feeSkeletonPath)
  ? JSON.parse(fs.readFileSync(feeSkeletonPath, "utf8"))
  : [];
const feeRelationsPath = path.join(root, "data", "remuneration-relations.json");
const feeRelations = fs.existsSync(feeRelationsPath)
  ? JSON.parse(fs.readFileSync(feeRelationsPath, "utf8"))
  : [];
const feeAmendmentsPath = path.join(root, "data", "remuneration-amendment-events.json");
const feeAmendments = fs.existsSync(feeAmendmentsPath)
  ? JSON.parse(fs.readFileSync(feeAmendmentsPath, "utf8"))
  : [];
const feeSourceChainPath = path.join(root, "data", "remuneration-source-chain.json");
const feeSourceChain = fs.existsSync(feeSourceChainPath)
  ? JSON.parse(fs.readFileSync(feeSourceChainPath, "utf8"))
  : [];
const feeCurrentTextPath = path.join(root, "data", "remuneration-current-text.json");
const feeCurrentText = fs.existsSync(feeCurrentTextPath)
  ? JSON.parse(fs.readFileSync(feeCurrentTextPath, "utf8"))
  : [];
const feeReviewPath = path.join(root, "data", "remuneration-review.json");
const feeReview = fs.existsSync(feeReviewPath)
  ? JSON.parse(fs.readFileSync(feeReviewPath, "utf8"))
  : { reviewed_nodes: [], reviewed_relations: [] };
const delegatedFeeNodesPath = path.join(root, "data", "remuneration-delegated-nodes.json");
const delegatedFeeNodes = fs.existsSync(delegatedFeeNodesPath)
  ? JSON.parse(fs.readFileSync(delegatedFeeNodesPath, "utf8"))
  : [];
const delegatedFeeRelationsPath = path.join(root, "data", "remuneration-delegated-relations.json");
const delegatedFeeRelations = fs.existsSync(delegatedFeeRelationsPath)
  ? JSON.parse(fs.readFileSync(delegatedFeeRelationsPath, "utf8"))
  : [];
const unitPricePath = path.join(root, "data", "unit-price-dayservice.json");
const unitPrices = fs.existsSync(unitPricePath)
  ? JSON.parse(fs.readFileSync(unitPricePath, "utf8"))
  : [];
const unitRegionAssignmentsPath = path.join(root, "data", "unit-price-region-assignments.json");
const unitRegionAssignments = fs.existsSync(unitRegionAssignmentsPath)
  ? JSON.parse(fs.readFileSync(unitRegionAssignmentsPath, "utf8"))
  : [];
const unitRegionAssignmentsMetaPath = path.join(root, "data", "unit-price-region-assignments-meta.json");
const unitRegionAssignmentsMeta = fs.existsSync(unitRegionAssignmentsMetaPath)
  ? JSON.parse(fs.readFileSync(unitRegionAssignmentsMetaPath, "utf8"))
  : null;
const unitPriceMetaPath = path.join(root, "data", "unit-price-dayservice-meta.json");
const unitPriceMeta = fs.existsSync(unitPriceMetaPath)
  ? JSON.parse(fs.readFileSync(unitPriceMetaPath, "utf8"))
  : null;
const unitPriceReviewPath = path.join(root, "data", "unit-price-review.json");
const unitPriceReview = fs.existsSync(unitPriceReviewPath)
  ? JSON.parse(fs.readFileSync(unitPriceReviewPath, "utf8"))
  : { reviewed_rate_ids: [], reviewed_assignment_ids: [], reviewed_default_rule: false };

const feeGuidancePath = path.join(root, "data", "fee-guidance-current-skeleton.json");
const feeGuidance = fs.existsSync(feeGuidancePath)
  ? JSON.parse(fs.readFileSync(feeGuidancePath, "utf8"))
  : [];
const feeGuidanceRelationsPath = path.join(root, "data", "fee-guidance-relations.json");
const feeGuidanceRelations = fs.existsSync(feeGuidanceRelationsPath)
  ? JSON.parse(fs.readFileSync(feeGuidanceRelationsPath, "utf8"))
  : [];
const feeGuidanceEventsPath = path.join(root, "data", "fee-guidance-amendment-events.json");
const feeGuidanceEvents = fs.existsSync(feeGuidanceEventsPath)
  ? JSON.parse(fs.readFileSync(feeGuidanceEventsPath, "utf8"))
  : [];
const feeGuidanceChainPath = path.join(root, "data", "fee-guidance-source-chain.json");
const feeGuidanceChain = fs.existsSync(feeGuidanceChainPath)
  ? JSON.parse(fs.readFileSync(feeGuidanceChainPath, "utf8"))
  : [];
const feeGuidanceMetaPath = path.join(root, "data", "fee-guidance-current-meta.json");
const feeGuidanceMeta = fs.existsSync(feeGuidanceMetaPath)
  ? JSON.parse(fs.readFileSync(feeGuidanceMetaPath, "utf8"))
  : null;
const feeGuidanceReviewPath = path.join(root, "data", "fee-guidance-review.json");
const feeGuidanceReview = fs.existsSync(feeGuidanceReviewPath)
  ? JSON.parse(fs.readFileSync(feeGuidanceReviewPath, "utf8"))
  : { reviewed_nodes: [], reviewed_relations: [] };
const feeGuidanceCandidatesPath = path.join(root, "data", "fee-guidance-text-candidates.json");
const feeGuidanceCandidates = fs.existsSync(feeGuidanceCandidatesPath)
  ? JSON.parse(fs.readFileSync(feeGuidanceCandidatesPath, "utf8"))
  : [];
const feeGuidanceReplayCoveragePath = path.join(root, "data", "fee-guidance-replay-coverage.json");
const feeGuidanceReplayCoverage = fs.existsSync(feeGuidanceReplayCoveragePath)
  ? JSON.parse(fs.readFileSync(feeGuidanceReplayCoveragePath, "utf8"))
  : [];
const feeGuidanceSourceManifestPath = path.join(root, "data", "fee-guidance-source-manifest.json");
const feeGuidanceSourceManifest = fs.existsSync(feeGuidanceSourceManifestPath)
  ? JSON.parse(fs.readFileSync(feeGuidanceSourceManifestPath, "utf8"))
  : null;
const feeGuidanceSnapshotsPath = path.join(root, "data", "fee-guidance-source-snapshots.json");
const feeGuidanceSnapshots = fs.existsSync(feeGuidanceSnapshotsPath)
  ? JSON.parse(fs.readFileSync(feeGuidanceSnapshotsPath, "utf8"))
  : null;
const feeGuidanceAssemblyPath = path.join(root, "data", "fee-guidance-current-assembly.json");
const feeGuidanceAssembly = fs.existsSync(feeGuidanceAssemblyPath)
  ? JSON.parse(fs.readFileSync(feeGuidanceAssemblyPath, "utf8"))
  : null;
const feeGuidanceCurrentCandidatesPath = path.join(root, "data", "fee-guidance-current-text-candidates.json");
const feeGuidanceCurrentCandidates = fs.existsSync(feeGuidanceCurrentCandidatesPath)
  ? JSON.parse(fs.readFileSync(feeGuidanceCurrentCandidatesPath, "utf8"))
  : null;
const careActPath = path.join(root, "data", "care-insurance-act-nodes.json");
const careActNodes = fs.existsSync(careActPath)
  ? JSON.parse(fs.readFileSync(careActPath, "utf8"))
  : [];
const careActRelationsPath = path.join(root, "data", "care-insurance-act-relations.json");
const careActRelations = fs.existsSync(careActRelationsPath)
  ? JSON.parse(fs.readFileSync(careActRelationsPath, "utf8"))
  : [];
const careActScopePath = path.join(root, "data", "care-insurance-act-scope.json");
const careActScope = fs.existsSync(careActScopePath)
  ? JSON.parse(fs.readFileSync(careActScopePath, "utf8"))
  : null;
const careActReviewPath = path.join(root, "data", "care-insurance-act-review.json");
const careActReview = fs.existsSync(careActReviewPath)
  ? JSON.parse(fs.readFileSync(careActReviewPath, "utf8"))
  : { reviewed_articles: [], reviewed_relations: [] };

const errors = [];
const unique = (items, key, label) => {
  const seen = new Set();
  for (const item of items) {
    const value = item[key];
    if (!value) errors.push(`${label}: missing ${key}`);
    else if (seen.has(value)) errors.push(`${label}: duplicate ${key} ${value}`);
    seen.add(value);
  }
};

unique(questions, "slug", "questions");
unique(sources, "id", "sources");
unique(rules, "id", "rules");
unique(notices, "id", "notices");
unique(qa, "id", "qa");
unique(qaCorpus, "id", "qa-corpus");
unique(ordinanceNodes, "id", "ordinance37-nodes");
unique(ordinanceApplications, "id", "ordinance37-applications");
unique(noticeSkeleton, "id", "notice-current-skeleton");
unique(noticeAmendments, "id", "notice-amendment-events");
unique(noticeHistory, "notice_id", "notice-historical-backfill");
unique(feeSkeleton, "id", "remuneration-skeleton");
unique(feeAmendments, "id", "remuneration-amendments");
unique(feeCurrentText, "fee_id", "remuneration-current-text");
unique(delegatedFeeNodes, "id", "remuneration-delegated-nodes");
unique(unitPrices, "id", "unit-price-dayservice");
unique(unitRegionAssignments, "id", "unit-price-region-assignments");
unique(feeGuidance, "id", "fee-guidance-current-skeleton");
unique(feeGuidanceEvents, "id", "fee-guidance-amendment-events");
unique(careActNodes, "id", "care-insurance-act-nodes");

const sourceIds = new Set(sources.map((x) => x.id));
const ruleIds = new Set(rules.map((x) => x.id));
const noticeIds = new Set(notices.map((x) => x.id));
const qaIds = new Set(qa.map((x) => x.id));

for (const q of questions) {
  if (q.status === "verified") {
    for (const field of ["last_verified", "short_answer", "practical_steps", "cautions"]) {
      if (!q[field] || (Array.isArray(q[field]) && q[field].length === 0)) {
        errors.push(`question ${q.slug}: verified but missing ${field}`);
      }
    }
  }
  for (const id of q.rule_node_ids || []) if (!ruleIds.has(id)) errors.push(`question ${q.slug}: missing rule ${id}`);
  for (const id of q.notice_node_ids || []) if (!noticeIds.has(id)) errors.push(`question ${q.slug}: missing notice ${id}`);
  for (const id of q.qa_item_ids || []) if (!qaIds.has(id)) errors.push(`question ${q.slug}: missing Q&A ${id}`);
  for (const ref of q.source_refs || []) if (!sourceIds.has(ref.source_id)) errors.push(`question ${q.slug}: missing source ${ref.source_id}`);
}

for (const r of rules) {
  if (!sourceIds.has(r.source_id)) errors.push(`rule ${r.id}: missing source ${r.source_id}`);
  if (r.verification_status === "VERIFIED_CURRENT" && !r.official_text) {
    errors.push(`rule ${r.id}: VERIFIED_CURRENT without text`);
  }
}

for (const n of notices) {
  for (const id of n.source_ids || []) {
    if (!sourceIds.has(id)) errors.push(`notice ${n.id}: missing source ${id}`);
  }
}

for (const item of qa) {
  if (!sourceIds.has(item.source_id)) errors.push(`Q&A ${item.id}: missing source ${item.source_id}`);
}

const corpusIds = new Set(qaCorpus.map((item) => item.id));

for (const item of qaCorpus) {
  if (!sourceIds.has(item.source_id)) errors.push(`Q&A corpus ${item.id}: missing source ${item.source_id}`);
  for (const field of ["service_code", "standard_code", "question", "answer", "ingestion_status"]) {
    if (!item[field]) errors.push(`Q&A corpus ${item.id || "(missing id)"}: missing ${field}`);
  }
  if (!["01", "02", "06", "16"].includes(item.service_code)) {
    errors.push(`Q&A corpus ${item.id}: unexpected service_code ${item.service_code}`);
  }
}

for (const group of qaCandidates.candidates || []) {
  if (!questions.some((q) => q.slug === group.question_slug)) {
    errors.push(`Q&A candidate group: missing question ${group.question_slug}`);
  }
  if (group.status !== "CANDIDATE_UNREVIEWED") {
    errors.push(`Q&A candidate group ${group.question_slug}: unexpected status ${group.status}`);
  }
  for (const candidate of group.candidates || []) {
    if (!corpusIds.has(candidate.qa_id)) {
      errors.push(`Q&A candidate ${group.question_slug}: missing corpus item ${candidate.qa_id}`);
    }
    if (candidate.status !== "CANDIDATE_UNREVIEWED") {
      errors.push(`Q&A candidate ${candidate.qa_id}: unexpected status ${candidate.status}`);
    }
  }
}

if (ordinanceNodes.length) {
  const ordinanceIds = new Set(ordinanceNodes.map((node) => node.id));
  const articleIds = new Set(
    ordinanceNodes.filter((node) => node.node_type === "article").map((node) => node.id)
  );

  for (const node of ordinanceNodes) {
    for (const field of ["node_type", "law_id", "article_num", "official_text", "service_scope", "source_url", "verification_status"]) {
      if (!node[field]) errors.push(`ordinance37 node ${node.id}: missing ${field}`);
    }
    if (node.verification_status !== "IMPORTED_NEEDS_HUMAN_CHECK" && node.verification_status !== "VERIFIED_CURRENT") {
      errors.push(`ordinance37 node ${node.id}: unexpected status ${node.verification_status}`);
    }
    if (node.parent_id && !ordinanceIds.has(node.parent_id)) {
      errors.push(`ordinance37 node ${node.id}: missing parent ${node.parent_id}`);
    }
  }

  for (const relation of ordinanceRelations) {
    if (!ordinanceIds.has(relation.from)) errors.push(`ordinance37 relation: missing from ${relation.from}`);
    if (!ordinanceIds.has(relation.to)) errors.push(`ordinance37 relation: missing to ${relation.to}`);
  }

  for (const rule of ordinanceApplications) {
    if (!articleIds.has(rule.via_article_id)) errors.push(`ordinance37 application ${rule.id}: missing via article ${rule.via_article_id}`);
    if (!articleIds.has(rule.target_article_id)) errors.push(`ordinance37 application ${rule.id}: missing target article ${rule.target_article_id}`);
    if (!Array.isArray(rule.substitutions) || rule.substitutions.length === 0) errors.push(`ordinance37 application ${rule.id}: missing substitutions`);
  }

  if (ordinanceScope) {
    for (const number of [...ordinanceScope.direct_articles, ...ordinanceScope.incorporated_articles]) {
      if (!articleIds.has(`ordinance37.article.${number}`)) {
        errors.push(`ordinance37 scope: missing article ${number}`);
      }
    }
  }

  const nodeById = new Map(ordinanceNodes.map((node) => [node.id, node]));
  const applicationById = new Map(ordinanceApplications.map((rule) => [rule.id, rule]));

  for (const review of ordinanceReview.reviewed_articles || []) {
    const node = nodeById.get(review.article_id);
    if (!node || node.node_type !== "article") {
      errors.push(`ordinance37 review: missing article ${review.article_id}`);
      continue;
    }
    if (review.text_sha256 !== node.text_sha256) {
      errors.push(`ordinance37 review ${review.article_id}: reviewed hash is stale`);
    }
    if (review.status !== "HUMAN_VERIFIED_AGAINST_OFFICIAL_SOURCE") {
      errors.push(`ordinance37 review ${review.article_id}: unexpected status ${review.status}`);
    }
  }

  for (const review of ordinanceReview.reviewed_application_rules || []) {
    if (!applicationById.has(review.application_rule_id)) {
      errors.push(`ordinance37 review: missing application rule ${review.application_rule_id}`);
    }
    if (review.status !== "HUMAN_VERIFIED_AGAINST_OFFICIAL_SOURCE") {
      errors.push(`ordinance37 application review ${review.application_rule_id}: unexpected status ${review.status}`);
    }
  }
}


if (noticeSkeleton.length) {
  const noticeSkeletonIds = new Set(noticeSkeleton.map((node) => node.id));
  const ordinanceIds = new Set(ordinanceNodes.map((node) => node.id));
  const allowedStatuses = new Set([
    "VERIFIED_CURRENT",
    "KNOWN_AFTER_TEXT",
    "INHERITED_UNVERIFIED",
    "UNKNOWN",
    "DELETED",
    "NOT_APPLICABLE",
  ]);

  for (const node of noticeSkeleton) {
    for (const field of ["id", "number_path", "title", "service_scope", "verification_status", "structure_status"]) {
      if (!node[field] || (Array.isArray(node[field]) && node[field].length === 0)) {
        errors.push(`notice skeleton ${node.id || "(missing id)"}: missing ${field}`);
      }
    }
    if (!allowedStatuses.has(node.verification_status)) {
      errors.push(`notice skeleton ${node.id}: unexpected status ${node.verification_status}`);
    }
    if (node.parent_id && !noticeSkeletonIds.has(node.parent_id)) {
      errors.push(`notice skeleton ${node.id}: missing parent ${node.parent_id}`);
    }
    if (node.verification_status === "VERIFIED_CURRENT" && !node.official_text) {
      errors.push(`notice skeleton ${node.id}: VERIFIED_CURRENT without official_text`);
    }
    for (const ordinanceId of node.related_ordinance_ids || []) {
      if (!ordinanceIds.has(ordinanceId)) {
        errors.push(`notice skeleton ${node.id}: missing ordinance node ${ordinanceId}`);
      }
    }
    for (const evidence of node.evidence || []) {
      if (!sourceIds.has(evidence.source_id)) {
        errors.push(`notice skeleton ${node.id}: missing evidence source ${evidence.source_id}`);
      }
      if (!evidence.locator || !evidence.evidence_type) {
        errors.push(`notice skeleton ${node.id}: incomplete evidence record`);
      }
    }
  }

  for (const relation of noticeRelations) {
    if (!noticeSkeletonIds.has(relation.from_notice_id)) {
      errors.push(`notice relation: missing notice ${relation.from_notice_id}`);
    }
    if (!ordinanceIds.has(relation.to_ordinance_id)) {
      errors.push(`notice relation: missing ordinance ${relation.to_ordinance_id}`);
    }
    if (relation.verification_status !== "STRUCTURAL_MAPPING_NEEDS_HUMAN_CHECK" &&
        relation.verification_status !== "HUMAN_VERIFIED") {
      errors.push(`notice relation ${relation.from_notice_id}: unexpected status ${relation.verification_status}`);
    }
  }

  for (const event of noticeAmendments) {
    if (!sourceIds.has(event.source_id)) {
      errors.push(`notice amendment ${event.id}: missing source ${event.source_id}`);
    }
    if (!noticeSkeletonIds.has(event.target_node_id)) {
      errors.push(`notice amendment ${event.id}: missing target ${event.target_node_id}`);
    }
    if (!event.operation || !event.effective_from || !event.summary || !event.verification_status) {
      errors.push(`notice amendment ${event.id}: incomplete event`);
    }
  }

  for (const entry of noticeSourceChain) {
    if (!sourceIds.has(entry.source_id)) {
      errors.push(`notice source chain: missing source ${entry.source_id}`);
    }
  }

  for (const review of noticeCurrentReview.reviewed_nodes || []) {
    if (!noticeSkeletonIds.has(review.notice_id)) {
      errors.push(`notice review: missing node ${review.notice_id}`);
    }
  }

  for (const candidate of noticeHistory) {
    if (!noticeSkeletonIds.has(candidate.notice_id)) {
      errors.push(`notice history: missing skeleton node ${candidate.notice_id}`);
    }
    if (!sourceIds.has(candidate.source_id)) {
      errors.push(`notice history ${candidate.notice_id}: missing source ${candidate.source_id}`);
    }
    if (!candidate.historical_text || !candidate.historical_text_sha256) {
      errors.push(`notice history ${candidate.notice_id}: missing text or hash`);
    }
    if (candidate.candidate_status !== "HISTORICAL_BACKFILL_CANDIDATE" || candidate.requires_forward_replay !== true) {
      errors.push(`notice history ${candidate.notice_id}: unsafe promotion state`);
    }
  }

  if (noticeCurrentMeta) {
    if (noticeCurrentMeta.counts?.total !== noticeSkeleton.length) {
      errors.push(`notice meta: total count ${noticeCurrentMeta.counts?.total} does not match ${noticeSkeleton.length}`);
    }
    const actualCounts = noticeSkeleton.reduce((acc, node) => {
      acc[node.verification_status] = (acc[node.verification_status] || 0) + 1;
      return acc;
    }, {});
    for (const [status, count] of Object.entries(actualCounts)) {
      if (noticeCurrentMeta.counts?.[status] !== count) {
        errors.push(`notice meta: ${status} count mismatch`);
      }
    }
  }
}

if (feeSkeleton.length) {
  const feeIds = new Set(feeSkeleton.map((node) => node.id));
  const ordinanceIds = new Set(ordinanceNodes.map((node) => node.id));
  const allowedFeeStatuses = new Set(["CURRENT_STRUCTURE_NEEDS_HUMAN_CHECK","CURRENT_AFTER_TEXT_NEEDS_HUMAN_CHECK","OUT_OF_CORE_SCOPE","VERIFIED_CURRENT","UNKNOWN"]);
  for (const node of feeSkeleton) {
    if (!node.id || !node.title || !node.authority_layer || !node.service_scope || !node.verification_status || !node.source_id) {
      errors.push(`fee skeleton ${node.id || "(missing id)"}: missing required field`);
    }
    if (!allowedFeeStatuses.has(node.verification_status)) errors.push(`fee skeleton ${node.id}: unexpected status ${node.verification_status}`);
    if (node.parent_id && !feeIds.has(node.parent_id)) errors.push(`fee skeleton ${node.id}: missing parent ${node.parent_id}`);
    if (!sourceIds.has(node.source_id)) errors.push(`fee skeleton ${node.id}: missing source ${node.source_id}`);
    for (const evidence of node.latest_amendment_evidence || []) {
      if (!sourceIds.has(evidence.source_id)) errors.push(`fee skeleton ${node.id}: missing evidence source ${evidence.source_id}`);
    }
  }
  for (const relation of feeRelations) {
    if (!feeIds.has(relation.from_fee_id)) errors.push(`fee relation: missing fee node ${relation.from_fee_id}`);
    if (relation.to_id && !ordinanceIds.has(relation.to_id)) errors.push(`fee relation: missing ordinance node ${relation.to_id}`);
    if (relation.to_source_id && !sourceIds.has(relation.to_source_id)) errors.push(`fee relation: missing source ${relation.to_source_id}`);
  }
  for (const event of feeAmendments) {
    if (!sourceIds.has(event.source_id)) errors.push(`fee amendment ${event.id}: missing source`);
    for (const id of event.target_ids || []) if (!feeIds.has(id)) errors.push(`fee amendment ${event.id}: missing target ${id}`);
  }
  for (const entry of feeSourceChain) if (!sourceIds.has(entry.source_id)) errors.push(`fee source chain: missing source ${entry.source_id}`);
  const feeTextById = new Map(feeCurrentText.map((record) => [record.fee_id, record]));
  for (const record of feeCurrentText) {
    if (!feeIds.has(record.fee_id)) errors.push(`fee current text: missing skeleton node ${record.fee_id}`);
    if (!sourceIds.has(record.source_id)) errors.push(`fee current text ${record.fee_id}: missing source ${record.source_id}`);
    if (!record.official_text || !record.text_sha256) errors.push(`fee current text ${record.fee_id}: missing text/hash`);
    if (record.import_status !== "IMPORTED_CURRENT_SOURCE_NEEDS_HUMAN_CHECK") errors.push(`fee current text ${record.fee_id}: unexpected status`);
  }

  for (const review of feeReview.reviewed_nodes || []) {
    if (!feeIds.has(review.fee_id)) {
      errors.push(`fee review: missing node ${review.fee_id}`);
      continue;
    }
    const current = feeTextById.get(review.fee_id);
    if (!current) {
      errors.push(`fee review ${review.fee_id}: no imported current text`);
      continue;
    }
    if (review.text_sha256 !== current.text_sha256) {
      errors.push(`fee review ${review.fee_id}: reviewed hash is stale`);
    }
    if (review.status !== "HUMAN_VERIFIED_AGAINST_OFFICIAL_SOURCE") {
      errors.push(`fee review ${review.fee_id}: unexpected status ${review.status}`);
    }
  }

  for (const review of feeReview.reviewed_relations || []) {
    if (!review.from_fee_id || !feeIds.has(review.from_fee_id)) {
      errors.push(`fee relation review: missing fee node ${review.from_fee_id}`);
    }
    if (review.status !== "HUMAN_VERIFIED") {
      errors.push(`fee relation review ${review.from_fee_id}: unexpected status ${review.status}`);
    }
  }
}

if (delegatedFeeNodes.length) {
  const delegatedIds = new Set(delegatedFeeNodes.map((node) => node.id));
  const feeIds = new Set(feeSkeleton.map((node) => node.id));
  for (const node of delegatedFeeNodes) {
    for (const field of ["id","source_id","source_url","heading","official_text","text_sha256","service_scope","verification_status"]) {
      if (!node[field]) errors.push(`delegated fee node ${node.id || "(missing id)"}: missing ${field}`);
    }
    if (!sourceIds.has(node.source_id)) errors.push(`delegated fee node ${node.id}: missing source ${node.source_id}`);
    if (node.verification_status !== "IMPORTED_CURRENT_SOURCE_NEEDS_HUMAN_CHECK" && node.verification_status !== "VERIFIED_CURRENT") {
      errors.push(`delegated fee node ${node.id}: unexpected status ${node.verification_status}`);
    }
    for (const feeId of node.related_fee_ids || []) if (!feeIds.has(feeId)) errors.push(`delegated fee node ${node.id}: missing fee ${feeId}`);
  }
  for (const relation of delegatedFeeRelations) {
    const fromKnown = feeIds.has(relation.from_id) || delegatedIds.has(relation.from_id);
    if (!fromKnown) errors.push(`delegated fee relation: missing from ${relation.from_id}`);
    if (!delegatedIds.has(relation.to_id)) errors.push(`delegated fee relation: missing to ${relation.to_id}`);
  }
}

if (unitPrices.length) {
  const expected = new Set(["一級地","二級地","三級地","四級地","五級地","六級地","七級地","その他"]);
  const seenRegions = new Set();
  for (const row of unitPrices) {
    if (!expected.has(row.region_class) && !seenRegions.has(row.region_class)) errors.push(`unit price ${row.id}: unexpected region ${row.region_class}`);
    if (seenRegions.has(row.region_class)) errors.push(`unit price: duplicate region ${row.region_class}`);
    seenRegions.add(row.region_class);
    if (row.service !== "通所介護") errors.push(`unit price ${row.id}: unexpected service`);
    if (!sourceIds.has(row.source_id)) errors.push(`unit price ${row.id}: missing source ${row.source_id}`);
    if (!Number.isFinite(row.ratio_per_thousand) || !Number.isFinite(row.unit_price_yen)) {
      errors.push(`unit price ${row.id}: invalid numeric value`);
    } else {
      const calculated = 10 * row.ratio_per_thousand / 1000;
      if (Math.abs(calculated - row.unit_price_yen) > 1e-9) errors.push(`unit price ${row.id}: ratio and yen value mismatch`);
    }
    if (row.verification_status !== "IMPORTED_CURRENT_SOURCE_NEEDS_HUMAN_CHECK" && row.verification_status !== "VERIFIED_CURRENT") errors.push(`unit price ${row.id}: unexpected status`);
    expected.delete(row.region_class);
  }
  if (expected.size) errors.push(`unit price: missing regions ${[...expected].join(",")}`);
}

if (unitRegionAssignments.length) {
  const rateIds = new Set(unitPrices.map((row) => row.id));
  const rateById = new Map(unitPrices.map((row) => [row.id, row]));
  const allowedRegions = new Set(["一級地","二級地","三級地","四級地","五級地","六級地","七級地"]);
  const explicitRegions = new Set();
  const localityKeys = new Set();

  for (const row of unitRegionAssignments) {
    for (const field of ["id","assignment_type","prefecture","locality","region_class","unit_price_id","source_id","effective_reference_date","verification_status"]) {
      if (!row[field]) errors.push(`unit region ${row.id || "(missing id)"}: missing ${field}`);
    }
    if (row.assignment_type !== "explicit") errors.push(`unit region ${row.id}: unexpected assignment_type`);
    if (!allowedRegions.has(row.region_class)) errors.push(`unit region ${row.id}: unexpected region ${row.region_class}`);
    if (!rateIds.has(row.unit_price_id)) {
      errors.push(`unit region ${row.id}: missing unit price ${row.unit_price_id}`);
    } else if (rateById.get(row.unit_price_id)?.region_class !== row.region_class) {
      errors.push(`unit region ${row.id}: region and unit price mismatch`);
    }
    if (!sourceIds.has(row.source_id)) errors.push(`unit region ${row.id}: missing source ${row.source_id}`);
    if (unitRegionAssignmentsMeta?.source_id && row.source_id !== unitRegionAssignmentsMeta.source_id) {
      errors.push(`unit region ${row.id}: source differs from assignment metadata`);
    }
    if (unitRegionAssignmentsMeta?.effective_reference_date && row.effective_reference_date !== unitRegionAssignmentsMeta.effective_reference_date) {
      errors.push(`unit region ${row.id}: reference date differs from assignment metadata`);
    }
    if (row.verification_status !== "IMPORTED_CURRENT_SOURCE_NEEDS_HUMAN_CHECK" && row.verification_status !== "VERIFIED_CURRENT") {
      errors.push(`unit region ${row.id}: unexpected status ${row.verification_status}`);
    }
    const key = `${row.prefecture}|${row.locality}`;
    if (localityKeys.has(key)) errors.push(`unit region: duplicate locality ${key}`);
    localityKeys.add(key);
    explicitRegions.add(row.region_class);
  }

  if (Number.isFinite(unitRegionAssignmentsMeta?.explicit_assignment_count) && unitRegionAssignmentsMeta.explicit_assignment_count !== unitRegionAssignments.length) {
    errors.push("unit region: explicit assignment count mismatch");
  }

  for (const region of allowedRegions) {
    if (!explicitRegions.has(region)) errors.push(`unit region: missing explicit assignments for ${region}`);
  }

  if (!unitRegionAssignmentsMeta?.default_rule_present) errors.push("unit region: missing default その他 rule");
  const defaultRule = unitRegionAssignmentsMeta?.default_rule;
  if (defaultRule) {
    if (defaultRule.region_class !== "その他") errors.push("unit region: default rule must point to その他");
    if (!rateIds.has(defaultRule.unit_price_id)) {
      errors.push("unit region: default rule missing unit price");
    } else if (rateById.get(defaultRule.unit_price_id)?.region_class !== "その他") {
      errors.push("unit region: default rule unit price must point to その他");
    }
    if (!sourceIds.has(defaultRule.source_id)) errors.push("unit region: default rule missing source");
    if (unitRegionAssignmentsMeta?.effective_reference_date && defaultRule.effective_reference_date !== unitRegionAssignmentsMeta.effective_reference_date) {
      errors.push("unit region: default rule reference date differs from assignment metadata");
    }
  }
}


if (unitPriceReview) {
  const rateIds = new Set(unitPrices.map((row) => row.id));
  const assignmentIds = new Set(unitRegionAssignments.map((row) => row.id));
  const sameHashes = (a, b) => JSON.stringify(a || []) === JSON.stringify(b || []);

  if ((unitPriceReview.reviewed_rate_ids || []).length || (unitPriceReview.reviewed_assignment_ids || []).length || unitPriceReview.reviewed_default_rule) {
    if (!sameHashes(unitPriceReview.source_sha256, unitPriceMeta?.source_sha256)) {
      errors.push("unit price review: rate source hash is stale");
    }
    if (!sameHashes(unitPriceReview.assignment_source_sha256, unitRegionAssignmentsMeta?.source_sha256)) {
      errors.push("unit price review: assignment source hash is stale");
    }
  }

  for (const id of unitPriceReview.reviewed_rate_ids || []) {
    if (!rateIds.has(id)) errors.push(`unit price review: missing rate ${id}`);
  }
  for (const id of unitPriceReview.reviewed_assignment_ids || []) {
    if (!assignmentIds.has(id)) errors.push(`unit price review: missing assignment ${id}`);
  }
}

if (feeGuidance.length) {
  const guidanceIds = new Set(feeGuidance.map((node) => node.id));
  const feeIds = new Set(feeSkeleton.map((node) => node.id));
  const allowed = new Set(["KNOWN_AFTER_TEXT","INHERITED_UNVERIFIED","UNKNOWN","VERIFIED_CURRENT"]);

  for (const node of feeGuidance) {
    for (const field of ["id","number_path","title","service_scope","verification_status","structure_status"]) {
      if (!node[field] || (Array.isArray(node[field]) && node[field].length === 0)) {
        errors.push(`fee guidance ${node.id || "(missing id)"}: missing ${field}`);
      }
    }
    if (!allowed.has(node.verification_status)) errors.push(`fee guidance ${node.id}: unexpected status ${node.verification_status}`);
    if (node.parent_id && !guidanceIds.has(node.parent_id)) errors.push(`fee guidance ${node.id}: missing parent ${node.parent_id}`);
    for (const feeId of node.related_fee_ids || []) if (!feeIds.has(feeId)) errors.push(`fee guidance ${node.id}: missing fee ${feeId}`);
    for (const evidence of node.evidence || []) if (!sourceIds.has(evidence.source_id)) errors.push(`fee guidance ${node.id}: missing source ${evidence.source_id}`);
  }

  for (const relation of feeGuidanceRelations) {
    if (!guidanceIds.has(relation.from_guidance_id)) errors.push(`fee guidance relation: missing from ${relation.from_guidance_id}`);
    if (!feeIds.has(relation.to_fee_id)) errors.push(`fee guidance relation: missing fee ${relation.to_fee_id}`);
  }
  for (const event of feeGuidanceEvents) {
    if (!sourceIds.has(event.source_id)) errors.push(`fee guidance event ${event.id}: missing source ${event.source_id}`);
    for (const id of event.target_ids || []) if (!guidanceIds.has(id)) errors.push(`fee guidance event ${event.id}: missing target ${id}`);
  }
  for (const item of feeGuidanceChain) if (!sourceIds.has(item.source_id)) errors.push(`fee guidance source chain: missing source ${item.source_id}`);
  for (const item of feeGuidanceReview.reviewed_nodes || []) if (!guidanceIds.has(item.guidance_id)) errors.push(`fee guidance review: missing node ${item.guidance_id}`);

  const candidateIds = new Set();
  for (const candidate of feeGuidanceCandidates) {
    for (const field of ["id","guidance_id","candidate_kind","source_id","source_locator","source_period","candidate_summary","replay_status","human_verification_status"]) {
      if (!candidate[field]) errors.push(`fee guidance candidate ${candidate.id || "(missing id)"}: missing ${field}`);
    }
    if (candidateIds.has(candidate.id)) errors.push(`fee guidance candidate: duplicate id ${candidate.id}`);
    candidateIds.add(candidate.id);
    if (!guidanceIds.has(candidate.guidance_id)) errors.push(`fee guidance candidate ${candidate.id}: missing guidance ${candidate.guidance_id}`);
    if (!sourceIds.has(candidate.source_id)) errors.push(`fee guidance candidate ${candidate.id}: missing source ${candidate.source_id}`);
    if (candidate.human_verification_status !== "NOT_REVIEWED") errors.push(`fee guidance candidate ${candidate.id}: unexpected human verification status`);
    if (candidate.structured_facts && (typeof candidate.structured_facts !== "object" || Array.isArray(candidate.structured_facts) || Object.keys(candidate.structured_facts).length === 0)) {
      errors.push(`fee guidance candidate ${candidate.id}: invalid structured_facts`);
    }
  }

  const replayGuidanceIds = new Set();
  for (const coverage of feeGuidanceReplayCoverage) {
    for (const field of ["guidance_id","baseline","checkpoints","replay_status","coverage_as_of","human_verification_status"]) {
      if (coverage[field] == null || (Array.isArray(coverage[field]) && coverage[field].length === 0)) {
        errors.push(`fee guidance replay ${coverage.guidance_id || "(missing id)"}: missing ${field}`);
      }
    }
    if (!guidanceIds.has(coverage.guidance_id)) errors.push(`fee guidance replay: missing guidance ${coverage.guidance_id}`);
    if (replayGuidanceIds.has(coverage.guidance_id)) errors.push(`fee guidance replay: duplicate guidance ${coverage.guidance_id}`);
    replayGuidanceIds.add(coverage.guidance_id);
    if (coverage.human_verification_status !== "NOT_REVIEWED") errors.push(`fee guidance replay ${coverage.guidance_id}: unexpected human verification status`);
    if (!coverage.baseline?.source_id || !sourceIds.has(coverage.baseline.source_id)) errors.push(`fee guidance replay ${coverage.guidance_id}: invalid baseline source`);
    for (const checkpoint of coverage.checkpoints || []) {
      for (const field of ["source_id","effective_from","effect","evidence","status"]) {
        if (!checkpoint[field]) errors.push(`fee guidance replay ${coverage.guidance_id}: checkpoint missing ${field}`);
      }
      if (!sourceIds.has(checkpoint.source_id)) errors.push(`fee guidance replay ${coverage.guidance_id}: missing checkpoint source ${checkpoint.source_id}`);
      if (checkpoint.status !== "CHECKED") errors.push(`fee guidance replay ${coverage.guidance_id}: unchecked checkpoint ${checkpoint.source_id}`);
    }
  }
  const candidateGuidanceIds = new Set(feeGuidanceCandidates.map((candidate) => candidate.guidance_id));
  for (const id of candidateGuidanceIds) {
    if (!replayGuidanceIds.has(id)) errors.push(`fee guidance replay: missing coverage for candidate ${id}`);
  }

  if (feeGuidanceSourceManifest) {
    const segmentIds = new Set();
    const sourceLayouts = feeGuidanceSourceManifest.source_layouts || {};
    for (const [sourceId, layout] of Object.entries(sourceLayouts)) {
      if (!sourceIds.has(sourceId)) errors.push(`fee guidance source manifest: layout source missing ${sourceId}`);
      if (!["left","right"].includes(layout?.current_column)) errors.push(`fee guidance source manifest: invalid current column for ${sourceId}`);
      if (!layout?.header_semantics) errors.push(`fee guidance source manifest: missing header semantics for ${sourceId}`);
    }
    for (const segment of feeGuidanceSourceManifest.segments || []) {
      for (const field of ["id","guidance_ids","source_id","role","page_start","page_end","item_start","item_end"]) {
        if (segment[field] == null || (Array.isArray(segment[field]) && segment[field].length === 0)) {
          errors.push(`fee guidance source manifest ${segment.id || "(missing id)"}: missing ${field}`);
        }
      }
      if (segmentIds.has(segment.id)) errors.push(`fee guidance source manifest: duplicate segment ${segment.id}`);
      segmentIds.add(segment.id);
      if (!sourceIds.has(segment.source_id)) errors.push(`fee guidance source manifest ${segment.id}: missing source ${segment.source_id}`);
      if (!sourceLayouts[segment.source_id]) errors.push(`fee guidance source manifest ${segment.id}: missing source layout ${segment.source_id}`);
      for (const id of segment.guidance_ids || []) if (!guidanceIds.has(id)) errors.push(`fee guidance source manifest ${segment.id}: missing guidance ${id}`);
      if (!Number.isInteger(segment.page_start) || !Number.isInteger(segment.page_end) || segment.page_start < 1 || segment.page_end < segment.page_start) {
        errors.push(`fee guidance source manifest ${segment.id}: invalid page range`);
      }
    }
  }

  if (feeGuidanceSnapshots) {
    if (feeGuidanceSnapshots.policy !== feeGuidanceSourceManifest?.policy) errors.push("fee guidance snapshots: policy differs from manifest");
    const manifestById = new Map((feeGuidanceSourceManifest?.segments || []).map((segment) => [segment.id, segment]));
    const snapshotIds = new Set();
    for (const snapshot of feeGuidanceSnapshots.segments || []) {
      if (snapshotIds.has(snapshot.id)) errors.push(`fee guidance snapshots: duplicate segment ${snapshot.id}`);
      snapshotIds.add(snapshot.id);
      const manifestSegment = manifestById.get(snapshot.id);
      if (!manifestSegment) errors.push(`fee guidance snapshots: segment not in manifest ${snapshot.id}`);
      if (!sourceIds.has(snapshot.source_id)) errors.push(`fee guidance snapshots ${snapshot.id}: missing source ${snapshot.source_id}`);
      if (!snapshot.text || !snapshot.text_sha256) errors.push(`fee guidance snapshots ${snapshot.id}: missing text/hash`);
      if ((feeGuidanceSnapshots.format_version || 1) >= 2) {
        if (!snapshot.current_side_text || !snapshot.current_side_text_sha256) errors.push(`fee guidance snapshots ${snapshot.id}: missing current-side text/hash`);
        if (!["left","right"].includes(snapshot.current_column)) errors.push(`fee guidance snapshots ${snapshot.id}: invalid current column`);
        if (manifestSegment && snapshot.current_column !== feeGuidanceSourceManifest?.source_layouts?.[snapshot.source_id]?.current_column) {
          errors.push(`fee guidance snapshots ${snapshot.id}: current column differs from manifest`);
        }
      }
      if ((feeGuidanceSnapshots.format_version || 1) >= 3) {
        if (!snapshot.item_text || !snapshot.item_text_sha256) errors.push(`fee guidance snapshots ${snapshot.id}: missing item text/hash`);
        if (manifestSegment?.patch_start || manifestSegment?.patch_end) {
          if (!manifestSegment?.patch_start || !manifestSegment?.patch_end) errors.push(`fee guidance source manifest ${snapshot.id}: incomplete patch boundaries`);
          if (!snapshot.patch_text || !snapshot.patch_text_sha256) errors.push(`fee guidance snapshots ${snapshot.id}: missing patch text/hash`);
        }
      }
      if (snapshot.verification_status !== "IMPORTED_OFFICIAL_PDF_NEEDS_HUMAN_CHECK") errors.push(`fee guidance snapshots ${snapshot.id}: unsafe verification status`);
    }
  }

  if (feeGuidanceAssembly) {
    const snapshotIds = new Set((feeGuidanceSnapshots?.segments || []).map((snapshot) => snapshot.id));
    const assembledGuidanceIds = new Set();
    for (const item of feeGuidanceAssembly.items || []) {
      if (!item.guidance_id || !guidanceIds.has(item.guidance_id)) errors.push(`fee guidance assembly: invalid guidance ${item.guidance_id}`);
      if (assembledGuidanceIds.has(item.guidance_id)) errors.push(`fee guidance assembly: duplicate guidance ${item.guidance_id}`);
      assembledGuidanceIds.add(item.guidance_id);
      if (!snapshotIds.has(item.baseline_snapshot_id)) errors.push(`fee guidance assembly ${item.guidance_id}: missing baseline snapshot ${item.baseline_snapshot_id}`);
      for (const patch of item.patches || []) {
        if (!snapshotIds.has(patch.snapshot_id)) errors.push(`fee guidance assembly ${item.guidance_id}: missing patch snapshot ${patch.snapshot_id}`);
        if (patch.operation !== "insert_before" || !patch.baseline_anchor) errors.push(`fee guidance assembly ${item.guidance_id}: invalid patch operation`);
      }
    }
    const expected = new Set(["fee-guidance.dayservice.4","fee-guidance.dayservice.5","fee-guidance.dayservice.6","fee-guidance.dayservice.7","fee-guidance.dayservice.7-2","fee-guidance.dayservice.18","fee-guidance.dayservice.24","fee-guidance.dayservice.25"]);
    for (const id of expected) if (!assembledGuidanceIds.has(id)) errors.push(`fee guidance assembly: missing scoped guidance ${id}`);
    if (assembledGuidanceIds.size !== expected.size) errors.push("fee guidance assembly: unexpected scoped guidance count");
  }

  if (feeGuidanceCurrentCandidates) {
    const sha256 = (value) => createHash("sha256").update(value, "utf8").digest("hex");
    if (feeGuidanceCurrentCandidates.policy !== feeGuidanceAssembly?.policy) errors.push("fee guidance current candidates: policy differs from assembly");
    if (feeGuidanceCurrentCandidates.reconstruction_status !== "MACHINE_RECONSTRUCTED_NEEDS_HUMAN_CHECK") errors.push("fee guidance current candidates: unsafe reconstruction status");
    const candidateIds = new Set();
    for (const item of feeGuidanceCurrentCandidates.items || []) {
      if (!guidanceIds.has(item.guidance_id)) errors.push(`fee guidance current candidate: missing guidance ${item.guidance_id}`);
      if (candidateIds.has(item.guidance_id)) errors.push(`fee guidance current candidate: duplicate guidance ${item.guidance_id}`);
      candidateIds.add(item.guidance_id);
      if (!item.candidate_text || !item.candidate_text_sha256) errors.push(`fee guidance current candidate ${item.guidance_id}: missing text/hash`);
      else if (sha256(item.candidate_text) !== item.candidate_text_sha256) errors.push(`fee guidance current candidate ${item.guidance_id}: text hash mismatch`);
      if (item.reconstruction_status !== "MACHINE_RECONSTRUCTED_NEEDS_HUMAN_CHECK") errors.push(`fee guidance current candidate ${item.guidance_id}: unsafe status`);
      if (item.human_verification_status !== "NOT_REVIEWED") errors.push(`fee guidance current candidate ${item.guidance_id}: unexpected human verification status`);
      if (!replayGuidanceIds.has(item.guidance_id)) errors.push(`fee guidance current candidate ${item.guidance_id}: missing replay coverage`);
      if (!item.evidence?.length) errors.push(`fee guidance current candidate ${item.guidance_id}: missing evidence`);
    }
    const configuredIds = new Set((feeGuidanceAssembly?.items || []).map((item) => item.guidance_id));
    for (const id of configuredIds) if (!candidateIds.has(id)) errors.push(`fee guidance current candidates: missing configured item ${id}`);

    // Regression guards from the 2026-09-23 independent primary-source audit.
    // These assert source-text facts only; they do not promote any verification status.
    const compactCandidate = (value) => String(value || "").normalize("NFKC").replace(/\s+/g, "");
    const currentCandidateById = new Map(
      (feeGuidanceCurrentCandidates.items || []).map((item) => [item.guidance_id, item])
    );
    const pageLabelArtifact = /(^|\n)\s*(?:-\s*)?\d{1,3}\s*-\s*(?=\n|$)/;

    const scale = currentCandidateById.get("fee-guidance.dayservice.6");
    if (scale) {
      const text = compactCandidate(scale.candidate_text);
      if (!text.includes(compactCandidate("⑤感染症又は災害の発生を理由とする利用者数の減少が一定以上生じている場合の事業所規模別の報酬区分の決定に係る特例については、別途通知を参照すること。"))) {
        errors.push("fee guidance current candidate 6: independently verified item ⑤ is missing");
      }
    }

    const disaster = currentCandidateById.get("fee-guidance.dayservice.7");
    if (disaster) {
      const text = compactCandidate(disaster.candidate_text);
      if (!text.includes(compactCandidate("災害時等の取扱い災害その他のやむを得ない理由による定員超過利用については、"))) {
        errors.push("fee guidance current candidate 7: verified opening text differs");
      }
      if (text.includes(compactCandidate("災害時等の取扱い、災害その他"))) {
        errors.push("fee guidance current candidate 7: spurious leading comma returned");
      }
      if (!text.includes(compactCandidate("場合は翌月も含む。）の翌月から所定単位数の減算を行う"))) {
        errors.push("fee guidance current candidate 7: verified closing parenthesis is missing");
      }
    }

    const capacity = currentCandidateById.get("fee-guidance.dayservice.24");
    if (capacity) {
      const text = compactCandidate(capacity.candidate_text);
      if (pageLabelArtifact.test(capacity.candidate_text)) {
        errors.push("fee guidance current candidate 24: PDF page label artifact returned");
      }
      if (!text.includes(compactCandidate("第27号。以下「通所介護費等の算定方法」という。）において、"))) {
        errors.push("fee guidance current candidate 24: first verified closing parenthesis is missing");
      }
      if (!text.includes(compactCandidate("場合は翌月も含む。）の翌月から所定単位数の減算を行う"))) {
        errors.push("fee guidance current candidate 24: second verified closing parenthesis is missing");
      }
    }

    const staffing = currentCandidateById.get("fee-guidance.dayservice.25");
    if (staffing) {
      if (pageLabelArtifact.test(staffing.candidate_text)) errors.push("fee guidance current candidate 25: PDF page label artifact returned");
      if (!(staffing.patch_snapshot_ids || []).includes("dayservice-25-r8-patch")) errors.push("fee guidance current candidate 25: missing R8 patch citation");
      if (!staffing.candidate_text.includes("別紙様式７") && !staffing.candidate_text.includes("別紙様式7")) errors.push("fee guidance current candidate 25: R8 report form missing");
    }
  }

  if (feeGuidanceMeta) {
    if (feeGuidanceMeta.counts?.total !== feeGuidance.length) errors.push("fee guidance meta: total mismatch");
    const actual = feeGuidance.reduce((acc,node)=>{acc[node.verification_status]=(acc[node.verification_status]||0)+1;return acc;},{});
    for (const [status,count] of Object.entries(actual)) {
      if (feeGuidanceMeta.counts?.[status] !== count) errors.push(`fee guidance meta: ${status} count mismatch`);
    }
  }
}

if (careActNodes.length) {
  const careIds = new Set(careActNodes.map((node) => node.id));
  const careArticleIds = new Set(careActNodes.filter((node) => node.node_type === "article").map((node) => node.id));
  const ordinanceIds = new Set(ordinanceNodes.map((node) => node.id));
  const feeIds = new Set(feeSkeleton.map((node) => node.id));
  const noticeIdsCurrent = new Set(noticeSkeleton.map((node) => node.id));

  for (const node of careActNodes) {
    for (const field of ["node_type","law_id","article_num","official_text","service_scope","source_url","verification_status"]) {
      if (!node[field]) errors.push(`care act node ${node.id}: missing ${field}`);
    }
    if (!["IMPORTED_NEEDS_HUMAN_CHECK","VERIFIED_CURRENT"].includes(node.verification_status)) {
      errors.push(`care act node ${node.id}: unexpected status ${node.verification_status}`);
    }
    if (node.parent_id && !careIds.has(node.parent_id)) errors.push(`care act node ${node.id}: missing parent ${node.parent_id}`);
  }

  for (const relation of careActRelations) {
    if (!careIds.has(relation.from)) errors.push(`care act relation: missing from ${relation.from}`);
    if (relation.target_layer === "care_insurance_act" && !careIds.has(relation.to)) errors.push(`care act relation: missing law target ${relation.to}`);
    if (relation.target_layer === "ordinance37" && !ordinanceIds.has(relation.to)) errors.push(`care act relation: missing ordinance target ${relation.to}`);
    if (relation.target_layer === "remuneration" && !feeIds.has(relation.to)) errors.push(`care act relation: missing fee target ${relation.to}`);
    if (relation.target_layer === "interpretation_notice" && !noticeIdsCurrent.has(relation.to)) errors.push(`care act relation: missing notice target ${relation.to}`);
  }

  if (careActScope) {
    for (const number of careActScope.articles || []) {
      if (!careArticleIds.has(`careact.article.${number}`)) errors.push(`care act scope: missing article ${number}`);
    }
  }

  const careById = new Map(careActNodes.map((node) => [node.id,node]));
  for (const item of careActReview.reviewed_articles || []) {
    const node = careById.get(item.article_id);
    if (!node || node.node_type !== "article") {
      errors.push(`care act review: missing article ${item.article_id}`);
      continue;
    }
    if (item.text_sha256 !== node.text_sha256) errors.push(`care act review ${item.article_id}: reviewed hash is stale`);
    if (item.status !== "HUMAN_VERIFIED_AGAINST_OFFICIAL_SOURCE") errors.push(`care act review ${item.article_id}: unexpected status ${item.status}`);
  }
}

if (errors.length) {
  console.error(errors.join("\n"));
  process.exit(1);
}

console.log(
  `Data validation PASS: ${questions.length} questions, ${rules.length} rules, ${notices.length} notice nodes, ${qa.length} curated Q&A items, ${qaCorpus.length} imported Q&A rows, ${(qaCandidates.candidates || []).reduce((n, g) => n + (g.candidates || []).length, 0)} review-only Q&A candidates, ${ordinanceNodes.length} ordinance nodes, ${noticeSkeleton.length} notice-skeleton nodes, ${noticeHistory.length} historical notice candidates, ${feeSkeleton.length} remuneration nodes, ${feeCurrentText.length} current remuneration texts, ${feeGuidance.length} fee-guidance nodes, ${careActNodes.length} Care Insurance Act nodes, ${sources.length} sources.`
);
