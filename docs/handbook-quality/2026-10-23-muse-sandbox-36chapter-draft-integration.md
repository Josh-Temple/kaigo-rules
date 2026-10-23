# Muse-sandbox: 36 sparse handbook chapters — draft integration

Date: 2026-10-23  
Status: **DRAFT_UNREVIEWED / HOLD_NO_MERGE**  
Target: `data/handbook-content.json`  
Base kaigo-rules main: `49de8c21b1bd837f8fbdb1538f179f86b5c0c54b`  
Source: [Josh-Temple/muse-sandbox](https://github.com/Josh-Temple/muse-sandbox/tree/8f94ab9734410569653c7dd09012f1d10ef44480), SHA `8f94ab9734410569653c7dd09012f1d10ef44480`, `batch-01`–`batch-08`.

## Scope and safeguards

- Selected **exactly 36** chapters for which the base `data/handbook-content.json` had no `summary` and combined `paragraphs` below 200 characters. All 36 service/chapter keys exist in the base and exactly match the source's `progress.json` weak-chapter selection.
- Added **36 summaries, 140 paragraphs and 169 checkpoints**. Prior paragraphs and checkpoints are retained *as ordered prefixes*. Existing `role_sections` are retained verbatim. No other chapter records were changed. Service/chapter totals remain **39 / 585**.
- Existing legal source corpora, currentness, verification, applicability, review status, release flags, and Q&A state were **not** modified. This integration **does not grant** source verification, human legal review, complete legal currentness, applicability to any individual provider, or production release.
- Source ledgers contain **199 evidence entries** across 36 chapters. Each includes an e-Gov URL, law ID, main/supplementary provision, quote/excerpt, date and source-data SHA-256. These are Muse's *reported* checks, **not independently re-run or accepted by this import**.
- **Do not treat imported explanatory prose or practical checkpoints as statutory text.** Muse labels them AI-authored interpretation. The ledgers predominantly cite Acts and ministerial ordinances, not a comprehensive current set of interpretation notices, national Q&A, or local ordinance requirements.
- In particular, `homevisit/staffing` already had detailed `role_sections` addressing manager, service-provision responsible person and care workers. Preserve those richer role-based sections and resolve any contradictory duplicate content before acceptance.
- `batch-01`–`batch-05` record separate `unverified_notes`, while later batches do not carry the same field: absence of notes **must not** be interpreted as zero unresolved questions.

## Targeted correction made during import

The Muse draft for `homevisit/staffing` cited the manager requirement as Ordinance 37 Article 6 paragraph 1 and its concurrent-role exception as paragraph 2, but its own ledger's Article 6 text comprises a main provision followed by a proviso. In the imported paragraphs, corrected the references to **「第6条本文」** and **「第6条ただし書」**, respectively.

This correction is scoped to those two mistaken references and **is not an exhaustive legal validation** of the other statements, paragraph/item locators, cross-references, or applicability.

## Known open review work

1. Independently match every quantitative requirement, period, role qualification, exception, proviso and paragraph/item number to a current official text. Verify any incorporation-by-reference or read-across, including local provisions. Confirm there are no conflicts with the existing detailed staffing sections.
2. Reconcile each chapter with **national interpretation notices, administrative circulars, and Q&A** and distinguish local ordinances and municipal handbook examples from the national baseline.
3. Verify effective-date/currentness and source identities against the project's existing national source and service applicability models. Muse's original data SHA-256 is evidence provenance, not a live currentness grant.
4. Inspect practical checkpoints for descriptions of legal duties vs suggestions for internal operation. Ensure no recommendation is described as a statutory requirement without a source.
5. Run `npm run check:handbook`, `npm run test:handbook`, and `npm run build`; inspect service handbook output for each target and ensure no change to the non-targeted **549** chapters.
6. Conduct independent legal/content acceptance and Android/browser checks as appropriate before merging. Existing release and noindex policy remain unchanged.

## Readback / implementation notes

- Created from the exact base main SHA above, not from an unspecified snapshot.
- Static preflight confirmed 36 unique target keys; all target summaries were blank, each target combined paragraph count below 200 characters; 585 chapters unchanged; all 549 non-target chapter objects JSON-identical; existing `homevisit/staffing.role_sections` JSON-identical; old paragraphs and checkpoints preserved as prefixes.
- **Remote Node/npm tests and live official-source verification have not yet been run.** Do not present this as a test pass.
- **Merge gate: HOLD_NO_MERGE.** This is a working draft for review, not approved national legal guidance.
