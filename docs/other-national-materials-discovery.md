# Other National Manuals / Forms — discovery foundation

Observed against main at 754bc7b223db4aa35675c840f1a0032ca71eeb96 on 2026-10-04.

## Purpose

other_national_manuals_forms is a residual source family, not a catch-all. A candidate belongs here only when it is an official national primary source with material operational or administrative relevance to long-term-care services and it is not already contained by the eight established source families.

This wave creates discovery and classification evidence only. It does not make the shared corpus available, define any of the 39 service scopes, ingest document bodies, establish currentness, complete verification or human review, permit publication, or enable routes.

## Included candidate classes

Examples accepted for further corpus work are nationwide designation/application standard forms, the national electronic application/notification system operator manual, the national accident-reporting format, and the care-service-provider financial-information database operator manual.

A source being national does not imply applicability to every service. Every candidate remains applicability.state = NOT_ESTABLISHED until service-specific evidence is reviewed.

## Deduplication boundary

Materials structurally belonging to an established family are not duplicated here. This inventory classifies fee filing guidance/forms under fee_calculation_guidance, forms annexed to standards interpretation notices under standards_interpretation_notice, and system Q&A under national_qa.

Official index or landing pages may be used as discovery evidence, but a changing index is not treated as a bounded canonical source document by itself.

## Currentness and provenance

All listed candidates retain currentness_state = NOT_ESTABLISHED. Current landing pages were observed, but raw attachment bytes and amendment/supersession chains were not pinned in this discovery wave. OFFICIAL_SOURCE_LOCATED_NOT_SNAPSHOTTED is therefore preserved rather than inferring currentness from discoverability.

## Files

- data/shared/other-national-materials/manifest.json — machine-readable inclusion/exclusion and fail-closed policy.
- data/shared/other-national-materials/source-registry.json — source identity, official URL, locator, classification, overlap and assurance state.
- data/shared/other-national-materials/classification-audit.json — one-row-per-candidate dedup/classification audit and counts.
- scripts/validate_other_national_materials.py — schema, official-host, dedup, applicability and no-promotion validation.
- tests/test_other_national_materials.py — regression coverage.

The global database coverage matrix is intentionally untouched in Worker D. Projection changes belong to the integrator after source acceptance and mapping decisions are independently reviewed.
