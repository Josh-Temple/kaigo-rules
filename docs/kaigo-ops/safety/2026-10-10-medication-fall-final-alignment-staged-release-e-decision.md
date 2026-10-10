# Kaigo Ops — Final Medication/Fall Alignment, Independent Reaudit and Staged Release: E Decision

**Checked:** 2026-10-10 JST (fresh GitHub and Vercel connector reads).
**Wave instruction:** `/Kaigo Ops/Work Instructions/2026-10-10_medication_fall_final_alignment_independent_safety_reaudit_and_staged_release_wave_instructions.md`.
**Prior E decision:** [2026-10-10-medication-fall-exact-head-controlled-release-e-decision.md](2026-10-10-medication-fall-exact-head-controlled-release-e-decision.md).
**Decision:** **`PARTIAL_WITH_GAPS`; no application merge, no new production release, no deploy-state advancement.** This decision records current evidence and blockers; it is not a clinical, legal or expert approval.

## 1. Independent scope decisions

| Scope | E decision | Reason |
| --- | --- | --- |
| Existing medication-source guide text revision | **`RELEASE_HOLD`** | A finally reconciled B latest, but D §10 predates that reconciliation; same-version final independent D acceptance is absent. Penal Code Article 211 effective-version full direct authoritative text remains `NOT_ESTABLISHED`. |
| New facility-focused fall/fall-from-bed source guide | **`PUBLIC_SOURCE_GUIDE_HOLD`** | C implemented the route and CI passed, but final A/B/C/D identity and independent D review of those final exact references are not established. |
| Nonmedical navigation, citation/print and accessibility UI | **`RELEASE_HOLD`** | D's limited mechanical assessment does not authorize merging the coupled eight-file C PR. No independent UI-only release unit, new-head CI and D reacceptance exist. |
| Foreign-object ingestion | **`PUBLIC_SOURCE_GUIDE_HOLD`** | Outside this Wave. |
| Aspiration / choking | **`PUBLIC_SOURCE_GUIDE_HOLD`** | Outside this Wave. |
| Selection-based medication prototype #451 | **`PREVIEW_ONLY / NOT_PUBLIC / HUMAN_REVIEW_DEFERRED`** | Draft and unmerged. Do not enable preview flags on public deployments. EX01/EX02 not requested / expert review not done; HU01 human approval not done. |

**A/B/C/D final same-version chain:** `NOT_ESTABLISHED`. **Wave:** `PARTIAL_WITH_GAPS`. No `RELEASE_GO` was issued.

## 2. Freshly retrieved immutable identities and relationships

At start of E integration, latest `main` was **`9dd655fcbd2a37c19d5d8b77606d75149105434d`**, following historical E PR #476 (docs-only). GitHub PR states and changed paths were checked afresh:

