# Kaigo Ops Research Checkpoint — Outdoor Service Claim Boundary

更新日: 2026-09-22  
状態: **outdoor service boundary complete / 181 checks PASS**

## 対象

自治体queryのうち、

- MQ-004: 外出レクリエーションを通所介護サービスとして実施できるか
- MQ-005: 外出レクリエーションはサービス提供時間の範囲に限られるか

を、厚生労働省の全国共通資料だけで独立reviewした。

## 確認できた全国ルール

指定通所介護は事業所内での提供が原則。

ただし、

1. あらかじめ通所介護計画に位置付けられていること
2. 効果的な機能訓練等のサービスを提供できること

の双方を満たす場合は、事業所の屋外でサービス提供が可能。

## 新規Claim

### claim.service.outdoor.conditions

`VERIFIED_WITH_SOURCE_LIMITATION / ANSWER`

「外出レクリエーション」という名称だけで一律に可とはしない。

回答可能な範囲は、

`計画への事前位置付け + 効果的な機能訓練等としての実質`

がある場合に屋外提供が可能、という条件付き命題。

現行解釈通知の統合全文をrepository内で完全再構成していないため、statusはSOURCE_TEXTではなくSOURCE_LIMITATION付きとする。

## 時間境界

### review.service.outdoor.time-boundary

`REVIEW_REQUIRED`

屋外提供の可否と、

「サービス提供時間のどの範囲で実施できるか」

は分ける。

保険外の個別外出支援では通所介護を中断する取扱いがあるが、それを保険内の計画的屋外サービスへそのまま一般化しない。

MQ-005は引き続き停止する。

## Regression

- municipal query: 15 / 15
- MHLW external query: 33 / 33
- verified regression: 51 / 51
- coverage gap: 20 / 20
- false-ANSWER stress: 12 / 12
- claim promotion: 2 / 2
- natural-language routing: 12 / 12
- verified Claim routing: 28 / 28
- multi-claim routing: 5 / 5
- important-matters routing: 3 / 3

合計 **181 / 181**。

## 現在の正本

- Claim Registry: `claims-v0.11.json`
- Composition Registry: `claim-compositions-v0.3.json`
- Classifier: `research-coverage-classifier-v0.17.mjs`
- Municipal sample: `municipal-query-sample-v0.3.json`
- Benchmark: `benchmark-v0.15.json`

## 次

次回は、

1. 理美容の「誰が提供できるか／資格」境界
2. 訪問診療・訪問歯科
3. 別自治体query

の順が自然。

RAGはまだ実装しない。
