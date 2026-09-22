# Information Retrieval Benchmark

作成日: 2026-09-22  
状態: **v0.18 current-source reconstruction gate complete**

## 現在のsuite

合計 **190ケース**。

- `benchmark-v0.18.json`: 50
- `coverage-gap-v0.1.json`: 20
- `false-answer-stress-v0.1.json`: 12
- `external-qa-query-sample-v0.5.json`: 33
- `claim-promotion-benchmark-v0.1.json`: 2
- `claim-routing-natural-language-v0.1.json`: 12
- `verified-claim-routing-probe-v0.1.json`: 28
- `multi-claim-routing-v0.1.json`: 5
- `important-matters-claim-routing-v0.1.json`: 3
- `municipal-query-sample-v0.5.json`: 25

索引:

- `benchmark-v0.7.json`

## 主結果

### Known coverage

- Issue Hit@1: 92.3%
- Issue Hit@3: 100%
- direct source Complete@5: 82.1%
- linked-source complete: 100%

### Coverage / safety

- coverage gap: 20 / 20
- false-ANSWER stress: 12 / 12
- external MHLW Q&A label + Claim: 33 / 33
- claim promotion paraphrase: 2 / 2
- claim routing natural language: 12 / 12
- verified Claim routing: 28 / 28
- multi-claim routing: 5 / 5
- important matters Claim routing: 3 / 3
- external ANSWER expected Claim ID: 6 / 6
- municipal query label + provenance: 15 / 15
- verified regression Issue fallback: 0 / 51
- classifier checks baseline: 191 / 191
- verified regression: 51 / 51

### Safety prose

- research-session template review: 11 / 11 PASS
- human sign-off: PENDING

## 最重要の設計変更

Issue単位で `verified` とするだけでは粗い。

今後は:

```text
Issue
 ↓
Claim / Subtopic
 ↓
Review state
 ↓
Source
```

を正本にする方向。

例:

```text
生活相談員
 ├─ 基本配置                     VERIFIED
 ├─ 勤務時間基準                 VERIFIED
 ├─ サービス担当者会議の時間     UNREVIEWED
 └─ 地域連携活動の時間           UNREVIEWED
```

## 再現script

- `node scripts/research-issue-router-v0.1.mjs`
- `node scripts/research-coverage-classifier-v0.2.mjs`
- `node scripts/research-coverage-classifier-v0.3.mjs`
- `node scripts/research-coverage-classifier-v0.5.mjs`
- `node scripts/research-coverage-classifier-v0.6.mjs`
- `node scripts/research-coverage-classifier-v0.10.mjs`
- `node scripts/research-coverage-classifier-v0.11.mjs`
- `node scripts/research-coverage-classifier-v0.14.mjs`
- `node scripts/research-coverage-classifier-v0.16.mjs`
- `node scripts/research-coverage-classifier-v0.17.mjs`
- `node scripts/research-coverage-classifier-v0.19.mjs`
- `node scripts/research-coverage-classifier-v0.20.mjs`
- `node scripts/research-coverage-classifier-v0.21.mjs`
- `node scripts/research-claim-registry-validate-v0.14.mjs`
- `node scripts/research-claim-registry-validate-v0.13.mjs`
- `node scripts/research-claim-compositions-validate-v0.5.mjs`
- `node scripts/research-claim-registry-validate-v0.11.mjs`
- `node scripts/research-claim-registry-validate-v0.10.mjs`
- `node scripts/research-claim-registry-validate-v0.8.mjs`
- `node scripts/research-claim-registry-validate-v0.6.mjs`
- `node scripts/research-claim-compositions-validate-v0.2.mjs`
- `node scripts/research-claim-registry-validate-v0.2.mjs`
- `node scripts/research-claim-registry-validate-v0.3.mjs`

## 次の再開点

1. safety proseのhuman sign-off
2. 屋外サービス1件のcurrent integrated source reconstruction
3. controlled RAG comparison

`VERIFIED_WITH_SOURCE_LIMITATION` は現在1件のみ。
RAGはまだ実装しない。
