# Kaigo Ops Research Checkpoint — First Claim Promotion

更新日: 2026-09-22  
状態: **2 claims promoted / claim-aware regression preserved**

## 今回の対象

- `candidate.staff.life-counselor.service-meeting-time`
- `candidate.facility.dining-training.multi-room`

claim_idは参照安定性のため変更せず、statusを正本とする。

## Promotion 1 — 生活相談員のサービス担当者会議時間

確認した公式資料:

- 厚生労働省「平成24年度介護報酬改定に関するQ&A（Vol.2）」問12
- 厚生労働省「介護サービス関係Q&A」現行公式索引

固定したclaim:

> 指定通所介護事業所の生活相談員がサービス担当者会議に出席するための時間は、確保すべき勤務延時間数に含めることができる。

status:

`VERIFIED_WITH_SOURCE_LIMITATION / ANSWER`

Q&A本文は直接確認でき、現行公式Q&A索引も確認できた。一方、ローカルの解釈通知統合全文再構成は未完了のため、source limitationを保持する。

## Promotion 2 — 食堂・機能訓練室の複数室合算

確認した公式資料:

- 基準省令第95条
- 厚生労働省の解釈通知「設備に関する基準」(2)①
- 介護サービス関係Q&A集 No.599
- 令和6年度介護報酬改定の公式ページ

固定したclaim:

> 狭隘な部屋を多数設置して面積を確保する方法は原則不可。ただし、通所介護の単位をさらにグループ分けし、効果的な指定通所介護の提供が期待される場合は例外となる。Q&Aではこの条件を満たす複数室合算の具体例が認められている。

status:

`VERIFIED_WITH_SOURCE_LIMITATION / ANSWER`

重要なboundary:

**複数室なら無条件に面積を足してよい、というclaimではない。**

## Versioning

昇格前の状態を再現できるよう、

- `claims-v0.1.json`
- `external-qa-query-sample-v0.1.json`
- `research-coverage-classifier-v0.4.mjs`

は履歴として保持した。

昇格後は、

- `claims-v0.2.json`
- `external-qa-query-sample-v0.2.json`
- `research-coverage-classifier-v0.5.mjs`
- `benchmark-v0.6.json`

を使う。

## Regression

新しい期待値で:

- verified regression: 51 / 51
- coverage gap: 20 / 20
- false-ANSWER stress: 12 / 12
- external Q&A: 15 / 15
- claim promotion paraphrase: 2 / 2
- total classifier checks: 100 / 100

EQ-004とEQ-010は、公式資料reviewによるcoverage拡張のため、期待値を意図的に `REVIEW_REQUIRED → ANSWER` へ変更した。

## 次

次はfalse abstentionを測る。

特に、

- verified claimなのに自然な言い換えでREVIEW_REQUIREDになるケース
- Issue-level fallbackが広すぎて、未確認subtopicをANSWERするケース

の両方を分けて測る。

RAGはまだ実装しない。
