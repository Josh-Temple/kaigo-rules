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
}

if (errors.length) {
  console.error(errors.join("\n"));
  process.exit(1);
}

console.log(
  `Data validation PASS: ${questions.length} questions, ${rules.length} rules, ${notices.length} notice nodes, ${qa.length} curated Q&A items, ${qaCorpus.length} imported Q&A rows, ${(qaCandidates.candidates || []).reduce((n, g) => n + (g.candidates || []).length, 0)} review-only Q&A candidates, ${ordinanceNodes.length} ordinance nodes, ${sources.length} sources.`
);
