# Service-scope surface inventory

Issue: #170 Integration Sprint A: service-scope contract and search isolation

Inventory baseline: `main@10123d5e5aca842caffa8ce568f4c2a12abf75bd`

## Purpose

This inventory identifies service-facing runtime surfaces that read shared or service-bound corpora and records how service isolation is enforced today.

This document is inventory only. It does not change verification, currentness, human-review, publication, relation, or routing state.

## Classification

- **UNSCOPED_SHARED**: reads a shared corpus without applying the selected/public service scope.
- **PARTIAL_SCOPE**: some service logic exists, but it is hard-coded or not reusable across surfaces.
- **ISOLATED_BY_DATASET**: current data is service-specific, but isolation is provided by file/ID naming rather than a shared scope contract.
- **EXPLICIT_SERVICE_GUARD**: the surface rejects a request whose service ID does not match its corpus/package.
- **GLOBAL_BY_DESIGN**: intentionally cross-service/global and should not be filtered as a service-specific view.

## Inventory

| Surface | Runtime file | Corpus / dependency | Current service behavior | Classification | Scope risk / A2-A3 implication |
| --- | --- | --- | --- | --- | --- |
| Cross-source search `/search` | `app/search/page.tsx` | `questions.json`, `qa-corpus.json`, `ordinance37-nodes.json`, remuneration data | Gets the default service for labels/fee links, but rule matching filters all Ordinance 37 article nodes without a service predicate. QA matching also searches the loaded corpus without applying the selected service. | **UNSCOPED_SHARED** | Homevisit-only Ordinance 37 nodes can match a dayservice search. Result counts inherit the same leak. A3 must apply the canonical scope before matching and counting. |
| Ordinance list `/rules` | `app/rules/page.tsx` | `ordinance37-nodes.json`, `ordinance37-meta.json`, review data | List rows are split with hard-coded `service_scope` strings for dayservice direct/incorporated rules. Stats use global corpus meta counts. | **PARTIAL_SCOPE** | Rows currently omit homevisit-only nodes, but `nodes_total`, `articles_total`, and review denominator are shared-corpus totals. A2 helper should replace label-string checks; counts must reuse the same rule. |
| Ordinance detail `/rules/[article]` | `app/rules/[article]/page.tsx` | `ordinance37-nodes.json`, relations, application rules, law/notice/fee/question data, `incomingEdges` | `generateStaticParams` and article lookup use every article in the shared Ordinance 37 corpus. Child lookup is article-number based. Related-record panels read global relations and then apply only source-type-specific filters. | **UNSCOPED_SHARED** | A dayservice legacy URL can resolve a homevisit-exclusive article. This is the clearest detail-page isolation defect. A3 must scope both route generation/lookup and related-record rendering. |
| Care Insurance Act list `/law` | `app/law/page.tsx` | `care-insurance-act-nodes.json`, meta, dayservice scope, review | Renders all article nodes from the shared corpus. The current shared corpus was not expanded for homevisit in #168, so no present leak was reproduced, but the runtime rule is not service-aware. Stats are corpus-wide. | **UNSCOPED_SHARED (latent)** | A future shared-corpus expansion can leak another service without any page change. A2/A3 should make this surface consume the same reusable scope rule. |
| Care Insurance Act detail `/law/[article]` | `app/law/[article]/page.tsx` | shared Care Insurance Act nodes/relations/review/meta | Static params, lookup, children, and outgoing relation graph are not service-scoped. | **UNSCOPED_SHARED (latent)** | Same fail-open pattern as Ordinance detail, currently masked by corpus contents. |
| National Q&A search `/qa` | `app/qa/page.tsx` | `qa-corpus.json`, meta | Uses source-specific `service_code` values. Empty filter means all loaded rows; explicit options distinguish dayservice, day-service common, home-service common, and all-service common. | **PARTIAL_SCOPE** | Legitimate common/shared records are represented explicitly today, but with Q&A-specific codes rather than the service catalog contract. A2 should preserve this explicit common behavior while normalizing applicability. |
| Curated practical-question detail `/questions/[slug]` | `app/questions/[slug]/page.tsx` | dayservice questions/rule nodes/notices/QA plus current Ordinance 37 nodes for links | Curated corpus is dayservice-specific. Rule DB links test only whether an article number exists in the current shared Ordinance corpus. Q&A links hard-code `service=16`. | **ISOLATED_BY_DATASET / PARTIAL_SCOPE** | Current question records are dayservice-only, but linked shared records should be checked by the canonical scope before rendering. |
| Home practical-question search | `components/question-search.tsx` | `questions.json` | Searches the dayservice curated question dataset only, then submits to `/search`. | **ISOLATED_BY_DATASET** | No current cross-service corpus leak, but service identity is implicit in the dataset rather than enforced by a reusable contract. |
| Remuneration list `/fees` | `app/fees/page.tsx` | dayservice remuneration skeleton/text/meta/review | IDs and root are explicitly `fee.dayservice.*`. | **ISOLATED_BY_DATASET** | Current isolation is strong because data is dayservice-namespaced. Reuse the canonical service helper if remuneration becomes shared across services rather than duplicating this pattern. |
| Remuneration detail `/fees/[node]` | `app/fees/[node]/page.tsx` | dayservice remuneration data and relations | Reconstructs `fee.dayservice.<route>` and resolves dayservice data only. | **ISOLATED_BY_DATASET** | No current homevisit leak reproduced. Related Ordinance links should still land on a service-valid target once A3 scopes rule detail lookup. |
| Interpretation notice `/notices` | `app/notices/page.tsx` | dayservice notice review/currentness/source-chain data | Page data is explicitly the dayservice 22-item review packet. | **ISOLATED_BY_DATASET** | No current shared-corpus leak. Future multi-service notice storage should use the same contract instead of page-local dataset choice. |
| Fee guidance `/fees/guidance` | `app/fees/guidance/page.tsx` | dayservice guidance skeleton/relations/candidates/review | Dataset and related fee IDs are dayservice-specific. | **ISOLATED_BY_DATASET** | No current cross-service leak. |
| Unit price `/fees/unit-price` | `app/fees/unit-price/page.tsx` | dayservice unit-price and region-assignment data | Dataset is explicitly dayservice-specific. | **ISOLATED_BY_DATASET** | No current cross-service leak. |
| Question context API `/api/context/services/[serviceId]/questions/[slug]` | `app/api/context/services/[serviceId]/questions/[slug]/route.ts` | generated dayservice context package | Rejects a request when route `serviceId` differs from the package `service_id`. | **EXPLICIT_SERVICE_GUARD** | Positive reference for A2/A3: service identity is explicit and failure is closed. |
| Relation provider | `lib/knowledge-relations.ts` | shared relation corpora + independent audits | Builds one global relation graph. It does not apply a service filter itself. | **GLOBAL_BY_DESIGN library** | Keep the graph global, but every service-facing renderer must filter edges/targets through the canonical applicability helper. Do not change audit ownership or verification state. |
| Information overview `/overview` | `app/overview/page.tsx` | verification registry / relation inventory | Presents cross-layer/global information-foundation counts and explicitly describes broad future scope. | **GLOBAL_BY_DESIGN** | Do not force service filtering onto intentionally global product metrics. Service-specific links reached from this page still need scoped detail lookup. |
| Startup guide `/start` | `app/start/page.tsx` | static startup steps + source registry | Explicit dayservice content; no shared legal-node corpus lookup. | **ISOLATED_BY_DATASET / out of A3 core** | No shared-node isolation defect identified. |