| Worker | Live PR / latest head | GitHub blob read back / evidence | E finding |
| --- | --- | --- | --- |
| A | [#474](https://github.com/Josh-Temple/kaigo-rules/pull/474), open, non-draft, head `55e7dbee9838d7055ffc3115b3bcc870eb5844f3` | Claim ledger `b603592b3b91f303cf021af283b953bd8b9e05d1`, §8 | **Now reconciles B exact head `0b192a...` / blob `4549fa...`** (MED-A01–08, X-02, FALL-01–03); SOURCE `PASS_LIMITED`. Earlier §7 retains historical B ref. |
| B | [#466](https://github.com/Josh-Temple/kaigo-rules/pull/466), **draft**, open, head `0b192a57674681952afcc4766d4cd03ce523e331` | Editorial `4549faac7651b6c3f88291740548e179e74e037a`, §8 | Compares 16 quoted blocks to C candidate (self-assessment); editorial `PASS_LIMITED`, not independent approval. |
| C | [#465](https://github.com/Josh-Temple/kaigo-rules/pull/465), open, head `b33f8b166628f7c06fb96cc7ccac95a579e24434` | Handoff `2f9c3003e4839505e22195ce685e8d7f5587bebb`. Medication TSX `f3415366187b47c8a6a93a378f3f223e0971d181`; fall TSX `de66e2dfcb0985864be230049ecea44612fd3b05`. Browser tests `b7f07446c80e5aaf14b4a872a90c68a9e16b1ccc`. | Eight changed paths: handoff, CSS, two guide TSXs, home, sitemap, route verifier and browser spec. Code blobs read back at **latest C head**; doc-only final handoff update does not equate to D review of final A/B versions. |
| D | [#475](https://github.com/Josh-Temple/kaigo-rules/pull/475), open, non-draft, head `4694ca9ee6ce383be03c0f661baeacb067c5a20d` | Independent audit `a72a7fbf6af813d7c7de38f3a033014c1c9584c3`, §10 | D independently examined 12 risk cases and C **older head `ef12b659...`**, B **older blob `1394df...`**, A **older blob `2849cdc...`**. That C version shares current code/test blobs, but D did **not** validate final A/B references or C head `b33f8b...` as the complete acceptance tuple. D: medication BLOCKED; fall PARTIAL_WITH_GAPS; nonclinical UI PASS_LIMITED. |

The document-only late A/B/C head updates are not treated as proof of a **new D acceptance**. D's §10 request to repair A's older B reference was substantially addressed by A §8 **after D's assessment**. The correct next action is a bounded D delta-reaudit at the fixed final A/B/C identity, not retroactive alteration of D's verdict.

### C code/test evidence (latest head readback)

`ops-site/app/page.tsx` blob `ca0113d6de512236acb87c5346bc6d69bcd8b26e`; `ops-site/app/sitemap.ts` blob `a85ad4d8069e0d0f4bde400fbda7dfaba2f44175`; `ops-site/app/globals.css` blob `f2a43acf8f062560db9fbf3aa2fffc31e684ed58`; `ops-site/scripts/verify-routes.mjs` blob `1f8e9c1e321c4961fa2844bbc3621e934fd1b267`.

Current C head GitHub Actions: [Validate ops site #38046418244](https://github.com/Josh-Temple/kaigo-rules/actions/runs/38046418244), [Verify publication readiness #38046418246](https://github.com/Josh-Temple/kaigo-rules/actions/runs/38046418246), [Validate build #38046418248](https://github.com/Josh-Temple/kaigo-rules/actions/runs/38046418248) **completed/success**. This is machine/CI evidence at C head, not production or native mobile verification.

B head build and publication-readiness were success (runs #38046502595 / #38046502583); D head build and publication-readiness were success (runs #38046664797 / #38046664783). A head publication-readiness was success (run #38046714637); its build **was in progress at the E pre-decision query** (run #38046714695). Do not represent that in-progress result as PASS; refresh before any A documentation-only merge. CI checks do not supersede the D publication gate.

## 3. Source boundaries and 12-risk-case safety disposition

A §8 and D §10 distinguish Ministry of Health 2025 Vol.1436 facility-focused guideline (booklet pp25–26, 30, 32, 38–39 / PDF pp28–29, 33, 35, 41–42); Ministry 2024 Vol.1332 accident notification (text pp1–3 / PDF pp2–4: superseded 2021 notice, reportable accident, five-day **guideline**, common form target services); 2017 research in housing for older people (Part I p45 / PDF p57); PMDA's general drug inquiry; and Penal Code Article 211. Their different document types, applicability and page locators are not interchangeable.

A's latest B comparison found the N24 link split to PDF pp3 and 2 without a new medical/legal claim. A `PASS_LIMITED` is source-to-paragraph consistency, not legal assurance. The effective-revision official **full text** of Article 211 has not been directly verified by both A and D: `NOT_ESTABLISHED`. Municipality-specific reporting rules: `NOT_ESTABLISHED`. No automatic individual medical, emergency, accident-report, restraint, or criminal-liability judgment is permitted.

D §10 assessed seven medication-risk interpretations (trivial injury means no response; nationwide mandatory medical referral; medical advice substitutes for municipal reporting; wrong drug means criminal liability; static guide as emergency protocol; facility example generalized nationwide; false MHLW/expert approval) and five fall risks (guaranteed prevention/negligence; restraint legality; bed rail/sensor/instruction prescription; individual clinical referral; single-facility efficacy generalized). **No new conspicuous unsafe assertions were identified in those inspected C TSX blobs**, but D left medication BLOCKED and fall PARTIAL_WITH_GAPS for the final acceptance gate. Machine red-team review is not field or expert safety approval.

## 4. Production and verification separation

Kaigo Ops **dedicated Vercel project**: `prj_7kKmZkto1j9r9Z3otwccx05LAjTp`. Fresh Vercel production list plus alias lookup show deployment **`dpl_9r41Hq62ViHcU2YAtMyuoMGmqUbu`**, `READY`, target `production`, GitHub repo `Josh-Temple/kaigo-rules`, runtime Git SHA **`ffd70abb5723e950a0a1036795f28da31614a1f3`**, alias **`https://ops-site-pi.vercel.app/`**. This is the **existing** medication source-guide runtime, not C #465 or the E docs-only commit. It is distinct from `main` and from CI head.

Historical external read-only public HTTP probe [#37993334787](https://github.com/Josh-Temple/kaigo-rules/actions/runs/37993334787) confirmed expected **15/15** responses on that older runtime. There has been **no newly released** E code deployment; hence **`PRODUCTION_NOT_VERIFIED` for a new 15/16-URL release**, with new-release HTTP/HTML/DOM **`NOT_RUN`**. If fall is published in a later wave, require 16 target URLs; without fall, 15, including the 11 original public routes, medication guide, #451 404, robots and sitemap. Headless CI checks are not Android native zoom or human usability trials.

- Android Chrome native 200%, screen-reader human listening, paper print, PDF `#page` real-viewer behavior: **`NOT_RUN`**.
- EX01 / EX02: **`NOT_REQUESTED / EXPERT_REVIEW_NOT_DONE`**; HU01: **`HUMAN_APPROVAL_NOT_DONE`**. #451 remains draft/unmerged/nonpublic; no flag activation.
- Fresh read of GitHub `deploy-state/kaigo-ops` branch resolves to **`e49e770a970e541d2ad95204ad277eca89a485d3`**. **`UNCHANGED`**. No new formal post-deploy verifier run or deploy-hook chronology satisfying the contract was supplied; do not advance the marker.

## 5. Integration actions and explicit next owners

This E decision is **documentation-only**. It does not merge #465, #466, #474 or #475, change #451, modify the public app, enable flags, trigger a new production deploy, touch analytics or run external expert outreach. A/D documentation-only PRs can be merged separately **only** after their latest content, CI, mergeability and version applicability are rechecked; D §10 is not the final aligned D audit. In particular, A's pending build is not a green check.

1. **D owner:** independently compare final **A blob `b603592...` → B blob `4549faa...` → C head `b33f8b...`** and final code/test blobs, and record explicit 12-case scope decisions in #475 §11 or a clearly versioned addendum. Resolve or hold L211 legally sensitive text; do not assume final PASS from unchanged TSX.
2. **B/C owners:** if D identifies any source/wording/rendered-text mismatch, fix only that scope, refreeze immutable blobs, rerun exact-head CI and D. For an independent UI-only release, split the actually safe files so no held guide route/link/sitemap/medical/legal statement leaks, then retest and re-audit the **new** head.
3. **E owner:** rerun the three independent publication decisions against exact A/B/C/D, recheck latest PR/CI/mergeability, then merge only supported release units. If actual production code is merged, verify the dedicated deployment ID, runtime SHA, alias and new external HTTP/HTML/DOM; advance deploy-state **only** on the formal deployment-verification contract. Update E decision/CURRENT/README and read back main.
4. **Human gates:** no expert or public-release approval is inferred; no independent reviewer is contacted during this Wave.

**Fail-closed endpoint:** `PARTIAL_WITH_GAPS` and each scoped HOLD are a completed E decision, not a blocked request to publish at any cost. Preserve older ledger sections as history and revisit only when new relevant evidence exists.
