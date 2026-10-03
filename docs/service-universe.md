# Service universe and catalog decisions

## Purpose

This record defines the service universe used by Kaigo Rules for cross-service database completion. The immediate goal is database completeness, not handbook authoring.

Registration alone does not imply ingestion, service applicability, currentness, verification, human review, publication readiness, or route exposure.

## Official basis

Primary references checked for this change:

- Long-Term Care Insurance Act, Article 8 and Article 8-2: https://www.mhlw.go.jp/web/t_doc?dataId=82998034&dataType=0&pageNo=1
- MHLW long-term care service explanation: https://www.kaigokensaku.mhlw.go.jp/commentary/service.html
- MHLW service-type overview: https://www.mhlw.go.jp/content/12301000/001544646.pdf
- MHLW management-information system manual: https://www.mhlw.go.jp/content/12300000/001470543.pdf
- MHLW notice on abolition of 介護療養型医療施設: https://www.mhlw.go.jp/web/t_doc?dataId=00tc8486&dataType=1&pageNo=1
- MHLW basic guideline on transfer of 介護予防訪問介護 and 介護予防通所介護 to the community support program: https://www.mhlw.go.jp/web/t_doc?dataId=00013180&dataType=0&pageNo=1

## Current service universe

The current catalog contains **39 services**: 12 home services, 9 community-based services, 1 care-management service, 3 facility services, 10 preventive services, 3 community-based preventive services, and 1 preventive-support service.

### Existing stable IDs retained

`dayservice`, `homevisit`, `homebath`, `homenursing`, `homerehab`, `homecaremanagement`, `dayrehab`, `shortstay-life`, `community-dayservice`, `regular-round`, `night-homevisit`, `care-management`, and `preventive-support`.

### Newly registered current services

- 短期入所療養介護 — `shortstay-medical`
- 特定施設入居者生活介護 — `specific-facility`
- 福祉用具貸与 — `welfare-equipment-rental`
- 特定福祉用具販売 — `specific-welfare-equipment-sale`
- 認知症対応型通所介護 — `dementia-dayservice`
- 小規模多機能型居宅介護 — `small-scale-multifunctional`
- 認知症対応型共同生活介護 — `dementia-group-home`
- 地域密着型特定施設入居者生活介護 — `community-specific-facility`
- 地域密着型介護老人福祉施設入所者生活介護 — `community-elderly-facility`
- 看護小規模多機能型居宅介護 — `nursing-small-scale-multifunctional`
- 介護老人福祉施設 — `elderly-welfare-facility`
- 介護老人保健施設 — `elderly-health-facility`
- 介護医療院 — `care-medical-institution`
- 介護予防訪問入浴介護 — `preventive-homebath`
- 介護予防訪問看護 — `preventive-homenursing`
- 介護予防訪問リハビリテーション — `preventive-homerehab`
- 介護予防居宅療養管理指導 — `preventive-homecaremanagement`
- 介護予防通所リハビリテーション — `preventive-dayrehab`
- 介護予防短期入所生活介護 — `preventive-shortstay-life`
- 介護予防短期入所療養介護 — `preventive-shortstay-medical`
- 介護予防特定施設入居者生活介護 — `preventive-specific-facility`
- 介護予防福祉用具貸与 — `preventive-welfare-equipment-rental`
- 特定介護予防福祉用具販売 — `specific-preventive-welfare-equipment-sale`
- 介護予防認知症対応型通所介護 — `preventive-dementia-dayservice`
- 介護予防小規模多機能型居宅介護 — `preventive-small-scale-multifunctional`
- 介護予防認知症対応型共同生活介護 — `preventive-dementia-group-home`

All 26 use `REGISTERED_NOT_INGESTED` and closed publication/routes.

## Historical services

Historical entries retain stable IDs but are outside the current 39-service list:

- `care-medical-facility` — 介護療養型医療施設; abolished after the transition period ended on 2024-03-31.
- `preventive-homevisit` — 介護予防訪問介護; preventive-benefit category transferred to the community support program.
- `preventive-dayservice` — 介護予防通所介護; preventive-benefit category transferred to the community support program.

Historical entries do not receive active service configs.

## Special categories

- `housing-renovation` — 居宅介護・介護予防住宅改修. Important insurance benefits, but not Article 8 / Article 8-2 service definitions.
- `community-support-program` — 介護予防・日常生活支援総合事業. A municipal program, not one nationally uniform current service.

These remain available for future Q&A and evidence mapping without being mixed into current services.

## Subtypes not assigned separate top-level IDs

Publication or operational subtypes are not promoted when the statute treats them as a subtype of a current service. Examples include 療養通所介護, external-service-use variants of 特定施設入居者生活介護, and facility-type variants of 短期入所療養介護.

## Stub semantics

Each new stub contains service identity, official service class, expected national source families, empty scopes, no verification-layer assignments, a disabled future route, and fail-closed publication gates.

The stub does not claim that a shared corpus is available or that service applicability/currentness has been established.

## Validation

The manifest validator now rejects duplicate service labels, config identity mismatches, current/historical mixing, malformed historical or special categories, and malformed `REGISTERED_NOT_INGESTED` stubs. The generated catalog check continues to detect manifest/config/catalog drift.
