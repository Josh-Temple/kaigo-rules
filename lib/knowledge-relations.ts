import careRelationsData from "../data/care-insurance-act-relations.json";
import feeGuidanceRelationsData from "../data/fee-guidance-relations.json";
import noticeRelationsData from "../data/notice-ordinance-relations.json";
import ordinanceRelationsData from "../data/ordinance37-relations.json";
import questionRelationsData from "../data/relationships.json";
import remunerationDelegatedRelationsData from "../data/remuneration-delegated-relations.json";
import remunerationRelationsData from "../data/remuneration-relations.json";

import explicitAuditData from "../data/relation-semantic-independent-audit.json";
import careActAuditData from "../data/careact-internal-relation-independent-audit.json";
import crossLayerAuditData from "../data/cross-layer-source-chain-independent-audit.json";
import remunerationAuditData from "../data/remuneration-delegation-relation-independent-audit.json";
import registryData from "../data/verification-registry.json";

export type KnowledgeEdge = {
  source_id: string;
  relation: string;
  target_id: string;
  source_file: string;
  declared_status: string | null;
  independent_verification:
    | { status: "PASS"; lane: string }
    | { status: "NOT_AUDITED"; lane: null };
};

type RawRelation = Record<string, unknown>;
type Identity = string;

const FROM_KEYS = [
  "from",
  "from_id",
  "from_guidance_id",
  "from_notice_id",
  "from_fee_id",
] as const;

const TO_KEYS = [
  "to",
  "to_id",
  "to_fee_id",
  "to_ordinance_id",
  "to_source_id",
] as const;

const relationSources: Array<[string, RawRelation[]]> = [
  ["data/care-insurance-act-relations.json", careRelationsData as RawRelation[]],
  ["data/fee-guidance-relations.json", feeGuidanceRelationsData as RawRelation[]],
  ["data/notice-ordinance-relations.json", noticeRelationsData as RawRelation[]],
  ["data/ordinance37-relations.json", ordinanceRelationsData as RawRelation[]],
  ["data/relationships.json", questionRelationsData as RawRelation[]],
  ["data/remuneration-delegated-relations.json", remunerationDelegatedRelationsData as RawRelation[]],
  ["data/remuneration-relations.json", remunerationRelationsData as RawRelation[]],
];

const firstString = (row: RawRelation, keys: readonly string[]) => {
  for (const key of keys) {
    const value = row[key];
    if (typeof value === "string" && value) return value;
  }
  return null;
};

const identity = (source: string, relation: string, target: string): Identity =>
  `${source}\u001f${relation}\u001f${target}`;

const verifiedOwners = new Map<Identity, string>();

const addVerified = (source: string, relation: string, target: string, lane: string) => {
  const key = identity(source, relation, target);
  const previous = verifiedOwners.get(key);
  if (previous && previous !== lane) {
    throw new Error(`Knowledge relation audit overlap: ${source} | ${relation} | ${target}`);
  }
  verifiedOwners.set(key, lane);
};

const explicitAudit = explicitAuditData as any;
for (const check of explicitAudit.checks || []) {
  if (check.result !== "PASS" || (check.differences || []).length) continue;
  for (const target of check.expected_relation_targets || []) {
    addVerified(
      check.source_article_id,
      check.relation,
      `ordinance37.article.${target}`,
      "explicit-legal-reference"
    );
  }
}

const careActAudit = careActAuditData as any;
for (const check of careActAudit.checks || []) {
  if (check.result !== "PASS" || (check.differences || []).length) continue;
  addVerified(check.source_article_id, check.relation, check.target_id, "careact-internal");
}

const crossLayerAudit = crossLayerAuditData as any;
for (const check of crossLayerAudit.checks || []) {
  if (check.result !== "PASS" || (check.differences || []).length) continue;
  if (check.target_id) {
    addVerified(check.source_id, check.relation, check.target_id, "cross-layer-source-chain");
  } else if (check.target_layer === "ordinance37") {
    for (const target of check.committed_relation_targets || []) {
      addVerified(
        check.source_id,
        check.relation,
        `ordinance37.article.${target}`,
        "cross-layer-source-chain"
      );
    }
  }
}

const remunerationAudit = remunerationAuditData as any;
for (const check of remunerationAudit.checks || []) {
  if (check.result !== "PASS" || (check.differences || []).length) continue;
  addVerified(check.from_id, check.relation, check.to_id, "remuneration-delegation");
}

const edges: KnowledgeEdge[] = [];
const seen = new Set<Identity>();

for (const [sourceFile, rows] of relationSources) {
  for (const row of rows) {
    const relation = typeof row.relation === "string" ? row.relation : null;
    if (!relation || relation === "contains") continue;

    const source = firstString(row, FROM_KEYS);
    const target = firstString(row, TO_KEYS);
    if (!source || !target) {
      throw new Error(`Incomplete relation in ${sourceFile}`);
    }

    const key = identity(source, relation, target);
    if (seen.has(key)) {
      throw new Error(`Duplicate knowledge relation: ${source} | ${relation} | ${target}`);
    }
    seen.add(key);

    const lane = verifiedOwners.get(key);
    const declared =
      typeof row.verification_status === "string"
        ? row.verification_status
        : typeof row.status === "string"
          ? row.status
          : null;

    edges.push({
      source_id: source,
      relation,
      target_id: target,
      source_file: sourceFile,
      declared_status: declared,
      independent_verification: lane
        ? { status: "PASS", lane }
        : { status: "NOT_AUDITED", lane: null },
    });
  }
}

const summary = (registryData as any).summary || {};
const expectedTotal = Number(summary.semantic_or_cross_layer_relations_total);
const expectedVerified = Number(summary.semantic_or_cross_layer_relations_independently_verified);
const actualVerified = edges.filter(
  (edge) => edge.independent_verification.status === "PASS"
).length;

if (edges.length !== expectedTotal || actualVerified !== expectedVerified) {
  throw new Error(
    `Knowledge relation coverage drift: edges=${edges.length}/${expectedTotal}, verified=${actualVerified}/${expectedVerified}`
  );
}

export const knowledgeEdges = edges;

export function edgesTouching(targetPrefix: string) {
  return knowledgeEdges.filter(
    (edge) =>
      edge.source_id === targetPrefix ||
      edge.source_id.startsWith(`${targetPrefix}.`) ||
      edge.target_id === targetPrefix ||
      edge.target_id.startsWith(`${targetPrefix}.`)
  );
}

export function incomingEdges(targetPrefix: string) {
  return knowledgeEdges.filter(
    (edge) =>
      edge.target_id === targetPrefix ||
      edge.target_id.startsWith(`${targetPrefix}.`)
  );
}
