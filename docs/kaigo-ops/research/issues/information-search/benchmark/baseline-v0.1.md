# Deterministic Retrieval Baseline v0.1

実行日: 2026-09-22  
corpus: verified questions 12 / VERIFIED_CURRENT rule nodes 21  
test set: 20（canonical 12 + paraphrase 8）

## Method

dependencyなしのNode.js scriptで、

- Unicode NFKC正規化
- 記号・空白除去
- 日本語を含むcharacter bigram
- TF-IDF
- cosine similarity

を使った。

二つのbaselineを測定した。

### FAQ retrieval

対象document:
- question title
- aliases
- short answer

gold:
- 正しいquestion slug

### Raw rule retrieval

対象document:
- rule topic
- path
- official text

gold:
- questionに紐づくrule nodeのいずれか

## Result

| Baseline | Hit@1 | Hit@3 | Hit@5 |
|---|---:|---:|---:|
| Curated FAQ retrieval | 95% | 100% | — |
| Raw verified-rule retrieval | 95% | 100% | 100% |

## Misses

### FAQ top-1

`兼務について教えてください。`

gold:
`multiple-roles`

top-1:
`manager-concurrent-role`

これは単純な検索失敗というより、query自体が曖昧。

「管理者の兼務」なのか、
「生活相談員と介護職員等の複数職種兼務」なのか
を追加確認した方がよい。

### Raw rule top-1

`運営規程 記載について教えてください。`

gold rule:
`ordinance37.article100`

top-1:
`ordinance37.article99.1`

ただしArticle 100はtop-3に入った。

短いkeyword queryでは「記載」が通所介護計画の条文にも強くhitする。

## Interpretation

### 1. RAGの比較対象は意外と強い

21件のきれいなverified corpusでは、単純なcharacter bigram検索でもtop-3 100%。

したがって、

> 「LLMを使えば検索が賢くなる」

だけでは追加価値にならない。

RAGは少なくとも、

- multi-source synthesis
- condition handling
- citation
- currentness
- no-answer
- contradiction handling

で差を示す必要がある。

### 2. Clean corpusの効果が大きい可能性

今回の高いhit率は、

- corpusが21件と小さい
- nodeのtopic/pathが整理済み
- ground truthが既存questionから作られている

ためでもある。

つまり、AIより前の構造化がすでに大きな価値を持っている。

### 3. Benchmarkを難しくする必要がある

v0.2では、

- 未知の自然文
- 条件不足
- 同義語
- 複数source横断
- stale source
- contradiction
- answer unavailable
- local-vs-national scope

を増やす。

## Reproduce

repo root:

```bash
node scripts/research-retrieval-baseline.mjs
```

## Do not over-interpret

この95% / 100%はproduct KPIではない。

既存のtitle/aliasを元にしたseed setであり、
production user queriesの代表sampleではない。

目的は、以後のsearch / RAG改善を同じtestで比較できる最初のbaselineを固定すること。
