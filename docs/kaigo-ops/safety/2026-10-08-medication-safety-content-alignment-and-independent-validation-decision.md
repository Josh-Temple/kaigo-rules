# Kaigo Ops — Medication-safety content alignment & independent validation: E decision

Checked at: **2026-10-09 JST** (GitHub / Vercel / MHLW primary-source fresh read)  
Source instructions: `/Kaigo Ops/Work Instructions/2026-10-08_medication_safety_content_alignment_and_independent_validation_wave_instructions.md`  
Base `main`: `233f11f60bd53cee4684fd66eb5c0490b2fee926`  
Scope: **誤薬・与薬漏れの非公開試作のみ**。実在の症例・薬剤情報は使用しない。

## 1. Explicit decision (two independent axes)

- **Wave validation:** `PARTIAL_WITH_GAPS`
- **Independent safety:** `SAFETY_PARTIAL_WITH_GAPS`
- **Publication:** `PREVIEW_ONLY / NOT_PUBLIC` — **NO GO_FOR_PUBLICATION**
- **EX01:** `EXPERT_REVIEW_NOT_DONE`; **EX02:** `EXPERT_REVIEW_NOT_DONE`
- **HU01:** `HUMAN_APPROVAL_NOT_DONE`
- No new public Issue, action tool, sitemap/nav registration, enabled public preview, merge of C #451, or medication-safety production release is authorized. **PREVIEW_ONLY means isolated prototype retained; it does not mean an anonymously accessible preview is approved.**

This is an E documentation and publication-gate decision, not an expert review or a clinical safety determination. No red-team result is treated as evidence of reduced medication accidents.

Previous wave decision remains at [2026-10-08-medication-safety-validation-and-review-decision.md](./2026-10-08-medication-safety-validation-and-review-decision.md). Its earlier observations are historical and are not silently replaced.

## 2. Fresh repository/branch/version ledger

