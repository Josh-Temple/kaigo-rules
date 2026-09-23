# Kaigo Ops Research Checkpoint — Combined Staffing Claim Promotion

更新日: 2026-09-23  
状態: **last candidate claim promoted / no PARTIAL claims remain**

## Claim

`candidate.staff.life-care-worker.combined-placement`

## Current primary source

現行厚生労働省令第37号 第93条を直接確認した。

### 生活相談員

提供日ごとに、
サービス提供時間帯に生活相談員が勤務した時間数の合計を
サービス提供時間で除した数が1以上となるよう必要数を確保する。

### 介護職員

指定通所介護の単位ごとに、
勤務時間数の合計を提供時間で除した数が

- 利用者15人まで: 1以上
- 15人超: 15人を超える部分 ÷ 5 + 1 以上

となるよう必要数を確保する。

さらに第2項により、
サービス提供時間帯を通じて常時1人以上の介護職員を従事させる。

### 常勤要件

第6項により、
生活相談員または介護職員のうち1人以上は常勤。

## Current Q&A corroboration

current mainの
令和8年9月掲載厚労省Q&A workbook由来corpusに、
平成24年度Q&A
「生活相談員及び介護職員の具体的な人員配置の方法」
が継続収載されていることを確認。

具体例では、
介護職員を常時1名以上確保しつつ、
必要勤務延時間の範囲でピークタイムへ柔軟配置できることが示されている。

## Promotion

- CANDIDATE_UNREVIEWED → **VERIFIED_CURRENT**
- PARTIAL → **ANSWER**

## Boundary

このClaimに含めない:
- 報酬加算上の追加配置要件
- 看護職員・機能訓練指導員
- 第一号通所事業と一体運営する場合の市町村基準の詳細
- 人員欠如時の報酬減算

## Regression update

`external-qa-query-sample-v0.8.json`

- EQ-003: PARTIAL → ANSWER
- expected Claim: `candidate.staff.life-care-worker.combined-placement`

classifierに新しいspecial caseは追加していない。

## Current

- Claim Registry: `claims-v0.18.json`
- External sample: `external-qa-query-sample-v0.8.json`
- Classifier: `research-coverage-classifier-v0.26.mjs`
- Validator: `research-claim-registry-validate-v0.18.mjs`
- expected regression checks: 191
- actual execution: PENDING

これによりClaim Registryの
`CANDIDATE_UNREVIEWED` と `PARTIAL` は0件になった。
