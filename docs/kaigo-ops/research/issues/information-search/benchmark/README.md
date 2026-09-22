# Information Retrieval Benchmark

作成日: 2026-09-22  
状態: **v0.3 complete / paused before coverage-gap expansion**

## 目的

介護ルールを使って、

- navigation
- full-text / keyword search
- structured FAQ
- Issue routing + linked-source expansion
- source-grounded RAG

を同じground truthで比較する。

## 現在地

### v0.1
- 20 core questions
- safety seed
- simple deterministic retrieval

### v0.2
- unseen natural-language 18
- multi-source 6
- safety 11
- answer scoring rubric

### v0.3
合計 **50 case**。

- retrieval / synthesis: 39
- fail-closed safety: 11

Files:

- `benchmark-v0.3.json`
- `baseline-v0.3.md`
- `router-design-v0.1.md`
- `scripts/research-issue-router-v0.1.mjs`

再現:

```bash
node scripts/research-issue-router-v0.1.mjs
```

## v0.3 headline result

39 retrieval cases:

- FAQ / Issue Hit@1: 92.3%
- FAQ / Issue Hit@3: 100%
- direct source mean Recall@5: 89.5%
- direct source Complete@5: 82.1%
- top-3 Issue → linked-source complete: 100%

11 safety cases:

- deterministic decision baseline: 11 / 11

ただし11/11は生成文章の品質ではない。

評価対象は、

- answer
- abstain
- clarify
- metadata-status answer

のdecision layer。

## Strong non-RAG baseline

```text
query
 ↓
fail-closed guards
 ↓
Issue router
 ↓
top 3
 ↓
ambiguity handling
 ↓
linked-source expansion
 ↓
verification / currentness filter
 ↓
verified answer components
```

現段階では、RAGを入れる前にこのbaselineを比較対象として維持する。

## 重要な限界

v0.3の質問は依然として、現在のverified coverageを理解した上で作成している。

つまり、

> 「既知の12 Issueへroutingする性能」

を中心に測っている。

実利用のcoverageを代表しているわけではない。

## 次の再開点

### 1. Coverage-gap benchmark

現在の12 Issueでは答えられない、または部分回答になる質問を追加する。

分類:

- ANSWER
- PARTIAL
- REVIEW_REQUIRED
- LOCAL
- OUT_OF_SCOPE

### 2. Human answer review

11 safety caseについて、最終文章として

- 条件を落としていないか
- 余計なIssueを混ぜていないか
- source statusを正確に説明しているか

を人手採点する。

### 3. RAG comparison

上記2点を終えてから行う。

RAGが、
- coverage
- synthesis
- safety
のどこを改善するのか確認できない場合は採用しない。
