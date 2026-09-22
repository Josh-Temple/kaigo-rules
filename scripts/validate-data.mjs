import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

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
  const allowedFeeStatuses = new Set(["BASE_TEXT_REPLAY_PENDING","KNOWN_AFTER_TEXT","OUT_OF_CORE_SCOPE","VERIFIED_CURRENT","UNKNOWN"]);
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
}

if (errors.length) {
  console.error(errors.join("\n"));
  process.exit(1);
}

console.log(
  `Data validation PASS: ${questions.length} questions, ${rules.length} rules, ${notices.length} notice nodes, ${qa.length} curated Q&A items, ${qaCorpus.length} imported Q&A rows, ${(qaCandidates.candidates || []).reduce((n, g) => n + (g.candidates || []).length, 0)} review-only Q&A candidates, ${ordinanceNodes.length} ordinance nodes, ${noticeSkeleton.length} notice-skeleton nodes, ${noticeHistory.length} historical notice candidates, ${feeSkeleton.length} remuneration nodes, ${sources.length} sources.`
);
