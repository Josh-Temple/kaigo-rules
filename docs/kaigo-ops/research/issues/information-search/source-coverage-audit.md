# Kaigo Rules — Source Coverage Audit for Retrieval Benchmark

監査日: 2026-09-22  
対象branch: `docs/kaigo-ops-research-plan`  
目的: ordinary search / FAQ / RAG比較を始める前に、ground truthとして使える範囲と、使ってはいけない範囲を固定する。

## 結論

**小規模benchmarkは開始可能。広域RAG評価はまだ早い。**

現在の最も安全な実験範囲は、

> `data/questions.json` の12件の検証済み質問 + それが参照する検証済み制度ノード

である。

一方、

- 843件のQ&A corpus
- e-Govから生成した基準省令全182ノード
- 介護保険法137ノード
- 通知再構成29区画
- 報酬30ノード / 現行本文29区画
- 一単位単価の地域割当427件

は、機械取込や骨格生成ができていても、人手レビューが終わっていない層を含む。

これらを一括でRAGへ入れて正答率だけを測ると、model性能とsource qualityを混同する。

---

## 1. Layer別 readiness

| Layer | 現在の状態 | 件数 | Benchmark利用 |
|---|---|---:|---|
| 検証済み実務質問 | verified | 12 | **利用可** |
| 回答ページ接続済みrule nodes | VERIFIED_CURRENT | 21 | **利用可** |
| 基準省令37号 generated nodes | IMPORTED_NEEDS_HUMAN_CHECK | 182 | 原則まだ不可 |
| 基準省令review overlay | NOT_STARTED | 0 reviewed | 不可 |
| notice nodes | VERIFIED_SOURCE_TEXT 2 / KNOWN_AFTER_TEXT 4 / UNKNOWN 3 | 9 | nodeごとに制限 |
| 老企25号current skeleton | text reconstruction pending | 29 | 広域利用不可 |
| 老企25号review | NOT_STARTED | 0 | 不可 |
| 国Q&A corpus | INGESTED_UNREVIEWED | 843 | **探索候補には可、ground truth不可** |
| 回答へ接続済みQ&A | STRUCTURED | 1 | 当該質問の補助根拠として可 |
| 介護保険法 generated nodes | IMPORTED_NEEDS_HUMAN_CHECK | 137 | 原則まだ不可 |
| 介護保険法review | NOT_STARTED | 0 | 不可 |
| 報酬 skeleton | human check pending | 30 | 広域利用不可 |
| 報酬 current text | IMPORTED_CURRENT_SOURCE_NEEDS_HUMAN_CHECK | 29 | ground truth不可 |
| 報酬review | NOT_STARTED | 0 | 不可 |
| 留意事項current skeleton | backfill pending | 29（21 known / 8 unknown） | 不可 |
| 一単位単価 | imported current source / human check pending | 8区分 | 候補値のみ |
| 地域区分assignment | human check pending | 427明示地域 + default | ground truth不可 |

## 2. 良い点

### Provenanceがかなり強い

多数のlayerで、

- source URL
- source SHA-256
- amendment/revision
- effective date
- review status

が分離されている。

これはRAGを作る前提として非常に良い。

### Machine importとhuman verificationが分離されている

特に、

- `*-meta.json`
- `*-review.json`

を分けた設計により、「取得できた」ことと「正しいと確認した」ことを混ぜていない。

このfail-closed設計はbenchmarkでも維持する。

### Current / historical / partial sourceを区別している

`sources.json` では、

- verified_source
- current_official_source
- partial_source
- historical_reference
- base_text_replay_pending

等が区別されている。

RAGではこのstatusをretrieval metadataへ必ず渡すべき。

---

## 3. 現在の弱点

### Ground truthが12問に集中

12問は質が高い一方、

- 人員
- 運営
- 計画
- 研修

が中心で、報酬・加算・Q&A横断・改正差分を十分に試せない。

まず12問でpipelineの安全性を検証し、その後ground truthを50問へ拡張する。

### 843 Q&Aのレビュー差

Q&A corpus:

- scanned: 3,739 rows
- included: 843
- 通所介護: 252
- 全サービス共通: 480
- 居宅サービス共通: 47
- 通所系共通: 64
- status: `INGESTED_UNREVIEWED`

したがって、843件を「答え」として使うのではなく、

> reviewed questionに対するcandidate retrieval source

として使い、人手採用後にground truthへ昇格させる。

### 通知・報酬はcurrentnessの難度が高い

老企25号・36号は、最新改正資料の「略」や過去HTMLを組み合わせて現行状態を再構成する必要がある。

ここはLLMに補完させない。

`UNKNOWN` は `UNKNOWN` のまま返すことをbenchmarkで評価する。

---

## 4. Benchmark v0.1

### Core set

`questions-v0.1.csv`

- canonical verified: 12問
- paraphrase verified: 8問
- total: 20問

最初はこの20問でretrieval / citation pipelineの基本動作を確認する。

### Safety challenge

`challenges-v0.1.csv`

- local-rule scope
- out-of-scope service
- unreviewed remuneration
- unreviewed unit price assignments
- stale source
- unreviewed Q&A corpus
- condition loss
- false premise

を含む10問。

この10問は「答えられる量」ではなく、

> **答えてはいけない時に止まれるか**

を見る。

---

## 5. 次のGate

### Gate A — v0.1 pipeline

20 verified/paraphrase + 10 safety challenge。

合格条件を先に固定する。

### Gate B — 50問化

追加する質問は、人間が一次資料を確認し、
`data/questions.json` またはbenchmark専用gold fileへ固定した後に使う。

### Gate C — unreviewed corpus retrieval

843 Q&A等は最初からanswer corpusにせず、

1. candidate retrieval
2. human review
3. status promotion
4. benchmark追加

の順にする。

### Gate D — RAG

ordinary navigation / full-text / curated FAQ baselineを作ってからRAGを比較する。

RAGだけを単独評価しない。

---

## 6. Benchmark前に実装すべきmetadata filter

最低限:

- verification_status
- source status
- effective_from / effective_to
- reviewed_at
- service scope
- source authority
- superseded / historical

retrieval時に、

- unreviewed
- historical
- out-of-scope

を同列にrankしない。

---

## 7. 判断

現時点では、**RAG実装を急ぐよりbenchmark harnessを先に作る**のが妥当。

理由:

1. ground truthがすでに12問ある。
2. source statusが豊富で、安全性テストを作りやすい。
3. unreviewed corpusをあえて残しているので、fail-closed性能も評価できる。
4. benchmarkを先に作れば、将来modelやsearch engineを変えても同じ条件で再評価できる。

これはKaigo Rulesそのものの品質保証にも使える。
