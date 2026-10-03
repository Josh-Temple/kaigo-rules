# Product direction: national-source database + service handbooks + Q&A search

Status: design note / draft  
Recorded: 2026-10-03

## Purpose

Kaigo Rules should be developed as a national-source knowledge base for long-term care service operation.

The core objective is not to reproduce a municipal handbook. It is to make the parts of operation that can be established from national primary materials easier to inspect, understand, and trace back to evidence.

The product should therefore have three first-class public surfaces:

1. a comprehensive evidence-backed database,
2. service-specific handbook-style guidance,
3. a searchable Q&A database.

The database is the foundation. The handbook and Q&A experiences should be built on top of structured, traceable data rather than maintained as independent copies of the same rules.

## 1. Database remains the primary foundation

The database should continue to move toward completeness across all services and all major national source types.

The public database overview is a required product surface, not an internal implementation detail.

Users should be able to browse and filter structured records directly, including by:

- service,
- topic,
- source type,
- legal / notice / Q&A layer,
- effective period,
- verification state,
- publication state,
- related rule or Q&A.

The database should preserve the difference between:

- official source text,
- machine-extracted or reconstructed text,
- normalized structured data,
- human-authored explanation,
- verification / currentness / human-review state.

No presentation layer should erase these distinctions.

## 2. Service-specific handbook experience

Each service should eventually have a handbook-style view that is practical to read from beginning to end.

A typical structure can follow the order used in well-developed municipal operating guides:

- scope and basic concepts,
- staffing requirements,
- facility / equipment requirements,
- operating requirements,
- records and documentation,
- user protection and risk management,
- remuneration,
- reductions,
- additions,
- related procedures and notices.

The handbook should be written for practical comprehension, but each statement should link back to the structured rule records and their primary evidence.

A handbook page should therefore be able to show, where applicable:

- plain-language explanation,
- applicable service and scope,
- controlling ordinance / ministerial ordinance,
- interpretation notice,
- related notification or administrative communication,
- related national Q&A,
- effective date / revision context,
- currentness state,
- verification state,
- link to the corresponding database record.

The handbook must not silently fill gaps in national materials. If the national source does not establish a point clearly, the page should say so and distinguish matters that require municipal confirmation.

## 3. Q&A as a searchable database

National Q&A should remain a structured database in its own right.

The Q&A surface should support full-text and faceted search and preserve, at minimum:

- service classification,
- topic,
- question,
- answer,
- issuing document,
- issue date,
- question number,
- official source URL,
- relationship to relevant rules / notices,
- currentness or review state where available.

Q&A should be reachable both directly and from handbook sections.

Navigation should work in both directions:

- handbook -> related Q&A,
- Q&A -> related rule / handbook section,
- database record -> related Q&A.

Q&A alone should not be treated as the complete legal basis when a higher-level source exists.

## 4. Role of municipal handbooks

Municipal handbooks are useful references for information design and coverage, but are not the canonical legal source for the national layer.

They should mainly be used to identify:

- topics practitioners actually need,
- useful section ordering,
- recurring operational questions,
- checklist structures,
- omissions in the current Kaigo Rules coverage,
- ways to make complex national rules readable.

Examples worth continuing to compare include:

- Yokohama: detailed service-by-service operating handbooks,
- Sagamihara: separation of operating handbook and self-check materials,
- Nagoya: practical handbook structure with related Q&A,
- Sapporo / Saitama: check sheets and self-inspection-oriented materials,
- Kawasaki / Yokohama: independently searchable or separately maintained Q&A resources.

Municipal-specific ordinances, local interpretations, forms, or administrative practices must not be presented as national requirements.

A future municipal-difference layer may be added, but it should remain separate from the national baseline.

## 5. Source hierarchy and evidence boundary

For the national baseline, primary national materials remain the authority.

Typical source layers include:

- Act on Long-Term Care Insurance,
- ministerial ordinances,
- fee schedules and delegated notifications,
- interpretation notices,
- administrative communications,
- national Q&A,
- official forms / manuals where they have relevant normative or interpretive value.

The product should retain source identity, version / date information, locators, and verification receipts so a user can trace a displayed statement back to its evidence.

