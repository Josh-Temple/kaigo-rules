# Information Retrieval Benchmark

作成日: 2026-09-22  
状態: **Claim Registry v0.18 / corrected regression harness v0.26 / RAG deferred**

## 現在のsuite

合計 **190ケース**。

- `benchmark-v0.3.json`: 50
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
- `node scripts/research-coverage-classifier-v0.26.mjs`
- `node scripts/research-claim-registry-validate-v0.18.mjs`
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

## Controlled RAG comparison

比較条件は `controlled-rag-comparison-protocol-v0.1.md` と `controlled-rag-eval-contract-v0.1.json` に固定した。
RAG code / vector DB / embeddingはまだ導入していない。

## 次の再開点

1. new external holdout 30〜50件の作成
2. safety proseのhuman sign-off
3. 屋外サービス1件のcurrent integrated source reconstruction
4. gate通過後にcontrolled RAG comparisonを実装

`VERIFIED_WITH_SOURCE_LIMITATION` は現在1件のみ。
RAGはまだ実装しない。


## Controlled RAG external holdout

### Batch 1 — municipal / local boundary

- `rag-holdout-raw-v0.1.json`: raw 30 queries
- `rag-holdout-labeled-v0.1.json`: independent labels
- distribution: LOCAL 26 / OUT_OF_SCOPE 3 / REVIEW_REQUIRED 1

### Batch 2 — national MHLW Q&A

- `rag-holdout-national-raw-v0.1.json`: raw 20 queries
- `rag-holdout-national-labeled-v0.1.json`: independent labels
- distribution: REVIEW_REQUIRED 20

Combined 50-query holdout:
- ANSWER: 0
- PARTIAL: 0
- REVIEW_REQUIRED: 21
- LOCAL: 26
- OUT_OF_SCOPE: 3

この結果はretrieval failureではなく、current reviewed Claim coverageの不足を示す。
RAGはcoverage拡張より先に実装しない。

## Current Claim promotion

`claims-v0.16.json` で以下をANSWERへ昇格:

- 管理者の具体的責務
- 生活相談員の地域連携活動時間

external sampleは `external-qa-query-sample-v0.6.json`。
classifierは `research-coverage-classifier-v0.26.mjs`。

## Reproducibility

`research-coverage-classifier-v0.19.mjs`〜`v0.22.mjs` が自治体sample v0.4（15件）を読んでいた一方、checkpointはv0.5（25件）として191 checksを記録していた不整合を確認した。

`v0.23` 以降:
- municipal sample v0.5を使用
- suite cardinalityをfail closedで検査
- expected total checks = 191

GitHub Actions:
- `.github/workflows/verify-kaigo-ops-research.yml`
- classifier / Claim Registry / Composition Registryを検証
- Vercel deployとは独立

再実行結果を確認するまでは191/191を新規PASSとして扱わない。


## Claim coverage update — 2026-09-23

`claims-v0.18.json` で、生活相談員・介護職員の具体的人員配置を
PARTIAL / CANDIDATE_UNREVIEWED から ANSWER / VERIFIED_CURRENT へ昇格した。

- EQ-003: PARTIAL → ANSWER
- external sample: `external-qa-query-sample-v0.8.json`
- classifier: `research-coverage-classifier-v0.26.mjs`

現在:
- CANDIDATE_UNREVIEWED: 0
- PARTIAL: 0
- 残るREVIEW_REQUIREDは、報酬・単価・重要事項変更時同意・屋外時間境界・訪問診療等の5論点。
