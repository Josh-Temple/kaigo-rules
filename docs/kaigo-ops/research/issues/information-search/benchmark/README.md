# Information Retrieval Benchmark

作成日: 2026-09-22  
状態: **Claim Registry v0.21 / corrected regression harness v0.29 / RAG deferred**

## 現在のsuite

合計 **190ケース**。

- `benchmark-v0.3.json`: 50
- `coverage-gap-v0.1.json`: 20
- `false-answer-stress-v0.1.json`: 12
- `external-qa-query-sample-v0.8.json`: 33
- `claim-promotion-benchmark-v0.1.json`: 2
- `claim-routing-natural-language-v0.1.json`: 12
- `verified-claim-routing-probe-v0.1.json`: 28
- `multi-claim-routing-v0.1.json`: 5
- `important-matters-claim-routing-v0.1.json`: 3
- `municipal-query-sample-v0.6.json`: 25

索引:

- `benchmark-v0.7.json`

## 主結果

### Known coverage

- Issue Hit@1: 92.3%
- Issue Hit@3: 100%
- direct source Complete@5: 82.1%
- linked-source complete: 100%

### Coverage / safety

- coverage gap: 20 / 20
- false-ANSWER stress: 12 / 12
- external MHLW Q&A label + Claim: 33 / 33
- claim promotion paraphrase: 2 / 2
- claim routing natural language: 12 / 12
- verified Claim routing: 28 / 28
- multi-claim routing: 5 / 5
- important matters Claim routing: 3 / 3
- external ANSWER expected Claim ID: 6 / 6
- municipal query label + provenance: 25 / 25
- verified regression Issue fallback: 0 / 51
- classifier checks baseline: 191 / 191
- verified regression: 51 / 51

### Safety prose

- research-session template review: 11 / 11 PASS
- human sign-off: PENDING

## 最重要の設計変更

Issue単位で `verified` とするだけでは粗い。

今後は:

```text
Issue
 ↓
Claim / Subtopic
 ↓
Review state
 ↓
Source
```

を正本にする方向。

例:

```text
生活相談員
 ├─ 基本配置                     VERIFIED
 ├─ 勤務時間基準                 VERIFIED
 ├─ サービス担当者会議の時間     UNREVIEWED
 └─ 地域連携活動の時間           UNREVIEWED
```

## 再現script

- `node scripts/research-issue-router-v0.1.mjs`
- `node scripts/research-coverage-classifier-v0.2.mjs`
- `node scripts/research-coverage-classifier-v0.3.mjs`
- `node scripts/research-coverage-classifier-v0.5.mjs`
- `node scripts/research-coverage-classifier-v0.6.mjs`
- `node scripts/research-coverage-classifier-v0.10.mjs`
- `node scripts/research-coverage-classifier-v0.11.mjs`
- `node scripts/research-coverage-classifier-v0.14.mjs`
- `node scripts/research-coverage-classifier-v0.16.mjs`
- `node scripts/research-coverage-classifier-v0.17.mjs`
- `node scripts/research-coverage-classifier-v0.19.mjs`
- `node scripts/research-coverage-classifier-v0.20.mjs`
- `node scripts/research-coverage-classifier-v0.21.mjs`
- `node scripts/research-coverage-classifier-v0.29.mjs`
- `node scripts/research-coverage-classifier-v0.28.mjs`
- `node scripts/research-coverage-classifier-v0.27.mjs`
- `node scripts/research-claim-registry-validate-v0.21.mjs`
- `node scripts/research-claim-registry-validate-v0.20.mjs`
- `node scripts/research-claim-registry-validate-v0.19.mjs`
- `node scripts/research-claim-registry-validate-v0.14.mjs`
- `node scripts/research-claim-registry-validate-v0.13.mjs`
- `node scripts/research-claim-compositions-validate-v0.8.mjs`
- `node scripts/research-claim-compositions-validate-v0.7.mjs`
- `node scripts/research-claim-compositions-validate-v0.6.mjs`
- `node scripts/research-claim-registry-validate-v0.11.mjs`
- `node scripts/research-claim-registry-validate-v0.10.mjs`
- `node scripts/research-claim-registry-validate-v0.8.mjs`
- `node scripts/research-claim-registry-validate-v0.6.mjs`
- `node scripts/research-claim-compositions-validate-v0.2.mjs`
- `node scripts/research-claim-registry-validate-v0.2.mjs`
- `node scripts/research-claim-registry-validate-v0.3.mjs`

## Controlled RAG comparison

比較条件は `controlled-rag-comparison-protocol-v0.1.md` と `controlled-rag-eval-contract-v0.1.json` に固定した。
RAG code / vector DB / embeddingはまだ導入していない。

## 次の再開点

