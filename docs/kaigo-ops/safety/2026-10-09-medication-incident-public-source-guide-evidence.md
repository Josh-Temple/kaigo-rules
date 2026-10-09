# Kaigo Ops — 公的資料による服薬事故の注意事項（公開情報ページ）: Scope and Evidence Record

**2026-10-09 JST / Source check fresh / Baseline main:** `baccd8b7dd2423e5969534678ee6c566e6f0ed44`  
**Candidate:** `ops-site/app/guides/medication-incident-sources/page.tsx`  
**Previous E safety decision:** [2026-10-09 medication safety expert/accessibility/privacy gates](./2026-10-09-medication-safety-expert-review-and-accessibility-privacy-gates-decision.md)  
**Publication boundary:** Public **static source guide only**. Existing hidden interactive `/tools/medication-safety-preview` (C #451) remains `PREVIEW_ONLY/NOT_PUBLIC`. Publishing the guide does **not** amend any EX01/EX02/HU01 gate or authorize the prototype. No collection of patient, medication or incident details; no incident grading, clinical decisions or case-specific statutory verdicts.

## 1. Why this is separate from the unapproved prototype

The existing C prototype performs selections/answers and produces customized on-screen/print results: it requires real expert/operational reviews, accessibility/privacy checks and HU01 approval. The **new candidate is editorial text with outbound official-source links only**. It does not present a self-test, medical decision tree, risk score, personal health or medicine data entry, emergency response automation, or new public issue/action-tool registry item. Review and any production deployment must be gated and independently verified. **This information page is not evidence that the held prototype passed human gates.**

## 2. Source-to-claim and force/scope mapping

| Topic / planned publication statement | Grounding / precise location | Evidence type / applicability | What must NOT be said |
| --- | --- | --- | --- |
| Safety first, internal report, nursing/medical professional coordination and predefined first-response route | [MHLW Vol.1436](https://www.mhlw.go.jp/content/001591418.pdf), booklet p25–26, PDF 0-based pp27–28 (2025-11-07) | Public guideline, primarily facilities; institutional procedure recommendation. E checked text and PDF screenshots | Site decides ambulance/observation/treatment or authorizes medicine decisions |
| Wrong medication administered to a resident: don't independently label it harmless; seek examination | [2017 MHLW-hosted research report](https://www.mhlw.go.jp/file/06-Seisakujouhou-12300000-Roukenkyoku/73_aruteppu.pdf), Ⅰ編 p45, PDF 0-based p56 | **Research report's practice recommendation scoped to elderly housing**, not an all-service statute. Includes `必ず受診` in this defined example | “Every medication issue must by law be phoned to the PCP”; universal requirement or personal medical advice |
| Medicine interactions & how to ask a professional | [PMDA medication consultation](https://www.pmda.go.jp/safety/consultation-for-patients/on-drugs/0003.html), current official page | General pharmacist/physician consultation information. PMDA does not provide diagnosis/treatment | Assert interaction severity, infer symptoms, predict medicine effects |
| Municipality accident reporting death/treatment vs other cases | [MHLW Vol.1332](https://www.mhlw.go.jp/content/001574219.pdf), notification PDF 0-based p2–3 (2024-11-29) | “In principle report all” if death or physician-assessed treatment; others per local government. First report promptly, 5 days **guideline** | Reporting every minor error by national law; guarantee a single statutory deadline/service-wide applicability |
| Preventive multilayer checks, interruption reduction, systems vs person blame | [MHLW Vol.1436](https://www.mhlw.go.jp/content/001591418.pdf), booklet p38–39, PDF 0-based pp40–41 | Facility-oriented prevention recommendations; case on p39 is single facility. E checked PDF screenshots | Two-person check is legally mandatory everywhere; demonstrated accident reduction |
| Criminal exposure only if criminal-law conditions actually satisfied | [Japanese Penal Code art.211](https://laws.e-gov.go.jp/law/140AC0000000045) | Law on professional negligence causing death/injury; responsibility depends on necessary elements in a case | A medication error is automatically criminal; threat-based instruction to contact PCP |

**Authoring rule:** Link the original official documents and give title, date, page, purpose, and publication scope. Paraphrase, don't republish full PDFs or copyrighted tables/figures. A visible source anchor should follow every risky statement. Prefer "資料にはこう記載" and "所属先の正式手順で確認" to unconditional invented requirements. Distinguish advice to notify clinicians from separate municipal reporting and from criminal liability.

## 3. Verification and release conditions

- Static new route: `/guides/medication-incident-sources`, canonical metadata via `buildPublicPageMetadata`; homepage entry and sitemap path. No new Issue or tool, no C source changes or enabling flags.
- Extend route smoke to require the new source page, the source anchors, link from homepage and absence of unapproved interactive tool link. Keep existing 11 routes' checks and 5 Issue/5 tool counts unchanged.
- Run `npm test`, `npm run build`, `npm run test:browser`, `npm run verify:routes`, and publication readiness on PR. Browser and 390px verification should be reported as local vs production separately.
- Required after merge to claim publicly live: Kaigo Ops project ID `prj_7kKmZkto1j9r9Z3otwccx05LAjTp`, target=production, READY, exact runtime SHA, alias `https://ops-site-pi.vercel.app`, new route HTTP 200 + source links/metadata, existing 11 routes and prototype route 404, main readback, and `deploy-state` if officially verified.
- If no evidence of production runtime and route operation, report `MERGED_NOT_DEPLOYED` or `PRODUCTION_NOT_VERIFIED`, not publicly live.
- On this public informational page, there is **no EX01/EX02 expert review**. This is expressly disclosed; publication as source signposting does not approve the operational use of any medical procedure. Formal real reviewer requests stay deferred as instructed by project owner (NOT_REQUESTED).

## 4. Consequential risk / review trigger

P0 if any unsupported categorical medical action (“always call a primary doctor even for every incident”), de-contextualized 2017 guidance, fabricated criminal penalty inevitability, misstatement of municipal reporting obligations, missing incident-response emergency boundary, exposed input or unwanted changes to C draft. Revisit if MHLW/PMDA sources updated, user feedback questions applicability, service-specific use is proposed, or a technical test fails.

**Human-expert gate for the separate C worksheet remains `EX01/EX02 EXPERT_REVIEW_NOT_DONE / HU01 HUMAN_APPROVAL_NOT_DONE` with release HOLD.**