# Kaigo Ops Research Checkpoint — Pre-RAG Gate v0.4

更新日: 2026-09-22  
状態: **82-case pre-RAG suite complete / paused before external-query sampling**

## 1. 今回の到達点

これまでのbenchmarkを、検索精度だけでなく、

- 既知Issueを探せるか
- 必要根拠を揃えられるか
- 答えてよい範囲か
- 未レビュー資料で止まれるか
- 似ているが別論点の質問を誤ANSWERしないか
- 止まる場合も利用者に役立つ説明を返せるか

まで拡張した。

## 2. Suite

合計 **82ケース**。

### A. v0.3 — 50

- retrieval / synthesis: 39
- safety: 11

主結果:

- Issue Hit@1: 92.3%
- Issue Hit@3: 100%
- direct source mean Recall@5: 89.5%
- direct source Complete@5: 82.1%
- Top3 Issue → linked-source complete: 100%
- safety decision: 11 / 11

### B. Coverage gap — 20

分類:

- ANSWER
- PARTIAL
- REVIEW_REQUIRED
- LOCAL
- OUT_OF_SCOPE

結果:

**20 / 20 expected class**

既存Issue routerだけでは、
coverage外質問も必ずどこかへnearest-neighbor routingされることを確認した。

例:

- 基本報酬 → nurse-staffing
- 地域密着型通所介護 → operation-rules-content
- LIFE加算 → bcp-training

これにより、
retrievalの前にcoverage classificationが必要だと確認。

### C. False-ANSWER stress — 12

verified Issueに語彙が近いが、
現在は回答対象ではない質問。

例:

- 機能訓練指導員の資格
- 非常災害対策計画
- 介護職員の資格
- 営業時間変更届
- 管理者不在時の代替

#### v0.1

score thresholdだけ:

**7 / 12**

5件を誤ってANSWER。

#### v0.2

verified intent signatureを追加:

- verified regression: **51 / 51**
- false-answer stress: **12 / 12**
- coverage gap: **20 / 20**

## 3. 重要な設計原則

### Similarity ≠ Answerability

検索scoreは、
どのIssueに近いかを探すために使う。

答えてよいかは別判定。

### Model外で持つもの

- service scope
- local dependency
- human review status
- source currentness
- verified intent
- explicit source relation

これらをLLMの推測へ委ねない。

## 4. 現時点のarchitecture

```text
question
 ↓
coverage / scope / review / currentness gate
 ├─ LOCAL
 ├─ OUT_OF_SCOPE
 ├─ REVIEW_REQUIRED
 ├─ PARTIAL
 └─ ANSWER candidate
       ↓
   Issue similarity routing
       ↓
   verified intent signature
       ↓
   top-k ambiguity handling
       ↓
   explicit linked-source expansion
       ↓
   verified answer components
       ↓
   optional generation
```

生成AIは一番最後。

## 5. Safety prose

11 safety casesについて定型回答を作成。

research-session rubricでは:

- hard fail: 0 / 11
- template PASS: 11 / 11
- human sign-off: **PENDING**

重要:

これは人による確認済みという意味ではない。

production前には人による最終確認を行う。

## 6. RAG判断

### 現段階では実装しない

理由:

1. 既知coverageではnon-RAG baselineが強い。
2. 現在の主なfailureはretrieval能力不足ではなくcoverage誤認。
3. RAGを入れると未レビューcorpusからもっともらしい回答を作る危険が増える。
4. explicit relation graphが複数根拠回収に効いている。

RAGの比較価値が出るのは、

- source graphが未整備
- 新しいIssue
- 大規模corpus
- natural-language coverage expansion

へ進んでから。

## 7. 次の研究課題

### Priority 1 — external / realistic query sampling

現在のquestion setは、
このDBの構造を知っている状態で作成したものが多い。

次は、

- 公開FAQの質問文
- 開業相談で一般に出る質問
- 検索query風の短文
- 初心者の曖昧な聞き方

などから、現在の12 Issueを見ずにquestion setを作る。

### Priority 2 — false abstention

v0.2 coverage classifierは保守的。

未知の自然な言い換えを
REVIEW_REQUIREDへ落としすぎないか測る。

### Priority 3 — human sign-off

11 safety proseの最終確認。

### Priority 4 — Review queue

REVIEW_REQUIREDとなった質問を、

> 何のsourceを確認すればANSWERへ昇格できるか

へつなげる。

これはDB拡張の優先順位にも使える。

### Priority 5 — RAG candidate

上記が終わってから、

non-RAG baselineと同じsuiteで比較する。

## 8. Productへの示唆

ユーザーにとって価値があるのは、
何でも回答することではない。

```text
確認済み → 根拠付きで回答
一部確認済み → どこまで分かるか回答
未レビュー → 現在の状態を説明
自治体依存 → 正しい確認先を示す
範囲外 → 混同せず分ける
```

という挙動自体が、
介護制度情報サイトの信頼性になる。

## 9. Pause condition

- 82-case suite
- coverage classifier
- false-answer stress
- intent-gated routing
- safety prose templates
- pre-RAG architecture

まで固定した。

次は外部・実利用に近いquery sampleから再開する。