## Confirmed defect paths on the baseline

### 1. Search leak

`app/search/page.tsx` creates:

```ts
const articleNodes = rules.filter((node) => node.node_type === "article");
```

and searches those nodes without checking whether each article applies to the default service.

After #169, the shared Ordinance 37 corpus contains homevisit-only articles in addition to the existing dayservice scopes. Therefore a dayservice search can match an article that is exclusive to homevisit.

### 2. Detail-route leak

`app/rules/[article]/page.tsx` generates routes and resolves article data from every shared-corpus article:

```ts
return nodes
  .filter((node) => node.node_type === "article")
  .map((node) => ({ article: node.article_num }));
```

and:

```ts
const articleNode = nodes.find(
  (node) => node.node_type === "article" && node.article_num === article
);
```

No selected-service applicability check occurs before rendering.

### 3. Count leak

`app/rules/page.tsx` filters displayed dayservice rows with hard-coded `service_scope` labels, but its stats and review denominator use shared `ordinance37-meta.json` totals. After the shared corpus expansion, these totals include homevisit-only nodes/articles.

## Existing representations that A2 must preserve

The current repository already has several forms of applicability evidence. A2 should normalize them instead of inventing relations.

- Ordinance 37 nodes:
  - `service_scope = "通所介護・直接規定"`
  - `service_scope = "通所介護・第105条準用"`
  - `service_scope = "訪問介護・直接規定"`
  - `applicable_via` records the legal mechanism for incorporated dayservice rules.
- `data/ordinance37-scope.json`:
  - dayservice direct articles
  - dayservice incorporated articles
  - `additional_service_direct_scopes` for homevisit.
- `data/services/<service_id>.json`:
  - service-specific scope files
  - publication/routing state.
- Homevisit generated indexes:
  - `data/services/homevisit/care-insurance-act-index.generated.json`
  - `data/services/homevisit/ordinance37-index.generated.json`
  - these select node IDs from shared corpora without promoting service-specific verification.
- Q&A:
  - explicit common scopes are represented with service codes (all-service common, home-service common, day-service common) rather than by omission.
- Context API:
  - route service ID must equal package service ID; mismatch fails closed.

## A2 handoff constraints from this inventory

The canonical contract/helper should:

1. accept an explicit `service_id`;
2. answer whether a record is applicable to that service;
3. distinguish direct, incorporated/delegated, common/shared, and exclusive-to-other-service applicability;
4. derive membership from committed scope/index evidence, not title text, search terms, or guessed relations;
5. fail closed for unknown services or records whose service applicability cannot be established;
6. be reusable by search matching, detail lookup/static params, counts, and related-record rendering;
7. leave verification/currentness/human-review/publication gates untouched;
8. preserve intentionally global surfaces such as the information-foundation overview and the underlying global relation graph.

## Export/API check

No general export endpoint is part of the currently identified service-facing runtime path. The service-specific question context API above is present and already uses an explicit service guard. If new export/API routes are added before A3, they must be added to this inventory and routed through the same canonical scope contract.
