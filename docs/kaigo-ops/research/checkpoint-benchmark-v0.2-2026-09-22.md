# Kaigo Ops Research Checkpoint — Benchmark v0.2

更新日: 2026-09-22  
状態: **Benchmark v0.2 complete / paused**

## 今回の区切り

前回のResearch foundation v0.1から、情報探索Issueのbenchmarkを一段進めた。

完了:

- unseen natural-language 18問
- multi-source 6問
- safety challenge 11問
- answer-level scoring rubric
- deterministic v0.2 runner
- direct trusted-source retrieval baseline
- FAQ / Issue routing baseline
- linked-source expansion baseline

## 主結果

### Direct source search

24問:

- mean Recall@5: 91.3%
- Complete@5: 79.2%

multi-source 6問ではComplete@5 66.7%。

単純なsource検索では、「関連資料は見つかる」が「必要根拠を全部揃える」で落ちる。

### Curated Issue routing

- FAQ Hit@1: 95.8%
- FAQ Hit@3: 100%

### Issue routing + linked-source expansion

- Top1 bundle complete: 91.7%
- Top3 union complete: **100%**

この小規模testでは、

> query → Issue候補 → 明示済みrelationで根拠展開

が非常に強かった。

## 設計への示唆

RAGを急いで入れる必要はない。

当面のstrong baseline:

```text
query
 ↓
deterministic Issue router
 ↓
top 3
 ↓
ambiguity check
 ↓
linked-source expansion
 ↓
verification/currentness filter
 ↓
answer
```

これはKaigo Rulesの既存構造を最大限使う。

## 見つかった弱点

1. 「感染症研修」の質問でFAQ top-1がBCP研修へ誤着地。
   - top-3では正しいIssueを回収。
   - top-1即答は避けるべき。

2. raw source searchは準用関係・複数根拠を全部集めにくい。
   - article relation / Issue relationを使う方が安定。

3. multi-sourceではtop-k budgetが問題になる。
   - 検索結果だけで全sourceを集めるよりgraph expansionが有効。

## まだ証明できていないこと

- real usersの質問でも同じ性能か
- 50問以上へ拡張して維持するか
- answer生成で条件を落とさないか
- safety challengeに全て合格できるか
- RAGがnon-RAG baselineを上回るか

## 次回の再開点

Priority:

1. **Benchmark v0.3 / 50問化**
   - current coverageを直接見ない形でqueryを追加
   - 複数資料横断を増やす
   - out-of-scopeを増やす

2. **Answer-level baseline**
   - safety 11問
   - hard fail = 0 を確認

3. **Issue router + linked-source expansion**
   - 小さく実装
   - status filter必須

4. **その後にRAG candidate**
   - 同じbenchmarkで比較
   - 明確な追加価値がなければ採用しない

## Pause condition

Benchmark設計、再現script、non-RAG baseline、次のGateまで固定できた。

**ここで一旦止めるのが適切。**
