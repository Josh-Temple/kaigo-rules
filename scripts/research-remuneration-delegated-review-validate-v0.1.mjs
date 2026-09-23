import fs from "node:fs";
import path from "node:path";

const root = process.cwd();
const readJson = (relative) =>
  JSON.parse(fs.readFileSync(path.join(root, relative), "utf8"));

const review = readJson("data/remuneration-review.json");
const meta = readJson("data/remuneration-delegated-meta.json");
const nodes = readJson("data/remuneration-delegated-nodes.json");

const errors = [];
const delegated = review.delegated_review;
if (!delegated || delegated.status !== "COMPLETE") {
  errors.push("delegated_review is not COMPLETE");
}

const expectedSources = {
  "mhlw-fee-notice27-base": meta.sources.notice27,
  "mhlw-fee-criteria95-current": meta.sources.notice95,
};

for (const [sourceId, sourceMeta] of Object.entries(expectedSources)) {
  const sourceReview = delegated?.sources?.[sourceId];
  if (!sourceReview || sourceReview.status !== "COMPLETE") {
    errors.push("source review incomplete: " + sourceId);
    continue;
  }
  if (sourceReview.source_url !== sourceMeta.url) {
    errors.push("source URL mismatch: " + sourceId);
  }
  if (sourceReview.source_sha256 !== sourceMeta.sha256) {
    errors.push("source SHA mismatch: " + sourceId);
  }

  const current = nodes.filter((x) => x.source_id === sourceId);
  const reviewed = new Map(
    (sourceReview.reviewed_nodes ?? []).map((x) => [x.id, x.text_sha256]),
  );

  if (reviewed.size !== current.length) {
    errors.push("reviewed node count mismatch: " + sourceId);
  }
  for (const node of current) {
    if (!reviewed.has(node.id)) {
      errors.push("unreviewed delegated node: " + node.id);
    } else if (reviewed.get(node.id) !== node.text_sha256) {
      errors.push("delegated text drift: " + node.id);
    }
  }
}

if (nodes.length !== meta.counts.nodes || nodes.length !== 17) {
  errors.push("delegated node total mismatch");
}
if (nodes.filter((x) => x.source_id === "mhlw-fee-notice27-base").length !== 3) {
  errors.push("notice27 node count mismatch");
}
if (nodes.filter((x) => x.source_id === "mhlw-fee-criteria95-current").length !== 14) {
  errors.push("notice95 node count mismatch");
}

console.log(JSON.stringify({
  delegated_review_status: delegated?.status ?? null,
  delegated_nodes: nodes.length,
  notice27_nodes: nodes.filter((x) => x.source_id === "mhlw-fee-notice27-base").length,
  notice95_nodes: nodes.filter((x) => x.source_id === "mhlw-fee-criteria95-current").length,
  errors,
  valid: errors.length === 0
}, null, 2));

if (errors.length > 0) process.exitCode = 1;
