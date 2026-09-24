# Kaigo Ops Research Checkpoint — Municipal Claim Review

更新日: 2026-09-22  
状態: **one promotion / one deliberate abstention / 181 checks PASS**

## 今回の対象

自治体query gateで見つかった未確認論点から、まず次を独立reviewした。

- 重要事項変更時の再説明・同意
- 機能訓練指導員の提供日・単位ごとの配置

自治体回答はground truthに使用せず、厚生労働省の現行基準・資料を確認した。

## 機能訓練指導員

新規Claim:

`claim.staff.functional-instructor.not-per-day-unit`

status:

`VERIFIED_INTERPRETATION / ANSWER`

現行基準第93条は、指定通所介護事業所ごとに置く従業者として機能訓練指導員を「一以上」と規定する。

同じ条文で、

- 生活相談員: 提供日ごと
- 看護職員: 単位ごと
- 介護職員: 単位ごと

という条件は明示されている。

機能訓練指導員には同じ限定がないため、基本人員基準については「サービス提供日ごと・単位ごとに一名以上」という要件ではない、と狭く固定した。

ただし、個別機能訓練加算などの報酬要件は別。

## 重要事項変更時

`review.important.change-consent`

は **REVIEW_REQUIREDを維持**。

第8条・第105条は提供開始前の説明・同意を明示する。

厚労省の文書負担軽減資料には変更時の重要事項説明書が登場するが、「すべての変更について改めて文書同意が必要」という全国一律の拘束的ルールまで確認できない。

したがって、

`提供開始前の同意claim → 変更時にも必ず再同意`

とは拡張しない。

## 追加探索

### 理美容

厚労省Q&Aでは、通所サービスと明確に区分できれば、理美容は必ずしもサービス開始前・終了後に限られない。

ただし自治体query MQ-002は「介護職員が散髪する」ため、理美容サービスの時間区分だけでは答えられない。REVIEW_REQUIREDを維持。

### 訪問診療

併設医療機関受診については、サービス提供時間中は緊急やむを得ない場合を除き認めないQ&Aがある。

しかしMQ-003は訪問診療・訪問歯科というより広い質問であり、同じ規律を無条件に一般化しない。REVIEW_REQUIREDを維持。

### 外出レクリエーション

厚労省解釈通知には、通所介護は原則事業所内だが、一定条件では屋外提供が可能とある。

また2018年通知は、

- 通所介護計画に位置づけられた機能訓練としての外出
- 利用者個人の希望による保険外の外出支援

を区別している。

次のClaim候補として有力だが、MQ-004/005へ答える射程をもう一段固定してから昇格する。

## Regression

- municipal query: 15 / 15
- MHLW external query: 33 / 33
- verified regression: 51 / 51
- coverage gap: 20 / 20
- false-ANSWER stress: 12 / 12
- claim promotion: 2 / 2
- natural-language routing: 12 / 12
- verified Claim routing: 28 / 28
- multi-claim routing: 5 / 5
- important-matters routing: 3 / 3

合計 **181 / 181**。

## 現在の正本

- Claim Registry: `claims-v0.10.json`
- Composition Registry: `claim-compositions-v0.3.json`
- Classifier: `research-coverage-classifier-v0.16.mjs`
- Municipal sample: `municipal-query-sample-v0.2.json`
- Benchmark: `benchmark-v0.14.json`

## 次

次は外出サービスのClaim boundaryを固定する。

その後、

- 理美容の「誰が提供できるか」
- 訪問診療・訪問歯科
- 別自治体のquery

へ進む。

RAGはまだ実装しない。
