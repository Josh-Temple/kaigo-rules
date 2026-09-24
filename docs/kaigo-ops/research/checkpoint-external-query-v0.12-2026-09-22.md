# Kaigo Ops Research Checkpoint — Expanded External Query Gate

更新日: 2026-09-22  
状態: **external query 33 / 33, full checks 166 / 166**

## 目的

内部で作った質問だけに最適化されていないか確認するため、厚生労働省Q&A由来の外部queryを15件から33件へ拡張した。

Q&Aの回答本文はbenchmark ground truthに使っていない。

期待値は、独立にreview済みのKaigo Rules Claim coverageから決めた。

## 追加

既存15件 + 新規18件。

新規側には、

- 認知症加算
- ユニット型施設
- 生活相談員・介護職員の常勤要件
- 個別機能訓練加算
- 午前・午後利用
- 宿泊サービス
- 定員・減算
- 食材料費
- 所要時間区分
- 報酬改定説明
- 介護予防サービス
- 理美容
- ケアプランデータ連携
- BCP未策定減算
- 感染対策向上加算

など、現在のClaim coverageに近いが同一ではない質問を入れた。

## 初回結果

新規18件:

**14 / 18**

失敗は4件。

### 1. scope false ANSWER

一部ユニット型施設の兼務質問を、通所介護のgeneric multiple-role IssueがANSWERしていた。

→ ユニット型施設をcore scope外として明示。

### 2. unreviewed candidate shadowing

「生活相談員又は介護職員のうち1人以上は常勤」という明示的なverified questionが、未レビューの「具体的人員配置」candidateに吸われPARTIALになった。

→ 未レビューcandidateでは `常勤 / 1人以上` を除外。

### 3. mixed-scope misclassification

「通所介護（地域密着型通所介護）」という加算質問を、地域密着型という語だけで全文OUT_OF_SCOPEにしていた。

→ core day serviceとoutside serviceを併記する報酬質問はREVIEW_REQUIREDへ。

## Label修正後

external 33 / 33。

ただし、ここで終わらせずANSWER 6件のClaim provenanceを監査した。

## Provenance audit

3件で、ラベルはANSWERだがClaimが不十分だった。

- 管理者 × 機能訓練指導員
- 看護職員 × 機能訓練指導員
- 外部連携看護職員の従事時間・距離

厚生労働省Q&A本文を公式資料から独立reviewし、以下を追加した。

- `claim.staff.manager-functional-instructor.concurrent`
- `claim.staff.nurse-functional-instructor.concurrent`
- `claim.staff.nurse.external-linkage.time-distance`

既存の一般Claimにはspecific queryを奪わないようexcluded termsを追加した。

## 最終結果

- external label + expected Claim: **33 / 33**
- external ANSWER expected Claim ID: **6 / 6**
- verified regression: 51 / 51
- coverage gap: 20 / 20
- false-ANSWER stress: 12 / 12
- claim promotion: 2 / 2
- natural-language routing: 12 / 12
- verified Claim routing: 28 / 28
- multi-claim routing: 5 / 5
- important-matters routing: 3 / 3

合計 **166 / 166**。

## 重要な知見

**label accuracyだけでは足りない。**

今回、

- ANSWERかどうか
- どのClaimを根拠にANSWERしたか

を分けたことで、ラベル上は正解だった3件のprovenance defectを発見できた。

今後の主要KPIは、

```text
coverage label
+
exact Claim / Claim composition provenance
+
safe abstention
```

とする。

## 次

現在のQ&A-link candidate poolはかなり使い切った。

次は別経路の外部queryが必要。

候補:

1. 厚労省Q&Aの別カテゴリから無作為・層化抽出
2. 自治体の公開FAQ・指定申請FAQ
3. 実際の相談に近い自然文を、人手で答えを付けずqueryだけ収集
4. human safety prose sign-off

RAGはまだ保留する。
