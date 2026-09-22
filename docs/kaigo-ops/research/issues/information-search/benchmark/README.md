# Information Retrieval Benchmark

作成日: 2026-09-22  
状態: **v0.10 multi-claim composition gate complete**

## 現在のsuite

合計 **144ケース**。

- `benchmark-v0.10.json`: 50
- `coverage-gap-v0.1.json`: 20
- `false-answer-stress-v0.1.json`: 12
- `external-qa-query-sample-v0.2.json`: 15
- `claim-promotion-benchmark-v0.1.json`: 2
- `claim-routing-natural-language-v0.1.json`: 12
- `verified-claim-routing-probe-v0.1.json`: 28
- `multi-claim-routing-v0.1.json`: 5

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
- external MHLW Q&A query sample: 15 / 15
- claim promotion paraphrase: 2 / 2
- claim routing natural language: 12 / 12
- verified Claim routing: 28 / 28
- multi-claim routing: 5 / 5
- classifier checks: 145 / 145
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
- `node scripts/research-claim-compositions-validate-v0.2.mjs`
- `node scripts/research-claim-registry-validate-v0.2.mjs`
- `node scripts/research-claim-registry-validate-v0.3.mjs`

## 次の再開点

1. 重要事項説明書の固定様式・ひな形claimを独立review
2. 重要事項説明書の記載内容coverageをClaim単位で分解
3. 残るIssue fallback 3件を、根拠が揃う場合だけ解消
4. 外部queryで自然言語testを拡張
5. human sign-off
6. RAG comparison

RAGはまだ実装しない。
