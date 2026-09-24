import fs from "node:fs";
import path from "node:path";

const root = process.cwd();
const readJson = (relative) =>
  JSON.parse(fs.readFileSync(path.join(root, relative), "utf8"));

const review = readJson("data/unit-price-review.json");
const rates = readJson("data/unit-price-dayservice.json");
const rateMeta = readJson("data/unit-price-dayservice-meta.json");
const assignments = readJson("data/unit-price-region-assignments.json");
const assignmentMeta = readJson("data/unit-price-region-assignments-meta.json");

const errors = [];
const sameArray = (a, b) =>
  Array.isArray(a) &&
  Array.isArray(b) &&
  a.length === b.length &&
  a.every((v, i) => v === b[i]);

const sameSet = (a, b) => {
  if (!Array.isArray(a) || !Array.isArray(b)) return false;
  const aa = [...new Set(a)].sort();
  const bb = [...new Set(b)].sort();
  return aa.length === bb.length && aa.every((v, i) => v === bb[i]);
};

if (review.review_status !== "COMPLETE") {
  errors.push("unit-price review_status is not COMPLETE");
}
if (review.source_id !== rateMeta.source_id || review.source_id !== assignmentMeta.source_id) {
  errors.push("source_id mismatch");
}
if (!sameArray(review.source_sha256, rateMeta.source_sha256)) {
  errors.push("rate source_sha256 mismatch");
}
if (!sameArray(review.assignment_source_sha256, assignmentMeta.source_sha256)) {
  errors.push("assignment source_sha256 mismatch");
}
if (!sameSet(review.reviewed_rate_ids, rates.map((x) => x.id))) {
  errors.push("reviewed_rate_ids do not exactly cover current rates");
}
if (!sameSet(review.reviewed_assignment_ids, assignments.map((x) => x.id))) {
  errors.push("reviewed_assignment_ids do not exactly cover current assignments");
}
if (review.reviewed_default_rule !== true || assignmentMeta.default_rule_present !== true) {
  errors.push("default rule is not reviewed/present");
}
if (rates.length !== rateMeta.rate_count || rates.length !== 8) {
  errors.push(`rate count mismatch: data=${rates.length} meta=${rateMeta.rate_count}`);
}
if (assignments.length !== assignmentMeta.explicit_assignment_count) {
  errors.push(
    `assignment count mismatch: data=${assignments.length} meta=${assignmentMeta.explicit_assignment_count}`,
  );
}

const rateIds = new Set(rates.map((x) => x.id));
for (const assignment of assignments) {
  if (!rateIds.has(assignment.unit_price_id)) {
    errors.push(`unknown unit_price_id: ${assignment.id} -> ${assignment.unit_price_id}`);
  }
}

console.log(
  JSON.stringify(
    {
      review_status: review.review_status,
      rates: rates.length,
      assignments: assignments.length,
      default_rule_reviewed: review.reviewed_default_rule,
      errors,
      valid: errors.length === 0,
    },
    null,
    2,
  ),
);

if (errors.length > 0) process.exitCode = 1;
