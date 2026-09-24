import fs from "node:fs";
import path from "node:path";

const root = process.cwd();
const registry = JSON.parse(
  fs.readFileSync(
    path.join(root, "docs/kaigo-ops/research/claims/claims-v0.18.json"),
    "utf8",
  ),
);
const questions = JSON.parse(
  fs.readFileSync(path.join(root, "data/questions.json"), "utf8"),
);

const allowedAnswerability = new Set([
  "ANSWER",
  "PARTIAL",
  "REVIEW_REQUIRED",
  "LOCAL",
  "OUT_OF_SCOPE",
]);

const verifiedStatuses = new Set([
  "VERIFIED_CURRENT",
  "VERIFIED_SOURCE_TEXT",
  "VERIFIED_WITH_SOURCE_LIMITATION",
  "VERIFIED_INTERPRETATION",
]);

const allowedStatuses = new Set([
  ...verifiedStatuses,
  "CANDIDATE_UNREVIEWED",
  "REVIEW_REQUIRED",
  "LOCAL_DEPENDENT",
  "OUT_OF_SCOPE",
]);

const issueIds = new Set(questions.map((q) => q.slug));
const ids = new Set();
const errors = [];

for (const claim of registry.claims) {
  if (ids.has(claim.claim_id)) {
    errors.push(`duplicate claim_id: ${claim.claim_id}`);
  }
  ids.add(claim.claim_id);

  if (!allowedAnswerability.has(claim.answerability)) {
    errors.push(`invalid answerability: ${claim.claim_id}`);
  }

  if (!allowedStatuses.has(claim.verification_status)) {
    errors.push(`invalid verification_status: ${claim.claim_id}`);
  }

  if (
    claim.issue_id !== null &&
    !issueIds.has(claim.issue_id)
  ) {
    errors.push(
      `unknown issue_id ${claim.issue_id}: ${claim.claim_id}`,
    );
  }

  if (verifiedStatuses.has(claim.verification_status)) {
    if (claim.reviewed_at === null) {
      errors.push(
        `verified claim missing reviewed_at: ${claim.claim_id}`,
      );
    }

    if (
      claim.source_node_ids.length === 0 &&
      claim.source_ids.length === 0
    ) {
      errors.push(
        `verified claim missing source: ${claim.claim_id}`,
      );
    }

    if (claim.answerability !== "ANSWER") {
      errors.push(
        `verified claim not ANSWER: ${claim.claim_id}`,
      );
    }
  }

  if (
    claim.verification_status === "CANDIDATE_UNREVIEWED" &&
    claim.reviewed_at !== null
  ) {
    errors.push(
      `unreviewed candidate has reviewed_at: ${claim.claim_id}`,
    );
  }

  if (
    claim.answerability === "ANSWER" &&
    !verifiedStatuses.has(claim.verification_status)
  ) {
    errors.push(
      `ANSWER claim is not verified: ${claim.claim_id}`,
    );
  }
}

for (const claim of registry.claims) {
  if (claim.routing === undefined) continue;

  const groups = claim.routing.required_groups;
  if (!Array.isArray(groups) || groups.length === 0) {
    errors.push(`routing.required_groups missing: ${claim.claim_id}`);
    continue;
  }

  groups.forEach((group, groupIndex) => {
    if (
      !Array.isArray(group) ||
      group.length === 0 ||
      group.some((term) => typeof term !== "string" || term.length === 0)
    ) {
      errors.push(
        `invalid routing group ${groupIndex}: ${claim.claim_id}`,
      );
    }
  });

  const excluded = claim.routing.excluded_terms ?? [];
  if (
    !Array.isArray(excluded) ||
    excluded.some((term) => typeof term !== "string" || term.length === 0)
  ) {
    errors.push(`invalid routing.excluded_terms: ${claim.claim_id}`);
  }

  const guards = claim.routing.fallback_guard_terms ?? [];
  if (
    !Array.isArray(guards) ||
    guards.some((term) => typeof term !== "string" || term.length === 0)
  ) {
    errors.push(`invalid routing.fallback_guard_terms: ${claim.claim_id}`);
  }
}

const summary = {};
for (const claim of registry.claims) {
  const key = claim.verification_status;
  summary[key] = (summary[key] ?? 0) + 1;
}

console.log(
  JSON.stringify(
    {
      claims: registry.claims.length,
      status_counts: summary,
      routable_claims: registry.claims.filter((claim) => claim.routing !== undefined).length,
      errors,
      valid: errors.length === 0,
    },
    null,
    2,
  ),
);

if (errors.length > 0) {
  process.exitCode = 1;
}