Municipal materials may be recorded as secondary references for coverage analysis, but should not promote a national rule to a verified state.

## 6. Proposed information architecture

Existing public entry points should remain important:

- `/databases`: database overview,
- `/databases/search`: cross-database search,
- `/qa`: Q&A database,
- `/services`: service catalog.

A future service page can expose two distinct views without duplicating underlying data:

- a structured database view for inspection,
- a handbook view for practical reading.

Possible route shape, subject to implementation review:

- `/services/[service]`: service overview,
- `/services/[service]/handbook`: handbook,
- existing database detail routes: evidence / record inspection.

The exact routes are less important than preserving the separation between structured evidence and explanatory presentation.

## 7. Data model implications

The next design step should make the boundary between evidence and presentation explicit.

The structured data should support at least the following entities or equivalent concepts:

- source document,
- source version / amendment event,
- source locator,
- rule or requirement record,
- service applicability,
- topic / category,
- relation between source layers,
- verification receipt,
- currentness receipt,
- human-review state,
- Q&A item,
- handbook section,
- relation from handbook statement to rule records.

A handbook statement should normally reference existing rule records rather than duplicate source text.

This makes it possible to update a source, invalidate stale verification, and expose the same change consistently in the database, handbook, and Q&A relationships.

## 8. Publication safety

The existing fail-closed approach should continue.

A database record may exist before it is safe to present as a settled handbook statement.

The publication layer therefore needs to distinguish at least:

- collected,
- structurally validated,
- item-body verified,
- currentness established,
- human reviewed where required,
- publishable as evidence,
- publishable as explanatory handbook content.

These states should not be collapsed into a single "verified" label.

## 9. What should be designed next

The next design work should focus on four concrete decisions.

### A. Canonical unit of a rule

Decide what the smallest reusable rule record is.

It must be granular enough to connect one requirement to exact source evidence, but not so granular that the handbook becomes a direct rendering of sentence fragments.

### B. Handbook authoring model

Decide which content is:

- generated deterministically from structured data,
- authored manually,
- generated as a draft and then reviewed.

The preferred direction is to keep legal facts and evidence generated from structured data, while allowing human-authored explanatory text that references stable rule IDs.

### C. Topic taxonomy

Create a service-independent topic structure that can support:

- database filters,
- handbook section ordering,
- Q&A classification,
- cross-service comparison.

It should be broad enough for all service types, with service-specific subtopics where necessary.

### D. Currentness and version display

Define how the UI communicates:

- source date,
- effective date,
- last checked date,
- currentness status,
- superseded / historical material,
- unresolved gaps.

This must remain understandable to ordinary operators without weakening the underlying evidence model.

## 10. Product definition

A concise product definition is:

> A nationwide long-term care operations handbook backed by a traceable national-source database and searchable Q&A corpus.

The database is not a secondary developer surface. It is one of the product's main public outputs.

The handbook should make the database understandable.

The Q&A search should make it easy to reach the relevant part of the database from a practical question.

All three should remain connected to the same evidence chain.


## 11. Delivery priority: complete the database before handbook expansion

The immediate product priority is database completion.

Handbook implementation should not become the main workstream until the national-source database has substantially complete service breadth and the remaining verification gaps are reduced to an explicitly bounded set.

Near-term work should therefore prioritize:

1. registering the remaining service categories in the service catalog,
2. establishing service-specific scopes for the major national source layers,
3. ingesting missing ordinance / notice / remuneration / fee-guidance layers,
4. completing item-body verification,
5. establishing currentness where primary evidence permits,
6. resolving or explicitly bounding relation gaps,
7. preserving human-review state separately,
8. exposing all structured records through the database views even when publication status is limited.

The handbook remains an intended presentation layer, but database breadth, traceability, and verification take precedence.


## 12. Definition of database completion

Database completion should not be defined as "every record is fully human-verified and currentness-established."

That standard would make completion depend on whether every national source can be conclusively reconstructed, even when official publication practices leave unavoidable gaps.

Instead, the database can be considered structurally complete when all of the following are true:

