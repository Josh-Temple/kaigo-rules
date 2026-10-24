# Research Mesh — four additional staffing chapters (2026-10-24)

**Status:** `DRAFT_UNREVIEWED` / `HOLD_FOR_TECHNICAL_REVIEW`. No change to official Research Mesh Control Plane: `CUTOVER_CANARY / NO_GO`, `real_project_work_enabled=false`.

## Purpose and boundaries

Extend the existing "作成中・未確認" service handbooks with narrowly scoped staffing proposals for four more services. After #557 the base main is `0c525b49e3a8f6ae85004cb84da9ef89b69a4e62`. The input `data/handbook-content.json` is 39 services / 585 chapters. This change adds `role_sections` only to the `staffing` chapters below, retaining their summaries, paragraphs, checkpoints, all other 581 chapters, and all previously accepted role_sections.

| Service | Library ZIP candidate (Research Mesh) | ZIP SHA-256 | Original rules | Selected |
| --- | --- | --- | ---: | ---: |
| `homerehab` | `PRODUCE_KAIGO_HOMEREHAB_STAFFING_C7CAE7EF_20261024_REV2.zip` | `c0db74452aa2eca61689f1b7812653b5bb2c0a9b298260452b596b823c2eb599` | 12 | 5 |
| `preventive-homerehab` | `PRODUCE_KAIGO_PREVENTIVE_HOMEREHAB_STAFFING_C7CAE7EF_20261024.zip` | `1f0453b49b187fd30870237926358afeea5becb62ea5017662b390e89914da1b` | 7 | 5 |
| `preventive-dayrehab` | `PRODUCE_KAIGO_PREVENTIVE_DAYREHAB_STAFFING_C7CAE7EF_20261024.zip` | `fcea35e4771b9bf0b3f612f7938d3d0ada81804559f30cc6d54f79ebc86fd0ae` | 12 | 9 |
| `preventive-homenursing` | `PRODUCE_KAIGO_PREVENTIVE_HOMENURSING_STAFFING_C7CAE7EF_20261024_REV2.zip` | `35a46619b437488b8d295075320043580f126dc97191c22a714d34ec39a6b651` | 16 | 10 |

**Selection:** 29 of the 47 original isolated candidate rules are presented; this is **not** a 1:1 import. These are only rules directly concerning staffing levels, qualified professions, named management requirements, and conditional deemed staffing. Service operations, plan drafting, equipment and comparative/interpretation notes are not reclassified as personnel placement rules. All 47 source rules remain available in the immutable library ZIPs.

The source ZIPs are Research Mesh isolated candidates that received `PASS_SCOPED` and independent REVIEW/INTEGRATE in its own sandbox. Such a result covers source candidate structure and offline tests, not correct national law at a specific effective date, current e-Gov amended text, municipal by-laws, real Git overlay, or legal sign-off. This PR uses the library artifacts without changing any official adoption status.

## Source and confidence

- All additional requirements are `EVIDENCE_GAP`, all evidence references are `SOURCE_CANDIDATE_UNVERIFIED`, and `checked_at_jst` is empty.
- National law locators are source references **not** claims of independent verification. No newly added evidence URL is exposed as independently confirmed.
- Real-world applicability, effective dates, incorporation and read-across, exemptions, interpretation-notice text, national Q&A and municipal overrides remain **not established**.
- Clinical/human professional and facility-specific rules should be checked against original national articles and local interpretation before being relied upon.
- `shortstay-life/staffing` was **deliberately excluded** because the independent review marked its original candidate `NEEDS_REVISION` due to a substantive user-count/integrated preventive-care condition omission; a `REV2` ZIP exists but the distinct independent review of that revision was not established at the time of this wave.

## Integration and checks

The full chapter snapshots prior to this PR are pinned in `tests/fixtures/research-mesh-next-four-staffing-original.json`. The standalone `tests/research-mesh-next-four-staffing.test.mjs` checks exact pre-change chapter fields, 29 selected / 47 originally proposed, confidence-state guardrails and display allowlist. `tests/working-handbook.test.mjs` is extended for a scoped baseline exception. Only these four new service IDs are added to the handbook builder/renderer role target allowlists.

The required premerge gate is `npm run build:handbook`, `npm run check:handbook`, `npm run test:handbook`, `npm run build`, the GitHub build workflow, unchanged content outside targets, and a clean review of legal confidence labels.

**No merge or assertion of CI success is implied by authoring this document.**
