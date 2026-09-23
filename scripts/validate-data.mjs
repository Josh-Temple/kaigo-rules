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
const noticeEquipmentManifestPath = path.join(root, "data", "notice-equipment-source-manifest.json");
const noticeEquipmentManifest = fs.existsSync(noticeEquipmentManifestPath)
  ? JSON.parse(fs.readFileSync(noticeEquipmentManifestPath, "utf8"))
  : null;
const noticeEquipmentSnapshotsPath = path.join(root, "data", "notice-equipment-source-snapshots.json");
const noticeEquipmentSnapshots = fs.existsSync(noticeEquipmentSnapshotsPath)
  ? JSON.parse(fs.readFileSync(noticeEquipmentSnapshotsPath, "utf8"))
  : null;
const noticeEquipmentAssemblyPath = path.join(root, "data", "notice-equipment-current-assembly.json");
const noticeEquipmentAssembly = fs.existsSync(noticeEquipmentAssemblyPath)
  ? JSON.parse(fs.readFileSync(noticeEquipmentAssemblyPath, "utf8"))
  : null;
const noticeEquipmentReplayPath = path.join(root, "data", "notice-equipment-replay-coverage.json");
const noticeEquipmentReplay = fs.existsSync(noticeEquipmentReplayPath)
  ? JSON.parse(fs.readFileSync(noticeEquipmentReplayPath, "utf8"))
  : null;
const noticeEquipmentCandidatesPath = path.join(root, "data", "notice-equipment-current-text-candidates.json");
const noticeEquipmentCandidates = fs.existsSync(noticeEquipmentCandidatesPath)
  ? JSON.parse(fs.readFileSync(noticeEquipmentCandidatesPath, "utf8"))
  : null;
const noticePersonnelManifestPath = path.join(root, "data", "notice-personnel-source-manifest.json");
const noticePersonnelManifest = fs.existsSync(noticePersonnelManifestPath)
  ? JSON.parse(fs.readFileSync(noticePersonnelManifestPath, "utf8"))
  : null;
const noticePersonnelSnapshotsPath = path.join(root, "data", "notice-personnel-source-snapshots.json");
const noticePersonnelSnapshots = fs.existsSync(noticePersonnelSnapshotsPath)
  ? JSON.parse(fs.readFileSync(noticePersonnelSnapshotsPath, "utf8"))
  : null;
const noticePersonnelAssemblyPath = path.join(root, "data", "notice-personnel-current-assembly.json");
const noticePersonnelAssembly = fs.existsSync(noticePersonnelAssemblyPath)
  ? JSON.parse(fs.readFileSync(noticePersonnelAssemblyPath, "utf8"))
  : null;
const noticePersonnelReplayPath = path.join(root, "data", "notice-personnel-replay-coverage.json");
const noticePersonnelReplay = fs.existsSync(noticePersonnelReplayPath)
  ? JSON.parse(fs.readFileSync(noticePersonnelReplayPath, "utf8"))
  : null;
const noticePersonnelCandidatesPath = path.join(root, "data", "notice-personnel-current-text-candidates.json");
const noticePersonnelCandidates = fs.existsSync(noticePersonnelCandidatesPath)
  ? JSON.parse(fs.readFileSync(noticePersonnelCandidatesPath, "utf8"))
  : null;
const noticeOperationModernManifestPath = path.join(root, "data", "notice-operation-modern-source-manifest.json");
const noticeOperationModernManifest = fs.existsSync(noticeOperationModernManifestPath)
  ? JSON.parse(fs.readFileSync(noticeOperationModernManifestPath, "utf8"))
  : null;
const noticeOperationModernSnapshotsPath = path.join(root, "data", "notice-operation-modern-source-snapshots.json");
const noticeOperationModernSnapshots = fs.existsSync(noticeOperationModernSnapshotsPath)
  ? JSON.parse(fs.readFileSync(noticeOperationModernSnapshotsPath, "utf8"))
  : null;
const noticeOperationModernAssemblyPath = path.join(root, "data", "notice-operation-modern-current-assembly.json");
const noticeOperationModernAssembly = fs.existsSync(noticeOperationModernAssemblyPath)
  ? JSON.parse(fs.readFileSync(noticeOperationModernAssemblyPath, "utf8"))
  : null;
const noticeOperationModernReplayPath = path.join(root, "data", "notice-operation-modern-replay-coverage.json");
const noticeOperationModernReplay = fs.existsSync(noticeOperationModernReplayPath)
  ? JSON.parse(fs.readFileSync(noticeOperationModernReplayPath, "utf8"))
  : null;
const noticeOperationModernCandidatesPath = path.join(root, "data", "notice-operation-modern-current-text-candidates.json");
const noticeOperationModernCandidates = fs.existsSync(noticeOperationModernCandidatesPath)
  ? JSON.parse(fs.readFileSync(noticeOperationModernCandidatesPath, "utf8"))
  : null;
const noticeOperationLegacyManifestPath = path.join(root, "data", "notice-operation-legacy-source-manifest.json");
const noticeOperationLegacyManifest = fs.existsSync(noticeOperationLegacyManifestPath)
  ? JSON.parse(fs.readFileSync(noticeOperationLegacyManifestPath, "utf8"))
  : null;
const noticeOperationLegacySnapshotsPath = path.join(root, "data", "notice-operation-legacy-source-snapshots.json");
const noticeOperationLegacySnapshots = fs.existsSync(noticeOperationLegacySnapshotsPath)
  ? JSON.parse(fs.readFileSync(noticeOperationLegacySnapshotsPath, "utf8"))
  : null;
