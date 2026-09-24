# Kaigo Ops research assets — status and source-of-truth rules

Updated: 2026-09-25 JST

This directory contains research assets recovered from archived PR #51. The recovery preserved unique work, but recovery alone does **not** make every checkpoint, benchmark result, review status, or workflow description current.

## Source-of-truth precedence

When files in this directory disagree with the current repository state, use the following precedence:

1. Current `main` canonical data and review ledgers under `data/`.
2. Current active workflows under `.github/workflows/`.
3. Current generated/validated artifacts tied to those canonical files.
4. Research files under `docs/kaigo-ops/research/` as supporting or historical material.

Narrative checkpoints must not override a current canonical review ledger.

## Reconciliation finding on 2026-09-25

A fresh read found a material mismatch between recovered research notes and current canonical review state.

The recovered benchmark README records a later historical state including remuneration source-review closure. On current `main`, however:

- `data/remuneration-review.json` has `review_status: NOT_STARTED`.
- `data/fee-guidance-review.json` has `review_status: NOT_STARTED`.
- `scripts/research-coverage-classifier-v0.29.mjs` reads those current canonical review files and therefore fails closed for remuneration-related questions while the reviews remain incomplete.
- The old `verify-kaigo-ops-research.yml` workflow is not active under `.github/workflows/`; the recovered copy is archived under `docs/kaigo-ops/research/archived-workflows/`.

Therefore, statements in recovered notes such as “source layer CLOSED”, “human review COMPLETE”, or specific historical CI run results must be treated as historical evidence until replayed against current `main`.

## What remains reusable

The recovered assets are still useful as research inputs, especially:

- problem definition and evidence schema;
- Claim Registry and composition design;
- benchmark question sets and safety cases;
- deterministic classifier and validation scripts;
- prior review notes that identify primary sources and unresolved boundaries.

Their value is as candidate research work and reproducibility material, not as automatic proof of current verification status.

## Safe restart procedure

Before promoting any recovered result back into active use:

1. Fresh-read the relevant canonical `data/` files and active workflows.
2. Identify exactly which recovered result depends on those files.
3. Replay the relevant validator or research script against current `main`.
4. If the recovered result assumed a different review ledger, rebuild the evidence chain rather than copying the old status.
5. Add or reactivate CI only after confirming that its inputs and expected states match current canonical data.
6. Keep RAG and public answerability fail-closed until the corresponding current review gates are satisfied.

Do not bulk-reactivate the archived research workflow.

## Current practical restart point

The next useful work is not to resume from the old 2026-09-22 checkpoint literally. Instead, reconcile the recovered research state with current canonical review ledgers one bounded area at a time.

A sensible first target is the remuneration / fee-guidance path because the recovered material contains substantial prior work while current canonical review ledgers remain `NOT_STARTED`. Any promotion should be based on fresh primary-source verification and current-main validation, not on the recovered completion labels alone.
