# AI context package contract

Updated: 2026-09-25

Kaigo Rules exposes curated, machine-readable context packages derived from the same structured information used by the public site.

## Purpose

The package is not a second answer database and is not a free-form RAG dump.

It gives an AI or another program a bounded set of material for one practical question:

- the curated question and current answer text;
- directly cited ordinance nodes;
- directly cited interpretation-notice nodes;
- directly cited MHLW Q&A items;
- first-party source references;
- the semantic relations that connect the question to those nodes;
- assurance metadata that keeps content verification and relation verification separate.

## Generated source

`data/context-packages/dayservice-questions.generated.json`

is generated from existing canonical inputs by:

`scripts/build_question_context_packages.py`

Do not edit the generated file manually.

CI runs the builder in `--check` mode and fails if the package is stale.

## Retrieval API

Current route:

`GET /api/context/services/{service_id}/questions/{slug}`

Example:

`/api/context/services/dayservice/questions/nurse-staffing`

The service is part of the route so future services do not require a new API shape.

## Assurance rules

A package must not collapse these concepts:

1. question content status;
2. source/node verification status;
3. semantic relation independent-audit status;
4. source currentness.

For example, a curated FAQ may be marked `verified` because its direct sources were checked while the semantic edge `question -> ordinance node` is still `NOT_AUDITED` as an independently reconstructed graph relation. The package must preserve that distinction.

Current package generation does not promote any relation.

## AI use policy

Consumers should:

- prefer the direct evidence bundled with the package;
- use relation edges for navigation and retrieval expansion, not as proof when `NOT_AUDITED`;
- preserve cautions and scope constraints;
- avoid extending a legal conclusion beyond the bundled evidence without retrieving additional verified material;
- return users to first-party sources for consequential decisions.

## Expansion

Future context packages may be produced for:

- a rule article;
- a remuneration item;
- a provider-opening task;
- a cross-service comparison;
- an amendment impact set.

They should reuse the same service-aware route and assurance principles rather than introducing an unrelated AI-only knowledge store.