1. new external holdout 30〜50件の作成
2. safety proseのhuman sign-off
3. 屋外サービス1件のcurrent integrated source reconstruction
4. gate通過後にcontrolled RAG comparisonを実装

`VERIFIED_WITH_SOURCE_LIMITATION` は現在1件のみ。
RAGはまだ実装しない。


## Controlled RAG external holdout

### Batch 1 — municipal / local boundary

- `rag-holdout-raw-v0.1.json`: raw 30 queries
- `rag-holdout-labeled-v0.1.json`: independent labels
- distribution: LOCAL 26 / OUT_OF_SCOPE 3 / REVIEW_REQUIRED 1

### Batch 2 — national MHLW Q&A

- `rag-holdout-national-raw-v0.1.json`: raw 20 queries
- `rag-holdout-national-labeled-v0.1.json`: independent labels
- distribution: REVIEW_REQUIRED 20

Combined 50-query holdout:
- ANSWER: 0
- PARTIAL: 0
- REVIEW_REQUIRED: 21
- LOCAL: 26
- OUT_OF_SCOPE: 3

この結果はretrieval failureではなく、current reviewed Claim coverageの不足を示す。
RAGはcoverage拡張より先に実装しない。

## Current Claim promotion

`claims-v0.16.json` で以下をANSWERへ昇格:

- 管理者の具体的責務
- 生活相談員の地域連携活動時間

external sampleは `external-qa-query-sample-v0.8.json`。
classifierは `research-coverage-classifier-v0.29.mjs`。

## Reproducibility

`research-coverage-classifier-v0.19.mjs`〜`v0.22.mjs` が自治体sample v0.4（15件）を読んでいた一方、checkpointはv0.5（25件）として191 checksを記録していた不整合を確認した。

`v0.23` 以降:
- municipal sample v0.5を使用
- suite cardinalityをfail closedで検査
- expected total checks = 191

GitHub Actions:
- `.github/workflows/verify-kaigo-ops-research.yml`
- classifier / Claim Registry / Composition Registryを検証
- Vercel deployとは独立

2026-09-23、head `9629ba14905f9b1569f2bda467e93397f10e75dc` のGitHub Actions run #15（35810802502）でclassifier v0.26の191 / 191 PASSを実測した。Claim Registry v0.18 validatorもvalid=true。その後、Composition validator v0.5が古いclaims-v0.12を参照していたことを発見し、v0.6でclaims-v0.19参照へ修正した。head `635bce98758ed2c998c99dd444fef376545dd220` のrun #16（35814522582）でclassifier v0.27は191 / 191 PASS、Claim Registry v0.19とComposition validator v0.6はいずれもvalid=trueを確認した。


## Claim coverage update — 2026-09-23

`claims-v0.18.json` で、生活相談員・介護職員の具体的人員配置を
PARTIAL / CANDIDATE_UNREVIEWED から ANSWER / VERIFIED_CURRENT へ昇格した。

- EQ-003: PARTIAL → ANSWER
- external sample: `external-qa-query-sample-v0.8.json`
- classifier: `research-coverage-classifier-v0.26.mjs`

現在:
- CANDIDATE_UNREVIEWED: 0
- PARTIAL: 0
- 残るREVIEW_REQUIREDは、報酬・単価・重要事項変更時同意・屋外時間境界・訪問診療等の5論点。


## Important matters change-consent review — 2026-09-23

`review.important.change-consent` を独立reviewし、`claims-v0.19.json` で
REVIEW_REQUIRED から ANSWER / VERIFIED_INTERPRETATION へ昇格した。

狭い結論:
- 第8条（第105条で指定通所介護に準用）が直接定めるのは、サービス提供開始時の重要事項の文書交付・説明と、当該提供開始への同意。
- 現行省令・解釈通知から、契約後の重要事項の全変更について一律に新たな文書同意を求める規定は確認できない。
- ただし、変更時の説明・通知が一切不要という意味ではない。別法令、報酬要件、契約、指定権者の運用は別途確認する。

MQ-001:
- REVIEW_REQUIRED → ANSWER
- municipal sample: `municipal-query-sample-v0.6.json`
- classifier: `research-coverage-classifier-v0.27.mjs`

Claim Registry v0.19:
- ANSWER: 45
- REVIEW_REQUIRED: 4
- PARTIAL: 0
- CANDIDATE_UNREVIEWED: 0


## Explicit HOLD review — visiting medical/dental + outdoor time boundary — 2026-09-23

`claims-v0.20.json` では、残るREVIEW_REQUIREDのうち次の2件をcurrent一次資料から独立reviewした。

- `review.service.visiting-medical-dental.in-service`
- `review.service.outdoor.time-boundary`

結論はいずれも **REVIEW_REQUIRED維持**。

