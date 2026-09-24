# Kaigo Ops Research Checkpoint — Important Matters Claims / Current Suite Coverage

更新日: 2026-09-22  
状態: **current suite claim coverage complete / 148 checks PASS**

## 今回の対象

Issue fallbackに残っていた3件:

- 重要事項説明書は国が決めた様式を使う必要があるか
- 国のひな形でなければならないか
- 重要事項説明書には何を記載するか

これらをrouting語彙追加だけで処理せず、公式資料を独立reviewした。

## 公式資料から確認したこと

指定通所介護には基準第105条で第8条が準用される。

第8条は、重要事項を記した文書を交付して説明し、提供開始について同意を得ることを求める。

解釈通知は、その文書について、

- 運営規程の概要
- 従業者の勤務体制
- 事故発生時の対応
- 苦情処理の体制
- その他、利用申込者がサービスを選択するために必要な重要事項

を、わかりやすい説明書やパンフレット等で示す趣旨としている。

## 新規Claim

### claim.important.no-fixed-national-form

status:

`VERIFIED_INTERPRETATION / ANSWER`

固定した射程:

全国共通の指定通所介護基準・解釈通知は、特定の一つの固定様式の使用までは求めていない。

ただし、

- 自治体の標準例・独自様式
- 自治体独自の追加記載事項
- 国が参考様式を一切公開していないか

まではこのClaimから推測しない。

また、有料老人ホームでは厚生労働省が明示的な別紙様式を定めているため、別制度として区別する。

### claim.important.document-content-core

status:

`VERIFIED_SOURCE_TEXT / ANSWER`

重要事項文書の中核内容として、運営規程概要、勤務体制、事故対応、苦情処理体制等を保持する。

「等」であるため、完全な全国共通チェックリストとは断定しない。

## Result

新規3ケース:

- 3 / 3 PASS
- 期待Claim IDまで一致

全体:

- verified regression: 51 / 51
- coverage gap: 20 / 20
- false-ANSWER stress: 12 / 12
- external Q&A: 15 / 15
- claim promotion: 2 / 2
- natural-language routing: 12 / 12
- verified Claim routing: 28 / 28
- multi-claim routing: 5 / 5
- important-matters routing: 3 / 3

合計 **148 / 148**。

## Issue fallback

current verified regressionでは **0 / 51**。

ただし、これはproduction coverageが完成したという意味ではない。

現在のsuite内で、

- 単一Claim質問 → Claim
- 複数Claim質問 → composition
- coverage外 → abstain / REVIEW_REQUIRED

へ移せたというだけ。

次は外部queryを増やして、この構造が未知の自然言語でも維持されるかを確認する。

## RAG

まだ実装しない。

次のgateは外部query拡張。
