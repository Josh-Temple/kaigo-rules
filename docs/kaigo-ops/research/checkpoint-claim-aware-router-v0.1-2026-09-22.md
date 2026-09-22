# Kaigo Ops Research Checkpoint — Claim-aware Router v0.1

更新日: 2026-09-22  
状態: **claim-aware routing prototype implemented / regression preserved**

## 今回完了

Claim Registryを参照する `research-coverage-classifier-v0.4.mjs` を追加した。

従来コードへ直接書いていた以下のsubtopic boundaryを、Claim Registryの `routing.required_groups` / `routing.excluded_terms` へ移した。

- 管理者の具体的責務
- 生活相談員のサービス担当者会議時間
- 生活相談員の地域連携活動時間
- 生活相談員・介護職員の具体的人員配置
- 食堂・機能訓練室の複数室合算
- 災害時の定員例外

あわせて、報酬・加算・減算、地域区分・一単位単価にもrouting metadataを付与した。既存のcurrentness / review gateは安全側のため現時点では残している。

## 現在の判定経路

```text
query
 ↓
global scope/currentness gates
 ↓
Issue candidates
 ↓
Claim candidates
 ↓
explicit Claim routing metadata
 ↓
claim verification_status / answerability
 ↓
source relation
 ↓
Issue-level intent fallback（未移行部分のみ）
```

重要なのは、Claim候補のsimilarity rankingだけではANSWERにしないこと。

`similarity ≠ answerability` は維持している。

## Regression

- verified regression: 51 / 51
- coverage gap: 20 / 20
- false-ANSWER stress: 12 / 12
- external MHLW Q&A query: 15 / 15
- total: 98 / 98

記録:

`docs/kaigo-ops/research/issues/information-search/benchmark/claim-aware-router-eval-v0.1.json`

## Validator

Claim Registry schemaへoptionalな `routing` を追加した。

validatorでは、

- required_groupsが空でない
- 各groupに空でない文字列がある
- excluded_termsが文字列配列である

ことを確認する。

## まだ残っているhard-code

verified claimの多くはまだrouting metadataを持たず、既存のIssue-level intent signatureへfallbackする。

したがってv0.4は完全移行ではなく、**subtopic safety boundaryからClaim Registryへ移す最初のprototype**。

Issue-level intent signatureを一度に全廃すると、現在の51件のverified regressionを壊しやすいため段階移行とした。

## 次

1. candidate claimを1件以上、公式資料でreviewする
2. promotion flowを実地検証する
3. promotionしたclaimへrouting metadataを維持したままANSWERへ昇格できるか確認する
4. false abstentionを測る
5. verified claim側のrouting metadataを段階的に増やす
6. human sign-off
7. その後にRAG比較

RAGはまだ実装しない。
