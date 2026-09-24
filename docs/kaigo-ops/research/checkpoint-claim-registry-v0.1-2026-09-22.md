# Kaigo Ops Research Checkpoint — Claim Registry v0.1

更新日: 2026-09-22  
状態: **claim-level coverage model seeded / paused before claim-aware router**

## 今回完了

External-query benchmarkで確認した、

> Issue単位のverifiedでは細かすぎる境界を表現できない

という問題に対し、claim registry v0.1を作成した。

## Claim registry

`docs/kaigo-ops/research/claims/claims-v0.1.json`

36 claims:

- VERIFIED_CURRENT: 20
- VERIFIED_WITH_SOURCE_LIMITATION: 4
- VERIFIED_SOURCE_TEXT: 2
- VERIFIED_INTERPRETATION: 2
- CANDIDATE_UNREVIEWED: 6
- REVIEW_REQUIRED: 2

Answerability:

- ANSWER: 28
- PARTIAL: 1
- REVIEW_REQUIRED: 7

validator:

**valid = true / errors = 0**

## 何をclaim化したか

### Verified

- 管理者の兼務
- 生活相談員の基本配置
- 看護職員の基本配置
- 看護職員の外部連携
- 介護職員の他単位兼務
- 機能訓練指導員の他職務
- 勤務表
- 食堂・機能訓練室の基本面積
- 同一場所利用
- 運営規程
- 重要事項の事前説明
- 掲示・ウェブ掲載
- 事故・苦情体制
- 通所介護計画
- 署名・押印
- 電磁的方法
- BCP
- 感染症
- 虐待防止

等。

### Unreviewed / review required

- 管理者の具体的責務
- 生活相談員のサービス担当者会議時間
- 生活相談員の地域連携活動時間
- 生活相談員 + 介護職員の詳細配置
- 食堂・機能訓練室の複数室合算
- 災害時の定員例外
- 報酬・加算
- 地域区分・一単位単価

## 原則

```text
Issue verified
  ≠
Issue配下の全claim verified
```

最終回答ではclaim単位のstatusを使う。

## Promotion flow

`claim-promotion-flow.md`

```text
candidate Q&A / source
 ↓
subtopic identification
 ↓
current official source check
 ↓
claim statement固定
 ↓
boundary固定
 ↓
review
 ↓
benchmark追加
 ↓
VERIFIED
```

candidateを検索で見つけただけでは昇格させない。

## Source limitationもclaim側に保持

例:

BCP年1回以上は、
基準省令本文の「定期的」ではなく
解釈通知の改正後文に基づく。

そのため、

`VERIFIED_WITH_SOURCE_LIMITATION`

として保持。

回答文を短くしても、
provenance layerではこの差を失わない。

## 次に実装するもの

### Claim-aware router

現在:

```text
query
 ↓
Issue
 ↓
hard-coded subtopic boundary
```

次:

```text
query
 ↓
Issue candidate
 ↓
Claim candidate
 ↓
claim verification status
 ↓
source expansion
 ↓
answerability
```

subtopic例外をコードへ増やし続けず、
claim registryへ寄せる。

## RAG

まだ不要。

claim registryがない状態でRAGを導入すると、
未レビューQ&Aを検索できる能力だけが上がり、
answerability判断は改善しない。

## 次回の再開点

1. claim-aware router prototype
2. hard-coded boundaryをclaim dataへ移す
3. external Q&A 15件で再評価
4. candidate claimを1〜2件実際にreviewしてpromotion flowを試す
5. human sign-off
6. その後RAG比較

## Pause condition

- external-query test
- subtopic boundary
- 36-claim registry
- schema
- promotion flow
- validator

まで揃った。

次回はclaim-aware routerから再開できる。
