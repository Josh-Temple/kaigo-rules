# Controlled RAG Comparison Protocol v0.1

作成日: 2026-09-23  
状態: **PROTOCOL_FIXED / RAG NOT IMPLEMENTED**

## 目的

Claim-aware non-RAG baselineに対して、RAGを追加することで実際に価値が増えるかを比較する。

RAG導入自体を成果としない。

比較対象は「検索がそれらしくなるか」ではなく、

- 答えてよい範囲を守れるか
- 正しいClaimへ着地できるか
- 必要な根拠を揃えられるか
- 未レビュー資料を回答根拠へ混入させないか
- 未知表現で不要なabstentionを減らせるか

とする。

## 固定原則

以下はRAG導入後も変更しない。

1. similarity ≠ answerability
2. Issue verified ≠ all subtopics verified
3. retrievable corpus ≠ answerable corpus
4. service scope / locality / review state / currentnessはmodel外で判定する
5. generationは最後の層に置く
6. 未レビュー資料を、検索で見つかったことだけを理由に回答可能へ昇格しない

## 現在のbaseline

- Claim Registry: `claims-v0.15.json`
- Composition Registry: `claim-compositions-v0.5.json`
- Classifier: `research-coverage-classifier-v0.22.mjs`
- Frozen regression suite: 190 cases
- Last executed classifier baseline: 191 / 191
- verified regression Issue fallback: 0 / 51
- safety prose human sign-off: PENDING
- source-limited Claim: 1

191/191は直前の実行結果であり、v0.15/v0.22へのsource-only update後に再実行した値ではない。
decision fieldsとclassifier logicに判定差分がないことは確認済み。

## 比較を二段階に分ける

### Stage 1 — Retrieval only

生成AIを使わない。

同じqueryに対して、

- expected Claim / Composition
- expected answerability
- expected source set

をどこまで再現できるか比較する。

Stage 1で安全性またはprovenance gateを落とす候補はStage 2へ進めない。

### Stage 2 — Answer composition

Stage 1を通過した方式だけを対象にする。

回答材料はStage 1で許可されたClaim / sourceに限定し、
自由なcorpus探索を回答生成中に追加しない。

## 比較arm

### Arm A — Current non-RAG baseline

現在のClaim-aware router。

```text
query
 ↓
coverage / scope / review / currentness gate
 ↓
Issue candidate
 ↓
Claim / Composition routing
 ↓
verification status / answerability
 ↓
explicit linked sources
```

### Arm B — Verified-only RAG candidate

production候補。

重要:
RAGはanswerability gateの代替にしない。

```text
query
 ↓
deterministic answerability gate
 ↓
verified / answerable corpusだけをretrieval
 ↓
Claim / source candidate
 ↓
Claim Registryとの整合確認
 ↓
explicit source relation
```

retrieval corpusへ入れてよいもの:
- ANSWER Claim
- approved Composition
- それらに明示接続されたverified/current source text
- source limitationを保持したClaimはstatusを落とさず収載

入れてはいけないもの:
- INGESTED_UNREVIEWED Q&A本文
- CANDIDATE_UNREVIEWED
- REVIEW_REQUIRED
- human review未完了の報酬・一単位単価を確定情報として表すchunk
- LOCALな自治体回答を全国ルールとして扱うchunk

### Arm C — Broad-corpus retrieval negative control

research-only。production候補ではない。

機械取込済みだが未レビューの資料を含む広いcorpusでretrievalだけを実施し、
どの程度unreviewed sourceが上位へ混入するかを測る。

生成回答には使わない。

目的は
`retrievable corpus ≠ answerable corpus`
を実測すること。

## Test data

### Frozen regression suite

現在の190 casesを変更しない。

ここは安全性回帰確認に使う。

### New holdout

RAGの有効性判定は、既存190件だけで行わない。

理由:
現在のrouterは既存suiteへ繰り返し改善されており、
同じsetだけではRAGの追加価値を測りにくい。

新規holdoutは次の条件で作る。

- 30〜50件を目安
- current registryを見ながら質問を作らない
- 既存のexternal sampleで未使用の公式・自治体公開質問から採る
- 検索query風の短文を含める
- 曖昧表現を含める
- ANSWERだけでなく PARTIAL / REVIEW_REQUIRED / LOCAL / OUT_OF_SCOPE を含める
- 答え本文はquery作成時にRAG corpusへ追加しない

holdoutのexpected label / Claim / sourceは、query収集後に別工程で固定する。

## Primary safety metrics

候補が1件でも以下を起こした場合はfail。

- false ANSWER
- LOCALを全国共通ルールとしてANSWER
- OUT_OF_SCOPEへの類推ANSWER
- REVIEW_REQUIRED sourceから確定回答
- stale/currentness未確認情報の現行扱い
- unreviewed source leakage
- expected Claimとは異なるverified Claimで意味をすり替えてANSWER

## Retrieval metrics

- answerability accuracy
- expected Claim Hit@1 / Hit@3
- multi-Claim complete
- trusted-source Recall@5
- trusted-source Complete@5
- false abstention
- provenance contamination rate

既存baselineと同じ定義を優先し、新しいmetricを増やしすぎない。

## Advance rule

Arm Bを採用候補にする条件:

1. primary safety metricでArm Aから悪化しない
2. frozen regression suiteでhard fail 0
3. new holdoutでClaim retrieval、source completeness、false abstentionの少なくとも一つに実質的改善がある
4. 改善が既存のexplicit relation graphだけで同等に得られる場合は、より単純な方式を優先する
5. 運用負荷・再現性・currentness管理を悪化させる場合は採用しない

「RAGだから採用」は不可。

## Parameter tuning rule

以下をfrozen regression / holdoutの結果を見ながら都合よく変更しない。

- embedding model
- chunk unit
- top-k
- metadata filter
- reranking有無

最初の比較条件は別のdevelopment setで決める。
holdoutを見て変更した場合、そのholdoutは以後test setとして扱わない。

## Chunking policy candidate

最初の候補単位:

1. Claim statement
2. Claim boundaries
3. source node単位の本文
4. Claim ID / source ID / verification statusをmetadataとして保持

大きなPDFページ単位やQ&A corpus丸ごとのchunkを初期候補にしない。

## Generation gate

Stage 2で生成を使う場合も、modelへ渡す材料は

- resolved Claim
- boundaries
- verification status
- linked source excerpt
- answerability decision

に限定する。

model自身に
「このsourceはreview済みか」
を推測させない。

## 実験終了時に残すもの

- fixed config
- corpus manifest
- development set
- frozen regression result
- holdout result
- per-case error log
- safety failures
- source contamination log
- 採用 / 不採用理由

平均scoreだけを残さない。

## 現時点

この文書では実験条件だけを固定した。

- vector DB: 未導入
- embedding: 未選定
- RAG code: 未実装
- generation comparison: 未実施

次はnew holdoutの作成を先に行う。
