# National Q&A service-code taxonomy and mapping audit

Status: worker artifact / integration handoff  
Worker: National Q&A Shared Corpus & Service Mapping Worker  
Branch: `db/qa-service-mapping`  
Fresh-read base main: `228a7fbbe8e8df025a37812e63b5569519dc0a5f`

## Purpose

This audit makes the existing MHLW Q&A corpus usable as a shared national source layer without copying Q&A bodies into service-specific datasets.

It separates:

- the Q&A workbook's service code,
- Kaigo Rules service identity,
- shared/common service-group scope,
- historical or special classifications,
- row-level qualifiers in the original workbook label,
- verification/currentness/human-review state.

The mapping is not a new source of legal applicability. It is a machine-readable relation layer over the committed Q&A corpus.

## Source and corpus boundary

The committed source is the MHLW 介護サービス関係Q&A workbook recorded in:

- `data/qa-corpus-meta.json`
- `data/qa-corpus.json`
- `data/qa-corpus-independent-audit.json`

At the fresh-read base:

- corpus rows: 3,695
- observed service codes: 36
- independent corpus reparse: PASS
- source freshness monitoring: active
- human review: not promoted by this work
- currentness: not promoted by this work

This worker does not change Q&A question/answer text, source provenance, workbook hash, or existing Q&A IDs.

## Taxonomy

The 36 observed codes are classified as follows.

| Classification | Codes | Count |
| --- | --- | ---: |
| Individual service | 11–25 except 26, 40–49, XX | 26 |
| Shared/common category | 01, 02, 03, 04, 05, 06 | 6 |
| Historical/abolished service | 26 | 1 |
| Remuneration-only theme | 50 | 1 |
| Other/special | 27, 51 | 2 |

Code 26 (介護療養型医療施設) is kept outside the current-service mapping so historical Q&A remains searchable without implying a current service.

Code 27 (住宅改修) and code 51 (介護予防・日常生活支援総合事業) are retained as special classifications rather than forced into an individual-service ID.

Code 50 is a cross-service remuneration theme, not a service identity.

`XX` is mapped to the existing `preventive-support` service because the committed workbook metadata identifies it as 介護予防支援 and that service ID already exists in the current catalog.

## Existing Kaigo Rules service mappings

The 13 service IDs already present in the fresh-read catalog map directly as follows.

| Q&A code | Official Q&A label | service_id |
| --- | --- | --- |
| 11 | 訪問介護事業 | homevisit |
| 12 | 訪問入浴介護事業 | homebath |
| 13 | 訪問看護事業 | homenursing |
| 14 | 訪問リハビリテーション事業 | homerehab |
| 15 | 居宅療養管理指導事業 | homecaremanagement |
| 16 | 通所介護事業 | dayservice |
| 17 | 通所リハビリテーション事業 | dayrehab |
| 18 | 短期入所生活介護事業 | shortstay-life |
| 23 | 居宅介護支援事業 | care-management |
| 40 | 定期巡回・随時対応型訪問介護看護事業 | regular-round |
| 41 | 夜間対応型訪問介護事業 | night-homevisit |
| 48 | 地域密着型通所介護事業 | community-dayservice |
| XX | 介護予防支援 | preventive-support |

No existing service ID is renamed.

## Pending mappings for the parallel service-catalog worker

The following 13 individual-service codes are not in the fresh-read catalog. This worker intentionally does not invent stable IDs.

| Q&A code | Official Q&A label | Mapping state |
| --- | --- | --- |
| 19 | 短期入所療養介護事業 | PENDING_PARALLEL_SERVICE_CATALOG |
| 20 | 特定施設入居者生活介護事業 | PENDING_PARALLEL_SERVICE_CATALOG |
| 21 | 福祉用具貸与事業 | PENDING_PARALLEL_SERVICE_CATALOG |
| 22 | 特定福祉用具販売事業 | PENDING_PARALLEL_SERVICE_CATALOG |
| 24 | 介護老人福祉施設 | PENDING_PARALLEL_SERVICE_CATALOG |
| 25 | 介護老人保健施設 | PENDING_PARALLEL_SERVICE_CATALOG |
| 42 | 認知症対応型通所介護事業 | PENDING_PARALLEL_SERVICE_CATALOG |
| 43 | 小規模多機能型居宅介護事業 | PENDING_PARALLEL_SERVICE_CATALOG |
| 44 | 認知症対応型共同生活介護事業 | PENDING_PARALLEL_SERVICE_CATALOG |
| 45 | 地域密着型特定施設入居者生活介護事業 | PENDING_PARALLEL_SERVICE_CATALOG |
| 46 | 地域密着型介護老人福祉施設 | PENDING_PARALLEL_SERVICE_CATALOG |
| 47 | 看護小規模多機能型居宅介護 | PENDING_PARALLEL_SERVICE_CATALOG |
| 49 | 介護医療院 | PENDING_PARALLEL_SERVICE_CATALOG |

