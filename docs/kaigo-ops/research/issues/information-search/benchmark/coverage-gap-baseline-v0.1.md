# Coverage-gap Benchmark v0.1

実行日: 2026-09-22  
状態: **pre-RAG coverage gate baseline**

## 目的

従来のbenchmarkは、

> 現在のverified 12 Issueに近い質問を正しくroutingできるか

を中心に見ていた。

しかし実利用では、

- DBにまだない
- 機械取込だけ済んでいる
- 自治体差がある
- 別サービス
- 一部だけ回答できる

質問が大量に入る。

そこでretrievalの前に、

```text
ANSWER
PARTIAL
REVIEW_REQUIRED
LOCAL
OUT_OF_SCOPE
```

を判定するcoverage layerを置く。

## 20 cases

| Class | Cases |
|---|---:|
| ANSWER | 2 |
| PARTIAL | 3 |
| REVIEW_REQUIRED | 10 |
| LOCAL | 2 |
| OUT_OF_SCOPE | 3 |
| Total | 20 |

## 現行Issue routerだけを使うとどうなるか

coverage guardなしでは20問すべてが既存12 Issueのどれかへ強制的にroutingされる。

例:

- 基本報酬 → nurse-staffing
- 地域密着型通所介護 → operation-rules-content
- 一単位単価 → operation-rules-content
- LIFE加算 → bcp-training

scoreが低くても、nearest neighborは必ず存在する。

したがって、

> **retrieval confidenceだけで「回答可能」を判定しない**

ことが重要。

## Coverage classifier v0.1

research用のdeterministic classifierを作成した。

順序:

```text
service-boundary known answer
 ↓
local authority dependency
 ↓
out-of-scope service
 ↓
known verified special case
 ↓
remuneration review gate
 ↓
unit-price review gate
 ↓
currentness gate
 ↓
unreviewed Q&A gate
 ↓
partial startup guidance
 ↓
verified Issue confidence
 ↓
otherwise REVIEW_REQUIRED
```

重要なのは、

**検索してから止めるのではなく、止めるべき領域を先に判定する**

こと。

## Expected behavior

### ANSWER

現行reviewed dataだけで中核回答が作れる。

例:
- 定員18人のservice区分
- 看護職員の外部連携

### PARTIAL

役立つ全国共通情報はあるが、完全回答にはlocal/個別条件が必要。

例:
- 開設までの大まかな流れ
- 物件契約前の確認
- 国の標準申請様式

### REVIEW_REQUIRED

sourceはあるが、現在のreview stateでは確定回答しない。

例:
- 基本報酬
- 各種加算
- LIFE
- 一単位単価
- 地域区分
- 経過措置
- 未レビューQ&A

### LOCAL

指定権者の最新運用が必要。

例:
- 横浜市の申請締切
- 自治体独自様式

### OUT_OF_SCOPE

別サービスの基準を指定通所介護から推測しない。

例:
- 地域密着型通所介護の詳細基準
- 共生型通所介護
- 療養通所介護

## Architecture update

これまで:

```text
question
 ↓
scope/review guard
 ↓
Issue router
```

より一般化すると:

```text
question
 ↓
Coverage classifier
 ├─ LOCAL
 ├─ OUT_OF_SCOPE
 ├─ REVIEW_REQUIRED
 ├─ PARTIAL
 └─ ANSWER
       ↓
    Issue router / structured data
       ↓
    linked-source expansion
       ↓
    answer
```

## Why this matters for RAG

RAGはcoverage判定を自動的には保証しない。

検索対象に未レビュー資料が存在すれば、
むしろ「もっともらしい回答」を作りやすくなる。

本プロジェクトでは、

> **coverage / review stateはmodelの外側でdeterministicに管理する**

ことを原則候補とする。

## 次

1. classifier v0.1を20件で固定
2. 既存verified questionsでfalse abstention regressionを確認
3. さらにbenign unknown questionsを増やし、false ANSWERを測る
4. safety prose templateを評価
5. その後RAG候補と比較
