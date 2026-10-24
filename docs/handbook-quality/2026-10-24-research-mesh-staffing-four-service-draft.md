# Research Mesh staffing candidates: four-service scoped integration

**Date:** 2026-10-24 JST  
**State:** DRAFT_UNREVIEWED; not a national legal currentness or human-acceptance decision.  
**Source type:** Isolated ChatGPT Library research/production/review/integration bundles. These are **not** official Research Mesh adoption or publication artifacts (`real_project_work_enabled=false`).

## Source artifacts and provenance

| Service | Source Library PRODUCE ZIP | Raw ZIP SHA-256 |
| --- | --- | --- |
| 特定福祉用具販売 | `PRODUCE_KAIGO_SPECIFIC_WELFARE_EQUIPMENT_SALE_STAFFING_7F550720_20261024_REV2.zip` | `38ea38d53688a74069ac2c21d77798d068e8b5b3bc171fdb1a50d625be1cf302` |
| 福祉用具貸与 | `PRODUCE_KAIGO_WELFARE_EQUIPMENT_RENTAL_STAFFING_7F550720_20261024_REV2.zip` | `c3694726b0b8869385cf637ee32644340cd27211e70208cdf49b68833590df06` |
| 介護予防福祉用具貸与 | `PRODUCE_KAIGO_PREVENTIVE_WELFARE_EQUIPMENT_RENTAL_STAFFING_7F550720_20261024_REV2.zip` | `5e8338590bf55a44bd790f9685ca9d20969175ad14578f178dfd29246d346864` |
| 介護予防支援 | `PRODUCE_KAIGO_PREVENTIVE_SUPPORT_STAFFING_7F550720_20261023_REV2.zip` | `eddb9458acd9cd4fdcedf1a8b63a4750766bed470756432a813e7a22b1977299` |

All four ZIPs were retrieved as original Library bytes and their SHA-256 values independently computed during preparation. The source `candidate.json` files contain **44** structured rule proposals across the four services (10, 12, 11 and 11 respectively). This PR **does not import those raw objects verbatim**, because the `rule_id/requirement_kind` structure does not conform to the established handbook renderer's `role_sections[].requirements[]` schema. Instead, a focused **34-description editorial adaptation** combines certain closely related source conditions while preserving distinct specified/criteria-equivalent variants and explicit applicability caveats.

**No assertion of complete equivalence to all 44 candidate records.** Any omitted individual rule or condition remains open for follow-up source-to-target traceability. Where a prospective rule's interpretation depends on currentness or an incorporation-by-reference, it is labelled a candidate and not marked verified.

## Actual changes to Kaigo Rules

- Base main commit `f128932f3ebc39ea09edb42368cb17255465d03e`; original handbook blob `c7cae7ef47733d4b1c6303bbf36bfde9939dd44d`.
- Exactly **four** `staffing` chapters gain `role_sections`: `specific-welfare-equipment-sale`, `welfare-equipment-rental`, `preventive-welfare-equipment-rental`, `preventive-support`.
- Added 9 / 9 / 8 / 8 **individual requirements** respectively, grouped into specialist/staffing, manager, and scope/other (three groups per service).
- All other fields in these four chapters, including their prior `summary`, `paragraphs`, `checkpoints`, and any Muse-appended text, are unchanged. All other **581** chapters are byte-equivalent at JSON-object level. `homevisit` and `small-scale-multifunctional` verified/scoped `role_sections` remain untouched.
- `components/service-handbook.tsx` now renders already-supported role UI for these services; no new UI component, schema migration, source-currentness elevation, or route exposure change.
- `tests/fixtures/research-mesh-four-staffing-original.json` preserves the complete pre-integration chapter objects for independent regression; `tests/research-mesh-four-staffing.test.mjs` checks preservation, bounded scope, candidate display, and non-promotion.

## Safety / accuracy boundaries

Every added role requirement is `verification_state=EVIDENCE_GAP`. Every evidence reference is `verification_state=SOURCE_CANDIDATE_UNVERIFIED`, with empty `checked_at_jst`. A published source **URL and candidate locator do not prove** current amendment applicability, interpretation-notice consistency, local ordinance rules, qualification grandfathering, or the applicability of conditions to an individual provider.

In particular, direct designated service requirements, criteria-equivalent provisions, conditional deeming for integrated operations, separate manager provisions, read-across clauses, insurance-benefit classification and consulting qualifications are not interchangeable. The text is deliberately qualified rather than a certification that a numerical threshold currently applies to all providers.

Prior independent Research Mesh REV2 reviews were limited to isolated payload/validator tests and synthetic handbook overlays. Their `PASS_SCOPED` findings are **not** a GitHub/Next.js build pass, independent current-law check, human acceptance or official Mesh adoption. The four outputs are not granted `SOURCE_TEXT_VERIFIED`, `CURRENTNESS_VERIFIED`, `REVIEWED`, `PUBLICATION_READY`, or `DONE`.

## Before merge and future work

1. Run `npm run build:handbook`, `npm run check:handbook`, `npm run test:handbook`, and `npm run build` on this exact PR commit; fix any legacy baseline tests without weakening the invariants.
2. Independently verify the national standard's exact subsection and item locators, amendment effective dates, incorporation/read-as rules, national notices/QA, and the applicable municipal ordinances. Unknown information must remain unknown. An especially important boundary is **介護予防支援の第32条**.
3. Compare all 44 Research Mesh source rules with the 34 editorial summaries to identify details requiring a follow-up chapter update. Do not imply all 44 are represented in full.
4. Check UI/Android readability and ensure the unverified warnings are visible. Review possible overlap with open PR #552 and other handbook-content PRs before merging.
5. Do not change the Research Mesh Control Plane or its `NO_GO / real_project_work_enabled=false` state as part of this PR.

**Integration verdict at authoring: DRAFT_UNREVIEWED / no legal acceptance.**
