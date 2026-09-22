# Experiment Plan — 介護ルールを使った情報探索benchmark

作成日: 2026-09-22  
状態: Draft / 実行前

## 目的

「介護分野の情報探索」において、

- 現在のnavigation / search
- 構造化FAQ
- source-grounded RAG

のどこに追加価値があるかを、小規模に検証する。

AIを導入すること自体を目的にしない。

## 1. Benchmark question set

公開情報だけから回答できる質問を30〜50問程度作る。

質問タイプを分ける。

### A. 単純lookup
例:
- 基準上必要な数値
- 用語
- 一単位単価

### B. 複数資料を横断
例:
- 告示 + Q&A
- 基準 + 解釈通知

### C. 条件付き
例:
- Aの場合とBの場合で扱いが変わるもの

### D. 原典への到達が重要
回答本文より「どこを読めばよいか」が価値になる質問。

### E. 回答不能
現在のDBに根拠がない質問。

AIが無理に答えず「確認できない」と返せるかを見る。

## 2. Compare

### Baseline 1
通常navigation。

### Baseline 2
keyword / full-text search。

### Candidate
source-grounded RAG。

## 3. Metrics

- correct answer
- correct source
- source coverage
- unsupported claim rate
- abstention accuracy
- time to answer
- number of clicks
- user confidence
- correction effort

最重要は「回答速度」単独ではなく、

> 正しい根拠に短時間で到達できるか

とする。

## 4. Safety

最初は公開情報のみ。

除外:
- 個人情報
- 利用者記録
- 未公開自治体内部資料
- individual care decision
- 高リスクな自動判断

## 5. Hypothesis

### H-A
単純lookupでは、よく設計されたordinary searchがRAGと同等または優位な可能性がある。

### H-B
複数資料横断・自然言語質問ではRAGの追加価値が出る可能性がある。

### H-C
source freshness / provenanceを設計しないRAGは、検索時間を短縮しても信頼性を損なう。

### H-D
「回答不能」を正しく返す能力が、介護ルール用途では重要になる。

## 6. 実施後の判断

### RAGを進める
- source accuracyが高い
- unsupported claimが低い
- baselineより明確な時間短縮
- 原典確認が容易

### 検索改善を優先
- RAG差分が小さい
- simple searchで十分
- hallucination / stale answer管理コストが大きい

### Hold
- authoritative source coverageが不足
- benchmark question自体が安定しない
-制度DBの整備を先にした方がよい

## 7. サイトへの反映

結果が出るまで、

「AI検索なら解決できる」

とは書かない。

公開時は、

- AIを使う場合
- AIを使わない場合
- 適用条件
- benchmark結果

を並べる。
