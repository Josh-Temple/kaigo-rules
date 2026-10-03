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
