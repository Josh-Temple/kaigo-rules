# Experiment Plan — 介護ルールを使った情報探索benchmark

作成日: 2026-09-22  
状態: Draft v0.2 / 実行前

## 目的

介護分野のcodified knowledge retrievalにおいて、

- navigation
- keyword / full-text search
- structured FAQ
- source-grounded RAG

のどこに追加価値があるかを検証する。

AI導入自体を目的にしない。

## 0. 実験前Gate — source hygiene

benchmark前に、対象sourceについて確認する。

- authoritative sourceか
- 現行版か
- superseded relationが分かるか
- published_at / effective_at / checked_atがあるか
- service type / scopeが分かるか
- Q&Aと上位ruleの関係を追えるか
- conflicting sourceを検出できるか

coverageが不足する領域は「AI性能評価」に進まず、DB整備を先にする。

## 1. Question set

最初は30〜50問。

### A. 単純lookup

- 基準上の数値
- 用語
- 一単位単価

### B. 複数資料横断

- 告示 + Q&A
- 基準 + 解釈通知

### C. 条件付き

条件により扱いが変わるもの。

### D. 原典探索

「答え」より正しい原典・該当箇所へ到達できるか。

### E. No-answer

DBに根拠がない。

無理に答えず「確認できない」と返せるか。

### F. Stale-source trap

旧版と現行版を両方入れたとき、現行版を優先できるか。

### G. Contradiction trap

複数sourceが異なるように見える場合、勝手に統合せずscope/date差を示せるか。

### H. Ambiguous question

質問条件が足りない場合、断定せず不足条件を示せるか。

## 2. Conditions

### Baseline 1
現行navigation。

### Baseline 2
keyword / full-text search。

### Baseline 3
structured FAQ / curated answer。

### Candidate
source-grounded RAG。

可能ならsame question setを固定して比較する。

## 3. Ground truth

各questionについて事前に人間が、

- correct answer
- required conditions
- authoritative source
- exact section
- acceptable alternate sources
- no-answer criterion

を確定する。

AI出力を見てからground truthを変えない。

## 4. Metrics

### Correctness
- answer correctness
- condition correctness
- source correctness
- citation entailment

### Safety
- unsupported claim rate
- stale-source error rate
- contradiction handling
- abstention accuracy
- overconfident answer rate

### Efficiency
- time to first correct source
- time to final answer
- clicks
- query reformulations
- human correction time

### Usefulness
- user confidence
- source readability
- next-action clarity

最重要metric:

> **正しい原典に短時間で到達し、誤った断定をしないか**

## 5. Analysis

平均だけでなくquestion type別に見る。

想定:

- lookup → ordinary searchが強い可能性
- multi-source → RAG advantageの可能性
- stale / contradiction → governance qualityが支配
- no-answer → model restraintが重要

## 6. Safety boundary

最初はpublic codified knowledgeのみ。

除外:

- 個人情報
- 利用者case note
- 未公開自治体資料
- individual care decision
- medical diagnosis
- 高リスクな自動判断

## 7. Hypotheses

### H-A
単純lookupでは、よく設計されたordinary searchがRAGと同等以上の可能性がある。

### H-B
複数資料横断・自然言語質問ではRAGに追加価値が出る可能性がある。

### H-C
source freshness / provenance不備はmodel性能では補えない。

### H-D
no-answerを正しく返す能力は介護ルール用途で重要。

### H-E
RAG導入効果の相当部分は、RAGそのものではなく、前段のsource整理・metadata整備から生じる可能性がある。

## 8. Decision rule

### RAGを進める

- source correctnessが高い
- unsupported claimが十分低い
- stale / contradiction handlingが合格
- baselineより明確に探索時間を短縮
- human correction effortが増えない

### Search/FAQ改善を優先

- RAG差分が小さい
- simple searchで十分
- citation checking負担が大きい
- currentness管理が難しい

### DB整備へ戻る

- authoritative coverage不足
- version relation不明
- scope metadata不足

### Hold

- benchmark ground truthが安定しない
- high-risk質問とlow-risk質問を分離できない

## 9. Public reporting

結果は「AIの勝敗」ではなく、

- 何に強かったか
- 何に弱かったか
- どの前提が必要だったか
- AIなしで十分な領域
- remaining risk

を公開する。
