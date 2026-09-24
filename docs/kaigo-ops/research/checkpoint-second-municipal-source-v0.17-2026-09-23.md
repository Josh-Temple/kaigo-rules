# Kaigo Ops Research Checkpoint — Second Municipal Source Gate

更新日: 2026-09-23  
状態: **大阪市10/10、自治体query 25/25、全191 checks PASS**

## 目的

横浜市・東京都とは別の自治体ソースを追加し、自治体固有の質問文でLOCAL境界が保たれるか確認した。

追加ソース:

- 大阪市
- 「新規介護保険事業者の指定前の確認について（Q&A）」

PDFは大阪市公式の2026年版を確認した。

自治体回答は全国ルールのground truthには使っていない。

## 追加した質問

10件。

主なテーマ:

- 指定事業者になるための要件
- 指定手続
- 法人設立前の申込
- 吸収合併・吸収分割
- 指定後に体制を整えて営業開始できるか
- 予約申込の入力
- 審査手数料
- 申請サービス種別を誤った場合
- 指定申請書類の提出方法
- 指定前に確認すべきこと

source documentのページ文脈だけに「大阪市」がある質問は、benchmark queryへ最小限「大阪市で」を補った。

これは回答内容を改変するためではなく、**LOCAL判定に必要な利用者文脈を落とさないため**。

## 初回判定

10件中6件がLOCAL。

4件が漏れた。

- MQ-016 指定事業者になる要件
- MQ-017 指定事業者になる手続
- MQ-020 先に指定を受けて後から営業開始
- MQ-025 指定前に確認すべきこと

原因は、自治体context自体は認識できていたが、LOCAL procedure vocabularyが狭かったこと。

## 修正

classifier v0.20で、**自治体contextが明示されている場合だけ**、次の語をLOCAL候補へ追加。

- 指定事業者
- 指定前
- 先に指定
- 営業開始
- 営業を開始

同じ語があっても、自治体名・都道府県市区町村・指定権者contextがなければLOCALにはしない。

## Result

- 大阪市追加10件: **10 / 10**
- 自治体query全体: **25 / 25**
- MHLW external: 33 / 33
- verified regression: 51 / 51
- coverage gap: 20 / 20
- false-ANSWER stress: 12 / 12
- claim promotion: 2 / 2
- natural-language routing: 12 / 12
- verified Claim routing: 28 / 28
- multi-claim routing: 5 / 5
- important-matters routing: 3 / 3

合計 **191 / 191**。

## 今回の設計知見

### locality is part of answerability

自治体FAQの質問だけを切り出すと、全国ルールの質問に見えるものがある。

したがって、

```text
query text
+
authority / locality context
```

を保持しないと、LOCALと全国ANSWERの境界を正しく判定できない。

今後、municipal corpusを検索対象にする場合も、自治体名・指定権者をprovenanceとして落とさない。

## 現在の正本

- Claim Registry: `claims-v0.13.json`
- Composition Registry: `claim-compositions-v0.5.json`
- Classifier: `research-coverage-classifier-v0.20.mjs`
- MHLW external sample: `external-qa-query-sample-v0.5.json`
- Municipal sample: `municipal-query-sample-v0.5.json`
- Benchmark: `benchmark-v0.17.json`

## 次

次は量を増やすより、

1. safety proseのhuman sign-off
2. source limitationのcurrent reconstruction

を優先する。

3自治体目は、新しいsemantic familyを追加できる場合だけ行う。

RAGはまだ実装しない。
