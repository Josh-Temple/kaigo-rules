# Kaigo Ops Research Checkpoint — Hairdressing / Visiting Medical Boundary

更新日: 2026-09-23  
状態: **hairdressing boundary complete / visiting medical intentionally held / 181 checks PASS**

## 対象

前回残した次の2論点を、厚生労働省の全国資料だけで独立reviewした。

- MQ-002: 通所介護提供時間中に介護職員が利用者の散髪を行えるか
- MQ-003: 通所介護提供時間中に医師・歯科医師の訪問診療を受けられるか

あわせて、MHLW外部query EQ-028「理美容は開始前・終了後に限るか」を再reviewした。

## 理美容

理美容は3層に分けた。

### 1. 介護保険上の区分

`claim.service.hairdressing.not-covered`

`VERIFIED_SOURCE_TEXT / ANSWER`

- 理美容は通所介護には含まれない
- 通所介護とは別サービスとして明確に区分する
- 開始前・終了後だけに限られない
- 通所介護を一旦中断して理美容を提供し、その後再開できる
- 理美容に要した時間は通所介護の提供時間に含めない

### 2. 提供者の免許

`claim.hairdressing.license-required`

`VERIFIED_SOURCE_TEXT / ANSWER`

頭髪の刈込等の理容を反復継続の意思をもって業として行うには理容師免許が必要。

美容に該当するカッティング等も美容師免許が必要。

「業」は有料・無料を問わない。

したがって、**介護職員資格そのものが理容師・美容師免許の代わりになるわけではない。**

### 3. デイサービス内という場所

`claim.hairdressing.outcall-location-conditions`

`VERIFIED_CURRENT / ANSWER`

理容・美容は原則として理容所・美容所で行う。

事業所以外で行えるのは、

- 疾病その他の理由で来店できない者等
- 法令上のその他の例外
- 自治体条例で追加された場合

など。

デイサービス利用者であるだけで自動的に出張理美容対象とはしない。

## MQ-002

単一Claimでは足りないため、

`composition.service.hairdressing.by-care-worker`

を追加。

- 保険内外区分
- 免許
- 出張場所要件

の3 Claimを同時に返す。

既存Issueに無理に紐付けると誤ったtaxonomyになるため、compositionに `issue_id: null` を許すようrouter/validatorも一般化した。

## EQ-028

従来 REVIEW_REQUIRED だったが、全国通知を直接確認した結果 ANSWERへ更新。

「理美容は開始前・終了後だけに限られない」が確認できたため。

## 訪問診療・訪問歯科

`review.service.visiting-medical-dental.in-service`

は **REVIEW_REQUIREDを維持**。

全国資料では、

- 併設医療機関受診
- 巡回健診・予防接種・採血
- オンライン診療

について個別ルールを確認できる。

しかし、それらを一般的な対面の訪問診療・訪問歯科へ一律に一般化するには根拠が不足する。

したがってMQ-003は止める。

## Regression

- verified regression: 51 / 51
- coverage gap: 20 / 20
- false-ANSWER stress: 12 / 12
- MHLW external query: 33 / 33
- claim promotion: 2 / 2
- natural-language routing: 12 / 12
- verified Claim routing: 28 / 28
- multi-claim routing: 5 / 5
- important-matters routing: 3 / 3
- municipal query: 15 / 15

合計 **181 / 181**。

## 現在の正本

- Claim Registry: `claims-v0.13.json`
- Composition Registry: `claim-compositions-v0.5.json`
- Classifier: `research-coverage-classifier-v0.19.mjs`
- MHLW external sample: `external-qa-query-sample-v0.5.json`
- Municipal sample: `municipal-query-sample-v0.4.json`
- Benchmark: `benchmark-v0.16.json`

## 次

次回の自然な作業は、

1. 別自治体の外部queryを追加
2. safety proseのhuman sign-off
3. source limitationのcurrent reconstruction

この3つ。

RAGはまだ実装しない。
