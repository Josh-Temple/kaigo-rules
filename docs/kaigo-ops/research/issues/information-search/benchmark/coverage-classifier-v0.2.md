# Coverage Classifier v0.2 — False-ANSWER Stress

実行日: 2026-09-22  
状態: research baseline

## 問題

Coverage classifier v0.1は20件のcoverage-gapには20/20で一致し、
既存verified Issueも12/12でANSWERを維持した。

しかし「既知Issueに似ているが、実際には別論点」の12問を追加すると、

- pass: 7 / 12
- false ANSWER: 5 / 12

だった。

誤ANSWER例:

| Question | 誤って寄ったIssue |
|---|---|
| 機能訓練指導員になれる資格 | multiple-roles |
| 非常災害対策計画の内容 | operation-rules-content |
| 介護職員の資格要件 | life-counselor-staffing |
| 営業時間変更時の変更届 | operation-rules-content |
| 管理者不在時の代替管理者 | manager-concurrent-role |

単純なTF-IDF score thresholdでは防げなかった。

## 対策

各verified Issueに **intent signature** を追加した。

例:

### manager-concurrent-role

必要:

- 「管理者」
- かつ「兼務 / 他の職務 / 別の事業所」等

「管理者」という語だけではANSWERしない。

### multiple-roles

必要:

- 「兼務 / 複数職種 / 別職種」
- かつ職種・職員語

「機能訓練指導員 + 資格」では使わない。

### operation-rules-content

必要:

- 「運営規程」
- かつ「記載 / 項目 / 内容」等

単に「計画」「営業時間」という語が近くても使わない。

## v0.2 test

intent signatureを加えた結果:

- v0.3 retrieval 39問 + canonical 12問 = **51 / 51 coverage維持**
- false-ANSWER stress = **12 / 12 REVIEW_REQUIRED**
- coverage-gap 20問 = **20 / 20 expected class**

この結果は小規模で手作業のtestなので、本番精度ではない。

ただし設計上の重要な示唆がある。

## 設計原則

```text
similarity ≠ answerability
```

similarityは、

> 「どのIssueに近いか」

には使える。

しかし、

> 「そのIssueで答えてよいか」

の判定には使わない。

ANSWERへ進むには、

1. coverage gateを通過
2. review/currentness gateを通過
3. verified intent signatureに一致
4. linked sourceが存在

を要求する。

## Architecture v0.2

```text
question
 ↓
coverage / scope / review gate
 ↓
Issue similarity routing
 ↓
verified intent signature
 ├─ match → ANSWER candidate
 └─ no match → REVIEW_REQUIRED
 ↓
linked-source expansion
 ↓
answer components
```

## Trade-off

intent signatureは保守的。

新しい自然な言い回しを
REVIEW_REQUIREDへ落とすfalse abstentionが増える可能性がある。

本プロジェクトでは現段階で、

> **false ANSWERよりfalse abstentionを優先して許容する**

方針とする。

制度情報では、未確認のまま回答するより
「現在の確認済み範囲では確定できない」と返す方が安全。

## 次

- benign paraphraseを増やしてfalse abstentionを測る
- intent signatureをdataとして外出しする
- manual prose review
- production UXではREVIEW_REQUIREDを単なる「回答不可」にせず、次に確認すべきsource/actionを返す
