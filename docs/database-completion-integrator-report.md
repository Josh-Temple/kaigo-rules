# Database Completion Integrator Report

Generated from the integrated coverage-matrix projection and canonical repository state on the integrator branch.

## Integrated result

- Current service universe: **39 services**
- National source families tracked by the coverage matrix: **9**
- Source families with reusable shared corpus available across all 39 services: **6**
  - Long-Term Care Insurance Act
  - governing standards ordinance family
  - remuneration notification
  - delegated remuneration criteria
  - unit price / regional classification
  - national Q&A
- Standards-interpretation service-specific ingestion: **13/39 services**
- Governing-standards article-level service scope: **3 defined / 36 not defined**
- Care Insurance Act service scope: **2 defined / 37 not defined**
- National Q&A direct individual-service mapping: **26 mapped / 13 without an individual Q&A code**
- Fully established currentness (`PASS`) across service × source-family cells: **0**
- Currentness gaps on ingested cells: **100**
- Item-body verification gaps on ingested cells: **12**
- Relation verification remaining: **59**
- Human review: **0 source-family cells promoted to human-review PASS; 39 services remain without completed cross-family human review**
- Public service exposure: **2 services have available service-specific publication/route surfaces in the projection; 37 services remain blocked from service-specific route exposure**
- Shared corpus available but service scope missing: **196 service × source-family cells**
- Genuinely missing corpus: **102 service × source-family cells**
- Publication gaps on ingested cells: **86**

## Design checks

The integration preserves these separations:

1. shared corpus availability is not service applicability;
2. service scope is not verification;
3. item-body verification is not currentness;
4. machine verification is not human review;
5. ingestion or verification does not enable publication or routes automatically;
6. the coverage matrix is a generated projection and is not a writable source of truth.

No new service route is enabled by this integration.

## Priority work remaining to complete the database

1. **Define missing service scope over reusable shared corpora.** The largest avoidable gap is 196 cells where the corpus exists but service scope does not. Governing standards are structurally mapped for all 39 services, but article-level scope is defined for only 3.
2. **Complete service-specific ingestion for the 26 newly registered services.** Standards interpretation, remuneration/guidance, service-specific currentness and related applicability work remain the main service-by-service workload.
3. **Establish currentness independently.** There are 100 currentness gaps on already ingested cells; machine ingestion or source-watch status must not be promoted to currentness PASS.
4. **Close the 59 remaining relation-verification items.** Keep semantic applicability, incorporation, delegation and read-as/substitution verification separate from source-corpus integrity.
5. **Complete human review after evidence/currentness gates.** No cross-family service is ready to be treated as fully human-reviewed.
6. **Expand genuinely missing corpora where materially required.** There are 102 missing corpus cells, concentrated in service-specific interpretation/guidance/manual families rather than the reusable Act/standards/Q&A foundations.
7. **Publish service-specific routes only after the above gates.** 37 services remain blocked from service-specific public exposure by design.

## Integrator decision

The A-E worker outputs are structurally reconcilable under the shared-corpus + service-scope/relation architecture. The combined-tree materializer independently re-ran the shared e-Gov corpus and relation verification lanes, regenerated dependent projections, and validated the integrated state successfully. Main merge remains gated on the final normal build check for the latest integrator HEAD.
