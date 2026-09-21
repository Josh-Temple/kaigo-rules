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
const qa = read("qa-items.json");\nconst qaCorpusPath = path.join(root, "data", "qa-corpus.json");\nconst qaCorpus = fs.existsSync(qaCorpusPath) ? JSON.parse(fs.readFileSync(qaCorpusPath, "utf8")) : [];

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
unique(qa, "id", "qa");\nunique(qaCorpus, "id", "qa-corpus");

const sourceIds = new Set(sources.map(x => x.id));
const ruleIds = new Set(rules.map(x => x.id));
const noticeIds = new Set(notices.map(x => x.id));
const qaIds = new Set(qa.map(x => x.id));

for (const q of questions) {
  if (q.status === "verified") {
    for (const field of ["last_verified", "short_answer", "practical_steps", "cautions"]) {
      if (!q[field] || (Array.isArray(q[field]) && q[field].length === 0)) errors.push(`question ${q.slug}: verified but missing ${field}`);
    }
  }
  for (const id of q.rule_node_ids || []) if (!ruleIds.has(id)) errors.push(`question ${q.slug}: missing rule ${id}`);
  for (const id of q.notice_node_ids || []) if (!noticeIds.has(id)) errors.push(`question ${q.slug}: missing notice ${id}`);
  for (const id of q.qa_item_ids || []) if (!qaIds.has(id)) errors.push(`question ${q.slug}: missing Q&A ${id}`);
  for (const ref of q.source_refs || []) if (!sourceIds.has(ref.source_id)) errors.push(`question ${q.slug}: missing source ${ref.source_id}`);
}
for (const r of rules) {
  if (!sourceIds.has(r.source_id)) errors.push(`rule ${r.id}: missing source ${r.source_id}`);
  if (r.verification_status === "VERIFIED_CURRENT" && !r.official_text) errors.push(`rule ${r.id}: VERIFIED_CURRENT without text`);
}
for (const n of notices) for (const id of n.source_ids || []) if (!sourceIds.has(id)) errors.push(`notice ${n.id}: missing source ${id}`);
for (const item of qa) if (!sourceIds.has(item.source_id)) errors.push(`Q&A ${item.id}: missing source ${item.source_id}`);\nfor (const item of qaCorpus) {\n  if (!sourceIds.has(item.source_id)) errors.push(`Q&A corpus ${item.id}: missing source ${item.source_id}`);\n  for (const field of ["service_code", "standard_code", "question", "answer", "ingestion_status"]) {\n    if (!item[field]) errors.push(`Q&A corpus ${item.id || "(missing id)"}: missing ${field}`);\n  }\n  if (!["01", "02", "06", "16"].includes(item.service_code)) errors.push(`Q&A corpus ${item.id}: unexpected service_code ${item.service_code}`);\n}

if (errors.length) {
  console.error(errors.join("\n"));
  process.exit(1);
}
console.log(`Data validation PASS: ${questions.length} questions, ${rules.length} rules, ${notices.length} notice nodes, ${qa.length} curated Q&A items, ${qaCorpus.length} imported Q&A rows, ${sources.length} sources.`);