1. all in-scope long-term care service categories are represented in the service catalog,
2. every service has an explicit scope for the major national source layers,
3. every expected source layer is represented by either structured data or an explicit bounded absence / unresolved state,
4. source identity, source version, locator, service applicability, and verification state are retained,
5. item-body verification, currentness, relation verification, human review, and publication state remain separate dimensions,
6. unresolved gaps are represented explicitly rather than disappearing as missing data,
7. public database views can enumerate and search the structured records that are safe to expose,
8. major upstream national sources have freshness / drift monitoring where practical,
9. source changes invalidate or flag stale downstream verification instead of silently preserving prior confidence,
10. the remaining unresolved set is measurable and bounded.

Examples of explicit non-complete states that are still valid database records include:

- `NOT_INGESTED`,
- `SOURCE_NOT_FOUND`,
- `HISTORICAL_SOURCE_ONLY`,
- `CURRENTNESS_NOT_ESTABLISHED`,
- `PARTIAL`,
- `HUMAN_REVIEW_PENDING`,
- `PUBLICATION_BLOCKED`.

A database that faithfully represents these states may be complete as a database even when the underlying legal evidence cannot yet support a stronger conclusion.

This distinction is important:

- **database completeness** means the expected domain is represented and gaps are explicit,
- **evidence completeness** means the required primary evidence exists for a given record,
- **verification completeness** means the relevant verification stages have passed,
- **human-review completeness** means the required human review is finished,
- **publication readiness** means the record is safe to expose in the intended user-facing context.

These dimensions must not be collapsed into a single completion percentage.

## 13. Coverage matrix as the main completion control

The next major control artifact should be a cross-service coverage matrix.

Rows should represent all in-scope services. Columns should represent the major national source layers.

At minimum, the matrix should cover:

- Long-Term Care Insurance Act / service identity,
- governing ministerial ordinance,
- standards interpretation notice,
- remuneration notification,
- delegated remuneration criteria,
- fee-calculation guidance,
- unit price / regional classification where applicable,
- national Q&A,
- related national forms / manuals when they materially affect interpretation.

Each service × layer cell should report a machine-readable state such as:

- scope defined / not defined,
- source located / not located,
- ingestion complete / partial / not started,
- item-body verification state,
- currentness state,
- relation verification state,
- human-review state,
- publication state,
- route / UI exposure state.

The matrix should be generated from repository state where possible rather than manually maintained as a separate truth source.

Its purposes are:

1. make the remaining database gaps visible,
2. prevent deep work on one service from hiding broad service coverage gaps,
3. support parallel work allocation,
4. define when database completion has been reached,
5. provide a stable input for later handbook generation.

The matrix itself should not promote any verification state. It is a projection of canonical service configs, verification receipts, and registries.

## 14. Current state snapshot and execution order

As of the 2026-10-03 repository state used when this note was updated:

- the service catalog contains 13 services,
- one service is `ACTIVE_MVP`,
- one service is `ACTIVE_PREVIEW`,
- eleven services are `PARTIAL_INGESTION`,
- the national Q&A corpus contains 3,695 classified rows and has an independent reparse PASS,
- the product snapshot reports 188 tracked relations, of which 129 are independently verified and 59 remain unverified,
- several service-specific standards-interpretation datasets now have item-body PASS, but currentness remains unestablished for multiple services,
- preventive-support still contains two PARTIAL item-body records in the current bounded scope.

These are a dated snapshot, not a permanent status source. Current status must continue to be read from the repository registries and receipts.

The preferred execution order is:

1. enumerate the full in-scope service universe,
2. add missing service descriptors to the service catalog,
3. generate the service × source-layer coverage matrix,
4. define missing scopes,
5. ingest missing source layers,
6. perform item-body verification,
7. establish currentness where the primary-source record supports it,
8. resolve or explicitly bound relation gaps,
9. add source-drift monitoring,
10. complete human review where required for publication,
11. expose the complete structured database through browse and search,
12. only then make handbook expansion a primary workstream.

The key operating rule is breadth first, then depth against the visible gaps.

Deep verification work remains necessary, but it should be prioritized from the coverage matrix so that the project converges toward a complete cross-service database rather than a small number of exceptionally deep service silos.


## 15. Prefer shared national corpora over per-service duplication

