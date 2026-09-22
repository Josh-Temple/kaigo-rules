# Kaigo Ops Research Checkpoint — Multi-Claim Composition

更新日: 2026-09-22  
状態: **multi-claim composition gate complete / 145 checks PASS**

## 背景

atomic Claim routingを進めた結果、Issue fallbackは51件中8件まで減った。

そのうち5件はcoverage不足ではなく、1つの質問が複数のverified Claimを正当に必要とするケースだった。

単一Claimへ無理に固定するとprovenanceを失うため、別のcomposition layerを作った。

## Composition Registry

`docs/kaigo-ops/research/claims/claim-compositions-v0.2.json`

現在4 composition。

- 看護職員の基本配置 + 外部連携
- 一般的な複数職種兼務
- 通所介護計画の記載 + 説明/同意 + 実施記録
- 毎年確認する主要研修

compositionは新しい事実を作らない。

構成要素はすべて、

- answerability = ANSWER
- verification_status = verified系

でなければならない。

1つでも未確認ならcomposition全体をANSWERにしない。

## 重要な失敗と修正

最初のannual-training compositionは、

- BCP年1回
- 感染症年1回
- 虐待防止年1回

という単一Claim質問まで拾い、verified Claim routing 28件のうち3件を壊した。

v0.2では、

- BCP
- 業務継続
- 感染症
- 虐待

を明示するqueryをannual summary compositionから除外した。

その結果、atomic Claimが優先される状態に戻った。

## 結果

- verified regression: 51 / 51
- coverage gap: 20 / 20
- false-ANSWER stress: 12 / 12
- external Q&A: 15 / 15
- claim promotion: 2 / 2
- natural-language routing: 12 / 12
- verified Claim routing: 28 / 28
- multi-claim routing: 5 / 5

合計 **145 / 145**。

## Issue fallback

推移:

- claims-v0.3: 51 / 51
- atomic Claim routing後: 8 / 51
- multi-claim composition後: **3 / 51**

残る3件:

- 重要事項説明書の国様式・ひな形: 2件
- 重要事項説明書の記載内容全体: 1件

ここから先はrouting改善ではなくClaim coverage review。

## 次

1. 重要事項説明書に国の固定様式があるかを独立review
2. 重要事項を記した文書の「内容」Claimを分解
3. last 3 fallbackを、根拠が揃う場合だけClaimへ移す
4. 外部queryで自然言語testを拡張
5. human sign-off
6. RAG比較

production app codeはまだ変更しない。
