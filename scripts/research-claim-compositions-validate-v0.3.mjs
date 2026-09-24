import fs from "node:fs";
import path from "node:path";

const root = process.cwd();
const readJson = (relative) =>
  JSON.parse(fs.readFileSync(path.join(root, relative), "utf8"));

const claims = readJson(
  "docs/kaigo-ops/research/claims/claims-v0.9.json",
);
const compositions = readJson(
  "docs/kaigo-ops/research/claims/claim-compositions-v0.3.json",
);
const questions = readJson("data/questions.json");

const verifiedStatuses = new Set([
  "VERIFIED_CURRENT",
  "VERIFIED_SOURCE_TEXT",
  "VERIFIED_WITH_SOURCE_LIMITATION",
  "VERIFIED_INTERPRETATION",
]);

const claimsById = new Map(
  claims.claims.map((claim) => [claim.claim_id, claim]),
);
const issueIds = new Set(questions.map((question) => question.slug));
const compositionIds = new Set();
const errors = [];

for (const composition of compositions.compositions) {
  if (compositionIds.has(composition.composition_id)) {
    errors.push(`duplicate composition_id: ${composition.composition_id}`);
  }
  compositionIds.add(composition.composition_id);

  if (!issueIds.has(composition.issue_id)) {
    errors.push(
      `unknown issue_id ${composition.issue_id}: ${composition.composition_id}`,
    );
  }

  if (
    !Array.isArray(composition.required_groups) ||
    composition.required_groups.length === 0
  ) {
    errors.push(
      `routing.required_groups missing: ${composition.composition_id}`,
    );
  } else {
    composition.required_groups.forEach((group, index) => {
      if (
        !Array.isArray(group) ||
        group.length === 0 ||
        group.some((term) => typeof term !== "string" || term.length === 0)
      ) {
        errors.push(
          `invalid routing group ${index}: ${composition.composition_id}`,
        );
      }
    });
  }

  if (
    !Array.isArray(composition.claim_ids) ||
    composition.claim_ids.length < 2
  ) {
    errors.push(
      `composition must contain at least 2 claims: ${composition.composition_id}`,
    );
    continue;
  }

  for (const claimId of composition.claim_ids) {
    const claim = claimsById.get(claimId);
    if (!claim) {
      errors.push(
        `unknown claim_id ${claimId}: ${composition.composition_id}`,
      );
      continue;
    }

    if (
      claim.answerability !== "ANSWER" ||
      !verifiedStatuses.has(claim.verification_status)
    ) {
      errors.push(
        `unsafe composition claim ${claimId}: ${composition.composition_id}`,
      );
    }
  }
}

console.log(
  JSON.stringify(
    {
      compositions: compositions.compositions.length,
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
