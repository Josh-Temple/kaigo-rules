# Kaigo Ops Research Checkpoint — RAG Holdout Labeling v0.1

更新日: 2026-09-23  
状態: **batch 1 labeled / class imbalance preserved**

## Raw set

`rag-holdout-raw-v0.1.json`

30件をラベル付け前に固定した。

## 独立ラベル結果

- LOCAL: **26**
- OUT_OF_SCOPE: **3**
- REVIEW_REQUIRED: **1**
- ANSWER: **0**
- PARTIAL: **0**

既存queryを削除・差替えしてclass balanceを整えていない。

## 偏りの理由

### 神戸市

質問の中心は神戸市の
「介護予防・日常生活支援総合事業」の
`介護予防通所サービス`。

これは現在の指定通所介護core DBとは別に、
自治体の総合事業として運用される。

### 仙台市

質問の中心は
地域密着型サービス事業者の
事前申出・事前協議。

指定権者固有の手続・募集・協議文脈が強い。

### 名古屋市

3件のうち、
- 提供時間中の医療受診 → REVIEW_REQUIRED
- 認知症対応型通所介護 → OUT_OF_SCOPE
- 小規模多機能型との併用 → OUT_OF_SCOPE

とした。

## 意味

このbatchは失敗ではない。

実利用queryの外部sourceを無作為に近く取ると、
現在の狭いcore scopeではLOCAL / OUT_OF_SCOPEが多くなること自体が重要な観測。

一方で、RAGがverified Claim retrievalを改善するかを見るにはANSWER caseがないため、
この30件だけでは不十分。

## 次

第2batchとして、
- 国Q&A
- 全国共通の指定通所介護
- current Claimへ到達可能な未知表現

を中心に追加する。

ただし、ANSWERだけを意図的に集めず、
REVIEW_REQUIREDやPARTIALも残す。

Batch 1は安全性・scope gate用として固定する。