The database completion plan should avoid rebuilding the same national legal text separately for each service when an authoritative structured source can be maintained once and reused safely.

For source families that are naturally shared across services, the preferred model is:

1. ingest and validate one shared national corpus,
2. retain stable source-node identifiers,
3. define service-specific applicability as scope and relations,
4. add service-specific verification only where the applicability or interpretation itself requires verification.

This applies especially to structured or structurally obtainable national materials such as:

- the Long-Term Care Insurance Act,
- governing ministerial ordinances,
- major notifications / fee schedules where a shared corpus is practical,
- the national Q&A corpus,
- shared source registries and amendment metadata.

The service-specific unit should therefore usually be the applicability mapping, not a copied source text.

A service layer should answer questions such as:

- which Act provisions define or govern the service,
- which ordinance articles apply directly,
- which provisions apply by reference,
- what substitutions or reading rules apply,
- which notice sections interpret those provisions,
- which remuneration provisions apply,
- which Q&A classifications or individual Q&A items apply,
- what currentness or verification status is established for those relations.

This model is preferable to re-ingesting the same legal corpus for each service because a national-source update can be handled once while preserving service-specific scope and downstream invalidation.

## 16. Distinguish corpus availability from service coverage

The coverage matrix should distinguish whether the underlying corpus already exists from whether a service has been mapped onto it.

A missing service layer must not automatically be interpreted as missing source data.

At minimum, shared-source coverage should distinguish states equivalent to:

- `SHARED_CORPUS_AVAILABLE`,
- `SERVICE_SCOPE_DEFINED`,
- `SERVICE_SCOPE_PARTIAL`,
- `SERVICE_SCOPE_NOT_DEFINED`,
- `SERVICE_RELATIONS_VERIFIED`,
- `SERVICE_RELATIONS_PENDING`,
- `SERVICE_SPECIFIC_DATA_INGESTED`,
- `SERVICE_SPECIFIC_DATA_NOT_INGESTED`.

This distinction changes how remaining work is estimated.

For example, adding a new service should not require re-fetching or duplicating the entire Long-Term Care Insurance Act, a shared ministerial-ordinance corpus, or the national Q&A workbook if those corpora already exist. The work may instead consist mainly of:

1. adding the service descriptor,
2. defining applicable source-node scope,
3. defining direct, referenced, and substituted relations,
4. linking the relevant Q&A classification,
5. ingesting genuinely service-specific notice / remuneration / guidance data,
6. independently verifying the service-specific applicability and currentness boundaries.

## 17. Where service-by-service deep work remains necessary

Shared corpora do not remove the need for service-specific verification.

Deep service-by-service work remains appropriate where the evidence itself is service-specific or where applicability cannot be established by a simple structural selection.

This includes, in particular:

- standards interpretation notices,
- service sections of remuneration notifications,
- fee-calculation guidance,
- amendment reconstruction,
- incorporation by reference,
- substitution / reading rules,
- cross-layer relations,
- service-specific currentness,
- practical applicability of national Q&A.

The project should therefore use two complementary work modes:

### Shared-corpus work

Build and maintain reusable national corpora once.

### Service-applicability work

Map, verify, and version the way each service uses those shared corpora, then add genuinely service-specific sources.

The completion program should maximize the first mode before repeating work in the second.

## 18. Revised completion sequence

Given the shared-corpus strategy, the preferred database-completion sequence is refined to:

1. enumerate the complete in-scope service universe,
2. inventory which national source families can be maintained as shared corpora,
3. complete or expand those shared corpora first,
4. register all service descriptors,
5. generate the coverage matrix with corpus-availability and service-scope states separated,
6. define service applicability for the shared legal corpora,
7. ingest genuinely service-specific interpretation / remuneration / guidance layers,
8. verify service-specific applicability and item-body evidence,
9. establish currentness where the primary evidence permits,
10. resolve or explicitly bound cross-layer relation gaps,
11. add freshness / drift monitoring,
12. complete required human review and public database exposure.

The practical objective is to reduce service expansion from repeated source ingestion to a smaller and more auditable problem of applicability, relations, service-specific evidence, and currentness.
