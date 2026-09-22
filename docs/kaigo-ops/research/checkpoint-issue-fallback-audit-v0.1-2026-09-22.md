# Kaigo Ops Research Checkpoint — Issue Fallback Audit

更新日: 2026-09-22  
状態: **safe fallback reduction complete / 8 intentional fallback cases remain**

## 今回の目的

Claim routingを増やすこと自体ではなく、Issue-level fallbackに残っている質問の理由を明示する。

## Fallback推移

- claims-v0.3: 51 / 51
- claims-v0.4: 17 / 51
- claims-v0.5: 8 / 51

claims-v0.5では、安全に単一Claimへ固定できる9件だけを追加routingした。

## 残る8件

### 複数Claim composition — 5件

- 看護職員の「ずっと事業所にいる必要があるか」
- 職員の複数職種兼務（2件）
- 通所介護計画の内容・説明・記録を一括で尋ねる質問
- 毎年必要な研修の一覧

これらは単一Claimへ押し込むべきではない。

次のrouterは、複数Claimを同時に採用してsource relationを維持できる必要がある。

### Claim coverage gap — 3件

- 重要事項説明書に国の固定様式・ひな形があるか（2件）
- 重要事項説明書に何を記載するかという広い質問

前者は「規定が存在しない」という解釈を含むため、routing追加だけでANSWER化しない。独立review後にVERIFIED_INTERPRETATION候補とする。

後者は、文書内容・開始前手続・掲示/ウェブ掲載が混在しているため、Claim coverageを分解して確認する。

## 現在の原則

`Issue fallback = 0` をKPIにしない。

目標は、

```text
single verified claim query
  → exact Claim

multi-claim query
  → multiple verified Claims

claim coverage gap
  → REVIEW_REQUIRED / review queue

ambiguous query
  → abstain
```

とする。

## Regression

claims-v0.5相当の事前再生では、既存140 checksをすべて維持した。

- 51 / 51 verified regression
- 20 / 20 coverage gap
- 12 / 12 false-ANSWER stress
- 15 / 15 external Q&A
- 2 / 2 promotion
- 12 / 12 natural-language routing
- 28 / 28 verified Claim routing

## 次

最優先はmulti-claim routing/output prototype。

重要事項説明書の固定様式claimについては、その後に公式資料を独立reviewする。

RAGはまだ実装しない。
