# Kaigo Ops Research Checkpoint — External Query Gate v0.5

更新日: 2026-09-22  
状態: **external-query coverage gate complete / paused before claim-registry design**

## 今回の追加

前回の82-case pre-RAG suiteに、
厚労省Q&A由来の質問文15件を追加した。

Q&A corpus自体は `INGESTED_UNREVIEWED` のため、
回答本文はground truthに使用していない。

利用したのは公開Q&Aの質問文previewのみ。

## Suite全体

合計 **97ケース**。

- v0.3: 50
- coverage gap: 20
- false-ANSWER stress: 12
- external Q&A query: 15

## 外部Q&A sampleで見つかったこと

Coverage classifier v0.2:

**10 / 15**

5件のfailure。

### False abstention
- 「兼務」ではなく「兼ねる」という自然表現を拾えない。

### False ANSWER
大Issueはverifiedだが、細目は未レビュー。

例:

- 生活相談員のサービス担当者会議時間
- 生活相談員の地域連携活動時間
- 食堂・機能訓練室の複数室合算
- 生活相談員 + 介護職員の包括的配置

## v0.3での修正

### 1. synonym
- 兼務
- 兼ねる
- 兼ね

### 2. subtopic boundary
既知Issue配下でも未レビュー細目は止める。

### 3. PARTIAL
質問の一部だけverifiedの場合はANSWERへ丸めない。

例:

生活相談員 + 介護職員の配置
→ 生活相談員部分はverified
→ 介護職員部分は現在未review
→ PARTIAL

## 回帰結果

Classifier v0.3:

- verified regression: **51 / 51**
- coverage gap: **20 / 20**
- false-ANSWER stress: **12 / 12**
- external Q&A: **15 / 15**

合計98 classification checksでexpected classを維持。

## 最も重要な知見

### Issue-level verificationでは粗い

現在:

```text
生活相談員の配置
  = verified Issue
```

だけでは足りない。

実際には:

```text
生活相談員
 ├─ 基本配置                     VERIFIED
 ├─ 必要勤務時間                 VERIFIED
 ├─ サービス担当者会議時間       UNREVIEWED
 └─ 地域連携活動時間             UNREVIEWED
```

設備も同様。

```text
食堂・機能訓練室
 ├─ 基本面積                     VERIFIED
 └─ 複数部屋の合算               UNREVIEWED
```

したがって今後は、

> **Issue → Claim/Subtopic → Source → Review state**

の構造が必要。

## Architecture更新

```text
query
 ↓
coverage category
 ↓
Issue
 ↓
Claim / Subtopic
 ↓
review state
 ↓
source relation
 ↓
answer components
 ↓
optional generation
```

LLMはclaim review stateを推測しない。

## RAGについて

まだ実装しない。

今回のfailureはembedding不足ではなく、
coverage granularity不足だった。

RAGを先に入れても、
未レビューQ&Aをもっと上手に検索してしまうだけで、
「答えてよいか」は改善しない。

## 次の優先順位

### 1. Claim registry設計

最低限:

- claim_id
- issue_id
- statement / intent
- scope
- verification_status
- source_ids
- reviewed_at
- superseded_by
- boundary / exclusions

### 2. Q&A promotion flow

```text
Q&A candidate
 ↓
human / formal review
 ↓
claim candidate
 ↓
source check
 ↓
VERIFIED claim
 ↓
benchmark追加
```

### 3. false abstention

保守的classifierが、
本当は回答可能な自然な言い換えを止めすぎないか確認。

### 4. safety prose human sign-off

現在はresearch-session PASSのみ。

### 5. RAG

claim-level coverageが明示された後に比較する。

## Productへの示唆

「このテーマは掲載済み」だけでは不十分。

利用者へは、

- ここまでは確認済み
- この細目は未確認
- この部分は自治体確認が必要

と境界を見せられる方が価値が高い。

## Pause condition

外部由来questionを使って、
内部benchmarkの楽観性を一段崩せた。

その結果、
次に必要なのがRAGではなくclaim-level data modelだと確認できた。

ここで一度区切れる。