`data/qa-service-mapping.json` carries the MHLW code and official label as the proposed matching key. The Integrator must replace each pending state with the exact stable `service_id` produced by Chat A, then regenerate/revalidate the combined state.

## Shared-category relations

The shared categories are represented as group relations:

| Q&A code | Q&A category | group_id |
| --- | --- | --- |
| 01 | 全サービス共通 | qa.shared.all-services |
| 02 | 居宅サービス共通 | qa.shared.home-services |
| 03 | 施設サービス共通 | qa.shared.facility-services |
| 04 | 地域密着型サービス共通 | qa.shared.community-based-services |
| 05 | 訪問系サービス共通 | qa.shared.visit-services |
| 06 | 通所系サービス共通 | qa.shared.day-services |

This worker does not enumerate group membership and does not create per-service copies of shared Q&A rows. Membership must be resolved from explicit service/group metadata after the full service catalog is integrated.

## Row-level qualifiers and fail-closed handling

The primary `service_code` is not sufficient to infer every row's exact applicability.

In the committed 3,695-row corpus, 297 rows have a raw `service_label` that differs from the canonical label for their primary code. Examples include:

- code 01 rows that say “全サービス共通” but explicitly exclude named services,
- shared/common rows that also mention code 50,
- composite service labels,
- historical naming for code 47.

For those rows, `data/qa-service-mapping.json` preserves the raw-label variants and marks the policy:

`PRESERVE_RAW_LABEL_AND_DO_NOT_AUTO_EXPAND_WITHOUT_EXPLICIT_ROW_SCOPE_RESOLUTION`

Therefore a future service search must not obtain a shared Q&A merely because the primary category appears broad when the row's original label narrows or combines the scope.

This is intentionally fail-closed. A later row-scope parser or reviewed mapping may make the relation more specific, but this worker does not infer it.

## Query contract

A future all-service Q&A search can use this mapping under the following rules.

1. Individual-service code: use the exact service-code relation once its catalog mapping is resolved.
2. Shared/common category: resolve through explicit group membership; do not duplicate Q&A rows.
3. Qualified raw label: preserve the qualifier and do not auto-expand until explicit row-scope resolution exists.
4. `current_service_scope`: preserve it as source data; it does not overwrite the primary service code automatically.
5. Historical/special/theme classifications: expose through separate taxonomy facets; do not attach them to current services automatically.

## Validation

`scripts/validate_qa_service_mapping.py` checks:

- complete one-to-one coverage of all 36 committed Q&A service codes,
- code/label/count agreement with `qa-corpus-meta.json`,
- exact existing service-ID mappings,
- unresolved status for parallel-catalog services,
- shared categories remain group relations,
- historical/special/theme classifications remain separate,
- row-label variants remain accounted for,
- manifest/catalog compatibility,
- no implicit verification/currentness promotion.

`tests/test_qa_service_mapping.py` covers the same safety invariants and runs under the repository's existing Python unittest discovery.

## Integration handoff

After Chat A is available, the Database Completion Integrator should:

1. compare Chat A's complete service catalog with the 13 pending individual Q&A codes,
2. use the exact stable IDs chosen by Chat A,
3. update only the pending mapping entries and catalog snapshot,
4. define service-group membership in an explicit shared relation layer if Chat A/C provides the required classification metadata,
5. rerun `python scripts/validate_qa_service_mapping.py` and the full `npm run validate:data`,
6. retain historical/special/theme rows outside individual current-service mappings,
7. keep verification, currentness, human review, and publication state unchanged unless independently established.

