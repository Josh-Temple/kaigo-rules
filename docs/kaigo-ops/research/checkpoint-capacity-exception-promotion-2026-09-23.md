# Kaigo Ops Research Checkpoint — Capacity Exception Claim Promotion

更新日: 2026-09-23  
状態: **capacity disaster exception promoted / remuneration boundary retained**

## Claim

`candidate.operation.capacity-disaster-exception`

## 一次資料

現行「指定居宅サービス等の事業の人員、設備及び運営に関する基準」
第102条。

規定:
- 利用定員を超えて指定通所介護を提供してはならない
- ただし、災害その他のやむを得ない事情がある場合はこの限りではない

current MHLW Q&A corpusにも、
この例外の趣旨と、真にやむを得ない事情かを個別に判断する取扱いが継続収載されている。

## Promotion

- CANDIDATE_UNREVIEWED → **VERIFIED_CURRENT**
- REVIEW_REQUIRED → **ANSWER**

## Boundary

このClaimで回答するのは
**運営基準上の定員遵守の例外**まで。

回答しない:
- 定員超過減算がいつ適用されるか
- 減算率・算定期間
- 報酬上の災害特例

これらは報酬告示・老企第36号側の未レビュー論点。

## Regression update

`external-qa-query-sample-v0.7.json`

- EQ-011: REVIEW_REQUIRED → ANSWER
- expected Claim: `candidate.operation.capacity-disaster-exception`

EQ-021 / EQ-023など、定員と報酬・複合運用を問う別queryはREVIEW_REQUIREDを維持。

## Current

- Claim Registry: `claims-v0.17.json`
- External sample: `external-qa-query-sample-v0.7.json`
- Classifier: `research-coverage-classifier-v0.25.mjs`
- Validator: `research-claim-registry-validate-v0.17.mjs`
- expected regression checks: 191
- actual execution: PENDING

classifierへ特例ルールは追加していない。
