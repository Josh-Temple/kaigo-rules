# Benchmark v0.3 — 50-case Non-RAG Baseline

実行日: 2026-09-22  
状態: **v0.3 fixed**

## 1. Test set

合計50件。

- retrieval / synthesis: 39
  - unseen: 18
  - multi-source: 6
  - natural variant: 13
  - cross-issue: 2
- safety / fail-closed: 11

RAGは使用していない。

## 2. Retrieval result

39問:

| Metric | Result |
|---|---:|
| FAQ / Issue Hit@1 | 92.3% |
| FAQ / Issue Hit@3 | **100%** |
| Direct trusted-source mean Recall@5 | 89.5% |
| Direct trusted-source Complete@5 | 82.1% |
| Top3 Issue → linked-source mean recall | **100%** |
| Top3 Issue → linked-source complete | **100%** |

### v0.2から変わった点

質問を15件増やすと、FAQ top-1は95.8% → 92.3%へ低下した。

これは良い方向の劣化。

より自然な質問では、

- 「感染症研修」→ BCP研修
- 「計画の説明・同意・交付」→ 署名
- 「感染症 + 虐待防止研修」→ BCP

のように、近いIssueへtop-1が寄る。

一方、正しいIssueは全件top-3内に残った。

## 3. Direct source searchの限界

direct source search:

- mean Recall@5: 89.5%
- Complete@5: 82.1%

つまり関連資料はかなり拾えるが、

> 必要な根拠を全部揃える

ところで落ちる。

これは特に、
- 準用関係
- 複数研修
- 複数職種
- 説明 + 同意 + 交付
などで起きやすい。

## 4. Existing relation graphの価値

Top3 Issueから既存の

- rule_node_ids
- notice_node_ids
- qa_item_ids

を展開すると、今回の39問ではgold sourceを100%回収した。

したがって、現時点のstrong baselineは、

```text
query
 ↓
Issue router
 ↓
top 3
 ↓
ambiguity / scope / review guard
 ↓
explicit linked-source expansion
 ↓
currentness / verification filter
 ↓
answer
```

とする。

## 5. Safety guard

11件について、deterministic guard/decision baselineを作成した。

対象:

- 自治体固有
- 初期scope外
- 未レビュー報酬
- 未レビュー単価
- currentness未確認の経過措置
- Q&A corpusのreview status
- 看護職員の条件落ち
- 生活相談員の条件落ち
- false premise
- 短い曖昧質問

prototype実行ではdecision-levelで **11/11** が期待decisionに一致した。

重要:

これは生成文章の品質を11/11と評価したものではない。

確認したのは、

- answerしてよい
- abstainすべき
- clarificationすべき
- metadata statusを返すべき

というdecision layer。

## 6. Fail-closed guardの構造

production候補ではなくresearch baselineとして、

### Local
自治体固有の指定申請・締切等を全国共通DBから推測しない。

### Scope
地域密着型通所介護・共生型通所介護等、現在のcore scope外を通常の通所介護から推測しない。

### Review
review statusが未完了なら、
機械取込データを確定情報へ昇格させない。

### Currentness
経過措置など時点依存情報でcurrent reconstruction未完了なら停止。

### Provenance
`INGESTED_UNREVIEWED` を「確認済み」と表示しない。

### Ambiguity
短く、複数Issueのscoreが近い質問は確認質問へ回す。

## 7. Answer composition

free-form generationはまだ行わない。

verified routeでは、

- top-ranked Issue
- scoreがtop1の80%以上の近接Issue
- linked sources

をanswer componentsとして返す設計にした。

これは最終UIではなく、
「どのverified knowledgeだけを回答材料にしたか」を追えるようにするため。

## 8. 現時点の判断

### RAGはまだ不要

Benchmarkを50件へ増やしても、

- Issue Hit@3 100%
- relation expansion source completeness 100%

だった。

RAGの導入理由をまだ確認できていない。

### 次に必要なのはcoverage stress

今のtestは、既存verified coverageを知った上で作成している。

したがって次の重要課題は、

> 既存12 Issueで答えられない、または境界にある質問を増やす

こと。

「既知Issueへうまくroutingできるか」だけでは、
現実の検索体験を代表しない。

## 9. 次のGate

次は二つに分ける。

### A. Coverage-gap benchmark

- 現在DBにないが利用者が聞きそうな質問
- 部分的にしか答えられない質問
- 自治体差が大きい質問
- 報酬 / 加算
- Q&A only
- 改正差分

を収集し、

`ANSWER / PARTIAL / REVIEW_REQUIRED / LOCAL / OUT_OF_SCOPE`

を正しく分類できるか測る。

### B. Human answer review

現在の11 safety caseについて、
deterministic answer componentsから作る回答文を人が採点する。

特に、
- 条件を落とさない
- 不要な関連Issueを混ぜない
- 出典状態を正しく説明
を確認する。

この二つができるまでRAG比較へ進まない。
