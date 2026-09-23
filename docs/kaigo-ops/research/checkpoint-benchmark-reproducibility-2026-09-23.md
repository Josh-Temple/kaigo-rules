# Kaigo Ops Research Checkpoint — Benchmark Reproducibility Audit

更新日: 2026-09-23  
状態: **current harness 191 / 191実測済み / current-registry validators CLOSED**

## 旧不整合

旧harnessでは、checkpoint上は自治体queryを25件として191 checksを記録していた一方、
`research-coverage-classifier-v0.19.mjs`〜`v0.22.mjs` は
`municipal-query-sample-v0.4.json`（15件）を読み込んでいた。

そのため、過去の191 / 191はcurrent harnessでの再現値として扱わず、
v0.23以降で以下をfail closedにした。

- municipal sample: v0.5（25件）
- suite cardinality検査
- expected total checks: 191

## 実測結果

2026-09-23、research branch head
`9629ba14905f9b1569f2bda467e93397f10e75dc`
に対するGitHub Actions:

- workflow: `.github/workflows/verify-kaigo-ops-research.yml`
- run: #15
- run id: `35810802502`
- event: push
- conclusion: success

実ログ:

- classifier: v0.26
- total: **191**
- result: **PASS**
- Claim Registry v0.18: 49 claims / errors 0 / valid true
- Composition Registry v0.5 validator: 5 compositions / errors 0 / valid true

これにより、classifierのcurrent harnessについては191 / 191を再現済みとして扱える。

## 追加監査で見つけたvalidator依存関係

CI成功後にvalidator本体を静的確認したところ、
`scripts/research-claim-compositions-validate-v0.5.mjs` は
current Claim Registry v0.18ではなく、古い `claims-v0.12.json` を参照していた。

したがって、run #15のcomposition step成功を
「current Claim Registryとのcomposition整合性確認済み」とまでは扱わない。

対応:

- `research-claim-compositions-validate-v0.6.mjs` を作成
- current Claim Registry `claims-v0.19.json` を参照
- workflowをv0.6へ更新
- classifier v0.27 / Claim validator v0.19と合わせてCI再実行

研究ロジックをPASSさせるための変更ではなく、validatorの参照先をcurrent registryへ合わせる修正である。

## 判定

- classifier reproducibility: **CLOSED**
- Claim Registry validator: **CLOSED for v0.18 run #15**
- Composition current-registry validation: **CLOSED**
- RAG implementation: **HOLD**

## post-fix CI

research branch head `635bce98758ed2c998c99dd444fef376545dd220` に対する
GitHub Actions run #16（run id `35814522582`）を確認した。

実ログ:
- classifier v0.27: **191 / 191 PASS**
- Claim Registry v0.19: 49 claims / VERIFIED_INTERPRETATION 5 / REVIEW_REQUIRED 4 / errors 0 / valid true
- Composition validator v0.6: 5 compositions / errors 0 / valid true

v0.6は `claims-v0.19.json` を参照しており、古いv0.12依存は解消した。
これによりcurrent-registry validationもCLOSEDとする。
