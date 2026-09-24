# Kaigo Ops Research Checkpoint — Claim Promotion v0.23

更新日: 2026-09-23  
状態: **2 claims promoted / routing logic unchanged / execution rerun pending**

## 目的

RAG実装より先に、外部holdoutで明らかになったreviewed Claim coverageを増やす。

今回は報酬レイヤーを避け、既存REVIEW_REQUIREDから次の2件を独立reviewした。

## 1. 管理者の具体的責務

`candidate.staff.manager.responsibilities`

### 一次資料

- 現行厚生労働省令第37号 第52条
- 同第105条（第52条を指定通所介護へ準用）
- 令和6年度介護報酬改定Q&A Vol.1 問184

### 確認結果

指定通所介護の管理者は、
- 従業者・業務の管理を一元的に行う
- 利用申込みの調整、業務実施状況の把握等を行う
- 従業者に指定基準を遵守させるため必要な指揮命令を行う

Q&A問184は、利用者本位のサービス提供のため現場で生じる事象を把握しながら一元管理・指揮命令を行う責務として具体化している。

### Promotion

- CANDIDATE_UNREVIEWED → **VERIFIED_CURRENT**
- REVIEW_REQUIRED → **ANSWER**

管理者向けガイドラインに記載された参考事項すべてを法令上の必須義務へ一般化しない。

## 2. 生活相談員の地域連携活動時間

`candidate.staff.life-counselor.community-time`

### 一次資料

平成27年度介護報酬改定Q&A 問49。

確認した具体例:
- 地域住民等が参加する会議への参加
- 地域ボランティア団体との調整

事業所外活動は利用者の地域生活を支える取組である必要があり、活動・取組を事業所で記録する必要がある。

### Currentness確認

current mainの `qa-corpus-meta.json` は、
令和8年9月掲載の厚労省公式workbook
`001751835.xlsx`
を正本としている。

そのcurrent `qa-corpus.json` を直接確認し、
同Q&Aの質問・回答全文が現在も収載されていることを確認した。

### Promotion

- CANDIDATE_UNREVIEWED → **VERIFIED_CURRENT**
- REVIEW_REQUIRED → **ANSWER**

一般的な地域活動すべてを算入可能とはしない。

## Routing

既存routing語彙で両queryを解決できるため、新しいhard-coded ruleは追加しない。

- manager: `管理者` + `具体的な役割/責務`
- community time: `生活相談員` + `町内会/自治会/ボランティア/地域連携` + `時間/算入`

## Regression data

`external-qa-query-sample-v0.6.json`

変更:
- EQ-002: REVIEW_REQUIRED → ANSWER
- EQ-005: REVIEW_REQUIRED → ANSWER
- expected Claim IDを付与

case数は33のまま。

## Current

- Claim Registry: `claims-v0.16.json`
- External sample: `external-qa-query-sample-v0.6.json`
- Classifier: `research-coverage-classifier-v0.24.mjs`
- corrected harness expected checks: 191

## Validation caveat

classifier v0.24は、v0.23から
- Claim Registry参照先
- external sample参照先
- version metadata

のみ変更し、判定アルゴリズム自体は変更していない。

実行環境での191 checks再実行はまだPENDING。
未実行のため191/191とは記録しない。

## 次

1. corrected harness v0.24の実行
2. 残る非報酬REVIEW_REQUIRED Claimを優先順位付け
3. coverage拡張後に新しいexternal holdoutを追加
4. RAGは引き続き保留
