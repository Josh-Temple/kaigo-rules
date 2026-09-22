# Information Retrieval Benchmark

作成日: 2026-09-22  
状態: **v0.2 complete / paused before RAG**

## 目的

介護ルールを使って、

- navigation
- full-text / keyword search
- structured FAQ
- Issue routing + linked-source expansion
- source-grounded RAG

を同じground truthで比較する。

## v0.1

- `questions-v0.1.csv`: 20問
- `challenges-v0.1.csv`: safety challenge
- `baseline-v0.1.md`: title / alias由来seedの最初のbaseline

v0.1ではclean small corpusでsimple retrievalがかなり強いことを確認した。

## v0.2

- `benchmark-v0.2.json`
  - unseen natural-language: 18
  - multi-source: 6
  - safety: 11
- `scoring-v0.2.md`
  - answer-level rubric
  - hard fail条件
- `baseline-v0.2.md`
  - deterministic baseline結果

再現:

```bash
node scripts/research-retrieval-benchmark-v0.2.mjs
```

## v0.2 result

24 retrieval tests:

- FAQ Hit@1: 95.8%
- FAQ Hit@3: 100%
- direct trusted-source mean Recall@5: 91.3%
- direct trusted-source Complete@5: 79.2%
- FAQ routing + Top3 linked-source union Complete: 100%

この結果から、現段階ではRAGより先に、

```text
query
 ↓
Issue router
 ↓
top-k ambiguity handling
 ↓
linked source graph expansion
 ↓
status / currentness filter
 ↓
answer
```

を強いnon-RAG baselineとする。

## 重要な注意

v0.2もproduction benchmarkではない。

- 現在のverified coverageを見て手作業で作成
- corpusが小さい
- real user query logではない
- answer generation未評価

したがって100%を性能保証として使わない。

## Safety

11 challenge:

- local rule
- out-of-scope
- unreviewed source
- stale source
- provenance status
- condition loss
- false premise
- ambiguity

これらはretrieval-only scriptでは採点しない。

将来のanswer systemに対して、
`scoring-v0.2.md` のrubricでhuman-reviewed evaluationを行う。

## 次の再開点

RAG実装はまだ行わない。

次は:

1. benchmarkを50問程度へ拡張
2. 現在のcoverageを知らない第三者的なqueryを増やす
3. safety 11問でanswer-level baselineを取る
4. Issue router + linked-source expansionを実装候補として評価
5. その後RAG candidateを同条件で比較

RAGがこのbaselineを上回らなければ、導入しない。
