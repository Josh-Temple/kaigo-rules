# External Q&A Query Sample v0.1

実施日: 2026-09-22  
source: 厚労省Q&A corpusから生成済みの `qa-link-candidates.json`

## 重要な方法

Q&A corpus本体は現在 `INGESTED_UNREVIEWED`。

したがって、

**回答内容をground truthには使わない。**

利用したのは公開Q&Aの質問文previewのみ。

目的:

> 現在のverified DBを知らない外部由来の聞き方を、
> coverage classifierへ入力したらどうなるか。

expected labelは、
現在別途確認済みのKaigo Rules coverageだけを基準に付けた。

## Sample

15問。

主な論点:

- 管理者と機能訓練指導員の兼務
- 管理者の責務
- 生活相談員 + 介護職員の配置
- サービス担当者会議時間
- 地域連携時間
- 外部看護職員
- 個別機能訓練加算
- 複数部屋の面積
- 定員例外
- 運営規程
- 所要時間区分

## Coverage classifier v0.2

結果:

**10 / 15**

内部benchmarkでは見えなかった5 failureが出た。

### False abstention

#### EQ-001
管理者が機能訓練指導員を「兼ねる」。

既存signatureが「兼務」という表現に寄っており、
「兼ねる」を拾えなかった。

対策:
- natural synonymを追加。

### False ANSWER

#### EQ-003
生活相談員 + 介護職員の具体的人員配置。

生活相談員部分はverifiedだが、
介護職員配置まで現在のverified answerは覆っていない。

→ **PARTIAL**

#### EQ-004
生活相談員のサービス担当者会議参加時間。

生活相談員の大テーマはverifiedでも、
勤務延時間に含められる活動のQ&A細目は未レビュー。

→ **REVIEW_REQUIRED**

#### EQ-005
生活相談員の地域連携活動時間。

同様。

→ **REVIEW_REQUIRED**

#### EQ-010
食堂・機能訓練室を複数室の合計面積で満たせるか。

基本面積はverifiedだが、
「複数室合算」のQ&A解釈は未レビュー。

→ **REVIEW_REQUIRED**

## Classifier v0.3

追加:

### Synonym expansion

- 兼務
- 兼ねる
- 兼ね

### Reviewed boundary

大Issueがverifiedでも、
未レビューのQ&A subtopicへ踏み込む場合は止める。

追加boundary:

- 生活相談員 × サービス担当者会議
- 生活相談員 × 地域連携 / 社会資源
- 生活相談員 + 介護職員の包括配置
- 食堂・機能訓練室 × 複数部屋合算

### Remuneration gate

「加算」「減算」だけでなく「算定」を含むquestionも、
報酬review未完了なら先に止める。

## v0.3 expected regression

対象:

- verified regression: 51
- coverage gap: 20
- false-answer stress: 12
- external Q&A: 15

合計 **98 classification checks**。

設計上は全setのexpected labelを維持するよう固定した。

## 新しい知見

### Issueがverifiedでも、その下位論点までverifiedとは限らない

これは重要。

```text
人員基準
 └─ 生活相談員
      ├─ 基本配置 ← verified
      ├─ サービス担当者会議の時間 ← unreviewed
      └─ 地域連携活動の時間 ← unreviewed
```

同様に、

```text
設備基準
 └─ 食堂・機能訓練室
      ├─ 基本面積 ← verified
      └─ 複数室合算 ← unreviewed
```

となる。

したがってcoverageはIssue単位のbooleanではなく、
将来的には **claim / subtopic単位** で持つ方がよい。

## Architectureへの変更

```text
query
 ↓
coverage category
 ↓
Issue
 ↓
subtopic / claim boundary
 ↓
review state
 ↓
source relation
 ↓
answer
```

Issue単位の「verified」だけでは粗すぎる。

## 次

この結果は、次のDB設計に直接つながる。

- verified claim registry
- subtopic ID
- claim-level review status
- Q&A candidate → claim promotion

を検討する。
