# RAG Holdout Collection v0.1

作成日: 2026-09-23  
状態: **30 raw queries frozen / labels not assigned**

## 目的

controlled RAG comparison用の新規holdoutを、
現在のClaim Registryやclassifier結果を見ずに先に固定する。

## Source

既存benchmarkで使用していない自治体の公式HTML Q&Aから収集した。

- 名古屋市
- 神戸市
- 仙台市

自治体回答は全国ルールのground truthには使用しない。

## Collection result

- raw queries: **30**
- expected answerability: 未付与
- expected Claim: 未付与
- expected source: 未付与
- classifier実行: 未実施

## 重要

この30件は、収集後に質問を差し替えてclass balanceを整えない。

次の工程で独立にラベル付けし、
結果としてLOCAL / OUT_OF_SCOPEが多すぎる等の偏りが判明した場合は、

- v0.1をそのまま残す
- 別sourceから追加batchを作る

ことで対応する。

既存30件を削って見栄えを整えない。

## 次

1. 30件を current scope / national-vs-local の観点から独立label
2. ANSWER候補だけは一次資料からexpected Claim / sourceを固定
3. class distributionを確認
4. 不足classがあれば別sourceからholdout batch v0.2を追加
5. その後にArm A/B/Cを実行
