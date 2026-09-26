# Multi-service architecture

Kaigo Rules must scale by adding service definitions and service-specific scope, not by copying the whole application or verification pipeline per service.

## Invariants

1. `data/services/manifest.json` is the service registry. Keep it small.
2. Each service owns one isolated config at `data/services/<service_id>.json`.
3. Shared legal sources are stored once. Service configs point to service-specific scope definitions.
4. Existing IDs and legacy routes remain stable unless an explicit migration is approved.
5. Verification dimensions remain separate:
   - content reconstruction / independent audit
   - currentness / source freshness
   - human review
6. A service is not public merely because its scope exists.
7. A service must not inherit verification coverage from another service unless the verification evidence actually covers it.
8. Do not copy workflows per service when a shared workflow can consume service metadata.
9. Do not generalize a special reconstruction pipeline until at least two real services prove that the duplicated behavior is actually common.

## Adding a service

A new service begins as a non-public descriptor:

1. Add one descriptor to `data/services/manifest.json`.
2. Add `data/services/<service_id>.json`.
3. Add only the service-specific scope files needed to identify the relevant parts of shared sources.
4. Keep `future_service_base_enabled=false`.
5. Keep `verification_layer_ids=[]` until independent evidence for that service exists.
6. Run the full validation/build suite.
7. Add ingestion and independent verification in separate changes.
8. Enable public routes only after the publication gate is intentionally satisfied.

## Verification extension

Existing verification layers remain compatible with the current legacy builders.

New service-specific verification should prefer a normalized report provider declared in `data/services/verification-layers.json`. A normalized report must expose:

- `id`
- `title`
- `content_verification`
- `currentness`
- `monitoring`
- `human_review`
- `assurance`

This allows Verification Registry to ingest a new layer without adding a new service-specific branch to the registry builder.

## Runtime routing

Runtime service metadata is generated into `data/services/catalog.generated.json`.

Application code should use `lib/service-catalog.ts` for service lookup, route construction, and ID namespace handling. Avoid embedding strings such as `fee.dayservice.` in page logic.

The current default service keeps its legacy root URLs. Non-default services use reserved `/services/<service_id>` paths and fail closed until explicitly enabled.

## Current second-service probe: homevisit

`homevisit` is registered as `PARTIAL_INGESTION`.

Its initial scope defines:

- Care Insurance Act service definition and shared designated-home-service legal core
- Ordinance 37, Chapter 2, ordinary designated home-visit care
- Rouki 25, Section 3
- Remuneration Notice 19, fee schedule item 1, plus identified shared delegated notices

Two shared-law ingestion steps are now complete.

- Care Insurance Act: `data/services/homevisit/care-insurance-act-index.generated.json` selects 106 existing node references.
- Ordinance 37: `data/services/homevisit/ordinance37-index.generated.json` selects 165 node references covering 38 ordinary homevisit articles in Chapter 2.

The Ordinance 37 shared corpus itself was expanded from 40 to 56 article nodes. The 16 newly added articles are homevisit-only within the current two-service scope; existing dayservice node semantics were preserved.

This does **not** mean the service is fully ingested or verified.

- service-specific independent verification: NOT_RUN
- service-specific currentness verification: NOT_RUN
- human review: NOT_RUN
- public routing: disabled
- Rouki 25: scope defined, not reconstructed
- remuneration: scope defined, not ingested

The purpose of this stage is to prove that a second real service can reuse and incrementally expand shared source corpora without copying the day-service implementation or overstating verification.
