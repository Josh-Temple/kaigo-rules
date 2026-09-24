# Deterministic Retrieval Baseline v0.2

実行日: 2026-09-22  
test set: 24 retrieval questions  
- unseen natural-language: 18
- multi-source: 6

safety set: 11（answer-level評価用、今回のretrieval scriptでは未採点）

## 1. 比較した方式

### A. Curated FAQ retrieval

既存12問について、

- title
- aliases
- short answer
- practical steps
- cautions

をcharacter-bigram TF-IDFで検索。

### B. Direct trusted-source retrieval

対象:
- VERIFIED_CURRENT rule nodes
- verified questionに使用中の VERIFIED_SOURCE_TEXT / KNOWN_AFTER_TEXT notice fragments
- STRUCTURED QA item

計28 source documents。

### C. FAQ routing + linked-source expansion

FAQ検索で上位Issueを選び、そのIssueに明示的に紐づく
- rule_node_ids
- notice_node_ids
- qa_item_ids

を根拠bundleとして展開。

LLMは使わない。

## 2. Result

### Overall

| Method | Metric | Result |
|---|---|---:|
| FAQ retrieval | Hit@1 | 95.8% |
| FAQ retrieval | Hit@3 | 100% |
| Direct source | mean Recall@5 | 91.3% |
| Direct source | Complete@5 | 79.2% |
| FAQ bundle Top1 | mean source recall | 93.8% |
| FAQ bundle Top1 | complete | 91.7% |
| FAQ bundle Top3 union | mean source recall | **100%** |
| FAQ bundle Top3 union | complete | **100%** |

### Unseen 18

| Method | Result |
|---|---:|
| FAQ Hit@1 | 94.4% |
| FAQ Hit@3 | 100% |
| Direct source mean Recall@5 | 90.7% |
| Direct source Complete@5 | 83.3% |
| FAQ bundle Top1 Complete | 94.4% |
| FAQ bundle Top3 union Complete | 100% |

### Multi-source 6

| Method | Result |
|---|---:|
| FAQ Hit@1 | 100% |
| FAQ Hit@3 | 100% |
| Direct source mean Recall@5 | 93.1% |
| Direct source Complete@5 | 66.7% |
| FAQ bundle Top1 Complete | 83.3% |
| FAQ bundle Top3 union Complete | 100% |

## 3. 重要な結果

### 3.1 Direct source searchは複数根拠で落ちる

単純検索は関連sourceを上位へ出せても、
複数の根拠をすべてtop-5へ揃えるとComplete@5は79.2%。

multi-sourceでは66.7%。

これはRAGの余地にも見えるが、別の単純解がある。

### 3.2 Issue routing + source graphが非常に強い

FAQ上位3件のlinked sourcesをunionすると、
この24問ではgold source completeness 100%。

つまり現在のDBでは、

```text
自然文
  ↓
既存Issueへrouting
  ↓
明示的relationで根拠を展開
  ↓
回答
```

というarchitectureがかなり有望。

embedding / vector DB / generative retrievalを先に入れなくてもよい。

### 3.3 「検索」と「関係展開」を分けた方がよい

重要事項のweb掲載では、direct searchは第32条を拾うが、
第105条の準用関係をtop-5へ必ずしも出せなかった。

これは意味検索より、

> 条文関係graphを明示的に展開する問題

に近い。

同様に、
- multi-role
- 研修3種
- 署名・同意

でも、検索だけで全根拠を集めるより既存relationを使う方が安定する。

### 3.4 ambiguityは残る

「感染症対策の研修は年に何回？」でFAQ top-1は `bcp-training` に誤着地し、top-3で `annual-training` を回収した。

このためtop-1をそのまま回答へ使うのは危険。

候補差が小さい場合、
- top-k rerank
- category signal
- clarification
- deterministic relation
のいずれかが必要。

## 4. 現時点のarchitecture候補

RAGの前に、次をbaselineとして実装候補にする。

```text
query
 ↓
Issue router (simple deterministic search)
 ↓
top 3
 ↓
ambiguity check
 ↓
linked source graph expansion
 ↓
status/currentness filter
 ↓
answer template / optional generation
```

AIを使うとしても、retrievalをAIへ全面委任しない。

## 5. RAGに要求する追加価値

このbaselineを超えるには少なくとも、

- 未登録Issueへの対応
- 本当に新しい自然文へのrobustness
- 50問以上へcoverage拡大
- multi-source synthesis
- no-answer
- stale / contradiction handling
- source relationが未整備の領域

で改善が必要。

## 6. Limitations

この結果はまだ楽観的。

- question setは研究者が現在のverified coverageを見て作成
- production user log由来ではない
- corpusが小さい
- source graphが手作業で高品質
- answer generationを評価していない

したがって100%は「問題が解けた」という意味ではない。

むしろ、

> 次に何を難しくすべきかが分かった

という結果。

## 7. 次のGate

Benchmark v0.2はここで固定。

次の実作業は、
1. unseen questionを外部/利用者由来へ近づける
2. 50問へ拡大
3. answer-level safety testを実行
4. その後に初めてRAG candidateを比較

とする。
