# Kaigo Ops Research Checkpoint — 2026-09-22

状態: **Research foundation v0.1 complete / paused**

この時点で一度区切る。  
次回はこの文書から再開する。

## 1. 今回までに完了したこと

### A. Product / research strategy

以下をGitHubへ固定済み。

- Kaigo Rules = 制度・基準・Q&A・原典
- Kaigo Ops = 現場の困りごとから改善策を探す公開サイト
- Studio Lab = 調査・比較・再調査エンジン
- Research Site = Evidence Review / 方法 / 不確実性の公開

AIは目的ではなく手段の一つとする。

### B. 世界の介護DX・AIランドスケープ

初回調査を実施。

対象:
- Japan
- England
- Australia
- Denmark
- Singapore
- United States
- Europe / international reviews

主要カテゴリ:
- 電子記録・data linkage
- information search / knowledge management
- documentation / summarization
- monitoring / falls
- virtual care
- workforce scheduling / routing
- narrow AI
- robots
- care planning
- training
- family / citizen access

Source register、case register、Japan transferability reviewを作成済み。

### C. 日本の定量Evidence

厚生労働省等の公開資料を中心に整理。

主な観察:
- 記録・転記の時間削減が観測された実証がある。
- ただしsoftware単体ではなくworkflow redesignを同時に行っている。
- 介護記録software導入後も手入力転記が残る事業所が多い。
- training / troubleshooting / interoperabilityが導入条件になる。
- data linkageは自施設だけでなく連携先の普及に依存する。

したがって、
**digitisation = productivity improvement**
とは置かない。

### D. First deep Issue

暫定テーマ:

> **必要な情報を探すのに時間がかかる**

ただし二種類へ分離した。

#### Type A: codified knowledge retrieval
- 法令
- 基準
- 通知
- Q&A
- manual
- policy
- FAQ

→ 最初のbenchmark対象。

#### Type B: person-specific care information
- 利用者状態
- 生活歴
- care goals
- sensitive information
- handoff

→ 検索だけでは解けないため後段。

### E. Kaigo Rules source coverage audit

現状を監査。

安全にground truthへ使える中心:
- verified questions: 12
- VERIFIED_CURRENT rule nodes: 21

一方、
- Q&A corpus 843件
- 基準省令generated nodes
- 介護保険法generated nodes
- 通知再構成
- 報酬
- 地域区分

には未レビュー層が残る。

結論:

> **小規模benchmarkは開始可能。全データを一括RAGへ投入するのはまだ早い。**

### F. Retrieval benchmark v0.1

seed:

- canonical verified questions: 12
- paraphrases: 8
- core: 20
- safety challenges: 11

安全性challengeには、
- local rule
- out-of-scope
- unreviewed source
- stale source
- false premise
- ambiguity
- no-answer / conditional

を含めた。

### G. Deterministic baseline

dependencyなしのNode.js scriptを作成。

Method:
- NFKC normalize
- character bigram
- TF-IDF
- cosine similarity

20問seedで:

| Corpus | Hit@1 | Hit@3 |
|---|---:|---:|
| curated FAQ | 95% | 100% |
| raw VERIFIED_CURRENT rule nodes | 95% | 100% |

重要:

これはproduction性能ではない。

既存12問のtitle / alias由来の簡単なseedであり、
目的は比較用baselineを固定すること。

それでも、

> **cleanで小さいcorpusならsimple searchがすでに強い**

ことが分かった。

RAGは単なるretrieval hitではなく、
- multi-source synthesis
- condition handling
- currentness
- citation
- contradiction
- abstention

で価値を示す必要がある。

## 2. 現在の重要な見立て

### 2.1 AIより前の構造化が大きな価値を持つ

Kaigo Rulesでは、
- source provenance
- status
- version
- scope
- review overlay

を整理しているため、単純検索でも高いbaselineになった。

この構造化そのものが資産。

### 2.2 RAGを急がない

次にAIを作るのではなく、

1. benchmarkを難しくする
2. safety challengeを採点可能にする
3. unseen queriesを追加する
4. ordinary search baselineを固定する

の順に進める。

### 2.3 Kaigo Opsの価値は「世界のAIニュース」ではない

中核候補:

> 世界の介護DX・AIを定期的に再調査し、
> 何が実用段階で、
> 何がEvidence不足で、
> 日本ではどの条件なら使えるかを整理する。

高頻度更新より、
深い初回調査 + 数か月ごとの差分再調査を基本とする。

## 3. 今回やらなかったこと

意図的に未実施。

- RAG実装
- LLM benchmark
- 全843 Q&Aのレビュー
- 報酬DB全体のhuman verification
- 介護保険法全node human review
- Kaigo Ops公開Issue pageの本番作成
- 課金機能
- 大規模共通platform
- 他業界展開

現時点では不要。

## 4. 次回の再開点

### Priority 1 — Benchmark v0.2

- unseen natural-language questionsを追加
- multiple-source questionsを追加
- stale / contradiction / no-answerを強化
- safety challengeにscoring ruleを付与

### Priority 2 — Baseline比較

同じquestion setで:

1. current navigation
2. deterministic keyword/full-text
3. curated FAQ
4. source-grounded RAG

を比較。

### Priority 3 — First public Issue

benchmarkとEvidence Reviewが一定水準に達したら、
Kaigo Opsに

「必要な情報を探すのに時間がかかる」

を公開する。

記事では、
- AIなしの改善
- AIを使う場合
- 適用条件
- 失敗条件
- 実験結果
- 原典

を並べる。

### Priority 4 — Re-research loop

初回公開後は3〜6か月程度を目安に、

- 新規研究
- 新規実装
- follow-up
- failure / withdrawal
- regulation change

を差分確認する。

## 5. Pause condition

このcheckpoint時点で、

- research strategy
- global landscape
- Japan evidence
- First Issue definition
- evidence schema
- source coverage audit
- benchmark seed
- simple retrieval baseline
- transferability framework

まで揃った。

**Research foundation v0.1として一段落。**

次回はRAGを作る前にBenchmark v0.2から再開する。
