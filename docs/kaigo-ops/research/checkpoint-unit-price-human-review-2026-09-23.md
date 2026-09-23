# Kaigo Ops Research Checkpoint — Unit Price Human Review

更新日: 2026-09-23  
対象: `review.unit-price.region-and-rate`  
判定: **ANSWER / VERIFIED_CURRENT**

## Source of truth

厚生労働大臣が定める一単位の単価
（平成27年3月23日 厚生労働省告示第93号）

current official HTML:
https://www.mhlw.go.jp/web/t_doc?dataId=82ab4582&dataType=0&pageNo=1

repo source id:
`mhlw-unit-price-current`

reviewed source SHA-256:
- `6aab4a9fdce647a6415bca5d56fc482d648b4b711e822f0468f7ea13502e3395`
- `815f61dbc573e2e7319bb86e7da9cd19703b0670c85f07ec6b38af9768528e88`

## 1. 通所介護の一単位単価

現行公式表と `data/unit-price-dayservice.json` を全8区分照合した。

| 地域区分 | 告示割合 | 一単位単価 |
| --- | ---: | ---: |
| 一級地 | 1090 / 1000 | 10.90円 |
| 二級地 | 1072 / 1000 | 10.72円 |
| 三級地 | 1068 / 1000 | 10.68円 |
| 四級地 | 1054 / 1000 | 10.54円 |
| 五級地 | 1045 / 1000 | 10.45円 |
| 六級地 | 1027 / 1000 | 10.27円 |
| 七級地 | 1014 / 1000 | 10.14円 |
| その他 | 1000 / 1000 | 10.00円 |

8 / 8 一致。

## 2. 地域割当

現行公式表の一級地〜七級地を、
`data/unit-price-region-assignments.json`
と都道府県単位で全件照合した。

一致件数:
- 一級地: 1
- 二級地: 7
- 三級地: 29
- 四級地: 24
- 五級地: 59
- 六級地: 137
- 七級地: 170

合計:
**427 / 427**

また、
- 一級地〜七級地以外は「その他」
- 「その他」の通所介護は10.00円
- 地域の名称・区域は令和6年4月1日時点を基準とし、その後の名称又は区域の変更で影響されない

ことを確認した。

## 3. 所在地基準

告示本文は、一単位単価を、
サービスを行う事業所又は介護保険施設が所在する地域区分に応じて定める。

したがって、指定通所介護では利用者住所ではなく、
事業所所在地の地域区分を用いる。

例:
- 横浜市: 二級地
- 通所介護: 10.72円 / 1単位

## 4. Review ledger

`data/unit-price-review.json`:
- review_status: COMPLETE
- reviewed_rate_ids: 8 / 8
- reviewed_assignment_ids: 427 / 427
- reviewed_default_rule: true

生成データそのものの verification_status は書き換えず、
生成層とhuman review ledgerを分離する設計を維持する。

## 5. Drift guard

`scripts/research-unit-price-review-validate-v0.1.mjs` を追加した。

CIで以下をfail closedに確認する:
- review source SHA == current imported source SHA
- reviewed rate IDs == current rate IDs
- reviewed assignment IDs == current assignment IDs
- rate count == 8
- assignment count == metadata count
- default rule reviewed
- assignmentが参照するunit price IDが現行rate setに存在

公式ソースまたは生成データが変わった場合、
過去のCOMPLETEをそのまま使わない。

## 6. Claim / benchmark

`claims-v0.21.json`:
- `review.unit-price.region-and-rate`
- REVIEW_REQUIRED → ANSWER
- REVIEW_REQUIRED → VERIFIED_CURRENT

`coverage-gap-v0.2.json`:
- CG-010 → ANSWER
- CG-011 → ANSWER
- CG-019 → ANSWER

classifier:
- `research-coverage-classifier-v0.29.mjs`

post-change GitHub Actionsで回帰とreview-ledger validatorを確認する。