| Item | Actual inspected identity | E disposition |
| --- | --- | --- |
| `main` | `233f11f60bd53cee4684fd66eb5c0490b2fee926` | Before this E integration; **different from deployed runtime** |
| Worker A | [PR #458](https://github.com/Josh-Temple/kaigo-rules/pull/458), open, non-draft, head `cbdaddd843db2d1b193b34738272c538086039d1`; trace blob `0b042421f49ae5213f80b71e4cf04c502d32c1f9` | New crosswalk exists, **but applies to previous B blob** |
| Worker B | [PR #459](https://github.com/Josh-Temple/kaigo-rules/pull/459), open, non-draft, head `5e4a0de41afd947c3851ba75b61ee71431273255`; Issue blob `315e71f959d8d4b18e7634dd9f8c56ab184f89ae`; service blob `2f65cd6a97c9bd815d3193eb1e08a444a7d3166d` | Updated B-00–B-13 and service matrix. Final A approval of this blob **NOT_DONE** |
| Worker C | [PR #451](https://github.com/Josh-Temple/kaigo-rules/pull/451), **open/draft/unmerged**, head `3026b965ad8ef78acde36e530655426055cd716d`; `page.tsx` blob `cfa6f30633c5c8536b570c4c82b2794cd4353320`, `worksheet.tsx` `bc54ab9d8c13a1713f9e68d41b433f2c3130dc95`, review model `8853e5c5dae84293e5c283bc779fd08a3c2c79db`, C ledger `e1431d7794a476ff5823204a117841dad95cc618` | Isolated preview with changed copy, **not** production |
| Worker D | [PR #457](https://github.com/Josh-Temple/kaigo-rules/pull/457), **open/draft/unmerged**, head `dc883d027c52d90422f6e161aaa3470ab7b4048a`; results blob `9f62196382b543d5a09d8904b4e97a8ce016a263`, pack blob `eee6b2a2fae695e630cc3e8ab451339182b0ffa5` | Independent dynamic audit executed **against pinned older C** `a1357ad7ebd723c5a8c8fcf754c04b384f7db95d`. Retest is required |
| E | This decision, plus projections in E integration PR | No source or expert approval implied |

GitHub status checked on 2026-10-09 JST: A #458 and B #459 had successful `Validate build` and `Verify publication readiness integration` runs. D #457 had successful `Independent medication safety dynamic audit`, `Validate build`, and publication-readiness workflows. C #451 had successful `Validate medication safety preview`, `Validate ops site`, `Validate build`, and publication-readiness workflows. This is evidence of **those exact workflow checks**, not an overall medical-safety PASS.

C latest preview run [37783554826](https://github.com/Josh-Temple/kaigo-rules/actions/runs/37783554826): both `preview` (enabled on localhost) and `disabled` jobs succeeded, with npm install/tests/build, Chromium and route checks in the jobs. D independent run [37783550622](https://github.com/Josh-Temple/kaigo-rules/actions/runs/37783550622): `independent-enabled` and `independent-disabled` jobs succeeded using localhost, read-only source checkout and a D-owned test suite. The D case-level evidence is in [medication-safety-test-results.md](./medication-safety-test-results.md) §9 in **PR #457**, not in this E summary.

### Version discrepancy: publication-blocking

1. A's new crosswalk (§7 of PR #458) explicitly anchors B blob `083ffd0a17419e1533e65205e9230d725f3232ab`. B #459 subsequently produced `315e71f959d8d4b18e7634dd9f8c56ab184f89ae`. A **has not independently certified the final B version**. Matching paragraph IDs is not sufficient.
2. B #459's five-state handoff corresponds in visible labels to the C latest review model: `まだ確認していない / 取扱いを把握している（自己申告・未検証） / 相談したい点がある / 取り決めが見つからない / 自分の担当範囲では扱わない（責任者確認前）`. C's page/worksheet show accident-time prohibition, no clinical or reporting decision, independent design status, and print warnings. This is **E source-text inspection**, not A claim approval or independent browser/print verification of the final B+C pair. The B fixed common disclaimer and C's written text are not verbatim identical: human semantic review remains required.
3. D's 13 independent browser assertions were executed against `a1357ad7...`. Compare to latest C `3026b965...` found **7 intervening commits, including changes to `page.tsx`, `worksheet.tsx`, review model and tests**. The successful D run **must not be re-labeled as testing latest C**.
4. Professional authority, workflow existence, facility-versus-day/visit/residential/short-stay/care-management applicability, and municipality-specific accident handling remain `REVIEW_REQUIRED / NOT_ESTABLISHED`. A facility example is not a universal regulatory or staffing requirement.

## 3. Primary-source boundary (fresh E read)

- MHLW [Vol.1436, 2025-11-07](https://www.mhlw.go.jp/content/001591418.pdf): printed **p38** (PDF zero-index 40) distinguishes medication preparation and administration, potential interruptions and multiple-check examples; printed **p39** (PDF 41) is **one specified special nursing home case**, not validated general causality or universal staffing law. Printed **p46** (PDF 48) covers broader day-service information-sharing and visit-service coordination, **not universal medication-work authority**. PDF introductory notification says primary scope is facility services and additionally discusses other services' safety management.
- MHLW [Vol.1332, 2024-11-29](https://www.mhlw.go.jp/content/001574219.pdf), PDF zero-index p2: discusses accident-report scope and method; local procedures remain relevant. It **does not authorize this tool to determine individual reportability/deadlines**.
- These specific pages were opened in this E run on **2026-10-09 JST**. The complete guideline and all service-specific regulations were **not** reaudited here.

`SOURCE_SUPPORTED` is limited to bounded source descriptions; all site-specific five-state choices, workflow checklist, privacy boundary and safety disclaimers remain `DESIGN_PROPOSAL` or `REVIEW_REQUIRED`, not a Ministry-certified checklist.

## 4. Independent safety and privacy evidence versus unperformed checks

- D #457 §9 gives case-level `expected/actual/method/environment/evidence/status/limitation/retest` for **R01–R16, P01–P07 and U01–U06 (29 cases)**. Its verdicts mix `PASS_LIMITED` with `PARTIAL`. In the **tested older C version**, 13 independent Chromium tests and disabled/invalid local flag + route verifications succeeded. No high-risk failure was observed **in this bounded run**.
- D sampled synthetic selection markers in request URLs/headers/body, browser state and storage, and inspected print-mode DOM/in-memory PDF, keyboard, labels, 390px and **CSS zoom**. This is not a proof of non-disclosure in all browsers/times or of safe clinical practice. Existing pageview Analytics traffic is distinct from answer transmission.
- Still `NOT_RUN` or `NOT_ESTABLISHED`: **D re-run against latest C/B**, native 200% browser zoom, real Android Chrome, real screen reader, human print-preview inspection, offline/clipboard beyond the tested subset, actual external preview access restrictions, and interactive production-browser regression after this decision. These omissions cannot be converted into PASS.
- All cases must be re-pinned after A's final B trace, C's approved candidate SHA and D's independent rerun. Statuses for old SHA remain historical evidence.

## 5. Human review gates — no surrogate approval

| Gate | Present status | What is needed |
| --- | --- | --- |
| EX01 appropriate medical/medication safety professional | **EXPERT_REVIEW_NOT_DONE**, review ID/date/version/decision absent | Review exact A/B/C/D versions, clinical inference, medication-safety language, rights; record anonymized ID, findings, disposition, retest |
| EX02 care-accident prevention / operational risk owner | **EXPERT_REVIEW_NOT_DONE**, review ID/date/version/decision absent | Check service scope, feasible roles, workload, incident route, self-report misleading reassurance |
| HU01 authorized content/publication owner | **HUMAN_APPROVAL_NOT_DONE**, no explicit target-version GO | After EX01 and EX02 and technical closure, approve exact version, scope, text, support/update owner, publication mechanics |

Preparation of a review pack is **REVIEW_PACK_READY**, not an actual request, human review, signature or approval. Do not contact, invite or publish reviewer identities without prior explicit authorization.

## 6. Public reliability and actual production state

Fresh Vercel API check (2026-10-09 JST):
- Project: **`kaigo-ops`** / `prj_7kKmZkto1j9r9Z3otwccx05LAjTp`.
- Production deployment: **`dpl_Ae1BwiQChp3CfmK1izUcNQH8wL8S` / `target=production` / `READY`**.
- Exact production Git SHA: **`e49e770a970e541d2ad95204ad277eca89a485d3`**; canonical alias **`https://ops-site-pi.vercel.app/`**. GitHub `deploy-state/kaigo-ops` still points to that runtime SHA. The docs-only current `main` has another SHA by design.
- Authenticated Vercel HTTP fetch in this E run: home **200**; five existing Issue routes **all 200**; five existing action-tool routes **all 200**; `/robots.txt` **200**; `/sitemap.xml` **200**; **`/tools/medication-safety-preview` 404**.
- Public registry, action-tool list and sitemap generator retrieved from `main` have **only the existing five issues/tools** and no medication-safety registration. This plus HTTP 404 is a **bounded current exposure check**, not a proof that every potential preview host is inaccessible.
- Vercel project metadata lists SSO protection `all_except_custom_domains`. **Access control of any hypothetical flag-enabled C preview is not demonstrated**; `PREVIEW_ACCESS_NOT_ESTABLISHED`. No such preview was enabled by E.
- Existing routes' HTTP status **is not a browser action regression**; E did not independently operate the five live tools at 390px, inspect live Network/Analytics payloads, or test canonical for every route. Automated prior run and current HTTP smoke must remain distinct.
- Analytics `RECEIVE_CONFIRMED` (first confirmed 2026-10-07), Search Console `UNKNOWN`, custom event `CUSTOM_EVENT_NOT_JUSTIFIED`, review window **around 2026-10-21 through 2026-11-04** are **inherited canonical states**, not a fresh authenticated analytics or Search Console measurement in this E run. No measuring definition or observation window was changed.

## 7. Integration and next-owner disposition

- **E did not merge C #451 or trigger medication-safety release**, and made no production, feature-flag, Analytics, public registry or sitemap changes.
- A #458, B #459 and D #457 are source/validation documentation work awaiting final **cross-version** review. E creates the decision/projection only; **no A/B/D merge is represented as completed by this decision**. Integrate safe docs diffs only after their meaning/required-check/status has been checked again; D includes an independent CI workflow, not only Markdown.
- **A (P0):** independently map every material assertion in final B blob `315e71...` and new service blob `2f65cd...` to primary sources, correct the latest crosswalk, tag `NOT_ESTABLISHED` and `REVIEW_REQUIRED`.
- **B (P0):** finalize precise B-to-C option/result/print wording and safety boundary; avoid service-wide guarantees.
- **C (P0):** after A+B are fixed, pin exact new C SHA, run both flag cases, privacy/URL/storage/print and existing routes on isolated localhost; keep #451 draft.
- **D (P0):** independently retest full R/P/U matrix against **new pinned C code and B text** using localhost-only secret-free jobs; record limitations; prepare accurate updated expert review pack.
- **EX01/EX02 (human required):** independently evaluate the **same final frozen version**, provide actual review records.
- **HU01 (human required):** explicitly approve a specific public service scope, wording, update/feedback owner and deploy version, or hold.
- **E:** only after those gates, reassess. If approved, conduct gated CI, Vercel exact SHA/READY/alias, 11 existing + added route, robots/sitemap/canonical/feedback, network boundary, native/mobile accessibility and production regression.
- **Operations (separate track):** daily deployment verifier actual end-to-end success/token availability and authenticated Search Console state remain independently unverified.

**Wave closure:** documentation-level E decision completed **with gaps**. Publication remains **held**. Neither technical CI success nor the existence of a professional review pack licenses live medication decision support or publication.
