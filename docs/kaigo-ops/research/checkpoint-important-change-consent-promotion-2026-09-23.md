# Kaigo Ops Research Checkpoint — Important Matters Change / Consent

更新日: 2026-09-23  
対象: `review.important.change-consent`  
判定: **ANSWER / VERIFIED_INTERPRETATION**

## 問い

重要事項説明書の内容が変わった場合、全国共通の指定通所介護の運営基準として、
すべての変更について改めて文書による同意が必要か。

## 独立review

既存の自治体Q&AやClaimを正解として確認せず、
厚生労働省のcurrent一次資料から確認した。

### 厚生省令第37号 第8条

https://www.mhlw.go.jp/web/t_doc?dataId=82999404&dataType=0&pageNo=1

第8条第1項は、「提供の開始に際し、あらかじめ」重要事項を記した文書を交付して説明し、
「当該提供の開始について」利用申込者の同意を得ることを定める。

### 第105条

https://www.mhlw.go.jp/web/t_doc?dataId=82999404&dataType=0&pageNo=2

第105条により第8条は指定通所介護へ準用される。

### 老企第25号

https://www.mhlw.go.jp/web/t_doc?dataId=00ta4369&dataType=1

第8条の解釈は、サービス提供開始時に重要事項を説明し、
当該事業所からサービス提供を受けることについて同意を得る趣旨と説明している。
同意は、双方の保護の立場から書面で確認することが望ましいとされる。

## 変更時文書に関する補助資料

厚生労働省の文書負担軽減関連資料:
https://www.mhlw.go.jp/content/12300000/000692165.pdf

通所介護事業所の文書例として「重要事項説明書（変更時）」が示されている。
これは変更時に重要事項説明書を扱う実務があることを示すが、
この図だけから「内容が変わるたびに、すべての変更について新たな文書同意が全国一律に必須」とは判定しない。

令和3年度介護報酬改定資料:
https://www.mhlw.go.jp/content/12404000/000768899.pdf

説明・同意について、電磁的対応を原則認め、
署名・押印を求めないことが可能であることと代替手段を明示する見直しが行われた。

## Claim判定

狭い全国共通Claimとして、次をANSWER可能とする。

> 全国共通の指定通所介護の運営基準では、重要事項説明書の内容が変更されるたびに、すべての変更について改めて文書による同意を得なければならないという一律の規定は確認できない。第8条（第105条で準用）が直接求めるのは、サービス提供開始時に重要事項を文書で説明し、当該提供の開始について同意を得ることである。

verification_statusは `VERIFIED_INTERPRETATION` とする。
「不存在」を条文が明示しているわけではなく、current条文と解釈通知の射程を限定して読む判断だからである。

## boundary

このClaimから次を推測しない。

- 変更時の説明・通知は一切不要
- 契約内容の変更について利用者の合意が不要
- 報酬・加算等の別要件による説明・同意が不要
- 指定権者の様式・運用を無視してよい
- 「署名・押印不要」と「同意不要」は同じ

変更内容に別の法令上の手続、契約上の合意、報酬要件、指定権者の運用がある場合は個別に確認する。

## Registry / benchmark

`claims-v0.19.json`:
- `review.important.change-consent`
- REVIEW_REQUIRED → ANSWER
- REVIEW_REQUIRED → VERIFIED_INTERPRETATION

`municipal-query-sample-v0.6.json`:
- MQ-001 expected: REVIEW_REQUIRED → ANSWER
- expected_claim_idは維持

classifier:
- `research-coverage-classifier-v0.27.mjs`

post-change CIで回帰を確認する。
