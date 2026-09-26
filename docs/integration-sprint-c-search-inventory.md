# Integration Sprint C — C1 search source inventory

Issue: #172 `Integration Sprint C: FAQ-to-authority retrieval bridge and notice search`

Baseline main SHA: `10123d5e5aca842caffa8ce568f4c2a12abf75bd`

## Purpose

C1 records the current retrieval wiring before C2/C3 change behavior. This is an inventory only: it does not promote any source, relation, currentness state, verification state, or publication state.

## Current /search participation

| Source type | Current data path | Directly searched by `/search` | Current reachability |
| --- | --- | --- | --- |
| Practical FAQ / verified question pages | `data/questions.json` | Yes | Ranked by `rankQuestionMatches`; answer detail remains fail-closed when a question is not verified |
| Ordinance / standards | `data/ordinance37-nodes.json` | Yes | Article title, caption, and related official text are searched; review state is displayed separately |
| National Q&A | `data/qa-corpus.json` | Yes | Corpus text is searched directly and is labelled as collected/currentness-unconfirmed |
| Remuneration notice / fee schedule | `data/remuneration-current-skeleton.json` + `data/remuneration-current-text.json` | Yes | Structured fee nodes and official-text candidates are searched; review state is displayed separately |
| Interpretation notices | `data/notice-nodes.json` | No | Reachable only through verified FAQ detail pages that already carry explicit `notice_node_ids`; not cross-searched |
| Fee guidance / 老企第36号 | `data/fee-guidance-*.json` | No | Separate `/fees/guidance` review surface; not cross-searched |
| Care Insurance Act | `data/care-insurance-act-nodes.json` and service indexes | No | Structured corpus exists, but `/search` does not import it; homevisit indexes remain explicitly non-public/unverified |

## FAQ-to-authority bridge today

`app/questions/[slug]/page.tsx` already has an explicit, verified-gated evidence path:

- `rule_node_ids` → standards records
- `notice_node_ids` → interpretation notice records
- `qa_item_ids` → curated national Q&A records
- `source_refs` → source registry records

The cross-source search page does **not** consume `data/relationships.json`, so a lexical FAQ hit is not expanded into its linked authority records in the search result set. That is the C2 gap.

## Notice-search gap

Interpretation notices are present as structured records with mixed verification states, but `app/search/page.tsx` does not import or search them. Any C3 implementation must preserve the existing fail-closed publication/currentness rules instead of treating every notice candidate as public or current.

## Safety observations

- No inferred relation is used by the current search page.
- FAQ detail authority links are gated by `question.status === "verified"`.
- Fee-guidance machine reconstruction remains separate from direct cross-search.
- The Care Insurance Act shared corpus and service indexes do not imply service-specific publication or verification.
- C1 makes no behavior change and does not alter provenance/currentness/verification/publication fields.

## C1 conclusion

The current cross-source search directly searches four source families: practical FAQ, standards, national Q&A, and remuneration fee records. Interpretation notices, fee guidance, and the Care Insurance Act are excluded from direct cross-search. Interpretation notices can be reached indirectly from selected verified FAQ pages through explicit stored IDs; relation-driven expansion is not yet implemented.
