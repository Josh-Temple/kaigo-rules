# Shared ministerial standards corpora

Status: implementation / database foundation  
Scope: national primary-source ministerial standards

## Purpose

Ministerial standards are stored as reusable national source corpora. The official text is ingested once per law and services reference stable source node IDs through separate scope and relation data.

A shared corpus being available does **not** mean that a service is verified, current, human reviewed, or publishable.

## Current-law inventory

The shared layer contains the full MainProvision of nine current standards ordinances:

1. `411M50000100037` — 指定居宅サービス等の事業の人員、設備及び運営に関する基準
2. `418M60000100034` — 指定地域密着型サービスの事業の人員、設備及び運営に関する基準
3. `418M60000100035` — 指定介護予防サービス等の事業の人員、設備及び運営並びに指定介護予防サービス等に係る介護予防のための効果的な支援の方法に関する基準
4. `418M60000100036` — 指定地域密着型介護予防サービスの事業の人員、設備及び運営並びに指定地域密着型介護予防サービスに係る介護予防のための効果的な支援の方法に関する基準
5. `411M50000100038` — 指定居宅介護支援等の事業の人員及び運営に関する基準
6. `418M60000100037` — 指定介護予防支援等の事業の人員及び運営並びに指定介護予防支援等に係る介護予防のための効果的な支援の方法に関する基準
7. `411M50000100039` — 指定介護老人福祉施設の人員、設備及び運営に関する基準
8. `411M50000100040` — 介護老人保健施設の人員、施設及び設備並びに運営に関する基準
9. `430M60000100005` — 介護医療院の人員、施設及び設備並びに運営に関する基準

`411M50000100041`（指定介護療養型医療施設の基準）は廃止済みのため、current baselineには混在させず historical inventory に残す。

## Ordinance 37 compatibility

Existing IDs such as `ordinance37.article.93.p.1.i.1` remain unchanged.

Previously the generated Ordinance 37 corpus contained only the slices needed by dayservice, ordinary homevisit, and dayrehab. It is now generated from the full MainProvision. Existing `service_scope` / `applicable_via` fields in Ordinance 37 nodes remain only as compatibility metadata; they are not the canonical service-applicability layer.

All other shared standards corpora are source-only: source nodes contain no service-specific applicability fields.

## Separation of concerns

The data model keeps these dimensions separate:

- source corpus: official text, article/paragraph/item hierarchy, source version
- service scope: which source nodes a service selects
- relation: direct applicability, incorporation by reference, or application with substitution/read-as rules
- independent source verification: live e-Gov text and structural reparse
- source freshness: live e-Gov source/revision drift
- service applicability verification
- service-specific currentness
- human review
- publication / route exposure

No machine source PASS automatically promotes any downstream state.

## Existing service scopes

The generated service-relation projection reuses existing scopes for:

- dayservice
- homevisit
- dayrehab

For the other services currently registered on main, only the governing standards law family is recorded. Their article-level scope remains `SCOPE_NOT_DEFINED` until service-specific work establishes it.

The service-law-family map is intentionally limited to service IDs already present on main. IDs introduced by the parallel service-universe worker must be reconciled by the integrator rather than guessed here.

## Incorporation and read-as rules

`data/shared/standards/relation-model.json` defines three relation types:

- `direct_applicability`
- `incorporates_by_reference`
- `applies_with_substitution`

The source corpus validator checks that referenced source nodes exist. This is distinct from proving that the relation is legally applicable to the service.

Existing dayservice Article 105 and dayrehab Article 119 scope/read-as data are projected without copying the referenced legal text.

## Verification and freshness

The new corpora are generated from the e-Gov law-data API and independently reparsed with a different XML implementation. The independent audit covers official text, stable node structure, and containment only.

A separate freshness check compares live law XML, revision-response hash, revision count, and current revision metadata. Ordinance 37 continues to use the existing independent e-Gov audit and freshness lane.

## Remaining service-specific work

The shared corpus layer removes repeated source ingestion but does not complete service coverage. Remaining work includes:

- article-level scopes for services without an existing standards scope,
- independent verification of direct applicability,
- service-specific incorporation-by-reference relations,
- substitutions/read-as rules,
- service-specific currentness,
- human review and publication decisions.

Those unresolved states are deliberate and fail closed.

## Integrator reconciliation

The structural service-to-governing-standards map now covers all 39 current services from the completed service catalog. This mapping only selects the governing shared corpus; article-level service scope remains defined only where a service-specific scope exists, and every structural mapping remains NOT_SERVICE_VERIFIED.
