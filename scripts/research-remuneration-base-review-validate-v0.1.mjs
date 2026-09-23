import fs from "node:fs";
import path from "node:path";

const root = process.cwd();
const readJson = (relative) =>
  JSON.parse(fs.readFileSync(path.join(root, relative), "utf8"));

const review = readJson("data/remuneration-review.json");
const textMeta = readJson("data/remuneration-current-text-meta.json");
const textRows = readJson("data/remuneration-current-text.json");

const errors = [];
if (review.review_status !== "IN_PROGRESS") errors.push("overall review must remain IN_PROGRESS");
if (review.base_notice_review?.status !== "COMPLETE") errors.push("base review is not COMPLETE");
if (review.base_notice_review?.source_id !== textMeta.source_id) errors.push("source_id mismatch");
if (review.base_notice_review?.source_sha256 !== textMeta.source_sha256) errors.push("source SHA mismatch");
if (textRows.length !== textMeta.record_count || textRows.length !== 29) errors.push("record count mismatch");

const reviewed = new Map(
  (review.base_notice_review?.reviewed_nodes ?? []).map((x) => [x.fee_id, x.text_sha256]),
);
if (reviewed.size !== textRows.length) errors.push("reviewed node count mismatch");
for (const row of textRows) {
  if (!reviewed.has(row.fee_id)) errors.push("unreviewed: " + row.fee_id);
  else if (reviewed.get(row.fee_id) !== row.text_sha256) errors.push("text drift: " + row.fee_id);
}

console.log(JSON.stringify({
  review_status: review.review_status,
  base_notice_review_status: review.base_notice_review?.status ?? null,
  base_nodes: textRows.length,
  errors,
  valid: errors.length === 0
}, null, 2));

if (errors.length > 0) process.exitCode = 1;
