# Integration Sprint B verification wording inventory

Issue: #171 Integration Sprint B: verification wording and scoped counts  
Baseline main: `10123d5e5aca842caffa8ce568f4c2a12abf75bd`

This inventory covers the user-visible verification wording on the top page, cross-source search results, and representative detail surfaces. Verification dimensions remain separate: FAQ evidence mapping, independent content verification, currentness, and human review must not be promoted into one another.

| Surface | User-visible wording/state | Backing field/state | Interpretation | Action in B1/B2 |
| --- | --- | --- | --- | --- |
| Top FAQ list via `components/question-search.tsx` | `確認済み` when `status === "verified"` | `data/questions.json -> status`, plus `last_verified` and `source_refs` | The FAQ conclusion has a checked mapping to listed evidence. It does **not** mean every underlying source is current or human-verified. | Change to `根拠対応確認済み`. |
| Top FAQ empty state | `確認済みの候補ページ` | Same FAQ dataset | Same scoped FAQ state. | Change to `根拠対応確認済みの候補ページ`. |
| Cross-source search lead/section in `app/search/page.tsx` | `確認済みの実務ページ` | `questionMatches` from `questions.json` | Same FAQ evidence-mapping state, not a global currentness claim. | Change to `根拠対応確認済みの実務ページ`. |
| Cross-source FAQ result badge | `確認済み` when `item.status === "verified"` | `questions[].status` | Same scoped FAQ evidence-mapping state. | Change to `根拠対応確認済み`. |
| FAQ detail `app/questions/[slug]/page.tsx` | `FAQ根拠対応を確認済み` | `question.status === "verified"` | Explicitly scoped to the FAQ conclusion ↔ evidence relationship; page also states currentness and layer human-review are separate. | Retain. |
| Cross-source rule result | `人手確認済み` | membership in `ordinance37-review.json -> reviewed_articles` | Human review only. | Retain. |
| Cross-source fee result | `人手確認済み` | membership in `remuneration-review.json -> reviewed_nodes` | Human review only. | Retain. |
| Verification summary / overview | `独立確認済み` | `verification-registry.json -> content_verification.status === PASS` | Independent source/content verification; currentness and human review are displayed separately. | Retain. |
| Rule detail relation rows | `独立監査済み` | `edge.independent_verification.status === PASS` | Verification of the relation edge only. | Retain. |
| Law list/detail | `人手確認済み` | `care-insurance-act-review.json -> reviewed_articles` | Human review only. | Retain. |
| Notice detail | `本文の独立機械照合：一致 / 現行性：未確定 / 人手確認：…` | per-item independent verification + currentness ledger + human review | Dimensions are explicitly separated. | Retain. |

## Boundary for this work unit

This unit changes only the ambiguous FAQ list/search wording and adds regression coverage. It does not change currentness, provenance, relation verification, publication gates, or service-scope logic. Scoped corpus/service counts remain for B3 after the Sprint A service-scope contract is available.
