# Kaigo Ops Research Checkpoint — Remuneration Base Notice Review

更新日: 2026-09-23  
対象: 厚生省告示第19号「6 通所介護費」  
判定: **base notice COMPLETE / overall remuneration review IN_PROGRESS**

## current source

指定居宅サービスに要する費用の額の算定に関する基準
（平成12年厚生省告示第19号）

current official HTML:
https://www.mhlw.go.jp/web/t_doc?dataId=82aa0253&dataType=0&pageNo=1

repo:
- source id: `mhlw-fee-notice19-base`
- source SHA-256: `e189120c253f72d2d5dab24dfe7118bad7d602f0baba3d8cdf98a58c7ecc5bbd`
- current amendment: 令和8年厚生労働省告示第87号
- effective: 2026-06-01

## reviewed scope

`data/remuneration-current-text.json` の29レコードを確認。

- 通常規模型
- 大規模型(I)
- 大規模型(II)
- 注1〜24
- サービス提供体制強化加算
- 介護職員等処遇改善加算

29 / 29 の fee_id と text_sha256 を
`data/remuneration-review.json` に固定した。

## examples checked

通常規模型・7時間以上8時間未満:
- 要介護1: 658単位
- 要介護2: 777単位
- 要介護3: 900単位
- 要介護4: 1,023単位
- 要介護5: 1,148単位

サービス提供体制強化加算:
- (I): 22単位
- (II): 18単位
- (III): 6単位

令和8年6月1日以降の介護職員等処遇改善加算:
- (I)イ: 111 / 1000
- (I)ロ: 120 / 1000
- (II)イ: 109 / 1000
- (II)ロ: 118 / 1000

## why overall is not COMPLETE

告示第19号だけでは次を閉じられない。

- 利用者数超過・人員欠如時の算定: 告示第27号
- 各種加算・減算の委任基準: 告示第95号等
- 算定上の運用・解釈: 老企第36号
- 令和8年改正を含む現行留意事項の再構成

したがってoverall `review_status` は IN_PROGRESS。

## drift guard

`scripts/research-remuneration-base-review-validate-v0.1.mjs`

CIで:
- review source SHA == current import source SHA
- records == 29
- reviewed fee IDs == current fee IDs
- reviewed text SHA == current text SHA

を確認する。

次:
1. 告示第27号3 nodeを照合
2. 告示第95号14 nodeを照合
3. delegated reviewをCOMPLETE
4. 老企第36号reviewへ接続