const noticeOperationLegacyAssemblyPath = path.join(root, "data", "notice-operation-legacy-current-assembly.json");
const noticeOperationLegacyAssembly = fs.existsSync(noticeOperationLegacyAssemblyPath)
  ? JSON.parse(fs.readFileSync(noticeOperationLegacyAssemblyPath, "utf8"))
  : null;
const noticeOperationLegacyReplayPath = path.join(root, "data", "notice-operation-legacy-replay-coverage.json");
const noticeOperationLegacyReplay = fs.existsSync(noticeOperationLegacyReplayPath)
  ? JSON.parse(fs.readFileSync(noticeOperationLegacyReplayPath, "utf8"))
  : null;
const noticeOperationLegacyCandidatesPath = path.join(root, "data", "notice-operation-legacy-current-text-candidates.json");
const noticeOperationLegacyCandidates = fs.existsSync(noticeOperationLegacyCandidatesPath)
  ? JSON.parse(fs.readFileSync(noticeOperationLegacyCandidatesPath, "utf8"))
  : null;
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

  const requiredRouki25EquipmentIds = [
    "notice.dayservice.equipment.office",
    "notice.dayservice.equipment.dining-training-room",
    "notice.dayservice.equipment.fire-safety",
    "notice.dayservice.equipment.shared-equipment",
    "notice.dayservice.equipment.overnight-service",
  ];
  for (const id of requiredRouki25EquipmentIds) {
    if (!noticeSkeletonIds.has(id)) {
      errors.push(`notice skeleton: missing required day-service equipment node ${id}`);
    }
  }
  const noticeSourceChainIds = new Set(noticeSourceChain.map((entry) => entry.source_id));
  for (const sourceId of ["mhlw-h27-interpretation-redline", "mhlw-h30-interpretation-redline"]) {
    if (!noticeSourceChainIds.has(sourceId)) {
      errors.push(`notice source chain: missing required forward-replay source ${sourceId}`);
    }
  }

  const h30SharingRestructure = noticeAmendments.find(
    (event) => event.id === "rouki25.h30.dayservice.restructure-equipment-sharing"
  );
  if (!h30SharingRestructure ||
      h30SharingRestructure.operation !== "split_and_relocate_fragment" ||
      h30SharingRestructure.related_target_node_id !== "notice.dayservice.equipment.shared-equipment") {
    errors.push("notice amendment events: missing H30 equipment-sharing restructure");
  }

  const equipmentPipelineParts = [
    noticeEquipmentManifest,
    noticeEquipmentSnapshots,
    noticeEquipmentAssembly,
    noticeEquipmentReplay,
    noticeEquipmentCandidates,
  ];
  if (equipmentPipelineParts.some(Boolean) && !equipmentPipelineParts.every(Boolean)) {
    errors.push("notice equipment reconstruction: incomplete pipeline files");
  }
  if (equipmentPipelineParts.every(Boolean)) {
    const expectedEquipmentIds = new Set(requiredRouki25EquipmentIds);
    const sameIdSet = (values) =>
      values.length === expectedEquipmentIds.size &&
      values.every((id) => expectedEquipmentIds.has(id));

    const manifestSegments = noticeEquipmentManifest.segments || [];
    if (!sameIdSet(manifestSegments.map((segment) => segment.notice_id))) {
      errors.push("notice equipment manifest: unexpected equipment coverage");
    }
    for (const segment of manifestSegments) {
      if (!sourceIds.has(segment.source_id)) errors.push(`notice equipment manifest ${segment.id}: missing source ${segment.source_id}`);
      if (!segment.body_start || !segment.body_end || !segment.page_start || !segment.page_end) {
        errors.push(`notice equipment manifest ${segment.id}: incomplete extraction boundary`);
      }
    }

    const snapshotById = new Map((noticeEquipmentSnapshots.segments || []).map((item) => [item.id, item]));
    if (!sameIdSet((noticeEquipmentSnapshots.segments || []).map((item) => item.notice_id))) {
      errors.push("notice equipment snapshots: unexpected equipment coverage");
    }
    for (const snapshot of noticeEquipmentSnapshots.segments || []) {
      if (!sourceIds.has(snapshot.source_id)) errors.push(`notice equipment snapshot ${snapshot.id}: missing source ${snapshot.source_id}`);
      if (snapshot.verification_status !== "IMPORTED_OFFICIAL_PDF_NEEDS_HUMAN_CHECK") {
        errors.push(`notice equipment snapshot ${snapshot.id}: unsafe verification status`);
      }
      if (!snapshot.body_text || !snapshot.body_text_sha256 ||
          createHash("sha256").update(snapshot.body_text, "utf8").digest("hex") !== snapshot.body_text_sha256) {
        errors.push(`notice equipment snapshot ${snapshot.id}: body text/hash mismatch`);
      }
    }

    if (!sameIdSet((noticeEquipmentAssembly.items || []).map((item) => item.notice_id))) {
      errors.push("notice equipment assembly: unexpected equipment coverage");
    }

    const replayById = new Map((noticeEquipmentReplay || []).map((item) => [item.notice_id, item]));
    if (!sameIdSet((noticeEquipmentReplay || []).map((item) => item.notice_id))) {
      errors.push("notice equipment replay: unexpected equipment coverage");
    }
    for (const coverage of noticeEquipmentReplay || []) {
      if (coverage.human_verification_status !== "NOT_REVIEWED") {
        errors.push(`notice equipment replay ${coverage.notice_id}: unexpected human verification status`);
      }
      for (const checkpoint of coverage.checkpoints || []) {
        if (!sourceIds.has(checkpoint.source_id)) {
          errors.push(`notice equipment replay ${coverage.notice_id}: missing checkpoint source ${checkpoint.source_id}`);
        }
        if (checkpoint.status !== "CHECKED") {
          errors.push(`notice equipment replay ${coverage.notice_id}: unchecked checkpoint ${checkpoint.source_id}`);
        }
      }
    }

    const candidates = noticeEquipmentCandidates.items || [];
    if (!sameIdSet(candidates.map((item) => item.notice_id))) {
      errors.push("notice equipment candidates: unexpected equipment coverage");
    }
    const candidateById = new Map(candidates.map((item) => [item.notice_id, item]));
    for (const candidate of candidates) {
      if (candidate.reconstruction_status !== "MACHINE_RECONSTRUCTED_NEEDS_HUMAN_CHECK" ||
          candidate.human_verification_status !== "NOT_REVIEWED") {
        errors.push(`notice equipment candidate ${candidate.notice_id}: unsafe status`);
      }
      if (!candidate.candidate_text || !candidate.candidate_text_sha256 ||
          createHash("sha256").update(candidate.candidate_text, "utf8").digest("hex") !== candidate.candidate_text_sha256) {
        errors.push(`notice equipment candidate ${candidate.notice_id}: text/hash mismatch`);
      }
      const snapshot = snapshotById.get(candidate.baseline_snapshot_id);
      if (!snapshot || snapshot.notice_id !== candidate.notice_id ||
          snapshot.body_text_sha256 !== candidate.candidate_text_sha256) {
        errors.push(`notice equipment candidate ${candidate.notice_id}: baseline snapshot mismatch`);
      }
      const coverage = replayById.get(candidate.notice_id);
      if (!coverage || candidate.replay_status !== coverage.replay_status) {
        errors.push(`notice equipment candidate ${candidate.notice_id}: replay coverage mismatch`);
      }
    }

    const compact = (value) => String(value || "").normalize("NFKC").replace(/\s+/g, "");
    const requireCandidateText = (id, needle, label) => {
      const item = candidateById.get(id);
      if (!item || !compact(item.candidate_text).includes(compact(needle))) {
        errors.push(`notice equipment candidate ${id}: ${label}`);
      }
    };
    requireCandidateText(
      "notice.dayservice.equipment.office",
      "原則として一の建物につき、一の事業所とする",
      "verified office wording missing"
    );
    requireCandidateText(
      "notice.dayservice.equipment.dining-training-room",
      "狭隘な部屋を多数設置することにより面積を確保すべきではない",
      "verified dining/training-room wording missing"
    );
    const dining = candidateById.get("notice.dayservice.equipment.dining-training-room");
    if (dining && compact(dining.candidate_text).includes(compact("指定通所リハビリテーション"))) {
      errors.push("notice equipment candidate dining-training-room: removed H30 shared-space fragment returned");
    }
    requireCandidateText(
      "notice.dayservice.equipment.fire-safety",
      "消防法その他の法令等に規定された設備",
      "verified fire-safety wording missing"
    );
    requireCandidateText(
      "notice.dayservice.equipment.shared-equipment",
      "病院、診療所、介護老人保健施設又は介護医療院",
      "verified H30 shared-equipment scope missing"
    );
    requireCandidateText(
      "notice.dayservice.equipment.shared-equipment",
      "玄関、廊下、階段、送迎車両",
      "verified H30 common-equipment examples missing"
    );
    requireCandidateText(
      "notice.dayservice.equipment.overnight-service",
      "変更の事由が生じてから10日以内",
      "verified overnight-service change deadline missing"
    );
    requireCandidateText(
      "notice.dayservice.equipment.overnight-service",
      "休止又は廃止の日の１月前まで",
      "verified overnight-service suspension/closure deadline missing"
    );
  }

  const requiredRouki25PersonnelIds = [
    "notice.dayservice.personnel.staffing",
    "notice.dayservice.personnel.life-counselor",
    "notice.dayservice.personnel.function-training",
    "notice.dayservice.personnel.manager",
  ];
  for (const id of requiredRouki25PersonnelIds) {
    if (!noticeSkeletonIds.has(id)) {
      errors.push(`notice skeleton: missing required day-service personnel node ${id}`);
    }
  }

  const r3NurseStaffingEvent = noticeAmendments.find(
    (event) => event.id === "rouki25.r3.dayservice.nurse-staffing-structure"
  );
  if (!r3NurseStaffingEvent ||
      r3NurseStaffingEvent.operation !== "replace_fragment" ||
      r3NurseStaffingEvent.target_node_id !== "notice.dayservice.personnel.staffing") {
    errors.push("notice amendment events: missing R3 nurse-staffing restructure");
  }

  const personnelPipelineParts = [
    noticePersonnelManifest,
    noticePersonnelSnapshots,
    noticePersonnelAssembly,
    noticePersonnelReplay,
    noticePersonnelCandidates,
  ];
  if (personnelPipelineParts.some(Boolean) && !personnelPipelineParts.every(Boolean)) {
    errors.push("notice personnel reconstruction: incomplete pipeline files");
  }
  if (personnelPipelineParts.every(Boolean)) {
    const expectedPersonnelIds = new Set(requiredRouki25PersonnelIds);
    const samePersonnelIdSet = (values) => {
      const actual = new Set(values);
      return actual.size === expectedPersonnelIds.size &&
        [...expectedPersonnelIds].every((id) => actual.has(id));
    };

    const manifestSegments = noticePersonnelManifest.segments || [];
    if (!samePersonnelIdSet(manifestSegments.map((segment) => segment.notice_id))) {
      errors.push("notice personnel manifest: unexpected personnel coverage");
    }
    const manifestSegmentIds = new Set();
    for (const segment of manifestSegments) {
      if (manifestSegmentIds.has(segment.id)) errors.push(`notice personnel manifest: duplicate segment ${segment.id}`);
      manifestSegmentIds.add(segment.id);
      if (!sourceIds.has(segment.source_id)) errors.push(`notice personnel manifest ${segment.id}: missing source ${segment.source_id}`);
      if (!segment.body_start || !segment.body_end || !segment.page_start || !segment.page_end) {
        errors.push(`notice personnel manifest ${segment.id}: incomplete extraction boundary`);
      }
    }

    const snapshots = noticePersonnelSnapshots.segments || [];
    const snapshotById = new Map(snapshots.map((item) => [item.id, item]));
    if (!samePersonnelIdSet(snapshots.map((item) => item.notice_id))) {
      errors.push("notice personnel snapshots: unexpected personnel coverage");
    }
    for (const snapshot of snapshots) {
      if (!sourceIds.has(snapshot.source_id)) errors.push(`notice personnel snapshot ${snapshot.id}: missing source ${snapshot.source_id}`);
      if (snapshot.verification_status !== "IMPORTED_OFFICIAL_PDF_NEEDS_HUMAN_CHECK") {
        errors.push(`notice personnel snapshot ${snapshot.id}: unsafe verification status`);
      }
      if (!snapshot.body_text || !snapshot.body_text_sha256 ||
          createHash("sha256").update(snapshot.body_text, "utf8").digest("hex") !== snapshot.body_text_sha256) {
        errors.push(`notice personnel snapshot ${snapshot.id}: body text/hash mismatch`);
      }
    }

    if (!samePersonnelIdSet((noticePersonnelAssembly.items || []).map((item) => item.notice_id))) {
      errors.push("notice personnel assembly: unexpected personnel coverage");
    }

    const replayById = new Map((noticePersonnelReplay || []).map((item) => [item.notice_id, item]));
    if (!samePersonnelIdSet((noticePersonnelReplay || []).map((item) => item.notice_id))) {
      errors.push("notice personnel replay: unexpected personnel coverage");
    }
    for (const coverage of noticePersonnelReplay || []) {
      if (coverage.human_verification_status !== "NOT_REVIEWED") {
        errors.push(`notice personnel replay ${coverage.notice_id}: unexpected human verification status`);
      }
      for (const checkpoint of coverage.checkpoints || []) {
        if (!sourceIds.has(checkpoint.source_id)) {
          errors.push(`notice personnel replay ${coverage.notice_id}: missing checkpoint source ${checkpoint.source_id}`);
        }
        if (checkpoint.status !== "CHECKED") {
          errors.push(`notice personnel replay ${coverage.notice_id}: unchecked checkpoint ${checkpoint.source_id}`);
        }
      }
    }

    const candidates = noticePersonnelCandidates.items || [];
    if (!samePersonnelIdSet(candidates.map((item) => item.notice_id))) {
      errors.push("notice personnel candidates: unexpected personnel coverage");
    }
    const candidateById = new Map(candidates.map((item) => [item.notice_id, item]));
    for (const candidate of candidates) {
      if (candidate.reconstruction_status !== "MACHINE_RECONSTRUCTED_NEEDS_HUMAN_CHECK" ||
          candidate.human_verification_status !== "NOT_REVIEWED") {
        errors.push(`notice personnel candidate ${candidate.notice_id}: unsafe status`);
      }
      if (!candidate.candidate_text || !candidate.candidate_text_sha256 ||
          createHash("sha256").update(candidate.candidate_text, "utf8").digest("hex") !== candidate.candidate_text_sha256) {
        errors.push(`notice personnel candidate ${candidate.notice_id}: text/hash mismatch`);
      }
      const baseline = snapshotById.get(candidate.baseline_snapshot_id);
      if (!baseline || baseline.notice_id !== candidate.notice_id) {
        errors.push(`notice personnel candidate ${candidate.notice_id}: baseline snapshot mismatch`);
      }
      for (const patchId of candidate.patch_snapshot_ids || []) {
        const patch = snapshotById.get(patchId);
        if (!patch || patch.notice_id !== candidate.notice_id) {
          errors.push(`notice personnel candidate ${candidate.notice_id}: patch snapshot mismatch ${patchId}`);
        }
      }
      const coverage = replayById.get(candidate.notice_id);
      if (!coverage || candidate.replay_status !== coverage.replay_status) {
        errors.push(`notice personnel candidate ${candidate.notice_id}: replay coverage mismatch`);
      }
    }

    const staffing = candidateById.get("notice.dayservice.personnel.staffing");
    if (staffing) {
      const compact = String(staffing.candidate_text || "").normalize("NFKC").replace(/\s+/g, "");
      const normalizedNeedle = (value) => String(value).normalize("NFKC").replace(/\s+/g, "");
      if (!compact.includes(normalizedNeedle("②８時間以上９時間未満の指定通所介護の前後に連続して延長サービス"))) {
        errors.push("notice personnel staffing: H30 extended-hours wording missing");
      }
      if (compact.includes(normalizedNeedle("②７時間以上９時間未満の通所介護の前後に連続して延長サービス"))) {
        errors.push("notice personnel staffing: pre-H30 extended-hours wording returned");
      }
      for (const phrase of [
        "ア指定通所介護事業所の従業者により確保する場合",
        "イ病院、診療所、訪問看護ステーションとの連携により確保する場合",
        "サービス担当者会議や地域ケア会議に出席するための時間",
      ]) {
        if (!compact.includes(phrase.normalize("NFKC").replace(/\s+/g, ""))) {
          errors.push(`notice personnel staffing: verified wording missing: ${phrase}`);
        }
      }
      const patches = staffing.patch_snapshot_ids || [];
      for (const patchId of [
        "dayservice-personnel-staffing-h30-hours-patch",
        "dayservice-personnel-staffing-r3-nurse-patch",
      ]) {
        if (!patches.includes(patchId)) errors.push(`notice personnel staffing: missing patch ${patchId}`);
      }
    }

    const lifeCounselor = candidateById.get("notice.dayservice.personnel.life-counselor");
    if (lifeCounselor && !String(lifeCounselor.candidate_text).includes("特別養護老人ホームの設備及び運営に関する基準")) {
      errors.push("notice personnel life-counselor: verified qualification reference missing");
    }

    const functionTraining = candidateById.get("notice.dayservice.personnel.function-training");
    if (functionTraining) {
      const compact = String(functionTraining.candidate_text || "").normalize("NFKC").replace(/\s+/g, "");
      for (const phrase of ["はり師又はきゅう師", "6月以上機能訓練指導に従事した経験"]) {
        if (!compact.includes(phrase.normalize("NFKC").replace(/\s+/g, ""))) {
          errors.push(`notice personnel function-training: H30 wording missing: ${phrase}`);
        }
      }
    }

    const manager = candidateById.get("notice.dayservice.personnel.manager");
    if (manager && !String(manager.candidate_text).normalize("NFKC").replace(/\s+/g, "").includes("第三の一の1の(3)を参照されたい")) {
      errors.push("notice personnel manager: verified cross-reference missing");
    }
  }

  const requiredRouki25OperationModernIds = [
    "notice.dayservice.operation.bcp",
    "notice.dayservice.operation.disaster",
    "notice.dayservice.operation.hygiene",
    "notice.dayservice.operation.community",
    "notice.dayservice.operation.accident",
    "notice.dayservice.operation.abuse",
    "notice.dayservice.operation.records",
    "notice.dayservice.operation.incorporation",
  ];
  for (const id of requiredRouki25OperationModernIds) {
    if (!noticeSkeletonIds.has(id)) {
      errors.push(`notice skeleton: missing required modern operation node ${id}`);
    }
  }

  const r6HygieneTransitionExpiry = noticeAmendments.find(
    (event) => event.id === "rouki25.r6.dayservice.hygiene-transition-expiry"
  );
  if (!r6HygieneTransitionExpiry ||
      r6HygieneTransitionExpiry.operation !== "delete_expired_transition_fragment" ||
      r6HygieneTransitionExpiry.target_node_id !== "notice.dayservice.operation.hygiene") {
    errors.push("notice amendment events: missing R6 hygiene transition-expiry event");
  }

  const operationModernPipelineParts = [
    noticeOperationModernManifest,
    noticeOperationModernSnapshots,
    noticeOperationModernAssembly,
    noticeOperationModernReplay,
    noticeOperationModernCandidates,
  ];
  if (operationModernPipelineParts.some(Boolean) && !operationModernPipelineParts.every(Boolean)) {
    errors.push("notice operation-modern reconstruction: incomplete pipeline files");
  }
  if (operationModernPipelineParts.every(Boolean)) {
    const expectedOperationModernIds = new Set(requiredRouki25OperationModernIds);
    const sameOperationModernIdSet = (values) => {
      const actual = new Set(values);
      return actual.size === expectedOperationModernIds.size &&
        [...expectedOperationModernIds].every((id) => actual.has(id));
    };

    const manifestSegments = noticeOperationModernManifest.segments || [];
    if (!sameOperationModernIdSet(manifestSegments.map((segment) => segment.notice_id))) {
      errors.push("notice operation-modern manifest: unexpected operation coverage");
    }
    const manifestSegmentIds = new Set();
    for (const segment of manifestSegments) {
      if (manifestSegmentIds.has(segment.id)) {
        errors.push(`notice operation-modern manifest: duplicate segment ${segment.id}`);
      }
      manifestSegmentIds.add(segment.id);
      if (!sourceIds.has(segment.source_id)) {
        errors.push(`notice operation-modern manifest ${segment.id}: missing source ${segment.source_id}`);
      }
      if (!segment.body_start || !segment.body_end || !segment.page_start || !segment.page_end) {
        errors.push(`notice operation-modern manifest ${segment.id}: incomplete extraction boundary`);
      }
    }

    const snapshots = noticeOperationModernSnapshots.segments || [];
    const snapshotById = new Map(snapshots.map((item) => [item.id, item]));
    if (!sameOperationModernIdSet(snapshots.map((item) => item.notice_id))) {
      errors.push("notice operation-modern snapshots: unexpected operation coverage");
    }
    for (const snapshot of snapshots) {
      if (!sourceIds.has(snapshot.source_id)) {
        errors.push(`notice operation-modern snapshot ${snapshot.id}: missing source ${snapshot.source_id}`);
      }
      if (snapshot.verification_status !== "IMPORTED_OFFICIAL_PDF_NEEDS_HUMAN_CHECK") {
        errors.push(`notice operation-modern snapshot ${snapshot.id}: unsafe verification status`);
      }
      if (!snapshot.body_text || !snapshot.body_text_sha256 ||
          createHash("sha256").update(snapshot.body_text, "utf8").digest("hex") !== snapshot.body_text_sha256) {
        errors.push(`notice operation-modern snapshot ${snapshot.id}: body text/hash mismatch`);
      }
    }

    if (!sameOperationModernIdSet((noticeOperationModernAssembly.items || []).map((item) => item.notice_id))) {
      errors.push("notice operation-modern assembly: unexpected operation coverage");
    }

    const replayById = new Map((noticeOperationModernReplay || []).map((item) => [item.notice_id, item]));
    if (!sameOperationModernIdSet((noticeOperationModernReplay || []).map((item) => item.notice_id))) {
      errors.push("notice operation-modern replay: unexpected operation coverage");
    }
    for (const coverage of noticeOperationModernReplay || []) {
      if (coverage.human_verification_status !== "NOT_REVIEWED") {
        errors.push(`notice operation-modern replay ${coverage.notice_id}: unexpected human verification status`);
      }
      for (const checkpoint of coverage.checkpoints || []) {
        if (!sourceIds.has(checkpoint.source_id)) {
          errors.push(`notice operation-modern replay ${coverage.notice_id}: missing checkpoint source ${checkpoint.source_id}`);
        }
        if (checkpoint.status !== "CHECKED") {
          errors.push(`notice operation-modern replay ${coverage.notice_id}: unchecked checkpoint ${checkpoint.source_id}`);
        }
      }
    }

    const candidates = noticeOperationModernCandidates.items || [];
    if (!sameOperationModernIdSet(candidates.map((item) => item.notice_id))) {
      errors.push("notice operation-modern candidates: unexpected operation coverage");
    }
    const candidateById = new Map(candidates.map((item) => [item.notice_id, item]));
    for (const candidate of candidates) {
      if (candidate.reconstruction_status !== "MACHINE_RECONSTRUCTED_NEEDS_HUMAN_CHECK" ||
          candidate.human_verification_status !== "NOT_REVIEWED") {
        errors.push(`notice operation-modern candidate ${candidate.notice_id}: unsafe status`);
      }
      if (!candidate.candidate_text || !candidate.candidate_text_sha256 ||
          createHash("sha256").update(candidate.candidate_text, "utf8").digest("hex") !== candidate.candidate_text_sha256) {
        errors.push(`notice operation-modern candidate ${candidate.notice_id}: text/hash mismatch`);
      }
      const baseline = snapshotById.get(candidate.baseline_snapshot_id);
      if (!baseline || baseline.notice_id !== candidate.notice_id) {
        errors.push(`notice operation-modern candidate ${candidate.notice_id}: baseline snapshot mismatch`);
      }
      for (const patchId of candidate.patch_snapshot_ids || []) {
        const patch = snapshotById.get(patchId);
        if (!patch || patch.notice_id !== candidate.notice_id) {
          errors.push(`notice operation-modern candidate ${candidate.notice_id}: patch snapshot mismatch ${patchId}`);
        }
      }
      const coverage = replayById.get(candidate.notice_id);
      if (!coverage || candidate.replay_status !== coverage.replay_status) {
        errors.push(`notice operation-modern candidate ${candidate.notice_id}: replay coverage mismatch`);
      }
    }

    const compact = (value) => String(value || "").normalize("NFKC").replace(/\s+/g, "");
    const requireOperationText = (id, phrase, label) => {
      const item = candidateById.get(id);
      if (!item || !compact(item.candidate_text).includes(compact(phrase))) {
        errors.push(`notice operation-modern candidate ${id}: ${label}`);
      }
    };
    const forbidOperationText = (id, phrase, label) => {
      const item = candidateById.get(id);
      if (item && compact(item.candidate_text).includes(compact(phrase))) {
        errors.push(`notice operation-modern candidate ${id}: ${label}`);
      }
    };

    for (const phrase of [
      "介護施設・事業所における感染症発生時の業務継続ガイドライン",
      "一体的に策定することとして差し支えない",
      "定期的（年１回以上）な教育",
      "訓練（シミュレーション）",
    ]) {
      requireOperationText("notice.dayservice.operation.bcp", phrase, `verified BCP wording missing: ${phrase}`);
    }
    forbidOperationText(
      "notice.dayservice.operation.bcp",
      "令和６年３月31日までの間は、努力義務",
      "expired R3 BCP transition wording returned"
    );
    forbidOperationText(
      "notice.dayservice.operation.bcp",
      "新型コロナウイルス感染症発生時",
      "pre-R6 BCP guideline title returned"
    );

    requireOperationText(
      "notice.dayservice.operation.disaster",
      "できるだけ地域住民の参加が得られるよう努める",
      "R3 disaster regional-participation wording missing"
    );

    for (const phrase of [
      "感染症の予防及びまん延の防止のための対策を検討する委員会",
      "定期的な教育（年１回以上）",
      "訓練（シミュレーション）を定期的（年１回以上）",
    ]) {
      requireOperationText("notice.dayservice.operation.hygiene", phrase, `verified hygiene wording missing: ${phrase}`);
    }
    forbidOperationText(
      "notice.dayservice.operation.hygiene",
      "令和６年３月31日までの間は、努力義務",
      "expired R3 hygiene transition wording returned"
    );

    requireOperationText(
      "notice.dayservice.operation.community",
      "地域の住民やボランティア団体等との連携及び協力",
      "community linkage wording missing"
    );
    requireOperationText(
      "notice.dayservice.operation.community",
      "介護サービス相談員を派遣する事業",
      "community consultation-program wording missing"
    );
    requireOperationText(
      "notice.dayservice.operation.accident",
      "事故の状況及び事故に際して採った処置についての記録は、２年間保存",
      "accident record-retention wording missing"
    );
    requireOperationText(
      "notice.dayservice.operation.abuse",
      "居宅基準第37条の２",
      "abuse prevention cross-reference missing"
    );
    requireOperationText(
      "notice.dayservice.operation.records",
      "一連のサービス提供が終了した日",
      "records completion-date definition missing"
    );
    requireOperationText(
      "notice.dayservice.operation.incorporation",
      "ウェブサイトへの掲載に関する取扱い",
      "R6 website-publication wording missing"
    );
    const incorporation = candidateById.get("notice.dayservice.operation.incorporation");
    if (incorporation && incorporation.baseline_snapshot_id !== "dayservice-operation-incorporation-2026") {
      errors.push("notice operation-modern incorporation: current 2026 MHLW reference is not the baseline snapshot");
    }
  }

  const requiredRouki25OperationLegacyIds = [
    "notice.dayservice.operation.fees",
    "notice.dayservice.operation.policy",
    "notice.dayservice.operation.plan",
    "notice.dayservice.operation.rules",
    "notice.dayservice.operation.staffing",
  ];
  for (const id of requiredRouki25OperationLegacyIds) {
    if (!noticeSkeletonIds.has(id)) {
      errors.push(`notice skeleton: missing required legacy operation node ${id}`);
    }
  }

  const requiredLegacyEvents = [
    ["rouki25.h30.dayservice.plan-record-reference", "notice.dayservice.operation.plan"],
    ["rouki25.h30.dayservice.rules-extended-hours", "notice.dayservice.operation.rules"],
    ["rouki25.r3.dayservice.fees-reference", "notice.dayservice.operation.fees"],
    ["rouki25.r3.dayservice.plan-references", "notice.dayservice.operation.plan"],
    ["rouki25.r3.dayservice.rules-references", "notice.dayservice.operation.rules"],
    ["rouki25.r3.dayservice.staffing-additions", "notice.dayservice.operation.staffing"],
    ["rouki25.r6.dayservice.physical-restraint", "notice.dayservice.operation.policy"],
  ];
  for (const [eventId, targetId] of requiredLegacyEvents) {
    const event = noticeAmendments.find((entry) => entry.id === eventId);
    if (!event || event.target_node_id !== targetId) {
      errors.push(`notice amendment events: missing or mis-targeted ${eventId}`);
    }
  }

  const operationLegacyPipelineParts = [
    noticeOperationLegacyManifest,
    noticeOperationLegacySnapshots,
    noticeOperationLegacyAssembly,
    noticeOperationLegacyReplay,
    noticeOperationLegacyCandidates,
  ];
  if (operationLegacyPipelineParts.some(Boolean) && !operationLegacyPipelineParts.every(Boolean)) {
    errors.push("notice operation-legacy reconstruction: incomplete pipeline files");
  }
  if (operationLegacyPipelineParts.every(Boolean)) {
    const expectedLegacyIds = new Set(requiredRouki25OperationLegacyIds);
    const sameLegacyIdSet = (values) => {
      const actual = new Set(values);
      return actual.size === expectedLegacyIds.size &&
        [...expectedLegacyIds].every((id) => actual.has(id));
    };

    const manifestSegments = noticeOperationLegacyManifest.segments || [];
    if (!sameLegacyIdSet(manifestSegments.map((segment) => segment.notice_id))) {
      errors.push("notice operation-legacy manifest: unexpected operation coverage");
    }
    const manifestSegmentIds = new Set();
    for (const segment of manifestSegments) {
      if (manifestSegmentIds.has(segment.id)) {
        errors.push(`notice operation-legacy manifest: duplicate segment ${segment.id}`);
      }
      manifestSegmentIds.add(segment.id);
      if (!sourceIds.has(segment.source_id)) {
        errors.push(`notice operation-legacy manifest ${segment.id}: missing source ${segment.source_id}`);
      }
      if (!segment.body_start || !segment.body_end || !segment.page_start || !segment.page_end) {
        errors.push(`notice operation-legacy manifest ${segment.id}: incomplete extraction boundary`);
      }
      for (const replacement of segment.layout_replacements || []) {
        if (!replacement.from || !replacement.to || !replacement.reason) {
          errors.push(`notice operation-legacy manifest ${segment.id}: incomplete layout replacement declaration`);
        }
      }
    }

    const snapshots = noticeOperationLegacySnapshots.segments || [];
    const snapshotById = new Map(snapshots.map((item) => [item.id, item]));
    if (!sameLegacyIdSet(snapshots.map((item) => item.notice_id))) {
      errors.push("notice operation-legacy snapshots: unexpected operation coverage");
    }
    for (const snapshot of snapshots) {
      if (!sourceIds.has(snapshot.source_id)) {
        errors.push(`notice operation-legacy snapshot ${snapshot.id}: missing source ${snapshot.source_id}`);
      }
      if (snapshot.verification_status !== "IMPORTED_OFFICIAL_PDF_NEEDS_HUMAN_CHECK") {
        errors.push(`notice operation-legacy snapshot ${snapshot.id}: unsafe verification status`);
      }
      if (!snapshot.body_text || !snapshot.body_text_sha256 ||
          createHash("sha256").update(snapshot.body_text, "utf8").digest("hex") !== snapshot.body_text_sha256) {
        errors.push(`notice operation-legacy snapshot ${snapshot.id}: body text/hash mismatch`);
      }
      if ((snapshot.body_text || "").includes("事業。所") || (snapshot.body_text || "").includes("置かれ、ている")) {
        errors.push(`notice operation-legacy snapshot ${snapshot.id}: known PDF layout artifact returned`);
      }
    }

    if (!sameLegacyIdSet((noticeOperationLegacyAssembly.items || []).map((item) => item.notice_id))) {
      errors.push("notice operation-legacy assembly: unexpected operation coverage");
    }

    const replayById = new Map((noticeOperationLegacyReplay || []).map((item) => [item.notice_id, item]));
    if (!sameLegacyIdSet((noticeOperationLegacyReplay || []).map((item) => item.notice_id))) {
      errors.push("notice operation-legacy replay: unexpected operation coverage");
    }
    for (const coverage of noticeOperationLegacyReplay || []) {
      if (coverage.human_verification_status !== "NOT_REVIEWED") {
        errors.push(`notice operation-legacy replay ${coverage.notice_id}: unexpected human verification status`);
      }
      for (const checkpoint of coverage.checkpoints || []) {
        if (!sourceIds.has(checkpoint.source_id)) {
          errors.push(`notice operation-legacy replay ${coverage.notice_id}: missing checkpoint source ${checkpoint.source_id}`);
        }
        if (checkpoint.status !== "CHECKED") {
          errors.push(`notice operation-legacy replay ${coverage.notice_id}: unchecked checkpoint ${checkpoint.source_id}`);
        }
      }
    }

    const candidates = noticeOperationLegacyCandidates.items || [];
    if (!sameLegacyIdSet(candidates.map((item) => item.notice_id))) {
      errors.push("notice operation-legacy candidates: unexpected operation coverage");
    }
    const candidateById = new Map(candidates.map((item) => [item.notice_id, item]));
    for (const candidate of candidates) {
      if (candidate.reconstruction_status !== "MACHINE_RECONSTRUCTED_NEEDS_HUMAN_CHECK" ||
          candidate.human_verification_status !== "NOT_REVIEWED") {
        errors.push(`notice operation-legacy candidate ${candidate.notice_id}: unsafe status`);
      }
      if (!candidate.candidate_text || !candidate.candidate_text_sha256 ||
          createHash("sha256").update(candidate.candidate_text, "utf8").digest("hex") !== candidate.candidate_text_sha256) {
        errors.push(`notice operation-legacy candidate ${candidate.notice_id}: text/hash mismatch`);
      }
      const baseline = snapshotById.get(candidate.baseline_snapshot_id);
      if (!baseline || baseline.notice_id !== candidate.notice_id) {
        errors.push(`notice operation-legacy candidate ${candidate.notice_id}: baseline snapshot mismatch`);
      }
      for (const patchId of candidate.patch_snapshot_ids || []) {
        const patch = snapshotById.get(patchId);
        if (!patch || patch.notice_id !== candidate.notice_id) {
          errors.push(`notice operation-legacy candidate ${candidate.notice_id}: patch snapshot mismatch ${patchId}`);
        }
      }
      const coverage = replayById.get(candidate.notice_id);
      if (!coverage || coverage.replay_status !== candidate.replay_status) {
        errors.push(`notice operation-legacy candidate ${candidate.notice_id}: replay coverage mismatch`);
      }
    }

    const compact = (value) => String(value || "").normalize("NFKC").replace(/\s+/g, "");
    const requireLegacyText = (id, phrase, label) => {
      const item = candidateById.get(id);
      if (!item || !compact(item.candidate_text).includes(compact(phrase))) {
        errors.push(`notice operation-legacy candidate ${id}: ${label}`);
      }
    };
    const forbidLegacyText = (id, phrase, label) => {
      const item = candidateById.get(id);
      if (item && compact(item.candidate_text).includes(compact(phrase))) {
        errors.push(`notice operation-legacy candidate ${id}: ${label}`);
      }
    };

    requireLegacyText("notice.dayservice.operation.fees", "第３の一の３の⑾の①、②及び④", "R3 current reference target missing");
    requireLegacyText("notice.dayservice.operation.fees", "ハ食事の提供に要する費用", "H27 fee item wording missing");
    forbidLegacyText("notice.dayservice.operation.fees", "第三の一の３の⑽の①、②及び④", "pre-R3 cross-reference returned");

    for (const phrase of [
      "③指定通所介護の提供に当たっては",
      "身体的拘束等を行ってはならず",
      "切迫性、非代替性及び一時性",
      "当該記録は、２年間保存しなければならない",
      "④認知症の状態にある要介護者",
      "⑤指定通所介護は、事業所内でサービスを提供することが原則",
    ]) {
      requireLegacyText("notice.dayservice.operation.policy", phrase, `R6 policy wording/order missing: ${phrase}`);
    }
    forbidLegacyText("notice.dayservice.operation.policy", "事業。所", "PDF layout artifact returned");

    requireLegacyText("notice.dayservice.operation.plan", "居宅基準第104条の４第２項", "R3 record-retention reference missing");
    requireLegacyText("notice.dayservice.operation.plan", "第３の一の３の⒁の⑥を準用する", "R3 visit-care reference missing");
    forbidLegacyText("notice.dayservice.operation.plan", "居宅基準第104条の２第２項", "pre-H30 record reference returned");
    forbidLegacyText("notice.dayservice.operation.plan", "居宅基準第104条の３第２項", "H30-only record reference returned");
    forbidLegacyText("notice.dayservice.operation.plan", "第三の一の３の⒀の⑥", "pre-R3 visit-care reference returned");
    forbidLegacyText("notice.dayservice.operation.plan", "置かれ、ている", "PDF layout artifact returned");

    requireLegacyText("notice.dayservice.operation.rules", "同条第１号から第11号まで", "R3 rule-number range missing");
    requireLegacyText("notice.dayservice.operation.rules", "８時間以上９時間未満の指定通所介護", "H30 extended-hours wording missing");
    requireLegacyText("notice.dayservice.operation.rules", "⑺の非常災害に関する具体的計画", "R3 disaster-reference update missing");
    forbidLegacyText("notice.dayservice.operation.rules", "７時間以上９時間未満の通所介護", "pre-H30 extended-hours wording returned");
    forbidLegacyText("notice.dayservice.operation.rules", "同条第１号から第10号まで", "pre-R3 rule-number range returned");
    forbidLegacyText("notice.dayservice.operation.rules", "⑹の非常災害に関する具体的計画", "pre-R3 disaster reference returned");

    for (const phrase of [
      "原則として月ごとの勤務表を作成",
      "機能訓練指導員の配置",
      "居宅基準第53条の２第３項",
      "居宅基準第30条第４項",
    ]) {
      requireLegacyText("notice.dayservice.operation.staffing", phrase, `staffing wording missing: ${phrase}`);
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
