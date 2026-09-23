# Kaigo Ops Research Checkpoint — National RAG Holdout Labeling v0.1

更新日: 2026-09-23  
状態: **20 / 20 labeled REVIEW_REQUIRED**

## 対象

`rag-holdout-national-raw-v0.1.json`

厚生労働省「令和6年度介護報酬改定に関するQ&A（Vol.1）」の
通所介護関連20問。

## Fresh review state

current mainを再確認。

- `remuneration-review.json`: **NOT_STARTED**
- `fee-guidance-review.json`: **NOT_STARTED**
- `unit-price-review.json`: **NOT_STARTED**

機械取込や独立機械照合が進んでいても、
人手確認済みの算定要件としては扱わない。

## Label result

- REVIEW_REQUIRED: **20**
- ANSWER: 0
- PARTIAL: 0
- LOCAL: 0
- OUT_OF_SCOPE: 0

主な論点:
- 個別機能訓練加算
- 入浴介助加算
- 所要時間区分
- 送迎減算
- 3％加算
- 事業所規模区分の特例

## 判断理由

質問の途中に既に検証済みの人員配置事実が含まれていても、
利用者が求めている結論が「加算を算定できるか」「減算されるか」
である以上、未レビューの報酬レイヤーを飛び越えてANSWERしない。

厚労省Q&A本文も、見つかったことだけを理由にClaim promotionへ使わない。

## Combined external holdout

Batch 1（自治体30件）:
- LOCAL 26
- OUT_OF_SCOPE 3
- REVIEW_REQUIRED 1

Batch 2（国Q&A 20件）:
- REVIEW_REQUIRED 20

合計50件:
- LOCAL: **26**
- OUT_OF_SCOPE: **3**
- REVIEW_REQUIRED: **21**
- ANSWER: **0**
- PARTIAL: **0**

## 重要な観測

新しい外部queryを先に固定してからラベル付けすると、
現在のanswerable corpusでANSWERできる質問は **0 / 50** だった。

これはRAGの検索能力不足を示す結果ではない。

むしろ現在の制約は

> retrieval coverage ではなく reviewed Claim coverage

である可能性が高い。

RAGを先に実装しても、
検索できる未レビュー資料が増えるだけで、
安全にANSWERできる範囲は広がらない。

## 次

1. benchmark harness v0.23を実行可能環境で再実行
2. RAG実装は保留
3. REVIEW_REQUIREDから再利用価値の高いClaimを選び、promotion flowでcoverageを増やす
4. coverage拡張後に新しいholdout batchを追加し、RAGの追加価値を再評価する
