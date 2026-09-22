# Information Retrieval Benchmark

作成日: 2026-09-22  
状態: **v0.15 outdoor service claim boundary complete**

## 現在のsuite

合計 **180ケース**。

- `benchmark-v0.15.json`: 50
- `coverage-gap-v0.1.json`: 20
- `false-answer-stress-v0.1.json`: 12
- `external-qa-query-sample-v0.4.json`: 33
- `claim-promotion-benchmark-v0.1.json`: 2
- `claim-routing-natural-language-v0.1.json`: 12
- `verified-claim-routing-probe-v0.1.json`: 28
- `multi-claim-routing-v0.1.json`: 5
- `important-matters-claim-routing-v0.1.json`: 3
- `municipal-query-sample-v0.3.json`: 15

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
- classifier checks: 181 / 181
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
- `node scripts/research-claim-registry-validate-v0.11.mjs`
- `node scripts/research-claim-registry-validate-v0.10.mjs`
- `node scripts/research-claim-registry-validate-v0.8.mjs`
- `node scripts/research-claim-registry-validate-v0.6.mjs`
- `node scripts/research-claim-compositions-validate-v0.2.mjs`
- `node scripts/research-claim-registry-validate-v0.2.mjs`
- `node scripts/research-claim-registry-validate-v0.3.mjs`

## 次の再開点

1. 理美容の提供者・資格境界を独立review
2. 訪問診療・訪問歯科を独立review
3. 別自治体のqueryを追加
4. human safety prose sign-off
5. source limitationのcurrent reconstruction
6. controlled RAG comparison

RAGはまだ実装しない。
