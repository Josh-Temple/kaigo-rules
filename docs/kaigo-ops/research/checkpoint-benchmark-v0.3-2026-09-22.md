# Kaigo Ops Research Checkpoint — Benchmark v0.3

更新日: 2026-09-22  
状態: **50-case non-RAG baseline complete / paused**

## 今回完了

Benchmark v0.2から以下へ進めた。

### 50-case benchmark

- retrieval / synthesis: 39
  - unseen: 18
  - multi-source: 6
  - natural variant: 13
  - cross-issue: 2
- safety / fail-closed: 11

### Non-RAG Issue Router v0.1

LLMなし。

- character bigram TF-IDF
- top-3 Issue保持
- explicit linked-source expansion
- review/currentness guards
- local/scope guards
- short ambiguity clarification
- verified answer components

## 結果

### Retrieval

- Hit@1: 92.3%
- Hit@3: 100%
- direct source mean Recall@5: 89.5%
- direct source Complete@5: 82.1%
- top-3 linked-source mean recall: 100%
- top-3 linked-source complete: 100%

### Safety decision

11 / 11 expected decisionと一致。

ただし、
**full prose answer qualityは未評価**。

## 重要な知見

### 1. Relation graphがsearchより重要な場面がある

準用、複数資料、複数研修等は、
生のsearchで全部拾わせるより、

Issue → linked sources

の方が安定。

### 2. Top-1即答は危険

質問を自然にするとHit@1は下がった。

近接Issue:

- BCP / 感染症 / 虐待防止研修
- 通所介護計画 / 署名 / 押印

などで誤着地する。

top-k保持が必要。

### 3. Fail-closedをretrievalより前へ置く

- local
- out-of-scope
- unreviewed
- stale
- ambiguous

を先に止める。

「検索結果があるから答える」という順番にしない。

## 現在のarchitecture候補

```text
question
 ↓
scope / review / currentness guard
 ↓
Issue router
 ↓
top-k
 ↓
ambiguity handling
 ↓
source graph expansion
 ↓
verified answer components
 ↓
(optional generation later)
```

生成AIは最後の層として考える。

## RAGをまだ作らない理由

現在の50件では、RAGなしでも既知Issueの根拠回収が強い。

今RAGを入れると、

- model能力
- source coverage
- data quality
- relation quality

のどれが価値を出したか分からなくなる。

## 次回

### Priority 1
Coverage-gap benchmark。

「今のDBでは答えられない質問」を増やす。

### Priority 2
11 safety caseのprose human review。

### Priority 3
Issue routerのfalse positive / false abstention試験。

### Priority 4
その後、初めてRAG候補と比較。

## Pause condition

- 50問化
- non-RAG router
- fail-closed decision baseline
- source graph baseline
- 次のGate

まで固定した。

ここで一度区切れる。
