# Service-scope contract

Issue: #170 Integration Sprint A, task A2.

## Purpose

Service-facing runtime code must not infer applicability from corpus presence, Japanese labels, route shape, or verification state.

The canonical runtime question is:

> Is this committed record applicable to this explicit `service_id`, and what committed scope evidence establishes that applicability?

`lib/service-scope.ts` is the canonical helper for that question for the currently shared legal corpora.

## Contract

Every lookup is identified by:

- `service_id`
- `layer`
- `record_id`

The helper returns:

- whether the record is applicable to the requested service;
- the applicability basis for that service;
- every service for which committed scope evidence exists;
- whether the record is exclusive to one service or shared across multiple services.

Unknown services and records without committed scope evidence fail closed.

## Applicability bases

### Ordinance 37

For `dayservice`:

- `DIRECT_SCOPE`: article is in `data/ordinance37-scope.json#direct_articles`.
- `INCORPORATED_SCOPE`: article is in `data/ordinance37-scope.json#incorporated_articles`.

For `homevisit`:

- `DIRECT_SCOPE`: the exact node ID is present in `data/services/homevisit/ordinance37-index.generated.json`.

The exact node index is used for homevisit so a service never receives a child node merely because another node in the same article was selected.

### Care Insurance Act

For `dayservice`:

- `SERVICE_SCOPE`: the article is in `data/care-insurance-act-scope.json#articles`.

For `homevisit`:

- `SERVICE_DEFINITION_INDEX`: the exact node ID is in the homevisit service-definition index.
- `SHARED_CORE_INDEX`: the exact node ID is in the homevisit shared designated-home-service core index.

## Shared/common records

A shared/common record is represented explicitly by multiple service memberships.

Example:

- Ordinance 37 Article 10 is incorporated into dayservice through Article 105.
- The same Article 10 is a direct homevisit rule.

The helper therefore resolves the record with both memberships:

- `dayservice / INCORPORATED_SCOPE`
- `homevisit / DIRECT_SCOPE`
- `sharing = SHARED`

Shared status is never inferred from a missing service label and never means the legal applicability mechanism is the same for every service.

Likewise, the Care Insurance Act designated-home-service core can be shared while retaining distinct committed evidence for each service.

## Source-of-truth hierarchy

The contract derives applicability from committed scope/index evidence:

1. service-specific generated node indexes where they exist;
2. committed service/layer scope files;
3. service catalog only for validating whether a `service_id` is known.

It deliberately does **not** derive applicability from:

- `verification_status`;
- independent-audit PASS/HOLD state;
- currentness state;
- human-review state;
- publication/routing enablement;
- search text;
- display labels such as `service_scope`;
- guessed relations.

Those dimensions remain independent.

## Reuse

The same helper is intended to be called before:

- service-specific search matching;
- detail lookup and static-route generation;
- service-specific counts;
- related-record rendering.

A service-facing caller should filter/resolve scope before applying search ranking, counting, or relation display.

The underlying relation graph may remain global. The renderer is responsible for checking whether the source/target record is applicable to the selected service.

## Q&A and future layers

The current Q&A corpus already represents common scopes explicitly with source service codes such as all-service common and home-service common. A future Q&A adapter should translate those explicit codes into the same service-membership contract; absence of a service code must not mean "common to all".

New shared layers should add one adapter to the canonical helper rather than introducing page-local service predicates.

## Assurance boundary

This contract changes only applicability lookup.

It does not:

- promote homevisit to public routing;
- copy dayservice verification to homevisit;
- modify provenance;
- modify currentness;
- modify human-review state;
- modify publication gates.