訪問診療・訪問歯科:
- 2018年厚労省通知は、通所介護中の併設医療機関受診、巡回健診等、保険外サービスとの組合せを具体的に整理している。
- ただし、一般的な対面訪問診療・訪問歯科を直接扱う全国共通条項は確認できない。
- 令和8年度医科・歯科診療報酬の訪問診療算定要件は確認したが、算定可否から診療行為自体の一律可否を推測しない。

屋外サービスの時間境界:
- 屋外提供の実体条件（計画への位置付け + 効果的な機能訓練等）は厚労省資料で確認できる。
- 保険外の個別外出支援は通所介護を中断し、その時間を通所介護の提供時間へ含めない。
- しかし、この保険外ルールを反転して、保険内屋外活動の時間境界を全国一律に固定しない。

MQ-003 / MQ-005 はともに expected = REVIEW_REQUIRED のまま。
これは未調査ではなく、current national evidenceを確認した上でのfail-closed判定。

Claim Registry v0.20:
- ANSWER: 45
- REVIEW_REQUIRED: 4
- PARTIAL: 0
- CANDIDATE_UNREVIEWED: 0

次の大きなreview候補は、
- 基本報酬・加算・減算
- 地域区分・一単位単価
のreview ledger。
RAG実装は引き続き保留。


## Unit-price human review closure — 2026-09-23

`data/unit-price-review.json` を COMPLETE へ更新した。

独立確認元:
- 厚生労働大臣が定める一単位の単価（平成27年厚生労働省告示第93号）
- current official HTML: https://www.mhlw.go.jp/web/t_doc?dataId=82ab4582&dataType=0&pageNo=1

通所介護の一単位単価:
- 一級地 10.90円
- 二級地 10.72円
- 三級地 10.68円
- 四級地 10.54円
- 五級地 10.45円
- 六級地 10.27円
- 七級地 10.14円
- その他 10.00円

地域割当:
- 明示割当 427件を都道府県単位で公式表と全件照合
- 区分別件数: 1 / 7 / 29 / 24 / 59 / 137 / 170
- その他地域default ruleを確認
- 地域名称・区域は令和6年4月1日時点を基準とする備考を確認

`review.unit-price.region-and-rate`:
- REVIEW_REQUIRED → ANSWER
- verification: VERIFIED_CURRENT

coverage-gap:
- CG-010 横浜市: ANSWER（二級地 / 10.72円）
- CG-011 その他地域: ANSWER（10.00円）
- CG-019 地域区分の基準: ANSWER（事業所等の所在地）

fail-closed safeguard:
- `research-unit-price-review-validate-v0.1.mjs`
- source SHA、8 rates、427 assignments、default ruleをcurrent generated dataと照合
- source/data drift時はCIをfailさせる

Claim Registry v0.21 expected:
- ANSWER: 46
- REVIEW_REQUIRED: 3
- PARTIAL: 0
- CANDIDATE_UNREVIEWED: 0

残るREVIEW_REQUIRED:
- 基本報酬・加算・減算
- 通所介護提供時間中の対面訪問診療・訪問歯科（独立review済みHOLD）
- 屋外サービス提供時間境界（独立review済みHOLD）

RAGは引き続き実装しない。


## Remuneration base notice review — 2026-09-23

`data/remuneration-review.json` をv2へ更新。

- overall: IN_PROGRESS
- 告示第19号「6 通所介護費」本文: COMPLETE
- 委任先告示第27号・第95号: IN_PROGRESS
- 老企第36号: PENDING

告示第19号のcurrent official HTMLと、`remuneration-current-text.json` の29 / 29 fee nodeを照合済み。
source SHAと各fee nodeのtext SHAをreview ledgerへ固定した。

`research-remuneration-base-review-validate-v0.1.mjs` により、
current importが変化した場合はCIをfailさせる。

委任先告示と留意事項が閉じるまではoverallをCOMPLETEにせず、
報酬queryのREVIEW_REQUIREDを維持する。


## Remuneration delegated notice review — 2026-09-23

`data/remuneration-review.json` の委任先告示reviewを COMPLETEへ更新。

- 告示第27号: 3 / 3 node
- 告示第95号: 14 / 14 node
- total: 17 / 17

確認した主な関係:
- 利用定員超過: 所定単位数の70%
- 看護職員・介護職員の人員欠如: 所定単位数の70%
- 高齢者虐待防止措置未実施減算
- BCP未策定減算
- 入浴介助加算
- 中重度者ケア体制加算
- 個別機能訓練加算
- 認知症加算
- 栄養・口腔関連加算
- サービス提供体制強化加算
- 介護職員等処遇改善加算

`research-remuneration-delegated-review-validate-v0.1.mjs` で
source SHAと17 nodeのtext SHAをcurrent importへ固定。

overall remuneration reviewは引き続きIN_PROGRESS。
残る主要ゲートは老企第36号の現行再構成・留意事項review。
